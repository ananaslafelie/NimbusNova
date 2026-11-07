"""
SIMPLE_UI.py - UI simplu și funcțional pentru distribuție taskuri
"""
import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime
from nicegui import ui, app
import tempfile
import os

MASTER_URL = "http://localhost:8003"

class SimpleDistributor:
    def __init__(self):
        self.status_label = None
        self.result_text = None
        self.workers_label = None
        
    async def check_workers(self):
        """Verifică workerii"""
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
                data = r.json()
                workers = data.get('workers', [])
                
                text = f"📊 Workeri online: {len(workers)}\n\n"
                for w in workers:
                    icon = "🖥️" if 'windows' in w['id'] else "🍎"
                    text += f"{icon} {w['id']}\n"
                    text += f"   Status: {w['status']} | CPU: {w['cpu']:.1f}%\n"
                    text += f"   Chunks procesate: {w['chunks_done']}\n\n"
                
                if self.workers_label:
                    self.workers_label.set_text(text)
                
                return len(workers)
        except Exception as e:
            if self.workers_label:
                self.workers_label.set_text(f"❌ Eroare: {e}")
            return 0
    
    async def upload_and_process(self, e):
        """Procesează fișierele încărcate"""
        try:
            # În NiceGUI 4.x, e.files conține fișierele
            files = e.files if hasattr(e, 'files') else [e]
            
            if not files:
                return
            
            for file in files:
                file_name = file.name if hasattr(file, 'name') else 'uploaded_file'
                self.status_label.set_text(f"📤 Procesez: {file_name}")
                
                # Citește conținutul fișierului
                content = file.content if hasattr(file, 'content') else file.read()
                
                # Parsează fișierul
                if file_name.endswith('.json'):
                    items = json.loads(content.decode('utf-8'))
                    if not isinstance(items, list):
                        items = [items]
                elif file_name.endswith('.csv'):
                    import csv
                    import io
                    items = []
                    csv_text = content.decode('utf-8')
                    reader = csv.DictReader(io.StringIO(csv_text))
                    for row in reader:
                        items.append(dict(row))
                else:
                    # Text file
                    text = content.decode('utf-8')
                    items = [{"line_num": i+1, "content": line.strip()} 
                            for i, line in enumerate(text.split('\n')) if line.strip()]
                
                num_items = len(items)
                self.status_label.set_text(f"✅ {num_items} iteme în fișier. Trimit la Master...")
                
                # Trimite la master
                async with httpx.AsyncClient() as client:
                    r = await client.post(
                        f"{MASTER_URL}/submit-task",
                        json={"items": items, "filename": file_name},
                        timeout=10.0
                    )
                    result = r.json()
                    task_id = result['task_id']
                    total_chunks = result['total_chunks']
                    
                    self.status_label.set_text(f"⏳ Task {task_id}: {total_chunks} chunks...")
                    
                    # Așteaptă completarea
                    start_time = datetime.now()
                    while True:
                        r = await client.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
                        data = r.json()
                        
                        status = data.get('status')
                        done = data.get('done_chunks', 0)
                        total = data.get('total_chunks', 1)
                        
                        pct = (done / total) * 100
                        self.status_label.set_text(f"⏳ [{done}/{total}] {pct:.0f}% - Task {task_id}")
                        
                        if status == 'COMPLETED':
                            elapsed = (datetime.now() - start_time).total_seconds()
                            
                            # Statistici finale
                            r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
                            status_data = r.json()
                            
                            result_text = f"🎉 Task Completat!\n\n"
                            result_text += f"📁 Fișier: {file_name}\n"
                            result_text += f"📊 Iteme: {num_items} | Chunks: {total_chunks}\n"
                            result_text += f"⏱️ Timp: {elapsed:.1f} secunde\n\n"
                            result_text += "📈 Distribuție:\n"
                            
                            for w in status_data.get('workers', []):
                                icon = "🖥️" if 'windows' in w['id'] else "🍎"
                                chunks = w.get('chunks_done', 0)
                                pct_w = (chunks / total * 100) if total > 0 else 0
                                result_text += f"   {icon} {w['id']}: {chunks} chunks ({pct_w:.1f}%)\n"
                            
                            self.result_text.set_text(result_text)
                            self.status_label.set_text(f"✅ Completat în {elapsed:.1f}s!")
                            ui.notify("Task completat!", type='positive')
                            break
                        
                        elif status == 'FAILED':
                            self.status_label.set_text("❌ Task eșuat!")
                            ui.notify("Task eșuat!", type='negative')
                            break
                        
                        await asyncio.sleep(0.5)
        
        except Exception as e:
                self.status_label.set_text(f"❌ Eroare: {str(e)}")
                ui.notify(f"Eroare: {str(e)}", type='negative')
                import traceback
                traceback.print_exc()
    
    def build(self):
        """Construiește UI-ul"""
        ui.page_title('QA DNA - Distribuitor')
        
        with ui.column().classes('w-full items-center p-6'):
            # Header
            ui.label('🧬 QA DNA - Distribuitor Taskuri').classes('text-3xl font-bold mb-2')
            ui.label('Încarcă fișier JSON/CSV pentru procesare distribuită').classes('text-lg mb-4')
            
            # Panou workeri
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📊 Workeri Conectați').classes('text-xl font-bold mb-2')
                self.workers_label = ui.label('⏳ Se încarcă...').classes('text-mono whitespace-pre')
            
            # Upload
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📁 Încarcă Fișier').classes('text-xl font-bold mb-2')
                
                ui.label('Selectează fișier JSON sau CSV:').classes('mb-2')
                
                # Upload nativ care funcționează sigur
                ui.upload(
                    label='Click pentru a selecta fișier',
                    auto_upload=True,
                    on_upload=lambda e: asyncio.create_task(self.upload_and_process([e]))
                ).classes('w-full')
            
            # Status
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('⏳ Status').classes('text-xl font-bold mb-2')
                self.status_label = ui.label('Aștept fișier...').classes('text-lg')
            
            # Rezultate
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📋 Rezultate').classes('text-xl font-bold mb-2')
                self.result_text = ui.textarea('').classes('w-full h-48 font-mono')
            
            # Butoane
            with ui.row().classes('mt-4 gap-4'):
                ui.button('🔄 Refresh', on_click=lambda: asyncio.create_task(self.check_workers()))
                ui.button('📊 Dashboard', on_click=lambda: ui.navigate.to('http://localhost:8003/status', new_tab=True))

# Crează și rulează
distributor = SimpleDistributor()

@app.on_startup
async def startup():
    await distributor.check_workers()

# Timer pentru refresh automat
ui.timer(5.0, lambda: asyncio.create_task(distributor.check_workers()))

distributor.build()

ui.run(title='QA DNA - Distribuitor', port=8080, reload=False)
