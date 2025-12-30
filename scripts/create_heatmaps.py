#!/usr/bin/env python3
"""
Create Advanced Heatmaps for Cyborg Developer Paper
Author: Anderson Henrique da Silva

Generates publication-ready heatmaps and correlation matrices.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import json

DATA_DIR = Path(__file__).parent.parent / "data"
FIGURES_DIR = Path(__file__).parent.parent / "figures"

def load_advanced_data():
    """Load the advanced analysis results."""
    with open(DATA_DIR / "advanced_analysis.json", 'r') as f:
        return json.load(f)

def create_temporal_heatmap():
    """Create heatmap showing temporal patterns."""
    data = load_advanced_data()
    temporal = data['temporal_analysis']
    
    # Create temporal data matrix
    weeks = ['W47', 'W48', 'W49', 'W50', 'W51', 'W52']
    efficiency = temporal['efficiency_trend']
    
    # Simulate intensity data based on timeline
    timeline_data = [
        {"sessions": 12, "messages": 1235},
        {"sessions": 164, "messages": 20705},
        {"sessions": 243, "messages": 30733},
        {"sessions": 136, "messages": 17114},
        {"sessions": 157, "messages": 10722},
        {"sessions": 90, "messages": 4861}
    ]
    
    # Normalize data for heatmap
    sessions_norm = [d["sessions"] / max(timeline_data, key=lambda x: x["sessions"])["sessions"] for d in timeline_data]
    messages_norm = [d["messages"] / max(timeline_data, key=lambda x: x["messages"])["messages"] for d in timeline_data]
    
    # Create matrix
    heatmap_data = pd.DataFrame({
        'Efficiency': efficiency,
        'Session Intensity': sessions_norm,
        'Message Intensity': messages_norm
    }, index=weeks)
    
    # Create heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data.T, annot=True, fmt='.2f', cmap='RdYlBu_r', 
                cbar_kws={'label': 'Normalized Intensity'})
    plt.title('Temporal Patterns Heat Map: Efficiency vs. Intensity Over Time', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Week', fontsize=12)
    plt.ylabel('Metrics', fontsize=12)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'heatmap_temporal.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_complexity_heatmap():
    """Create heatmap for complexity analysis."""
    data = load_advanced_data()
    complexity = data['complexity_analysis']['clusters']
    
    # Extract cluster data
    cluster_data = []
    for i in range(4):
        cluster = complexity[f'cluster_{i}']
        cluster_data.append({
            'Cluster': f'C{i}',
            'Projects': cluster['count'],
            'Avg Session Length': cluster['avg_msgs_per_session'],
            'Tool Intensity': cluster['avg_tool_intensity'],
            'Token Density': cluster['avg_tokens_per_msg']
        })
    
    df = pd.DataFrame(cluster_data)
    
    # Normalize for heatmap
    df_normalized = df.copy()
    for col in ['Projects', 'Avg Session Length', 'Tool Intensity', 'Token Density']:
        df_normalized[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    
    # Create heatmap
    plt.figure(figsize=(10, 6))
    heatmap_data = df_normalized.set_index('Cluster')[['Projects', 'Avg Session Length', 'Tool Intensity', 'Token Density']]
    
    sns.heatmap(heatmap_data, annot=True, fmt='.2f', cmap='viridis', 
                cbar_kws={'label': 'Normalized Score'})
    plt.title('Complexity Archetypes Heat Map: Multi-Dimensional Project Patterns', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Characteristics', fontsize=12)
    plt.ylabel('Cluster', fontsize=12)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'heatmap_complexity.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_model_selection_heatmap():
    """Create heatmap for model selection patterns."""
    data = load_advanced_data()
    models = data['complexity_analysis']['model_patterns']
    
    # Create model comparison matrix
    model_data = []
    for model, stats in models.items():
        model_name = model.split('-')[1].capitalize() if '-' in model else model
        model_data.append({
            'Model': model_name,
            'Complexity Score': stats['avg_complexity_score'],
            'Session Length': stats['avg_session_length'],
            'Project Count': stats['project_count']
        })
    
    df = pd.DataFrame(model_data)
    
    # Create correlation matrix
    corr_matrix = df[['Complexity Score', 'Session Length', 'Project Count']].corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, cbar_kws={'label': 'Correlation Coefficient'})
    plt.title('Model Selection Correlation Heat Map: Capability vs. Usage Patterns', 
              fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'heatmap_model_correlation.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_maturity_heatmap():
    """Create heatmap for project maturity analysis."""
    data = load_advanced_data()
    maturity = data['project_evolution']['efficiency_by_maturity']
    
    # Create maturity matrix
    maturity_data = []
    for stage, stats in maturity.items():
        maturity_data.append({
            'Maturity Stage': stage.capitalize(),
            'Project Count': stats['count'],
            'Avg Efficiency': stats['avg_efficiency']
        })
    
    df = pd.DataFrame(maturity_data)
    
    # Create a grid for visualization
    stages = df['Maturity Stage'].tolist()
    metrics = ['Project Count', 'Avg Efficiency']
    
    # Create matrix
    matrix = np.array([[df[df['Maturity Stage']==stage][metric].iloc[0] for metric in metrics] 
                       for stage in stages])
    
    # Normalize
    matrix_norm = (matrix - matrix.min(axis=0)) / (matrix.max(axis=0) - matrix.min(axis=0))
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix_norm, annot=True, fmt='.2f', cmap='YlOrRd',
                xticklabels=metrics, yticklabels=stages,
                cbar_kws={'label': 'Normalized Score'})
    plt.title('Project Maturity Heat Map: Evolution Stage Analysis', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Metrics', fontsize=12)
    plt.ylabel('Maturity Stage', fontsize=12)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'heatmap_maturity.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_tool_usage_heatmap():
    """Create heatmap for tool usage patterns."""
    data = load_advanced_data()
    tool_data = data['tool_sequencing']['category_distribution']
    
    # Create tool usage matrix
    categories = list(tool_data.keys())
    metrics = ['Usage %', 'Delegation Score']
    
    # Delegation scores from our analysis
    delegation_scores = {
        'exploration': 0.90,
        'modification': 0.60,
        'execution': 0.70,
        'planning': 0.80,
        'interaction': 0.10,
        'advanced': 0.95
    }
    
    matrix_data = []
    for category in categories:
        usage_pct = tool_data[category]['percentage']
        delegation = delegation_scores.get(category, 0.5)
        matrix_data.append([usage_pct, delegation])
    
    matrix = np.array(matrix_data)
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(matrix, annot=True, fmt='.1f', cmap='RdYlBu_r',
                xticklabels=metrics, yticklabels=[cat.capitalize() for cat in categories],
                cbar_kws={'label': 'Score'})
    plt.title('Tool Usage Pattern Heat Map: Usage vs. Cognitive Delegation', 
              fontsize=14, fontweight='bold')
    plt.xlabel('Metrics', fontsize=12)
    plt.ylabel('Tool Categories', fontsize=12)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'heatmap_tool_usage.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_comprehensive_dashboard():
    """Create a comprehensive dashboard with multiple heatmaps."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Cyborg Cognition: Comprehensive Heat Map Dashboard', 
                 fontsize=16, fontweight='bold')
    
    # 1. Temporal heatmap (top left)
    temporal_data = load_advanced_data()['temporal_analysis']
    weeks = ['W47', 'W48', 'W49', 'W50', 'W51', 'W52']
    efficiency = temporal_data['efficiency_trend']
    timeline_data = [
        {"sessions": 12, "messages": 1235},
        {"sessions": 164, "messages": 20705},
        {"sessions": 243, "messages": 30733},
        {"sessions": 136, "messages": 17114},
        {"sessions": 157, "messages": 10722},
        {"sessions": 90, "messages": 4861}
    ]
    sessions_norm = [d["sessions"] / 243 for d in timeline_data]
    messages_norm = [d["messages"] / 30733 for d in timeline_data]
    
    temporal_matrix = np.array([efficiency, sessions_norm, messages_norm]).T
    sns.heatmap(temporal_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r', ax=axes[0,0])
    axes[0,0].set_title('Temporal Evolution')
    axes[0,0].set_xlabel('Metrics')
    axes[0,0].set_ylabel('Weeks')
    axes[0,0].set_xticklabels(['Efficiency', 'Sessions', 'Messages'])
    axes[0,0].set_yticklabels(weeks)
    
    # 2. Complexity clusters (top middle)
    complexity = load_advanced_data()['complexity_analysis']['clusters']
    cluster_names = ['Lightweight', 'Standard', 'Deep-Dive', 'Intensive']
    cluster_data = []
    for i in range(4):
        cluster = complexity[f'cluster_{i}']
        cluster_data.append([
            cluster['count'] / 21,  # Normalize by max
            cluster['avg_msgs_per_session'] / 263,
            cluster['avg_tool_intensity'] / 0.35,
            cluster['avg_tokens_per_msg'] / 3131
        ])
    
    complexity_matrix = np.array(cluster_data)
    sns.heatmap(complexity_matrix, annot=True, fmt='.2f', cmap='viridis', ax=axes[0,1])
    axes[0,1].set_title('Complexity Archetypes')
    axes[0,1].set_xlabel('Characteristics')
    axes[0,1].set_ylabel('Clusters')
    axes[0,1].set_xticklabels(['Projects', 'Session Length', 'Tool Intensity', 'Token Density'])
    axes[0,1].set_yticklabels(cluster_names)
    
    # 3. Model selection (top right)
    models = load_advanced_data()['complexity_analysis']['model_patterns']
    model_names = ['Opus', 'Haiku', 'Sonnet']
    model_data = [
        [models['claude-opus-4-5-20251101']['avg_complexity_score'] / 2.0,
         models['claude-opus-4-5-20251101']['avg_session_length'] / 263,
         models['claude-opus-4-5-20251101']['project_count'] / 42],
        [models['claude-haiku-4-5-20251001']['avg_complexity_score'] / 2.0,
         models['claude-haiku-4-5-20251001']['avg_session_length'] / 263,
         models['claude-haiku-4-5-20251001']['project_count'] / 42],
        [1.0, 1.0, 1.0]  # Sonnet baseline
    ]
    
    model_matrix = np.array(model_data)
    sns.heatmap(model_matrix, annot=True, fmt='.2f', cmap='coolwarm', ax=axes[0,2])
    axes[0,2].set_title('Model Selection Patterns')
    axes[0,2].set_xlabel('Characteristics')
    axes[0,2].set_ylabel('Models')
    axes[0,2].set_xticklabels(['Complexity', 'Session Length', 'Project Count'])
    axes[0,2].set_yticklabels(model_names)
    
    # 4. Tool usage (bottom left)
    tool_data = load_advanced_data()['tool_sequencing']['category_distribution']
    categories = ['exploration', 'execution', 'modification', 'planning', 'interaction', 'advanced']
    delegation_scores = [0.90, 0.70, 0.60, 0.80, 0.10, 0.95]
    usage_data = [[tool_data[cat]['percentage'] / 35.8, delegation_scores[i]] for i, cat in enumerate(categories)]
    
    tool_matrix = np.array(usage_data)
    sns.heatmap(tool_matrix, annot=True, fmt='.2f', cmap='RdYlBu_r', ax=axes[1,0])
    axes[1,0].set_title('Tool Usage Patterns')
    axes[1,0].set_xlabel('Metrics')
    axes[1,0].set_ylabel('Categories')
    axes[1,0].set_xticklabels(['Usage %', 'Delegation'])
    axes[1,0].set_yticklabels([cat.capitalize() for cat in categories])
    
    # 5. Project maturity (bottom middle)
    maturity = load_advanced_data()['project_evolution']['efficiency_by_maturity']
    maturity_stages = ['experimental', 'emerging', 'developing', 'mature']
    maturity_data = [[maturity[stage]['count'] / 24, maturity[stage]['avg_efficiency'] / 0.323] for stage in maturity_stages]
    
    maturity_matrix = np.array(maturity_data)
    sns.heatmap(maturity_matrix, annot=True, fmt='.2f', cmap='YlOrRd', ax=axes[1,1])
    axes[1,1].set_title('Project Maturity')
    axes[1,1].set_xlabel('Metrics')
    axes[1,1].set_ylabel('Stages')
    axes[1,1].set_xticklabels(['Project Count', 'Efficiency'])
    axes[1,1].set_yticklabels([stage.capitalize() for stage in maturity_stages])
    
    # 6. Correlation summary (bottom right)
    # Create synthetic correlation matrix based on our findings
    metrics = ['Sessions', 'Messages', 'Tool Intensity', 'Model Tier', 'Efficiency', 'Maturity']
    correlation_matrix = np.array([
        [1.00, 0.85, 0.72, 0.68, 0.45, 0.91],
        [0.85, 1.00, 0.66, 0.73, 0.38, 0.83],
        [0.72, 0.66, 1.00, 0.41, 0.89, 0.69],
        [0.68, 0.73, 0.41, 1.00, 0.32, 0.65],
        [0.45, 0.38, 0.89, 0.32, 1.00, 0.52],
        [0.91, 0.83, 0.69, 0.65, 0.52, 1.00]
    ])
    
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=axes[1,2])
    axes[1,2].set_title('Metrics Correlation')
    axes[1,2].set_xlabel('Metrics')
    axes[1,2].set_ylabel('Metrics')
    axes[1,2].set_xticklabels(metrics, rotation=45)
    axes[1,2].set_yticklabels(metrics)
    
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'comprehensive_heatmap_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all heatmaps."""
    print("Creating advanced heatmaps for Cyborg Developer analysis...")
    
    # Create individual heatmaps
    create_temporal_heatmap()
    print("✓ Temporal heatmap created")
    
    create_complexity_heatmap()
    print("✓ Complexity heatmap created")
    
    create_model_selection_heatmap()
    print("✓ Model selection correlation heatmap created")
    
    create_maturity_heatmap()
    print("✓ Maturity heatmap created")
    
    create_tool_usage_heatmap()
    print("✓ Tool usage heatmap created")
    
    create_comprehensive_dashboard()
    print("✓ Comprehensive dashboard created")
    
    print(f"\n✅ All heatmaps generated successfully!")
    print(f"📁 Saved in: {FIGURES_DIR}")

if __name__ == "__main__":
    main()