"""
QA DNA - Multithreaded | WORKER (PULL-Based nod de calcul)

NU expune porturi (firewall-friendly). DOAR face cereri de iesire catre Master:
  1. POST /register      - se anunta la pornire (cu IP-ul real de Tailscale)
  2. POST /heartbeat     - la fiecare 3-5s cu psutil (CPU %, RAM liber)
  3. GET  /get-task      - cere chunk, daca e idle
  4. asyncio.to_thread   - proceseaza chunk-ul ca sa nu blocheze bucla async
  5. POST /submit-result - trimite rezultatul partial inapoi

Rulare:
    python worker.py                                  # master local
    python worker.py --master http://100.x.y.z:8000   # master pe Tailscale
"""

from __future__ import annotations

import argparse
import asyncio
import socket
import time
from typing import List, Optional
from urllib.parse import urlparse

import httpx
import psutil
from rich.console import Console

console = Console()

IDLE_SLEEP_S = 1.0        # intre poll-uri cand nu e de lucru
HEARTBEAT_PERIOD_S = 3.0  # intervalul de heartbeat (spec: 3-5s)
HTTP_TIMEOUT_S = 8.0      # tolerant la retea slabe (Tailscale)


def _local_ip_towards(master_url: str) -> str:
    """Trick UDP: afla IP-ul local cu care ai ajunge la master (merge si pt Tailscale)."""
    try:
        host = urlparse(master_url).hostname
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((host or "127.0.0.1", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def chunk_work(data: List[dict], worker_id: str) -> List[dict]:
    """Procesare 'grea' simulata - ruleaza intr-un THREAD separat (nu blocheaza bucla)."""
    out = []
    for item in data:
        # Schimba aici logica reala (model run, parsing, hashing, etc.)
        out.append({
            "item": item,
            "processed_by": worker_id,
            "processed_at": time.time(),
        })
        time.sleep(0.005)  # simuleaza CPU work
    return out


async def register(client: httpx.AsyncClient, master: str, worker_id: str, ip: str) -> None:
    for attempt in range(1, 11):
        try:
            r = await client.post(f"{master}/register", json={"worker_id": worker_id, "ip": ip})
            r.raise_for_status()
            console.print(
                f"[bold green]🟢 REGISTER OK[/] worker [bold cyan]{worker_id}[/]"
                f" (ip={ip}) -> {master}"
            )
            return
        except (httpx.HTTPError, OSError) as e:
            console.print(f"[red]register retry {attempt}[/]: {type(e).__name__}: {e}")
            await asyncio.sleep(min(2 ** attempt, 10))
    raise SystemExit(f"NU ma pot inregistra la {master}")


async def heartbeat_loop(client: httpx.AsyncClient, master: str, worker_id: str) -> None:
    """Trimite heartbeat cu resurse la fiecare 3-5s (self-healing pentru master)."""
    while True:
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().available / 1024 / 1024
            await client.post(
                f"{master}/heartbeat",
                json={"worker_id": worker_id, "cpu_percent": cpu, "ram_free_mb": ram},
            )
            console.print(f"[dim]💓 heartbeat[/] cpu={cpu:.0f}% ram={ram:.0f}MB")
        except (httpx.HTTPError, OSError) as e:
            console.print(f"[red]heartbeat esuat[/]: {type(e).__name__}: {e}")
        await asyncio.sleep(HEARTBEAT_PERIOD_S)


async def worker_loop(client: httpx.AsyncClient, master: str, worker_id: str) -> None:
    while True:
        try:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().available / 1024 / 1024
            q = f"{master}/get-task?worker_id={worker_id}&cpu_percent={cpu}&ram_free_mb={ram}"
            r = await client.get(q)
            r.raise_for_status()
            body = r.json()
            chunk = body.get("chunk")
            if not chunk:
                await asyncio.sleep(IDLE_SLEEP_S)
                continue

            cid = chunk["id"]
            console.print(f"[bold blue]⚒  LUCRU[/] chunk [bold]{cid}[/]"
                          f" ({len(chunk['data'])} iteme) in thread separat...")
            t0 = time.monotonic()
            result = await asyncio.to_thread(chunk_work, chunk["data"], worker_id)
            dt = time.monotonic() - t0

            rr = await client.post(
                f"{master}/submit-result",
                json={"worker_id": worker_id, "chunk_id": cid, "results": result},
            )
            rr.raise_for_status()
            console.print(
                f"[bold green]✅ DONE[/] chunk [bold]{cid}[/] in {dt:.2f}s"
                f" -> trimis masterului"
            )
        except (httpx.HTTPError, OSError) as e:
            # fault-tolerant: nu mor, retry cu backoff (retea sau master restart)
            console.print(f"[red]network hiccup[/]: {type(e).__name__}: {e} - retry in 3s")
            await asyncio.sleep(3.0)


async def main() -> None:
    ap = argparse.ArgumentParser(description="QA DNA pull-based worker")
    ap.add_argument("--master", default="http://127.0.0.1:8000",
                    help="URL-ul Tailscale al masterului")
    ap.add_argument("--id", default=f"worker-{socket.gethostname().lower()}-{psutil.Process().pid % 1000:03d}",
                    help="id unic de worker")
    args = ap.parse_args()

    ip = _local_ip_towards(args.master)
    console.print(f"[bold cyan]🛰  {args.id}[/] pornind, master={args.master}, ip={ip}")

    timeout = httpx.Timeout(HTTP_TIMEOUT_S)
    async with httpx.AsyncClient(timeout=timeout) as client:
        await register(client, args.master, args.id, ip)
        hb = asyncio.create_task(heartbeat_loop(client, args.master, args.id))
        try:
            await worker_loop(client, args.master, args.id)
        finally:
            hb.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Worker oprit (Ctrl+C). Pana data viitoare![/]")
