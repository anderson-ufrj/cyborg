#!/usr/bin/env python3
"""
Comprehensive Analysis of All Data Sources for Cyborg Developer Paper
Author: Anderson Henrique da Silva

Analyzes and compares:
1. Claude Code CLI sessions (from history import)
2. Claude.ai Web conversations (from Anthropic export)
3. DevGPT dataset (external comparison)
"""

import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = DATA_DIR / "comprehensive_analysis.json"


def analyze_claude_code():
    """Analyze Claude Code CLI data from historical import."""
    report_file = DATA_DIR / "aggregate_report.json"
    if not report_file.exists():
        return None

    with open(report_file, 'r') as f:
        data = json.load(f)

    sessions = data.get("total_sessions", 0)
    return {
        "source": "Claude Code (CLI)",
        "sessions": sessions,
        "total_messages": data.get("total_messages", 0),
        "total_tool_uses": data.get("total_tool_uses", 0),
        "unique_projects": data.get("project_count", 0),
        "period_days": 30,
        "avg_messages_per_session": round(data.get("total_messages", 0) / max(sessions, 1), 1),
        "characteristics": [
            "Terminal-based interaction",
            "Tool-augmented workflow",
            "Project-specific context",
            "High autonomy mode"
        ]
    }


def analyze_claude_web():
    """Analyze Claude.ai web conversations from Anthropic export."""
    conv_file = DATA_DIR / "anthropic_export" / "conversations.json"
    if not conv_file.exists():
        return None

    with open(conv_file, 'r') as f:
        data = json.load(f)

    total_msgs = sum(len(c.get('chat_messages', [])) for c in data)
    msg_counts = [len(c.get('chat_messages', [])) for c in data]

    # Get date range
    dates = [c.get('created_at', '')[:10] for c in data if c.get('created_at')]

    return {
        "source": "Claude.ai (Web)",
        "sessions": len(data),
        "total_messages": total_msgs,
        "total_tool_uses": 0,  # Web interface doesn't have tool tracking
        "unique_projects": 14,  # From projects.json
        "period_days": 365,  # Full year
        "date_range": f"{min(dates)} to {max(dates)}" if dates else "N/A",
        "avg_messages_per_session": round(total_msgs / max(len(data), 1), 1),
        "characteristics": [
            "Browser-based interaction",
            "Conversational Q&A",
            "General-purpose queries",
            "Manual copy-paste workflow"
        ]
    }


def analyze_devgpt():
    """Analyze DevGPT dataset for external comparison."""
    devgpt_file = DATA_DIR / "devgpt_analysis.json"
    if not devgpt_file.exists():
        return None

    with open(devgpt_file, 'r') as f:
        data = json.load(f)

    return {
        "source": "DevGPT (External)",
        "sessions": data.get("total_conversations", 0),
        "total_messages": data.get("total_prompts", 0) * 2,  # prompts + answers
        "total_prompts": data.get("total_prompts", 0),
        "code_snippets": data.get("code_snippets", 0),
        "avg_messages_per_session": data.get("avg_prompts_per_conversation", 0) * 2,
        "models": data.get("models", {}),
        "characteristics": [
            "ChatGPT shared links",
            "GitHub/HackerNews context",
            "Community-sourced data",
            "Multiple developers"
        ]
    }


def create_comparison():
    """Create comparison analysis."""
    claude_code = analyze_claude_code()
    claude_web = analyze_claude_web()
    devgpt = analyze_devgpt()

    comparison = {
        "claude_code": claude_code,
        "claude_web": claude_web,
        "devgpt": devgpt,
        "key_insights": []
    }

    # Calculate key insights
    if claude_code and claude_web:
        intensity_ratio = round(claude_code["avg_messages_per_session"] / claude_web["avg_messages_per_session"], 1)
        comparison["key_insights"].append({
            "insight": "Session Intensity Difference",
            "value": f"{intensity_ratio}x",
            "description": f"Claude Code sessions are {intensity_ratio}x more intensive than web chat"
        })

    if claude_code and devgpt:
        devgpt_ratio = round(claude_code["avg_messages_per_session"] / max(devgpt["avg_messages_per_session"], 1), 1)
        comparison["key_insights"].append({
            "insight": "vs DevGPT Community Average",
            "value": f"{devgpt_ratio}x",
            "description": f"Individual developer sessions {devgpt_ratio}x longer than DevGPT community average"
        })

    if claude_code:
        comparison["key_insights"].append({
            "insight": "Tool Augmentation",
            "value": f"{claude_code['total_tool_uses']:,}",
            "description": "Tool invocations demonstrating AI as execution engine, not just conversational agent"
        })

    return comparison


def main():
    print("=" * 60)
    print("COMPREHENSIVE DATA ANALYSIS")
    print("=" * 60)

    comparison = create_comparison()

    # Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(comparison, f, indent=2)
    print(f"\nSaved to: {OUTPUT_FILE}")

    # Print summary
    print("\n" + "=" * 60)
    print("DATA SOURCE COMPARISON")
    print("=" * 60)

    sources = [
        ("Claude Code (CLI)", comparison.get("claude_code")),
        ("Claude.ai (Web)", comparison.get("claude_web")),
        ("DevGPT (External)", comparison.get("devgpt"))
    ]

    print(f"\n{'Source':<20} {'Sessions':>10} {'Messages':>12} {'Avg/Session':>12}")
    print("-" * 56)

    for name, data in sources:
        if data:
            print(f"{name:<20} {data['sessions']:>10,} {data['total_messages']:>12,} {data['avg_messages_per_session']:>12.1f}")

    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)

    for insight in comparison.get("key_insights", []):
        print(f"\n{insight['insight']}: {insight['value']}")
        print(f"  → {insight['description']}")

    return comparison


if __name__ == "__main__":
    main()
