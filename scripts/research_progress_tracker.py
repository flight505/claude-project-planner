"""
Research Progress Tracker - Pattern 2

Track progress of long-running research operations using progress files.

Usage:
    tracker = ResearchProgressTracker(project_folder, task_id)
    await tracker.start(query, provider, estimated_duration)
    await tracker.update("phase", "action", progress_pct)
    await tracker.complete(results)

Features:
- Progress file with JSON format
- Checkpoint history
- External monitoring support
- Estimated completion time
"""

import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field

# Import state machine for transition validation
from research_state_machine import ResearchTaskStateMachine, ResearchTaskState


@dataclass
class Activity:
    """
    Single research activity with weight.

    Represents a distinct phase of research with a relative weight
    that contributes to overall progress calculation.
    """
    name: str
    weight: float  # 0.0 to 1.0 (must sum to 1.0 across all activities)
    progress_pct: float = 0.0  # Current progress within this activity (0-100)
    started: bool = False
    completed: bool = False


class ActivityBasedProgressTracker:
    """
    Track progress across multiple weighted activities.

    Instead of jumping from 0% → 15% → 30%, this provides granular
    progress by breaking research into weighted activities.

    Example:
        - "Searching sources" (25% weight) at 50% complete = 12.5% overall
        - "Analyzing sources" (35% weight) at 100% complete = 35% overall
        - Total = 47.5% overall progress with sub-activity detail
    """

    def __init__(self, activities: Optional[List[Activity]] = None):
        """
        Initialize activity tracker with default or custom activities.

        Args:
            activities: List of Activity instances (defaults to standard research activities)
        """
        if activities is None:
            # Default activities for research operations
            self.activities = [
                Activity("Searching sources", weight=0.25),
                Activity("Analyzing sources", weight=0.35),
                Activity("Synthesizing findings", weight=0.30),
                Activity("Generating report", weight=0.10),
            ]
        else:
            self.activities = activities

        # Validate weights sum to 1.0
        total_weight = sum(a.weight for a in self.activities)
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point error
            raise ValueError(
                f"Activity weights must sum to 1.0, got {total_weight}. "
                f"Weights: {[a.weight for a in self.activities]}"
            )

    def get_overall_progress(self) -> float:
        """
        Calculate overall progress from weighted activities.

        Returns:
            Progress percentage (0-100) based on weighted activity completion
        """
        total = 0.0
        for activity in self.activities:
            if activity.completed:
                # Activity is fully complete - contribute full weight
                total += activity.weight * 100
            elif activity.started:
                # Activity is in progress - contribute partial weight
                total += activity.weight * activity.progress_pct
        return total

    def update_activity(self, activity_name: str, progress_pct: float):
        """
        Update progress for a specific activity.

        Args:
            activity_name: Name of activity to update
            progress_pct: Progress percentage within this activity (0-100)

        Raises:
            ValueError: If activity_name not found
        """
        for activity in self.activities:
            if activity.name == activity_name:
                activity.started = True
                activity.progress_pct = min(100.0, max(0.0, progress_pct))  # Clamp 0-100

                if activity.progress_pct >= 100:
                    activity.completed = True

                return

        # Activity not found
        raise ValueError(
            f"Activity '{activity_name}' not found. "
            f"Available: {[a.name for a in self.activities]}"
        )

    def get_current_activity(self) -> Optional[Activity]:
        """
        Get currently active activity (started but not completed).

        Returns:
            Current Activity or None if all complete/none started
        """
        for activity in self.activities:
            if activity.started and not activity.completed:
                return activity
        return None

    def get_next_activity(self) -> Optional[Activity]:
        """
        Get next activity that hasn't started yet.

        Returns:
            Next Activity or None if all started
        """
        for activity in self.activities:
            if not activity.started:
                return activity
        return None

    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get summary of all activities and overall progress.

        Returns:
            Dictionary with activity details and overall progress
        """
        return {
            "overall_progress_pct": self.get_overall_progress(),
            "current_activity": self.get_current_activity().name if self.get_current_activity() else None,
            "next_activity": self.get_next_activity().name if self.get_next_activity() else None,
            "activities": [
                {
                    "name": a.name,
                    "weight": a.weight,
                    "progress_pct": a.progress_pct,
                    "started": a.started,
                    "completed": a.completed,
                }
                for a in self.activities
            ]
        }


class ResearchProgressTracker:
    """
    Track progress of long-running research operations.

    Creates and updates a progress file that external systems can monitor.
    Useful for operations like Gemini Deep Research (60 minutes).
    """

    def __init__(self, project_folder: Path, task_id: str, activities: Optional[List[Activity]] = None):
        """
        Initialize progress tracker with state machine validation and activity tracking.

        Args:
            project_folder: Root folder for project outputs
            task_id: Unique identifier for this research task
            activities: Optional custom activities (uses defaults if not provided)
        """
        self.project_folder = Path(project_folder)
        self.task_id = task_id
        self.progress_file = self.project_folder / f".research-progress-{task_id}.json"
        self.start_time: Optional[datetime] = None

        # Initialize state machine for transition validation
        self.state_machine = ResearchTaskStateMachine()

        # Initialize activity-based progress tracking
        self.activity_tracker = ActivityBasedProgressTracker(activities)

    def _get_initial_state(
        self,
        query: str,
        provider: str,
        estimated_duration_sec: int
    ) -> Dict[str, Any]:
        """Create initial progress state."""
        now = datetime.now()

        return {
            "task_id": self.task_id,
            "query": query,
            "provider": provider,
            "status": "running",
            "estimated_duration_sec": estimated_duration_sec,
            "started_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "estimated_completion_at": (
                now + timedelta(seconds=estimated_duration_sec)
            ).isoformat(),
            "phase": "initializing",
            "progress_pct": 0,
            "current_action": "Starting research...",
            "checkpoints": [],
            "metadata": {
                "version": "1.0",
                "created_by": "research_progress_tracker"
            }
        }

    async def start(
        self,
        query: str,
        provider: str,
        estimated_duration_sec: int = 3600,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Start tracking a new research operation.

        Args:
            query: Research question being investigated
            provider: Provider name (e.g., "gemini_deep_research", "perplexity_sonar")
            estimated_duration_sec: Estimated duration in seconds (default: 3600 = 60 min)
            metadata: Optional additional metadata

        Creates a progress file with initial state.
        """
        # Validate state transition
        self.state_machine.transition(ResearchTaskState.RUNNING, "start")

        self.start_time = datetime.now()

        # Ensure project folder exists
        self.project_folder.mkdir(parents=True, exist_ok=True)

        # Create initial state
        state = self._get_initial_state(query, provider, estimated_duration_sec)

        # Add custom metadata if provided
        if metadata:
            state["metadata"].update(metadata)

        # Write progress file
        self.progress_file.write_text(json.dumps(state, indent=2))

    async def update(
        self,
        phase: Optional[str] = None,
        action: Optional[str] = None,
        progress_pct: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        save_checkpoint: bool = False,
        activity_name: Optional[str] = None,
        activity_progress_pct: Optional[float] = None
    ):
        """
        Update progress state with current phase and action.

        Supports two modes:
        1. Direct progress: Pass phase, action, progress_pct directly
        2. Activity-based: Pass activity_name and activity_progress_pct for granular tracking

        Args:
            phase: Current phase name (e.g., "Gathering sources", "Analyzing literature")
            action: Current action description
            progress_pct: Progress percentage (0-100)
            metadata: Optional metadata to include
            save_checkpoint: If True, save this update as a checkpoint in history
            activity_name: Optional activity name for activity-based tracking
            activity_progress_pct: Optional progress within specific activity (0-100)

        Updates the progress file atomically.

        Example (activity-based):
            await tracker.update(
                activity_name="Searching sources",
                activity_progress_pct=50.0
            )
            # Results in overall progress of 12.5% (25% weight * 50%)
        """
        if not self.progress_file.exists():
            raise FileNotFoundError(
                f"Progress file not found: {self.progress_file}. "
                "Call start() first."
            )

        # Activity-based progress calculation
        if activity_name is not None and activity_progress_pct is not None:
            # Update activity tracker
            self.activity_tracker.update_activity(activity_name, activity_progress_pct)

            # Calculate overall progress from activities
            progress_pct = self.activity_tracker.get_overall_progress()

            # Get current activity for phase/action
            current_activity = self.activity_tracker.get_current_activity()
            if current_activity:
                phase = current_activity.name
                action = f"{current_activity.name}: {activity_progress_pct:.0f}%"

        # Validate that we have the required fields
        if phase is None or action is None or progress_pct is None:
            raise ValueError(
                "Must provide either (phase, action, progress_pct) or "
                "(activity_name, activity_progress_pct)"
            )

        # Read current state
        progress = json.loads(self.progress_file.read_text())

        # Update fields
        now = datetime.now()
        progress.update({
            "status": "running",
            "phase": phase,
            "current_action": action,
            "progress_pct": progress_pct,
            "updated_at": now.isoformat(),
        })

        # Add activity tracking status if using activity-based tracking
        if activity_name is not None:
            progress["activity_status"] = self.activity_tracker.get_status_summary()

        # Update estimated completion based on progress
        if self.start_time and progress_pct > 0:
            elapsed = (now - self.start_time).total_seconds()
            estimated_total = elapsed / (progress_pct / 100)
            remaining = estimated_total - elapsed
            estimated_completion = now + timedelta(seconds=remaining)
            progress["estimated_completion_at"] = estimated_completion.isoformat()

        # Add metadata if provided
        if metadata:
            progress.setdefault("metadata", {}).update(metadata)

        # Save checkpoint to history if requested
        if save_checkpoint:
            checkpoint = {
                "timestamp": now.isoformat(),
                "phase": phase,
                "action": action,
                "progress_pct": progress_pct
            }
            progress["checkpoints"].append(checkpoint)

        # Write atomically (write to temp, then rename)
        temp_file = self.progress_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(progress, indent=2))
        temp_file.replace(self.progress_file)

    async def complete(self, results: Optional[Dict[str, Any]] = None):
        """
        Mark research as completed.

        Args:
            results: Optional results dictionary to include

        Updates status to "completed" and records completion time.
        """
        # Validate state transition
        self.state_machine.transition(ResearchTaskState.COMPLETED, "complete")

        if not self.progress_file.exists():
            return  # Already cleaned up or never started

        # Read current state
        progress = json.loads(self.progress_file.read_text())

        # Update to completed
        now = datetime.now()
        duration = (now - self.start_time).total_seconds() if self.start_time else 0

        progress.update({
            "status": "completed",
            "phase": "complete",
            "current_action": "Research complete",
            "progress_pct": 100,
            "updated_at": now.isoformat(),
            "completed_at": now.isoformat(),
            "actual_duration_sec": duration
        })

        # Add results if provided
        if results:
            progress["results"] = results

        # Write final state
        self.progress_file.write_text(json.dumps(progress, indent=2))

    async def fail(self, error: str, error_type: Optional[str] = None):
        """
        Mark research as failed.

        Args:
            error: Error message
            error_type: Optional error type classification

        Updates status to "failed" and records error details.
        """
        # Validate state transition
        self.state_machine.transition(ResearchTaskState.FAILED, "fail")

        if not self.progress_file.exists():
            return  # Already cleaned up or never started

        # Read current state
        progress = json.loads(self.progress_file.read_text())

        # Update to failed
        now = datetime.now()
        duration = (now - self.start_time).total_seconds() if self.start_time else 0

        progress.update({
            "status": "failed",
            "updated_at": now.isoformat(),
            "failed_at": now.isoformat(),
            "actual_duration_sec": duration,
            "error": error,
            "error_type": error_type
        })

        # Write final state
        self.progress_file.write_text(json.dumps(progress, indent=2))

    def read_progress(self) -> Optional[Dict[str, Any]]:
        """
        Read current progress state.

        Returns:
            Progress dictionary if file exists, None otherwise
        """
        if not self.progress_file.exists():
            return None

        return json.loads(self.progress_file.read_text())

    def cleanup(self):
        """
        Delete progress file.

        Call this after successful completion to avoid clutter.
        """
        if self.progress_file.exists():
            self.progress_file.unlink()

    @classmethod
    def list_active_research(cls, project_folder: Path) -> List[Dict[str, Any]]:
        """
        List all active research operations in a project folder.

        Args:
            project_folder: Root folder for project outputs

        Returns:
            List of progress dictionaries for all active research tasks
        """
        project_folder = Path(project_folder)
        active = []

        if not project_folder.exists():
            return []

        # Find all progress files
        for progress_file in project_folder.glob(".research-progress-*.json"):
            try:
                progress = json.loads(progress_file.read_text())
                if progress.get("status") == "running":
                    active.append(progress)
            except (json.JSONDecodeError, OSError):
                # Skip corrupted files
                continue

        return active

    @classmethod
    def cleanup_old_progress_files(cls, project_folder: Path, max_age_days: int = 7):
        """
        Clean up old progress files.

        Args:
            project_folder: Root folder for project outputs
            max_age_days: Maximum age in days (default: 7)

        Removes progress files older than max_age_days.
        """
        project_folder = Path(project_folder)
        cutoff = datetime.now() - timedelta(days=max_age_days)

        for progress_file in project_folder.glob(".research-progress-*.json"):
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(progress_file.stat().st_mtime)
                if mtime < cutoff:
                    progress_file.unlink()
            except OSError:
                # Skip files we can't access
                continue


class ProgressMonitor:
    """
    Monitor progress of a research task.

    Provides convenience methods for checking progress and waiting for completion.
    """

    def __init__(self, tracker: ResearchProgressTracker):
        """Initialize monitor with a tracker."""
        self.tracker = tracker

    def get_status(self) -> Optional[str]:
        """Get current status (running, completed, failed)."""
        progress = self.tracker.read_progress()
        return progress.get("status") if progress else None

    def get_progress_pct(self) -> Optional[float]:
        """Get current progress percentage."""
        progress = self.tracker.read_progress()
        return progress.get("progress_pct") if progress else None

    def get_current_action(self) -> Optional[str]:
        """Get current action description."""
        progress = self.tracker.read_progress()
        return progress.get("current_action") if progress else None

    def get_estimated_remaining_sec(self) -> Optional[float]:
        """
        Get estimated remaining time in seconds.

        Returns:
            Estimated seconds remaining, or None if cannot estimate
        """
        progress = self.tracker.read_progress()
        if not progress:
            return None

        estimated_completion = progress.get("estimated_completion_at")
        if not estimated_completion:
            return None

        try:
            completion_time = datetime.fromisoformat(estimated_completion)
            remaining = (completion_time - datetime.now()).total_seconds()
            return max(0, remaining)  # Don't return negative
        except (ValueError, TypeError):
            return None

    async def wait_for_completion(
        self,
        poll_interval_sec: float = 5.0,
        timeout_sec: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Wait for research to complete.

        Args:
            poll_interval_sec: Seconds between status checks (default: 5)
            timeout_sec: Optional timeout in seconds

        Returns:
            Final progress state

        Raises:
            TimeoutError: If timeout is reached
            Exception: If research fails
        """
        start = datetime.now()

        while True:
            progress = self.tracker.read_progress()

            if not progress:
                raise Exception("Progress file not found")

            status = progress.get("status")

            if status == "completed":
                return progress

            if status == "failed":
                error = progress.get("error", "Unknown error")
                raise Exception(f"Research failed: {error}")

            # Check timeout
            if timeout_sec:
                elapsed = (datetime.now() - start).total_seconds()
                if elapsed >= timeout_sec:
                    raise TimeoutError(
                        f"Research did not complete within {timeout_sec}s"
                    )

            # Wait before next check
            await asyncio.sleep(poll_interval_sec)


# Example usage
async def example_usage():
    """Example of how to use ResearchProgressTracker."""
    import tempfile

    # Create temp project folder
    with tempfile.TemporaryDirectory() as tmpdir:
        project_folder = Path(tmpdir)
        task_id = "dr-example-1736956800"

        # Create tracker
        tracker = ResearchProgressTracker(project_folder, task_id)

        # Start research
        await tracker.start(
            query="What are the latest AI agent frameworks?",
            provider="gemini_deep_research",
            estimated_duration_sec=3600
        )

        # Simulate progress updates
        phases = [
            (15, "Gathering sources", "Searching academic databases..."),
            (30, "Analyzing literature", "Reviewing 25 papers..."),
            (50, "Cross-referencing", "Comparing frameworks..."),
            (75, "Synthesizing", "Generating report..."),
        ]

        for pct, phase, action in phases:
            await tracker.update(phase, action, pct, save_checkpoint=True)
            print(f"[{pct}%] {phase}: {action}")
            await asyncio.sleep(1)

        # Complete
        await tracker.complete(results={"findings": "..."})

        # Read final state
        final = tracker.read_progress()
        print(f"\nCompleted in {final['actual_duration_sec']:.1f}s")

        # List active research
        active = ResearchProgressTracker.list_active_research(project_folder)
        print(f"Active research tasks: {len(active)}")


if __name__ == "__main__":
    asyncio.run(example_usage())
