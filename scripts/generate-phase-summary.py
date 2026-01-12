#!/usr/bin/env python3
"""
Phase Summary Generator

Creates formatted summaries after each phase completion for interactive approval.
Extracts key decisions, outputs, and provides continuation options.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


def extract_key_decisions_from_files(phase_dir: Path, phase_num: int) -> List[str]:
    """
    Extract key decisions from phase output files.

    Uses heuristics to find important content:
    - Lines starting with "##" (markdown headers)
    - Lines with "Decision:", "Recommendation:", "Selected:"
    - First paragraph of each major section
    """
    decisions = []

    if not phase_dir.exists():
        return decisions

    # Phase-specific key files
    key_files = {
        1: ["competitive_analysis.md", "market_overview.md"],
        2: ["architecture_document.md", "building_blocks.md"],
        3: ["feasibility_analysis.md", "risk_assessment.md", "service_cost_analysis.md"],
        4: ["sprint_plan.md"],
        5: ["marketing_campaign.md"],
        6: ["plan_review.md"]
    }

    for filename in key_files.get(phase_num, []):
        file_path = phase_dir / filename
        if file_path.exists():
            decisions.extend(_extract_decisions_from_file(file_path))

    return decisions[:10]  # Limit to top 10 most important


def _extract_decisions_from_file(file_path: Path) -> List[str]:
    """Extract decision-like statements from a file."""
    decisions = []

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.strip()

            # Look for explicit decision markers
            if any(marker in line.lower() for marker in [
                "decision:", "recommendation:", "selected:", "chosen:",
                "we will", "approach:", "strategy:", "conclusion:"
            ]):
                # Get the decision (current line + next line if short)
                decision = line
                if i + 1 < len(lines) and len(line) < 50:
                    decision += " " + lines[i + 1].strip()
                decisions.append(_clean_decision(decision))

            # Look for ## headers (key sections)
            elif line.startswith("## "):
                header = line.replace("## ", "").strip()
                # Get first non-empty line after header
                for j in range(i + 1, min(i + 5, len(lines))):
                    content = lines[j].strip()
                    if content and not content.startswith("#"):
                        decisions.append(f"{header}: {content[:100]}")
                        break

    except Exception:
        pass  # Gracefully handle file read errors

    return decisions


def _clean_decision(text: str) -> str:
    """Clean up extracted decision text."""
    # Remove markdown formatting
    text = text.replace("**", "").replace("*", "").replace("#", "")
    # Remove excessive whitespace
    text = " ".join(text.split())
    # Limit length
    if len(text) > 120:
        text = text[:117] + "..."
    return text


def count_output_files(phase_dir: Path) -> Dict[str, int]:
    """Count outputs by type."""
    if not phase_dir.exists():
        return {}

    counts = {
        "markdown": 0,
        "diagrams": 0,
        "yaml": 0,
        "total_lines": 0
    }

    for file_path in phase_dir.rglob("*"):
        if file_path.is_file():
            if file_path.suffix == ".md":
                counts["markdown"] += 1
                try:
                    with open(file_path, encoding="utf-8") as f:
                        counts["total_lines"] += len(f.readlines())
                except Exception:
                    pass
            elif file_path.suffix in [".png", ".svg", ".mermaid"]:
                counts["diagrams"] += 1
            elif file_path.suffix in [".yaml", ".yml"]:
                counts["yaml"] += 1

    return counts


def generate_phase_summary(
    plan_dir: Path,
    phase_num: int,
    phase_name: str,
    duration_minutes: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive summary for a completed phase.

    Returns:
        Dictionary with summary data for display
    """
    phase_dir = plan_dir / f"0{phase_num}_{phase_name.lower().replace(' ', '_').replace('&', 'and')}"

    # Extract key information
    decisions = extract_key_decisions_from_files(phase_dir, phase_num)
    outputs = count_output_files(phase_dir)

    # Build summary
    summary = {
        "phase_num": phase_num,
        "phase_name": phase_name,
        "completed_at": datetime.now().isoformat(),
        "duration_minutes": duration_minutes,
        "key_decisions": decisions,
        "outputs": outputs,
        "phase_dir": str(phase_dir)
    }

    return summary


def format_phase_summary_markdown(summary: Dict[str, Any]) -> str:
    """Format phase summary as markdown for display."""
    lines = [
        "=" * 70,
        f"✓ PHASE {summary['phase_num']} COMPLETE: {summary['phase_name']}",
    ]

    if summary.get('duration_minutes'):
        lines[1] += f" ({summary['duration_minutes']} min)"

    lines.extend([
        "=" * 70,
        ""
    ])

    # Key Decisions
    if summary["key_decisions"]:
        lines.append("Key Decisions:")
        for decision in summary["key_decisions"][:5]:  # Top 5
            lines.append(f"  • {decision}")
        lines.append("")

    # Outputs
    outputs = summary["outputs"]
    if outputs:
        lines.append("Key Outputs:")
        if outputs.get("markdown", 0) > 0:
            lines.append(f"  • 📄 {outputs['markdown']} markdown documents ({outputs.get('total_lines', 0):,} lines)")
        if outputs.get("diagrams", 0) > 0:
            lines.append(f"  • 📊 {outputs['diagrams']} diagrams generated")
        if outputs.get("yaml", 0) > 0:
            lines.append(f"  • 🔧 {outputs['yaml']} YAML building blocks")
        lines.append("")

    # Next steps
    next_phase_names = {
        1: "Phase 2: Architecture & Design",
        2: "Phase 3: Feasibility & Costs",
        3: "Phase 4: Implementation Planning",
        4: "Phase 5: Go-to-Market Strategy",
        5: "Phase 6: Plan Review",
        6: None  # Final phase
    }

    next_phase = next_phase_names.get(summary['phase_num'])
    if next_phase:
        lines.append(f"Next: {next_phase}")
        lines.append("")

    lines.append("=" * 70)

    return "\n".join(lines)


def generate_approval_question(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AskUserQuestion payload for interactive approval.

    Returns:
        Question dict for AskUserQuestion tool
    """
    phase_num = summary['phase_num']
    phase_name = summary['phase_name']

    # Check if this is the final phase
    is_final = phase_num == 6

    if is_final:
        # Final phase - just ask if they want post-plan analysis
        return {
            "question": f"Phase {phase_num} ({phase_name}) is complete. What would you like to do?",
            "header": "Completion",
            "multiSelect": False,
            "options": [
                {
                    "label": "Finalize plan (Recommended)",
                    "description": "Generate executive summary and run post-plan analysis for optimization recommendations"
                },
                {
                    "label": "Review outputs manually first",
                    "description": "Pause here. Resume later with /resume-plan if needed"
                }
            ]
        }

    # Regular phase approval
    return {
        "question": f"Phase {phase_num} ({phase_name}) is complete. How would you like to proceed?",
        "header": f"Phase {phase_num}",
        "multiSelect": False,
        "options": [
            {
                "label": "Continue to next phase (Recommended)",
                "description": f"Proceed with Phase {phase_num + 1}. Outputs look good"
            },
            {
                "label": "Revise this phase",
                "description": "Provide feedback to adjust direction before continuing. Useful if key decisions need refinement"
            },
            {
                "label": "Pause planning",
                "description": "Stop here to review outputs thoroughly. Resume later with /resume-plan"
            }
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate phase summary for interactive approval"
    )
    parser.add_argument(
        "plan_directory",
        type=Path,
        help="Path to planning output directory"
    )
    parser.add_argument(
        "phase_num",
        type=int,
        help="Phase number (1-6)"
    )
    parser.add_argument(
        "phase_name",
        type=str,
        help="Phase name (e.g., 'Market Research')"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Phase duration in minutes (optional)"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "question"],
        default="markdown",
        help="Output format"
    )

    args = parser.parse_args()

    # Generate summary
    summary = generate_phase_summary(
        args.plan_directory,
        args.phase_num,
        args.phase_name,
        args.duration
    )

    # Output in requested format
    if args.format == "json":
        print(json.dumps(summary, indent=2))
    elif args.format == "question":
        question = generate_approval_question(summary)
        print(json.dumps({"questions": [question]}, indent=2))
    else:  # markdown
        print(format_phase_summary_markdown(summary))


if __name__ == "__main__":
    main()
