#!/usr/bin/env python3
"""
Interaction Metrics Analyzer
Captura e analisa métricas de interações AI-humanas para calibração evolutiva

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brazil
"""

import json
import datetime
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class InteractionMetrics:
    timestamp: str
    prompt_tokens: int
    response_tokens: int
    response_time_ms: int
    quality_score: float  # 0-1
    iteration_count: int
    context_used: List[str]
    pattern_applied: Optional[str] = None
    success_indicators: List[str] = None

class MetricsCollector:
    def __init__(self, storage_path: Path = Path("evidence/metrics/data")):
        self.storage_path = storage_path
        self.storage_path.mkdir(exist_ok=True)
        
    def capture_interaction(self, metrics: InteractionMetrics) -> str:
        """Captura uma interação e retorna hash único"""
        interaction_id = hashlib.md5(
            f"{metrics.timestamp}{metrics.prompt_tokens}".encode()
        ).hexdigest()[:8]
        
        file_path = self.storage_path / f"{interaction_id}.json"
        with open(file_path, 'w') as f:
            json.dump(metrics.__dict__, f, indent=2, ensure_ascii=False)
            
        return interaction_id
    
    def generate_report(self, days: int = 7) -> Dict:
        """Gera relatório de métricas do período"""
        interactions = []
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        for file in self.storage_path.glob("*.json"):
            with open(file) as f:
                data = json.load(f)
                if datetime.datetime.fromisoformat(data['timestamp']) > cutoff_date:
                    interactions.append(data)
        
        if not interactions:
            return {"error": "No interactions found"}
            
        return {
            "period_days": days,
            "total_interactions": len(interactions),
            "avg_quality_score": sum(i['quality_score'] for i in interactions) / len(interactions),
            "avg_response_time": sum(i['response_time_ms'] for i in interactions) / len(interactions),
            "avg_iterations": sum(i['iteration_count'] for i in interactions) / len(interactions),
            "top_patterns": self._extract_top_patterns(interactions),
            "quality_distribution": self._quality_distribution(interactions),
            "recommendations": self._generate_recommendations(interactions)
        }
    
    def _extract_top_patterns(self, interactions: List[Dict]) -> List[str]:
        patterns = [i.get('pattern_applied') for i in interactions if i.get('pattern_applied')]
        return list(set(patterns))[:5] if patterns else []
    
    def _quality_distribution(self, interactions: List[Dict]) -> Dict[str, int]:
        distribution = {"high": 0, "medium": 0, "low": 0}
        for i in interactions:
            score = i['quality_score']
            if score >= 0.8: distribution["high"] += 1
            elif score >= 0.5: distribution["medium"] += 1
            else: distribution["low"] += 1
        return distribution
    
    def _generate_recommendations(self, interactions: List[Dict]) -> List[str]:
        recommendations = []
        
        avg_quality = sum(i['quality_score'] for i in interactions) / len(interactions)
        if avg_quality < 0.7:
            recommendations.append("Consider reviewing prompt composition strategy")
            
        avg_iterations = sum(i['iteration_count'] for i in interactions) / len(interactions)
        if avg_iterations > 2:
            recommendations.append("High iteration count suggests need for clearer initial prompts")
            
        return recommendations

# Exemplo de uso
if __name__ == "__main__":
    collector = MetricsCollector()
    
    # Simula captura de interação
    metrics = InteractionMetrics(
        timestamp=datetime.datetime.now().isoformat(),
        prompt_tokens=150,
        response_tokens=280,
        response_time_ms=1200,
        quality_score=0.85,
        iteration_count=1,
        context_used=["anderson-skill", "cognitive-workflows"],
        pattern_applied="chain",
        success_indicators=["task_completed", "no_followup_needed"]
    )
    
    interaction_id = collector.capture_interaction(metrics)
    print(f"Interaction captured: {interaction_id}")
    
    # Gera relatório
    report = collector.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))