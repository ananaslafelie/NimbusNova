# NOVA - Distributed Processing System

Sistem distribuit Master-Worker cu Invite System - trimite link, devine worker automat!

## 🎯 Scenariul tău

**Tu pe Windows (Master)** → **Generezi link** → **Trimiti prietenului** → **El dă click pe MacBook** → **Devine worker automat**

## 🚀 Quick Start

### Tu (Windows - Master + Dashboard):

```powershell
# Pornește totul
python nova_dashboard.py

# Sau dublu-click
START_NOVA.bat
```

**Accesează:** http://localhost:8090

### 2. Generează invitație:
1. Click "Invită în echipă" în sidebar
2. Completează nume + IP (sau Tailscale IP)
3. Click "Generează Link"
4. Copiază și trimite

### Prietenul tău (MacBook):

```bash
# Deschide linkul primit în browser
# Click "Descarcă Worker"
# Rulează:

pip install requests
python nova_worker.py
```

**✅ GATA!** Se conectează automat și procesează taskuri!

## 🎨 Features

- 🌊 **Design futurist** - Glassmorphism, wave animations
- 📤 **Upload drag & drop** - JSON/CSV/TXT
- 🔔 **Invite system** - Trimite link, devine worker
- 📊 **Real-time dashboard** - Vezi tot live
- ⚡ **Progress tracking** - Urmărește taskuri
- 🔗 **Cross-platform** - Windows + Mac

## 📁 Fișiere

- `nova_dashboard.py` - Dashboard (port 8090)
- `master.py` - API Master (port 8003)
- `nova_worker.py` - Generat automat din invitație
- `requirements.txt` - Dependențe

## 🌐 URLs

- **Dashboard:** http://localhost:8090
- **Master:** http://localhost:8003
- **Join:** http://IP:8090/join/CODE

## 💡 Cum funcționează

```
Tu generezi link → Trimite pe WhatsApp → Prietenul dă click → Descarcă → Conectat → Procesează
```

## 📖 Documentație completă

Vezi: [README_NOVA.md](README_NOVA.md)

## 🎉 Status

✅ **FUNCȚIONAL** - Ready for hackathon!

**Built with ❤️ for QA DNA**
