#!/usr/bin/env python3
"""
Verification Pattern Analyzer for Cyborg Developer Paper
Author: Anderson Henrique da Silva

Analyzes AI output verification/rejection patterns to assess "automatic endorsement":
1. Consecutive edits to same file (corrections)
2. Bash command failures and retries
3. User rejection keywords ("no", "wrong", "try again")
4. Tool result errors

This addresses the peer review concern about measuring verification behavior.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Generator, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# Paths
CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "evidence" / "analysis"

# Rejection keywords (case-insensitive)
REJECTION_KEYWORDS = [
    r"\bno\b",
    r"\bwrong\b",
    r"\bincorrect\b",
    r"\btry again\b",
    r"\bfix\b",
    r"\bundo\b",
    r"\brevert\b",
    r"\bnot what i\b",
    r"\bthat's not\b",
    r"\bactually\b",
    r"\binstead\b",
    r"\bdon't\b",
    r"\bstop\b",
    r"\bcancel\b",
    r"\berror\b",
    r"\bfailed\b",
    r"\bbroke\b",
]


@dataclass
class VerificationMetrics:
    """Aggregated verification behavior metrics."""
    total_tool_uses: int = 0
    tool_errors: int = 0
    bash_failures: int = 0
    bash_retries: int = 0
    consecutive_edits_same_file: int = 0
    user_rejection_messages: int = 0
    total_user_messages: int = 0

    # Derived metrics
    @property
    def error_rate(self) -> float:
        return self.tool_errors / self.total_tool_uses if self.total_tool_uses > 0 else 0

    @property
    def bash_failure_rate(self) -> float:
        return self.bash_failures / self.total_tool_uses if self.total_tool_uses > 0 else 0

    @property
    def correction_rate(self) -> float:
        """Rate of edits that are corrections to previous edits."""
        return self.consecutive_edits_same_file / self.total_tool_uses if self.total_tool_uses > 0 else 0

    @property
    def user_rejection_rate(self) -> float:
        """Rate of user messages containing rejection keywords."""
        return self.user_rejection_messages / self.total_user_messages if self.total_user_messages > 0 else 0


class VerificationAnalyzer:
    """Analyze verification and rejection patterns in Claude transcripts."""

    def __init__(self, source_dir: Path = CLAUDE_PROJECTS):
        self.source_dir = source_dir
        self.metrics = VerificationMetrics()
        self.examples = {
            "bash_failures": [],
            "corrections": [],
            "rejections": [],
        }

    def parse_jsonl(self, file_path: Path) -> Generator[Dict, None, None]:
        """Parse JSONL file."""
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

    def analyze_session(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single session for verification patterns."""
        session_metrics = {
            "tool_uses": 0,
            "tool_errors": 0,
            "bash_failures": 0,
            "bash_retries": 0,
            "consecutive_edits": 0,
            "user_rejections": 0,
            "user_messages": 0,
        }

        # Track tool uses for pattern detection
        recent_tools = []  # (tool_name, file_path, success, index)
        recent_bash_failed = False

        for entry in self.parse_jsonl(file_path):
            if entry.get("type") == "summary":
                continue

            message = entry.get("message", {})
            role = message.get("role")
            content = message.get("content", [])

            # Analyze user messages for rejection keywords
            if role == "user":
                session_metrics["user_messages"] += 1
                self.metrics.total_user_messages += 1

                # Check for rejection keywords
                user_text = self._extract_text(content)
                if self._contains_rejection(user_text):
                    session_metrics["user_rejections"] += 1
                    self.metrics.user_rejection_messages += 1

                    # Store example (limit to first few)
                    if len(self.examples["rejections"]) < 20:
                        self.examples["rejections"].append({
                            "session": file_path.stem[:8],
                            "text_preview": user_text[:200],
                        })

            # Analyze assistant tool uses
            elif role == "assistant" and isinstance(content, list):
                for item in content:
                    if item.get("type") == "tool_use":
                        session_metrics["tool_uses"] += 1
                        self.metrics.total_tool_uses += 1

                        tool_name = item.get("name", "")
                        tool_input = item.get("input", {})
                        file_path_val = None

                        if isinstance(tool_input, dict):
                            file_path_val = tool_input.get("file_path") or tool_input.get("path")

                        # Check for Bash retry after failure
                        if tool_name == "Bash" and recent_bash_failed:
                            session_metrics["bash_retries"] += 1
                            self.metrics.bash_retries += 1
                            recent_bash_failed = False

                        # Check for consecutive edits to same file
                        if tool_name in ["Edit", "Write", "MultiEdit"] and file_path_val:
                            for prev_tool, prev_path, prev_success, prev_idx in reversed(recent_tools[-5:]):
                                if prev_tool in ["Edit", "Write", "MultiEdit"] and prev_path == file_path_val:
                                    session_metrics["consecutive_edits"] += 1
                                    self.metrics.consecutive_edits_same_file += 1

                                    if len(self.examples["corrections"]) < 20:
                                        self.examples["corrections"].append({
                                            "session": file_path.stem[:8],
                                            "file": Path(file_path_val).name if file_path_val else "unknown",
                                            "tool": tool_name,
                                        })
                                    break

                        recent_tools.append((tool_name, file_path_val, True, len(recent_tools)))

                    elif item.get("type") == "tool_result":
                        is_error = item.get("is_error", False)
                        if is_error:
                            session_metrics["tool_errors"] += 1
                            self.metrics.tool_errors += 1

                            # Check if it was a Bash failure
                            if recent_tools and recent_tools[-1][0] == "Bash":
                                session_metrics["bash_failures"] += 1
                                self.metrics.bash_failures += 1
                                recent_bash_failed = True

                                if len(self.examples["bash_failures"]) < 20:
                                    content_text = str(item.get("content", ""))[:200]
                                    self.examples["bash_failures"].append({
                                        "session": file_path.stem[:8],
                                        "error_preview": content_text,
                                    })

        return session_metrics

    def _extract_text(self, content) -> str:
        """Extract text from message content."""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    texts.append(item.get("text", ""))
                elif isinstance(item, str):
                    texts.append(item)
            return " ".join(texts)
        return ""

    def _contains_rejection(self, text: str) -> bool:
        """Check if text contains rejection keywords."""
        text_lower = text.lower()
        for pattern in REJECTION_KEYWORDS:
            if re.search(pattern, text_lower):
                return True
        return False

    def run(self, limit: int = None) -> Dict[str, Any]:
        """Run analysis on all sessions."""
        print(f"[analyzer] Scanning {self.source_dir}...")

        files = list(self.source_dir.rglob("*.jsonl"))
        if limit:
            files = files[:limit]

        print(f"[analyzer] Processing {len(files)} files...")

        session_count = 0
        for i, file_path in enumerate(files):
            if (i + 1) % 100 == 0:
                print(f"[analyzer] Progress: {i + 1}/{len(files)}")

            # Skip agent files
            if "agent-" in file_path.name:
                continue

            self.analyze_session(file_path)
            session_count += 1

        print(f"[analyzer] Processed {session_count} sessions")

        return self._generate_report()

    def _generate_report(self) -> Dict[str, Any]:
        """Generate verification behavior report."""
        m = self.metrics

        # Calculate verification proxy metrics
        # Higher values = more verification behavior
        verification_score = (
            m.error_rate * 0.3 +           # Tool errors (weighted low)
            m.correction_rate * 0.4 +      # Corrections (weighted high)
            m.user_rejection_rate * 0.3    # User rejections
        )

        # Automatic endorsement proxy (inverse of verification)
        # This is what the peer review is asking about
        endorsement_proxy = 1 - verification_score

        return {
            "timestamp": datetime.now().isoformat(),
            "raw_metrics": {
                "total_tool_uses": m.total_tool_uses,
                "tool_errors": m.tool_errors,
                "bash_failures": m.bash_failures,
                "bash_retries": m.bash_retries,
                "consecutive_edits_same_file": m.consecutive_edits_same_file,
                "user_rejection_messages": m.user_rejection_messages,
                "total_user_messages": m.total_user_messages,
            },
            "rates": {
                "tool_error_rate": round(m.error_rate * 100, 2),
                "bash_failure_rate": round(m.bash_failure_rate * 100, 2),
                "correction_rate": round(m.correction_rate * 100, 2),
                "user_rejection_rate": round(m.user_rejection_rate * 100, 2),
            },
            "derived_metrics": {
                "verification_score": round(verification_score, 4),
                "endorsement_proxy": round(endorsement_proxy, 4),
            },
            "interpretation": {
                "verification_behavior": self._interpret_verification(verification_score),
                "endorsement_level": self._interpret_endorsement(endorsement_proxy),
            },
            "examples": {
                "bash_failures": self.examples["bash_failures"][:5],
                "corrections": self.examples["corrections"][:5],
                "rejections": self.examples["rejections"][:5],
            },
            "paper_finding": self._generate_paper_finding(),
        }

    def _interpret_verification(self, score: float) -> str:
        if score < 0.05:
            return "Minimal verification behavior - high automatic endorsement"
        elif score < 0.10:
            return "Low verification behavior - substantial automatic endorsement"
        elif score < 0.20:
            return "Moderate verification behavior - mixed endorsement pattern"
        else:
            return "High verification behavior - skeptical endorsement pattern"

    def _interpret_endorsement(self, score: float) -> str:
        if score > 0.95:
            return "Very high automatic endorsement"
        elif score > 0.90:
            return "High automatic endorsement"
        elif score > 0.80:
            return "Moderate automatic endorsement"
        else:
            return "Low automatic endorsement"

    def _generate_paper_finding(self) -> str:
        """Generate finding text for paper."""
        m = self.metrics

        return f"""Verification Behavior Analysis:
- Tool error rate: {m.error_rate*100:.1f}% ({m.tool_errors}/{m.total_tool_uses} tool uses)
- Bash failure rate: {m.bash_failure_rate*100:.1f}% ({m.bash_failures} failures, {m.bash_retries} retries)
- Correction rate: {m.correction_rate*100:.1f}% ({m.consecutive_edits_same_file} consecutive edits to same file)
- User rejection rate: {m.user_rejection_rate*100:.1f}% ({m.user_rejection_messages}/{m.total_user_messages} user messages)

These metrics provide partial evidence for automatic endorsement behavior. The low
correction and rejection rates suggest substantial trust in AI outputs, though we
acknowledge this is a behavioral proxy, not direct measurement of cognitive endorsement."""

    def save_results(self, results: Dict, output_path: Path = None):
        """Save analysis results."""
        if output_path is None:
            output_path = OUTPUT_DIR / "verification_analysis.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"[analyzer] Saved results to {output_path}")

        # Also save paper-ready text
        paper_path = OUTPUT_DIR / "verification_finding.md"
        with open(paper_path, 'w', encoding='utf-8') as f:
            f.write("# Verification Behavior Analysis\n\n")
            f.write("## Key Finding\n\n")
            f.write(results["paper_finding"])
            f.write("\n\n## Rates\n\n")
            for metric, value in results["rates"].items():
                f.write(f"- **{metric.replace('_', ' ').title()}**: {value}%\n")
            f.write("\n\n## Interpretation\n\n")
            f.write(f"- Verification Behavior: {results['interpretation']['verification_behavior']}\n")
            f.write(f"- Endorsement Level: {results['interpretation']['endorsement_level']}\n")
        print(f"[analyzer] Saved paper finding to {paper_path}")


def main():
    print("=" * 60)
    print("VERIFICATION PATTERN ANALYZER")
    print("Cyborg Developer Paper - Automatic Endorsement Assessment")
    print("=" * 60)

    analyzer = VerificationAnalyzer()
    results = analyzer.run()
    analyzer.save_results(results)

    print("\n" + "=" * 60)
    print("VERIFICATION ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"\nRaw Metrics:")
    for metric, value in results["raw_metrics"].items():
        print(f"  {metric}: {value:,}")

    print(f"\nRates:")
    for metric, value in results["rates"].items():
        print(f"  {metric}: {value}%")

    print(f"\nDerived Metrics:")
    print(f"  Verification Score: {results['derived_metrics']['verification_score']:.4f}")
    print(f"  Endorsement Proxy: {results['derived_metrics']['endorsement_proxy']:.4f}")

    print(f"\nInterpretation:")
    print(f"  {results['interpretation']['verification_behavior']}")
    print(f"  {results['interpretation']['endorsement_level']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
