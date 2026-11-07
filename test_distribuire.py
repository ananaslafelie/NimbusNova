"""
TEST_DISTRIBUIRE.py - Test complet distribuție taskuri
Rulează pe Windows, trimite task, vezi distribuția
"""

import httpx
import asyncio
import time
import sys

MASTER_URL = "http://localhost:8003"

async def test_distribuire():
    print("=" * 70)
    print("🧪 TEST DISTRIBUIRE TASK - QA DNA")
    print("=" * 70)
    print()
    
    async with httpx.AsyncClient() as client:
        # 1. Verifică workeri
        print("1️⃣ Verificare workeri conectați...")
        try:
            r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
            data = r.json()
            workers = data.get('workers', [])
            
            print(f"   ✅ {len(workers)} worker(i) găsit(i):")
            for w in workers:
                icon = "🖥️" if 'windows' in w['id'] else "🍎" if 'mac' in w['id'] else "💻"
                print(f"      {icon} {w['id']}: {w['status']} | CPU: {w['cpu']:.0f}% | RAM: {w['ram_free_mb']:.0f}MB")
            
            if len(workers) < 2:
                print()
                print("   ⚠️  ATENȚIE: Doar 1 worker!")
                print("      Pentru test distribuit, conectează și MacBook:")
                print("      python3 worker.py --master http://100.64.66.23:8003 --id worker-macbook")
                print()
        except Exception as e:
            print(f"   ❌ Eroare: {e}")
            print("   Verifică că master.py rulează pe Windows!")
            return
        
        # 2. Crează task
        print()
        print("2️⃣ Creare task (100 iteme)...")
        items = [
            {"id": i, "nume": f"Item_{i:03d}", "valoare": i*10, "categorie": "A" if i % 2 == 0 else "B"}
            for i in range(100)
        ]
        
        try:
            r = await client.post(
                f"{MASTER_URL}/submit-task",
                json={"items": items},
                timeout=10.0
            )
            result = r.json()
            task_id = result['task_id']
            total_chunks = result['total_chunks']
            
            print(f"   ✅ Task creat: {task_id}")
            print(f"   📊 {len(items)} iteme → {total_chunks} chunks (10 iteme/chunk)")
            print()
        except Exception as e:
            print(f"   ❌ Eroare: {e}")
            return
        
        # 3. Așteaptă procesare
        print("3️⃣ Procesare distribuită în timp real...")
        print()
        
        start_time = time.time()
        
        while True:
            try:
                r = await client.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
                data = r.json()
                
                status = data.get('status', 'unknown')
                done = data.get('done_chunks', 0)
                total = data.get('total_chunks', 1)
                
                elapsed = time.time() - start_time
                
                if status == 'COMPLETED':
                    print(f"   ✅ COMPLETAT în {elapsed:.1f} secunde!")
                    print(f"   📈 {done}/{total} chunks procesate")
                    break
                elif status == 'FAILED':
                    print(f"   ❌ TASK EȘUAT!")
                    return
                else:
                    # Afișare progres
                    procent = (done / total) * 100
                    bar_len = int(procent / 5)
                    bar = "█" * bar_len + "░" * (20 - bar_len)
                    print(f"   ⏳ [{bar}] {done}/{total} chunks ({procent:.0f}%) - {elapsed:.1f}s")
                    
            except Exception as e:
                print(f"   ⚠️  Eroare poll: {e}")
            
            await asyncio.sleep(1)
        
        # 4. Statistici finale
        print()
        print("4️⃣ Statistici finale:")
        try:
            r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
            data = r.json()
            
            print(f"   📊 Distribuție pe workeri:")
            for w in data.get('workers', []):
                print(f"      {w['id']}: {w['chunks_done']} chunks procesate")
            
            print()
            print("=" * 70)
            print("🎉 TEST REUȘIT!")
            print("=" * 70)
            print()
            print("✅ Taskul a fost împărțit automat în chunks")
            print("✅ Chunks au fost distribuite workerilor disponibili")
            print("✅ Rezultatele au fost reasamblate")
            print()
            
            if len(data.get('workers', [])) >= 2:
                print("🌟 SUPER! Ai avut 2+ workeri - distribuție reală!")
            else:
                print("💡 Pentru distribuție reală multi-device, conectează MacBook!")
            
        except Exception as e:
            print(f"   ❌ Eroare statistici: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_distribuire())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test întrerupt")
    except Exception as e:
        print(f"\n\n❌ Eroare: {e}")
        import traceback
        traceback.print_exc()
