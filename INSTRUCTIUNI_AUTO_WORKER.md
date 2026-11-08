# NOVA - Auto-Worker Setup (Fără comenzi manuale!)

## 🎯 Ce e nou?

**Înainte:** Trebuia să ruleze `pip install requests` și `python worker.py` manual

**Acum:** O singură comandă copy-paste și rulează automat!

---

## 🚀 Cum funcționează (Super simplu!)

### Tu (Windows - Master + Dashboard):

```powershell
# 1. Pornește NOVA
python nova_dashboard.py

# Sau dublu-click
START_NOVA.bat
```

### 2. Generează invitație:
1. Deschide http://localhost:8090
2. Click **"Invită în echipă"** în sidebar
3. Completează numele echipei și IP-ul tău
4. Click **"Generează Link"**
5. Copiază linkul (ex: `http://100.x.x.x:8090/join/ABC123`)

### 3. Trimite linkul prietenului
- WhatsApp
- Email
- SMS
- etc.

---

## 💻 Prietenul tău (MacBook):

### OPȚIUNEA 1: One-Liner (Cel mai simplu!)

**Doar COPIAZĂ și LIPEȘTE în Terminal:**

```bash
curl -sSL http://IP_TAU:8090/install-worker | python3 - IP_TAU
```

**Exemplu:**
```bash
curl -sSL http://100.64.12.34:8090/install-worker | python3 - 100.64.12.34
```

**Ce face:**
1. ✅ Descarcă automat scriptul
2. ✅ Instalează dependențele (requests)
3. ✅ Se conectează la Master
4. ✅ Începe să proceseze taskuri

**Totul automat!**

---

### OPȚIUNEA 2: Download Manual

1. Deschide linkul primit în browser
2. Click **"↓ Descarcă auto_worker.py"**
3. Salvează fișierul
4. Rulează:
```bash
python3 auto_worker.py
```

---

## 🎉 Rezultat

**După 10 secunde:**
- ✅ Workerul e conectat
- ✅ Dashboard îl arată ca "Online"
- ✅ Poți face upload și taskurile se distribuie automat

---

## 💡 De ce e mai bun?

| Înainte | Acum |
|---------|------|
| `pip install requests` | Automat |
| `python worker.py` | Automat |
| Configurat manual | IP pre-configurat |
| 3 pași | 1 comandă |
| Poate greși | Copy-paste simplu |

---

## 🔧 Troubleshooting

### "curl: command not found"
```bash
# Pe MacBook, curl e deja instalat
# Dacă nu:
brew install curl
```

### "python3: command not found"
```bash
# Instalează Python
brew install python3
```

### "Nu se conectează"
```bash
# Verifică IP-ul
curl http://IP:8003/status

# Sau testează
curl -sSL http://IP:8090/install-worker | python3 - IP
```

---

## 🎯 Workflow complet

```
Tu generezi link ──► Trimiti pe WhatsApp ──► Prietenul dă copy-paste la comandă
                                              │
                                              ▼
                                        Rulează automat
                                              │
                                              ▼
                                        Conectat în 10 sec
                                              │
                                              ▼
                                        Procesează taskuri 🎉
```

---

## 📝 Comanda magică

```bash
curl -sSL http://IP:8090/install-worker | python3 - IP
```

**Unde înlocuiești:**
- `IP` = IP-ul tău (ex: 100.64.12.34 sau 192.168.0.100)

---

## ✅ Status

**GATA DE HACKATHON!**

- Dashboard: http://localhost:8090 ✅
- Auto-install worker ✅
- One-liner command ✅
- Zero config pentru prieteni ✅

**Testat și funcțional!** 🚀
