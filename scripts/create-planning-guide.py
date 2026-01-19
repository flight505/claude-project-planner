#!/usr/bin/env python3
"""
Create simple planning guide from user input.
NO gap-filling, NO assumptions - just organize what's provided.
"""

import argparse
import sys
from pathlib import Path


def extract_simple_info(raw_input: str) -> dict:
    """
    Extract basic information from input WITHOUT adding/assuming anything.

    Rules:
    - Only extract brief overview
    - Preserve original input completely
    - NO gap-filling or assumptions
    """

    # Extract overview (first 3-5 meaningful lines)
    lines = [line.strip() for line in raw_input.strip().split('\n') if line.strip()]

    # Get first few non-header lines as overview
    overview_lines = []
    for line in lines[:10]:  # Check first 10 lines
        if not line.startswith('#') and len(line) > 20:  # Skip headers and short lines
            overview_lines.append(line)
            if len(overview_lines) >= 3:  # Take first 3 meaningful lines
                break

    overview = " ".join(overview_lines) if overview_lines else raw_input[:300]

    # Truncate overview if too long
    if len(overview) > 400:
        overview = overview[:400] + "..."

    return {
        "overview": overview
    }


def create_guide(raw_input: str, output_path: Path):
    """
    Create simple planning guide from raw input.

    Format:
    - What we're building
    - Mentioned details (ONLY what's explicitly in input)
    - Original input preserved
    - Clear statement: NO additions made
    """

    info = extract_simple_info(raw_input)

    guide = f"""# Project Planning Guide
*Auto-generated from your input - review before proceeding*

## Overview
{info['overview']}

---

## Complete Input
```
{raw_input}
```

---

**Note**: This is your original input organized for review. NO additional information has been added. The AI will use this to create research prompts and generate your comprehensive project plan.
"""

    output_path.write_text(guide)
    print(f"✅ Created planning guide: {output_path}")
    print(f"   Overview: {info['overview'][:80]}...")


def main():
    parser = argparse.ArgumentParser(
        description="Create simple planning guide from user input"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Raw input text or path to file (prefix with @ for file)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for guide file"
    )

    args = parser.parse_args()

    # Get input
    if args.input.startswith("@"):
        # File reference
        input_file = Path(args.input[1:])
        if not input_file.exists():
            print(f"❌ Input file not found: {input_file}", file=sys.stderr)
            sys.exit(1)
        raw_input = input_file.read_text()
    else:
        # Direct text
        raw_input = args.input

    # Create guide
    create_guide(raw_input, args.output)


if __name__ == "__main__":
    main()
