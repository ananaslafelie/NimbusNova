"""
Test complet: Verifică workeri și trimite task
"""
import httpx
import asyncio
import time

async def test():
    print("=" * 60)
    print("🧪 TEST SISTEM QA DNA")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # 1. Verifică workeri
        print("\n1. Verificare workeri...")
        r = await client.get('http://localhost:8003/status')
        data = r.json()
        workers = data.get('workers', [])
        print(f"   ✅ {len(workers)} workeri conectați:")
        for w in workers:
            print(f"      - {w['id']} ({w['status']}) - CPU: {w['cpu']:.0f}%")
        
        if len(workers) < 2:
            print("   ⚠️  Așteaptă MacBook să se conecteze!")
            return
        
        # 2. Trimite task
        print("\n2. Creare task...")
        items = [{'id': i, 'value': i*2} for i in range(100)]
        r = await client.post('http://localhost:8003/submit-task', 
                              json={'items': items})
        result = r.json()
        task_id = result['task_id']
        total_chunks = result['total_chunks']
        print(f"   ✅ Task: {task_id}")
        print(f"   📊 {total_chunks} chunks (100 iteme)")
        
        # 3. Așteaptă finalizare
        print("\n3. Procesare...")
        start_time = time.time()
        
        for i in range(30):  # Max 30 secunde
            await asyncio.sleep(1)
            r = await client.get(f'http://localhost:8003/results/{task_id}')
            data = r.json()
            
            done = data['done_chunks']
            total = data['total_chunks']
            status = data['status']
            
            if status == 'COMPLETED':
                elapsed = time.time() - start_time
                print(f"   ✅ COMPLETAT în {elapsed:.1f} secunde!")
                print(f"   📈 {done}/{total} chunks procesate")
                print(f"   🖥️  Distribuit pe: {len(workers)} dispozitive")
                
                # Verifică câte chunks a făcut fiecare
                r = await client.get('http://localhost:8003/status')
                data = r.json()
                print("\n4. Statistici workeri:")
                for w in data['workers']:
                    print(f"   {w['id']}: {w['chunks_done']} chunks")
                return
            
            elif status == 'FAILED':
                print(f"   ❌ Task eșuat!")
                return
            
            else:
                print(f"   ⏳ {done}/{total} chunks complete...")
        
        print("   ⏱️  Timeout - verifică manual")

if __name__ == "__main__":
    asyncio.run(test())
