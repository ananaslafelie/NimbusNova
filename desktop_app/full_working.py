"""
FULL_WORKING.py - UI completă care funcționează
"""
import asyncio
import httpx
import json
from datetime import datetime
from nicegui import ui, app, events

MASTER_URL = "http://localhost:8003"

class FullDistributor:
    def __init__(self):
        self.status_label = None
        self.result_text = None
        self.workers_label = None
        self.file_label = None
        self.stored_content = None
        self.stored_name = None
        
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
    
    async def handle_upload(self, e: events.UploadEventArguments):
        """Handler pentru upload - citește conținutul"""
        try:
            print(f"\n=== UPLOAD EVENT ===")
            print(f"Type: {type(e)}")
            
            # În NiceGUI 4.x, e.file conține fișierul
            if hasattr(e, 'file'):
                f = e.file
                print(f"File type: {type(f)}")
                
                # Obține numele
                name = getattr(f, 'name', getattr(f, 'filename', 'unknown'))
                print(f"Name: {name}")
                
                # Citește conținutul - încearcă multiple metode
                content = None
                
                # Metoda 1: .content
                if hasattr(f, 'content'):
                    content = f.content
                    print(f"Content via .content: {type(content)} {len(content) if content else 0}")
                
                # Metoda 2: .read() 
                if content is None and hasattr(f, 'read'):
                    try:
                        result = f.read()
                        if asyncio.iscoroutine(result):
                            result = await result
                        content = result
                        print(f"Content via .read(): {type(content)} {len(content) if content else 0}")
                    except Exception as ex:
                        print(f".read() error: {ex}")
                
                # Metoda 3: .read_text()
                if content is None and hasattr(f, 'read_text'):
                    try:
                        result = f.read_text()
                        if asyncio.iscoroutine(result):
                            result = await result
                        content = result.encode('utf-8') if isinstance(result, str) else result
                        print(f"Content via .read_text(): {type(content)} {len(content) if content else 0}")
                    except Exception as ex:
                        print(f".read_text() error: {ex}")
                
                # Metoda 4: .text()
                if content is None and hasattr(f, 'text'):
                    try:
                        val = f.text
                        if callable(val):
                            result = val()
                            if asyncio.iscoroutine(result):
                                result = await result
                            content = result.encode('utf-8') if isinstance(result, str) else result
                        else:
                            content = val.encode('utf-8') if isinstance(val, str) else val
                        print(f"Content via .text: {type(content)} {len(content) if content else 0}")
                    except Exception as ex:
                        print(f".text error: {ex}")
                
                # Metoda 5: .file (file-like object)
                if content is None and hasattr(f, 'file'):
                    try:
                        file_obj = f.file
                        print(f"File attr type: {type(file_obj)}")
                        if hasattr(file_obj, 'read'):
                            result = file_obj.read()
                            if asyncio.iscoroutine(result):
                                result = await result
                            content = result
                            print(f"Content via .file.read(): {type(content)} {len(content) if content else 0}")
                    except Exception as ex:
                        print(f".file.read() error: {ex}")
                
                if content is None:
                    # Last resort: try converting f to string
                    try:
                        s = str(f)
                        if len(s) > 100:
                            print(f"str(f) length: {len(s)}")
                            # Maybe the content is in the string representation
                    except:
                        pass
                    
                    self.status_label.set_text("❌ Nu pot citi conținutul fișierului")
                    print("❌ All methods failed to read content")
                    return
                
                # Salvează
                self.stored_name = name
                if isinstance(content, str):
                    self.stored_content = content.encode('utf-8')
                else:
                    self.stored_content = content
                
                size = len(self.stored_content)
                print(f"✅ SUCCESS: {name} ({size} bytes)")
                
                self.file_label.set_text(f"✅ {name} ({size} bytes)")
                self.status_label.set_text("📤 Fișier încărcat! Click pe Procesează")
            else:
                print("❌ No 'file' attribute on event")
                self.status_label.set_text("❌ Eroare: structură invalidă")
                
        except Exception as ex:
            print(f"Error: {ex}")
            import traceback
            traceback.print_exc()
            self.status_label.set_text(f"❌ Eroare: {ex}")
    
    async def process(self):
        """Procesează fișierul"""
        if not self.stored_content or not self.stored_name:
            self.status_label.set_text("❌ Nu a fost selectat niciun fișier!")
            return
        
        try:
            self.status_label.set_text("📤 Procesez...")
            
            # Decodează
            if isinstance(self.stored_content, bytes):
                text = self.stored_content.decode('utf-8')
            else:
                text = str(self.stored_content)
            
            # Parsează JSON
            data = json.loads(text)
            items = data if isinstance(data, list) else [data]
            
            self.status_label.set_text(f"✅ {len(items)} iteme. Trimit...")
            
            # Trimite la master
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{MASTER_URL}/submit-task",
                    json={"items": items, "filename": self.stored_name},
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
                        res += f"📁 {self.stored_name}\n"
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
                
                ui.upload(
                    on_upload=self.handle_upload,
                    auto_upload=True,
                ).props('accept=.json,.csv,.txt').classes('w-full mb-2')
                
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
distributor = FullDistributor()

@app.on_startup
async def startup():
    await distributor.check_workers()

ui.timer(5.0, lambda: asyncio.create_task(distributor.check_workers()))

distributor.build()

ui.run(title='QA DNA - Distribuitor', port=8081, reload=False)
