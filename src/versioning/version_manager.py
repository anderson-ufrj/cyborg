#!/usr/bin/env python3
"""
Intelligent Version Manager for Prompt Engineering System
Gerencia versionamento semântico com detecção automática de mudanças

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brazil
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class VersionChange:
    type: str  # major, minor, patch
    description: str
    impact_score: float  # 0.0 - 1.0
    files_affected: List[str]
    timestamp: str

class VersionManager:
    def __init__(self, base_path: Path = Path("anderson-skill")):
        self.base_path = base_path
        self.versions_path = base_path / "meta" / "versions"
        self.versions_path.mkdir(parents=True, exist_ok=True)
        self.current_version = self._load_current_version()
        
    def _load_current_version(self) -> str:
        """Carrega versão atual do sistema"""
        version_file = self.base_path / "meta" / "current_version.json"
        if version_file.exists():
            with open(version_file) as f:
                data = json.load(f)
                return data.get("version", "0.1.0")
        return "0.1.0"
    
    def analyze_changes(self, changes: List[Dict]) -> str:
        """Analisa mudanças e sugere novo versionamento"""
        if not changes:
            return self.current_version
            
        # Calcula impacto total
        total_impact = sum(change.get("impact_score", 0) for change in changes)
        max_impact = max(change.get("impact_score", 0) for change in changes)
        
        # Determina tipo de versão baseado no impacto
        if max_impact >= 0.8:
            change_type = "major"
        elif max_impact >= 0.5 or total_impact >= 1.5:
            change_type = "minor"
        else:
            change_type = "patch"
            
        # Gera nova versão
        new_version = self._bump_version(self.current_version, change_type)
        
        # Registra mudanças
        self._record_version_change(new_version, changes, change_type)
        
        return new_version
    
    def _bump_version(self, current: str, change_type: str) -> str:
        """Incrementa versão baseado no tipo de mudança"""
        major, minor, patch = map(int, current.split('.'))
        
        if change_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif change_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
            
        return f"{major}.{minor}.{patch}"
    
    def _record_version_change(self, new_version: str, changes: List[Dict], change_type: str):
        """Registra mudança de versão com detalhes"""
        version_data = {
            "version": new_version,
            "previous_version": self.current_version,
            "change_type": change_type,
            "timestamp": datetime.now().isoformat(),
            "changes": changes,
            "summary": {
                "total_changes": len(changes),
                "total_impact": sum(c.get("impact_score", 0) for c in changes),
                "files_modified": list(set(flatten([c.get("files_affected", []) for c in changes])))
            }
        }
        
        # Salva registro da versão
        version_file = self.versions_path / f"v{new_version.replace('.', '_')}.json"
        with open(version_file, 'w') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
        
        # Atualiza versão atual
        self._update_current_version(new_version)
        self.current_version = new_version
        
    def _update_current_version(self, new_version: str):
        """Atualiza arquivo de versão atual"""
        version_file = self.base_path / "meta" / "current_version.json"
        with open(version_file, 'w') as f:
            json.dump({
                "version": new_version,
                "updated_at": datetime.now().isoformat(),
                "changelog_summary": self._generate_changelog_summary(new_version)
            }, f, indent=2, ensure_ascii=False)
    
    def _generate_changelog_summary(self, version: str) -> str:
        """Gera resumo do changelog para a versão"""
        version_file = self.versions_path / f"v{version.replace('.', '_')}.json"
        if not version_file.exists():
            return "Version details not found"
            
        with open(version_file) as f:
            data = json.load(f)
            
        change_type = data["change_type"]
        changes = data["changes"]
        
        summary = f"{change_type.title()} version with {len(changes)} changes"
        if changes:
            high_impact = [c for c in changes if c.get("impact_score", 0) > 0.7]
            if high_impact:
                summary += f", including {len(high_impact)} high-impact changes"
                
        return summary
    
    def detect_changes_from_files(self, file_changes: List[Dict]) -> List[Dict]:
        """Detecta tipos de mudanças a partir de modificações de arquivos"""
        detected_changes = []
        
        for change in file_changes:
            file_path = change["file"]
            change_type = change["type"]  # added, modified, deleted
            
            # Analisa impacto baseado no arquivo modificado
            impact_analysis = self._analyze_file_impact(file_path, change_type)
            
            if impact_analysis:
                detected_changes.append({
                    "type": impact_analysis["change_type"],
                    "description": impact_analysis["description"],
                    "impact_score": impact_analysis["impact_score"],
                    "files_affected": [file_path],
                    "timestamp": datetime.now().isoformat()
                })
                
        return detected_changes
    
    def _analyze_file_impact(self, file_path: str, change_type: str) -> Optional[Dict]:
        """Analiza impacto de mudança em arquivo específico"""
        impact_map = {
            # Core files - alto impacto
            "anderson-skill/core/identity.md": {
                "change_type": "major",
                "description": "Core identity changes - fundamental context shift",
                "impact_score": 0.9
            },
            "anderson-skill/core/communication-style.md": {
                "change_type": "major",
                "description": "Communication style changes - affects all interactions",
                "impact_score": 0.85
            },
            "anderson-skill/core/technical-profile.md": {
                "change_type": "minor",
                "description": "Technical profile updates - new capabilities",
                "impact_score": 0.6
            },
            # Dynamic files - médio impacto
            "anderson-skill/dynamic/career-status.md": {
                "change_type": "minor",
                "description": "Career status update - context refinement",
                "impact_score": 0.5
            },
            "anderson-skill/dynamic/goals.md": {
                "change_type": "minor",
                "description": "Goals update - priority shifts",
                "impact_score": 0.4
            },
            # Context files - médio/baixo impacto
            "anderson-skill/contexts/": {
                "change_type": "patch",
                "description": "Context mode adjustments",
                "impact_score": 0.3
            },
            # Interactions - baixo impacto
            "anderson-skill/interactions/": {
                "change_type": "patch",
                "description": "Calibration examples update",
                "impact_score": 0.2
            }
        }
        
        # Procura correspondência exata
        if file_path in impact_map:
            return impact_map[file_path]
            
        # Procura por padrões de diretório
        for pattern, analysis in impact_map.items():
            if pattern.endswith("/") and file_path.startswith(pattern):
                return analysis
                
        # Default para arquivos não mapeados
        return {
            "change_type": "patch",
            "description": f"File {change_type}: {file_path}",
            "impact_score": 0.1
        }
    
    def get_version_history(self, limit: int = 10) -> List[Dict]:
        """Retorna histórico de versões"""
        versions = []
        
        for version_file in sorted(self.versions_path.glob("v*.json"), reverse=True):
            with open(version_file) as f:
                version_data = json.load(f)
                versions.append({
                    "version": version_data["version"],
                    "change_type": version_data["change_type"],
                    "timestamp": version_data["timestamp"],
                    "summary": version_data["summary"]
                })
                
        return versions[:limit]
    
    def suggest_next_changes(self) -> List[str]:
        """Sugere próximas mudanças baseadas em padrões"""
        suggestions = []
        
        # Analisa versões recentes
        recent_versions = self.get_version_history(5)
        
        if not recent_versions:
            return ["Start with baseline version 0.1.0"]
            
        # Verifica se tem muitos patches seguidos
        recent_types = [v["change_type"] for v in recent_versions]
        if recent_types.count("patch") >= 3:
            suggestions.append("Consider a minor version to bundle recent refinements")
            
        # Verifica tempo desde última versão
        if recent_versions:
            last_update = datetime.fromisoformat(recent_versions[0]["timestamp"])
            days_since_update = (datetime.now() - last_update).days
            if days_since_update > 30:
                suggestions.append(f"No updates in {days_since_update} days - consider if system needs evolution")
                
        # Sugere baseado no roadmap
        suggestions.extend([
            "Review evidence base for new patterns",
            "Consider A/B testing recent hypothesis",
            "Update interaction examples with recent good/bad patterns"
        ])
        
        return suggestions

def flatten(lst):
    """Helper para flatten list aninhada"""
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result

# Exemplo de uso
if __name__ == "__main__":
    manager = VersionManager()
    
    # Simula detecção de mudanças
    file_changes = [
        {"file": "anderson-skill/core/identity.md", "type": "modified"},
        {"file": "anderson-skill/dynamic/career-status.md", "type": "modified"},
        {"file": "anderson-skill/interactions/good/example1.md", "type": "added"}
    ]
    
    detected_changes = manager.detect_changes_from_files(file_changes)
    print(f"Detected changes: {len(detected_changes)}")
    
    # Analisa e sugere nova versão
    new_version = manager.analyze_changes(detected_changes)
    print(f"Suggested version: {new_version}")
    
    # Mostra histórico
    history = manager.get_version_history(5)
    print(f"Version history: {len(history)} versions")
    
    # Sugere próximas mudanças
    suggestions = manager.suggest_next_changes()
    print(f"Next change suggestions: {suggestions}")