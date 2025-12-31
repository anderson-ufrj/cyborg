#!/usr/bin/env python3
"""
Historical Data Importer for Claude Code Sessions
Author: Anderson Henrique da Silva

Imports interaction data from ~/.claude/projects JSONL files
and converts to the prompt engineering lab metrics format.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Generator, Dict, Any, List
import hashlib
import argparse

# Default paths
DEFAULT_SOURCE = Path.home() / ".claude" / "projects"
DEFAULT_OUTPUT = Path(__file__).parent.parent.parent / "evidence" / "metrics" / "historical"


class HistoryImporter:
    """Import and process Claude Code session history."""

    def __init__(self, source_dir: Path, output_dir: Path):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "files_processed": 0,
            "sessions_found": 0,
            "messages_processed": 0,
            "tool_uses_extracted": 0,
            "errors": 0,
            "projects": set(),
            "models": defaultdict(int),
            "tools": defaultdict(int),
        }

    def find_jsonl_files(self) -> Generator[Path, None, None]:
        """Find all JSONL session files."""
        for jsonl_file in self.source_dir.rglob("*.jsonl"):
            yield jsonl_file

    def parse_jsonl(self, file_path: Path) -> Generator[Dict[str, Any], None, None]:
        """Parse a JSONL file line by line."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as e:
                        self.stats["errors"] += 1
        except Exception as e:
            self.stats["errors"] += 1

    def extract_tool_uses(self, content: List[Dict]) -> List[Dict]:
        """Extract tool use information from message content."""
        tool_uses = []
        for item in content:
            if item.get("type") == "tool_use":
                tool_uses.append({
                    "tool_id": item.get("id"),
                    "tool_name": item.get("name"),
                    "input_keys": list(item.get("input", {}).keys()) if isinstance(item.get("input"), dict) else None,
                })
        return tool_uses

    def extract_tool_results(self, content: List[Dict]) -> List[Dict]:
        """Extract tool result information from message content."""
        results = []
        for item in content:
            if item.get("type") == "tool_result":
                # Check for errors
                is_error = item.get("is_error", False)
                content_preview = str(item.get("content", ""))[:100] if item.get("content") else None
                results.append({
                    "tool_use_id": item.get("tool_use_id"),
                    "is_error": is_error,
                    "has_content": bool(item.get("content")),
                })
        return results

    def process_session(self, file_path: Path) -> Dict[str, Any]:
        """Process a single session file and extract metrics."""
        session_data = {
            "file": str(file_path),
            "session_id": None,
            "project": None,
            "git_branch": None,
            "models_used": [],
            "messages": [],
            "tool_uses": [],
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cache_tokens": 0,
            "start_time": None,
            "end_time": None,
            "message_count": 0,
            "user_message_count": 0,
            "assistant_message_count": 0,
        }

        for event in self.parse_jsonl(file_path):
            event_type = event.get("type")

            # Skip file history snapshots
            if event_type == "file-history-snapshot":
                continue

            # Extract session metadata
            if not session_data["session_id"]:
                session_data["session_id"] = event.get("sessionId")

            if not session_data["project"] and event.get("cwd"):
                session_data["project"] = os.path.basename(event.get("cwd"))
                self.stats["projects"].add(session_data["project"])

            if not session_data["git_branch"]:
                session_data["git_branch"] = event.get("gitBranch")

            # Process timestamp
            timestamp = event.get("timestamp")
            if timestamp:
                if not session_data["start_time"]:
                    session_data["start_time"] = timestamp
                session_data["end_time"] = timestamp

            # Process messages
            message = event.get("message", {})
            role = message.get("role")

            if role == "user":
                session_data["user_message_count"] += 1
                session_data["message_count"] += 1
                self.stats["messages_processed"] += 1

            elif role == "assistant":
                session_data["assistant_message_count"] += 1
                session_data["message_count"] += 1
                self.stats["messages_processed"] += 1

                # Extract model
                model = message.get("model")
                if model and model not in session_data["models_used"]:
                    session_data["models_used"].append(model)
                    self.stats["models"][model] += 1

                # Extract usage tokens
                usage = message.get("usage", {})
                session_data["total_input_tokens"] += usage.get("input_tokens", 0)
                session_data["total_output_tokens"] += usage.get("output_tokens", 0)
                session_data["total_cache_tokens"] += usage.get("cache_read_input_tokens", 0)
                session_data["total_cache_tokens"] += usage.get("cache_creation_input_tokens", 0)

                # Extract tool uses
                content = message.get("content", [])
                if isinstance(content, list):
                    tool_uses = self.extract_tool_uses(content)
                    for tu in tool_uses:
                        session_data["tool_uses"].append(tu)
                        if tu["tool_name"]:
                            self.stats["tools"][tu["tool_name"]] += 1
                            self.stats["tool_uses_extracted"] += 1

        return session_data

    def aggregate_sessions(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Aggregate metrics across all sessions."""
        aggregate = {
            "import_timestamp": datetime.now().isoformat(),
            "total_sessions": len(sessions),
            "total_messages": sum(s["message_count"] for s in sessions),
            "total_user_messages": sum(s["user_message_count"] for s in sessions),
            "total_assistant_messages": sum(s["assistant_message_count"] for s in sessions),
            "total_tool_uses": sum(len(s["tool_uses"]) for s in sessions),
            "total_input_tokens": sum(s["total_input_tokens"] for s in sessions),
            "total_output_tokens": sum(s["total_output_tokens"] for s in sessions),
            "total_cache_tokens": sum(s["total_cache_tokens"] for s in sessions),
            "unique_projects": list(self.stats["projects"]),
            "project_count": len(self.stats["projects"]),
            "models_distribution": dict(self.stats["models"]),
            "tools_distribution": dict(self.stats["tools"]),
            "top_tools": sorted(self.stats["tools"].items(), key=lambda x: x[1], reverse=True)[:20],
            "sessions_by_project": defaultdict(int),
        }

        # Count sessions per project
        for s in sessions:
            if s["project"]:
                aggregate["sessions_by_project"][s["project"]] += 1

        aggregate["sessions_by_project"] = dict(aggregate["sessions_by_project"])

        return aggregate

    def run(self, limit: int = None) -> Dict[str, Any]:
        """Run the full import process."""
        print(f"[importer] Scanning {self.source_dir}...")

        sessions = []
        jsonl_files = list(self.find_jsonl_files())
        total_files = len(jsonl_files)

        if limit:
            jsonl_files = jsonl_files[:limit]

        print(f"[importer] Found {total_files} JSONL files, processing {len(jsonl_files)}...")

        for i, file_path in enumerate(jsonl_files):
            if (i + 1) % 100 == 0:
                print(f"[importer] Progress: {i + 1}/{len(jsonl_files)} files...")

            session_data = self.process_session(file_path)
            if session_data["message_count"] > 0:
                sessions.append(session_data)
                self.stats["sessions_found"] += 1

            self.stats["files_processed"] += 1

        print(f"[importer] Processed {self.stats['files_processed']} files")
        print(f"[importer] Found {self.stats['sessions_found']} valid sessions")

        # Aggregate
        aggregate = self.aggregate_sessions(sessions)

        # Save aggregate report
        aggregate_file = self.output_dir / "aggregate_report.json"
        with open(aggregate_file, 'w', encoding='utf-8') as f:
            json.dump(aggregate, f, indent=2, ensure_ascii=False)
        print(f"[importer] Saved aggregate report to {aggregate_file}")

        # Save individual session summaries (without full content for privacy)
        sessions_file = self.output_dir / "sessions_summary.json"
        session_summaries = []
        for s in sessions:
            summary = {
                "session_id": s["session_id"],
                "project": s["project"],
                "git_branch": s["git_branch"],
                "models_used": s["models_used"],
                "message_count": s["message_count"],
                "user_message_count": s["user_message_count"],
                "assistant_message_count": s["assistant_message_count"],
                "tool_use_count": len(s["tool_uses"]),
                "total_input_tokens": s["total_input_tokens"],
                "total_output_tokens": s["total_output_tokens"],
                "start_time": s["start_time"],
                "end_time": s["end_time"],
            }
            session_summaries.append(summary)

        with open(sessions_file, 'w', encoding='utf-8') as f:
            json.dump(session_summaries, f, indent=2, ensure_ascii=False)
        print(f"[importer] Saved {len(session_summaries)} session summaries to {sessions_file}")

        # Save tool usage stats
        tools_file = self.output_dir / "tool_usage_stats.json"
        with open(tools_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_tool_uses": self.stats["tool_uses_extracted"],
                "tools": dict(self.stats["tools"]),
                "top_20": aggregate["top_tools"],
            }, f, indent=2, ensure_ascii=False)
        print(f"[importer] Saved tool usage stats to {tools_file}")

        return aggregate


def main():
    parser = argparse.ArgumentParser(description="Import Claude Code history")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                        help="Source directory with JSONL files")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output directory for metrics")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of files to process (for testing)")

    args = parser.parse_args()

    importer = HistoryImporter(args.source, args.output)
    result = importer.run(limit=args.limit)

    # Print summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Total Sessions:      {result['total_sessions']}")
    print(f"Total Messages:      {result['total_messages']}")
    print(f"Total Tool Uses:     {result['total_tool_uses']}")
    print(f"Unique Projects:     {result['project_count']}")
    print(f"Input Tokens:        {result['total_input_tokens']:,}")
    print(f"Output Tokens:       {result['total_output_tokens']:,}")
    print(f"Cache Tokens:        {result['total_cache_tokens']:,}")
    print("\nTop 10 Tools:")
    for tool, count in result['top_tools'][:10]:
        print(f"  {tool}: {count}")
    print("\nModels Used:")
    for model, count in result['models_distribution'].items():
        print(f"  {model}: {count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
