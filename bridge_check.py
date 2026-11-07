#!/usr/bin/env python3
"""
Verificare status MacBook (rulează pe Windows)
"""

import json
import subprocess
from datetime import datetime

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.returncode

def main():
    print("=" * 60)
    print("🔍 Verificare status MacBook")
    print("=" * 60)
    print()
    
    # Pull ultima versiune
    print("📥 Actualizare de la GitHub...")
    stdout, rc = run_cmd("git pull origin master")
    
    if rc != 0:
        print("   ⚠️  Eroare git pull:", stdout)
    else:
        print("   ✅ Cod actualizat")
    
    print()
    
    # Citește protocol
    try:
        with open('bridge_protocol.json', 'r') as f:
            protocol = json.load(f)
        
        status = protocol.get('status', {})
        
        print("📊 Status MacBook:")
        print(f"   🟢 Ready: {status.get('macbook_ready', False)}")
        print(f"   🖥️  Worker: {status.get('worker_running', False)}")
        print(f"   ⏱️  Last heartbeat: {status.get('last_heartbeat', 'N/A')}")
        print(f"   📝 Acțiune curentă: {status.get('current_action', 'N/A')}")
        
        print()
        
        # Comenzi
        completed = protocol['commands'].get('completed', [])
        if completed:
            print(f"📋 Ultimele comenzi completate ({len(completed)}):")
            for cmd in completed[-3:]:  # Ultimele 3
                print(f"   - {cmd['command']}: {'✅' if cmd.get('success') else '❌'}")
                print(f"     Output: {cmd.get('output', 'N/A')[:80]}")
        else:
            print("   Nicio comandă finalizată încă")
        
        print()
        
        # Verifică workeri
        print("🔗 Verificare workeri în Master...")
        import httpx
        try:
            r = httpx.get('http://localhost:8003/status', timeout=3.0)
            data = r.json()
            workers = data.get('workers', [])
            
            print(f"   ✅ {len(workers)} worker(i) conectați:")
            for w in workers:
                icon = "🖥️" if 'windows' in w['id'] else "🍎"
                print(f"      {icon} {w['id']}: {w['status']} (CPU: {w['cpu']:.0f}%)")
                
        except Exception as e:
            print(f"   ❌ Nu pot accesa Master: {e}")
            print("      Verifică: python master.py rulează?")
            
    except Exception as e:
        print(f"❌ Eroare citire protocol: {e}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
