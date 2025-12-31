#!/usr/bin/env python3
"""
Integration Pipeline for Prompt Engineering Lab
Author: Anderson Henrique da Silva
Location: Minas Gerais, Brazil

Complete pipeline that connects all components with real interaction data.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.metrics.interaction_analyzer import MetricsCollector, InteractionMetrics
from src.experiments.experiment_runner import ExperimentRunner, Experiment, ExperimentVariant
from src.calibration.auto_calibration import AutoCalibrationEngine
from src.calibration.dashboard import PerformanceDashboard
from src.versioning.version_manager import VersionManager

class IntegrationPipeline:
    """Main integration pipeline for the prompt engineering system"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.experiment_runner = ExperimentRunner()
        self.calibration_engine = AutoCalibrationEngine()
        self.dashboard = PerformanceDashboard()
        self.version_manager = VersionManager()
        
        # Configuration
        self.min_interactions_for_training = 50
        self.min_experiment_duration_days = 7
        self.auto_calibration_threshold = 0.7
        
    def collect_interaction(self, 
                          prompt_tokens: int,
                          response_tokens: int, 
                          response_time_ms: int,
                          quality_score: float,
                          iteration_count: int,
                          context_used: List[str],
                          pattern_applied: Optional[str] = None,
                          success_indicators: Optional[List[str]] = None) -> str:
        """Collect a single interaction and return interaction ID"""
        
        if success_indicators is None:
            success_indicators = self._determine_success_indicators(quality_score)
        
        metrics = InteractionMetrics(
            timestamp=datetime.now().isoformat(),
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            response_time_ms=response_time_ms,
            quality_score=quality_score,
            iteration_count=iteration_count,
            context_used=context_used,
            pattern_applied=pattern_applied,
            success_indicators=success_indicators
        )
        
        return self.metrics_collector.capture_interaction(metrics)
    
    def _determine_success_indicators(self, quality_score: float) -> List[str]:
        """Determine success indicators based on quality score"""
        if quality_score >= 0.8:
            return ["task_completed", "no_followup_needed", "user_satisfied"]
        elif quality_score >= 0.6:
            return ["task_completed", "minor_followup_needed"]
        else:
            return ["task_incomplete", "major_revisions_needed"]
    
    def run_health_check(self) -> Dict:
        """Run system health check"""
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "overall_status": "healthy",
            "recommendations": []
        }
        
        # Check metrics collection
        try:
            report = self.metrics_collector.generate_report(days=30)
            if 'error' not in report:
                health_status["components"]["metrics_collection"] = {
                    "status": "operational",
                    "total_interactions": report.get('total_interactions', 0),
                    "avg_quality": report.get('avg_quality_score', 0)
                }
                
                if report.get('avg_quality_score', 0) < 0.7:
                    health_status["recommendations"].append("Quality scores below 70% - review prompt strategy")
            else:
                health_status["components"]["metrics_collection"] = {
                    "status": "no_data",
                    "message": report['error']
                }
        except Exception as e:
            health_status["components"]["metrics_collection"] = {
                "status": "error",
                "message": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check experiment system
        try:
            # Try to create a test experiment
            test_exp = Experiment(
                id="health-check",
                name="Health Check Test",
                hypothesis="System health validation",
                variants=[],
                control_variant="",
                metrics_to_track=[],
                sample_size=1
            )
            self.experiment_runner.create_experiment(test_exp)
            
            health_status["components"]["experiment_system"] = {
                "status": "operational"
            }
        except Exception as e:
            health_status["components"]["experiment_system"] = {
                "status": "error",
                "message": str(e)
            }
            health_status["overall_status"] = "degraded"
        
        # Check calibration system
        try:
            # Check if models exist
            model_path = Path("evidence/models/success_predictor.pkl")
            if model_path.exists():
                health_status["components"]["calibration_system"] = {
                    "status": "trained",
                    "models_available": True
                }
            else:
                health_status["components"]["calibration_system"] = {
                    "status": "untrained",
                    "models_available": False
                }
                health_status["recommendations"].append("Train calibration models for better predictions")
        except Exception as e:
            health_status["components"]["calibration_system"] = {
                "status": "error",
                "message": str(e)
            }
        
        # Check data freshness
        try:
            recent_report = self.metrics_collector.generate_report(days=7)
            if 'error' not in recent_report and recent_report.get('total_interactions', 0) > 0:
                health_status["components"]["data_freshness"] = {
                    "status": "current",
                    "recent_interactions": recent_report['total_interactions']
                }
            else:
                health_status["components"]["data_freshness"] = {
                    "status": "stale",
                    "message": "No recent interactions"
                }
                health_status["recommendations"].append("Collect more recent interaction data")
        except Exception as e:
            health_status["components"]["data_freshness"] = {
                "status": "error",
                "message": str(e)
            }
        
        return health_status
    
    def train_calibration_models(self, force_retrain: bool = False) -> Dict:
        """Train calibration models if sufficient data is available"""
        
        print("🤖 Training calibration models...")
        
        # Check current data volume
        report = self.metrics_collector.generate_report(days=90)  # Use 90 days for more data
        
        if 'error' in report:
            return {
                "status": "failed",
                "error": f"No data available: {report['error']}"
            }
        
        total_interactions = report.get('total_interactions', 0)
        
        if total_interactions < self.min_interactions_for_training:
            return {
                "status": "insufficient_data",
                "required": self.min_interactions_for_training,
                "available": total_interactions,
                "message": "Collect more interactions before training"
            }
        
        # Load interaction data for training
        interaction_files = list(Path("evidence/metrics/data").glob("*.json"))
        interactions = []
        
        for file in interaction_files:
            try:
                with open(file) as f:
                    data = json.load(f)
                    interactions.append(data)
            except (json.JSONDecodeError, KeyError):
                continue
        
        if len(interactions) < 10:  # Minimum for basic training
            return {
                "status": "insufficient_data",
                "required": 10,
                "available": len(interactions),
                "message": "Need at least 10 valid interactions"
            }
        
        # Train models
        try:
            training_result = self.calibration_engine.train_models(interactions)
            
            if 'error' in training_result:
                return {
                    "status": "training_failed",
                    "error": training_result['error']
                }
            
            return {
                "status": "success",
                "model_accuracy": training_result.get('model_accuracy', 0),
                "clusters_found": training_result.get('clusters_found', 0),
                "samples_used": training_result.get('samples_used', 0),
                "message": "Models trained successfully"
            }
            
        except Exception as e:
            return {
                "status": "training_error",
                "error": str(e)
            }
    
    def suggest_prompt_optimizations(self, context: Dict) -> Dict:
        """Suggest optimizations based on calibration models"""
        
        try:
            prediction = self.calibration_engine.predict_optimal_config(context)
            
            suggestions = self.calibration_engine.suggest_context_improvements(
                " ".join(context.get('context_elements', [])),
                context.get('target_outcome', 'improve quality')
            )
            
            return {
                "status": "success",
                "predicted_success_rate": prediction.confidence,
                "recommendations": prediction.recommended_adjustments,
                "context_suggestions": suggestions,
                "prompt_characteristics": prediction.prompt_characteristics,
                "confidence": prediction.confidence
            }
            
        except Exception as e:
            return {
                "status": "prediction_failed",
                "error": str(e),
                "fallback_recommendations": [
                    "Add specific examples to context",
                    "Include success criteria",
                    "Specify constraints and requirements"
                ]
            }
    
    def run_experiment(self, experiment_config: Dict) -> Dict:
        """Run an experiment with the given configuration"""
        
        try:
            # Create experiment
            experiment = Experiment(
                id=experiment_config["id"],
                name=experiment_config["name"],
                hypothesis=experiment_config["hypothesis"],
                variants=[
                    ExperimentVariant(**variant) 
                    for variant in experiment_config["variants"]
                ],
                control_variant=experiment_config["control_variant"],
                metrics_to_track=experiment_config["metrics_to_track"],
                sample_size=experiment_config["sample_size"]
            )
            
            # Create and run experiment
            self.experiment_runner.create_experiment(experiment)
            results = self.experiment_runner.run_experiment(experiment.id)
            
            # Generate report
            report = self.experiment_runner.generate_experiment_report(experiment.id)
            
            return {
                "status": "success",
                "experiment_id": experiment.id,
                "results": results,
                "report": report,
                "winner": results.get('winner'),
                "confidence": results.get('confidence_level'),
                "significant": results.get('statistical_significance')
            }
            
        except Exception as e:
            return {
                "status": "experiment_failed",
                "error": str(e)
            }
    
    def generate_performance_report(self, days: int = 30) -> Dict:
        """Generate comprehensive performance report"""
        
        try:
            report = self.dashboard.generate_comprehensive_report(days)
            
            if 'error' in report:
                return {
                    "status": "report_failed",
                    "error": report['error']
                }
            
            # Add additional insights
            insights = self._generate_insights(report)
            
            return {
                "status": "success",
                "report": report,
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "report_error",
                "error": str(e)
            }
    
    def _generate_insights(self, report: Dict) -> List[str]:
        """Generate additional insights from the report"""
        insights = []
        
        # Quality insights
        avg_quality = report.get('avg_quality_score', 0)
        if avg_quality > 0.9:
            insights.append("Excellent quality scores - system performing optimally")
        elif avg_quality > 0.8:
            insights.append("Good quality scores - minor optimizations possible")
        elif avg_quality > 0.7:
            insights.append("Quality scores acceptable - consider prompt refinements")
        else:
            insights.append("Quality scores below target - significant improvements needed")
        
        # Trend insights
        if 'trend_analysis' in report and 'quality_trend' in report['trend_analysis']:
            trend = report['trend_analysis']['quality_trend']
            if trend['direction'] == 'improving':
                insights.append("Quality trend is positive - current strategies working")
            elif trend['direction'] == 'declining':
                insights.append("Quality trend declining - investigate recent changes")
        
        # Pattern insights
        if 'pattern_analysis' in report and 'most_used' in report['pattern_analysis']:
            most_used = report['pattern_analysis']['most_used']
            best_performing = report['pattern_analysis'].get('best_performing')
            
            if most_used and best_performing and most_used != best_performing:
                insights.append(f"Most used pattern ({most_used}) differs from best performing ({best_performing})")
        
        # Response time insights
        avg_response_time = report.get('avg_response_time', 0)
        if avg_response_time > 2000:
            insights.append("Response times above 2s - consider prompt optimization")
        elif avg_response_time < 1000:
            insights.append("Fast response times - excellent performance")
        
        return insights
    
    def auto_optimize(self, target_metric: str = "quality_score") -> Dict:
        """Automatically optimize based on collected data"""
        
        print(f"🎯 Auto-optimizing for {target_metric}...")
        
        # Get current performance
        report = self.generate_performance_report(30)
        
        if report['status'] != 'success':
            return {
                "status": "optimization_failed",
                "error": "Could not generate performance report",
                "report_error": report.get('error')
            }
        
        current_performance = report['report'].get(f'avg_{target_metric}', 0)
        
        # Train models if needed
        training_result = self.train_calibration_models()
        if training_result['status'] != 'success':
            return {
                "status": "optimization_failed",
                "error": "Could not train calibration models",
                "training_error": training_result.get('error')
            }
        
        # Suggest optimizations for common contexts
        contexts_to_optimize = [
            {
                "type": "debugging",
                "context_elements": ["anderson-skill", "debugging"],
                "target_outcome": f"improve {target_metric}"
            },
            {
                "type": "brainstorming", 
                "context_elements": ["anderson-skill", "brainstorming"],
                "target_outcome": f"improve {target_metric}"
            },
            {
                "type": "code_review",
                "context_elements": ["anderson-skill", "code-review"],
                "target_outcome": f"improve {target_metric}"
            }
        ]
        
        optimizations = []
        for context in contexts_to_optimize:
            suggestions = self.suggest_prompt_optimizations(context)
            if suggestions['status'] == 'success':
                optimizations.append({
                    "context": context['type'],
                    "suggestions": suggestions['recommendations'],
                    "predicted_improvement": suggestions['predicted_success_rate']
                })
        
        return {
            "status": "optimization_complete",
            "current_performance": current_performance,
            "optimizations": optimizations,
            "recommendations": self._generate_optimization_recommendations(optimizations)
        }
    
    def _generate_optimization_recommendations(self, optimizations: List[Dict]) -> List[str]:
        """Generate actionable recommendations from optimizations"""
        recommendations = []
        
        for opt in optimizations:
            if opt['predicted_improvement'] > self.auto_calibration_threshold:
                recommendations.append(
                    f"Implement suggestions for {opt['context']} context "
                    f"(predicted {opt['predicted_improvement']:.1%} success rate)"
                )
        
        if not recommendations:
            recommendations.append("Current performance is stable - monitor for trends")
            recommendations.append("Consider A/B testing new approaches")
        
        return recommendations

def main():
    """Main function for command-line usage"""
    
    parser = argparse.ArgumentParser(
        description="Prompt Engineering Lab Integration Pipeline",
        epilog="Author: Anderson Henrique da Silva - Minas Gerais, Brazil"
    )
    
    parser.add_argument(
        "action",
        choices=["health", "collect", "experiment", "train", "optimize", "report"],
        help="Action to perform"
    )
    
    parser.add_argument(
        "--days", 
        type=int, 
        default=30,
        help="Number of days for analysis (default: 30)"
    )
    
    parser.add_argument(
        "--target",
        choices=["quality_score", "response_time", "iteration_count"],
        default="quality_score",
        help="Target metric for optimization (default: quality_score)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    pipeline = IntegrationPipeline()
    
    if args.action == "health":
        result = pipeline.run_health_check()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "collect":
        if args.interactive:
            print("🔄 Interactive interaction collection mode")
            print("Enter interaction details (or 'quit' to stop):")
            
            while True:
                try:
                    prompt_tokens = input("Prompt tokens: ")
                    if prompt_tokens.lower() == 'quit':
                        break
                    
                    response_tokens = input("Response tokens: ")
                    response_time = input("Response time (ms): ")
                    quality = float(input("Quality score (0-1): "))
                    iterations = int(input("Iteration count: "))
                    context = input("Context (comma-separated): ").split(",")
                    
                    interaction_id = pipeline.collect_interaction(
                        int(prompt_tokens),
                        int(response_tokens),
                        int(response_time),
                        quality,
                        iterations,
                        [c.strip() for c in context]
                    )
                    
                    print(f"✅ Collected interaction: {interaction_id}")
                    
                except (ValueError, KeyboardInterrupt):
                    print("⚠️  Invalid input, try again")
                    continue
        else:
            # Collect sample data
            from tests.test_integration_real_data import collect_real_interactions
            collect_real_interactions(10)
    
    elif args.action == "experiment":
        # Run predefined experiment
        experiment_config = {
            "id": f"auto-exp-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "name": "Context Optimization Experiment",
            "hypothesis": "Optimized context selection improves overall performance",
            "variants": [
                {
                    "id": "standard",
                    "name": "Standard Context",
                    "prompt_template": "Full personal context with all skills",
                    "context_modifiers": ["complete_context", "all_skills"],
                    "expected_outcome": "Baseline performance",
                    "success_criteria": ["quality_score > 0.75"]
                },
                {
                    "id": "optimized",
                    "name": "Optimized Context",
                    "prompt_template": "Context selected based on task type",
                    "context_modifiers": ["task_specific", "minimal_relevant"],
                    "expected_outcome": "Improved efficiency",
                    "success_criteria": ["quality_score > 0.75", "response_time < 1500"]
                }
            ],
            "control_variant": "standard",
            "metrics_to_track": ["quality_score", "response_time", "iteration_count"],
            "sample_size": 30
        }
        
        result = pipeline.run_experiment(experiment_config)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "train":
        result = pipeline.train_calibration_models()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "optimize":
        result = pipeline.auto_optimize(args.target)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "report":
        result = pipeline.generate_performance_report(args.days)
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()