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


class ResearchProgressTracker:
    """
    Track progress of long-running research operations.

    Creates and updates a progress file that external systems can monitor.
    Useful for operations like Gemini Deep Research (60 minutes).
    """

    def __init__(self, project_folder: Path, task_id: str):
        """
        Initialize progress tracker.

        Args:
            project_folder: Root folder for project outputs
            task_id: Unique identifier for this research task
        """
        self.project_folder = Path(project_folder)
        self.task_id = task_id
        self.progress_file = self.project_folder / f".research-progress-{task_id}.json"
        self.start_time: Optional[datetime] = None

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
        phase: str,
        action: str,
        progress_pct: float,
        metadata: Optional[Dict[str, Any]] = None,
        save_checkpoint: bool = False
    ):
        """
        Update progress state with current phase and action.

        Args:
            phase: Current phase name (e.g., "Gathering sources", "Analyzing literature")
            action: Current action description
            progress_pct: Progress percentage (0-100)
            metadata: Optional metadata to include
            save_checkpoint: If True, save this update as a checkpoint in history

        Updates the progress file atomically.
        """
        if not self.progress_file.exists():
            raise FileNotFoundError(
                f"Progress file not found: {self.progress_file}. "
                "Call start() first."
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
