# QA DNA - Distributed Processing System

Sistem distribuit Master-Worker pentru procesare paralelă de task-uri.

## Quick Start

### Dublu-click pentru a porni totul:
```
START_SYSTEM.bat
```

### Manual:
```powershell
# Terminal 1 - Master
python master.py --host 0.0.0.0 --port 8003

# Terminal 2 - Dashboard
python dashboard_wave.py

# Terminal 3 - Worker (pe MacBook/alt laptop)
python worker.py --master http://IP_MASTER:8003 --id worker-1
```

## URLs
- Dashboard: http://localhost:8090
- Master API: http://localhost:8003/status

## Features
- Upload drag & drop (JSON/CSV/TXT)
- Real-time progress tracking
- Multi-worker support
- Glassmorphism UI with wave animations
- Cross-platform (Windows/Mac/Linux)

## Structură
- `dashboard_wave.py` - Dashboard modern (port 8090)
- `master.py` - API Master (port 8003)
- `worker.py` - Client Worker
- `requirements.txt` - Dependențe

## Pentru Hackathon / Multi-Laptop
Vezi: [README_DISTRIBUTED.md](README_DISTRIBUTED.md)

## Credits
Built for QA DNA Hackathon - Team NimbusNova
