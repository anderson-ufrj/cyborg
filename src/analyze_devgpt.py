#!/usr/bin/env python3
"""
DevGPT Dataset Analysis for Cyborg Developer Paper Comparison
Author: Anderson Henrique da Silva

Analyzes the DevGPT dataset to extract comparable metrics with our Cyborg Developer data.
"""

import json
import os
from pathlib import Path
from collections import defaultdict
import statistics

DEVGPT_DIR = Path(__file__).parent.parent / "data" / "DevGPT_full" / "snapshot_20231012"
OUTPUT_DIR = Path(__file__).parent.parent / "data"

def analyze_json_file(filepath: Path, limit: int = None) -> dict:
    """Analyze a single DevGPT JSON file."""
    print(f"  Analyzing {filepath.name}...")

    stats = {
        "total_entries": 0,
        "total_conversations": 0,
        "total_prompts": 0,
        "total_prompt_tokens": 0,
        "total_answer_tokens": 0,
        "models": defaultdict(int),
        "prompts_per_conversation": [],
        "code_snippets": 0,
        "status_200": 0,
        "status_other": 0,
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"    Error loading {filepath}: {e}")
        return stats

    # DevGPT data is nested inside "Sources" array
    if isinstance(data, dict) and "Sources" in data:
        entries = data["Sources"]
    elif isinstance(data, list):
        entries = data
    else:
        entries = [data]

    for i, entry in enumerate(entries):
        if limit and i >= limit:
            break

        stats["total_entries"] += 1

        # Process ChatGPT sharings
        sharings = entry.get("ChatgptSharing", [])
        if not isinstance(sharings, list):
            sharings = [sharings] if sharings else []

        for sharing in sharings:
            if not sharing:
                continue

            status = sharing.get("Status", 0)
            if status == 200:
                stats["status_200"] += 1
            else:
                stats["status_other"] += 1
                continue

            stats["total_conversations"] += 1

            num_prompts = sharing.get("NumberOfPrompts", 0)
            stats["total_prompts"] += num_prompts
            stats["prompts_per_conversation"].append(num_prompts)

            stats["total_prompt_tokens"] += sharing.get("TokensOfPrompts", 0) or 0
            stats["total_answer_tokens"] += sharing.get("TokensOfAnswers", 0) or 0

            model = sharing.get("Model", "unknown")
            stats["models"][model] += 1

            # Count code snippets
            conversations = sharing.get("Conversations", [])
            for conv in conversations:
                code_list = conv.get("ListOfCode", [])
                stats["code_snippets"] += len(code_list) if code_list else 0

    return stats


def main():
    print("=" * 60)
    print("DEVGPT DATASET ANALYSIS")
    print("=" * 60)

    # Files to analyze
    files = [
        "20231012_230826_commit_sharings.json",      # 54MB
        "20231012_233628_pr_sharings.json",          # 33MB
        "20231012_235128_issue_sharings.json",       # 69MB
        "20231012_235320_discussion_sharings.json",  # 7MB
        "20231012_232232_hn_sharings.json",          # 28MB
        # Skipping file_sharings.json (613MB) for now
    ]

    aggregate = {
        "total_entries": 0,
        "total_conversations": 0,
        "total_prompts": 0,
        "total_prompt_tokens": 0,
        "total_answer_tokens": 0,
        "models": defaultdict(int),
        "prompts_per_conversation": [],
        "code_snippets": 0,
        "status_200": 0,
        "by_source": {},
    }

    for filename in files:
        filepath = DEVGPT_DIR / filename
        if not filepath.exists():
            print(f"  Skipping {filename} (not found)")
            continue

        stats = analyze_json_file(filepath)

        # Store by source
        source = filename.split("_")[2].replace("sharings.json", "").replace("_", "")
        aggregate["by_source"][source] = {
            "entries": stats["total_entries"],
            "conversations": stats["total_conversations"],
            "prompts": stats["total_prompts"],
        }

        # Aggregate
        aggregate["total_entries"] += stats["total_entries"]
        aggregate["total_conversations"] += stats["total_conversations"]
        aggregate["total_prompts"] += stats["total_prompts"]
        aggregate["total_prompt_tokens"] += stats["total_prompt_tokens"]
        aggregate["total_answer_tokens"] += stats["total_answer_tokens"]
        aggregate["code_snippets"] += stats["code_snippets"]
        aggregate["status_200"] += stats["status_200"]
        aggregate["prompts_per_conversation"].extend(stats["prompts_per_conversation"])

        for model, count in stats["models"].items():
            aggregate["models"][model] += count

    # Calculate derived metrics
    if aggregate["prompts_per_conversation"]:
        aggregate["avg_prompts_per_conversation"] = statistics.mean(aggregate["prompts_per_conversation"])
        aggregate["median_prompts_per_conversation"] = statistics.median(aggregate["prompts_per_conversation"])
    else:
        aggregate["avg_prompts_per_conversation"] = 0
        aggregate["median_prompts_per_conversation"] = 0

    aggregate["total_tokens"] = aggregate["total_prompt_tokens"] + aggregate["total_answer_tokens"]

    # Convert defaultdict to dict for JSON
    aggregate["models"] = dict(aggregate["models"])
    del aggregate["prompts_per_conversation"]  # Too large to save

    # Save results
    output_file = OUTPUT_DIR / "devgpt_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(aggregate, f, indent=2)
    print(f"\nSaved analysis to {output_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("DEVGPT SUMMARY (excluding file_sharings)")
    print("=" * 60)
    print(f"Total GitHub/HN entries:     {aggregate['total_entries']:,}")
    print(f"Valid conversations (200):   {aggregate['total_conversations']:,}")
    print(f"Total prompts:               {aggregate['total_prompts']:,}")
    print(f"Total code snippets:         {aggregate['code_snippets']:,}")
    print(f"Avg prompts/conversation:    {aggregate['avg_prompts_per_conversation']:.1f}")
    print(f"Median prompts/conversation: {aggregate['median_prompts_per_conversation']:.1f}")
    print(f"Total prompt tokens:         {aggregate['total_prompt_tokens']:,}")
    print(f"Total answer tokens:         {aggregate['total_answer_tokens']:,}")
    print(f"\nBy source:")
    for source, data in aggregate['by_source'].items():
        print(f"  {source}: {data['conversations']:,} conversations, {data['prompts']:,} prompts")
    print(f"\nModels used:")
    for model, count in sorted(aggregate['models'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {model}: {count:,}")

    print("\n" + "=" * 60)

    return aggregate


if __name__ == "__main__":
    main()
