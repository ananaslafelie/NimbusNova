"""
FUNCTIONAL_APP.py - Aplicație completă cu drag-drop pentru distribuție taskuri
Rulează pe Windows (Master + UI), distribuie la Workers (Windows + MacBook)
"""

import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime
from nicegui import ui, app
import tempfile

MASTER_URL = "http://localhost:8003"

class TaskDistributor:
    def __init__(self):
        self.status_text = None
        self.progress_bar = None
        self.results_area = None
        self.workers_table = None
        
    async def check_workers(self):
        """Verifică workerii conectați"""
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
                data = r.json()
                workers = data.get('workers', [])
                
                rows = []
                for w in workers:
                    icon = "🖥️" if 'windows' in w['id'] else "🍎"
                    rows.append({
                        'icon': icon,
                        'id': w['id'],
                        'status': w['status'],
                        'cpu': f"{w['cpu']:.1f}%",
                        'ram': f"{w['ram_free_mb']:.0f}MB",
                        'chunks': w['chunks_done']
                    })
                
                if self.workers_table:
                    self.workers_table.rows = rows
                    self.workers_table.update()
                
                return len(workers)
        except Exception as e:
            if self.status_text:
                self.status_text.set_text(f"❌ Eroare conexiune: {e}")
            return 0
    
    async def process_file(self, file_path: str):
        """Procesează fișierul încărcat"""
        try:
            path = Path(file_path)
            
            # Citește fișierul
            self.status_text.set_text(f"📖 Citesc fișierul {path.name}...")
            
            if path.suffix == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        items = data
                    else:
                        items = [data]
            elif path.suffix == '.csv':
                import csv
                items = []
                with open(path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        items.append(dict(row))
            else:
                # Fișier text - fiecare linie = un item
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    items = [{"line_num": i+1, "content": line.strip()} 
                            for i, line in enumerate(lines) if line.strip()]
            
            num_items = len(items)
            self.status_text.set_text(f"✅ Fișier citit: {num_items} iteme")
            
            if num_items == 0:
                ui.notify("Fișierul este gol!", type='negative')
                return
            
            # Trimite task la master
            self.status_text.set_text(f"🚀 Trimit {num_items} iteme la Master...")
            
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{MASTER_URL}/submit-task",
                    json={"items": items, "filename": path.name},
                    timeout=30.0
                )
                result = r.json()
                task_id = result['task_id']
                total_chunks = result['total_chunks']
                
                self.status_text.set_text(
                    f"⏳ Task {task_id}: {num_items} iteme → {total_chunks} chunks"
                )
                
                # Așteaptă completarea
                start_time = datetime.now()
                while True:
                    r = await client.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
                    data = r.json()
                    
                    status = data.get('status')
                    done = data.get('done_chunks', 0)
                    total = data.get('total_chunks', 1)
                    
                    pct = (done / total) * 100
                    self.progress_bar.set_value(pct / 100)
                    
                    if status == 'COMPLETED':
                        elapsed = (datetime.now() - start_time).total_seconds()
                        self.status_text.set_text(
                            f"✅ COMPLETAT în {elapsed:.1f}s! "
                            f"{done}/{total} chunks procesate"
                        )
                        
                        # Afișează distribuția
                        r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
                        status_data = r.json()
                        
                        result_text = f"🎉 Task Completat!\n\n"
                        result_text += f"📁 Fișier: {path.name}\n"
                        result_text += f"📊 Iteme: {num_items}\n"
                        result_text += f"🧩 Chunks: {total_chunks}\n"
                        result_text += f"⏱️ Timp: {elapsed:.1f} secunde\n\n"
                        result_text += "📈 Distribuție pe workeri:\n"
                        
                        for w in status_data.get('workers', []):
                            icon = "🖥️" if 'windows' in w['id'] else "🍎"
                            pct_worker = (w['chunks_done'] / total_chunks * 100) if total_chunks > 0 else 0
                            result_text += f"   {icon} {w['id']}: {w['chunks_done']} chunks ({pct_worker:.1f}%)\n"
                        
                        self.results_area.set_text(result_text)
                        ui.notify("Task completat cu succes!", type='positive')
                        break
                    
                    elif status == 'FAILED':
                        self.status_text.set_text("❌ Task eșuat!")
                        ui.notify("Task eșuat!", type='negative')
                        break
                    
                    await asyncio.sleep(0.5)
                    
        except Exception as e:
            self.status_text.set_text(f"❌ Eroare: {str(e)}")
            ui.notify(f"Eroare: {str(e)}", type='negative')
            import traceback
            traceback.print_exc()
    
    def create_ui(self):
        """Creează interfața"""
        ui.page_title('QA DNA - Distribuitor Taskuri')
        
        with ui.column().classes('w-full items-center p-4'):
            # Header
            ui.label('🧬 QA DNA - Distribuitor Taskuri').classes('text-3xl font-bold mb-2')
            ui.label('Încarcă un fișier și distribuie procesarea pe multiple dispozitive').classes('text-lg mb-4')
            
            # Status workeri
            ui.label('📊 Workeri Conectați').classes('text-xl font-bold mt-4')
            self.workers_table = ui.table(
                columns=[
                    {'name': 'icon', 'label': '', 'field': 'icon'},
                    {'name': 'id', 'label': 'Worker ID', 'field': 'id'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'cpu', 'label': 'CPU', 'field': 'cpu'},
                    {'name': 'ram', 'label': 'RAM Liber', 'field': 'ram'},
                    {'name': 'chunks', 'label': 'Chunks', 'field': 'chunks'},
                ],
                rows=[],
                row_key='id'
            ).classes('w-full max-w-4xl mb-4')
            
            # Zonă drag & drop
            ui.label('📁 Încarcă Fișier').classes('text-xl font-bold mt-4')
            
            upload_area = ui.card().classes('w-full max-w-2xl h-48 border-2 border-dashed border-blue-500 bg-blue-50 flex items-center justify-center cursor-pointer hover:bg-blue-100')
            
            with upload_area:
                ui.label('📎 Drag & Drop sau Click pentru a selecta fișier').classes('text-lg text-blue-700')
                ui.label('Suportat: JSON, CSV, TXT').classes('text-sm text-gray-500 mt-2')
            
            def handle_upload(e):
                """Gestionează upload-ul"""
                if e.content:
                    # Salvează fișierul temporar
                    temp_path = Path(tempfile.gettempdir()) / e.name
                    with open(temp_path, 'wb') as f:
                        f.write(e.content.read() if hasattr(e.content, 'read') else e.content)
                    
                    ui.notify(f'📤 Fișier primit: {e.name}', type='info')
                    asyncio.create_task(self.process_file(str(temp_path)))
            
            upload = ui.upload(on_upload=handle_upload, auto_upload=True)
            upload.classes('hidden')
            
            upload_area.on('click', lambda: upload.run_method('pickFiles'))
            
            # Progres
            self.progress_bar = ui.linear_progress(value=0).classes('w-full max-w-2xl mt-4')
            self.progress_bar.set_visibility(False)
            
            # Status
            self.status_text = ui.label('⏳ Aștept fișier...').classes('text-lg mt-4')
            
            # Rezultate
            ui.label('📋 Rezultate').classes('text-xl font-bold mt-6')
            self.results_area = ui.textarea('').classes('w-full max-w-4xl h-64 font-mono text-sm')
            
            # Butoane
            with ui.row().classes('mt-4 gap-4'):
                ui.button('🔄 Refresh Workeri', on_click=lambda: asyncio.create_task(self.check_workers()))
                ui.button('📊 Deschide Dashboard', on_click=lambda: ui.navigate.to('http://localhost:8003/status', new_tab=True))
            
            # Footer
            ui.label('🔧 Master: localhost:8003 | UI: localhost:8080').classes('text-sm text-gray-500 mt-8')

# Crează aplicația
distributor = TaskDistributor()

@app.on_startup
async def startup():
    await distributor.check_workers()
    # Reîmprospătare automată la fiecare 5 secunde
    while True:
        await asyncio.sleep(5)
        await distributor.check_workers()

# Rulează UI
distributor.create_ui()

ui.run(title='QA DNA - Distribuitor', port=8080, reload=False)
