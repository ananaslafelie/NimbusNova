# QA DNA - Cum faci sistem distribuit pe 2 laptopuri

## Scenariul tău:
- Laptop 1 (Windows) = Master + Dashboard
- Laptop 2 (MacBook) = Worker
- Ambele văd aceeași interfață
- Upload de pe Windows → Processing pe MacBook

---

## PASUL 1: Pe Laptop Windows (Master)

### A. Pregătește repo-ul
```powershell
git clone https://github.com/ananaslafelie/NimbusNova.git
cd NimbusNova
pip install -r requirements.txt
```

### B. Află IP-ul tău
```powershell
# Opțiunea 1 - WiFi
ipconfig | findstr "IPv4"
# Output: 192.168.0.100

# Opțiunea 2 - Tailscale (RECOMANDAT)
tailscale ip -4
# Output: 100.x.y.z
```

**IMPORTANT**: Folosește IP-ul Tailscale (100.x.y.z) - funcționează oriunde!

### C. Pornește Master + Dashboard
```powershell
# Terminal 1
python master.py --host 0.0.0.0 --port 8003

# Terminal 2  
python dashboard_wave.py

# Sau dublu-click pe:
START_SYSTEM.bat
```

### D. URLs pe Laptop Windows
```
Dashboard: http://localhost:8090
Master:    http://localhost:8003
```

---

## PASUL 2: Pe MacBook (Worker)

### A. Clone repo
```bash
git clone https://github.com/ananaslafelie/NimbusNova.git
cd NimbusNova
pip install -r requirements.txt
```

### B. Pornește Worker
```bash
# Înlocuiește 100.x.y.z cu IP-ul de la pasul 1B
python worker.py --master http://100.x.y.z:8003 --id worker-macbook

# Sau cu IP WiFi:
python worker.py --master http://192.168.0.100:8003 --id worker-macbook
```

### C. Dashboard de pe MacBook
```
http://100.x.y.z:8090
```

**Da! Poți vedea Dashboard-ul și de pe MacBook!**

---

## PASUL 3: Testare

### De pe Laptop Windows:
1. Deschide http://localhost:8090
2. Dashboard arată: "1 Worker online" (MacBook)
3. Trage un fișier JSON în upload zone
4. Vezi progresul în timp real

### De pe MacBook:
1. Deschide http://100.x.y.z:8090 în browser
2. Vezi același Dashboard!
3. Vezi worker-ul tău conectat
4. Dashboard funcționează identic

### Ce se întâmplă:
```
[Windows] ──upload──→ [Master] ──task──→ [MacBook]
                    ↑
              [Dashboard] ←── ambele văd
```

---

## Setup cu Tailscale (Cel mai bun!)

### 1. Instalează Tailscale pe ambele laptopuri
- https://tailscale.com/download
- Login cu același cont Google

### 2. Pe Windows
```powershell
tailscale ip -4
# 100.64.12.34

python master.py --host 0.0.0.0 --port 8003
python dashboard_wave.py
```

### 3. Pe MacBook
```bash
tailscale ip -4
# 100.64.56.78

python worker.py --master http://100.64.12.34:8003 --id worker-macbook
```

### 4. Accesează de oriunde
```
http://100.64.12.34:8090  ← Dashboard
http://100.64.12.34:8003  ← Master API
```

**Funcționează chiar dacă sunteți în rețele diferite!**

---

## Comenzi rapide

### Windows (Master + Dashboard)
```powershell
# Totul deodată
START_SYSTEM.bat

# Sau manual:
python master.py --host 0.0.0.0 --port 8003
python dashboard_wave.py
```

### MacBook (Worker)
```bash
python worker.py --master http://IP_WINDOWS:8003 --id worker-macbook
```

---

## Troubleshooting

### "Connection refused"
```powershell
# Verifică firewall
netsh advfirewall firewall add rule name="QA DNA Master" dir=in action=allow protocol=tcp localport=8003

# Sau dezactivează temporar
netsh advfirewall set allprofiles state off
```

### "Nu văd workerul"
```powershell
# Verifică IP-ul
ipconfig

# Testează conexiunea
curl http://IP_WINDOWS:8003/status

# Pornește Master pe 0.0.0.0 (nu localhost!)
python master.py --host 0.0.0.0 --port 8003
```

### Dashboard nu răspunde
```powershell
# Verifică portul
netstat -ano | findstr 8090

# Oprește și repornește
taskkill /F /IM python.exe
python dashboard_wave.py
```

---

## Verificare rapidă

### Pe Windows:
```powershell
# Ar trebui să vezi:
curl http://localhost:8003/status
# {"workers": [...], "queue_len": 0, "tasks": []}

curl http://localhost:8090
# HTML page
```

### Pe MacBook:
```bash
# Ar trebui să te poți conecta:
curl http://IP_WINDOWS:8003/status

# Dashboard vizibil:
curl http://IP_WINDOWS:8090
```

---

## Succes!

Acum ai:
✅ Master pe Windows
✅ Worker pe MacBook
✅ Dashboard vizibil de pe ambele
✅ Upload cross-machine
✅ Progress real-time

**Întrebări? Vezi README_DISTRIBUTED.md**
