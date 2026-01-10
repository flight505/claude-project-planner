#!/usr/bin/env python3
"""
Progress Tracker for Claude Project Planner

Manages real-time progress tracking for planning phases.
Creates and updates progress.md with visual progress indicators.

Usage:
    python progress-tracker.py init <project_folder> <plan_type>
    python progress-tracker.py start <project_folder> <phase_num> <activity>
    python progress-tracker.py complete <project_folder> <phase_num>
    python progress-tracker.py activity <project_folder> <activity_text>
    python progress-tracker.py status <project_folder>
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# Phase definitions for each plan type
FULL_PLAN_PHASES = [
    {
        "num": 1,
        "name": "Market Research",
        "skills": [
            "research-lookup",
            "competitive-analysis",
            "market-research-reports",
        ],
        "est_minutes": 30,
    },
    {
        "num": 2,
        "name": "Architecture Design",
        "skills": ["architecture-research", "building-blocks", "project-diagrams"],
        "est_minutes": 45,
    },
    {
        "num": 3,
        "name": "Feasibility & Costs",
        "skills": ["feasibility-analysis", "risk-assessment", "service-cost-analysis"],
        "est_minutes": 30,
    },
    {
        "num": 4,
        "name": "Implementation Planning",
        "skills": ["sprint-planning", "project-diagrams"],
        "est_minutes": 30,
    },
    {
        "num": 5,
        "name": "Go-to-Market",
        "skills": ["marketing-campaign", "project-diagrams"],
        "est_minutes": 30,
    },
    {
        "num": 6,
        "name": "Review & Synthesis",
        "skills": ["plan-review"],
        "est_minutes": 30,
    },
]

TECH_PLAN_PHASES = [
    {
        "num": 1,
        "name": "Architecture Design",
        "skills": ["architecture-research", "building-blocks", "project-diagrams"],
        "est_minutes": 45,
    },
    {
        "num": 2,
        "name": "Feasibility & Costs",
        "skills": ["feasibility-analysis", "risk-assessment", "service-cost-analysis"],
        "est_minutes": 30,
    },
    {
        "num": 3,
        "name": "Implementation Planning",
        "skills": ["sprint-planning", "project-diagrams"],
        "est_minutes": 30,
    },
    {
        "num": 4,
        "name": "Review & Synthesis",
        "skills": ["plan-review"],
        "est_minutes": 30,
    },
]


def get_phases(plan_type: str) -> list:
    """Get phase definitions for plan type."""
    if plan_type == "full":
        return FULL_PLAN_PHASES
    elif plan_type == "tech":
        return TECH_PLAN_PHASES
    else:
        return FULL_PLAN_PHASES


def get_state_path(project_folder: Path) -> Path:
    """Get path to state file."""
    return project_folder / ".progress_state.json"


def load_state(project_folder: Path) -> dict:
    """Load progress state from file."""
    state_path = get_state_path(project_folder)
    if state_path.exists():
        return json.loads(state_path.read_text(encoding="utf-8"))
    return {}


def save_state(project_folder: Path, state: dict) -> None:
    """Save progress state to file."""
    state_path = get_state_path(project_folder)
    state_path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def format_duration(minutes: float) -> str:
    """Format duration in minutes to human readable string."""
    if minutes < 1:
        return "< 1 min"
    elif minutes < 60:
        return f"{int(minutes)} min"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins == 0:
            return f"{hours}h"
        return f"{hours}h {mins}m"


def get_status_icon(status: str) -> str:
    """Get icon for phase status."""
    icons = {
        "pending": "⏳",
        "in_progress": "🔄",
        "completed": "✅",
        "failed": "❌",
        "skipped": "⏭️",
    }
    return icons.get(status, "❓")


def calculate_progress(state: dict) -> dict:
    """Calculate overall progress metrics."""
    phases = state.get("phases", {})
    total = len(phases)
    completed = sum(1 for p in phases.values() if p.get("status") == "completed")
    in_progress = sum(1 for p in phases.values() if p.get("status") == "in_progress")

    # Calculate elapsed time
    start_time = state.get("start_time")
    elapsed_minutes = 0
    if start_time:
        start_dt = datetime.fromisoformat(start_time)
        elapsed_minutes = (datetime.now() - start_dt).total_seconds() / 60

    # Calculate estimated remaining
    remaining_minutes = 0
    for _, phase_data in phases.items():
        if phase_data.get("status") in ["pending", "in_progress"]:
            remaining_minutes += phase_data.get("est_minutes", 30)

    return {
        "total_phases": total,
        "completed_phases": completed,
        "in_progress_phases": in_progress,
        "percentage": int((completed / total) * 100) if total > 0 else 0,
        "elapsed_minutes": elapsed_minutes,
        "remaining_minutes": remaining_minutes,
    }


def generate_progress_md(project_folder: Path, state: dict) -> str:
    """Generate progress.md content."""
    project_name = state.get("project_name", project_folder.name)
    plan_type = state.get("plan_type", "full")
    phases = state.get("phases", {})
    current_activity = state.get("current_activity", "Initializing...")

    progress = calculate_progress(state)

    # Build progress bar
    filled = int(progress["percentage"] / 5)  # 20 chars total
    bar = "█" * filled + "░" * (20 - filled)

    lines = [
        f"# Planning Progress: {project_name}",
        "",
        f"**Plan Type:** {plan_type.title()} Plan",
        f"**Started:** {state.get('start_time', 'N/A')}",
        "",
        "## Overall Progress",
        "",
        "```",
        f"[{bar}] {progress['percentage']}%",
        "```",
        "",
        f"**Phases:** {progress['completed_phases']}/{progress['total_phases']} completed",
        f"**Elapsed:** {format_duration(progress['elapsed_minutes'])}",
        f"**Estimated Remaining:** {format_duration(progress['remaining_minutes'])}",
        "",
        "## Phase Status",
        "",
        "| Phase | Status | Duration | Skills |",
        "|-------|--------|----------|--------|",
    ]

    # Add phase rows
    for phase_num in sorted(phases.keys(), key=int):
        phase = phases[phase_num]
        icon = get_status_icon(phase.get("status", "pending"))
        name = phase.get("name", f"Phase {phase_num}")
        status = phase.get("status", "pending").replace("_", " ").title()

        # Calculate duration for completed phases
        duration = "-"
        if (
            phase.get("status") == "completed"
            and phase.get("start_time")
            and phase.get("end_time")
        ):
            start = datetime.fromisoformat(phase["start_time"])
            end = datetime.fromisoformat(phase["end_time"])
            dur_mins = (end - start).total_seconds() / 60
            duration = format_duration(dur_mins)
        elif phase.get("status") == "in_progress" and phase.get("start_time"):
            start = datetime.fromisoformat(phase["start_time"])
            dur_mins = (datetime.now() - start).total_seconds() / 60
            duration = f"{format_duration(dur_mins)} (running)"

        skills = ", ".join(phase.get("skills", [])[:2])
        if len(phase.get("skills", [])) > 2:
            skills += "..."

        lines.append(
            f"| {icon} {phase_num}. {name} | {status} | {duration} | {skills} |"
        )

    # Add current activity section
    lines.extend(
        [
            "",
            "## Current Activity",
            "",
            f"> {current_activity}",
            "",
            "---",
            f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        ]
    )

    return "\n".join(lines)


def write_progress_md(project_folder: Path, state: dict) -> None:
    """Write progress.md file."""
    content = generate_progress_md(project_folder, state)
    progress_path = project_folder / "progress.md"
    progress_path.write_text(content, encoding="utf-8")


def cmd_init(
    project_folder: Path, plan_type: str, project_name: Optional[str] = None
) -> None:
    """Initialize progress tracking for a project."""
    project_folder.mkdir(parents=True, exist_ok=True)

    phases_def = get_phases(plan_type)
    phases = {}
    for phase in phases_def:
        phases[str(phase["num"])] = {
            "name": phase["name"],
            "status": "pending",
            "skills": phase["skills"],
            "est_minutes": phase["est_minutes"],
            "start_time": None,
            "end_time": None,
        }

    state = {
        "project_name": project_name or project_folder.name,
        "plan_type": plan_type,
        "start_time": datetime.now().isoformat(),
        "phases": phases,
        "current_activity": "Planning initialized. Starting Phase 1...",
    }

    save_state(project_folder, state)
    write_progress_md(project_folder, state)
    print(f"✓ Progress tracking initialized for {plan_type} plan")


def cmd_start(
    project_folder: Path, phase_num: int, activity: Optional[str] = None
) -> None:
    """Mark a phase as started."""
    state = load_state(project_folder)
    phase_key = str(phase_num)

    if phase_key not in state.get("phases", {}):
        print(f"Error: Phase {phase_num} not found", file=sys.stderr)
        sys.exit(1)

    state["phases"][phase_key]["status"] = "in_progress"
    state["phases"][phase_key]["start_time"] = datetime.now().isoformat()

    phase_name = state["phases"][phase_key]["name"]
    state["current_activity"] = activity or f"Executing Phase {phase_num}: {phase_name}"

    save_state(project_folder, state)
    write_progress_md(project_folder, state)
    print(f"✓ Phase {phase_num} ({phase_name}) started")


def cmd_complete(project_folder: Path, phase_num: int) -> None:
    """Mark a phase as completed."""
    state = load_state(project_folder)
    phase_key = str(phase_num)

    if phase_key not in state.get("phases", {}):
        print(f"Error: Phase {phase_num} not found", file=sys.stderr)
        sys.exit(1)

    state["phases"][phase_key]["status"] = "completed"
    state["phases"][phase_key]["end_time"] = datetime.now().isoformat()

    # Update activity to show next phase or completion
    phases = state["phases"]
    next_phase = None
    for p_num in sorted(phases.keys(), key=int):
        if phases[p_num]["status"] == "pending":
            next_phase = phases[p_num]["name"]
            break

    if next_phase:
        state["current_activity"] = (
            f"Phase {phase_num} complete. Preparing {next_phase}..."
        )
    else:
        state["current_activity"] = "All phases complete! Generating final outputs..."

    save_state(project_folder, state)
    write_progress_md(project_folder, state)

    phase_name = state["phases"][phase_key]["name"]
    print(f"✓ Phase {phase_num} ({phase_name}) completed")


def cmd_activity(project_folder: Path, activity_text: str) -> None:
    """Update current activity text."""
    state = load_state(project_folder)
    state["current_activity"] = activity_text
    save_state(project_folder, state)
    write_progress_md(project_folder, state)
    print(f"✓ Activity updated: {activity_text[:50]}...")


def cmd_status(project_folder: Path) -> None:
    """Print current status as JSON."""
    state = load_state(project_folder)
    progress = calculate_progress(state)

    output = {
        "project": state.get("project_name"),
        "plan_type": state.get("plan_type"),
        "progress_percentage": progress["percentage"],
        "completed_phases": progress["completed_phases"],
        "total_phases": progress["total_phases"],
        "elapsed_minutes": round(progress["elapsed_minutes"], 1),
        "remaining_minutes": round(progress["remaining_minutes"], 1),
        "current_activity": state.get("current_activity"),
    }

    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Progress tracker for Claude Project Planner"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize progress tracking")
    init_parser.add_argument("project_folder", type=Path, help="Project output folder")
    init_parser.add_argument("plan_type", choices=["full", "tech"], help="Plan type")
    init_parser.add_argument("--name", type=str, help="Project name")

    # start command
    start_parser = subparsers.add_parser("start", help="Start a phase")
    start_parser.add_argument("project_folder", type=Path, help="Project output folder")
    start_parser.add_argument("phase_num", type=int, help="Phase number")
    start_parser.add_argument("--activity", type=str, help="Activity description")

    # complete command
    complete_parser = subparsers.add_parser("complete", help="Complete a phase")
    complete_parser.add_argument(
        "project_folder", type=Path, help="Project output folder"
    )
    complete_parser.add_argument("phase_num", type=int, help="Phase number")

    # activity command
    activity_parser = subparsers.add_parser("activity", help="Update current activity")
    activity_parser.add_argument(
        "project_folder", type=Path, help="Project output folder"
    )
    activity_parser.add_argument("activity_text", type=str, help="Activity text")

    # status command
    status_parser = subparsers.add_parser("status", help="Get current status as JSON")
    status_parser.add_argument(
        "project_folder", type=Path, help="Project output folder"
    )

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args.project_folder, args.plan_type, args.name)
    elif args.command == "start":
        cmd_start(args.project_folder, args.phase_num, getattr(args, "activity", None))
    elif args.command == "complete":
        cmd_complete(args.project_folder, args.phase_num)
    elif args.command == "activity":
        cmd_activity(args.project_folder, args.activity_text)
    elif args.command == "status":
        cmd_status(args.project_folder)


if __name__ == "__main__":
    main()
