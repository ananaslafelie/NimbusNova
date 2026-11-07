# QA DNA - Development Roadmap

## 🎯 Viziune
Sistem distribuit modular, cross-platform, cu AI integrat pentru procesare automată de taskuri.

---

## 📊 Arhitectura Actuală (Faza 1 - COMPLETĂ) ✅

### Componente Implementate:

```
📁 nimbusnovaa/
├── master.py              # Server FastAPI (broker)
├── worker.py              # Client worker PULL-based
├── test_pipeline.py       # Script test
├── task_manager.py        # BAZA: Plugin system + distribuție
├── ai_scanner.py          # AI: Detectare automată fișiere
├── integrated_system.py   # Demo integrare completă
├── requirements.txt       # Dependențe
└── README.md
```

### Funcționalități Active:
- ✅ **Task Manager**: Plugin system modular
- ✅ **AI Scanner**: Detectare automată tipuri fișiere
- ✅ **Python Executor**: Primul plugin funcțional
- ✅ **Distribuție**: Taskuri împărțite în chunks
- ✅ **Worker System**: PULL-based, fault-tolerant
- ✅ **Cross-Platform**: Windows | macOS | Linux

---

## 🗓️ Faza 2: Plugin-uri Esențiale (Next)

### 2.1 Data Processor Plugin 📊
**Scop**: Procesare CSV/JSON/TSV distribuită

```python
class DataProcessorPlugin(TaskPlugin):
    - Suport: CSV, JSON, JSONL, TSV, Parquet
    - Split: Pe rânduri (e.g., 1000 rânduri/chunk)
    - Operații: Map-Reduce, Aggregations, Transformări
    - Output: CSV/JSON rezultat
```

**Use case**: Procesare dataseturi mari (GB), ETL pipelines

### 2.2 Media Processor Plugin 🎬
**Scop**: Procesare imagini și video pentru ML

```python
class MediaProcessorPlugin(TaskPlugin):
    - Suport: PNG, JPG, MP4, AVI
    - Split: Frame-uri (video) sau grid (imagini)
    - Operații: Resize, Filter, Feature extraction
    - Output: Dataset ML ready
```

**Use case**: Preprocessing imagini ML, conversie video

### 2.3 Build System Plugin 🔨
**Scop**: Compilare proiecte mari distribuită

```python
class BuildSystemPlugin(TaskPlugin):
    - Suport: C/C++, Rust, Go, Java
    - Split: Pe module/source files
    - Operații: Compile, Link, Test
    - Output: Binare executabile
```

**Use case**: Compilare Chromium, LLVM, proiecte enterprise

### 2.4 STL/3D Processor Plugin 🖨️
**Scop**: Procesare fișiere 3D pentru printare

```python
class STLProcessorPlugin(TaskPlugin):
    - Suport: STL, OBJ, PLY, 3MF
    - Split: Pe triunghiuri sau regiuni
    - Operații: Repair, Optimize, Slice pentru G-code
    - Output: G-code sau mesh optimizat
```

**Use case**: Printare 3D industrială, optimizare mesh

---

## 🗓️ Faza 3: Features Avansate

### 3.1 AI Task Router 🧠
**Descriere**: Agent inteligent care alege strategia optimă

- Analizează fișier + resurse disponibile
- Sugerează: număr chunks, workeri potriviți, prioritate
- Auto-scale: Adaugă/elimină workeri dinamic

### 3.2 Persistent Storage 💾
**Descriere**: Stocare rezultate și recovery

- SQLite/PostgreSQL pentru metadate
- S3/MinIO pentru fișiere mari
- Resume: Continuă taskuri întrerupte

### 3.3 Security & Auth 🔒
**Descriere**: Autentificare și criptare

- JWT tokens pentru workeri
- TLS pentru comunicație
- Sandboxed execution pentru taskuri

### 3.4 Monitoring & Metrics 📈
**Descriere**: Observabilitate completă

- Prometheus metrics
- Grafana dashboards
- Alerting (worker offline, task stuck)

---

## 🗓️ Faza 4: UI Desktop (Final)

### 4.1 Core UI (NiceGUI) 🖥️

```
Main Window:
├── Sidebar:
│   ├── 📁 Projects
│   ├── ⚙️ Workers
│   ├── 📊 Queue
│   └── 🔔 Notifications
├── Main Area:
│   ├── 📂 File Drop Zone (drag & drop)
│   ├── 🎛️ Task Configuration Panel
│   ├── 📈 Real-time Progress Charts
│   └── 📝 Live Logs
└── Status Bar:
    ├── 🟢 System Status
    ├── 🌐 Network Status
    └── 📡 Active Connections
```

### 4.2 Features UI

- **Drag & Drop**: Tragi folderul în aplicație
- **Auto-detect**: AI detectează tipurile de fișiere
- **Visual Pipeline**: Vezi flow-ul taskurilor
- **Worker Map**: Hartă geografică a workerilor (Tailscale)
- **Result Viewer**: Preview rezultate în aplicație

### 4.3 Packaging 📦

- **Windows**: `.exe` cu PyInstaller + installer MSI
- **macOS**: `.app` bundle + DMG
- **Linux**: AppImage + deb/rpm packages

---

## 🧪 Testing Strategy

### Unit Tests
```python
test_plugins.py       # Test fiecare plugin
test_distributor.py   # Test distribuție
test_ai_scanner.py    # Test detectare fișiere
```

### Integration Tests
```python
test_end_to_end.py    # Flow complet
stress_test.py        # 1000+ taskuri
fault_tolerance.py    # Simulare erori
```

### Performance Benchmarks
- Task setup time < 100ms
- Chunk distribution < 500ms
- Throughput: 10,000 items/sec per worker

---

## 📅 Timeline Sugerit

| Sprint | Durată | Obiectiv |
|--------|--------|----------|
| **Sprint 1** | 2 zile | Data Processor Plugin |
| **Sprint 2** | 2 zile | Media Processor Plugin |
| **Sprint 3** | 3 zile | Build System + STL Plugins |
| **Sprint 4** | 2 zile | AI Task Router |
| **Sprint 5** | 3 zile | Persistent Storage |
| **Sprint 6** | 5 zile | UI Desktop (NiceGUI) |
| **Sprint 7** | 2 zile | Packaging & Polish |

**Total**: ~2-3 săptămâni pentru versiunea completă

---

## 🚀 Next Steps (Acum)

### Ce să faci tu:

1. **Testează sistemul actual**:
   ```powershell
   $env:PYTHONUTF8='1'
   python integrated_system.py
   ```

2. **Alege primul plugin** care te interesează:
   - Data Processor (CSV/JSON)?
   - Media Processor (Imagini)?
   - Build System (Compilare)?

3. **Spune-mi**: "Vreau să începem cu [X]"

4. **Implementăm împreună** pas cu pas:
   - Plugin skeleton
   - Logică de split
   - Execuție pe worker
   - Merge results
   - Testare

---

## 💡 Arhitectura Plugin-ului (Template)

```python
class NewPlugin(TaskPlugin):
    @property
    def name(self) -> str:
        return "Numele Pluginului"
    
    @property
    def task_type(self) -> TaskType:
        return TaskType.NEW_TYPE
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".ext1", ".ext2"]
    
    def can_handle(self, file_path: Path) -> bool:
        # Logică detectare
        pass
    
    def split_task(self, task: Task) -> List[Task]:
        # Logică împărțire
        pass
    
    async def execute_chunk(self, chunk: Task, worker_id: str) -> Any:
        # Logică execuție
        pass
    
    def merge_results(self, chunks: List[Task]) -> Any:
        # Logică reasamblare
        pass
```

---

## 🎯 Decizii de Luat

1. **Care plugin vrei primul?**
2. **Vrei să adăugăm suport Docker** pentru sandboxing?
3. **Să implementăm priority queue** pentru taskuri urgente?
4. **Vrei auto-scaling** (adaugare workeri dinamic)?

---

**Gata să începem Faza 2?** Spune-mi care plugin te interesează și construim împreună! 🚀
