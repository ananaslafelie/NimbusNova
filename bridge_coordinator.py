#!/usr/bin/env python3
"""
BRIDGE - Windows Side (Coordonator)
Rulează pe Windows și coordonează MacBook-ul
"""

import json
import time
import subprocess
import os
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """Execută comandă și returnează output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def update_protocol(macbook_status, action):
    """Updatează fișierul de protocol"""
    try:
        with open('bridge_protocol.json', 'r') as f:
            protocol = json.load(f)
        
        protocol['last_update'] = datetime.now().isoformat()
        protocol['status']['current_action'] = action
        
        if macbook_status:
            protocol['status'].update(macbook_status)
        
        with open('bridge_protocol.json', 'w') as f:
            json.dump(protocol, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Eroare update protocol: {e}")
        return False

def send_command_to_macbook(command, params=None):
    """Trimite comandă către MacBook"""
    with open('bridge_protocol.json', 'r') as f:
        protocol = json.load(f)
    
    cmd_obj = {
        'id': f"cmd_{int(time.time())}",
        'timestamp': datetime.now().isoformat(),
        'command': command,
        'params': params or {},
        'status': 'pending'
    }
    
    protocol['commands']['pending'].append(cmd_obj)
    
    with open('bridge_protocol.json', 'w') as f:
        json.dump(protocol, f, indent=2)
    
    print(f"✅ Comandă trimisă: {command}")
    print("   Acum fă GIT PUSH pentru a trimite la MacBook")
    return cmd_obj['id']

def check_macbook_response():
    """Verifică răspunsul de la MacBook"""
    try:
        # Pull ultima versiune
        run_command("git pull origin master")
        
        with open('bridge_protocol.json', 'r') as f:
            protocol = json.load(f)
        
        return protocol.get('status', {})
    except Exception as e:
        print(f"Eroare citire răspuns: {e}")
        return None

def main():
    """Coordonator principal"""
    print("=" * 60)
    print("🌉 QA DNA - Git Bridge Coordonator (Windows)")
    print("=" * 60)
    print()
    print("Acest script te ajută să coordonezi MacBook-ul")
    print()
    
    # Verifică starea curentă
    print("📋 Verificare stare curentă...")
    status = check_macbook_response()
    
    if status:
        print(f"   MacBook ready: {status.get('macbook_ready', False)}")
        print(f"   Worker running: {status.get('worker_running', False)}")
        print(f"   Last action: {status.get('current_action', 'N/A')}")
    else:
        print("   ⚠️  Nu am găsit status de la MacBook")
    
    print()
    print("🔧 Opțiuni:")
    print("   1. Trimite comandă START WORKER la MacBook")
    print("   2. Trimite comandă STOP WORKER")
    print("   3. Verifică status MacBook")
    print("   4. Trimite comandă CUSTOM")
    print("   5. Ieșire")
    print()
    
    choice = input("Alege (1-5): ").strip()
    
    if choice == "1":
        print("\n📤 Trimitere comandă START WORKER...")
        print("   Comandă: pornire worker pe MacBook")
        print("   Parametri:")
        print("     - master_ip: 100.64.66.23:8003")
        print("     - worker_id: worker-macbook")
        print()
        
        cmd_id = send_command_to_macbook("START_WORKER", {
            "master_url": "http://100.64.66.23:8003",
            "worker_id": "worker-macbook",
            "command": "python3 worker.py --master http://100.64.66.23:8003 --id worker-macbook"
        })
        
        print(f"\n✅ Comandă {cmd_id} creată!")
        print("\n📋 INSTRUCȚIUNI pentru tine:")
        print("   1. Deschide terminal pe MacBook")
        print("   2. Rulează: cd ~/Desktop/NimbusNova")
        print("   3. Rulează: git pull origin master")
        print("   4. Rulează: python3 bridge_macbook.py")
        print("   5. MacBook-ul va citi comanda și va porni workerul")
        print("   6. Așteaptă 10 secunde")
        print("   7. Rulează pe Windows: python bridge_check.py")
        
    elif choice == "2":
        print("\n📤 Trimitere comandă STOP WORKER...")
        cmd_id = send_command_to_macbook("STOP_WORKER", {})
        print(f"✅ Comandă {cmd_id} creată!")
        
    elif choice == "3":
        print("\n📊 Status MacBook:")
        if status:
            print(json.dumps(status, indent=2))
        else:
            print("   Nu am date. Asigură-te că MacBook a rulat bridge_macbook.py")
            
    elif choice == "4":
        custom_cmd = input("Comandă custom: ")
        cmd_id = send_command_to_macbook("CUSTOM", {"command": custom_cmd})
        print(f"✅ Comandă {cmd_id} creată!")
        
    elif choice == "5":
        print("La revedere!")
        return
    
    print("\n" + "=" * 60)
    print("🔔 Nu uita să faci GIT PUSH pentru a trimite comenzile!")
    print("=" * 60)

if __name__ == "__main__":
    main()
