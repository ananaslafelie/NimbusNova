"""
QA DNA Desktop Launcher
Pornește Master + Aplicația Desktop automat
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Configurare
MASTER_PORT = 8003
DESKTOP_PORT = 8080

def start_master():
    """Pornește serverul master în background"""
    print("🚀 Pornire Master Server...")
    
    env = os.environ.copy()
    env['PYTHONUTF8'] = '1'
    
    master_process = subprocess.Popen(
        [sys.executable, 'master.py', '--port', str(MASTER_PORT)],
        cwd=str(Path(__file__).parent.parent),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    print(f"   ✅ Master pornit pe port {MASTER_PORT}")
    return master_process

def start_worker(worker_id: str, master_url: str):
    """Pornește un worker local"""
    print(f"🖥️  Pornire Worker '{worker_id}'...")
    
    env = os.environ.copy()
    env['PYTHONUTF8'] = '1'
    
    worker_process = subprocess.Popen(
        [sys.executable, 'worker.py', '--master', master_url, '--id', worker_id],
        cwd=str(Path(__file__).parent.parent),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    print(f"   ✅ Worker '{worker_id}' pornit")
    return worker_process

def start_desktop_app():
    """Pornește aplicația desktop"""
    print("🖼️  Pornire Aplicație Desktop...")
    
    env = os.environ.copy()
    env['PYTHONUTF8'] = '1'
    
    # Așteptăm puțin să pornească masterul
    time.sleep(3)
    
    desktop_process = subprocess.Popen(
        [sys.executable, 'desktop_app/main.py'],
        cwd=str(Path(__file__).parent.parent),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    print(f"   ✅ Desktop App pornită pe port {DESKTOP_PORT}")
    return desktop_process

def main():
    """Main launcher"""
    print("=" * 70)
    print("🧬 QA DNA Desktop - Launcher")
    print("=" * 70)
    print()
    
    processes = []
    
    try:
        # 1. Pornim Masterul
        master = start_master()
        processes.append(master)
        time.sleep(2)
        
        # 2. Pornim Worker local
        worker = start_worker('worker-desktop', f'http://localhost:{MASTER_PORT}')
        processes.append(worker)
        time.sleep(1)
        
        # 3. Pornim Aplicația Desktop
        desktop = start_desktop_app()
        processes.append(desktop)
        
        print()
        print("=" * 70)
        print("✅ Toate serviciile pornite!")
        print()
        print("🌐 Accesează aplicația:")
        print(f"   http://localhost:{DESKTOP_PORT}")
        print()
        print("📊 Dashboard Master:")
        print(f"   http://localhost:{MASTER_PORT}/status")
        print()
        print("💡 Pentru MacBook sau alte laptopuri:")
        print(f"   python worker.py --master http://<IP-TAILSCALE>:{MASTER_PORT} --id worker-mac")
        print()
        print("⚠️  Apasă Ctrl+C pentru a opri toate serviciile")
        print("=" * 70)
        print()
        
        # Așteptăm
        while True:
            time.sleep(1)
            
            # Verificăm dacă procesele mai rulează
            for i, p in enumerate(processes):
                if p.poll() is not None:
                    print(f"⚠️  Procesul {i} s-a oprit (cod: {p.poll()})")
    
    except KeyboardInterrupt:
        print()
        print("\n🛑 Oprire servicii...")
        for p in processes:
            if p.poll() is None:
                p.terminate()
                p.wait(timeout=5)
        print("✅ Toate serviciile oprite")
    
    except Exception as e:
        print(f"\n❌ Eroare: {e}")
        for p in processes:
            if p.poll() is None:
                p.terminate()

if __name__ == '__main__':
    main()
