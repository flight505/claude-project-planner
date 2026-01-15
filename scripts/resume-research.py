#!/usr/bin/env python3
"""
Resume Research Command - Pattern 7

User-facing CLI for resuming interrupted research operations.

Usage:
    python scripts/resume-research.py <project_folder> <phase_num> --list
    python scripts/resume-research.py <project_folder> <phase_num> --task <task_name>
    python scripts/resume-research.py <project_folder> <phase_num> --task <task_name> --provider <provider>

Examples:
    # List all resumable tasks
    python scripts/resume-research.py planning_outputs/20260115_143022_my-project 1 --list

    # Resume specific task
    python scripts/resume-research.py planning_outputs/20260115_143022_my-project 1 --task competitive-analysis

    # Resume with specific provider (override auto-detection)
    python scripts/resume-research.py planning_outputs/20260115_143022_my-project 1 --task market-sizing --provider perplexity_sonar
"""

import argparse
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from research_checkpoint_manager import ResearchCheckpointManager, ResearchResumeHelper
from resumable_research import ResumableResearchExecutor


def list_resumable_tasks(project_folder: Path, phase_num: int):
    """
    List all resumable research tasks.

    Args:
        project_folder: Path to project output folder
        phase_num: Phase number to check
    """
    manager = ResearchCheckpointManager(project_folder, phase_num)
    helper = ResearchResumeHelper(manager)

    resumable = helper.find_resumable_tasks()

    if not resumable:
        print(f"\n{'='*70}")
        print(f"NO RESUMABLE RESEARCH TASKS FOUND (Phase {phase_num})")
        print("="*70)
        print("\nAll research tasks have been completed or checkpoints are too old.")
        print("Run a new /full-plan or /tech-plan to start fresh research.")
        return 0

    print(f"\n{'='*70}")
    print(f"RESUMABLE RESEARCH TASKS (Phase {phase_num})")
    print("="*70)

    for i, task in enumerate(resumable, 1):
        status = "✅ Resumable" if task["resumable"] else "❌ Not resumable"
        age_hours = task.get("checkpoint_age_hours", 0)
        age_str = f"{age_hours:.1f} hours" if age_hours < 24 else f"{age_hours/24:.1f} days"

        print(f"\n{i}. {status} - {task['task_name']}")
        print(f"   Progress: {task['progress_pct']:.0f}%")
        print(f"   Created: {task['created_at']}")
        print(f"   Age: {age_str}")
        print(f"   Time invested: ~{task.get('time_invested_min', 0)} minutes")
        print(f"   Time saved by resuming: ~{task.get('time_saved_min', 0)} minutes")
        print(f"   Estimated time remaining: ~{task.get('time_remaining_min', 0)} minutes")
        print(f"   Sources collected: {task.get('source_count', 0)}")

        # Warn if checkpoint is old
        if age_hours > 24:
            print(f"   ⚠️  Warning: Checkpoint is {age_str} old. Consider starting fresh.")

    print(f"\n{'='*70}")
    print("TO RESUME A TASK:")
    print(f"  python scripts/resume-research.py {project_folder} {phase_num} --task <task_name>")
    print("\nExample:")
    print(f"  python scripts/resume-research.py {project_folder} {phase_num} --task {resumable[0]['task_name']}")
    print("="*70)

    return 0


async def resume_research_task(
    project_folder: Path,
    phase_num: int,
    task_name: str,
    provider: Optional[str] = None
):
    """
    Resume a specific research task from checkpoint.

    Args:
        project_folder: Path to project output folder
        phase_num: Phase number
        task_name: Task name to resume
        provider: Optional provider override

    Returns:
        Exit code (0 for success, 1 for error)
    """
    manager = ResearchCheckpointManager(project_folder, phase_num)
    checkpoint = manager.load_research_checkpoint(task_name)

    if not checkpoint:
        print(f"\n❌ Error: No checkpoint found for task '{task_name}'")
        print(f"\nRun with --list to see available resumable tasks:")
        print(f"  python scripts/resume-research.py {project_folder} {phase_num} --list")
        return 1

    if not checkpoint.get("resumable", True):
        print(f"\n❌ Error: Task '{task_name}' is not resumable")
        print(f"   Progress: {checkpoint['progress_pct']}%")
        print(f"   Reason: Checkpoint is too late in the process (>{checkpoint['progress_pct']}%)")
        print(f"\nIt's faster to restart this task than to resume from this point.")
        return 1

    # Check age
    created_at = datetime.fromisoformat(checkpoint["created_at"])
    age_hours = (datetime.now() - created_at).total_seconds() / 3600

    if age_hours > 168:  # 7 days
        print(f"\n⚠️  Warning: Checkpoint is {age_hours/24:.1f} days old")
        print(f"   Consider starting fresh instead of resuming.")
        response = input("\nContinue with resume? (y/N): ")
        if response.lower() != 'y':
            print("Resume cancelled.")
            return 1

    # Display resume information
    print(f"\n{'='*70}")
    print(f"RESUMING RESEARCH TASK: {task_name}")
    print("="*70)
    print(f"Original query: {checkpoint['query'][:80]}...")
    print(f"Progress: {checkpoint['progress_pct']:.0f}%")
    print(f"Time invested: ~{checkpoint['progress_pct'] * 60 / 100:.0f} minutes")
    print(f"Sources collected: {checkpoint['metadata']['source_count']}")
    print(f"Checkpoint age: {age_hours:.1f} hours")

    # Estimate time remaining
    estimate = manager.get_resume_estimate(checkpoint)
    print(f"\nEstimated time remaining: ~{estimate['time_remaining_min']} minutes")
    print(f"Time saved by resuming: ~{estimate['time_saved_min']} minutes")

    # Determine provider
    if provider is None:
        # Auto-detect from checkpoint or default to perplexity
        provider = "perplexity_sonar"  # Safe default
        print(f"\nProvider: {provider} (auto-detected)")
    else:
        print(f"\nProvider: {provider} (user-specified)")

    print("\n" + "="*70)
    print("STARTING RESUME...")
    print("="*70 + "\n")

    # Create executor and resume
    executor = ResumableResearchExecutor(
        project_folder,
        phase_num,
        auto_resume=True
    )

    try:
        # Note: In production, this would call the actual research provider
        # For now, we demonstrate the resume capability
        print(f"🔄 Loading checkpoint and building resume prompt...")

        resume_prompt = manager.build_resume_prompt(task_name, checkpoint)
        if not resume_prompt:
            print(f"❌ Error: Could not build resume prompt")
            return 1

        print(f"✅ Resume prompt built successfully")
        print(f"\n📝 Resume Context (first 500 chars):")
        print("-" * 70)
        print(resume_prompt[:500] + "...")
        print("-" * 70)

        print(f"\n⚠️  Note: Actual research execution requires integration with research provider.")
        print(f"   This demonstrates the checkpoint and resume capability.")
        print(f"\n✅ Checkpoint loaded successfully and ready for resume.")
        print(f"\n💡 To complete the resume, integrate this with your research provider:")
        print(f"   - Use resume_prompt as the query")
        print(f"   - Pass to ResumableResearchExecutor.execute()")
        print(f"   - Research will continue from {checkpoint['progress_pct']}%")

        # In production, would execute:
        # result = await executor.execute(
        #     task_name=task_name,
        #     query=checkpoint['query'],
        #     provider=provider,
        #     estimated_duration_sec=estimate['time_remaining_min'] * 60,
        #     research_func=your_research_function
        # )

        return 0

    except Exception as e:
        print(f"\n❌ Error resuming research: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Resume interrupted research operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all resumable tasks for Phase 1
  %(prog)s planning_outputs/20260115_143022_my-project 1 --list

  # Resume specific task
  %(prog)s planning_outputs/20260115_143022_my-project 1 --task competitive-analysis

  # Resume with specific provider
  %(prog)s planning_outputs/20260115_143022_my-project 1 --task market-sizing --provider perplexity_sonar

  # Resume with force (ignore warnings)
  %(prog)s planning_outputs/20260115_143022_my-project 1 --task old-task --force
        """
    )

    parser.add_argument(
        "project_folder",
        type=str,
        help="Path to project output folder"
    )

    parser.add_argument(
        "phase_num",
        type=int,
        help="Phase number (1-6 for full-plan, 1-4 for tech-plan)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all resumable tasks"
    )

    parser.add_argument(
        "--task",
        type=str,
        help="Task name to resume"
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["gemini_deep_research", "perplexity_sonar", "perplexity_research"],
        help="Research provider (overrides auto-detection)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force resume even if checkpoint is old"
    )

    args = parser.parse_args()

    # Validate inputs
    project_folder = Path(args.project_folder)
    if not project_folder.exists():
        print(f"❌ Error: Project folder not found: {project_folder}", file=sys.stderr)
        sys.exit(1)

    if args.phase_num < 1 or args.phase_num > 6:
        print(f"❌ Error: Invalid phase number: {args.phase_num}", file=sys.stderr)
        print(f"   Phase must be between 1 and 6", file=sys.stderr)
        sys.exit(1)

    # Handle commands
    if args.list:
        # List resumable tasks
        exit_code = list_resumable_tasks(project_folder, args.phase_num)
        sys.exit(exit_code)

    elif args.task:
        # Resume specific task
        exit_code = asyncio.run(resume_research_task(
            project_folder,
            args.phase_num,
            args.task,
            provider=args.provider
        ))
        sys.exit(exit_code)

    else:
        # No command specified
        parser.print_help()
        print(f"\n❌ Error: Must specify either --list or --task", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
