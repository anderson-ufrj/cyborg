#!/usr/bin/env python3
"""
Compute weekly delegation scores for temporal stability analysis.

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brazil
"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
DATA_DIR = Path(__file__).parent.parent.parent / "evidence" / "metrics" / "data"

# Delegation weights
DELEGATION_WEIGHTS = {
    "exploration": 1.0,   # High delegation
    "planning": 1.0,      # High delegation
    "modification": 0.5,  # Medium delegation
    "execution": 0.5,     # Variable (treated as medium)
    "interaction": 0.0,   # Low delegation
    "other": 0.5
}

def compute_delegation_score(category_counts):
    """Compute delegation score from category counts."""
    total = sum(category_counts.values())
    if total == 0:
        return 0.0

    weighted_sum = 0
    for category, count in category_counts.items():
        weight = DELEGATION_WEIGHTS.get(category, 0.5)
        percentage = (count / total) * 100
        weighted_sum += percentage * weight

    return weighted_sum / 100  # Normalize to 0-1

def main():
    # Load all metric files and group by ISO week
    weekly_data = defaultdict(lambda: defaultdict(int))

    for json_file in DATA_DIR.glob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)

            timestamp = data.get("timestamp")
            category = data.get("tool_category", "other")

            if timestamp:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                week_key = dt.strftime("W%V")  # ISO week number
                weekly_data[week_key][category] += 1
        except Exception as e:
            continue

    # Compute delegation score per week
    print("\n" + "=" * 60)
    print("WEEKLY DELEGATION SCORES")
    print("=" * 60)
    print(f"\n{'Week':<8} {'Sessions':<10} {'D Score':<10} {'Exploration':<12} {'Execution':<10} {'Modification':<12}")
    print("-" * 62)

    weekly_scores = {}
    for week in sorted(weekly_data.keys()):
        categories = weekly_data[week]
        total = sum(categories.values())
        score = compute_delegation_score(categories)
        weekly_scores[week] = {
            "delegation_score": round(score, 2),
            "tool_uses": total,
            "exploration_pct": round(categories.get("exploration", 0) / total * 100, 1) if total > 0 else 0,
            "execution_pct": round(categories.get("execution", 0) / total * 100, 1) if total > 0 else 0,
            "modification_pct": round(categories.get("modification", 0) / total * 100, 1) if total > 0 else 0,
        }

        print(f"{week:<8} {total:<10} {score:.2f}       {weekly_scores[week]['exploration_pct']:<12} {weekly_scores[week]['execution_pct']:<10} {weekly_scores[week]['modification_pct']:<12}")

    # Summary statistics
    scores = [v["delegation_score"] for v in weekly_scores.values()]
    print("-" * 62)
    print(f"{'Overall':<8} {sum(v['tool_uses'] for v in weekly_scores.values()):<10} {sum(scores)/len(scores):.2f}")
    print(f"\nMin score: {min(scores):.2f}")
    print(f"Max score: {max(scores):.2f}")
    print(f"Range: {max(scores) - min(scores):.2f}")

    # LaTeX table
    print("\n\nLaTeX Table:")
    print("\\begin{table}[h]")
    print("\\caption{Weekly Delegation Score Stability}")
    print("\\label{tab:weekly-delegation}")
    print("\\begin{tabular}{lrrrr}")
    print("\\toprule")
    print("\\textbf{Week} & \\textbf{Tool Uses} & \\textbf{D Score} & \\textbf{Expl. \\%} & \\textbf{Exec. \\%} \\\\")
    print("\\midrule")
    for week in sorted(weekly_scores.keys()):
        ws = weekly_scores[week]
        print(f"{week} & {ws['tool_uses']:,} & {ws['delegation_score']:.2f} & {ws['exploration_pct']} & {ws['execution_pct']} \\\\")
    print("\\midrule")
    avg_score = sum(scores)/len(scores)
    total_uses = sum(v['tool_uses'] for v in weekly_scores.values())
    print(f"\\textbf{{Overall}} & \\textbf{{{total_uses:,}}} & \\textbf{{{avg_score:.2f}}} & --- & --- \\\\")
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{table}")

    return weekly_scores

if __name__ == "__main__":
    main()
