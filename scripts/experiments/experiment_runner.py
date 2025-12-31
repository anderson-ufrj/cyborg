#!/usr/bin/env python3
"""
A/B Testing Framework for Prompt Engineering
Executa experimentos controlados para otimização de prompts

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brazil
"""

import json
import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import random

@dataclass
class ExperimentVariant:
    id: str
    name: str
    prompt_template: str
    context_modifiers: List[str]
    expected_outcome: str
    success_criteria: List[str]

@dataclass
class Experiment:
    id: str
    name: str
    hypothesis: str
    variants: List[ExperimentVariant]
    control_variant: str
    metrics_to_track: List[str]
    sample_size: int
    status: str = "draft"  # draft, running, completed
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()

class ExperimentRunner:
    def __init__(self, base_path: Path = Path("experiments")):
        self.base_path = base_path
        self.hypothesis_path = base_path / "hypothesis"
        self.results_path = base_path / "results"
        self.hypothesis_path.mkdir(exist_ok=True)
        self.results_path.mkdir(exist_ok=True)
        
    def create_experiment(self, experiment: Experiment) -> str:
        """Cria novo experimento"""
        exp_file = self.hypothesis_path / f"{experiment.id}.json"
        with open(exp_file, 'w') as f:
            json.dump(asdict(experiment), f, indent=2, ensure_ascii=False)
        return experiment.id
    
    def run_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Executa experimento e coleta resultados"""
        exp_file = self.hypothesis_path / f"{experiment_id}.json"
        if not exp_file.exists():
            return {"error": "Experiment not found"}
            
        with open(exp_file) as f:
            experiment = json.load(f)
            
        # Simula execução (em produção, integraria com sistema real)
        results = {
            "experiment_id": experiment_id,
            "started_at": datetime.datetime.now().isoformat(),
            "completed_at": None,
            "variant_results": {},
            "statistical_significance": None,
            "winner": None,
            "confidence_level": None
        }
        
        # Coleta resultados para cada variante
        for variant in experiment["variants"]:
            results["variant_results"][variant["id"]] = self._simulate_variant_results(
                variant, experiment["sample_size"]
            )
        
        # Análise estatística
        analysis = self._statistical_analysis(results["variant_results"])
        results.update(analysis)
        results["completed_at"] = datetime.datetime.now().isoformat()
        
        # Salva resultados
        result_file = self.results_path / f"{experiment_id}_results.json"
        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        return results
    
    def _simulate_variant_results(self, variant: Dict, sample_size: int) -> Dict:
        """Simula resultados para uma variante (mock para desenvolvimento)"""
        # Em produção, isso integraria com métricas reais
        return {
            "variant_id": variant["id"],
            "total_interactions": sample_size,
            "success_rate": random.uniform(0.6, 0.95),
            "avg_quality_score": random.uniform(0.7, 0.95),
            "avg_response_time": random.randint(800, 2000),
            "iteration_count": random.randint(1, 3),
            "user_satisfaction": random.uniform(0.7, 0.98),
            "completion_rate": random.uniform(0.8, 0.99)
        }
    
    def _statistical_analysis(self, variant_results: Dict) -> Dict:
        """Análise estatística simples para determinar vencedor"""
        if len(variant_results) < 2:
            return {"error": "Need at least 2 variants for analysis"}
            
        # Calcula scores ponderados
        scores = {}
        for variant_id, results in variant_results.items():
            score = (
                results["success_rate"] * 0.3 +
                results["avg_quality_score"] * 0.3 +
                results["user_satisfaction"] * 0.2 +
                results["completion_rate"] * 0.2
            )
            scores[variant_id] = score
        
        # Determina vencedor
        winner = max(scores, key=scores.get)
        best_score = scores[winner]
        
        # Calcula confiança (simplificado)
        second_best = sorted(scores.values(), reverse=True)[1]
        confidence = min((best_score - second_best) / best_score, 0.95)
        
        return {
            "winner": winner,
            "winner_score": best_score,
            "confidence_level": confidence,
            "statistical_significance": confidence > 0.8,
            "all_scores": scores
        }
    
    def generate_experiment_report(self, experiment_id: str) -> str:
        """Gera relatório formatado do experimento"""
        result_file = self.results_path / f"{experiment_id}_results.json"
        if not result_file.exists():
            return "Experiment results not found"
            
        with open(result_file) as f:
            results = json.load(f)
            
        # Carrega detalhes do experimento
        exp_file = self.hypothesis_path / f"{experiment_id}.json"
        with open(exp_file) as f:
            experiment = json.load(f)
            
        report = f"""
# Experiment Report: {experiment['name']}

## Hypothesis
{experiment['hypothesis']}

## Results Summary
- **Winner:** {results.get('winner', 'Undetermined')}
- **Confidence Level:** {(results.get('confidence_level') or 0):.2%}
- **Statistical Significance:** {'Yes' if results.get('statistical_significance') else 'No'}

## Variant Performance
"""
        
        for variant_id, variant_data in results['variant_results'].items():
            variant_name = next(v['name'] for v in experiment['variants'] if v['id'] == variant_id)
            report += f"""
### {variant_name}
- Success Rate: {variant_data['success_rate']:.2%}
- Quality Score: {variant_data['avg_quality_score']:.2f}
- User Satisfaction: {variant_data['user_satisfaction']:.2%}
- Completion Rate: {variant_data['completion_rate']:.2%}
"""
        
        report += f"""
## Conclusion
{'Recommend implementing winner' if results.get('statistical_significance') else 'Results inconclusive - consider larger sample size'}

Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report

# Exemplos de experimentos
if __name__ == "__main__":
    runner = ExperimentRunner()
    
    # Experimento 1: Comparação de estilos de contexto
    exp1 = Experiment(
        id="ctx-style-001",
        name="Context Style Comparison",
        hypothesis="Adding specific examples to context will improve response quality by 15%",
        variants=[
            ExperimentVariant(
                id="v1-generic",
                name="Generic Context",
                prompt_template="You are a helpful AI assistant...",
                context_modifiers=[],
                expected_outcome="Baseline performance",
                success_criteria=["quality_score > 0.7", "iteration_count < 2"]
            ),
            ExperimentVariant(
                id="v2-specific",
                name="Specific Examples",
                prompt_template="You are a helpful AI assistant. Here are specific examples of good responses...",
                context_modifiers=["include_examples", "domain_specific"],
                expected_outcome="Improved quality",
                success_criteria=["quality_score > 0.8", "iteration_count < 2"]
            )
        ],
        control_variant="v1-generic",
        metrics_to_track=["quality_score", "response_time", "iteration_count", "user_satisfaction"],
        sample_size=100
    )
    
    experiment_id = runner.create_experiment(exp1)
    print(f"Created experiment: {experiment_id}")
    
    # Executa experimento
    results = runner.run_experiment(experiment_id)
    print(f"Experiment completed. Winner: {results.get('winner')}")
    
    # Gera relatório
    report = runner.generate_experiment_report(experiment_id)
    print(report)