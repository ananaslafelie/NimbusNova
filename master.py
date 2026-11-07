"""
QA DNA - Multithreaded | MASTER (Central Task Broker & Orchestrator)

Arhitectura PULL-Based:
  - Workerii POLL-uiesc masterul (get-task), deci NU e nevoie de porturi
    deschise pe laptopuri -> zero batai de cap cu firewall-ul.
  - Masterul expune: /register, /heartbeat, /submit-task, /get-task,
    /submit-result, /results/{id}, /status

Rulare:
    python master.py                 # asculta pe 0.0.0.0:8000
Dashboard live:
    http://127.0.0.1:8000/status     # tabel cu noduri + cu coada
"""

from __future__ import annotations

import asyncio
import time
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import uvicorn
import psutil
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# ----------------------------------------------------------------------------
# Config (achatite la hackathon; pune-le in .env daca cresti)
# ----------------------------------------------------------------------------
HEARTBEAT_TIMEOUT_S = 12.0   # worker fara heartbeat 12s => OFFLINE
TASK_TIMEOUT_S = 30.0        # chunk fara rezultat 30s => se intoarce in coada
CHUNK_SIZE = 10              # elemente per chunk
MAX_ATTEMPTS = 3             # dupa 3 esecuri chunk-ul ajunge in dead-letter

console = Console()

# ----------------------------------------------------------------------------
# In-memory state (single asyncio loop => fara race conditions intre request-uri)
# ----------------------------------------------------------------------------
@dataclass
class Worker:
    id: str
    ip: str
    cpu: float = 0.0
    ram_free_mb: float = 0.0
    last_seen: float = 0.0
    status: str = "ONLINE"
    chunks_done: int = 0

@dataclass
class Chunk:
    id: str
    task_id: str
    index: int
    data: List[dict]
    assigned_to: Optional[str] = None
    assigned_at: float = 0.0
    attempts: int = 0

@dataclass
class Task:
    id: str
    total_chunks: int
    chunks_done: set = field(default_factory=set)
    results: Dict[int, List[dict]] = field(default_factory=dict)
    failed_chunks: set = field(default_factory=set)
    status: str = "PENDING"   # PENDING / RUNNING / COMPLETED / FAILED

_workers: Dict[str, Worker] = {}
_tasks: Dict[str, Task] = {}
_chunks: Dict[str, Chunk] = {}
_ready: deque = deque()       # coada de chunk_ids disponibile (PULL source)

def _requeue(chunk: Chunk, reason: str) -> None:
    """Pune chunk-ul inapoi in coada (self-healing) sau il trimite la dead-letter."""
    chunk.attempts += 1
    chunk.assigned_to = None
    chunk.assigned_at = 0.0
    task = _tasks[chunk.task_id]
    if chunk.attempts >= MAX_ATTEMPTS:
        task.failed_chunks.add(chunk.index)
        console.print(
            f"[bold red]DEAD-LETTER[/] chunk [bold]{chunk.id}[/] "
            f"dupa [bold]{chunk.attempts}[/] incercari ({reason})"
        )
    else:
        _ready.append(chunk.id)
        console.print(
            f"[bold yellow]REQUEUE[/] chunk [bold]{chunk.id}[/] "
            f"(incercarea {chunk.attempts}/{MAX_ATTEMPTS}, motiv: {reason})"
        )

def _maybe_complete(task_id: str) -> None:
    t = _tasks[task_id]
    if len(t.chunks_done) + len(t.failed_chunks) != t.total_chunks:
        if t.status == "PENDING":
            t.status = "RUNNING"
        return
    if t.failed_chunks:
        t.status = "FAILED"
        console.print(Panel(
            f"Task [bold red]{task_id}[/] [bold red]FAILED[/] - "
            f"{len(t.failed_chunks)} chunk(s) in dead-letter",
            title="Task esuat", border_style="red",
        ))
    else:
        t.status = "COMPLETED"
        console.print(Panel(
            f"Task [bold green]{task_id}[/] [bold green]COMPLETED[/] - "
            f"{t.total_chunks} chunk-uri reasamblate",
            title="Task finalizat", border_style="green",
        ))

async def _janitor() -> None:
    """Self-healing: marcheaza workeri OFFLINE si requeue-ueste chunk-uri blocate."""
    while True:
        await asyncio.sleep(2.0)
        now = time.monotonic()

        for w in list(_workers.values()):
            if w.status == "ONLINE" and now - w.last_seen > HEARTBEAT_TIMEOUT_S:
                w.status = "OFFLINE"
                console.print(
                    f"[bold red]OFFLINE[/] worker [bold]{w.id}[/] "
                    f"(fara heartbeat de {now - w.last_seen:.0f}s)"
                )

        for ch in list(_chunks.values()):
            if ch.assigned_to and now - ch.assigned_at > TASK_TIMEOUT_S:
                reason = (
                    f"timeout {TASK_TIMEOUT_S:.0f}s"
                    if _workers.get(ch.assigned_to, Worker(id="", ip="")).status == "ONLINE"
                    else "worker-ul a picat"
                )
                ch.assigned_at = 0.0
                ch.assigned_to = None
                _requeue(ch, reason)

# ----------------------------------------------------------------------------
# Pydantic models
# ----------------------------------------------------------------------------
class RegisterIn(BaseModel):
    worker_id: str
    ip: str

class HeartbeatIn(BaseModel):
    worker_id: str
    cpu_percent: float = Field(ge=0, le=100)
    ram_free_mb: float = Field(ge=0)

# ----------------------------------------------------------------------------
# Lifespan + app
# ----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_janitor())
    console.print(Panel(
        "[bold cyan]QA DNA - Multithreaded[/] | [bold]MASTER broker pornit[/]\\n"
        f"  CPU: {psutil.cpu_percent(0.5):.1f}%  •  coada initiala goala\\n"
        f"  HEARTBEAT_TIMEOUT={HEARTBEAT_TIMEOUT_S}s  TASK_TIMEOUT={TASK_TIMEOUT_S}s  "
        f"CHUNK_SIZE={CHUNK_SIZE}",
        title="Master", border_style="cyan",
    ))
    yield
    task.cancel()

app = FastAPI(title="QA DNA Master", lifespan=lifespan)

# ----------------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------------
@app.post("/register")
async def register(body: RegisterIn) -> dict:
    _workers[body.worker_id] = Worker(body.worker_id, body.ip, last_seen=time.monotonic())
    console.print(Panel(
        f"[bold green]ONLINE[/]  worker [bold cyan]{body.worker_id}[/]  "
        f"inregistrat de la [dim]{body.ip}[/]",
        title="Node Registry", border_style="green",
    ))
    return {"ok": True, "worker_id": body.worker_id, "status": "ONLINE"}

@app.post("/heartbeat")
async def heartbeat(body: HeartbeatIn) -> dict:
    if body.worker_id not in _workers:
        raise HTTPException(404, "worker necunoscut, reînregistreaza-te")
    w = _workers[body.worker_id]
    if w.status == "OFFLINE":
        console.print(f"[bold green]REVIVED[/] worker [bold]{w.id}[/] a revenit la viata")
    w.status = "ONLINE"
    w.cpu = body.cpu_percent
    w.ram_free_mb = body.ram_free_mb
    w.last_seen = time.monotonic()
    return {"ok": True}

@app.post("/submit-task")
async def submit_task(payload: dict) -> dict:
    """Sparge payload-ul in chunks si-i baga in coada. Payload: {\"items\": [...]}"""
    items: List[dict] = payload.get("items", [])
    if not items:
        raise HTTPException(400, "'items' trebuie sa fie o lista nevida")
    if len(items) > 100_000:
        raise HTTPException(413, f"prea multe iteme ({len(items)}); max 100_000")

    task_id = f"task-{int(time.time())}-{len(_tasks):04d}"
    chunks: List[str] = []
    for i in range(0, len(items), CHUNK_SIZE):
        idx = i // CHUNK_SIZE
        ch = Chunk(
            id=f"{task_id}#{idx}",
            task_id=task_id,
            index=idx,
            data=items[i:i + CHUNK_SIZE],
        )
        _chunks[ch.id] = ch
        _ready.append(ch.id)
        chunks.append(ch.id)
    _tasks[task_id] = Task(id=task_id, total_chunks=len(chunks))
    console.print(Panel(
        f"[bold]TASK INGESTED[/]  [bold magenta]{task_id}[/]\\n"
        f"  iteme: [bold]{len(items)}[/]  •  chunks: [bold]{len(chunks)}[/]  "
        f"•  dimensiune chunk: {CHUNK_SIZE}\\n"
        f"  coada acum: [bold]{len(_ready)}[/] chunk-uri in asteptare",
        title="Task Ingestion", border_style="magenta",
    ))
    return {"ok": True, "task_id": task_id, "total_chunks": len(chunks)}

@app.get("/get-task")
async def get_task(
    worker_id: str,
    cpu_percent: float = 0.0,
    ram_free_mb: float = 0.0,
) -> dict:
    """DISPENSER: worker-ul cere de lucru; masterul ii da cel mai potrivit chunk.

    Politica de selectie:     chunks retry-uite primele, apoi FIFO.
    Resource-aware proof:     masterul logheaza cpu/ram raportate de worker.
    """
    if worker_id in _workers:
        _workers[worker_id].last_seen = time.monotonic()

    if not _ready:
        return {"chunk": None, "reason": "queue_empty"}

    ch = _chunks[_ready.popleft()]
    ch.assigned_to = worker_id
    ch.assigned_at = time.monotonic()
    ch.attempts += 1
    console.print(
        f"[bold blue]DISPATCH[/] [bold]{ch.id}[/] ->"
        f" [bold cyan]{worker_id}[/]"
        f"  [dim](cpu={cpu_percent:.0f}% ram={ram_free_mb:.0f}MB,"
        f" incercarea {ch.attempts})[/]"
    )
    return {
        "chunk": {
            "id": ch.id,
            "task_id": ch.task_id,
            "index": ch.index,
            "data": ch.data,
        },
        "attempts": ch.attempts,
    }

@app.post("/submit-result")
async def submit_result(payload: dict) -> dict:
    """Colecteaza rezultatul partial si-l pune la locul lui (reasamblare indexata)."""
    worker_id: str = payload.get("worker_id", "?")
    chunk_id: str = payload.get("chunk_id", "")
    ch = _chunks.get(chunk_id)
    if ch is None:
        raise HTTPException(404, f"chunk necunoscut: {chunk_id}")
    task = _tasks[ch.task_id]
    if ch.index in task.chunks_done:
        console.print(f"[dim]duplicat ignorat: {chunk_id} (deja livrat)[/]")
        return {"ok": True, "duplicate": True}

    results: List[dict] = payload.get("results", [])
    task.results[ch.index] = results
    task.chunks_done.add(ch.index)
    ch.assigned_to = None
    _workers.get(worker_id, Worker(id=worker_id, ip="?")).chunks_done += 1
    _maybe_complete(task.id)
    remaining = task.total_chunks - len(task.chunks_done) - len(task.failed_chunks)
    console.print(
        f"[bold green]IN-RESULT[/] chunk [bold]{chunk_id}[/]"
        f" <- [bold cyan]{worker_id}[/]"
        f"  [dim](iteme={len(results)}, rămase={remaining}/{task.total_chunks})[/]"
    )
    return {"ok": True, "task_id": task.id, "progress": f"{len(task.chunks_done)}/{task.total_chunks}"}

@app.get("/results/{task_id}")
async def results(task_id: str) -> dict:
    """Reassembly endpoint: intoarce raspunsul final cand toate chunk-urile au ajuns."""
    t = _tasks.get(task_id)
    if t is None:
        raise HTTPException(404, f"task necunoscut: {task_id}")
    assembled: Optional[List[dict]] = None
    if t.status == "COMPLETED":
        assembled = [item for i in range(t.total_chunks) for item in t.results[i]]
    return {
        "task_id": task_id,
        "status": t.status,
        "total_chunks": t.total_chunks,
        "done_chunks": len(t.chunks_done),
        "failed_chunks": sorted(t.failed_chunks),
        "results": assembled,
    }

@app.get("/status")
async def status() -> dict:
    """Dashboard: tabel rich in consola + JSON pentru programatic/hackathon demo."""
    table = Table(title="QA DNA - Master Node Status", border_style="cyan")
    table.add_column("Worker", style="cyan")
    table.add_column("Status")
    table.add_column("CPU %", justify="right")
    table.add_column("RAM liber (MB)", justify="right")
    table.add_column("Chunks done", justify="right")
    for w in _workers.values():
        color = "green" if w.status == "ONLINE" else "red"
        table.add_row(
            w.id,
            f"[{color}]{w.status}[/]",
            f"{w.cpu:.0f}",
            f"{w.ram_free_mb:.0f}",
            str(w.chunks_done),
        )
    console.print(table)
    queue_tbl = Table(title=f"_ready queue  (len={len(_ready)})", border_style="magenta")
    queue_tbl.add_column("Pozitie", justify="right", width=8)
    queue_tbl.add_column("Chunk ID", style="bold")
    for i, cid in enumerate(list(_ready)[:12]):
        queue_tbl.add_row(str(i), cid)
    console.print(queue_tbl)
    return {
        "workers": [w.__dict__ for w in _workers.values()],
        "queue_len": len(_ready),
        "tasks": [(t.id, t.status, len(t.chunks_done), t.total_chunks) for t in _tasks.values()],
    }

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    
    console.print(Panel(
        f"[bold cyan]QA DNA Master[/] pornind pe [bold]http://{args.host}:{args.port}[/]\\n"
        f"[dim]Dashboard: http://127.0.0.1:{args.port}/status[/dim]",
        title="Server", border_style="cyan",
    ))
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
