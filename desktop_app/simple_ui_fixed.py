"""
SIMPLE_UI_FIXED.py - UI simplu și funcțional pentru distribuție taskuri
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
    
    def process_upload(self, e):
        """Handler pentru upload - rulează async"""
        asyncio.create_task(self._handle_upload(e))
    
    async def _handle_upload(self, e):
        """Procesează upload-ul"""
        try:
            # Log pentru debug
            print(f"Upload event type: {type(e)}")
            print(f"Upload event attrs: {dir(e)}")
            
            # În NiceGUI 4.x, evenimentul are name și content direct
            # sau files ca listă
            files = []
            
            if hasattr(e, 'files'):
                files = e.files if e.files else []
            elif hasattr(e, 'name'):
                # Evenimentul este chiar fișierul
                files = [e]
            
            if not files:
                self.status_label.set_text("❌ Nu s-a selectat niciun fișier")
                return
            
            print(f"Files: {files}")
            print(f"Files type: {type(files)}")
            
            for file_obj in files:
                print(f"Processing file: {file_obj}")
                print(f"File type: {type(file_obj)}")
                print(f"File attrs: {dir(file_obj)}")
                
                # Obține numele fișierului
                file_name = getattr(file_obj, 'name', 'unknown_file')
                self.status_label.set_text(f"📤 Procesez: {file_name}")
                
                # Obține conținutul - în NiceGUI 4.x e .content (bytes)
                content = getattr(file_obj, 'content', None)
                if content is None and hasattr(file_obj, 'read'):
                    try:
                        content = file_obj.read()
                    except:
                        pass
                
                print(f"Content type: {type(content)}")
                if content is None:
                    self.status_label.set_text("❌ Nu pot citi conținutul fișierului")
                    continue
                
                # Decodează content-ul
                if isinstance(content, bytes):
                    text_content = content.decode('utf-8')
                else:
                    text_content = str(content)
                
                # Parsează fișierul
                items = []
                if file_name.endswith('.json'):
                    data = json.loads(text_content)
                    items = data if isinstance(data, list) else [data]
                elif file_name.endswith('.csv'):
                    import csv
                    import io
                    reader = csv.DictReader(io.StringIO(text_content))
                    items = list(reader)
                else:
                    # Fișier text - fiecare linie = un item
                    items = [{"line_num": i+1, "content": line.strip()} 
                            for i, line in enumerate(text_content.split('\n')) if line.strip()]
                
                num_items = len(items)
                if num_items == 0:
                    self.status_label.set_text("❌ Fișierul este gol")
                    continue
                
                self.status_label.set_text(f"✅ {num_items} iteme. Trimit la Master...")
                
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
                        self.status_label.set_text(f"⏳ [{done}/{total}] {pct:.0f}%")
                        
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
                            break
                        
                        elif status == 'FAILED':
                            self.status_label.set_text("❌ Task eșuat!")
                            break
                        
                        await asyncio.sleep(0.5)
        
        except Exception as e:
            error_msg = f"❌ Eroare: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            if self.status_label:
                self.status_label.set_text(error_msg)
    
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
                
                # Upload cu handler
                ui.upload(
                    label='Click pentru a selecta fișier',
                    auto_upload=True,
                    on_upload=self.process_upload
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
