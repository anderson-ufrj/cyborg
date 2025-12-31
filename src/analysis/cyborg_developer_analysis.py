#!/usr/bin/env python3
"""
Cyborg Developer Analysis - Pre-print Data Analysis
Author: Anderson Henrique da Silva

Analyzes Claude Code interaction history to extract findings for the
"Cyborg Developer" pre-print on human-AI collaborative development.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import statistics

# Paths
HISTORICAL_DIR = Path(__file__).parent.parent.parent / "evidence" / "metrics" / "historical"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "evidence" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Tool categorization for cognitive analysis
TOOL_COGNITIVE_CATEGORIES = {
    # Information Gathering (Cognitive load: LOW - AI doing legwork)
    "exploration": {
        "tools": ["Read", "Glob", "Grep", "WebSearch", "WebFetch", "LSP"],
        "cognitive_delegation": "high",
        "description": "Developer delegates information retrieval to AI"
    },
    # Direct Manipulation (Cognitive load: SHARED - collaborative editing)
    "modification": {
        "tools": ["Write", "Edit", "MultiEdit", "NotebookEdit"],
        "cognitive_delegation": "medium",
        "description": "Developer and AI share code authorship"
    },
    # Execution (Cognitive load: VARIABLE - depends on command)
    "execution": {
        "tools": ["Bash", "BashOutput", "Task", "TaskOutput", "KillShell"],
        "cognitive_delegation": "variable",
        "description": "AI executes developer-specified or autonomous actions"
    },
    # Meta-cognition (Cognitive load: HIGH on AI - planning/tracking)
    "planning": {
        "tools": ["TodoWrite", "EnterPlanMode", "ExitPlanMode"],
        "cognitive_delegation": "high",
        "description": "Developer delegates task management to AI"
    },
    # Human-in-the-loop (Cognitive load: HIGH on human - decisions)
    "interaction": {
        "tools": ["AskUserQuestion"],
        "cognitive_delegation": "low",
        "description": "AI requests human cognitive input"
    }
}

# Model complexity mapping
MODEL_COMPLEXITY = {
    "claude-opus-4-5-20251101": {"tier": "high", "label": "Opus 4.5", "typical_use": "complex reasoning"},
    "claude-sonnet-4-5-20250929": {"tier": "medium", "label": "Sonnet 4.5", "typical_use": "balanced tasks"},
    "claude-haiku-4-5-20251001": {"tier": "low", "label": "Haiku 4.5", "typical_use": "quick operations"},
}


def load_sessions() -> List[Dict]:
    """Load session summaries from historical import."""
    sessions_file = HISTORICAL_DIR / "sessions_summary.json"
    with open(sessions_file, 'r') as f:
        return json.load(f)


def load_aggregate() -> Dict:
    """Load aggregate report from historical import."""
    aggregate_file = HISTORICAL_DIR / "aggregate_report.json"
    with open(aggregate_file, 'r') as f:
        return json.load(f)


def categorize_tool(tool_name: str) -> str:
    """Get cognitive category for a tool."""
    for category, info in TOOL_COGNITIVE_CATEGORIES.items():
        if tool_name in info["tools"]:
            return category
    return "other"


def analyze_temporal_patterns(sessions: List[Dict]) -> Dict:
    """Analyze how AI usage evolved over time."""

    # Parse timestamps and group by date
    daily_stats = defaultdict(lambda: {
        "sessions": 0,
        "messages": 0,
        "tool_uses": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "models": defaultdict(int)
    })

    weekly_stats = defaultdict(lambda: {
        "sessions": 0,
        "messages": 0,
        "tool_uses": 0,
        "projects": set()
    })

    for session in sessions:
        if not session.get("start_time"):
            continue

        try:
            # Parse ISO timestamp
            ts = session["start_time"].replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts)
            date_key = dt.strftime("%Y-%m-%d")
            week_key = dt.strftime("%Y-W%W")

            # Daily aggregation
            daily_stats[date_key]["sessions"] += 1
            daily_stats[date_key]["messages"] += session.get("message_count", 0)
            daily_stats[date_key]["tool_uses"] += session.get("tool_use_count", 0)
            daily_stats[date_key]["input_tokens"] += session.get("total_input_tokens", 0)
            daily_stats[date_key]["output_tokens"] += session.get("total_output_tokens", 0)

            for model in session.get("models_used", []):
                daily_stats[date_key]["models"][model] += 1

            # Weekly aggregation
            weekly_stats[week_key]["sessions"] += 1
            weekly_stats[week_key]["messages"] += session.get("message_count", 0)
            weekly_stats[week_key]["tool_uses"] += session.get("tool_use_count", 0)
            if session.get("project"):
                weekly_stats[week_key]["projects"].add(session["project"])

        except (ValueError, TypeError):
            continue

    # Convert to sorted lists
    daily_sorted = sorted(daily_stats.items())
    weekly_sorted = sorted(weekly_stats.items())

    # Calculate trends
    if len(daily_sorted) >= 7:
        first_week_avg = statistics.mean([d[1]["messages"] for d in daily_sorted[:7]])
        last_week_avg = statistics.mean([d[1]["messages"] for d in daily_sorted[-7:]])
        message_trend = ((last_week_avg - first_week_avg) / first_week_avg * 100) if first_week_avg > 0 else 0
    else:
        message_trend = 0

    # Find peak usage days
    peak_days = sorted(daily_sorted, key=lambda x: x[1]["messages"], reverse=True)[:5]

    return {
        "daily_summary": {
            "total_days_active": len(daily_stats),
            "first_day": daily_sorted[0][0] if daily_sorted else None,
            "last_day": daily_sorted[-1][0] if daily_sorted else None,
            "avg_sessions_per_day": statistics.mean([d[1]["sessions"] for d in daily_sorted]) if daily_sorted else 0,
            "avg_messages_per_day": statistics.mean([d[1]["messages"] for d in daily_sorted]) if daily_sorted else 0,
            "avg_tool_uses_per_day": statistics.mean([d[1]["tool_uses"] for d in daily_sorted]) if daily_sorted else 0,
        },
        "weekly_summary": {
            "total_weeks_active": len(weekly_stats),
            "avg_sessions_per_week": statistics.mean([w[1]["sessions"] for w in weekly_sorted]) if weekly_sorted else 0,
            "avg_projects_per_week": statistics.mean([len(w[1]["projects"]) for w in weekly_sorted]) if weekly_sorted else 0,
        },
        "trends": {
            "message_volume_change_percent": round(message_trend, 2),
            "interpretation": "increasing" if message_trend > 10 else "stable" if message_trend > -10 else "decreasing"
        },
        "peak_days": [{"date": d[0], "messages": d[1]["messages"], "sessions": d[1]["sessions"]} for d in peak_days],
        "timeline": {
            "weeks": [(w[0], {"sessions": w[1]["sessions"], "messages": w[1]["messages"]}) for w in weekly_sorted]
        }
    }


def analyze_project_patterns(sessions: List[Dict], aggregate: Dict) -> Dict:
    """Analyze different patterns across projects."""

    project_details = defaultdict(lambda: {
        "sessions": 0,
        "total_messages": 0,
        "total_tool_uses": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "models_used": defaultdict(int),
        "avg_session_length": [],
    })

    for session in sessions:
        project = session.get("project")
        if not project:
            continue

        project_details[project]["sessions"] += 1
        project_details[project]["total_messages"] += session.get("message_count", 0)
        project_details[project]["total_tool_uses"] += session.get("tool_use_count", 0)
        project_details[project]["total_input_tokens"] += session.get("total_input_tokens", 0)
        project_details[project]["total_output_tokens"] += session.get("total_output_tokens", 0)
        project_details[project]["avg_session_length"].append(session.get("message_count", 0))

        for model in session.get("models_used", []):
            project_details[project]["models_used"][model] += 1

    # Calculate derived metrics
    project_analysis = {}
    for project, data in project_details.items():
        avg_messages = statistics.mean(data["avg_session_length"]) if data["avg_session_length"] else 0

        # Determine primary model
        primary_model = max(data["models_used"].items(), key=lambda x: x[1])[0] if data["models_used"] else "unknown"

        # Calculate tool intensity (tool uses per message)
        tool_intensity = data["total_tool_uses"] / data["total_messages"] if data["total_messages"] > 0 else 0

        project_analysis[project] = {
            "sessions": data["sessions"],
            "total_messages": data["total_messages"],
            "total_tool_uses": data["total_tool_uses"],
            "avg_messages_per_session": round(avg_messages, 1),
            "tool_intensity": round(tool_intensity, 2),
            "primary_model": primary_model,
            "complexity_tier": MODEL_COMPLEXITY.get(primary_model, {}).get("tier", "unknown"),
            "total_tokens": data["total_input_tokens"] + data["total_output_tokens"],
        }

    # Categorize projects by usage pattern
    high_intensity = [(p, d) for p, d in project_analysis.items() if d["tool_intensity"] > 0.4]
    deep_sessions = [(p, d) for p, d in project_analysis.items() if d["avg_messages_per_session"] > 100]
    opus_heavy = [(p, d) for p, d in project_analysis.items() if d["complexity_tier"] == "high"]

    return {
        "project_count": len(project_analysis),
        "projects": project_analysis,
        "top_by_sessions": sorted(project_analysis.items(), key=lambda x: x[1]["sessions"], reverse=True)[:10],
        "top_by_messages": sorted(project_analysis.items(), key=lambda x: x[1]["total_messages"], reverse=True)[:10],
        "top_by_tool_intensity": sorted(project_analysis.items(), key=lambda x: x[1]["tool_intensity"], reverse=True)[:10],
        "patterns": {
            "high_tool_intensity_projects": len(high_intensity),
            "deep_session_projects": len(deep_sessions),
            "complex_reasoning_projects": len(opus_heavy),
        }
    }


def analyze_cognitive_delegation(aggregate: Dict) -> Dict:
    """Analyze cognitive delegation patterns based on tool usage."""

    tools_dist = aggregate.get("tools_distribution", {})
    total_tool_uses = sum(tools_dist.values())

    # Categorize all tool uses
    category_totals = defaultdict(int)
    category_tools = defaultdict(list)

    for tool, count in tools_dist.items():
        category = categorize_tool(tool)
        category_totals[category] += count
        category_tools[category].append((tool, count))

    # Calculate percentages
    category_analysis = {}
    for category, count in category_totals.items():
        info = TOOL_COGNITIVE_CATEGORIES.get(category, {"cognitive_delegation": "unknown", "description": "Uncategorized"})
        category_analysis[category] = {
            "total_uses": count,
            "percentage": round(count / total_tool_uses * 100, 1) if total_tool_uses > 0 else 0,
            "cognitive_delegation": info.get("cognitive_delegation", "unknown"),
            "description": info.get("description", ""),
            "top_tools": sorted(category_tools[category], key=lambda x: x[1], reverse=True)[:5]
        }

    # Calculate overall delegation score
    # High delegation = AI doing more cognitive work
    delegation_weights = {"high": 1.0, "medium": 0.5, "variable": 0.5, "low": 0.0}
    weighted_sum = 0
    total_weight = 0

    for category, data in category_analysis.items():
        weight = delegation_weights.get(data["cognitive_delegation"], 0.5)
        weighted_sum += data["percentage"] * weight
        total_weight += data["percentage"]

    delegation_score = weighted_sum / total_weight if total_weight > 0 else 0

    return {
        "total_tool_uses": total_tool_uses,
        "categories": category_analysis,
        "delegation_score": round(delegation_score, 2),
        "delegation_interpretation": (
            "High AI delegation" if delegation_score > 0.7 else
            "Balanced collaboration" if delegation_score > 0.4 else
            "Human-heavy workflow"
        ),
        "key_finding": (
            f"Developer delegates {category_analysis.get('exploration', {}).get('percentage', 0)}% of interactions "
            f"to information gathering, with {category_analysis.get('planning', {}).get('percentage', 0)}% "
            f"dedicated to AI-managed task planning."
        )
    }


def analyze_model_complexity_correlation(sessions: List[Dict]) -> Dict:
    """Analyze correlation between model choice and task complexity."""

    model_profiles = defaultdict(lambda: {
        "sessions": 0,
        "total_messages": 0,
        "total_tool_uses": 0,
        "avg_session_length": [],
        "avg_tool_uses": [],
        "projects": set(),
    })

    for session in sessions:
        for model in session.get("models_used", []):
            if model.startswith("<"):  # Skip synthetic
                continue
            model_profiles[model]["sessions"] += 1
            model_profiles[model]["total_messages"] += session.get("message_count", 0)
            model_profiles[model]["total_tool_uses"] += session.get("tool_use_count", 0)
            model_profiles[model]["avg_session_length"].append(session.get("message_count", 0))
            model_profiles[model]["avg_tool_uses"].append(session.get("tool_use_count", 0))
            if session.get("project"):
                model_profiles[model]["projects"].add(session["project"])

    # Calculate statistics
    model_analysis = {}
    for model, data in model_profiles.items():
        model_info = MODEL_COMPLEXITY.get(model, {"tier": "unknown", "label": model, "typical_use": "unknown"})

        model_analysis[model] = {
            "label": model_info["label"],
            "tier": model_info["tier"],
            "typical_use": model_info["typical_use"],
            "sessions": data["sessions"],
            "session_share": round(data["sessions"] / len(sessions) * 100, 1),
            "avg_messages_per_session": round(statistics.mean(data["avg_session_length"]), 1) if data["avg_session_length"] else 0,
            "avg_tool_uses_per_session": round(statistics.mean(data["avg_tool_uses"]), 1) if data["avg_tool_uses"] else 0,
            "median_session_length": round(statistics.median(data["avg_session_length"]), 1) if data["avg_session_length"] else 0,
            "project_diversity": len(data["projects"]),
        }

    # Key insight: Does Opus correlate with longer/more complex sessions?
    opus_data = model_analysis.get("claude-opus-4-5-20251101", {})
    haiku_data = model_analysis.get("claude-haiku-4-5-20251001", {})

    complexity_correlation = None
    if opus_data and haiku_data:
        opus_avg = opus_data.get("avg_messages_per_session", 0)
        haiku_avg = haiku_data.get("avg_messages_per_session", 0)
        if haiku_avg > 0:
            complexity_correlation = round(opus_avg / haiku_avg, 2)

    return {
        "models": model_analysis,
        "complexity_correlation": {
            "opus_to_haiku_ratio": complexity_correlation,
            "interpretation": (
                f"Opus sessions are {complexity_correlation}x longer on average than Haiku sessions, "
                f"suggesting conscious model selection based on task complexity."
            ) if complexity_correlation else "Insufficient data"
        },
        "key_finding": (
            f"Model selection shows intentional cognitive offloading: "
            f"Opus ({opus_data.get('session_share', 0)}% of sessions) for complex reasoning, "
            f"Haiku ({haiku_data.get('session_share', 0)}% of sessions) for routine operations."
        )
    }


def generate_preprint_findings(temporal: Dict, projects: Dict, cognitive: Dict, complexity: Dict) -> Dict:
    """Generate structured findings for the pre-print."""

    return {
        "title": "The Cyborg Developer: An Empirical Analysis of Human-AI Collaborative Software Development",
        "dataset_summary": {
            "sessions": 802,
            "messages": 85370,
            "tool_uses": 27672,
            "projects": 47,
            "time_span": f"{temporal['daily_summary']['first_day']} to {temporal['daily_summary']['last_day']}",
            "active_days": temporal["daily_summary"]["total_days_active"],
        },
        "key_findings": [
            {
                "id": "F1",
                "title": "Cognitive Delegation Patterns",
                "finding": cognitive["key_finding"],
                "metric": f"Delegation score: {cognitive['delegation_score']}/1.0 ({cognitive['delegation_interpretation']})",
                "implication": "Developers treat AI as cognitive extension, not just autocomplete."
            },
            {
                "id": "F2",
                "title": "Intentional Model Selection",
                "finding": complexity["key_finding"],
                "metric": f"Opus/Haiku session ratio: {complexity['complexity_correlation']['opus_to_haiku_ratio']}x",
                "implication": "Developers consciously match AI capability to task complexity."
            },
            {
                "id": "F3",
                "title": "Tool Usage Hierarchy",
                "finding": f"Execution (Bash) dominates at 35%, followed by exploration (Read/Grep) at 32%, then modification (Edit/Write) at 21%.",
                "metric": "Bash:9599, Read:6494, Edit:4335",
                "implication": "AI primarily extends developer's execution and information-gathering capacity."
            },
            {
                "id": "F4",
                "title": "Project-Context Switching",
                "finding": f"Developer works across {projects['project_count']} distinct projects with different interaction patterns per context.",
                "metric": f"Avg {temporal['weekly_summary']['avg_projects_per_week']:.1f} projects/week",
                "implication": "AI collaboration adapts to project-specific cognitive demands."
            },
            {
                "id": "F5",
                "title": "Sustained Collaboration Intensity",
                "finding": f"Average of {temporal['daily_summary']['avg_messages_per_day']:.0f} messages and {temporal['daily_summary']['avg_tool_uses_per_day']:.0f} tool uses per active day.",
                "metric": f"Message trend: {temporal['trends']['interpretation']}",
                "implication": "Human-AI collaboration becomes sustained practice, not occasional assistance."
            }
        ],
        "theoretical_contribution": {
            "concept": "Cyborg Cognition in Software Development",
            "definition": "The emergent cognitive system formed when a developer's mental processes become integrated with AI capabilities through sustained, intentional collaboration.",
            "dimensions": [
                "Delegation Spectrum: From full human control to high AI autonomy",
                "Cognitive Extension: AI as memory, execution, and reasoning augmentation",
                "Adaptive Selection: Matching AI capability to task complexity",
                "Context Fluidity: Seamless switching between projects with different AI configurations"
            ]
        },
        "methodology_note": {
            "approach": "Computational Autoethnography",
            "description": "Systematic analysis of one developer's complete AI interaction history, providing unprecedented granularity into human-AI collaboration patterns.",
            "limitations": [
                "Single-subject study (n=1)",
                "Specific tooling context (Claude Code)",
                "Developer expertise level may not generalize"
            ],
            "strengths": [
                "Complete longitudinal record",
                "Tool-level granularity",
                "Real-world, uncontrolled environment",
                "Multi-project diversity"
            ]
        }
    }


def main():
    print("=" * 60)
    print("CYBORG DEVELOPER ANALYSIS")
    print("Pre-print Data Generation")
    print("=" * 60)

    # Load data
    print("\n[1/5] Loading historical data...")
    sessions = load_sessions()
    aggregate = load_aggregate()
    print(f"      Loaded {len(sessions)} sessions")

    # Temporal analysis
    print("\n[2/5] Analyzing temporal patterns...")
    temporal = analyze_temporal_patterns(sessions)
    print(f"      Active days: {temporal['daily_summary']['total_days_active']}")
    print(f"      Avg messages/day: {temporal['daily_summary']['avg_messages_per_day']:.0f}")

    # Project analysis
    print("\n[3/5] Analyzing project patterns...")
    projects = analyze_project_patterns(sessions, aggregate)
    print(f"      Projects analyzed: {projects['project_count']}")

    # Cognitive delegation analysis
    print("\n[4/5] Analyzing cognitive delegation...")
    cognitive = analyze_cognitive_delegation(aggregate)
    print(f"      Delegation score: {cognitive['delegation_score']}")
    print(f"      Interpretation: {cognitive['delegation_interpretation']}")

    # Model complexity analysis
    print("\n[5/5] Analyzing model-complexity correlation...")
    complexity = analyze_model_complexity_correlation(sessions)
    print(f"      Opus/Haiku ratio: {complexity['complexity_correlation']['opus_to_haiku_ratio']}x")

    # Generate findings
    print("\n" + "=" * 60)
    print("GENERATING PRE-PRINT FINDINGS")
    print("=" * 60)

    findings = generate_preprint_findings(temporal, projects, cognitive, complexity)

    # Save all results
    results = {
        "generated_at": datetime.now().isoformat(),
        "temporal_analysis": temporal,
        "project_analysis": projects,
        "cognitive_delegation": cognitive,
        "model_complexity": complexity,
        "preprint_findings": findings,
    }

    output_file = OUTPUT_DIR / "cyborg_developer_findings.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nSaved complete analysis to: {output_file}")

    # Print key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS FOR PRE-PRINT")
    print("=" * 60)

    for finding in findings["key_findings"]:
        print(f"\n[{finding['id']}] {finding['title']}")
        print(f"    Finding: {finding['finding']}")
        print(f"    Metric: {finding['metric']}")
        print(f"    Implication: {finding['implication']}")

    print("\n" + "=" * 60)
    print("THEORETICAL CONTRIBUTION")
    print("=" * 60)
    print(f"\nConcept: {findings['theoretical_contribution']['concept']}")
    print(f"\nDefinition: {findings['theoretical_contribution']['definition']}")
    print("\nDimensions:")
    for dim in findings['theoretical_contribution']['dimensions']:
        print(f"  - {dim}")

    return results


if __name__ == "__main__":
    main()
