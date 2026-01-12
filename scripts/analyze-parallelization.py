#!/usr/bin/env python3
"""
Analyze a completed project plan to determine parallelization opportunities.

This script examines a finished planning output directory and calculates
potential time savings from parallelizing independent tasks. It provides
recommendations for optimal parallelization strategy.

Usage:
    python scripts/analyze-parallelization.py <plan-directory> [--output <file>]

Exit codes:
    0 - Success
    1 - Error (directory not found, invalid structure)
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class TaskInfo:
    """Information about a planning task."""
    skill: str
    phase: int
    estimated_time: int  # minutes
    dependencies: List[str]  # skill names this depends on


@dataclass
class ParallelGroup:
    """Group of tasks that can run in parallel."""
    phase: int
    tasks: List[str]  # skill names
    group_type: str  # "parallel" or "sequential"
    estimated_time: int  # minutes for this group


@dataclass
class AnalysisResult:
    """Complete parallelization analysis."""
    plan_name: str
    total_sequential_time: int  # minutes
    total_parallel_time: int  # minutes
    time_savings_percent: float
    time_savings_minutes: int
    parallel_groups: List[ParallelGroup]
    recommendation: str  # "full", "conservative", "none"
    reasoning: str


# Task definitions with estimated times (in minutes)
TASK_DEFINITIONS = {
    "research-lookup": TaskInfo("research-lookup", 1, 5, []),
    "competitive-analysis": TaskInfo("competitive-analysis", 1, 8, []),
    "market-research-reports": TaskInfo("market-research-reports", 1, 10, ["research-lookup", "competitive-analysis"]),
    "project-diagrams-phase1": TaskInfo("project-diagrams", 1, 5, ["market-research-reports"]),

    "architecture-research": TaskInfo("architecture-research", 2, 15, ["market-research-reports"]),
    "building-blocks": TaskInfo("building-blocks", 2, 12, ["architecture-research"]),
    "project-diagrams-phase2": TaskInfo("project-diagrams", 2, 8, ["building-blocks"]),

    "feasibility-analysis": TaskInfo("feasibility-analysis", 3, 10, ["building-blocks"]),
    "risk-assessment": TaskInfo("risk-assessment", 3, 12, ["building-blocks"]),
    "service-cost-analysis": TaskInfo("service-cost-analysis", 3, 15, ["building-blocks"]),
    "project-diagrams-phase3": TaskInfo("project-diagrams", 3, 5, ["feasibility-analysis", "risk-assessment", "service-cost-analysis"]),

    "sprint-planning": TaskInfo("sprint-planning", 4, 20, ["building-blocks"]),
    "project-diagrams-phase4": TaskInfo("project-diagrams", 4, 5, ["sprint-planning"]),

    "marketing-campaign": TaskInfo("marketing-campaign", 5, 15, ["sprint-planning"]),
    "project-diagrams-phase5": TaskInfo("project-diagrams", 5, 5, ["marketing-campaign"]),

    "plan-review": TaskInfo("plan-review", 6, 10, ["marketing-campaign"]),
}


def detect_completed_tasks(plan_dir: Path) -> List[str]:
    """
    Detect which tasks were completed based on output files.

    Args:
        plan_dir: Path to planning output directory

    Returns:
        List of completed task identifiers
    """
    completed_tasks = []

    # Check Phase 1: Market Research
    if (plan_dir / "01_market_research").exists():
        if (plan_dir / "01_market_research" / "research_data.md").exists():
            completed_tasks.append("research-lookup")
        if (plan_dir / "01_market_research" / "competitive_analysis.md").exists():
            completed_tasks.append("competitive-analysis")
        if (plan_dir / "01_market_research" / "market_overview.md").exists():
            completed_tasks.append("market-research-reports")
        if (plan_dir / "01_market_research" / "diagrams").exists():
            completed_tasks.append("project-diagrams-phase1")

    # Check Phase 2: Architecture
    if (plan_dir / "02_architecture").exists():
        if (plan_dir / "02_architecture" / "architecture_document.md").exists():
            completed_tasks.append("architecture-research")
        if (plan_dir / "02_architecture" / "building_blocks.md").exists():
            completed_tasks.append("building-blocks")
        if (plan_dir / "02_architecture" / "diagrams").exists():
            completed_tasks.append("project-diagrams-phase2")

    # Check Phase 3: Feasibility
    if (plan_dir / "03_feasibility").exists():
        if (plan_dir / "03_feasibility" / "feasibility_analysis.md").exists():
            completed_tasks.append("feasibility-analysis")
        if (plan_dir / "03_feasibility" / "risk_assessment.md").exists():
            completed_tasks.append("risk-assessment")
        if (plan_dir / "03_feasibility" / "service_cost_analysis.md").exists():
            completed_tasks.append("service-cost-analysis")
        if (plan_dir / "03_feasibility" / "diagrams").exists():
            completed_tasks.append("project-diagrams-phase3")

    # Check Phase 4: Implementation
    if (plan_dir / "04_implementation").exists():
        if (plan_dir / "04_implementation" / "sprint_plan.md").exists():
            completed_tasks.append("sprint-planning")
        if (plan_dir / "04_implementation" / "diagrams").exists():
            completed_tasks.append("project-diagrams-phase4")

    # Check Phase 5: Go-to-Market
    if (plan_dir / "05_go_to_market").exists():
        if (plan_dir / "05_go_to_market" / "marketing_campaign.md").exists():
            completed_tasks.append("marketing-campaign")
        if (plan_dir / "05_go_to_market" / "diagrams").exists():
            completed_tasks.append("project-diagrams-phase5")

    # Check Phase 6: Review
    if (plan_dir / "06_review").exists():
        if (plan_dir / "06_review" / "plan_review.md").exists():
            completed_tasks.append("plan-review")

    return completed_tasks


def identify_parallel_groups(completed_tasks: List[str]) -> List[ParallelGroup]:
    """
    Identify groups of tasks that can run in parallel.

    Args:
        completed_tasks: List of completed task identifiers

    Returns:
        List of parallel execution groups
    """
    groups = []

    # Phase 1: research-lookup + competitive-analysis can run parallel
    phase1_parallel = []
    if "research-lookup" in completed_tasks:
        phase1_parallel.append("research-lookup")
    if "competitive-analysis" in completed_tasks:
        phase1_parallel.append("competitive-analysis")

    if phase1_parallel:
        max_time = max(TASK_DEFINITIONS[t].estimated_time for t in phase1_parallel)
        groups.append(ParallelGroup(
            phase=1,
            tasks=phase1_parallel,
            group_type="parallel",
            estimated_time=max_time
        ))

    # Phase 1: Sequential tasks
    phase1_sequential = []
    if "market-research-reports" in completed_tasks:
        phase1_sequential.append("market-research-reports")
    if "project-diagrams-phase1" in completed_tasks:
        phase1_sequential.append("project-diagrams-phase1")

    if phase1_sequential:
        total_time = sum(TASK_DEFINITIONS[t].estimated_time for t in phase1_sequential)
        groups.append(ParallelGroup(
            phase=1,
            tasks=phase1_sequential,
            group_type="sequential",
            estimated_time=total_time
        ))

    # Phase 2: All sequential (architecture has dependencies)
    phase2_tasks = [t for t in completed_tasks if TASK_DEFINITIONS.get(t, TaskInfo("", 0, 0, [])).phase == 2]
    if phase2_tasks:
        total_time = sum(TASK_DEFINITIONS[t].estimated_time for t in phase2_tasks)
        groups.append(ParallelGroup(
            phase=2,
            tasks=phase2_tasks,
            group_type="sequential",
            estimated_time=total_time
        ))

    # Phase 3: feasibility + risk + cost can ALL run parallel (HIGHEST parallelization)
    phase3_parallel = []
    for task in ["feasibility-analysis", "risk-assessment", "service-cost-analysis"]:
        if task in completed_tasks:
            phase3_parallel.append(task)

    if phase3_parallel:
        max_time = max(TASK_DEFINITIONS[t].estimated_time for t in phase3_parallel)
        groups.append(ParallelGroup(
            phase=3,
            tasks=phase3_parallel,
            group_type="parallel",
            estimated_time=max_time
        ))

    # Phase 3: Diagrams (sequential, depends on analysis)
    if "project-diagrams-phase3" in completed_tasks:
        groups.append(ParallelGroup(
            phase=3,
            tasks=["project-diagrams-phase3"],
            group_type="sequential",
            estimated_time=TASK_DEFINITIONS["project-diagrams-phase3"].estimated_time
        ))

    # Phase 4: All sequential
    phase4_tasks = [t for t in completed_tasks if TASK_DEFINITIONS.get(t, TaskInfo("", 0, 0, [])).phase == 4]
    if phase4_tasks:
        total_time = sum(TASK_DEFINITIONS[t].estimated_time for t in phase4_tasks)
        groups.append(ParallelGroup(
            phase=4,
            tasks=phase4_tasks,
            group_type="sequential",
            estimated_time=total_time
        ))

    # Phase 5: All sequential
    phase5_tasks = [t for t in completed_tasks if TASK_DEFINITIONS.get(t, TaskInfo("", 0, 0, [])).phase == 5]
    if phase5_tasks:
        total_time = sum(TASK_DEFINITIONS[t].estimated_time for t in phase5_tasks)
        groups.append(ParallelGroup(
            phase=5,
            tasks=phase5_tasks,
            group_type="sequential",
            estimated_time=total_time
        ))

    # Phase 6: All sequential
    phase6_tasks = [t for t in completed_tasks if TASK_DEFINITIONS.get(t, TaskInfo("", 0, 0, [])).phase == 6]
    if phase6_tasks:
        total_time = sum(TASK_DEFINITIONS[t].estimated_time for t in phase6_tasks)
        groups.append(ParallelGroup(
            phase=6,
            tasks=phase6_tasks,
            group_type="sequential",
            estimated_time=total_time
        ))

    return groups


def calculate_times(completed_tasks: List[str], parallel_groups: List[ParallelGroup]) -> Tuple[int, int]:
    """
    Calculate total sequential and parallel execution times.

    Args:
        completed_tasks: List of completed tasks
        parallel_groups: List of parallel execution groups

    Returns:
        Tuple of (sequential_time, parallel_time) in minutes
    """
    # Sequential time: sum of all tasks
    sequential_time = sum(
        TASK_DEFINITIONS[t].estimated_time
        for t in completed_tasks
        if t in TASK_DEFINITIONS
    )

    # Parallel time: sum of group times (groups already account for parallelization)
    parallel_time = sum(group.estimated_time for group in parallel_groups)

    return sequential_time, parallel_time


def generate_recommendation(
    time_savings_percent: float,
    parallel_groups: List[ParallelGroup]
) -> Tuple[str, str]:
    """
    Generate parallelization recommendation based on analysis.

    Args:
        time_savings_percent: Percentage of time saved
        parallel_groups: List of parallel groups

    Returns:
        Tuple of (recommendation, reasoning)
    """
    # Count how many parallel groups we have
    parallel_count = sum(1 for g in parallel_groups if g.group_type == "parallel")

    if time_savings_percent >= 20:
        return "full", f"Significant time savings ({time_savings_percent:.0f}%) with {parallel_count} parallel task groups. Highly recommended."
    elif time_savings_percent >= 10:
        return "conservative", f"Moderate time savings ({time_savings_percent:.0f}%) with {parallel_count} parallel task groups. Worth considering."
    else:
        return "none", f"Minimal time savings ({time_savings_percent:.0f}%). Sequential execution is fine."


def analyze_plan(plan_dir: Path) -> AnalysisResult:
    """
    Perform complete parallelization analysis on a plan.

    Args:
        plan_dir: Path to planning output directory

    Returns:
        AnalysisResult with complete analysis
    """
    # Get plan name from directory
    plan_name = plan_dir.name

    # Detect completed tasks
    completed_tasks = detect_completed_tasks(plan_dir)

    if not completed_tasks:
        raise ValueError(f"No completed tasks found in {plan_dir}")

    # Identify parallel groups
    parallel_groups = identify_parallel_groups(completed_tasks)

    # Calculate times
    sequential_time, parallel_time = calculate_times(completed_tasks, parallel_groups)

    # Calculate savings
    time_savings_minutes = sequential_time - parallel_time
    time_savings_percent = (time_savings_minutes / sequential_time * 100) if sequential_time > 0 else 0

    # Generate recommendation
    recommendation, reasoning = generate_recommendation(time_savings_percent, parallel_groups)

    return AnalysisResult(
        plan_name=plan_name,
        total_sequential_time=sequential_time,
        total_parallel_time=parallel_time,
        time_savings_percent=time_savings_percent,
        time_savings_minutes=time_savings_minutes,
        parallel_groups=parallel_groups,
        recommendation=recommendation,
        reasoning=reasoning
    )


def format_analysis_text(result: AnalysisResult) -> str:
    """Format analysis result as human-readable text."""
    lines = []

    lines.append("=" * 70)
    lines.append("Parallelization Analysis")
    lines.append("=" * 70)
    lines.append(f"Plan: {result.plan_name}")
    lines.append("")

    lines.append("Time Comparison:")
    lines.append(f"  Sequential execution: {result.total_sequential_time} minutes")
    lines.append(f"  Parallel execution:   {result.total_parallel_time} minutes")
    lines.append(f"  Time savings:         {result.time_savings_minutes} minutes ({result.time_savings_percent:.1f}%)")
    lines.append("")

    lines.append(f"Recommendation: {result.recommendation.upper()}")
    lines.append(f"  {result.reasoning}")
    lines.append("")

    lines.append("Parallel Execution Groups:")
    for group in result.parallel_groups:
        group_desc = "PARALLEL" if group.group_type == "parallel" else "Sequential"
        lines.append(f"  Phase {group.phase} - {group_desc} ({group.estimated_time} min):")
        for task in group.tasks:
            task_time = TASK_DEFINITIONS.get(task, TaskInfo("", 0, 0, [])).estimated_time
            lines.append(f"    - {task} ({task_time} min)")
    lines.append("")

    lines.append("=" * 70)

    return "\n".join(lines)


def format_analysis_json(result: AnalysisResult) -> str:
    """Format analysis result as JSON."""
    data = {
        "plan_name": result.plan_name,
        "sequential_time_minutes": result.total_sequential_time,
        "parallel_time_minutes": result.total_parallel_time,
        "time_savings_minutes": result.time_savings_minutes,
        "time_savings_percent": round(result.time_savings_percent, 1),
        "recommendation": result.recommendation,
        "reasoning": result.reasoning,
        "parallel_groups": [
            {
                "phase": g.phase,
                "type": g.group_type,
                "estimated_time": g.estimated_time,
                "tasks": g.tasks
            }
            for g in result.parallel_groups
        ]
    }

    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze completed project plan for parallelization opportunities"
    )
    parser.add_argument(
        "plan_directory",
        type=Path,
        help="Path to completed planning output directory"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file (default: print to stdout)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of text"
    )

    args = parser.parse_args()

    # Validate directory exists
    if not args.plan_directory.exists():
        print(f"Error: Directory not found: {args.plan_directory}", file=sys.stderr)
        sys.exit(1)

    if not args.plan_directory.is_dir():
        print(f"Error: Not a directory: {args.plan_directory}", file=sys.stderr)
        sys.exit(1)

    # Perform analysis
    try:
        result = analyze_plan(args.plan_directory)
    except Exception as e:
        print(f"Error analyzing plan: {e}", file=sys.stderr)
        sys.exit(1)

    # Format output
    if args.json:
        output = format_analysis_json(result)
    else:
        output = format_analysis_text(result)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✓ Analysis saved to: {args.output}")
    else:
        print(output)

    sys.exit(0)


if __name__ == "__main__":
    main()
