#!/usr/bin/env python3
"""
OCR Pipeline for Screenshot Analysis
Author: Anderson Henrique da Silva

Extracts text from screenshots to identify Claude Code interactions
and enrich the Cyborg Developer dataset.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
import easyocr

# Initialize OCR reader (downloads models on first run)
print("Initializing EasyOCR (may download models on first run)...")
reader = easyocr.Reader(['en', 'pt'], gpu=True)

SCREENSHOTS_DIR = Path(__file__).parent.parent / "data" / "screenshots"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "ocr_results"
OUTPUT_DIR.mkdir(exist_ok=True)


def extract_text(image_path: Path) -> dict:
    """Extract text from a single screenshot."""
    try:
        results = reader.readtext(str(image_path))

        # Combine all text
        full_text = " ".join([r[1] for r in results])

        # Detect if it's a Claude Code terminal session
        text_lower = full_text.lower()

        # Strong indicators (terminal-specific)
        strong_indicators = [
            'claude code v',  # Version string
            'opus 4', 'sonnet 4', 'haiku 4',  # Model names
            'todowrite', 'enterplanmode', 'exitplanmode',  # Claude Code tools
            'claude max', 'claude pro',  # Subscription tiers
            '~/documentos',  # Project path pattern
            'anderson%',  # Terminal prompt
        ]

        # Medium indicators (need 2+)
        medium_indicators = [
            'terminal', 'bash', 'grep', 'glob',
            'tool_use', 'tool_result',
            'for shortcuts', '/doctor',
        ]

        strong_match = any(p in text_lower for p in strong_indicators)
        medium_count = sum(1 for p in medium_indicators if p in text_lower)

        is_claude_code = strong_match or medium_count >= 2

        # Extract timestamp from filename
        filename = image_path.name
        timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2})\s*(\d{2}-\d{2}-\d{2})?', filename)
        if timestamp_match:
            date_str = timestamp_match.group(1)
            time_str = timestamp_match.group(2) if timestamp_match.group(2) else "00-00-00"
            timestamp = f"{date_str} {time_str.replace('-', ':')}"
        else:
            timestamp = None

        return {
            "file": str(image_path),
            "filename": filename,
            "timestamp": timestamp,
            "is_claude_code": is_claude_code,
            "text_length": len(full_text),
            "full_text": full_text,
            "raw_results": [(r[1], float(r[2])) for r in results]  # text, confidence
        }
    except Exception as e:
        return {
            "file": str(image_path),
            "filename": image_path.name,
            "error": str(e)
        }


def process_all_screenshots(limit: int = None):
    """Process all screenshots and save results."""
    all_pngs = list(SCREENSHOTS_DIR.rglob("*.png"))
    print(f"Found {len(all_pngs)} PNG files")

    if limit:
        all_pngs = all_pngs[:limit]
        print(f"Processing first {limit} files...")

    results = []
    claude_code_count = 0

    for i, png in enumerate(all_pngs):
        print(f"[{i+1}/{len(all_pngs)}] Processing: {png.name}...", end=" ")
        result = extract_text(png)
        results.append(result)

        if result.get("is_claude_code"):
            claude_code_count += 1
            print("✓ Claude Code detected")
        else:
            print("○")

    # Save results
    output_file = OUTPUT_DIR / f"ocr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    summary = {
        "total_processed": len(results),
        "claude_code_detected": claude_code_count,
        "errors": len([r for r in results if "error" in r]),
        "avg_text_length": sum(r.get("text_length", 0) for r in results) / max(len(results), 1)
    }

    summary_file = OUTPUT_DIR / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print("OCR PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total processed: {summary['total_processed']}")
    print(f"Claude Code detected: {summary['claude_code_detected']}")
    print(f"Errors: {summary['errors']}")
    print(f"Avg text length: {summary['avg_text_length']:.0f} chars")
    print(f"\nResults saved to: {output_file}")

    return results


def process_sample(n: int = 5):
    """Process a sample of screenshots for testing."""
    print(f"Processing sample of {n} screenshots...")
    return process_all_screenshots(limit=n)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        process_sample(n)
    else:
        process_all_screenshots()
