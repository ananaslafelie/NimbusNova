"""
JS_UPLOAD.py - Upload via JavaScript FileReader + fetch
"""
import asyncio
import httpx
import json
from datetime import datetime
from nicegui import ui, app

MASTER_URL = "http://localhost:8003"

# Storage global
uploaded = {"name": None, "content": None}

class JSUploader:
    def __init__(self):
        self.status_label = None
        self.result_text = None
        self.workers_label = None
        self.file_label = None
        
    async def check_workers(self):
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
    
    async def process(self):
        if not uploaded["content"] or not uploaded["name"]:
            self.status_label.set_text("❌ Nu a fost selectat niciun fișier!")
            return
        
        try:
            self.status_label.set_text("📤 Procesez...")
            text = uploaded["content"]
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            
            data = json.loads(text)
            items = data if isinstance(data, list) else [data]
            
            self.status_label.set_text(f"✅ {len(items)} iteme. Trimit...")
            
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"{MASTER_URL}/submit-task",
                    json={"items": items, "filename": uploaded["name"]},
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
                    total = data.get('total_chunks', 1)
                    status = data.get('status')
                    
                    pct = (done/total)*100
                    self.status_label.set_text(f"⏳ [{done}/{total}] {pct:.0f}%")
                    
                    if status == 'COMPLETED':
                        elapsed = (datetime.now() - start).total_seconds()
                        r = await client.get(f"{MASTER_URL}/status", timeout=5.0)
                        wdata = r.json()
                        
                        res = f"🎉 Task Completat!\n\n"
                        res += f"📁 {uploaded['name']}\n"
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
            
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📊 Workeri Conectați').classes('text-xl font-bold mb-2')
                self.workers_label = ui.label('⏳ Se încarcă...').classes('text-mono whitespace-pre')
            
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📁 Încarcă Fișier').classes('text-xl font-bold mb-2')
                
                # Input file + buton JS
                ui.html('''
                <input type="file" id="fileInput" accept=".json,.csv,.txt" style="margin-bottom: 10px; width: 100%;">
                <button onclick="readFile()" style="padding: 10px; background: #2196F3; color: white; border: none; border-radius: 5px; cursor: pointer; width: 100%; margin-bottom: 10px;">
                    📂 Citește Fișier
                </button>
                <div id="fileStatus" style="color: gray; font-size: 14px;">⏳ Niciun fișier selectat</div>
                ''')
                
                ui.button('▶️ Procesează', on_click=lambda: asyncio.create_task(self.process())).classes('w-full mt-4 bg-green-500')
            
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('⏳ Status').classes('text-xl font-bold mb-2')
                self.status_label = ui.label('Aștept fișier...').classes('text-lg')
            
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📋 Rezultate').classes('text-xl font-bold mb-2')
                self.result_text = ui.textarea('').classes('w-full h-48 font-mono')
            
            with ui.row().classes('mt-4 gap-4'):
                ui.button('🔄 Refresh', on_click=lambda: asyncio.create_task(self.check_workers()))
                ui.button('📊 Dashboard', on_click=lambda: ui.navigate.to('http://localhost:8003/status', new_tab=True))
        
        # JavaScript pentru citirea fișierului
        ui.add_head_html('''
        <script>
        async function readFile() {
            const input = document.getElementById('fileInput');
            const status = document.getElementById('fileStatus');
            
            if (!input.files || input.files.length === 0) {
                status.textContent = '❌ Selectează un fișier mai întâi';
                status.style.color = 'red';
                return;
            }
            
            const file = input.files[0];
            status.textContent = '⏳ Se citește...';
            status.style.color = 'orange';
            
            try {
                const text = await file.text();
                
                // Trimite la server
                const response = await fetch('/store-file', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: file.name, content: text})
                });
                
                const result = await response.json();
                
                if (result.status === 'ok') {
                    status.textContent = '✅ ' + file.name + ' (' + text.length + ' bytes)';
                    status.style.color = 'green';
                } else {
                    status.textContent = '❌ ' + (result.message || 'Eroare');
                    status.style.color = 'red';
                }
            } catch (err) {
                status.textContent = '❌ Eroare: ' + err.message;
                status.style.color = 'red';
            }
        }
        </script>
        ''')

# Endpoint pentru stocarea fișierului
@app.post('/store-file')
async def store_file(request):
    global uploaded
    try:
        data = await request.json()
        uploaded["name"] = data.get('name', 'unknown')
        uploaded["content"] = data.get('content', '')
        print(f"✅ File stored: {uploaded['name']} ({len(uploaded['content'])} bytes)")
        return {"status": "ok"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}

# Crează
distributor = JSUploader()

@app.on_startup
async def startup():
    await distributor.check_workers()

ui.timer(5.0, lambda: asyncio.create_task(distributor.check_workers()))

distributor.build()

ui.run(title='QA DNA - Distribuitor', port=8081, reload=False)
