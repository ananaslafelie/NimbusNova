"""
QA DNA Desktop - Aplicație Desktop cu NiceGUI
Simplificată pentru a funcționa corect
"""

import sys
import os
from pathlib import Path
import httpx
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nicegui import ui, app
from task_manager import TaskDistributor
from ai_scanner import AITaskScanner

# Global state
distributor = TaskDistributor()
scanner = AITaskScanner()
current_task = None
master_url = "http://localhost:8003"

# Auto-refresh timer
refresh_timer = None

# Variabile UI
detected_file = None
detected_info = {}

def analyze_file(path_str):
    """Analizează fișierul selectat"""
    global detected_file, detected_info
    
    if not path_str or not os.path.exists(path_str):
        ui.notify('❌ Fișier invalid!', type='negative')
        return
    
    try:
        analysis = scanner.analyze_file(Path(path_str))
        if analysis:
            detected_file = Path(path_str)
            detected_info = {
                'category': analysis.category.value,
                'plugin': analysis.suggested_plugin,
                'complexity': analysis.estimated_complexity,
                'size': analysis.metadata.get('size_human', 'N/A'),
                'confidence': f"{analysis.confidence:.0%}"
            }
            
            # Update UI
            file_info.set_text(f"📄 Detectat: {analysis.category.value}")
            plugin_info.set_text(f"🔧 Plugin: {analysis.suggested_plugin}")
            complexity_info.set_text(f"📊 Complexitate: {analysis.estimated_complexity}")
            size_info.set_text(f"💾 Dimensiune: {analysis.metadata.get('size_human', 'N/A')}")
            confidence_info.set_text(f"✅ Încredere: {analysis.confidence:.0%}")
            
            # Auto-set chunks
            if analysis.estimated_complexity == 'high':
                num_chunks.set_value(10)
            elif analysis.estimated_complexity == 'medium':
                num_chunks.set_value(5)
            else:
                num_chunks.set_value(2)
            
            ui.notify(f'✅ Detectat: {analysis.category.value}', type='positive')
            start_btn.enable()
    except Exception as e:
        ui.notify(f'❌ Eroare: {str(e)}', type='negative')

def pick_file():
    """Deschide file picker"""
    try:
        from tkinter import filedialog, Tk
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Selectează un fișier",
            filetypes=[
                ("Python", "*.py"),
                ("CSV", "*.csv"),
                ("JSON", "*.json"),
                ("STL 3D", "*.stl"),
                ("Toate fișierele", "*.*"),
            ]
        )
        root.destroy()
        if file_path:
            file_input.set_value(file_path)
            analyze_file(file_path)
    except Exception as e:
        ui.notify(f'❌ Eroare file picker: {str(e)}', type='negative')

def start_processing():
    """Pornește procesarea"""
    global current_task
    
    file_path = file_input.value
    if not file_path or not os.path.exists(file_path):
        ui.notify('❌ Selectează un fișier valid!', type='negative')
        return
    
    try:
        chunks = int(num_chunks.value)
        prio = priority.value
        
        task = distributor.create_task_from_file(
            Path(file_path),
            num_chunks=chunks,
            priority=prio
        )
        
        if task:
            current_task = task
            status_label.set_text(f"⏳ Task creat: {task.name} ({chunks} chunks)")
            progress_label.set_text("Așteaptă workeri...")
            ui.notify(f'🚀 Task {task.name} creat!', type='positive')
            
            # Simulare progres
            ui.timer(2.0, lambda: update_progress(), once=True)
        else:
            ui.notify('❌ Nu s-a putut crea taskul', type='negative')
    except Exception as e:
        ui.notify(f'❌ Eroare: {str(e)}', type='negative')

def update_progress():
    """Simulare actualizare progres"""
    progress_label.set_text("✅ Task în coadă - așteaptă procesare...")
    progress_bar.set_value(0.2)

async def check_status():
    """Verifică status sistem de la Master API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{master_url}/status", timeout=5.0)
            data = response.json()
            
            workers = data.get('workers', [])
            
            if workers:
                worker_texts = []
                for w in workers:
                    status_icon = "🟢" if w.get('status') == 'ONLINE' else "🔴"
                    worker_texts.append(f"{status_icon} {w['id']} ({w.get('cpu', 0):.0f}% CPU)")
                
                workers_label.set_text("🖥️ Workeri: " + ", ".join(worker_texts))
                
                # Update progress if there's a task
                tasks = data.get('tasks', [])
                if tasks:
                    task = tasks[0]  # First task
                    status_label.set_text(f"⏳ Task: {task[0]} - {task[1]}")
                    progress = task[2] / task[3] if task[3] > 0 else 0
                    progress_bar.set_value(progress)
                    progress_label.set_text(f"Progress: {task[2]}/{task[3]} chunks")
                
                ui.notify(f'✅ {len(workers)} workeri conectați', type='positive')
            else:
                workers_label.set_text("🖥️ Workeri: Niciunul conectat")
                ui.notify('⚠️ Niciun worker conectat', type='warning')
                
    except Exception as e:
        workers_label.set_text(f"🖥️ Eroare conexiune: {str(e)[:50]}")
        ui.notify(f'❌ Eroare: {str(e)}', type='negative')

# UI Principal
with ui.header().classes('bg-blue-600 text-white p-4'):
    ui.label('🧬 QA DNA Desktop').classes('text-2xl font-bold')
    ui.label('Procesare distribuită pe multiple dispozitive').classes('text-sm opacity-80')

with ui.row().classes('w-full p-4 gap-4'):
    # Panel stânga - Upload
    with ui.card().classes('w-1/2'):
        ui.label('📁 Selectare Fișier').classes('text-xl font-bold mb-4')
        
        # File input
        with ui.row().classes('w-full gap-2'):
            file_input = ui.input(label='Cale fișier', placeholder='Selectează un fișier...').classes('flex-grow')
            ui.button('📂 Browse', on_click=pick_file).classes('bg-blue-500')
        
        # Info detectat
        with ui.card().classes('w-full mt-4 bg-gray-100'):
            file_info = ui.label('📄 Detectat: -').classes('font-bold text-blue-600')
            plugin_info = ui.label('🔧 Plugin: -')
            complexity_info = ui.label('📊 Complexitate: -')
            size_info = ui.label('💾 Dimensiune: -')
            confidence_info = ui.label('✅ Încredere: -')
        
        # Configurare
        ui.separator().classes('my-4')
        ui.label('⚙️ Configurare').classes('text-lg font-bold')
        
        with ui.row().classes('w-full gap-4'):
            ui.label('Chunks:')
            num_chunks = ui.slider(min=1, max=20, value=5).classes('w-32')
            chunks_label = ui.label('5')
            num_chunks.on('change', lambda e: chunks_label.set_text(str(int(num_chunks.value))))
        
        priority = ui.select(['low', 'normal', 'high'], value='normal', label='Prioritate').classes('w-full')
        
        # Start button
        start_btn = ui.button('🚀 START PROCESARE', on_click=start_processing)
        start_btn.classes('w-full bg-green-600 text-white mt-4')
        start_btn.disable()
    
    # Panel dreapta - Status
    with ui.card().classes('w-1/2'):
        ui.label('📊 Status Sistem').classes('text-xl font-bold mb-4')
        
        workers_label = ui.label('🖥️ Workeri: Niciunul conectat').classes('mb-2')
        
        ui.separator().classes('my-4')
        
        status_label = ui.label('⏳ Niciun task activ').classes('font-bold')
        
        progress_bar = ui.linear_progress(value=0).classes('w-full mt-2')
        progress_label = ui.label('Așteaptă...').classes('text-gray-500 text-sm')
        
        ui.separator().classes('my-4')
        
        ui.label('📝 Instrucțiuni:').classes('text-sm font-bold')
        ui.label('1. Selectează un fișier (.py, .csv, .json)').classes('text-xs')
        ui.label('2. Configurează numărul de chunks').classes('text-xs')
        ui.label('3. Click START PROCESARE').classes('text-xs')
        ui.label('4. Taskul se distribuie automat').classes('text-xs')
        
        ui.button('🔄 Refresh Status', on_click=lambda: asyncio.create_task(check_status())).classes('mt-4 bg-blue-500')
        
        # Auto-refresh la fiecare 3 secunde
        ui.timer(3.0, lambda: asyncio.create_task(check_status()))

with ui.footer().classes('bg-gray-800 text-white p-2 text-center'):
    ui.label('QA DNA Desktop v1.0 | Cross-Platform Distributed Computing').classes('text-xs opacity-60')

# Pornire
print("🚀 QA DNA Desktop - Pornire...")
print("=" * 50)
print("Accesează în browser: http://localhost:8080")
print("=" * 50)

# Verificare inițială la pornire
app.on_startup(lambda: asyncio.create_task(check_status()))

ui.run(
    title='QA DNA Desktop',
    host='0.0.0.0',
    port=8080,
    reload=False,
    show=True
)
