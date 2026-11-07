"""
Quick test - trimite fisier direct la master
"""
import httpx
import json
import time

MASTER_URL = "http://localhost:8003"

def test_file(file_path: str):
    # Citeste fisierul
    print(f"📖 Citesc {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    print(f"✅ {len(items)} iteme citite")
    print(f"📊 Exemplu: {items[0]}")
    
    # Trimite la master
    print(f"\n🚀 Trimit la Master...")
    r = httpx.post(
        f"{MASTER_URL}/submit-task",
        json={"items": items, "filename": file_path},
        timeout=10.0
    )
    result = r.json()
    task_id = result['task_id']
    total_chunks = result['total_chunks']
    
    print(f"✅ Task creat: {task_id}")
    print(f"🧩 {total_chunks} chunks de procesat")
    print(f"\n⏳ Astept procesarea...")
    
    # Asteapta completarea
    while True:
        r = httpx.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
        data = r.json()
        
        status = data.get('status')
        done = data.get('done_chunks', 0)
        total = data.get('total_chunks', 1)
        
        pct = (done / total) * 100
        bar = "█" * int(pct/5) + "░" * (20 - int(pct/5))
        print(f"\r   [{bar}] {done}/{total} ({pct:.0f}%)", end="", flush=True)
        
        if status == 'COMPLETED':
            print("\n✅ COMPLETAT!")
            
            # Statistici
            r = httpx.get(f"{MASTER_URL}/status", timeout=5.0)
            status_data = r.json()
            
            print("\n📈 Distribuția pe workeri:")
            for w in status_data.get('workers', []):
                icon = "🖥️" if 'windows' in w['id'] else "🍎"
                chunks = w['chunks_done']
                pct_w = (chunks / total * 100) if total > 0 else 0
                print(f"   {icon} {w['id']}: {chunks} chunks ({pct_w:.1f}%)")
            
            break
        elif status == 'FAILED':
            print("\n❌ TASK EȘUAT!")
            break
        
        time.sleep(0.5)

if __name__ == "__main__":
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else "test_data_100.json"
    test_file(file_path)
