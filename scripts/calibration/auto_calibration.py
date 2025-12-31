#!/usr/bin/env python3
"""
Auto-Calibration System for Prompt Engineering
Usa machine learning para sugerir otimizações baseadas em padrões históricos

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brazil
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
import joblib

@dataclass
class CalibrationPattern:
    context_type: str
    prompt_characteristics: Dict[str, float]
    success_metrics: Dict[str, float]
    recommended_adjustments: List[str]
    confidence: float

class AutoCalibrationEngine:
    def __init__(self, data_path: Path = Path("evidence/metrics/data")):
        self.data_path = data_path
        self.model_path = Path("evidence/models")
        self.model_path.mkdir(exist_ok=True)
        self.vectorizer = None
        self.success_predictor = None
        self.pattern_clusterer = None
        
    def train_models(self, interactions: List[Dict]) -> Dict[str, float]:
        """Treina modelos de predição com dados históricos"""
        if len(interactions) < 50:
            return {"error": "Need at least 50 interactions for training"}
            
        # Prepara features
        X, y_success, y_quality = self._extract_features(interactions)
        
        # Treina preditor de sucesso
        self.success_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.success_predictor.fit(X, y_success)
        
        # Treina clusterizador de padrões
        self.pattern_clusterer = KMeans(n_clusters=5, random_state=42)
        clusters = self.pattern_clusterer.fit_predict(X)
        
        # Salva modelos
        joblib.dump(self.success_predictor, self.model_path / "success_predictor.pkl")
        joblib.dump(self.pattern_clusterer, self.model_path / "pattern_clusterer.pkl")
        joblib.dump(self.vectorizer, self.model_path / "vectorizer.pkl")
        
        # Avalia performance
        accuracy = self.success_predictor.score(X, y_success)
        
        return {
            "training_completed": True,
            "model_accuracy": accuracy,
            "clusters_found": len(set(clusters)),
            "samples_used": len(interactions)
        }
    
    def _extract_features(self, interactions: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Extrai features vetoriais das interações"""
        # Texto combinado para análise
        texts = []
        for interaction in interactions:
            context_text = " ".join(interaction.get('context_used', []))
            pattern_text = interaction.get('pattern_applied', '')
            texts.append(f"{context_text} {pattern_text}")
        
        # Vetorização TF-IDF
        self.vectorizer = TfidfVectorizer(max_features=50, stop_words=None)
        text_features = self.vectorizer.fit_transform(texts).toarray()
        
        # Features numéricas
        numeric_features = []
        for interaction in interactions:
            features = [
                interaction.get('prompt_tokens', 0) / 1000,  # normalizado
                interaction.get('response_tokens', 0) / 1000,
                interaction.get('response_time_ms', 0) / 1000,
                interaction.get('iteration_count', 1),
            ]
            numeric_features.append(features)
        
        # Combina features
        X = np.hstack([text_features, numeric_features])
        
        # Targets
        y_success = np.array([
            1 if i.get('quality_score', 0) > 0.7 else 0 
            for i in interactions
        ])
        y_quality = np.array([i.get('quality_score', 0) for i in interactions])
        
        return X, y_success, y_quality
    
    def predict_optimal_config(self, context: Dict) -> CalibrationPattern:
        """Prediz configuração ótima para novo contexto"""
        if not self._models_loaded():
            self._load_models()
            
        # Extrai features do contexto
        features = self._context_to_features(context)
        
        # Prediz probabilidade de sucesso
        success_prob = self.success_predictor.predict_proba(features)[0][1]
        
        # Identifica cluster mais próximo
        cluster = self.pattern_clusterer.predict(features)[0]
        
        # Gera recomendações baseadas no cluster
        recommendations = self._generate_cluster_recommendations(cluster, success_prob)
        
        return CalibrationPattern(
            context_type=context.get('type', 'unknown'),
            prompt_characteristics=self._analyze_prompt_characteristics(context),
            success_metrics={"predicted_success": success_prob},
            recommended_adjustments=recommendations,
            confidence=success_prob
        )
    
    def _models_loaded(self) -> bool:
        """Verifica se modelos estão carregados"""
        return all([
            self.success_predictor is not None,
            self.pattern_clusterer is not None,
            self.vectorizer is not None
        ])
    
    def _load_models(self):
        """Carrega modelos salvos"""
        try:
            self.success_predictor = joblib.load(self.model_path / "success_predictor.pkl")
            self.pattern_clusterer = joblib.load(self.model_path / "pattern_clusterer.pkl")
            self.vectorizer = joblib.load(self.model_path / "vectorizer.pkl")
        except FileNotFoundError:
            # Modelos não treinados ainda
            pass
    
    def _context_to_features(self, context: Dict) -> np.ndarray:
        """Converte contexto em features vetoriais"""
        # Texto do contexto
        context_text = " ".join(context.get('context_elements', []))
        pattern_text = context.get('pattern', '')
        full_text = f"{context_text} {pattern_text}"
        
        # Vetoriza texto
        text_features = self.vectorizer.transform([full_text]).toarray()[0]
        
        # Features numéricas
        numeric_features = np.array([
            context.get('prompt_tokens', 150) / 1000,
            context.get('expected_tokens', 200) / 1000,
            context.get('complexity', 1),
            context.get('urgency', 1)
        ])
        
        return np.hstack([text_features, numeric_features]).reshape(1, -1)
    
    def _analyze_prompt_characteristics(self, context: Dict) -> Dict[str, float]:
        """Analisa características do prompt"""
        return {
            "complexity": context.get('complexity', 1),
            "specificity": context.get('specificity', 0.5),
            "domain_focus": context.get('domain_focus', 0.3),
            "example_density": context.get('example_density', 0.1)
        }
    
    def _generate_cluster_recommendations(self, cluster: int, success_prob: float) -> List[str]:
        """Gera recomendações baseadas no cluster"""
        cluster_recommendations = {
            0: ["Add more specific examples", "Reduce prompt length"],
            1: ["Include domain-specific terminology", "Add success criteria"],
            2: ["Use parallel analysis patterns", "Include multiple perspectives"],
            3: ["Add step-by-step instructions", "Include validation checkpoints"],
            4: ["Reduce complexity", "Use simpler language"]
        }
        
        recommendations = cluster_recommendations.get(cluster, ["General optimization needed"])
        
        # Adiciona recomendações baseadas na probabilidade de sucesso
        if success_prob < 0.6:
            recommendations.append("Consider major prompt restructuring")
        elif success_prob < 0.8:
            recommendations.append("Minor adjustments recommended")
        else:
            recommendations.append("Current approach looks good")
            
        return recommendations
    
    def suggest_context_improvements(self, current_context: str, target_outcome: str) -> List[str]:
        """Sugere melhorias específicas no contexto"""
        suggestions = []
        
        # Análise de palavras-chave
        if "debug" in current_context.lower():
            suggestions.extend([
                "Add specific error messages",
                "Include stack traces if available",
                "Specify expected vs actual behavior"
            ])
        
        if "design" in current_context.lower():
            suggestions.extend([
                "Include stakeholder constraints",
                "Add success metrics",
                "Specify technical requirements"
            ])
        
        if len(current_context.split()) < 50:
            suggestions.append("Consider adding more context details")
        
        if len(current_context.split()) > 500:
            suggestions.append("Consider condensing context for clarity")
            
        # Análise de outcome
        if "quality" in target_outcome.lower():
            suggestions.append("Add quality criteria and examples")
        
        if "speed" in target_outcome.lower():
            suggestions.append("Include time constraints and priorities")
        
        return suggestions

# Exemplo de uso
if __name__ == "__main__":
    engine = AutoCalibrationEngine()
    
    # Dados de exemplo para treino
    sample_interactions = [
        {
            "context_used": ["anderson-skill", "debugging"],
            "pattern_applied": "chain",
            "prompt_tokens": 120,
            "response_tokens": 250,
            "response_time_ms": 1100,
            "quality_score": 0.85,
            "iteration_count": 1
        },
        {
            "context_used": ["anderson-skill", "brainstorming"],
            "pattern_applied": "parallel",
            "prompt_tokens": 200,
            "response_tokens": 400,
            "response_time_ms": 1800,
            "quality_score": 0.92,
            "iteration_count": 2
        }
    ]
    
    # Treina modelos
    training_result = engine.train_models(sample_interactions)
    print(f"Training completed: {training_result}")
    
    # Testa predição
    context = {
        "type": "debugging",
        "context_elements": ["anderson-skill", "debugging", "urgent"],
        "pattern": "chain",
        "prompt_tokens": 150,
        "urgency": 3
    }
    
    prediction = engine.predict_optimal_config(context)
    print(f"Predicted success: {prediction.confidence:.2%}")
    print(f"Recommendations: {prediction.recommended_adjustments}")
    
    # Sugestões de melhoria
    improvements = engine.suggest_context_improvements(
        "Debug this Python error",
        "Find root cause quickly"
    )
    print(f"Suggested improvements: {improvements}")