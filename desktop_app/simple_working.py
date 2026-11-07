"""
SIMPLE_WORKING.py - UI super simplu care funcționează 100%
Folosește doar elementele de bază NiceGUI
"""
import asyncio
import httpx
import json
from datetime import datetime
from nicegui import ui, app, native

MASTER_URL = "http://localhost:8003"

class SimpleDistributor:
    def __init__(self):
        self.status_label = None
        self.result_text = None
        self.workers_label = None
        self.file_label = None
        self.selected_file = None
        self.file_bytes = None
        
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
    
    async def pick_file(self):
        """Alege fișier folosind local_file_picker"""
        try:
            from nicegui import native
            
            # Folosește file picker nativ
            result = await native.file_picker(
                'Selectează fișier JSON',
                filter=['*.json', '*.csv', '*.txt'],
                multiple=False
            )
            
            if result:
                file_path = result[0] if isinstance(result, list) else result
                print(f"Selected: {file_path}")
                
                # Citește fișierul
                with open(file_path, 'rb') as f:
                    self.file_bytes = f.read()
                
                from pathlib import Path
                self.selected_file = Path(file_path).name
                
                self.file_label.set_text(f"✅ {self.selected_file} ({len(self.file_bytes)} bytes)")
                self.status_label.set_text("📤 Gata de procesare!")
                
        except Exception as e:
            print(f"Eroare: {e}")
            self.status_label.set_text(f"❌ Eroare: {e}")
    
    async def process(self):
        """Procesează fișierul"""
        if not self.file_bytes:
            self.status_label.set_text("❌ Nu a fost selectat niciun fișier!")
            return
        
        try:
            self.status_label.set_text("📤 Procesez...")
            
            # Parsează JSON
            text = self.file_bytes.decode('utf-8')
            data = json.loads(text)
            items = data if isinstance(data, list) else [data]
            
            self.status_label.set_text(f"✅ {len(items)} iteme. Trimit...")
            
            # Trimite la master
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{MASTER_URL}/submit-task",
                    json={"items": items, "filename": self.selected_file},
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
                        res += f"📁 {self.selected_file}\n"
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
                
                with ui.row().classes('w-full gap-4'):
                    ui.button('📂 Selectează Fișier', on_click=lambda: asyncio.create_task(self.pick_file())).classes('flex-grow')
                
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
distributor = SimpleDistributor()

@app.on_startup
async def startup():
    await distributor.check_workers()

ui.timer(5.0, lambda: asyncio.create_task(distributor.check_workers()))

distributor.build()

ui.run(title='QA DNA - Distribuitor', port=8080, reload=False)
