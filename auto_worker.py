"""
NOVA Auto-Worker
Rulează automat fără setup manual
"""

import subprocess
import sys
import os

# Instalare automată dependențe
def install_requirements():
    try:
        import requests
    except ImportError:
        print("📦 Instalare requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
        print("✅ Gata!")

install_requirements()

# Acum importăm
import requests
import time
import json
import platform
import socket

print("="*60)
print("  NOVA Auto-Worker")
print("="*60)

# Citește config din argumente sau întreabă
MASTER_IP = sys.argv[1] if len(sys.argv) > 1 else input("IP Master (ex: 100.x.x.x sau 192.168.x.x): ")
MASTER_URL = f"http://{MASTER_IP}:8003"
WORKER_ID = "worker-" + platform.node().lower().replace(" ", "-")[:10]

print(f"Master: {MASTER_URL}")
print(f"Worker ID: {WORKER_ID}")
print("="*60)

def register():
    try:
        r = requests.post(f"{MASTER_URL}/register", 
            json={"worker_id": WORKER_ID, "ip": socket.gethostbyname(socket.gethostname())},
            timeout=10
        )
        return r.json()
    except Exception as e:
        print(f"⚠️ Eroare înregistrare: {e}")
        return None

def get_task():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().available / (1024*1024)
    except:
        cpu = 10
        ram = 4000
    
    try:
        r = requests.get(f"{MASTER_URL}/get-task", 
            params={"worker_id": WORKER_ID, "cpu_percent": cpu, "ram_free_mb": ram},
            timeout=30
        )
        return r.json().get("chunk")
    except:
        return None

def process_chunk(chunk):
    """Procesare - exemplu simplu"""
    data = chunk.get("data", [])
    results = []
    for item in data:
        # Procesare exemplu
        result = dict(item)
        result["processed"] = True
        result["by"] = WORKER_ID
        results.append(result)
    return results

def submit_result(chunk_id, results):
    try:
        r = requests.post(f"{MASTER_URL}/submit-result",
            json={"worker_id": WORKER_ID, "chunk_id": chunk_id, "results": results},
            timeout=30
        )
        return r.json()
    except Exception as e:
        print(f"⚠️ Eroare submit: {e}")
        return None

# Main loop
if __name__ == "__main__":
    print("🔗 Conectare la Master...")
    
    # Încearcă să te înregistrezi
    for i in range(5):
        result = register()
        if result:
            print(f"✅ Înregistrat! Status: {result.get('status', 'OK')}")
            break
        else:
            print(f"⏳ Retry {i+1}/5...")
            time.sleep(2)
    else:
        print("❌ Nu m-am putut conecta. Verifică IP-ul și că Master rulează.")
        sys.exit(1)
    
    print("⏳ Aștept taskuri... (Ctrl+C pentru a opri)")
    print("="*60)
    
    chunks_done = 0
    
    while True:
        try:
            chunk = get_task()
            
            if chunk:
                chunk_id = chunk['id']
                print(f"📦 Procesez: {chunk_id}")
                
                # Procesare
                results = process_chunk(chunk)
                
                # Submit
                submit_result(chunk_id, results)
                chunks_done += 1
                
                print(f"✓ Completat ({chunks_done} chunks) - {chunk_id}")
            else:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Oprire...")
            break
        except Exception as e:
            print(f"⚠️ Eroare: {e}")
            time.sleep(2)
