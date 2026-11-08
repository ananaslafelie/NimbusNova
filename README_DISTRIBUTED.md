# QA DNA - Sistem Distribuit Multi-Laptop

## Arhitectură
```
Laptop 1 (Windows - Master + Dashboard)
├── Master API: http://localhost:8003
└── Dashboard: http://localhost:8090

Laptop 2 (MacBook - Worker)
└── Worker: se conectează la IP_LAPTOP1:8003
```

## Setup Master (Laptop Principal)

### 1. Pornește Master
```powershell
python master.py --host 0.0.0.0 --port 8003
```

### 2. Pornește Dashboard
```powershell
python dashboard_wave.py
```

### 3. Află IP-ul tău
```powershell
# Windows
ipconfig | findstr "IPv4"

# Sau
python -c "import socket; s=socket.socket(); s.bind(('',0)); print(s.getsockname()[0])"
```

**Exemplu IP**: `192.168.0.100`

## Setup Worker (MacBook/Alt Laptop)

### 1. Clone repo
```bash
git clone https://github.com/ananaslafelie/NimbusNova.git
cd NimbusNova
```

### 2. Instalare dependențe
```bash
pip install -r requirements.txt
```

### 3. Pornește Worker
```bash
# Înlocuiește IP_MASTER cu IP-ul din pasul 3 de mai sus
python worker.py --master http://192.168.0.100:8003 --id worker-macbook
```

## Setup cu Tailscale (Recomandat pentru Hackathon)

### 1. Instalează Tailscale pe ambele laptopuri
- https://tailscale.com/download
- Autentificare cu același cont Google

### 2. Află IP Tailscale
```powershell
tailscale ip -4
# Output: 100.x.y.z
```

### 3. Master (Laptop 1)
```powershell
python master.py --host 0.0.0.0 --port 8003
python dashboard_wave.py
```

### 4. Worker (MacBook)
```bash
python worker.py --master http://100.x.y.z:8003 --id worker-macbook
```

## URLs pentru acces

### De pe Laptop Master (Windows):
- Dashboard: http://localhost:8090
- Master API: http://localhost:8003

### De pe MacBook:
- Dashboard: http://192.168.0.100:8090 (sau IP Tailscale)
- Poți vedea dashboard-ul în browser!

## Flow Complet

1. **Laptop Master** pornește Master + Dashboard
2. **MacBook** pornește Worker și se conectează la Master
3. **Dashboard** (de pe orice laptop) arată:
   - Workeri conectați (inclusiv MacBook)
   - Taskuri în timp real
   - Upload funcțional

## Testare Upload

1. Deschide Dashboard: http://localhost:8090 (sau IP)
2. Trage un fișier JSON în zona de upload
3. Task-ul se distribuie automat la toți workerii
4. Vezi progresul în timp real

## Troubleshooting

### Eroare "Connection refused"
```powershell
# Verifică dacă Master rulează
netstat -ano | findstr 8003

# Verifică firewall
# Windows: Control Panel → Firewall → Allow apps
```

### Worker nu se conectează
```powershell
# Testează conexiunea
curl http://IP_MASTER:8003/status

# Sau din Python
python -c "import requests; print(requests.get('http://IP_MASTER:8003/status').json())"
```

### Dashboard nu vede workerii
- Verifică că Master e pornit pe `0.0.0.0` (nu `localhost`)
- Verifică porturile în firewall
- Folosește Tailscale pentru siguranță

## Fișiere importante
- `dashboard_wave.py` - Dashboard principal
- `master.py` - API Master
- `worker.py` - Client Worker
- `requirements.txt` - Dependențe

## Next Agent - Ce să faci:
1. Testează setup-ul pe 2 laptopuri
2. Verifică că upload-ul funcționează cross-machine
3. Adaugă autentificare dacă e nevoie
4. Îmbunătățește UI-ul
