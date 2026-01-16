#!/usr/bin/env python3
"""
Background Cleanup Script for Research Files

Removes old progress files and checkpoints to prevent accumulation.

Usage:
    python scripts/cleanup_research_files.py <project_folder> --max-age-days 7
    python scripts/cleanup_research_files.py planning_outputs/20260115_143022_my-project

Examples:
    # Clean up files older than 7 days (default)
    python scripts/cleanup_research_files.py planning_outputs/20260115_143022_my-project

    # Clean up files older than 14 days
    python scripts/cleanup_research_files.py planning_outputs/20260115_143022_my-project --max-age-days 14

    # Dry run - show what would be deleted without actually deleting
    python scripts/cleanup_research_files.py planning_outputs/20260115_143022_my-project --dry-run
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from research_progress_tracker import ResearchProgressTracker
from research_checkpoint_manager import ResearchCheckpointManager


def cleanup_old_files(
    project_folder: Path,
    max_age_days: int,
    dry_run: bool = False
) -> dict:
    """
    Clean up old progress files and checkpoints.

    Args:
        project_folder: Root folder for project outputs
        max_age_days: Maximum age in days before deletion
        dry_run: If True, show what would be deleted without deleting

    Returns:
        Dictionary with cleanup statistics
    """
    project_folder = Path(project_folder)

    if not project_folder.exists():
        print(f"❌ Error: Project folder not found: {project_folder}")
        return {"error": "folder_not_found"}

    print(f"\n{'='*70}")
    print(f"CLEANUP RESEARCH FILES")
    print("="*70)
    print(f"Project folder: {project_folder}")
    print(f"Max age: {max_age_days} days")
    print(f"Mode: {'DRY RUN (no files will be deleted)' if dry_run else 'LIVE'}")
    print("="*70 + "\n")

    total_deleted_progress = 0
    total_deleted_checkpoints = 0

    if dry_run:
        # Dry run: count files that would be deleted
        cutoff = datetime.now() - timedelta(days=max_age_days)

        # Count old progress files
        for progress_file in project_folder.glob(".research-progress-*.json"):
            try:
                mtime = datetime.fromtimestamp(progress_file.stat().st_mtime)
                if mtime < cutoff:
                    age_days = (datetime.now() - mtime).days
                    print(f"  Would delete progress file: {progress_file.name} (age: {age_days} days)")
                    total_deleted_progress += 1
            except OSError:
                continue

        # Count old checkpoints
        for phase_num in range(1, 7):
            manager = ResearchCheckpointManager(project_folder, phase_num)
            checkpoint_dir = manager.checkpoint_dir

            if not checkpoint_dir.exists():
                continue

            for checkpoint_file in checkpoint_dir.glob("*.json"):
                try:
                    mtime = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
                    if mtime < cutoff:
                        age_days = (datetime.now() - mtime).days
                        print(f"  Would delete checkpoint: {checkpoint_file.name} (age: {age_days} days)")
                        total_deleted_checkpoints += 1
                except OSError:
                    continue

        print(f"\n{'='*70}")
        print("DRY RUN SUMMARY")
        print("="*70)
        print(f"Progress files that would be deleted: {total_deleted_progress}")
        print(f"Checkpoints that would be deleted: {total_deleted_checkpoints}")
        print(f"\nRun without --dry-run to actually delete these files.")
        print("="*70)

    else:
        # Live cleanup
        print("Cleaning up old progress files...")
        deleted_progress = ResearchProgressTracker.cleanup_old_progress_files(
            project_folder,
            max_age_days=max_age_days
        )
        total_deleted_progress = deleted_progress
        print(f"  ✅ Deleted {deleted_progress} progress file(s)")

        print("\nCleaning up old checkpoints...")
        for phase_num in range(1, 7):
            manager = ResearchCheckpointManager(project_folder, phase_num)
            deleted = manager.cleanup_old_checkpoints(max_age_days=max_age_days)
            if deleted > 0:
                print(f"  ✅ Phase {phase_num}: Deleted {deleted} checkpoint(s)")
                total_deleted_checkpoints += deleted

        print(f"\n{'='*70}")
        print("CLEANUP COMPLETE")
        print("="*70)
        print(f"Progress files deleted: {total_deleted_progress}")
        print(f"Checkpoints deleted: {total_deleted_checkpoints}")
        print(f"Total files deleted: {total_deleted_progress + total_deleted_checkpoints}")
        print("="*70)

    return {
        "progress_files_deleted": total_deleted_progress,
        "checkpoints_deleted": total_deleted_checkpoints,
        "total_deleted": total_deleted_progress + total_deleted_checkpoints,
        "dry_run": dry_run
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean up old research progress files and checkpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clean up files older than 7 days (default)
  %(prog)s planning_outputs/20260115_143022_my-project

  # Clean up files older than 14 days
  %(prog)s planning_outputs/20260115_143022_my-project --max-age-days 14

  # Dry run (show what would be deleted)
  %(prog)s planning_outputs/20260115_143022_my-project --dry-run
        """
    )

    parser.add_argument(
        "project_folder",
        type=Path,
        help="Path to project output folder"
    )

    parser.add_argument(
        "--max-age-days",
        type=int,
        default=7,
        help="Maximum age in days before deletion (default: 7)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )

    args = parser.parse_args()

    # Validate max_age_days
    if args.max_age_days < 1:
        print(f"❌ Error: --max-age-days must be at least 1 day", file=sys.stderr)
        sys.exit(1)

    # Run cleanup
    result = cleanup_old_files(
        args.project_folder,
        args.max_age_days,
        dry_run=args.dry_run
    )

    # Exit with error code if folder not found
    if result.get("error") == "folder_not_found":
        sys.exit(1)

    # Exit with 0 on success
    sys.exit(0)


if __name__ == "__main__":
    main()
