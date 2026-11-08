# NOVA - Distributed Processing System

Sistem distribuit Master-Worker cu Invite System integrat.

## 🎯 Ce face NOVA?

**Scenariu simplu:**
1. Tu ești pe laptopul Windows (Master + Dashboard)
2. Vrei ca prietenul tău să devină worker cu MacBook-ul
3. Generezi un link de invitație în dashboard
4. Trimiti linkul prin WhatsApp/Email
5. Prietenul tău dă click → descarcă worker → se conectează automat → procesează taskuri

## 🚀 Quick Start

### Tu (Laptop Master - Windows):

```powershell
# 1. Clone repo
git clone https://github.com/ananaslafelie/NimbusNova.git
cd NimbusNova

# 2. Instalează dependențele
pip install -r requirements.txt

# 3. Pornește totul
python nova_dashboard.py

# Sau dublu-click pe START_NOVA.bat
```

**URLs:**
- Dashboard: http://localhost:8090
- Master API: http://localhost:8003

### Pasul 2: Generează invitație

1. Deschide http://localhost:8090
2. Click pe "Invită în echipă" în sidebar
3. Introdu numele echipei și IP-ul tău (sau Tailscale IP)
4. Click "Generează Link"
5. Copiază linkul și trimite-l prietenului

**Exemplu link:**
```
http://100.64.12.34:8090/join/ABC123XYZ
```

### Prietenul tău (MacBook):

1. Deschide linkul primit în browser
2. Click pe "Descarcă Worker"
3. Salvează `nova_worker.py`
4. Rulează în terminal:

```bash
# Instalează dependențe
pip install requests

# Rulează worker
python nova_worker.py
```

**✅ GATA!** Se conectează automat la tine și începe să proceseze taskuri!

## 📊 Dashboard

**Vezi în timp real:**
- ✅ Workeri conectați (inclusiv MacBook)
- 📁 Taskuri în coadă
- ⚡ Progres procesare
- 📈 Statistici

**Features:**
- Upload drag & drop
- Progress bar real-time
- Invite system
- Toast notifications
- Design futurist glassmorphism

## 🌐 Setup cu Tailscale (Recomandat)

### 1. Instalează pe ambele laptopuri
- https://tailscale.com/download
- Login cu același cont

### 2. Află IP-ul Tailscale
```powershell
# Pe Windows
tailscale ip -4
# Output: 100.64.x.x
```

### 3. Folosește IP-ul Tailscale
Când generezi invitația, folosește `100.64.x.x` în loc de `localhost`

### 4. Funcționează de oriunde!
Chiar dacă sunteți în rețele diferite sau la distanță.

## 🎨 Design

- **Culori:** Purple (#6366f1), Pink (#ec4899), Blue (#8b5cf6)
- **Style:** Glassmorphism, wave animations, glow orbs
- **Fonts:** Inter

## 📁 Fișiere importante

- `nova_dashboard.py` - Dashboard principal (port 8090)
- `nova_worker.py` - Generat automat din invitație
- `master.py` - API Master (port 8003)
- `requirements.txt` - Dependențe

## 🛠️ Troubleshooting

### "Connection refused"
```powershell
# Verifică dacă Master rulează
python master.py --host 0.0.0.0 --port 8003

# Verifică firewall
netsh advfirewall set allprofiles state off
```

### Worker nu se conectează
```bash
# Testează conexiunea
curl http://IP_MASTER:8003/status

# Sau
python -c "import requests; print(requests.get('http://IP:8003/status').json())"
```

### Dashboard nu răspunde
```powershell
netstat -ano | findstr 8090
taskkill /F /IM python.exe
python nova_dashboard.py
```

## 💡 Cum funcționează Invite System

```
[Master] --generează--> [Link: /join/ABC123]
     ↑
[Link trimis] ----------> [Prieten]
     ↑
[Worker auto] <---------- [Click + Download]
     ↑
[Conectat] -------------> [Procesează taskuri]
     ↑
[Rezultate] ------------> [Dashboard]
```

## 🎯 Use Case-uri

### Hackathon:
- Laptopuri în săli diferite
- Taskuri distribuite automat
- Monitorizare în timp real

### Procesare date:
- Fișiere JSON/CSV mari
- Procesare paralelă
- Rezultate combinate

### Cluster DIY:
- Laptopuri vechi devin workeri
- Procesare distribuită
- Zero config pentru workeri

## 📞 Suport

**URLs:**
- GitHub: https://github.com/ananaslafelie/NimbusNova
- Dashboard: http://localhost:8090
- Join: http://IP:8090/join/CODE

## 🎉 Succes!

Acum ai un sistem distribuit complet funcțional cu:
✅ Dashboard modern
✅ Invite system
✅ Upload funcțional
✅ Real-time progress
✅ Multi-platform (Win/Mac)

**Hackathon ready!** 🚀
