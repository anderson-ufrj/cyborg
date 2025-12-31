#!/usr/bin/env python3
"""
Micro-Example Extractor for Cyborg Developer Paper
Author: Anderson Henrique da Silva

Extracts interaction sequences from Claude Code transcripts to illustrate:
1. Execute-Explore-Modify cycles
2. Model selection patterns (complexity matching)
3. "Act first, understand later" patterns
4. Verification/correction sequences

Output: Anonymized examples suitable for paper inclusion.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Generator, Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime

# Paths
CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "evidence" / "analysis" / "micro_examples"

# Tool categories
TOOL_CATEGORIES = {
    "exploration": ["Read", "Glob", "Grep", "WebSearch", "WebFetch", "LSP"],
    "modification": ["Write", "Edit", "MultiEdit", "NotebookEdit"],
    "execution": ["Bash", "Task", "TaskOutput", "KillShell"],
    "planning": ["TodoWrite", "EnterPlanMode", "ExitPlanMode"],
    "interaction": ["AskUserQuestion"],
}

def get_tool_category(tool_name: str) -> str:
    """Get category for a tool."""
    for category, tools in TOOL_CATEGORIES.items():
        if tool_name in tools:
            return category
    return "other"


@dataclass
class ToolEvent:
    """A single tool use event."""
    tool_name: str
    category: str
    timestamp: str
    input_preview: str
    success: bool
    model: str = None
    file_path: str = None


@dataclass
class InteractionSequence:
    """A sequence of interactions forming a pattern."""
    pattern_type: str
    events: List[ToolEvent]
    session_id: str
    project: str
    description: str


class MicroExampleExtractor:
    """Extract micro-level interaction examples from Claude transcripts."""

    def __init__(self, source_dir: Path = CLAUDE_PROJECTS):
        self.source_dir = source_dir
        self.sequences: List[InteractionSequence] = []

    def parse_jsonl(self, file_path: Path) -> Generator[Dict, None, None]:
        """Parse JSONL file line by line."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass

    def extract_tool_events(self, file_path: Path) -> List[ToolEvent]:
        """Extract all tool events from a session."""
        events = []
        current_model = None

        for entry in self.parse_jsonl(file_path):
            if entry.get("type") == "summary":
                continue

            message = entry.get("message", {})
            timestamp = entry.get("timestamp", "")

            # Track model
            if message.get("model"):
                current_model = message.get("model")

            # Extract tool uses from content
            content = message.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "tool_use":
                        tool_name = item.get("name", "")
                        tool_input = item.get("input", {})

                        # Extract file path if present
                        file_path_val = None
                        if isinstance(tool_input, dict):
                            file_path_val = tool_input.get("file_path") or tool_input.get("path")

                        # Create preview
                        input_preview = self._create_input_preview(tool_name, tool_input)

                        events.append(ToolEvent(
                            tool_name=tool_name,
                            category=get_tool_category(tool_name),
                            timestamp=timestamp,
                            input_preview=input_preview,
                            success=True,  # Will be updated by tool_result
                            model=current_model,
                            file_path=file_path_val
                        ))

                    elif item.get("type") == "tool_result":
                        # Update success status of last matching tool
                        is_error = item.get("is_error", False)
                        if events:
                            events[-1].success = not is_error

        return events

    def _create_input_preview(self, tool_name: str, tool_input: Dict) -> str:
        """Create anonymized preview of tool input."""
        if not isinstance(tool_input, dict):
            return ""

        if tool_name == "Bash":
            cmd = tool_input.get("command", "")
            # Anonymize paths
            cmd = re.sub(r'/home/[^/]+', '/home/user', cmd)
            return cmd[:100]

        elif tool_name == "Read":
            path = tool_input.get("file_path", "")
            return f"Read: {Path(path).name}"

        elif tool_name in ["Edit", "Write"]:
            path = tool_input.get("file_path", "")
            return f"{tool_name}: {Path(path).name}"

        elif tool_name == "Grep":
            pattern = tool_input.get("pattern", "")
            return f"Grep: {pattern[:50]}"

        elif tool_name == "Glob":
            pattern = tool_input.get("pattern", "")
            return f"Glob: {pattern}"

        return ""

    def find_execute_explore_modify_cycles(self, events: List[ToolEvent]) -> List[Tuple[int, int]]:
        """Find Execute→Explore→Modify cycles in event sequence."""
        cycles = []
        i = 0

        while i < len(events) - 2:
            # Look for Execution followed by Exploration followed by Modification
            if events[i].category == "execution":
                # Check next few events for explore->modify pattern
                for j in range(i + 1, min(i + 5, len(events))):
                    if events[j].category == "exploration":
                        for k in range(j + 1, min(j + 5, len(events))):
                            if events[k].category == "modification":
                                cycles.append((i, k + 1))
                                i = k
                                break
                        break
            i += 1

        return cycles

    def find_model_switches(self, events: List[ToolEvent]) -> List[Tuple[int, str, str]]:
        """Find model switches within session (rare but interesting)."""
        switches = []
        last_model = None

        for i, event in enumerate(events):
            if event.model and event.model != last_model:
                if last_model is not None:
                    switches.append((i, last_model, event.model))
                last_model = event.model

        return switches

    def find_correction_sequences(self, events: List[ToolEvent]) -> List[Tuple[int, int]]:
        """Find correction sequences (same file edited multiple times)."""
        corrections = []
        file_edits = defaultdict(list)

        for i, event in enumerate(events):
            if event.category == "modification" and event.file_path:
                file_edits[event.file_path].append(i)

        for file_path, indices in file_edits.items():
            if len(indices) >= 2:
                # Check if edits are close together (within 10 events)
                for j in range(len(indices) - 1):
                    if indices[j + 1] - indices[j] <= 10:
                        corrections.append((indices[j], indices[j + 1] + 1))

        return corrections

    def find_bash_retry_sequences(self, events: List[ToolEvent]) -> List[Tuple[int, int]]:
        """Find Bash command retry sequences (failure followed by similar command)."""
        retries = []

        for i, event in enumerate(events):
            if event.tool_name == "Bash" and not event.success:
                # Look for retry in next few events
                for j in range(i + 1, min(i + 5, len(events))):
                    if events[j].tool_name == "Bash":
                        retries.append((i, j + 1))
                        break

        return retries

    def extract_sequence(self, events: List[ToolEvent], start: int, end: int,
                         pattern_type: str, session_id: str, project: str) -> InteractionSequence:
        """Extract a sequence from events."""
        seq_events = events[start:end]

        # Create description
        tools = [e.tool_name for e in seq_events]
        description = f"{pattern_type}: {' → '.join(tools)}"

        return InteractionSequence(
            pattern_type=pattern_type,
            events=seq_events,
            session_id=session_id,
            project=project,
            description=description
        )

    def process_session(self, file_path: Path) -> List[InteractionSequence]:
        """Process a single session file."""
        sequences = []
        events = self.extract_tool_events(file_path)

        if len(events) < 3:
            return sequences

        # Extract session/project info from path
        session_id = file_path.stem[:8]
        project = file_path.parent.name.split('-')[-1] if '-' in file_path.parent.name else "unknown"

        # Find patterns
        cycles = self.find_execute_explore_modify_cycles(events)
        for start, end in cycles[:2]:  # Limit to 2 per session
            seq = self.extract_sequence(events, start, end, "execute_explore_modify", session_id, project)
            sequences.append(seq)

        corrections = self.find_correction_sequences(events)
        for start, end in corrections[:1]:  # Limit to 1 per session
            seq = self.extract_sequence(events, start, end, "correction_sequence", session_id, project)
            sequences.append(seq)

        retries = self.find_bash_retry_sequences(events)
        for start, end in retries[:1]:
            seq = self.extract_sequence(events, start, end, "bash_retry", session_id, project)
            sequences.append(seq)

        return sequences

    def run(self, limit: int = None) -> Dict[str, Any]:
        """Run extraction on all sessions."""
        print(f"[extractor] Scanning {self.source_dir}...")

        all_sequences = []
        files = list(self.source_dir.rglob("*.jsonl"))

        if limit:
            files = files[:limit]

        print(f"[extractor] Processing {len(files)} files...")

        for i, file_path in enumerate(files):
            if (i + 1) % 100 == 0:
                print(f"[extractor] Progress: {i + 1}/{len(files)}")

            # Skip agent files for cleaner examples
            if "agent-" in file_path.name:
                continue

            sequences = self.process_session(file_path)
            all_sequences.extend(sequences)

        print(f"[extractor] Found {len(all_sequences)} sequences")

        # Group by pattern type
        by_pattern = defaultdict(list)
        for seq in all_sequences:
            by_pattern[seq.pattern_type].append(seq)

        # Select best examples (most complete sequences)
        selected = {
            "execute_explore_modify": [],
            "correction_sequence": [],
            "bash_retry": [],
        }

        for pattern, seqs in by_pattern.items():
            # Sort by number of events (prefer longer sequences)
            sorted_seqs = sorted(seqs, key=lambda s: len(s.events), reverse=True)
            selected[pattern] = sorted_seqs[:5]  # Top 5 of each

        return {
            "total_sequences": len(all_sequences),
            "by_pattern": {k: len(v) for k, v in by_pattern.items()},
            "selected_examples": selected,
        }

    def format_for_paper(self, sequences: List[InteractionSequence]) -> str:
        """Format sequences for paper inclusion."""
        output = []

        for seq in sequences:
            output.append(f"\n## {seq.pattern_type.replace('_', ' ').title()}")
            output.append(f"Project: {seq.project} | Session: {seq.session_id}")
            output.append("")
            output.append("```")
            for i, event in enumerate(seq.events):
                status = "✓" if event.success else "✗"
                output.append(f"{i+1}. [{event.category}] {event.tool_name} {status}")
                if event.input_preview:
                    output.append(f"   {event.input_preview}")
            output.append("```")
            output.append("")

        return "\n".join(output)

    def save_results(self, results: Dict, output_dir: Path = OUTPUT_DIR):
        """Save extraction results."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save raw results
        raw_file = output_dir / "extraction_results.json"

        # Convert to serializable format
        serializable = {
            "total_sequences": results["total_sequences"],
            "by_pattern": results["by_pattern"],
            "timestamp": datetime.now().isoformat(),
            "selected_examples": {}
        }

        for pattern, seqs in results["selected_examples"].items():
            serializable["selected_examples"][pattern] = [
                {
                    "pattern_type": s.pattern_type,
                    "session_id": s.session_id,
                    "project": s.project,
                    "description": s.description,
                    "events": [
                        {
                            "tool_name": e.tool_name,
                            "category": e.category,
                            "input_preview": e.input_preview,
                            "success": e.success,
                        }
                        for e in s.events
                    ]
                }
                for s in seqs
            ]

        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
        print(f"[extractor] Saved results to {raw_file}")

        # Save formatted examples for paper
        all_selected = []
        for seqs in results["selected_examples"].values():
            all_selected.extend(seqs)

        formatted = self.format_for_paper(all_selected[:10])
        paper_file = output_dir / "paper_examples.md"
        with open(paper_file, 'w', encoding='utf-8') as f:
            f.write("# Micro-Level Interaction Examples\n\n")
            f.write("Extracted from Claude Code transcripts for paper inclusion.\n")
            f.write(formatted)
        print(f"[extractor] Saved paper examples to {paper_file}")


def main():
    print("=" * 60)
    print("MICRO-EXAMPLE EXTRACTOR")
    print("Cyborg Developer Paper - Interaction Patterns")
    print("=" * 60)

    extractor = MicroExampleExtractor()
    results = extractor.run()
    extractor.save_results(results)

    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total sequences found: {results['total_sequences']}")
    print("\nBy pattern type:")
    for pattern, count in results["by_pattern"].items():
        print(f"  {pattern}: {count}")
    print("\nSelected examples saved for paper inclusion.")
    print("=" * 60)


if __name__ == "__main__":
    main()
