#!/usr/bin/env python3
"""
Phase Dependency Analyzer

Analyzes dependencies between planning phases to support intelligent revision cascading.
Determines which phases must be re-executed when a specific phase is revised.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List


# Phase dependency graph
# Each phase lists which phases it depends on
PHASE_DEPENDENCIES = {
    1: [],  # Market research - no dependencies
    2: [1],  # Architecture depends on market research
    3: [2],  # Feasibility depends on architecture
    4: [3],  # Implementation depends on feasibility
    5: [4],  # Marketing depends on implementation plan
    6: [1, 2, 3, 4, 5],  # Review depends on everything
}

# Reverse mapping: which phases depend on each phase?
DEPENDENT_PHASES = {
    1: [2, 3, 4, 5, 6],  # If Phase 1 revised, affects all later phases
    2: [3, 4, 6],        # If Phase 2 revised, affects 3, 4, and 6
    3: [4, 6],           # If Phase 3 revised, affects 4 and 6
    4: [5, 6],           # If Phase 4 revised, affects 5 and 6
    5: [6],              # If Phase 5 revised, affects only 6
    6: [],               # Phase 6 is terminal
}

# Estimated time to re-run each phase (minutes)
# Based on analysis in parallelization-scenarios.md
PHASE_TIMES = {
    1: 23,  # Market research (research-lookup + competitive-analysis + reports)
    2: 35,  # Architecture (architecture-research + building-blocks + diagrams)
    3: 37,  # Feasibility (feasibility + risk + cost + diagrams)
    4: 25,  # Implementation (sprint-planning + diagrams)
    5: 20,  # Marketing (marketing-campaign + diagrams)
    6: 10,  # Review (plan-review)
}

# Phase names for display
PHASE_NAMES = {
    1: "Market Research & Competitive Analysis",
    2: "Architecture & Technical Design",
    3: "Feasibility, Costs & Risk Assessment",
    4: "Implementation Planning & Sprints",
    5: "Go-to-Market Strategy & Marketing",
    6: "Plan Review & Synthesis"
}


def analyze_revision_impact(phase_num: int) -> Dict:
    """
    Analyze the impact of revising a specific phase.

    Args:
        phase_num: Phase number being revised (1-6)

    Returns:
        Dictionary with revision impact analysis
    """
    if phase_num < 1 or phase_num > 6:
        raise ValueError(f"Invalid phase number: {phase_num}. Must be 1-6.")

    dependent = DEPENDENT_PHASES[phase_num]

    # Calculate total time including revised phase + all dependents
    total_time = PHASE_TIMES[phase_num] + sum(PHASE_TIMES[p] for p in dependent)

    # Determine cascade recommendation
    # Auto-rerun if ≤2 dependent phases, otherwise ask
    cascade_rec = "auto" if len(dependent) <= 2 else "ask"

    return {
        "revised_phase": phase_num,
        "revised_phase_name": PHASE_NAMES[phase_num],
        "dependent_phases": dependent,
        "dependent_phase_names": [PHASE_NAMES[p] for p in dependent],
        "estimated_time_minutes": total_time,
        "estimated_time_hours": round(total_time / 60, 1),
        "cascade_recommendation": cascade_rec,
        "impact_level": _determine_impact_level(len(dependent)),
        "details": _generate_impact_details(phase_num, dependent)
    }


def _determine_impact_level(num_dependents: int) -> str:
    """Determine impact level based on number of dependent phases."""
    if num_dependents == 0:
        return "none"
    elif num_dependents <= 2:
        return "low"
    elif num_dependents <= 4:
        return "medium"
    else:
        return "high"


def _generate_impact_details(phase_num: int, dependent: List[int]) -> str:
    """Generate human-readable impact description."""
    if not dependent:
        return f"Phase {phase_num} is the final phase. No dependent phases to rerun."

    details = [
        f"Revising Phase {phase_num} ({PHASE_NAMES[phase_num]}) will affect {len(dependent)} downstream phase(s):",
        ""
    ]

    for dep_phase in dependent:
        dep_name = PHASE_NAMES[dep_phase]
        dep_time = PHASE_TIMES[dep_phase]
        reason = _get_dependency_reason(phase_num, dep_phase)
        details.append(f"  • Phase {dep_phase} ({dep_name}) - {dep_time} min")
        details.append(f"    Reason: {reason}")
        details.append("")

    return "\n".join(details)


def _get_dependency_reason(revised_phase: int, dependent_phase: int) -> str:
    """Explain why dependent_phase depends on revised_phase."""
    reasons = {
        (1, 2): "Architecture decisions based on market research findings",
        (1, 3): "Feasibility analysis uses market size and target audience",
        (1, 4): "Implementation plan targets specific market segments",
        (1, 5): "Marketing strategy based on market research insights",
        (1, 6): "Review validates against market research conclusions",

        (2, 3): "Feasibility and costs depend on architectural choices",
        (2, 4): "Implementation plan builds the defined architecture",
        (2, 6): "Review validates architectural decisions",

        (3, 4): "Sprint planning incorporates feasibility constraints and costs",
        (3, 6): "Review validates feasibility conclusions",

        (4, 5): "Marketing strategy aligns with implementation timeline",
        (4, 6): "Review validates implementation approach",

        (5, 6): "Review validates marketing strategy",
    }

    return reasons.get((revised_phase, dependent_phase), "Downstream dependency")


def check_plan_completeness(plan_dir: Path) -> Dict:
    """
    Check which phases have been completed in a plan.

    Args:
        plan_dir: Path to planning output directory

    Returns:
        Dictionary with completion status
    """
    completed_phases = []

    for phase_num in range(1, 7):
        # Check for phase directory
        phase_patterns = [
            f"0{phase_num}_market_research",
            f"0{phase_num}_architecture",
            f"0{phase_num}_feasibility",
            f"0{phase_num}_implementation",
            f"0{phase_num}_go_to_market",
            f"0{phase_num}_review"
        ]

        for pattern in phase_patterns:
            phase_path = plan_dir / pattern
            if phase_path.exists() and phase_path.is_dir():
                completed_phases.append(phase_num)
                break

    return {
        "plan_directory": str(plan_dir),
        "completed_phases": sorted(set(completed_phases)),
        "last_completed_phase": max(completed_phases) if completed_phases else 0,
        "total_phases_completed": len(completed_phases)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze phase dependencies for revision planning"
    )
    parser.add_argument(
        "--phase",
        type=int,
        required=True,
        help="Phase number to analyze (1-6)"
    )
    parser.add_argument(
        "--plan-dir",
        type=Path,
        help="Path to plan directory (optional, for completeness check)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format"
    )

    args = parser.parse_args()

    # Analyze revision impact
    impact = analyze_revision_impact(args.phase)

    # Add plan completeness if directory provided
    if args.plan_dir:
        completeness = check_plan_completeness(args.plan_dir)
        impact["plan_completeness"] = completeness

    # Output
    if args.format == "json":
        print(json.dumps(impact, indent=2))
    else:
        # Text format
        print(f"\n{'='*70}")
        print(f"Revision Impact Analysis: Phase {impact['revised_phase']}")
        print(f"{'='*70}\n")
        print(f"Phase: {impact['revised_phase_name']}")
        print(f"Impact Level: {impact['impact_level'].upper()}")
        print(f"Dependent Phases: {len(impact['dependent_phases'])}")
        print(f"Estimated Time: {impact['estimated_time_minutes']} minutes ({impact['estimated_time_hours']} hours)")
        print(f"Recommendation: {impact['cascade_recommendation'].upper()}")
        print(f"\n{impact['details']}")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
