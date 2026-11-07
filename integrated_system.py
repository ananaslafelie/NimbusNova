"""
QA DNA - Integrated System Demo
Sistem complet: Task Manager + AI Scanner + Distributie
"""

from pathlib import Path
import asyncio
import tempfile
import json
from task_manager import TaskDistributor, TaskType
from ai_scanner import AITaskScanner, FileCategory


class QADNASystem:
    """Sistemul complet QA DNA integrat."""
    
    def __init__(self):
        self.distributor = TaskDistributor()
        self.scanner = AITaskScanner()
        print("🚀 QA DNA System initialized")
        print(f"   Plugin-uri: {self.distributor.registry.list_plugins()}")
    
    async def process_folder(self, folder_path: Path, auto_execute: bool = True) -> dict:
        """Procesează un folder complet."""
        print(f"\n📁 Scanare folder: {folder_path}")
        
        # Pas 1: Scanare AI
        analyses = self.scanner.scan_folder(folder_path)
        summary = self.scanner.generate_summary(analyses)
        
        print(f"   Găsite {summary['total_files']} fișiere")
        print(f"   Dimensiune totală: {summary['total_size']}")
        
        # Pas 2: Creare task-uri
        tasks_created = []
        for analysis in analyses:
            if analysis.category == FileCategory.PYTHON_SCRIPT:
                task = self.distributor.create_task_from_file(
                    analysis.path,
                    num_chunks=2,  # Pentru demo
                    priority="normal"
                )
                if task:
                    tasks_created.append(task)
                    print(f"   ✅ Task creat: {task.name}")
        
        # Pas 3: Executare (opțional)
        if auto_execute and tasks_created:
            print(f"\n⚡ Executare {len(tasks_created)} task-uri...")
            results = await self._execute_tasks(tasks_created)
            return {
                "scanned": summary,
                "tasks": len(tasks_created),
                "results": results
            }
        
        return {
            "scanned": summary,
            "tasks": len(tasks_created),
            "tasks_pending": [t.id for t in tasks_created]
        }
    
    async def _execute_tasks(self, tasks: list) -> list:
        """Execută task-urile distribuit."""
        results = []
        
        for task in tasks:
            print(f"\n   🔄 Procesare {task.name}...")
            
            # Împărțim în chunks
            chunks = self.distributor.split_task(task.id)
            print(f"      Împărțit în {len(chunks)} chunks")
            
            # Executăm chunks (simulare workeri)
            for i, chunk in enumerate(chunks):
                worker_id = f"worker-{i % 3 + 1}"  # 3 workeri simulați
                await self.distributor.execute_chunk(chunk.id, worker_id)
            
            # Reasamblăm
            result = self.distributor.merge_task_results(task.id)
            results.append(result)
            
            # Status
            status = self.distributor.get_task_status(task.id)
            print(f"      ✅ Complet: {status['progress']} chunks")
        
        return results
    
    def get_system_status(self) -> dict:
        """Obține statusul complet al sistemului."""
        return {
            "plugins": self.distributor.registry.list_plugins(),
            "total_tasks": len(self.distributor.tasks),
            "total_chunks": len(self.distributor.chunks),
            "completed_results": len(self.distributor.results)
        }


async def demo():
    """Demo complet al sistemului."""
    print("=" * 70)
    print("🧪 QA DNA - Integrated System Demo")
    print("=" * 70)
    
    # Creăm sistemul
    system = QADNASystem()
    
    # Creăm folder de test
    with tempfile.TemporaryDirectory() as tmpdir:
        test_folder = Path(tmpdir)
        
        # Creăm diverse fișiere de test
        print("\n📂 Creare fișiere de test...")
        
        # 1. Script Python - Procesare date
        (test_folder / "data_processor.py").write_text("""
import pandas as pd
import numpy as np

def load_and_process(file_path):
    df = pd.read_csv(file_path)
    stats = df.describe()
    return stats

def analyze_correlations(df):
    return df.corr()

if __name__ == "__main__":
    print("Processing dataset...")
""")
        
        # 2. CSV - Date de test
        (test_folder / "sales_data.csv").write_text(
            "date,product,quantity,price\n" +
            "2024-01-01,Laptop,5,1200\n" +
            "2024-01-01,Mouse,20,25\n" +
            "2024-01-02,Laptop,3,1200\n" +
            "2024-01-02,Keyboard,10,80\n"
        )
        
        # 3. JSON - Configurare
        (test_folder / "pipeline_config.json").write_text(json.dumps({
            "workers": 3,
            "chunk_size": 10,
            "timeout": 30,
            "retry_attempts": 3
        }))
        
        # 4. Model STL (simulat)
        (test_folder / "component_v2.stl").write_bytes(
            b"solid component\nfacet normal 0 0 0\nouter loop\n"
            b"vertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\n"
            b"endsolid component\n"
        )
        
        # 5. Script Python - ML Inference
        (test_folder / "ml_predict.py").write_text("""
import torch
import numpy as np

def load_model(model_path):
    return torch.load(model_path)

def predict_batch(data, model):
    with torch.no_grad():
        return model(data)

if __name__ == "__main__":
    print("Running ML inference...")
""")
        
        print(f"   ✅ {len(list(test_folder.iterdir()))} fișiere create")
        
        # Procesăm folderul
        print("\n" + "=" * 70)
        print("🔄 PROCESARE FOLDER")
        print("=" * 70)
        
        result = await system.process_folder(test_folder, auto_execute=True)
        
        # Rezultat final
        print("\n" + "=" * 70)
        print("📊 REZULTAT FINAL")
        print("=" * 70)
        print(f"Fișiere scanate: {result['scanned']['total_files']}")
        print(f"Task-uri create: {result['tasks']}")
        print(f"Task-uri executate: {len(result.get('results', []))}")
        
        print("\n📋 Distribuție pe categorii:")
        for cat, count in result['scanned']['by_category'].items():
            print(f"   {cat}: {count} fișiere")
        
        print("\n🔧 Status sistem:")
        status = system.get_system_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
    
    print("\n" + "=" * 70)
    print("✨ Demo complet!")
    print("=" * 70)
    print("\n💡 Următorul pas: Adaugă plugin-uri noi:")
    print("   • DataProcessor (CSV/JSON)")
    print("   • MediaProcessor (Imagini/Video)")
    print("   • BuildSystem (C++/Rust)")
    print("   • STLProcessor (3D Printing)")


if __name__ == "__main__":
    asyncio.run(demo())
