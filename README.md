# QA DNA - Multithreaded | Arhitectură Distribuită PULL-Based

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-00a3e0.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Arhitectură ultra-robustă, fault-tolerant, pull-based pentru procesare distribuită de task-uri grele.**

---

## 🎯 De ce PULL-Based?

Pentru hackathon-ul "QA DNA - Multithreaded", am ales arhitectura **PULL-Based** pentru a evita blocajele de firewall pe laptopurile workerilor:

- ✅ **DOAR Masterul** expune endpoint-uri HTTP (port deschis)
- ✅ **Workerii** fac cereri de ieșire către Master (polling) - zero probleme firewall
- ✅ **Self-healing**: Workerii offline sunt detectați automat, task-urile redistribute
- ✅ **Reasamblare automată**: Rezultatele parțiale se reunesc în output final

---

## 🏗️ Arhitectură

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER (Broker Central)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ /register    │  │ /get-task    │  │ /results/{id}│        │
│  │ /heartbeat   │  │ /submit-task │  │ /status      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                               │
│  • Task Ingestion → chunks (CHUNK_SIZE=10 iteme)            │
│  • Task Dispenser (FIFO + resource-aware)                    │
│  • Self-Healing (12s heartbeat timeout, 30s task timeout)    │
│  • Result Reassembly                                         │
└─────────────────────────────────────────────────────────────┘
                               ▲ │
                               │ │ PULL (worker cere task)
                               │ │ PUSH (worker trimite rezultat)
          ┌────────────────────┘ └────────────────────┐
          │                                          │
┌─────────┴──────────────┐              ┌────────────┴──────────┐
│      WORKER-1          │              │      WORKER-2         │
│  • Se înregistrează    │              │  • Se înregistrează   │
│  • Heartbeat 3-5s      │              │  • Heartbeat 3-5s     │
│  • Poll /get-task      │              │  • Poll /get-task      │
│  • Procesează în       │              │  • Procesează în      │
│    thread separat      │              │    thread separat     │
│  • Submit rezultat     │              │  • Submit rezultat    │
└────────────────────────┘              └───────────────────────┘
```

---

## 🚀 Quick Start

### 1. Instalare Dependențe

```bash
pip install -r requirements.txt
```

**Dependențe:**
- `fastapi>=0.110` + `uvicorn[standard]` - server HTTP async
- `httpx>=0.27` - client HTTP pentru workeri
- `psutil>=5.9` - monitorizare resurse (CPU, RAM)
- `rich>=13.7` - loguri colorate și vizuale

### 2. Rulează Local (Test pe un singur laptop)

**Terminal 1 - Master:**
```powershell
$env:PYTHONUTF8='1'; python master.py --port 8000
```

**Terminal 2 - Worker 1:**
```powershell
$env:PYTHONUTF8='1'; python worker.py --master http://localhost:8000 --id worker-1
```

**Terminal 3 - Worker 2:**
```powershell
$env:PYTHONUTF8='1'; python worker.py --master http://localhost:8000 --id worker-2
```

**Terminal 4 - Test Pipeline:**
```powershell
$env:PYTHONUTF8='1'; python test_pipeline.py --master http://localhost:8000 --items 100
```

### 3. Dashboard Live

Accesează în browser:
```
http://127.0.0.1:8000/status
```

---

## 🌐 Deployment cu Tailscale (Echipa Distribuită)

### Pe MASTER (laptopul tău):

```powershell
# 1. Află IP-ul Tailscale
tailscale ip -4
# Output: 100.x.y.z

# 2. Rulează masterul pe IP-ul Tailscale
$env:PYTHONUTF8='1'; python master.py --host 0.0.0.0 --port 8002
```

### Pe WORKERI (alte laptopuri din echipă):

```powershell
# 1. Clonează repo-ul
git clone https://github.com/ananaslafelie/NimbusNova.git
cd NimbusNova
pip install -r requirements.txt

# 2. Rulează workerul (înlocuiește 100.x.y.z cu IP-ul masterului)
$env:PYTHONUTF8='1'; python worker.py --master http://100.x.y.z:8002 --id worker-[nume-laptop]
```

### Pe orice laptop (trimite task-uri):

```powershell
$env:PYTHONUTF8='1'; python test_pipeline.py --master http://100.x.y.z:8002 --items 1000
```

---

## 📊 Specificații Tehnice

| Caracteristică | Valoare | Descriere |
|----------------|---------|-----------|
| **HEARTBEAT_TIMEOUT** | 12 sec | Worker marcat OFFLINE dacă nu trimite ping |
| **TASK_TIMEOUT** | 30 sec | Chunk requeue-uit dacă nu primește rezultat |
| **CHUNK_SIZE** | 10 iteme | Dimensiunea unei bucăți de task |
| **MAX_ATTEMPTS** | 3 încercări | După 3 eșecuri, chunk → dead-letter |
| **IDLE_SLEEP** | 1 sec | Pausă între poll-uri când nu e de lucru |

---

## 🔄 Flow-ul Complet

1. **Master** primește task-ul (100 iteme) → îl sparge în 10 chunks
2. **Workerii** poll-uiesc `/get-task` și primesc chunks
3. **Workerii** procesează în thread separat (`asyncio.to_thread`)
4. **Workerii** trimit rezultatele la `/submit-result`
5. **Master** reasamblează rezultatele când toate chunks sunt gata
6. **Clientul** poll-uiește `/results/{task_id}` până primește status COMPLETED

---

## 🛡️ Fault Tolerance

- ✅ **Worker crash**: Task-urile assigned se requeue-uiesc automat în 30s
- ✅ **Network hiccup**: Workerii retry cu backoff exponențial
- ✅ **Duplicăți rezultate**: Ignorate idempotent (at-least-once delivery)
- ✅ **Dead-letter**: Chunks care eșuează de 3 ori marcate ca FAILED

---

## 📝 Exemplu Output

```
🚀 Submit
  master=http://localhost:8002 • items=100 • chunks=10
  task_id=task-1794080647-0000

⏱ 0s status=COMPLETED chunks=10/10
🎉 task-1794080647-0000 — COMPLETED in 1.0s

┌──────────┬─────────────────┐
│ Worker   │ Iteme procesate │
├──────────┼─────────────────┤
│ worker-1 │              50 │
│ worker-2 │              50 │
└──────────┴─────────────────┘
```

---

## 🔧 Comenzi Utile

```powershell
# Verifică procese Python
Get-Process | Where-Object { $_.ProcessName -eq "python" }

# Oprește toate procesele Python
Get-Process | Where-Object { $_.ProcessName -eq "python" } | Stop-Process -Force

# Verifică portul 8000
netstat -ano | findstr :8000

# Test cu curl
curl http://localhost:8000/status
```

---

## 🤝 Contribuitori

- **Vlad** - Arhitectură & Implementare Master/Worker
- **Echipa QA DNA** - Testare & Validare

---

## 📄 Licență

MIT License - vezi [LICENSE](LICENSE) pentru detalii.

---

**Built with ❤️ for Hackathon**
