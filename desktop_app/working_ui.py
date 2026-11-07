"""
WORKING_UI.py - UI funcțional garantat pentru distribuție taskuri
"""
import asyncio
import httpx
import json
from pathlib import Path
from datetime import datetime
from nicegui import ui, app

MASTER_URL = "http://localhost:8003"

class WorkingDistributor:
    def __init__(self):
        self.status_label = None
        self.result_text = None
        self.workers_label = None
        self.selected_file_label = None
        self.file_content = None
        self.file_name = None
        
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
    
    def handle_upload(self, e):
        """Handler pentru upload - funcționează cu NiceGUI 4.x"""
        try:
            import nicegui
            print(f"NiceGUI version: {nicegui.__version__}")
            print(f"Upload event: {e}")
            print(f"Event type: {type(e)}")
            
            # Verifică toate atributele evenimentului
            attrs = [a for a in dir(e) if not a.startswith('_')]
            print(f"Event attributes: {attrs}")
            
            # NiceGUI 4.x: e are direct name și content
            self.file_name = None
            self.file_content = None
            
            for attr in attrs:
                try:
                    val = getattr(e, attr)
                    if attr == 'name':
                        self.file_name = val
                        print(f"✓ Found name: {val}")
                    elif attr == 'content':
                        self.file_content = val
                        print(f"✓ Found content: {type(val)}, len={len(val) if val else 0}")
                except:
                    pass
            
            if self.file_name and self.file_content:
                self.selected_file_label.set_text(f"✅ Fișier selectat: {self.file_name} ({len(self.file_content)} bytes)")
                self.status_label.set_text("📤 Gata de procesare! Click pe 'Procesează Fișier'")
                print(f"✅ File ready: {self.file_name}")
            else:
                print(f"❌ Missing: name={self.file_name is not None}, content={self.file_content is not None}")
                self.status_label.set_text(f"❌ Eroare: nume={self.file_name is not None}, content={self.file_content is not None}")
                
        except Exception as ex:
            print(f"Eroare upload: {ex}")
            import traceback
            traceback.print_exc()
            self.status_label.set_text(f"❌ Eroare: {ex}")
    
    async def process_file(self):
        """Procesează fișierul selectat"""
        if not self.file_content or not self.file_name:
            self.status_label.set_text("❌ Nu a fost selectat niciun fișier!")
            return
        
        try:
            self.status_label.set_text(f"📤 Procesez: {self.file_name}")
            
            # Decodează content-ul
            if isinstance(self.file_content, bytes):
                text_content = self.file_content.decode('utf-8')
            else:
                text_content = str(self.file_content)
            
            # Parsează fișierul
            items = []
            if self.file_name.endswith('.json'):
                data = json.loads(text_content)
                items = data if isinstance(data, list) else [data]
            elif self.file_name.endswith('.csv'):
                import csv
                import io
                reader = csv.DictReader(io.StringIO(text_content))
                items = list(reader)
            else:
                # Fișier text
                items = [{"line_num": i+1, "content": line.strip()} 
                        for i, line in enumerate(text_content.split('\n')) if line.strip()]
            
            num_items = len(items)
            if num_items == 0:
                self.status_label.set_text("❌ Fișierul este gol!")
                return
            
            self.status_label.set_text(f"✅ {num_items} iteme. Trimit la Master...")
            
            # Trimite la master
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{MASTER_URL}/submit-task",
                    json={"items": items, "filename": self.file_name},
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
                        result_text += f"📁 Fișier: {self.file_name}\n"
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
            self.status_label.set_text(f"❌ Eroare: {str(e)}")
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
            
            # Upload - SIMPLIFICAT
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📁 Încarcă Fișier').classes('text-xl font-bold mb-2')
                
                # Upload component
                ui.upload(
                    label='Click pentru a selecta fișier',
                    auto_upload=True,
                    on_upload=self.handle_upload
                ).classes('w-full mb-2')
                
                # Label pentru fișier selectat
                self.selected_file_label = ui.label('⏳ Niciun fișier selectat').classes('text-sm text-gray-600 mb-2')
                
                # Buton de procesare
                ui.button(
                    '▶️ Procesează Fișier', 
                    on_click=lambda: asyncio.create_task(self.process_file())
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
distributor = WorkingDistributor()

@app.on_startup
async def startup():
    await distributor.check_workers()

# Timer pentru refresh automat
ui.timer(5.0, lambda: asyncio.create_task(distributor.check_workers()))

distributor.build()

ui.run(title='QA DNA - Distribuitor', port=8080, reload=False)
