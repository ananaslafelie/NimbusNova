"""
UPLOAD_WORKING.py - Salvează fișierul pe disk și îl procesează
"""
import asyncio
import httpx
import json
import os
from datetime import datetime
from nicegui import ui, app

MASTER_URL = "http://localhost:8003"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class WorkingUpload:
    def __init__(self):
        self.status_label = ui.label('⏳ Aștept fișier...')
        self.file_path = None
        self.file_name = None
        
    async def handle_upload(self, e):
        """Salvează fișierul pe disk"""
        try:
            print(f"Upload event type: {type(e)}")
            print(f"Event attrs: {[a for a in dir(e) if not a.startswith('_')]}")
            
            # NiceGUI UploadEventArguments - accesează e.files[0] sau e.file
            file_obj = None
            
            if hasattr(e, 'files') and e.files:
                file_obj = e.files[0]
                print(f"Found in e.files: {type(file_obj)}")
            elif hasattr(e, 'file') and e.file:
                file_obj = e.file
                print(f"Found in e.file: {type(file_obj)}")
            
            if file_obj:
                self.file_name = file_obj.name
                content = file_obj.content
                
                # Salvează pe disk
                self.file_path = os.path.join(UPLOAD_DIR, self.file_name)
                with open(self.file_path, 'wb') as f:
                    if asyncio.iscoroutine(content):
                        content = await content
                    if isinstance(content, bytes):
                        f.write(content)
                    else:
                        f.write(str(content).encode())
                
                size = os.path.getsize(self.file_path)
                self.status_label.set_text(f"✅ {self.file_name} ({size} bytes) - Gata de procesare!")
                print(f"✅ Saved: {self.file_path}")
            else:
                self.status_label.set_text(f"❌ Nu am găsit fișierul în event")
                
        except Exception as ex:
            print(f"Error: {ex}")
            import traceback
            traceback.print_exc()
            self.status_label.set_text(f"❌ Eroare: {ex}")
    
    async def process(self):
        if not self.file_path or not os.path.exists(self.file_path):
            self.status_label.set_text("❌ Nu a fost selectat niciun fișier!")
            return
        
        try:
            self.status_label.set_text("📤 Citesc fișierul...")
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            data = json.loads(text)
            items = data if isinstance(data, list) else [data]
            
            self.status_label.set_text(f"✅ {len(items)} iteme. Trimit la master...")
            
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{MASTER_URL}/submit-task",
                    json={"items": items, "filename": self.file_name},
                    timeout=10.0
                )
                result = r.json()
                task_id = result['task_id']
                total = result['total_chunks']
                
                self.status_label.set_text(f"⏳ Task {task_id}: {total} chunks...")
                
                start = datetime.now()
                while True:
                    await asyncio.sleep(0.5)
                    r = await client.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
                    data = r.json()
                    
                    done = data.get('done_chunks', 0)
                    status = data.get('status')
                    
                    if status == 'COMPLETED':
                        elapsed = (datetime.now() - start).total_seconds()
                        self.status_label.set_text(f"✅ Completat în {elapsed:.1f}s!")
                        break
                    elif status == 'FAILED':
                        self.status_label.set_text("❌ Eșuat!")
                        break
                        
        except Exception as e:
            self.status_label.set_text(f"❌ Eroare: {e}")
            import traceback
            traceback.print_exc()

# Build UI
ui.page_title('QA DNA - Upload')

uploader = WorkingUpload()

with ui.column().classes('w-full items-center p-6'):
    ui.label('🧬 QA DNA - Upload Funcțional').classes('text-3xl font-bold mb-4')
    
    with ui.card().classes('w-full max-w-2xl mb-4'):
        ui.label('📁 Selectează Fișier JSON').classes('text-xl font-bold mb-2')
        
        ui.upload(
            on_upload=lambda e: asyncio.create_task(uploader.handle_upload(e)),
            auto_upload=True
        ).classes('w-full mb-4').props('accept=.json')
        
        uploader.status_label.classes('text-lg text-gray-700')
        
        ui.button('▶️ PROCESEAZĂ', on_click=lambda: asyncio.create_task(uploader.process())).classes('w-full mt-4 bg-green-600 text-white font-bold')

ui.run(title='QA DNA Upload', port=8081, reload=False)
