#!/usr/bin/env python3
"""
BRIDGE - MacBook Side (Executor)
Rulează pe MacBook și execută comenzile de la Windows
"""

import json
import time
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None, background=False):
    """Execută comandă și returnează output"""
    try:
        if background:
            # Pornire în background
            process = subprocess.Popen(
                cmd, shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                cwd=cwd
            )
            return f"PID: {process.pid}", "", 0
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
            return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def update_status(macbook_ready, worker_running, current_action, errors=None):
    """Updatează status în protocol"""
    try:
        with open('bridge_protocol.json', 'r') as f:
            protocol = json.load(f)
        
        protocol['last_update'] = datetime.now().isoformat()
        protocol['status']['macbook_ready'] = macbook_ready
        protocol['status']['worker_running'] = worker_running
        protocol['status']['current_action'] = current_action
        protocol['status']['last_heartbeat'] = datetime.now().isoformat()
        
        if errors:
            protocol['status']['connection_errors'].append({
                'time': datetime.now().isoformat(),
                'error': str(errors)
            })
        
        with open('bridge_protocol.json', 'w') as f:
            json.dump(protocol, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Eroare update status: {e}")
        return False

def mark_command_complete(cmd_id, success=True, output=""):
    """Marchează comandă ca finalizată"""
    try:
        with open('bridge_protocol.json', 'r') as f:
            protocol = json.load(f)
        
        # Mută din pending în completed
        for cmd in protocol['commands']['pending']:
            if cmd['id'] == cmd_id:
                cmd['status'] = 'completed'
                cmd['completed_at'] = datetime.now().isoformat()
                cmd['success'] = success
                cmd['output'] = output
                protocol['commands']['completed'].append(cmd)
                protocol['commands']['pending'].remove(cmd)
                break
        
        with open('bridge_protocol.json', 'w') as f:
            json.dump(protocol, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Eroare marcare comandă: {e}")
        return False

def execute_start_worker(params):
    """Pornește workerul"""
    print("🚀 Pornire worker MacBook...")
    
    master_url = params.get('master_url', 'http://100.64.66.23:8003')
    worker_id = params.get('worker_id', 'worker-macbook')
    
    # Comandă pentru pornire worker
    cmd = f"python3 worker.py --master {master_url} --id {worker_id}"
    
    print(f"   Execut: {cmd}")
    print("   ⚠️  Workerul rulează în background!")
    print("   Pentru a-l vedea: tail -f worker.log")
    
    # Pornire în background cu log
    stdout, stderr, rc = run_command(f"{cmd} > worker.log 2>&1 &", background=True)
    
    if rc == 0:
        return True, f"Worker pornit. PID: {stdout}"
    else:
        return False, f"Eroare: {stderr}"

def execute_stop_worker():
    """Oprește workerul"""
    print("⏹️  Oprire worker MacBook...")
    
    # Găsește și omoară procesul worker
    stdout, stderr, rc = run_command("pkill -f 'worker.py --master'")
    
    if rc == 0:
        return True, "Worker oprit"
    else:
        return False, f"Eroare oprire: {stderr}"

def process_pending_commands():
    """Procesează comenzile în așteptare"""
    try:
        with open('bridge_protocol.json', 'r') as f:
            protocol = json.load(f)
        
        pending = protocol['commands']['pending']
        
        if not pending:
            print("📭 Nicio comandă în așteptare")
            return
        
        print(f"📬 {len(pending)} comandă(e) de executat")
        
        for cmd in pending[:]:
            cmd_id = cmd['id']
            command = cmd['command']
            params = cmd.get('params', {})
            
            print(f"\n🔧 Executare: {command}")
            update_status(True, True, f"Executare {command}")
            
            success = False
            output = ""
            
            if command == "START_WORKER":
                success, output = execute_start_worker(params)
                
            elif command == "STOP_WORKER":
                success, output = execute_stop_worker()
                
            elif command == "CUSTOM":
                custom_cmd = params.get('command', '')
                stdout, stderr, rc = run_command(custom_cmd)
                success = (rc == 0)
                output = stdout if success else stderr
                
            else:
                output = f"Comandă necunoscută: {command}"
            
            mark_command_complete(cmd_id, success, output)
            print(f"   {'✅' if success else '❌'} {output[:100]}")
            
    except Exception as e:
        print(f"Eroare procesare comenzi: {e}")
        update_status(True, False, f"Eroare: {str(e)}", e)

def main():
    """Executor principal MacBook"""
    print("=" * 60)
    print("🌉 QA DNA - Git Bridge Executor (MacBook)")
    print("=" * 60)
    print()
    print("Acest script:")
    print("  1. Citește comenzile din bridge_protocol.json")
    print("  2. Execută ce găsește")
    print("  3. Scrie rezultatele înapoi")
    print("  4. Fă git push să trimiți rezultatele")
    print()
    
    # Verifică conexiunea la Windows
    print("🔗 Verificare conexiune Tailscale...")
    stdout, stderr, rc = run_command("ping -c 1 100.64.66.23")
    
    if rc == 0:
        print("   ✅ Conexiune OK la Windows (100.64.66.23)")
        update_status(True, False, "Conexiune OK, așteaptă comenzi")
    else:
        print("   ❌ Nu pot ping-ui Windows-ul!")
        print("   Verifică: tailscale status")
        update_status(False, False, "Eroare conexiune")
        return
    
    print()
    print("📋 Procesare comenzi...")
    process_pending_commands()
    
    print()
    print("=" * 60)
    print("🔔 INSTRUCȚIUNI:")
    print("   1. Editează fișierul: git add . && git commit -m 'MacBook update'")
    print("   2. Trimite pe GitHub: git push origin master")
    print("   3. Windows va vedea rezultatele când face git pull")
    print("=" * 60)
    print()
    print("✅ Gata! Comenzile au fost procesate.")

if __name__ == "__main__":
    main()
