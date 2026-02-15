#!/usr/bin/env python3
"""
Checkpoint Manager for Claude Project Planner

Manages checkpoints for resuming interrupted planning sessions.
Saves state after each phase completion, enabling resume from last checkpoint.

Usage:
    python checkpoint_manager.py save <project_folder> <phase_num> [--context "context summary"]
    python checkpoint_manager.py load <project_folder>
    python checkpoint_manager.py list [search_path]
    python checkpoint_manager.py status <project_folder>
    python checkpoint_manager.py clear <project_folder>
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


CHECKPOINT_FILE = ".checkpoint.json"
STATE_DIR = ".state"


def get_checkpoint_path(project_folder: Path) -> Path:
    """Get path to checkpoint file."""
    return project_folder / CHECKPOINT_FILE


def get_state_dir(project_folder: Path) -> Path:
    """Get path to state directory."""
    return project_folder / STATE_DIR


def create_checkpoint(
    project_folder: Path,
    phase_num: int,
    plan_type: str = "full",
    project_name: Optional[str] = None,
    context_summary: Optional[str] = None,
    completed_outputs: Optional[list] = None,
) -> dict:
    """Create a checkpoint structure."""
    return {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "project_name": project_name or project_folder.name,
        "project_folder": str(project_folder.absolute()),
        "plan_type": plan_type,
        "last_completed_phase": phase_num,
        "next_phase": phase_num + 1,
        "context_summary": context_summary or "",
        "completed_outputs": completed_outputs or [],
        "phase_history": [],
    }


def save_checkpoint(
    project_folder: Path,
    phase_num: int,
    context_summary: Optional[str] = None,
    key_decisions: Optional[list] = None,
    research_tasks: Optional[dict] = None,
) -> dict:
    """
    Save checkpoint after phase completion.

    Args:
        project_folder: Path to project output folder
        phase_num: Phase number that was just completed
        context_summary: Summary of important context for continuation
        key_decisions: List of key decisions made in this phase
        research_tasks: Optional dict of research task statuses
                       {task_name: "completed"|"failed"|"skipped"}

    Returns:
        The checkpoint data that was saved
    """
    checkpoint_path = get_checkpoint_path(project_folder)
    state_dir = get_state_dir(project_folder)

    # Create state directory
    state_dir.mkdir(parents=True, exist_ok=True)

    # Load existing checkpoint or create new
    if checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        checkpoint["updated_at"] = datetime.now().isoformat()
        checkpoint["last_completed_phase"] = phase_num
        checkpoint["next_phase"] = phase_num + 1
    else:
        # Detect plan type from progress state
        progress_state_path = project_folder / ".progress_state.json"
        plan_type = "full"
        project_name = project_folder.name
        if progress_state_path.exists():
            progress_state = json.loads(progress_state_path.read_text(encoding="utf-8"))
            plan_type = progress_state.get("plan_type", "full")
            project_name = progress_state.get("project_name", project_folder.name)

        checkpoint = create_checkpoint(
            project_folder,
            phase_num,
            plan_type=plan_type,
            project_name=project_name,
        )

    # Update context summary if provided
    if context_summary:
        checkpoint["context_summary"] = context_summary

    # Record phase completion in history
    phase_record = {
        "phase": phase_num,
        "completed_at": datetime.now().isoformat(),
        "key_decisions": key_decisions or [],
    }
    checkpoint.setdefault("phase_history", []).append(phase_record)

    # Track research tasks (NEW in v1.4.0)
    if research_tasks:
        checkpoint.setdefault("research_tasks", {})[f"phase_{phase_num}"] = {
            "tasks": research_tasks,
            "updated_at": datetime.now().isoformat()
        }

    # Collect completed outputs
    completed_outputs = []
    for md_file in project_folder.rglob("*.md"):
        if md_file.name.startswith("."):
            continue
        relative_path = md_file.relative_to(project_folder)
        completed_outputs.append(str(relative_path))
    checkpoint["completed_outputs"] = sorted(completed_outputs)

    # Save phase-specific state
    phase_state_path = state_dir / f"phase{phase_num}_state.json"
    phase_state = {
        "phase": phase_num,
        "saved_at": datetime.now().isoformat(),
        "outputs_created": [
            o for o in completed_outputs if o.startswith(f"0{phase_num}_")
        ],
        "context": context_summary or "",
        "key_decisions": key_decisions or [],
    }
    phase_state_path.write_text(json.dumps(phase_state, indent=2), encoding="utf-8")

    # Save checkpoint
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")

    print(f"✓ Checkpoint saved after Phase {phase_num}")
    print(f"  Location: {checkpoint_path}")
    print(f"  Outputs: {len(completed_outputs)} files")

    return checkpoint


def load_checkpoint(project_folder: Path) -> Optional[dict]:
    """
    Load checkpoint for a project.

    Returns:
        Checkpoint data if exists, None otherwise
    """
    checkpoint_path = get_checkpoint_path(project_folder)

    if not checkpoint_path.exists():
        print(f"No checkpoint found in {project_folder}", file=sys.stderr)
        return None

    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    return checkpoint


def list_checkpoints(search_path: Path = Path("planning_outputs")) -> list:
    """
    List all available checkpoints.

    Args:
        search_path: Path to search for planning outputs

    Returns:
        List of checkpoint summaries
    """
    checkpoints = []

    if not search_path.exists():
        return checkpoints

    for checkpoint_file in search_path.rglob(CHECKPOINT_FILE):
        try:
            checkpoint = json.loads(checkpoint_file.read_text(encoding="utf-8"))
            checkpoints.append(
                {
                    "folder": str(checkpoint_file.parent),
                    "project_name": checkpoint.get("project_name", "Unknown"),
                    "plan_type": checkpoint.get("plan_type", "unknown"),
                    "last_completed_phase": checkpoint.get("last_completed_phase", 0),
                    "next_phase": checkpoint.get("next_phase", 1),
                    "updated_at": checkpoint.get("updated_at", "Unknown"),
                    "total_outputs": len(checkpoint.get("completed_outputs", [])),
                }
            )
        except (json.JSONDecodeError, IOError):
            continue

    # Sort by most recently updated
    checkpoints.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    return checkpoints


def get_status(project_folder: Path) -> dict:
    """
    Get detailed checkpoint status.

    Returns:
        Status dictionary with checkpoint details
    """
    checkpoint = load_checkpoint(project_folder)

    if not checkpoint:
        return {
            "has_checkpoint": False,
            "message": "No checkpoint found",
        }

    # Determine total phases based on plan type
    total_phases = 6 if checkpoint.get("plan_type") == "full" else 4
    completed = checkpoint.get("last_completed_phase", 0)
    remaining = total_phases - completed

    return {
        "has_checkpoint": True,
        "project_name": checkpoint.get("project_name"),
        "plan_type": checkpoint.get("plan_type"),
        "last_completed_phase": completed,
        "next_phase": checkpoint.get("next_phase"),
        "total_phases": total_phases,
        "remaining_phases": remaining,
        "progress_percentage": int((completed / total_phases) * 100),
        "context_summary": checkpoint.get("context_summary", ""),
        "completed_outputs": checkpoint.get("completed_outputs", []),
        "updated_at": checkpoint.get("updated_at"),
        "can_resume": remaining > 0,
    }


def get_research_task_status(project_folder: Path, phase_num: Optional[int] = None) -> dict:
    """
    Get research task statuses from checkpoint.

    Args:
        project_folder: Path to project output folder
        phase_num: Optional phase number (returns all phases if not specified)

    Returns:
        Dictionary of research tasks by phase
    """
    checkpoint = load_checkpoint(project_folder)
    if not checkpoint:
        return {}

    research_tasks = checkpoint.get("research_tasks", {})

    if phase_num is not None:
        return research_tasks.get(f"phase_{phase_num}", {})

    return research_tasks


def has_failed_research_tasks(project_folder: Path, phase_num: int) -> bool:
    """
    Check if a phase has any failed research tasks.

    Args:
        project_folder: Path to project output folder
        phase_num: Phase number to check

    Returns:
        True if there are failed tasks, False otherwise
    """
    phase_tasks = get_research_task_status(project_folder, phase_num)
    tasks = phase_tasks.get("tasks", {})

    return any(status == "failed" for status in tasks.values())


def get_failed_research_tasks(project_folder: Path, phase_num: int) -> list:
    """
    Get list of failed research tasks for a phase.

    Args:
        project_folder: Path to project output folder
        phase_num: Phase number to check

    Returns:
        List of task names that failed
    """
    phase_tasks = get_research_task_status(project_folder, phase_num)
    tasks = phase_tasks.get("tasks", {})

    return [name for name, status in tasks.items() if status == "failed"]


def generate_resume_context(project_folder: Path) -> str:
    """
    Generate context summary for resuming a plan.

    This reads key outputs and creates a context summary that can be used
    to continue planning without losing important decisions.
    """
    checkpoint = load_checkpoint(project_folder)
    if not checkpoint:
        return ""

    context_parts = [
        f"# Resume Context: {checkpoint.get('project_name', 'Unknown Project')}",
        "",
        f"**Plan Type:** {checkpoint.get('plan_type', 'full').title()} Plan",
        f"**Last Completed Phase:** {checkpoint.get('last_completed_phase', 0)}",
        f"**Resume From:** Phase {checkpoint.get('next_phase', 1)}",
        "",
        "## Key Decisions from Previous Phases",
        "",
    ]

    # Extract key decisions from phase history
    for phase_record in checkpoint.get("phase_history", []):
        phase_num = phase_record.get("phase", 0)
        decisions = phase_record.get("key_decisions", [])
        if decisions:
            context_parts.append(f"### Phase {phase_num}")
            for decision in decisions:
                context_parts.append(f"- {decision}")
            context_parts.append("")

    # Add stored context summary
    context_summary = checkpoint.get("context_summary", "")
    if context_summary:
        context_parts.extend(
            [
                "## Context Summary",
                "",
                context_summary,
                "",
            ]
        )

    # Add research task status (NEW in v1.4.0)
    research_tasks = checkpoint.get("research_tasks", {})
    if research_tasks:
        context_parts.extend([
            "## Research Task Status",
            "",
        ])
        for phase_key, phase_data in sorted(research_tasks.items()):
            phase_num = phase_key.replace("phase_", "")
            tasks = phase_data.get("tasks", {})
            if tasks:
                context_parts.append(f"### Phase {phase_num}")
                for task_name, status in tasks.items():
                    status_icon = "✅" if status == "completed" else "❌" if status == "failed" else "⏭️"
                    context_parts.append(f"- {status_icon} {task_name}: {status}")
                context_parts.append("")

    # List completed outputs
    context_parts.extend(
        [
            "## Completed Outputs",
            "",
        ]
    )
    for output in checkpoint.get("completed_outputs", [])[:20]:  # First 20
        context_parts.append(f"- {output}")

    if len(checkpoint.get("completed_outputs", [])) > 20:
        context_parts.append(
            f"- ... and {len(checkpoint['completed_outputs']) - 20} more files"
        )

    return "\n".join(context_parts)


def clear_checkpoint(project_folder: Path) -> bool:
    """
    Clear checkpoint for a project (allows fresh start).

    Returns:
        True if checkpoint was cleared, False if not found
    """
    checkpoint_path = get_checkpoint_path(project_folder)
    state_dir = get_state_dir(project_folder)

    cleared = False

    if checkpoint_path.exists():
        checkpoint_path.unlink()
        cleared = True
        print(f"✓ Checkpoint cleared: {checkpoint_path}")

    if state_dir.exists():
        import shutil

        shutil.rmtree(state_dir)
        cleared = True
        print(f"✓ State directory cleared: {state_dir}")

    if not cleared:
        print("No checkpoint found to clear")

    return cleared


def cmd_save(args):
    """Handle save command."""
    project_folder = Path(args.project_folder)
    if not project_folder.exists():
        print(f"Error: Project folder not found: {project_folder}", file=sys.stderr)
        sys.exit(1)

    key_decisions = None
    if args.decisions:
        key_decisions = [d.strip() for d in args.decisions.split(";")]

    research_tasks = None
    if args.research_tasks:
        # Parse research tasks in format: task1:status1;task2:status2
        research_tasks = {}
        for task_pair in args.research_tasks.split(";"):
            if ":" in task_pair:
                task_name, status = task_pair.split(":", 1)
                research_tasks[task_name.strip()] = status.strip()

    save_checkpoint(
        project_folder,
        args.phase_num,
        context_summary=args.context,
        key_decisions=key_decisions,
        research_tasks=research_tasks,
    )


def cmd_load(args):
    """Handle load command."""
    project_folder = Path(args.project_folder)
    checkpoint = load_checkpoint(project_folder)

    if checkpoint:
        if args.json:
            print(json.dumps(checkpoint, indent=2))
        else:
            print(f"Project: {checkpoint.get('project_name')}")
            print(f"Plan Type: {checkpoint.get('plan_type')}")
            print(f"Last Phase: {checkpoint.get('last_completed_phase')}")
            print(f"Next Phase: {checkpoint.get('next_phase')}")
            print(f"Updated: {checkpoint.get('updated_at')}")
    else:
        sys.exit(1)


def cmd_list(args):
    """Handle list command."""
    search_path = (
        Path(args.search_path) if args.search_path else Path("planning_outputs")
    )
    checkpoints = list_checkpoints(search_path)

    if args.json:
        print(json.dumps(checkpoints, indent=2))
    else:
        if not checkpoints:
            print("No checkpoints found")
            return

        print(f"Found {len(checkpoints)} checkpoint(s):\n")
        for cp in checkpoints:
            total_phases = 6 if cp.get("plan_type") == "full" else 4
            progress = int((cp.get("last_completed_phase", 0) / total_phases) * 100)
            print(f"📁 {cp['project_name']}")
            print(f"   Folder: {cp['folder']}")
            print(
                f"   Plan: {cp['plan_type']} | Phase {cp['last_completed_phase']}/{total_phases} ({progress}%)"
            )
            print(f"   Updated: {cp['updated_at']}")
            print(f"   Files: {cp['total_outputs']}")
            print()


def cmd_status(args):
    """Handle status command."""
    project_folder = Path(args.project_folder)
    status = get_status(project_folder)

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        if not status.get("has_checkpoint"):
            print("No checkpoint found")
            return

        print(f"Project: {status['project_name']}")
        print(f"Plan Type: {status['plan_type'].title()} Plan")
        print(
            f"Progress: {status['progress_percentage']}% ({status['last_completed_phase']}/{status['total_phases']} phases)"
        )
        print(f"Next Phase: {status['next_phase']}")
        print(f"Can Resume: {'Yes' if status['can_resume'] else 'No (complete)'}")
        print(f"Completed Files: {len(status['completed_outputs'])}")

        if status.get("context_summary"):
            print("\nContext Summary:")
            print(f"  {status['context_summary'][:200]}...")


def cmd_context(args):
    """Handle context command - generates resume context."""
    project_folder = Path(args.project_folder)
    context = generate_resume_context(project_folder)

    if context:
        print(context)
    else:
        print("Could not generate resume context", file=sys.stderr)
        sys.exit(1)


def cmd_clear(args):
    """Handle clear command."""
    project_folder = Path(args.project_folder)
    if not clear_checkpoint(project_folder):
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Checkpoint manager for Claude Project Planner"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # save command
    save_parser = subparsers.add_parser(
        "save", help="Save checkpoint after phase completion"
    )
    save_parser.add_argument("project_folder", type=str, help="Project output folder")
    save_parser.add_argument(
        "phase_num", type=int, help="Phase number that was completed"
    )
    save_parser.add_argument(
        "--context", type=str, help="Context summary for continuation"
    )
    save_parser.add_argument(
        "--decisions", type=str, help="Key decisions (semicolon-separated)"
    )
    save_parser.add_argument(
        "--research-tasks", type=str,
        help="Research task statuses (format: task1:status1;task2:status2)"
    )

    # load command
    load_parser = subparsers.add_parser("load", help="Load checkpoint")
    load_parser.add_argument("project_folder", type=str, help="Project output folder")
    load_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # list command
    list_parser = subparsers.add_parser("list", help="List all checkpoints")
    list_parser.add_argument("search_path", nargs="?", type=str, help="Path to search")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # status command
    status_parser = subparsers.add_parser("status", help="Get checkpoint status")
    status_parser.add_argument("project_folder", type=str, help="Project output folder")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # context command
    context_parser = subparsers.add_parser("context", help="Generate resume context")
    context_parser.add_argument(
        "project_folder", type=str, help="Project output folder"
    )

    # clear command
    clear_parser = subparsers.add_parser("clear", help="Clear checkpoint (start fresh)")
    clear_parser.add_argument("project_folder", type=str, help="Project output folder")

    args = parser.parse_args()

    if args.command == "save":
        cmd_save(args)
    elif args.command == "load":
        cmd_load(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "context":
        cmd_context(args)
    elif args.command == "clear":
        cmd_clear(args)


if __name__ == "__main__":
    main()
