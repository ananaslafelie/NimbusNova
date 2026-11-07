# QA DNA Desktop - Setup Universal

## 🎯 Obiectiv
Aplicație desktop cu UI modernă pentru procesare distribuită de fișiere între multiple laptopuri (Windows, MacBook, Linux).

---

## 📦 Ce Primești

```
nimbusnovaa/
├── desktop_app/
│   ├── main.py           # Aplicația desktop UI
│   ├── launcher.py       # Pornește tot automat
│   └── __init__.py
├── master.py             # Serverul central (rulează pe Windows)
├── worker.py             # Client worker (rulează pe MacBook)
├── task_manager.py       # Sistem modular de taskuri
├── ai_scanner.py         # Detectare automată fișiere
└── requirements.txt      # Toate dependențele
```

---

## 🚀 Setup Rapid (3 Pași)

### **PAS 1: Download & Instalare**

**Pe toate laptopurile (Windows + MacBook):**

```bash
# Clonează repo-ul
git clone https://github.com/ananaslafelie/NimbusNova.git
cd NimbusNova

# Instalează dependențele
pip install -r requirements.txt
```

**Pe MacBook, dacă `pip` nu există:**
```bash
python3 -m pip install -r requirements.txt
```

---

### **PAS 2: Configurează Tailscale**

**Asigură-te că ambele laptopuri sunt în aceeași rețea Tailscale.**

**Pe Windows (Master):**
```bash
# Află IP-ul tău Tailscale
tailscale ip -4
# Output: 100.x.x.x (notează-l)
```

**Pe MacBook (Worker):**
```bash
# Verifică conexiunea
tailscale status
# Trebuie să vezi laptopul Windows în listă
```

---

### **PAS 3: Rulează Aplicația**

#### **Opțiunea A: Modul Simplu (Doar Windows)**

**Pe Windows:**
```powershell
cd C:\Users\vladi\Desktop\nimbusnovaa
$env:PYTHONUTF8='1'
python desktop_app/launcher.py
```

**Se deschide automat:**
- Master Server pe port 8003
- Worker local
- Browser la `http://localhost:8080`

#### **Opțiunea B: Setup Complet (Windows + MacBook)**

**Terminal 1 - Windows (Master):**
```powershell
cd nimbusnovaa
$env:PYTHONUTF8='1'
python master.py --host 0.0.0.0 --port 8003
```

**Terminal 2 - Windows (Worker local):**
```powershell
cd nimbusnovaa
$env:PYTHONUTF8='1'
python worker.py --master http://localhost:8003 --id worker-windows
```

**Terminal 3 - Windows (Desktop App):**
```powershell
cd nimbusnovaa
$env:PYTHONUTF8='1'
python desktop_app/main.py
```

**Pe MacBook (Worker):**
```bash
cd nimbusnovaa
python3 worker.py --master http://100.x.x.x:8003 --id worker-macbook
```

**Deschide browser pe Windows:**
```
http://localhost:8080
```

---

## 🖥️ Cum Folosești Aplicația

### **1. Selectează Fișierul**
- Click pe "Browse" sau drag & drop fișier
- Suportă: `.py`, `.csv`, `.json`, `.stl`, `.png`, `.jpg`

### **2. Verifică Detectarea Automată**
- AI-ul detectează automat tipul fișierului
- Vezi: plugin recomandat, complexitate, dimensiune

### **3. Configurează**
- Ajustează numărul de chunks (auto-sugerat)
- Alege prioritatea: low / normal / high

### **4. Start Procesare**
- Click "START PROCESARE"
- Vezi progresul în timp real
- Taskul se distribuie automat între workeri

### **5. Rezultate**
- Când e gata, descarcă rezultatul
- Vezi statistici: timp, chunks procesate, workeri folosiți

---

## 📋 Exemple de Fișiere

### **Test simplu - Python Script**
Creează `test_script.py`:
```python
# Calculează ceva intensiv
import time

def process_chunk(data):
    time.sleep(0.1)  # Simulează procesare
    return sum(x**2 for x in data)

if __name__ == "__main__":
    print("Processing...")
```

### **Test - CSV Data**
Creează `data.csv`:
```csv
id,value,category
1,100,A
2,200,B
3,150,A
4,300,C
```

### **Test - 3D Model (STL)**
Descarcă orice fișier `.stl` de pe internet pentru testare.

---

## 🔧 Troubleshooting

### **Eroare "Port already in use"**
```powershell
# Găsește și oprește procesele Python
Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force
```

### **MacBook nu se conectează**
1. Verifică Tailscale: `tailscale status` pe ambele
2. Ping test: `ping 100.x.x.x` (IP Windows)
3. Firewall: Verifică că portul 8003 e deschis

### **Aplicația desktop nu pornește**
```bash
# Instalează manual nicegui
pip install nicegui>=1.4

# Sau pe Mac
pip3 install nicegui>=1.4
```

### **File picker nu funcționează**
- Folosește drag & drop în zona marcată
- Sau scrie calea manual în câmpul text

---

## 🎨 Compilare în EXE (Opțional)

### **Windows:**
```powershell
pip install pyinstaller
pyinstaller --onefile --windowed desktop_app/main.py --name "QADNA-Desktop"
```

### **MacBook:**
```bash
pip3 install pyinstaller
pyinstaller --onefile --windowed desktop_app/main.py --name "QADNA-Desktop"
```

**Rezultat:** Fișier `.exe` (Windows) sau `.app` (Mac) executabil direct!

---

## 🌐 Acces Remote

Dacă vrei să accesezi aplicația de pe alt dispozitiv în aceeași rețea:

**Pe Windows:**
```
http://<IP-Windows>:8080
```

**Exemplu:** `http://192.168.1.100:8080`

---

## ✅ Checklist Funcționalitate

- [ ] Master pornește fără erori
- [ ] Worker local se conectează (status ONLINE)
- [ ] MacBook se conectează (status ONLINE)
- [ ] UI se deschide în browser
- [ ] File picker funcționează
- [ ] Detectare automată funcționează
- [ ] Task se procesează distribuit
- [ ] Rezultatele se reasamblează
- [ ] Progress bar actualizează în timp real

---

## 💡 Sfaturi

1. **Testează întâi local** (doar Windows) înainte să adaugi MacBook
2. **Verifică Tailscale** înainte de orice test distribuit
3. **Folosește fișiere mici** la început (sub 1MB)
4. **Monitorizează logurile** în terminal pentru debugging

---

## 🆘 Support

Dacă ai probleme:
1. Verifică `http://localhost:8003/status` - trebuie să vezi workeri
2. Verifică `http://localhost:8080` - trebuie să vezi UI
3. Trimite screenshot cu erorile din terminal

---

**Gata să testezi?** Urmează pașii de mai sus și spune-mi ce vezi! 🚀
