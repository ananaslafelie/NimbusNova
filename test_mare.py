"""
TEST_MARE.py - Test cu 1000 iteme pentru a vedea distribuția reală
"""

import httpx
import asyncio
import time
import sys

MASTER_URL = "http://localhost:8003"

async def test_mare():
    print("=" * 70)
    print("🧪 TEST DISTRIBUIRE MARE - 1000 iteme")
    print("=" * 70)
    print()
    
    async with httpx.AsyncClient() as client:
        # Verificare workeri
        print("1️⃣ Verificare workeri...")
        r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
        data = r.json()
        workers = data.get('workers', [])
        
        print(f"   ✅ {len(workers)} worker(i) online")
        for w in workers:
            icon = "🖥️" if 'windows' in w['id'] else "🍎"
            print(f"      {icon} {w['id']}: CPU {w['cpu']:.0f}%")
        print()
        
        # Task mare
        print("2️⃣ Creare task cu 1000 iteme...")
        items = [{"id": i, "value": i*i, "data": f"Item_{i:04d}"} for i in range(1000)]
        
        r = await client.post(
            f"{MASTER_URL}/submit-task",
            json={"items": items},
            timeout=10.0
        )
        result = r.json()
        task_id = result['task_id']
        total_chunks = result['total_chunks']
        
        print(f"   ✅ Task: {task_id}")
        print(f"   📊 {len(items)} iteme → {total_chunks} chunks")
        print()
        
        # Progres
        print("3️⃣ Procesare în timp real...")
        print()
        
        start_time = time.time()
        last_done = 0
        
        while True:
            r = await client.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
            data = r.json()
            
            status = data.get('status', 'unknown')
            done = data.get('done_chunks', 0)
            total = data.get('total_chunks', 1)
            elapsed = time.time() - start_time
            
            if status == 'COMPLETED':
                print(f"\r   ✅ COMPLETAT în {elapsed:.1f}s!                    ")
                break
            elif done > last_done:
                pct = (done / total) * 100
                bar = "█" * int(pct/5) + "░" * (20 - int(pct/5))
                print(f"\r   ⏳ [{bar}] {done}/{total} ({pct:.0f}%) {elapsed:.1f}s", end="")
                last_done = done
            
            await asyncio.sleep(0.5)
        
        # Statistici finale
        print()
        print()
        print("4️⃣ Distribuția pe workeri:")
        r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
        data = r.json()
        
        for w in data.get('workers', []):
            chunks = w['chunks_done']
            pct = (chunks / total_chunks) * 100 if total_chunks > 0 else 0
            icon = "🖥️" if 'windows' in w['id'] else "🍎"
            print(f"      {icon} {w['id']}: {chunks} chunks ({pct:.1f}%)")
        
        print()
        print("=" * 70)
        print("🎉 TEST FINALIZAT!")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_mare())
