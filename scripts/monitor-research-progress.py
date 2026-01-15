#!/usr/bin/env python3
"""
Monitor Research Progress - Pattern 8

External monitoring script for tracking research progress in real-time.

Usage:
    python scripts/monitor-research-progress.py <project_folder> <task_id>
    python scripts/monitor-research-progress.py <project_folder> --list
    python scripts/monitor-research-progress.py <project_folder> <task_id> --follow

Examples:
    # List all active research operations
    python scripts/monitor-research-progress.py planning_outputs/20260115_143022_my-project --list

    # Monitor specific task
    python scripts/monitor-research-progress.py planning_outputs/20260115_143022_my-project dr-competitive-analysis-1736956800

    # Follow mode (tail -f style)
    python scripts/monitor-research-progress.py planning_outputs/20260115_143022_my-project dr-competitive-analysis-1736956800 --follow
"""

import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from research_progress_tracker import ResearchProgressTracker


def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp for display."""
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return iso_timestamp


def get_status_icon(status: str) -> str:
    """Get emoji icon for status."""
    icons = {
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "pending": "⏳"
    }
    return icons.get(status, "❓")


def get_progress_bar(progress_pct: float, width: int = 40) -> str:
    """Generate ASCII progress bar."""
    filled = int(width * progress_pct / 100)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}] {progress_pct:.0f}%"


def print_progress_snapshot(progress: Dict[str, Any], show_checkpoints: bool = False):
    """Print a snapshot of current progress."""
    status = progress.get("status", "unknown")
    status_icon = get_status_icon(status)

    print(f"\n{'='*70}")
    print(f"{status_icon} {status.upper()}")
    print("="*70)

    # Basic info
    print(f"Task ID: {progress.get('task_id', 'unknown')}")
    print(f"Provider: {progress.get('provider', 'unknown')}")
    print(f"Query: {progress.get('query', '')[:60]}...")

    # Progress
    progress_pct = progress.get("progress_pct", 0)
    phase = progress.get("phase", "unknown")
    action = progress.get("current_action", "")

    print(f"\nProgress: {get_progress_bar(progress_pct)}")
    print(f"Phase: {phase}")
    print(f"Action: {action}")

    # Timing
    started_at = progress.get("started_at")
    updated_at = progress.get("updated_at")
    estimated_completion = progress.get("estimated_completion_at")

    if started_at:
        start_time = datetime.fromisoformat(started_at)
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\nElapsed: {format_duration(elapsed)}")

    if updated_at:
        print(f"Last update: {format_timestamp(updated_at)}")

    if estimated_completion and status == "running":
        completion_time = datetime.fromisoformat(estimated_completion)
        remaining = (completion_time - datetime.now()).total_seconds()
        if remaining > 0:
            print(f"Estimated remaining: {format_duration(remaining)}")

    # Checkpoints
    if show_checkpoints:
        checkpoints = progress.get("checkpoints", [])
        if checkpoints:
            print(f"\nCheckpoints ({len(checkpoints)}):")
            for cp in checkpoints[-5:]:  # Show last 5
                timestamp = format_timestamp(cp.get("timestamp", ""))
                phase = cp.get("phase", "")
                pct = cp.get("progress_pct", 0)
                print(f"  [{timestamp}] {phase} ({pct:.0f}%)")

    # Final status details
    if status == "completed":
        completed_at = progress.get("completed_at")
        actual_duration = progress.get("actual_duration_sec", 0)
        if completed_at:
            print(f"\nCompleted: {format_timestamp(completed_at)}")
        if actual_duration:
            print(f"Total duration: {format_duration(actual_duration)}")

    elif status == "failed":
        error = progress.get("error", "Unknown error")
        error_type = progress.get("error_type", "unknown")
        print(f"\nError: {error}")
        print(f"Error type: {error_type}")

    print("="*70)


def monitor_progress_once(project_folder: Path, task_id: str, show_checkpoints: bool = False):
    """Monitor progress once and print status."""
    tracker = ResearchProgressTracker(project_folder, task_id)
    progress = tracker.read_progress()

    if not progress:
        print(f"❌ Error: No progress file found for task '{task_id}'")
        print(f"\nProgress file expected at:")
        print(f"  {tracker.progress_file}")
        print(f"\nRun with --list to see active research operations.")
        return 1

    print_progress_snapshot(progress, show_checkpoints=show_checkpoints)
    return 0


def monitor_progress_follow(project_folder: Path, task_id: str, interval: float = 5.0):
    """Monitor progress continuously (tail -f style)."""
    tracker = ResearchProgressTracker(project_folder, task_id)

    print(f"{'='*70}")
    print(f"MONITORING RESEARCH PROGRESS (Press Ctrl+C to stop)")
    print("="*70)
    print(f"Task ID: {task_id}")
    print(f"Update interval: {interval:.1f}s")
    print(f"Progress file: {tracker.progress_file}")
    print("="*70 + "\n")

    last_update = None
    last_progress_pct = None

    try:
        while True:
            progress = tracker.read_progress()

            if not progress:
                print(f"\r⚠️  Waiting for progress file...", end="", flush=True)
                time.sleep(interval)
                continue

            # Check if updated
            current_update = progress.get("updated_at")
            current_progress = progress.get("progress_pct", 0)

            if current_update != last_update or current_progress != last_progress_pct:
                # Progress changed, print update
                status = progress.get("status", "unknown")
                status_icon = get_status_icon(status)
                phase = progress.get("phase", "unknown")
                action = progress.get("current_action", "")

                timestamp = format_timestamp(current_update or "")
                progress_bar = get_progress_bar(current_progress, width=30)

                print(f"[{timestamp}] {status_icon} {progress_bar} | {phase}: {action[:40]}...")

                last_update = current_update
                last_progress_pct = current_progress

                # Check if done
                if status in ["completed", "failed"]:
                    print(f"\n{'='*70}")
                    if status == "completed":
                        print(f"✅ Research completed successfully!")
                        duration = progress.get("actual_duration_sec", 0)
                        if duration:
                            print(f"Total duration: {format_duration(duration)}")
                    else:
                        print(f"❌ Research failed")
                        error = progress.get("error", "Unknown error")
                        print(f"Error: {error}")
                    print("="*70)
                    break

            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print("Monitoring stopped by user")
        print("="*70)
        return 0

    return 0


def list_active_research(project_folder: Path):
    """List all active research operations."""
    active = ResearchProgressTracker.list_active_research(project_folder)

    if not active:
        print(f"\n{'='*70}")
        print("NO ACTIVE RESEARCH OPERATIONS")
        print("="*70)
        print("\nNo research operations are currently running.")
        print("Start a new research operation with /full-plan or /tech-plan.")
        return 0

    print(f"\n{'='*70}")
    print(f"ACTIVE RESEARCH OPERATIONS ({len(active)})")
    print("="*70)

    for i, progress in enumerate(active, 1):
        status_icon = get_status_icon(progress.get("status", "unknown"))
        task_id = progress.get("task_id", "unknown")
        provider = progress.get("provider", "unknown")
        progress_pct = progress.get("progress_pct", 0)
        phase = progress.get("phase", "unknown")

        started_at = progress.get("started_at")
        elapsed = "unknown"
        if started_at:
            start_time = datetime.fromisoformat(started_at)
            elapsed_sec = (datetime.now() - start_time).total_seconds()
            elapsed = format_duration(elapsed_sec)

        print(f"\n{i}. {status_icon} {task_id}")
        print(f"   Provider: {provider}")
        print(f"   Progress: {get_progress_bar(progress_pct, width=30)}")
        print(f"   Phase: {phase}")
        print(f"   Elapsed: {elapsed}")

    print(f"\n{'='*70}")
    print("TO MONITOR A TASK:")
    print(f"  python scripts/monitor-research-progress.py {project_folder} <task_id>")
    print("\nExample:")
    if active:
        print(f"  python scripts/monitor-research-progress.py {project_folder} {active[0]['task_id']}")
    print("="*70)

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor research progress in real-time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all active research operations
  %(prog)s planning_outputs/20260115_143022_my-project --list

  # Monitor specific task once
  %(prog)s planning_outputs/20260115_143022_my-project dr-task-123

  # Follow mode (continuous monitoring)
  %(prog)s planning_outputs/20260115_143022_my-project dr-task-123 --follow

  # Show checkpoint history
  %(prog)s planning_outputs/20260115_143022_my-project dr-task-123 --checkpoints

  # Follow with custom update interval
  %(prog)s planning_outputs/20260115_143022_my-project dr-task-123 --follow --interval 2
        """
    )

    parser.add_argument(
        "project_folder",
        type=str,
        help="Path to project output folder"
    )

    parser.add_argument(
        "task_id",
        type=str,
        nargs="?",
        help="Task ID to monitor (from progress file name)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all active research operations"
    )

    parser.add_argument(
        "--follow",
        action="store_true",
        help="Follow mode (continuous monitoring like tail -f)"
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Update interval in seconds for follow mode (default: 5.0)"
    )

    parser.add_argument(
        "--checkpoints",
        action="store_true",
        help="Show checkpoint history"
    )

    args = parser.parse_args()

    # Validate inputs
    project_folder = Path(args.project_folder)
    if not project_folder.exists():
        print(f"❌ Error: Project folder not found: {project_folder}", file=sys.stderr)
        sys.exit(1)

    # Handle commands
    if args.list:
        # List active research
        exit_code = list_active_research(project_folder)
        sys.exit(exit_code)

    elif args.task_id:
        # Monitor specific task
        if args.follow:
            # Follow mode
            exit_code = monitor_progress_follow(
                project_folder,
                args.task_id,
                interval=args.interval
            )
        else:
            # One-time snapshot
            exit_code = monitor_progress_once(
                project_folder,
                args.task_id,
                show_checkpoints=args.checkpoints
            )
        sys.exit(exit_code)

    else:
        # No command specified
        parser.print_help()
        print(f"\n❌ Error: Must specify either --list or provide a task_id", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
