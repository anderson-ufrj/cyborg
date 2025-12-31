#!/usr/bin/env python3
"""
Performance Dashboard for Prompt Engineering System
Visualiza métricas e tendências do sistema

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brazil
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
import pandas as pd

class PerformanceDashboard:
    def __init__(self, data_path: Path = Path("evidence/metrics/data")):
        self.data_path = data_path
        self.reports_path = Path("evidence/metrics/reports")
        self.reports_path.mkdir(exist_ok=True)
        
        # Configura estilo dos gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def load_interaction_data(self, days: int = 30) -> pd.DataFrame:
        """Carrega dados de interações do período"""
        interactions = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file in self.data_path.glob("*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    interaction_date = datetime.fromisoformat(data['timestamp'])
                    if interaction_date > cutoff_date:
                        interactions.append(data)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
                
        return pd.DataFrame(interactions)
    
    def generate_comprehensive_report(self, days: int = 30) -> Dict:
        """Gera relatório abrangente de performance"""
        df = self.load_interaction_data(days)
        
        if df.empty:
            return {"error": "No data available for the specified period"}
            
        # Calcula métricas principais
        metrics = {
            "period": f"Last {days} days",
            "total_interactions": len(df),
            "avg_quality_score": df['quality_score'].mean(),
            "avg_response_time": df['response_time_ms'].mean(),
            "avg_iterations": df['iteration_count'].mean(),
            "success_rate": (df['quality_score'] > 0.7).mean(),
            "trend_analysis": self._calculate_trends(df, days),
            "pattern_analysis": self._analyze_patterns(df),
            "context_performance": self._analyze_context_performance(df),
            "recommendations": self._generate_recommendations(df)
        }
        
        # Gera visualizações
        self._create_visualizations(df, days)
        
        # Salva relatório
        self._save_report(metrics, days)
        
        return metrics
    
    def _calculate_trends(self, df: pd.DataFrame, days: int) -> Dict:
        """Calcula tendências ao longo do tempo"""
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_metrics = df.groupby('date').agg({
            'quality_score': 'mean',
            'response_time_ms': 'mean',
            'iteration_count': 'mean'
        }).reset_index()
        
        # Calcula tendências lineares
        from scipy import stats
        
        if len(daily_metrics) < 2:
            return {"insufficient_data": True}
            
        x = range(len(daily_metrics))
        
        quality_trend = stats.linregress(x, daily_metrics['quality_score'])
        response_trend = stats.linregress(x, daily_metrics['response_time_ms'])
        iteration_trend = stats.linregress(x, daily_metrics['iteration_count'])
        
        return {
            "quality_trend": {
                "slope": quality_trend.slope,
                "r_squared": quality_trend.rvalue ** 2,
                "direction": "improving" if quality_trend.slope > 0 else "declining"
            },
            "response_time_trend": {
                "slope": response_trend.slope,
                "r_squared": response_trend.rvalue ** 2,
                "direction": "faster" if response_trend.slope < 0 else "slower"
            },
            "iteration_trend": {
                "slope": iteration_trend.slope,
                "r_squared": iteration_trend.rvalue ** 2,
                "direction": "fewer" if iteration_trend.slope < 0 else "more"
            }
        }
    
    def _analyze_patterns(self, df: pd.DataFrame) -> Dict:
        """Analisa padrões de uso e efetividade"""
        pattern_stats = {}
        
        if 'pattern_applied' in df.columns:
            pattern_counts = df['pattern_applied'].value_counts()
            pattern_quality = df.groupby('pattern_applied')['quality_score'].mean()
            
            pattern_stats = {
                "most_used": pattern_counts.index[0] if len(pattern_counts) > 0 else None,
                "best_performing": pattern_quality.idxmax() if len(pattern_quality) > 0 else None,
                "pattern_distribution": pattern_counts.to_dict(),
                "pattern_quality": pattern_quality.to_dict()
            }
            
        # Análise de contexto
        if 'context_used' in df.columns:
            all_contexts = []
            for contexts in df['context_used'].dropna():
                if isinstance(contexts, list):
                    all_contexts.extend(contexts)
                    
            context_counts = pd.Series(all_contexts).value_counts()
            pattern_stats["context_distribution"] = context_counts.to_dict()
            
        return pattern_stats
    
    def _analyze_context_performance(self, df: pd.DataFrame) -> Dict:
        """Analisa performance por tipo de contexto"""
        if 'context_used' not in df.columns:
            return {}
            
        context_performance = {}
        
        for idx, contexts in df['context_used'].dropna().items():
            if isinstance(contexts, list):
                quality = df.loc[idx, 'quality_score']
                for context in contexts:
                    if context not in context_performance:
                        context_performance[context] = []
                    context_performance[context].append(quality)
        
        # Calcula médias
        avg_performance = {
            context: np.mean(scores) 
            for context, scores in context_performance.items() 
            if len(scores) > 0
        }
        
        return avg_performance
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Gera recomendações baseadas nos dados"""
        recommendations = []
        
        # Análise de qualidade
        avg_quality = df['quality_score'].mean()
        if avg_quality < 0.7:
            recommendations.append("Quality scores are below 70% - review prompt composition strategy")
        elif avg_quality > 0.9:
            recommendations.append("Excellent quality scores - document successful patterns")
            
        # Análise de iterações
        avg_iterations = df['iteration_count'].mean()
        if avg_iterations > 2:
            recommendations.append("High iteration count suggests need for clearer initial prompts")
            
        # Análise de tempo de resposta
        avg_response_time = df['response_time_ms'].mean()
        if avg_response_time > 2000:
            recommendations.append("Response times above 2s - consider prompt optimization")
            
        # Análise de padrões
        if 'pattern_applied' in df.columns:
            pattern_quality = df.groupby('pattern_applied')['quality_score'].mean()
            low_performing = pattern_quality[pattern_quality < 0.7]
            if len(low_performing) > 0:
                patterns = ", ".join(low_performing.index)
                recommendations.append(f"Low-performing patterns detected: {patterns}")
                
        # Análise de tendências
        trends = self._calculate_trends(df, 30)
        if "quality_trend" in trends and trends["quality_trend"]["direction"] == "declining":
            recommendations.append("Quality trend is declining - investigate recent changes")
            
        # Recomendações padrão
        if len(recommendations) == 0:
            recommendations.extend([
                "System performance looks stable - consider A/B testing new patterns",
                "Review interaction examples for new calibration opportunities",
                "Monitor for seasonal/contextual performance variations"
            ])
            
        return recommendations
    
    def _create_visualizations(self, df: pd.DataFrame, days: int):
        """Cria visualizações dos dados"""
        # Prepara dados temporais
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        
        # Figura 1: Tendências ao longo do tempo
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Performance Dashboard - Last {days} Days', fontsize=16)
        
        # Qualidade ao longo do tempo
        daily_quality = df.groupby('date')['quality_score'].mean()
        axes[0, 0].plot(daily_quality.index, daily_quality.values, marker='o')
        axes[0, 0].set_title('Quality Score Trend')
        axes[0, 0].set_ylabel('Average Quality Score')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Tempo de resposta
        daily_response = df.groupby('date')['response_time_ms'].mean()
        axes[0, 1].plot(daily_response.index, daily_response.values, marker='o', color='orange')
        axes[0, 1].set_title('Response Time Trend')
        axes[0, 1].set_ylabel('Average Response Time (ms)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Distribuição de qualidade
        axes[1, 0].hist(df['quality_score'], bins=20, alpha=0.7, color='green')
        axes[1, 0].set_title('Quality Score Distribution')
        axes[1, 0].set_xlabel('Quality Score')
        axes[1, 0].set_ylabel('Frequency')
        
        # Padrões mais usados
        if 'pattern_applied' in df.columns:
            pattern_counts = df['pattern_applied'].value_counts().head(5)
            axes[1, 1].bar(range(len(pattern_counts)), pattern_counts.values)
            axes[1, 1].set_title('Most Used Patterns')
            axes[1, 1].set_xticks(range(len(pattern_counts)))
            axes[1, 1].set_xticklabels(pattern_counts.index, rotation=45)
            axes[1, 1].set_ylabel('Usage Count')
        else:
            axes[1, 1].text(0.5, 0.5, 'No Pattern Data Available', 
                          ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Pattern Usage')
        
        plt.tight_layout()
        
        # Salva figura
        fig_path = self.reports_path / f"dashboard_{days}days_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Figura 2: Análise de contexto
        if 'context_used' in df.columns:
            self._create_context_visualization(df)
    
    def _create_context_visualization(self, df: pd.DataFrame):
        """Cria visualização de performance por contexto"""
        # Analisa performance por contexto
        context_performance = self._analyze_context_performance(df)
        
        if context_performance:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            contexts = list(context_performance.keys())
            scores = list(context_performance.values())
            
            bars = ax.bar(contexts, scores, alpha=0.7)
            ax.set_title('Performance by Context Type')
            ax.set_ylabel('Average Quality Score')
            ax.set_xlabel('Context Type')
            
            # Coloriza barras baseado na performance
            for bar, score in zip(bars, scores):
                if score >= 0.8:
                    bar.set_color('green')
                elif score >= 0.6:
                    bar.set_color('orange')
                else:
                    bar.set_color('red')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Salva figura
            fig_path = self.reports_path / f"context_performance_{datetime.now().strftime('%Y%m%d')}.png"
            plt.savefig(fig_path, dpi=300, bbox_inches='tight')
            plt.close()
    
    def _save_report(self, metrics: Dict, days: int):
        """Salva relatório em formato JSON e Markdown"""
        # JSON
        json_path = self.reports_path / f"report_{days}days_{datetime.now().strftime('%Y%m%d')}.json"
        with open(json_path, 'w') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        # Markdown
        md_path = self.reports_path / f"report_{days}days_{datetime.now().strftime('%Y%m%d')}.md"
        with open(md_path, 'w') as f:
            f.write(self._format_markdown_report(metrics))
    
    def _format_markdown_report(self, metrics: Dict) -> str:
        """Formata relatório em Markdown"""
        report = f"""# Performance Report - {metrics['period']}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Metrics

- **Total Interactions:** {metrics['total_interactions']:,}
- **Average Quality Score:** {metrics['avg_quality_score']:.2f}
- **Average Response Time:** {metrics['avg_response_time']:.0f}ms
- **Average Iterations:** {metrics['avg_iterations']:.1f}
- **Success Rate:** {metrics['success_rate']:.1%}

## Trend Analysis
"""
        
        if "quality_trend" in metrics["trend_analysis"]:
            trend = metrics["trend_analysis"]["quality_trend"]
            report += f"""
- **Quality Trend:** {trend['direction']} (slope: {trend['slope']:.4f}, R²: {trend['r_squared']:.3f})
"""
        
        report += f"""
## Pattern Analysis
"""
        
        if "most_used" in metrics["pattern_analysis"]:
            patterns = metrics["pattern_analysis"]
            report += f"""
- **Most Used Pattern:** {patterns['most_used']}
- **Best Performing Pattern:** {patterns['best_performing']}
"""
        
        report += f"""
## Context Performance
"""
        
        for context, score in metrics["context_performance"].items():
            report += f"- **{context}:** {score:.2f}\n"
        
        report += f"""
## Recommendations
"""
        
        for rec in metrics["recommendations"]:
            report += f"- {rec}\n"
        
        return report

# Exemplo de uso
if __name__ == "__main__":
    dashboard = PerformanceDashboard()
    
    # Gera relatório completo
    report = dashboard.generate_comprehensive_report(30)
    
    if "error" not in report:
        print(f"Report generated successfully!")
        print(f"Total interactions: {report['total_interactions']}")
        print(f"Average quality: {report['avg_quality_score']:.2f}")
        print(f"Success rate: {report['success_rate']:.1%}")
        print(f"Recommendations: {len(report['recommendations'])}")
    else:
        print(f"Error: {report['error']}")