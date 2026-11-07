"""
QA DNA Desktop - Versiune Simplă și Robustă
Fără erori de async/background tasks
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nicegui import ui, app
from task_manager import TaskDistributor
from ai_scanner import AITaskScanner
import httpx

# State
distributor = TaskDistributor()
scanner = AITaskScanner()
master_url = "http://localhost:8003"

# UI Elements (global pentru update)
workers_label = None
file_info_label = None

async def check_status():
    """Verifică status - fără notificări, doar update text"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{master_url}/status", timeout=3.0)
            data = response.json()
            
            workers = data.get('workers', [])
            if workers:
                worker_texts = []
                for w in workers:
                    icon = "🟢" if w.get('status') == 'ONLINE' else "🔴"
                    worker_texts.append(f"{icon} {w['id']}")
                
                if workers_label:
                    workers_label.set_text(" | ".join(worker_texts))
            else:
                if workers_label:
                    workers_label.set_text("Niciun worker")
    except:
        if workers_label:
            workers_label.set_text("Eroare conexiune")

def analyze_file_ui(path_str):
    """Analizează fișier și update UI"""
    if not path_str:
        return
    
    try:
        analysis = scanner.analyze_file(Path(path_str))
        if analysis and file_info_label:
            info_text = f"📄 {analysis.category.value} | 🔧 {analysis.suggested_plugin} | 📊 {analysis.estimated_complexity}"
            file_info_label.set_text(info_text)
    except Exception as e:
        if file_info_label:
            file_info_label.set_text(f"❌ Eroare: {str(e)}")

# UI
with ui.header().classes('bg-blue-600 text-white p-4'):
    ui.label('🧬 QA DNA Desktop').classes('text-2xl font-bold')

with ui.card().classes('w-full p-4'):
    ui.label('📁 Selectare Fișier').classes('text-xl font-bold mb-4')
    
    # File path input
    file_input = ui.input(label='Cale fișier').classes('w-full')
    
    # File info display
    file_info_label = ui.label('Așteaptă selecție...').classes('text-blue-600 mt-2')
    
    # Buttons
    with ui.row().classes('mt-4 gap-2'):
        ui.button('📂 Browse', on_click=lambda: pick_file(file_input))
        ui.button('🔍 Analiză', on_click=lambda: analyze_file_ui(file_input.value))
        ui.button('🔄 Refresh Status', on_click=lambda: check_status())

with ui.card().classes('w-full p-4 mt-4'):
    ui.label('📊 Status Workeri').classes('text-xl font-bold mb-2')
    workers_label = ui.label('Necunoscut').classes('text-lg')

with ui.card().classes('w-full p-4 mt-4'):
    ui.label('⚙️ Configurare Task').classes('text-xl font-bold mb-2')
    chunks_slider = ui.slider(min=1, max=10, value=2).classes('w-full')
    chunks_label = ui.label('2 chunks').classes('text-sm')
    chunks_slider.on('change', lambda e: chunks_label.set_text(f"{int(e.args)} chunks"))
    
    status_label = ui.label('⏳ Așteaptă...').classes('mt-2')
    
    async def submit_task():
        """Trimite taskul la Master"""
        file_path = file_input.value
        if not file_path:
            ui.notify('❌ Selectează un fișier!', type='negative')
            return
        
        try:
            status_label.set_text('📤 Se trimite la Master...')
            
            # Verifică workeri
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{master_url}/status", timeout=5.0)
                data = response.json()
                workers = data.get('workers', [])
                
                if len(workers) < 2:
                    ui.notify(f'⚠️ Doar {len(workers)} worker conectat. Așteaptă MacBook!', type='warning')
                    status_label.set_text(f'⚠️ Doar {len(workers)} worker')
                    return
                
                # Trimite task
                import random
                items = [{'id': i, 'data': f'item_{i}'} for i in range(100)]
                
                response = await client.post(
                    f"{master_url}/submit-task",
                    json={'items': items},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get('task_id', 'unknown')
                    total_chunks = result.get('total_chunks', 0)
                    
                    ui.notify(f'✅ Task {task_id} creat cu {total_chunks} chunks!', type='positive')
                    status_label.set_text(f'✅ Task creat: {total_chunks} chunks')
                    
                    # Poll pentru status
                    await poll_task_status(client, task_id, status_label)
                else:
                    ui.notify(f'❌ Eroare: {response.status_code}', type='negative')
                    status_label.set_text('❌ Eroare la trimitere')
                    
        except Exception as e:
            ui.notify(f'❌ Eroare: {str(e)}', type='negative')
            status_label.set_text(f'❌ {str(e)[:50]}')
    
    async def poll_task_status(client, task_id, status_label):
        """Poll pentru statusul taskului"""
        for i in range(30):  # Max 30 secunde
            try:
                response = await client.get(f"{master_url}/results/{task_id}", timeout=5.0)
                data = response.json()
                
                status = data.get('status', 'unknown')
                done = data.get('done_chunks', 0)
                total = data.get('total_chunks', 1)
                
                if status == 'COMPLETED':
                    status_label.set_text(f'✅ COMPLET! {done}/{total} chunks')
                    ui.notify('🎉 Task finalizat!', type='positive')
                    # Update worker list
                    await check_status()
                    return
                elif status == 'FAILED':
                    status_label.set_text('❌ Task eșuat')
                    return
                else:
                    status_label.set_text(f'⏳ Procesare... {done}/{total} chunks')
                    
            except Exception as e:
                pass
            
            await asyncio.sleep(1)
        
        status_label.set_text('⏱️ Timeout - verifică manual')
    
    import asyncio
    ui.button('🚀 START', on_click=lambda: submit_task()).classes('mt-2 bg-green-600')

def pick_file(input_field):
    """File picker"""
    from tkinter import filedialog, Tk
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.destroy()
    if file_path:
        input_field.set_value(file_path)
        analyze_file_ui(file_path)

# Check status on startup
app.on_startup(check_status)

# Run
ui.run(title='QA DNA Desktop', port=8080, reload=False)
