"""
QA DNA - AI Task Scanner
Agent AI care analizează foldere și detectează automat tipurile de taskuri
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import mimetypes
import magic  # python-magic pentru detectare avansată

logger = logging.getLogger("qa_dna.ai_scanner")


class FileCategory(Enum):
    """Categorii de fișiere detectate."""
    PYTHON_SCRIPT = "python_script"
    DATA_CSV = "data_csv"
    DATA_JSON = "data_json"
    IMAGE = "image"
    VIDEO = "video"
    STL_3D = "stl_3d"
    SOURCE_CODE = "source_code"
    BUILD_CONFIG = "build_config"
    UNKNOWN = "unknown"


@dataclass
class FileAnalysis:
    """Rezultatul analizei unui fișier."""
    path: Path
    category: FileCategory
    confidence: float  # 0.0 - 1.0
    suggested_plugin: str
    estimated_complexity: str  # "low", "medium", "high"
    metadata: Dict
    recommendations: List[str]


class AITaskScanner:
    """Agent AI pentru scanarea și clasificarea taskurilor."""
    
    def __init__(self):
        self.mime = magic.Magic(mime=True)
        self.mime_encoding = magic.Magic(mime_encoding=True)
        
        # Mapare extensii -> categorii
        self.extension_map = {
            '.py': FileCategory.PYTHON_SCRIPT,
            '.pyw': FileCategory.PYTHON_SCRIPT,
            '.ipynb': FileCategory.PYTHON_SCRIPT,
            '.csv': FileCategory.DATA_CSV,
            '.tsv': FileCategory.DATA_CSV,
            '.json': FileCategory.DATA_JSON,
            '.jsonl': FileCategory.DATA_JSON,
            '.stl': FileCategory.STL_3D,
            '.obj': FileCategory.STL_3D,
            '.ply': FileCategory.STL_3D,
            '.png': FileCategory.IMAGE,
            '.jpg': FileCategory.IMAGE,
            '.jpeg': FileCategory.IMAGE,
            '.gif': FileCategory.IMAGE,
            '.bmp': FileCategory.IMAGE,
            '.tiff': FileCategory.IMAGE,
            '.mp4': FileCategory.VIDEO,
            '.avi': FileCategory.VIDEO,
            '.mov': FileCategory.VIDEO,
            '.mkv': FileCategory.VIDEO,
            '.cpp': FileCategory.SOURCE_CODE,
            '.c': FileCategory.SOURCE_CODE,
            '.h': FileCategory.SOURCE_CODE,
            '.hpp': FileCategory.SOURCE_CODE,
            '.rs': FileCategory.SOURCE_CODE,
            '.go': FileCategory.SOURCE_CODE,
            '.java': FileCategory.SOURCE_CODE,
            '.scala': FileCategory.SOURCE_CODE,
            '.kt': FileCategory.SOURCE_CODE,
            '.cmake': FileCategory.BUILD_CONFIG,
            '.mk': FileCategory.BUILD_CONFIG,
            'makefile': FileCategory.BUILD_CONFIG,
            'cargo.toml': FileCategory.BUILD_CONFIG,
            'package.json': FileCategory.BUILD_CONFIG,
        }
    
    def scan_folder(self, folder_path: Path, recursive: bool = True) -> List[FileAnalysis]:
        """Scanează un folder și returnează analiza tuturor fișierelor."""
        logger.info(f"🔍 Scanare folder: {folder_path}")
        
        results = []
        pattern = "**/*" if recursive else "*"
        
        for file_path in folder_path.glob(pattern):
            if file_path.is_file():
                analysis = self.analyze_file(file_path)
                if analysis:
                    results.append(analysis)
        
        # Sortează după complexitate (high -> low -> medium)
        complexity_order = {"high": 0, "low": 1, "medium": 2}
        results.sort(key=lambda x: complexity_order.get(x.estimated_complexity, 3))
        
        logger.info(f"✅ Scanare completă: {len(results)} fișiere detectate")
        return results
    
    def analyze_file(self, file_path: Path) -> Optional[FileAnalysis]:
        """Analizează un singur fișier."""
        try:
            # Detectare bazată pe extensie
            ext = file_path.suffix.lower()
            name = file_path.name.lower()
            
            category = self.extension_map.get(ext)
            if not category and name in self.extension_map:
                category = self.extension_map[name]
            
            if not category:
                category = FileCategory.UNKNOWN
            
            # Detectare MIME pentru validare
            mime_type = self.mime.from_file(str(file_path))
            
            # Calculează confidence și complexitate
            confidence = self._calculate_confidence(file_path, category, mime_type)
            complexity = self._estimate_complexity(file_path, category)
            plugin = self._suggest_plugin(category)
            metadata = self._extract_metadata(file_path, category, mime_type)
            recommendations = self._generate_recommendations(file_path, category, metadata)
            
            return FileAnalysis(
                path=file_path,
                category=category,
                confidence=confidence,
                suggested_plugin=plugin,
                estimated_complexity=complexity,
                metadata=metadata,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Eroare analiză {file_path}: {e}")
            return None
    
    def _calculate_confidence(self, file_path: Path, category: FileCategory, mime_type: str) -> float:
        """Calculează confidence-ul detectării."""
        confidence = 0.5  # Base
        
        # Verificare extensie cunoscută
        if category != FileCategory.UNKNOWN:
            confidence += 0.3
        
        # Verificare MIME valid
        if mime_type and mime_type != "application/octet-stream":
            confidence += 0.2
        
        # Fișier accesibil
        if file_path.stat().st_size > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _estimate_complexity(self, file_path: Path, category: FileCategory) -> str:
        """Estimează complexitatea procesării."""
        size = file_path.stat().st_size
        
        # Dimensiune
        if size < 1024:  # < 1KB
            return "low"
        elif size < 1024 * 1024:  # < 1MB
            return "medium"
        else:  # > 1MB
            # Pentru fișiere mari, depinde de tip
            if category in [FileCategory.IMAGE, FileCategory.VIDEO, FileCategory.STL_3D]:
                return "high"
            return "medium"
    
    def _suggest_plugin(self, category: FileCategory) -> str:
        """Sugerează plugin-ul potrivit."""
        plugin_map = {
            FileCategory.PYTHON_SCRIPT: "Python Script Executor",
            FileCategory.DATA_CSV: "Data Processor (CSV)",
            FileCategory.DATA_JSON: "Data Processor (JSON)",
            FileCategory.IMAGE: "Media Processor (Image)",
            FileCategory.VIDEO: "Media Processor (Video)",
            FileCategory.STL_3D: "3D Processor (STL)",
            FileCategory.SOURCE_CODE: "Build System (Compile)",
            FileCategory.BUILD_CONFIG: "Build System (Config)",
            FileCategory.UNKNOWN: "Generic Processor",
        }
        return plugin_map.get(category, "Generic Processor")
    
    def _extract_metadata(self, file_path: Path, category: FileCategory, mime_type: str) -> Dict:
        """Extrage metadate din fișier."""
        stat = file_path.stat()
        
        metadata = {
            "size_bytes": stat.st_size,
            "size_human": self._human_readable_size(stat.st_size),
            "mime_type": mime_type,
            "modified": stat.st_mtime,
        }
        
        # Extrage info specific per categorie
        if category == FileCategory.PYTHON_SCRIPT:
            metadata.update(self._analyze_python_file(file_path))
        elif category in [FileCategory.DATA_CSV, FileCategory.DATA_JSON]:
            metadata.update(self._analyze_data_file(file_path, category))
        elif category == FileCategory.IMAGE:
            metadata.update(self._analyze_image_file(file_path))
        
        return metadata
    
    def _analyze_python_file(self, file_path: Path) -> Dict:
        """Analizează un fișier Python."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Numără elementele
            imports = [l for l in lines if l.strip().startswith('import ') or l.strip().startswith('from ')]
            functions = [l for l in lines if l.strip().startswith('def ')]
            classes = [l for l in lines if l.strip().startswith('class ')]
            
            return {
                "lines_of_code": len(lines),
                "imports": len(imports),
                "functions": len(functions),
                "classes": len(classes),
                "has_main": "if __name__ == \"__main__\"" in content or "if __name__ == '__main__'" in content,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_data_file(self, file_path: Path, category: FileCategory) -> Dict:
        """Analizează un fișier de date."""
        try:
            if category == FileCategory.DATA_CSV:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline()
                    delimiter = ',' if ',' in first_line else '\t' if '\t' in first_line else 'unknown'
                    columns = len(first_line.split(delimiter))
                    
                    # Estimare rânduri
                    size = file_path.stat().st_size
                    avg_line_size = len(first_line.encode('utf-8'))
                    estimated_rows = size // avg_line_size if avg_line_size > 0 else 0
                    
                    return {
                        "columns": columns,
                        "estimated_rows": estimated_rows,
                        "delimiter": delimiter,
                    }
            
            elif category == FileCategory.DATA_JSON:
                import json
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return {"type": "array", "items": len(data)}
                    elif isinstance(data, dict):
                        return {"type": "object", "keys": len(data)}
                    return {"type": type(data).__name__}
                    
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_image_file(self, file_path: Path) -> Dict:
        """Analizează un fișier imagine (fără PIL - doar bazat pe extensie)."""
        return {
            "format": file_path.suffix.upper().replace('.', ''),
            "needs_pil": True,  # Pentru procesare reală
        }
    
    def _generate_recommendations(self, file_path: Path, category: FileCategory, metadata: Dict) -> List[str]:
        """Generează recomandări pentru procesare."""
        recommendations = []
        
        if category == FileCategory.PYTHON_SCRIPT:
            if metadata.get("has_main"):
                recommendations.append("Script poate fi executat direct")
            if metadata.get("imports", 0) > 10:
                recommendations.append("Multe imports - verifică dependențele")
            if metadata.get("functions", 0) > 0:
                recommendations.append("Poate fi împărțit în chunks pe funcții")
        
        elif category in [FileCategory.DATA_CSV, FileCategory.DATA_JSON]:
            if metadata.get("estimated_rows", 0) > 10000:
                recommendations.append("Fișier mare - procesare în chunks recomandată")
            recommendations.append("Verifică encoding-ul (UTF-8 recomandat)")
        
        elif category == FileCategory.STL_3D:
            size_mb = metadata.get("size_bytes", 0) / (1024 * 1024)
            if size_mb > 50:
                recommendations.append("Fișier STL mare - procesare pe GPU recomandată")
            recommendations.append("Verifică integritatea mesh-ului înainte de procesare")
        
        elif category == FileCategory.SOURCE_CODE:
            recommendations.append("Compilare necesară - asigură-te că toolchains sunt instalate")
            recommendations.append("Verifică dependențele înainte de build")
        
        if not recommendations:
            recommendations.append("Procesare standard recomandată")
        
        return recommendations
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convertește bytes în format human-readable."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
    
    def generate_summary(self, analyses: List[FileAnalysis]) -> Dict:
        """Generează un rezumat al scanării."""
        if not analyses:
            return {"message": "Niciun fișier detectat"}
        
        categories = {}
        complexities = {"low": 0, "medium": 0, "high": 0}
        total_size = 0
        
        for analysis in analyses:
            cat = analysis.category.value
            categories[cat] = categories.get(cat, 0) + 1
            complexities[analysis.estimated_complexity] += 1
            total_size += analysis.metadata.get("size_bytes", 0)
        
        return {
            "total_files": len(analyses),
            "total_size": self._human_readable_size(total_size),
            "by_category": categories,
            "by_complexity": complexities,
            "suggested_processing_order": [
                {"file": str(a.path.name), "plugin": a.suggested_plugin}
                for a in analyses[:10]  # Top 10
            ]
        }


# Demo/Test
if __name__ == "__main__":
    import tempfile
    import os
    
    print("🧪 AI Task Scanner - Test Mode")
    print("=" * 60)
    
    # Creăm folder de test
    with tempfile.TemporaryDirectory() as tmpdir:
        test_folder = Path(tmpdir)
        
        # Creăm fișiere de test
        # Python script
        (test_folder / "process_data.py").write_text("""
import pandas as pd
import numpy as np

def analyze_data(file_path):
    df = pd.read_csv(file_path)
    return df.describe()

if __name__ == "__main__":
    print("Processing...")
""")
        
        # CSV file
        (test_folder / "data.csv").write_text("id,name,value\n1,Test,100\n2,Test2,200\n")
        
        # JSON file
        (test_folder / "config.json").write_text('{"workers": 3, "timeout": 30}')
        
        # STL-like (simulat)
        (test_folder / "model.stl").write_bytes(b"STL binary data placeholder")
        
        # Scanăm
        print(f"\n📁 Scanare folder: {test_folder}")
        scanner = AITaskScanner()
        
        try:
            analyses = scanner.scan_folder(test_folder)
            
            # Afișăm rezultatele
            print(f"\n📊 {len(analyses)} fișiere detectate:")
            print("-" * 60)
            
            for analysis in analyses:
                print(f"\n📄 {analysis.path.name}")
                print(f"   Categorie: {analysis.category.value}")
                print(f"   Plugin: {analysis.suggested_plugin}")
                print(f"   Complexitate: {analysis.estimated_complexity}")
                print(f"   Încredere: {analysis.confidence:.1%}")
                print(f"   Dimensiune: {analysis.metadata.get('size_human', 'N/A')}")
                print(f"   Recomandări:")
                for rec in analysis.recommendations:
                    print(f"      • {rec}")
            
            # Rezumat
            print("\n" + "=" * 60)
            print("📋 REZUMAT:")
            summary = scanner.generate_summary(analyses)
            print(json.dumps(summary, indent=2))
            
        except Exception as e:
            print(f"⚠️  Librăria 'python-magic' nu e instalată. Test simplu:")
            print(f"   pip install python-magic")
            print(f"   Eroare: {e}")
            
            # Test fallback fără magic
            print("\n🔄 Test fallback (fără magic):")
            scanner = AITaskScanner()
            scanner.mime = None  # Dezactivăm magic
            
            # Mock analyze
            for file_path in test_folder.iterdir():
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    category = scanner.extension_map.get(ext, FileCategory.UNKNOWN)
                    print(f"   {file_path.name} -> {category.value}")
    
    print("\n✨ Test complet!")
