"""
TEST VIZUAL LIVE - Vezi distribuția în timp real între Windows și MacBook
"""
import httpx
import json
import time
import os
from datetime import datetime

MASTER_URL = "http://localhost:8003"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_bar(current, total, width=50):
    pct = current / total
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{total} ({pct*100:.1f}%)"

def show_live_dashboard(task_id, total_chunks):
    """Arată dashboard în timp real"""
    
    # Istoric chunk-uri
    windows_chunks = []
    macbook_chunks = []
    
    while True:
        try:
            # Ia status
            r = httpx.get(f"{MASTER_URL}/status", timeout=5.0)
            status_data = r.json()
            
            # Ia progres task
            r = httpx.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
            task_data = r.json()
            
            status = task_data.get('status', 'PROCESSING')
            done = task_data.get('done_chunks', 0)
            
            # Găsește chunks per worker
            for w in status_data.get('workers', []):
                worker_id = w['id']
                chunks = w.get('chunks_done', 0)
                
                # Actualizează istoric
                if 'windows' in worker_id:
                    if chunks > len(windows_chunks):
                        # Worker Windows a procesat chunk nou
                        for i in range(len(windows_chunks), chunks):
                            windows_chunks.append(i)
                elif 'macbook' in worker_id:
                    if chunks > len(macbook_chunks):
                        # MacBook a procesat chunk nou
                        for i in range(len(macbook_chunks), chunks):
                            macbook_chunks.append(i)
            
            # Afișează dashboard
            clear_screen()
            print("=" * 80)
            print("🧬 QA DNA - DISTRIBUȚIE ÎN TIMP REAL")
            print("=" * 80)
            print()
            
            # Progress
            print(f"Task: {task_id}")
            print(f"Progres: {draw_bar(done, total_chunks)}")
            print()
            
            # Status workeri
            print("📊 STATUS WORKERI:")
            print("-" * 80)
            
            for w in status_data.get('workers', []):
                worker_id = w['id']
                cpu = w['cpu']
                ram = w['ram_free_mb']
                chunks = w.get('chunks_done', 0)
                
                icon = "🖥️" if 'windows' in worker_id else "🍎"
                chunks_list = windows_chunks if 'windows' in worker_id else macbook_chunks
                
                print(f"{icon} {worker_id}")
                print(f"   CPU: {cpu:.1f}% | RAM: {ram:.0f}MB | Chunks: {chunks}")
                
                # Arată ultimele 10 chunk-uri procesate
                if chunks_list:
                    recent = chunks_list[-10:]
                    print(f"   Chunk-uri recente: {recent}")
                print()
            
            # Distribuție vizuală
            print("📈 DISTRIBUȚIA CHUNK-URILOR:")
            print("-" * 80)
            
            total_w = len(windows_chunks)
            total_m = len(macbook_chunks)
            total_processed = total_w + total_m
            
            if total_processed > 0:
                w_pct = (total_w / total_processed) * 100
                m_pct = (total_m / total_processed) * 100
                
                # Bare orizontale
                w_bar = "█" * int(w_pct / 2)
                m_bar = "█" * int(m_pct / 2)
                
                print(f"🖥️  Windows: {w_bar} {total_w} chunks ({w_pct:.1f}%)")
                print(f"🍎 MacBook: {m_bar} {total_m} chunks ({m_pct:.1f}%)")
            
            print()
            print(f"⏱️  Timp: {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 80)
            
            # Verifică dacă s-a terminat
            if status == 'COMPLETED':
                print()
                print("🎉 TASK COMPLETAT!")
                print(f"✅ {total_chunks} chunks procesate în paralel!")
                print()
                print("💾 Rezultate salvate la master.")
                break
            elif status == 'FAILED':
                print()
                print("❌ TASK EȘUAT!")
                break
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Eroare: {e}")
            time.sleep(1)

def test_vizual():
    """Test vizual cu fișier"""
    
    # Alege fișierul
    import sys
    file_path = sys.argv[1] if len(sys.argv) > 1 else "test_real_1000.json"
    
    print(f"📁 Încarc fișierul: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    print(f"✅ {len(items)} iteme găsite")
    print("\n🚀 Pornesc procesarea distribuită în 2 secunde...")
    import time
    time.sleep(2)
    
    # Trimite task
    r = httpx.post(
        f"{MASTER_URL}/submit-task",
        json={"items": items, "filename": file_path},
        timeout=10.0
    )
    result = r.json()
    task_id = result['task_id']
    total_chunks = result['total_chunks']
    
    print(f"\n🚀 Task creat: {task_id}")
    print(f"🧩 {total_chunks} chunks de procesat...")
    print("\n" + "=" * 80)
    time.sleep(1)
    
    # Afișează dashboard live
    show_live_dashboard(task_id, total_chunks)

if __name__ == "__main__":
    test_vizual()
