"""
FINAL_UI.py - UI garantat funcțional cu input HTML nativ
"""
import asyncio
import httpx
import json
import base64
from datetime import datetime
from nicegui import ui, app

MASTER_URL = "http://localhost:8003"

class FinalDistributor:
    def __init__(self):
        self.status_label = None
        self.result_text = None
        self.workers_label = None
        self.file_info_label = None
        self.file_content = None
        self.file_name = None
        self.upload_component = None
        
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
    
    async def handle_file_selected(self, e):
        """Handler pentru fișier selectat din dialog"""
        try:
            print(f"File selected event: {e}")
            print(f"Event type: {type(e)}")
            
            # În NiceGUI, evenimentul are .args cu datele
            if hasattr(e, 'args') and e.args:
                file_data = e.args
                print(f"File data type: {type(file_data)}")
                print(f"File data: {file_data[:100] if len(file_data) > 100 else file_data}...")
                
                # Decodează base64
                if isinstance(file_data, str) and ',' in file_data:
                    # Format: data:text/plain;base64,content
                    header, content = file_data.split(',', 1)
                    self.file_content = base64.b64decode(content)
                    print(f"Decoded content: {len(self.file_content)} bytes")
                else:
                    self.file_content = file_data
                    
                self.file_name = "selected_file.json"
                self.file_info_label.set_text(f"✅ Fișier: {self.file_name} ({len(self.file_content)} bytes)")
                self.status_label.set_text("📤 Gata de procesare!")
            else:
                print("No args in event")
                self.status_label.set_text("❌ Nu s-a putut citi fișierul")
                
        except Exception as ex:
            print(f"Eroare: {ex}")
            import traceback
            traceback.print_exc()
            self.status_label.set_text(f"❌ Eroare: {ex}")
    
    async def process_file(self):
        """Procesează fișierul"""
        if not self.file_content:
            self.status_label.set_text("❌ Nu a fost selectat niciun fișier!")
            return
        
        try:
            self.status_label.set_text("📤 Procesez...")
            
            # Parsează JSON
            if isinstance(self.file_content, bytes):
                text_content = self.file_content.decode('utf-8')
            else:
                text_content = str(self.file_content)
            
            data = json.loads(text_content)
            items = data if isinstance(data, list) else [data]
            num_items = len(items)
            
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
                    await asyncio.sleep(0.5)
                    r = await client.get(f"{MASTER_URL}/results/{task_id}", timeout=5.0)
                    data = r.json()
                    
                    status = data.get('status')
                    done = data.get('done_chunks', 0)
                    total = data.get('total_chunks', 1)
                    
                    pct = (done / total) * 100
                    self.status_label.set_text(f"⏳ [{done}/{total}] {pct:.0f}%")
                    
                    if status == 'COMPLETED':
                        elapsed = (datetime.now() - start_time).total_seconds()
                        
                        # Statistici
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
                        
                        self.result_text.set_value(result_text)
                        self.status_label.set_text(f"✅ Completat în {elapsed:.1f}s!")
                        break
                    
                    elif status == 'FAILED':
                        self.status_label.set_text("❌ Task eșuat!")
                        break
        
        except Exception as e:
            self.status_label.set_text(f"❌ Eroare: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def open_file_dialog(self):
        """Deschide dialogul de fișiere folosind JavaScript"""
        ui.run_javascript('''
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json,.csv,.txt';
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        // Trimite conținutul înapoi la Python
                        window.fileContent = event.target.result;
                        window.fileName = file.name;
                        // Declanșează un eveniment custom
                        document.dispatchEvent(new CustomEvent('fileSelected', {
                            detail: { name: file.name, content: event.target.result }
                        }));
                    };
                    reader.readAsText(file);
                }
            };
            input.click();
        ''')
    
    def build(self):
        """Construiește UI-ul simplu și funcțional"""
        ui.page_title('QA DNA - Distribuitor')
        
        with ui.column().classes('w-full items-center p-6'):
            # Header
            ui.label('🧬 QA DNA - Distribuitor Taskuri').classes('text-3xl font-bold mb-2')
            ui.label('Încarcă fișier JSON/CSV pentru procesare distribuită').classes('text-lg mb-4')
            
            # Panou workeri
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📊 Workeri Conectați').classes('text-xl font-bold mb-2')
                self.workers_label = ui.label('⏳ Se încarcă...').classes('text-mono whitespace-pre')
            
            # Upload SIMPLU - folosesc local_file_picker din nicegui
            with ui.card().classes('w-full max-w-2xl mb-4'):
                ui.label('📁 Încarcă Fișier').classes('text-xl font-bold mb-2')
                
                # Folosesc o abordare diferită - buton + input
                with ui.row().classes('w-full gap-4'):
                    ui.button('📂 Selectează Fișier', on_click=self.pick_file).classes('flex-grow')
                
                self.file_info_label = ui.label('⏳ Niciun fișier selectat').classes('text-sm text-gray-600 mt-2')
                
                # Buton procesare
                ui.button(
                    '▶️ Procesează Fișier', 
                    on_click=lambda: asyncio.create_task(self.process_file())
                ).classes('w-full mt-4')
            
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
        
        # Handler pentru evenimentul de fișier selectat (via JavaScript)
        ui.add_head_html('''
        <script>
        document.addEventListener('fileSelected', function(e) {
            // Salvează în sessionStorage pentru a fi accesibil din Python
            sessionStorage.setItem('selectedFileName', e.detail.name);
            sessionStorage.setItem('selectedFileContent', e.detail.content);
            // Notifică NiceGUI
            window.location.reload();
        });
        </script>
        ''')

    def pick_file(self):
        """Alege fișier folosind dialog nativ"""
        ui.run_javascript('''
            (async () => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '.json,.csv,.txt';
                
                input.onchange = async (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        const text = await file.text();
                        
                        // Salvează în window pentru a fi accesibil
                        window.selectedFileName = file.name;
                        window.selectedFileContent = text;
                        
                        // Trimite la server via POST
                        fetch('/_nicegui/file-upload', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({name: file.name, content: text})
                        });
                    }
                };
                input.click();
            })();
        ''')

# Crează aplicația
distributor = FinalDistributor()

@app.post('/_nicegui/file-upload')
async def handle_file_upload(request):
    """Endpoint pentru primirea fișierului de la JavaScript"""
    try:
        data = await request.json()
        distributor.file_name = data.get('name', 'unknown')
        content = data.get('content', '')
        
        if isinstance(content, str):
            distributor.file_content = content.encode('utf-8')
        else:
            distributor.file_content = content
        
        print(f"File received: {distributor.file_name} ({len(distributor.file_content)} bytes)")
        
        # Actualizează UI
        if distributor.file_info_label:
            distributor.file_info_label.set_text(f"✅ {distributor.file_name} ({len(distributor.file_content)} bytes)")
        if distributor.status_label:
            distributor.status_label.set_text("📤 Gata de procesare!")
            
        return {"status": "ok"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}

@app.on_startup
async def startup():
    await distributor.check_workers()

# Timer pentru refresh
ui.timer(5.0, lambda: asyncio.create_task(distributor.check_workers()))

distributor.build()

ui.run(title='QA DNA - Distribuitor', port=8080, reload=False)
