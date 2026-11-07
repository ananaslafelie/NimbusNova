"""
QA DNA - Multithreaded | TEST PIPELINE

Trimite o lista de date de test spre Master, apoi poll-uieste
pana cand task-ul e reasamblat COMPLET - simuleaza un flux complet
end-to-end.

Rulare:
    python test_pipeline.py                                  # master local
    python test_pipeline.py --master http://100.x.y.z:8000
"""

from __future__ import annotations

import argparse
import asyncio
import random
import time

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

POLL_INTERVAL_S = 1.0
OVERALL_TIMEOUT_S = 300.0


async def main() -> None:
    ap = argparse.ArgumentParser(description="QA DNA test pipeline")
    ap.add_argument("--master", default="http://127.0.0.1:8000")
    ap.add_argument("--items", type=int, default=100, help="numarul de iteme de trimis")
    args = ap.parse_args()

    payload = {
        "items": [
            {"id": i, "gene": f"SEQ{i:04d}", "mutation": random.choice("ACGT")}
            for i in range(args.items)
        ]
    }

    timeout = httpx.Timeout(10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        # 1. ingest
        r = await client.post(f"{args.master}/submit-task", json=payload)
        r.raise_for_status()
        info = r.json()
        task_id = info["task_id"]
        total = info["total_chunks"]
        console.print(Panel(
            f"[bold]🧪 Test Pipeline pornit[/]\n"
            f"  master={args.master} • items={args.items} • chunks={total}\n"
            f"  task_id=[bold magenta]{task_id}[/]",
            title="🚀 Submit", border_style="magenta",
        ))

        # 2. poll pana e COMPLETED
        start = time.monotonic()
        while True:
            elapsed = time.monotonic() - start
            if elapsed > OVERALL_TIMEOUT_S:
                console.print(f"[bold red]⏰ Timeout dupa {elapsed:.0f}s[/]")
                raise SystemExit(1)
            await asyncio.sleep(POLL_INTERVAL_S)
            rr = await client.get(f"{args.master}/results/{task_id}")
            rr.raise_for_status()
            st = rr.json()
            done, failed, status = st["done_chunks"], st["failed_chunks"], st["status"]
            console.print(
                f"⏱ {elapsed:5.0f}s  status=[bold]{status}[/]  "
                f"chunks=[cyan]{done}/{total}[/]"
                + (f"  [red]failed={len(failed)}[/]" if failed else "")
            )
            if status in ("COMPLETED", "FAILED"):
                break

        # 3. sumar final
        if status == "FAILED":
            console.print(Panel(
                f"[bold red]Task FAILED[/] - chunks in dead-letter: {st['failed_chunks']}",
                title="🧨", border_style="red",
            ))
            raise SystemExit(2)

        results = st["results"] or []
        workers = {}
        for item in results:
            w = item.get("processed_by", "?")
            workers[w] = workers.get(w, 0) + 1

        table = Table(title=f"🎉 {task_id} — COMPLETED in {time.monotonic()-start:.1f}s",
                      border_style="green")
        table.add_column("Worker", style="cyan")
        table.add_column("Iteme procesate", justify="right")
        for w, c in sorted(workers.items()):
            table.add_row(w, str(c))
        console.print(table)

        console.print(Panel(
            f"[bold]Eșantion din rezultate:[/]\n"
            + "\n".join(f"  {r['item']['gene']} -> procesat de {r['processed_by']}"
                        for r in results[:5]),
            title="📄 Reasamblare finala", border_style="green",
        ))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Test intrerupt[/]")
