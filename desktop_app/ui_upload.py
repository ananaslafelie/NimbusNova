"""
UI_UPLOAD.py - Folosește ui.upload() corect
"""
import asyncio
import httpx
import json
from datetime import datetime
from nicegui import ui, app

MASTER_URL = "http://localhost:8003"

class UploadDistributor:
    def __init__(self):
        self.status_label = None
        self.result_text = None
        self.workers_label = None
        self.file_label = None
        self.upload = None
        self.selected_files = []
        
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
                    text += f"   Chunks: {w['chunks_done']}\n\n"
                
                if self.workers_label:
                    self.workers_label.set_text(text)
                return len(workers)
        except Exception as e:
            if self.workers_label:
                self.workers_label.set_text(f"❌ Eroare: {e}")
            return 0
    
    def on_upload(self, e):
        """Handler pentru upload"""
        print(f"Upload event: {e}")
        print(f"Type: {type(e)}")
        
        try:
            # În NiceGUI 4.x, e are atributele: client, file, sender
            # Fișierul real e în e.file
            attrs = [a for a in dir(e) if not a.startswith('_')]
            print(f"Event attributes: {attrs}")
            
            # Obține fișierul din e.file
            if hasattr(e, 'file'):
                file_obj = e.file
                print(f"File object: {file_obj}")
                print(f"File type: {type(file_obj)}")
                
                # Acum file_obj ar trebui să aibă name și content
                file_attrs = [a for a in dir(file_obj) if not a.startswith('_')]
                print(f"File attributes: {file_attrs}")
                
                # Obține name și content
                name = getattr(file_obj, 'name', 'unknown')
                content = getattr(file_obj, 'content', None)
                
                print(f"Name: {name}")
                print(f"Content type: {type(content)}")
                print(f"Content size: {len(content) if content else 0}")
                
                if content is None:
                    self.status_label.set_text("❌ Fișierul nu are conținut")
                    return
                
                # Salvează fișierul
                self.selected_files = [file_obj]
                
                size = len(content)
                self.file_label.set_text(f"✅ {name} ({size} bytes)")
                self.status_label.set_text("📤 Fișier încărcat! Click pe Procesează")
                
            else:
                self.status_label.set_text(f"❌ Nu am găsit atributul 'file'")
                
        except Exception as ex:
            print(f"Error: {ex}")
            import traceback
            traceback.print_exc()
            self.status_label.set_text(f"❌ Eroare: {ex}")
    
    async def process(self):
        """Procesează fișierul"""
        if not self.selected_files:
            self.status_label.set_text("❌ Nu a fost selectat niciun fișier!")
            return
        
        try:
            self.status_label.set_text("📤 Procesez...")
            
            # Obține primul fișier
            file_obj = self.selected_files[0]
            
            # Obține conținutul - încearcă multiple metode
            content = None
            if hasattr(file_obj, 'content'):
                content = file_obj.content
            elif hasattr(file_obj, 'read'):
                try:
                    content = file_obj.read()
                except:
                    pass
            
            if content is None:
                self.status_label.set_text("❌ Nu pot citi conținutul fișierului")
                return
            
            # Decodează
            if isinstance(content, bytes):
                text = content.decode('utf-8')
            else:
                text = str(content)
            
            # Parsează JSON
            data = json.loads(text)
            items = data if isinstance(data, list) else [data]
            
            file_name = getattr(file_obj, 'name', 'file.json')
            
            self.status_label.set_text(f"✅ {len(items)} iteme. Trimit...")
            
            # Trimite la master
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{MASTER_URL}/submit-task",
                    json={"items": items, "filename": file_name},
                    timeout=10.0
                )
                result = r.json()
                task_id = result['task_id']
                total = result['total_chunks']
                
                self.status_label.set_text(f"⏳ Task {task_id}: {total} chunks...")
                
                # Așteaptă
                start = datetime.now()
                while True:
                    await asyncio.sleep(0.5)
                    r = await client.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
                    data = r.json()
                    
                    done = data.get('done_chunks', 0)
                    total = data.get('total_chunks', 1)
                    status = data.get('status')
                    
                    pct = (done/total)*100
                    self.status_label.set_text(f"⏳ [{done}/{total}] {pct:.0f}%")
                    
                    if status == 'COMPLETED':
                        elapsed = (datetime.now() - start).total_seconds()
                        
                        # Statistici
                        r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
                        wdata = r.json()
                        
                        res = f"🎉 Task Completat!\n\n"
                        res += f"📁 {file_name}\n"
                        res += f"📊 Iteme: {len(items)} | Chunks: {total}\n"
                        res += f"⏱️ Timp: {elapsed:.1f}s\n\n"
                        res += "📈 Distribuție:\n"
                        
                        for w in wdata.get('workers', []):
                            icon = "🖥️" if 'windows' in w['id'] else "🍎"
                            c = w.get('chunks_done', 0)
                            p = (c/total*100) if total > 0 else 0
                            res += f"   {icon} {w['id']}: {c} ({p:.1f}%)\n"
                        
                        self.result_text.set_value(res)
                        self.status_label.set_text(f"✅ Completat în {elapsed:.1f}s!")
                        break
                    elif status == 'FAILED':
                        self.status_label.set_text("❌ Eșuat!")
                        break
                        
        except Exception as e:
            self.status_label.set_text(f"❌ Eroare: {e}")
            import traceback
            traceback.print_exc()
    
    def build(self):
        ui.page_title('QA DNA - Distribuitor')
        
        with ui.column().classes('w-full items-center p-6'):
            ui.label('🧬 QA DNA - Distribuitor Taskuri').classes('text-3xl font-bold mb-2')
            
            # Workeri
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📊 Workeri Conectați').classes('text-xl font-bold mb-2')
                self.workers_label = ui.label('⏳ Se încarcă...').classes('text-mono whitespace-pre')
            
            # Upload
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📁 Încarcă Fișier').classes('text-xl font-bold mb-2')
                
                # Upload component - fără auto_upload
                self.upload = ui.upload(
                    label='Drag & drop sau click pentru a selecta fișier',
                    auto_upload=True,
                    on_upload=self.on_upload
                ).classes('w-full mb-2')
                
                self.file_label = ui.label('⏳ Niciun fișier selectat').classes('text-sm text-gray-600 mt-2')
                
                ui.button('▶️ Procesează', on_click=lambda: asyncio.create_task(self.process())).classes('w-full mt-4 bg-green-500')
            
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

# Crează
distributor = UploadDistributor()

@app.on_startup
async def startup():
    await distributor.check_workers()

ui.timer(5.0, lambda: asyncio.create_task(distributor.check_workers()))

distributor.build()

ui.run(title='QA DNA - Distribuitor', port=8081, reload=False)
