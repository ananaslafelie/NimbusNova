"""
QA DNA - Task Manager System
Modular Plugin-Based Architecture
Cross-Platform: Windows | macOS | Linux
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qa_dna")


class TaskType(Enum):
    """Tipuri de taskuri suportate."""
    PYTHON_SCRIPT = "python_script"
    DATA_PROCESSING = "data_processing"
    MEDIA_PROCESSING = "media_processing"
    BUILD_TASK = "build_task"
    GENERIC = "generic"


class TaskStatus(Enum):
    """Statusuri posibile pentru un task."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Reprezentare generică a unui task."""
    id: str
    task_type: TaskType
    name: str
    data: Dict[str, Any]
    files: List[Path] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculează durata taskului în secunde."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class TaskPlugin(ABC):
    """Interfață abstractă pentru plugin-uri de taskuri."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Numele pluginului."""
        pass
    
    @property
    @abstractmethod
    def task_type(self) -> TaskType:
        """Tipul de task suportat."""
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Extensii de fișiere suportate."""
        pass
    
    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Verifică dacă pluginul poate procesa un fișier dat."""
        pass
    
    @abstractmethod
    def split_task(self, task: Task) -> List[Task]:
        """Împarte taskul în sub-taskuri (chunks)."""
        pass
    
    @abstractmethod
    async def execute_chunk(self, chunk: Task, worker_id: str) -> Any:
        """Execută un chunk pe un worker."""
        pass
    
    @abstractmethod
    def merge_results(self, chunks: List[Task]) -> Any:
        """Reasamblează rezultatele chunk-urilor."""
        pass


class PythonScriptPlugin(TaskPlugin):
    """Plugin pentru executarea scripturilor Python distribuite."""
    
    @property
    def name(self) -> str:
        return "Python Script Executor"
    
    @property
    def task_type(self) -> TaskType:
        return TaskType.PYTHON_SCRIPT
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".py", ".pyw"]
    
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.supported_extensions
    
    def split_task(self, task: Task) -> List[Task]:
        """Pentru Python, putem împărți după range-uri de date sau funcții."""
        chunks = []
        
        # Citim scriptul
        script_path = task.files[0] if task.files else None
        if not script_path:
            return [task]
        
        # Pentru început, 1 chunk = 1 script complet
        # Ulterior putem face analiză AST să împărțim în funcții
        num_chunks = task.data.get("num_chunks", 1)
        
        for i in range(num_chunks):
            chunk_id = f"{task.id}_chunk_{i}"
            chunk = Task(
                id=chunk_id,
                task_type=self.task_type,
                name=f"{task.name} - Chunk {i}",
                data={
                    **task.data,
                    "chunk_index": i,
                    "total_chunks": num_chunks,
                    "script_path": str(script_path),
                },
                files=task.files,
                metadata={"parent_task": task.id}
            )
            chunks.append(chunk)
        
        return chunks
    
    async def execute_chunk(self, chunk: Task, worker_id: str) -> Any:
        """Execută scriptul Python pe worker."""
        script_path = chunk.data.get("script_path")
        chunk_index = chunk.data.get("chunk_index", 0)
        
        logger.info(f"[Worker {worker_id}] Executing {script_path} chunk {chunk_index}")
        
        # Simulare execuție (în realitate, am rula subprocess)
        await asyncio.sleep(0.5)  # Simulare procesare
        
        return {
            "worker_id": worker_id,
            "chunk_index": chunk_index,
            "status": "success",
            "output": f"Processed by {worker_id}, chunk {chunk_index}",
            "timestamp": datetime.now().isoformat()
        }
    
    def merge_results(self, chunks: List[Task]) -> Any:
        """Reasamblează rezultatele."""
        return {
            "status": "completed",
            "total_chunks": len(chunks),
            "results": [c.result for c in chunks if c.result],
            "completed_at": datetime.now().isoformat()
        }


class TaskPluginRegistry:
    """Registru pentru plugin-uri."""
    
    def __init__(self):
        self._plugins: Dict[TaskType, TaskPlugin] = {}
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """Înregistrează plugin-urile default."""
        self.register(PythonScriptPlugin())
    
    def register(self, plugin: TaskPlugin):
        """Înregistrează un plugin."""
        self._plugins[plugin.task_type] = plugin
        logger.info(f"Registered plugin: {plugin.name} for {plugin.task_type.value}")
    
    def get_plugin(self, task_type: TaskType) -> Optional[TaskPlugin]:
        """Obține plugin-ul pentru un tip de task."""
        return self._plugins.get(task_type)
    
    def detect_task_type(self, file_path: Path) -> Optional[TaskType]:
        """Detectează automat tipul de task bazat pe fișier."""
        for task_type, plugin in self._plugins.items():
            if plugin.can_handle(file_path):
                return task_type
        return None
    
    def list_plugins(self) -> List[str]:
        """Lista plugin-urilor disponibile."""
        return [p.name for p in self._plugins.values()]


class TaskDistributor:
    """Distribuitor central de taskuri."""
    
    def __init__(self):
        self.registry = TaskPluginRegistry()
        self.tasks: Dict[str, Task] = {}
        self.chunks: Dict[str, Task] = {}
        self.results: Dict[str, Any] = {}
    
    def create_task(self, name: str, task_type: TaskType, 
                    data: Dict[str, Any], files: List[Path] = None) -> Task:
        """Creează un task nou."""
        task_id = hashlib.md5(f"{name}_{datetime.now()}".encode()).hexdigest()[:12]
        task = Task(
            id=task_id,
            task_type=task_type,
            name=name,
            data=data,
            files=files or [],
            status=TaskStatus.PENDING
        )
        self.tasks[task_id] = task
        return task
    
    def create_task_from_file(self, file_path: Path, **kwargs) -> Optional[Task]:
        """Creează automat un task dintr-un fișier."""
        task_type = self.registry.detect_task_type(file_path)
        if not task_type:
            logger.error(f"Nu am găsit plugin pentru {file_path}")
            return None
        
        return self.create_task(
            name=file_path.stem,
            task_type=task_type,
            data=kwargs,
            files=[file_path]
        )
    
    def split_task(self, task_id: str) -> List[Task]:
        """Împarte un task în chunks."""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} nu există")
        
        plugin = self.registry.get_plugin(task.task_type)
        if not plugin:
            raise ValueError(f"Nu există plugin pentru {task.task_type}")
        
        chunks = plugin.split_task(task)
        for chunk in chunks:
            self.chunks[chunk.id] = chunk
            chunk.status = TaskStatus.QUEUED
        
        task.status = TaskStatus.QUEUED
        return chunks
    
    async def execute_chunk(self, chunk_id: str, worker_id: str) -> Any:
        """Execută un chunk pe un worker."""
        chunk = self.chunks.get(chunk_id)
        if not chunk:
            raise ValueError(f"Chunk {chunk_id} nu există")
        
        plugin = self.registry.get_plugin(chunk.task_type)
        if not plugin:
            raise ValueError(f"Nu există plugin pentru {chunk.task_type}")
        
        chunk.status = TaskStatus.RUNNING
        chunk.started_at = datetime.now()
        
        try:
            result = await plugin.execute_chunk(chunk, worker_id)
            chunk.result = result
            chunk.status = TaskStatus.COMPLETED
            chunk.completed_at = datetime.now()
        except Exception as e:
            chunk.error = str(e)
            chunk.status = TaskStatus.FAILED
            logger.error(f"Chunk {chunk_id} failed: {e}")
            raise
        
        return result
    
    def merge_task_results(self, task_id: str) -> Any:
        """Reasamblează rezultatele unui task complet."""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} nu există")
        
        # Găsește toate chunks pentru acest task
        task_chunks = [
            c for c in self.chunks.values()
            if c.metadata.get("parent_task") == task_id
        ]
        
        plugin = self.registry.get_plugin(task.task_type)
        if not plugin:
            raise ValueError(f"Nu există plugin pentru {task.task_type}")
        
        result = plugin.merge_results(task_chunks)
        self.results[task_id] = result
        task.result = result
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        
        return result
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Obține statusul complet al unui task."""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": "Task not found"}
        
        chunks = [c for c in self.chunks.values() 
                  if c.metadata.get("parent_task") == task_id]
        
        return {
            "task_id": task_id,
            "name": task.name,
            "type": task.task_type.value,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "duration": task.duration,
            "total_chunks": len(chunks),
            "completed_chunks": sum(1 for c in chunks if c.status == TaskStatus.COMPLETED),
            "failed_chunks": sum(1 for c in chunks if c.status == TaskStatus.FAILED),
            "progress": f"{sum(1 for c in chunks if c.status == TaskStatus.COMPLETED)}/{len(chunks)}"
        }


# Test/Demo
if __name__ == "__main__":
    print("🧪 QA DNA Task Manager - Test Mode")
    print("=" * 50)
    
    # Creăm distribuitorul
    distributor = TaskDistributor()
    
    # Afișăm plugin-urile disponibile
    print(f"\n📦 Plugin-uri disponibile: {distributor.registry.list_plugins()}")
    
    # Testăm crearea unui task Python
    print("\n🐍 Creăm task Python...")
    test_script = Path("test_script.py")
    
    # Creăm un fișier de test
    with open(test_script, "w") as f:
        f.write("print('Hello from distributed Python!')")
    
    task = distributor.create_task_from_file(
        test_script,
        num_chunks=3,
        timeout=30
    )
    
    if task:
        print(f"✅ Task creat: {task.name} (ID: {task.id})")
        print(f"   Tip: {task.task_type.value}")
        print(f"   Fișiere: {[f.name for f in task.files]}")
        
        # Împărțim în chunks
        print("\n📊 Împărțim în chunks...")
        chunks = distributor.split_task(task.id)
        print(f"✅ {len(chunks)} chunks create")
        
        # Simulăm execuția
        print("\n⚡ Simulăm execuție distribuită...")
        
        async def simulate():
            for i, chunk in enumerate(chunks):
                worker = f"worker-{i+1}"
                print(f"   [Worker {worker}] Procesez {chunk.id}...")
                await distributor.execute_chunk(chunk.id, worker)
                print(f"   ✅ Complet")
        
        asyncio.run(simulate())
        
        # Reasamblăm rezultatele
        print("\n🔧 Reasamblare rezultate...")
        result = distributor.merge_task_results(task.id)
        print(f"✅ Task complet! Rezultat: {json.dumps(result, indent=2, default=str)}")
        
        # Status final
        print("\n📋 Status final:")
        status = distributor.get_task_status(task.id)
        for key, value in status.items():
            print(f"   {key}: {value}")
    
    # Curățăm
    test_script.unlink(missing_ok=True)
    print("\n✨ Test complet!")
