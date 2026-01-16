"""
Research Checkpoint Manager - Patterns 4, 5, 6

Manages fine-grained checkpoints during research operations and enables resume capability.

Usage:
    manager = ResearchCheckpointManager(project_folder, phase_num)
    manager.save_research_checkpoint(task_name, query, partial_results, sources, progress_pct)
    checkpoint = manager.load_research_checkpoint(task_name)
    if checkpoint and checkpoint['resumable']:
        # Resume from checkpoint

Features:
- Fine-grained checkpoints at 15%, 30%, 50% completion
- Resumable research (saves up to 50 minutes of work)
- Resume prompt generation with partial results
- Checkpoint cleanup after successful completion
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Import configuration system
from research_config import ResearchConfig, DEFAULT_CONFIG

# Import structured error system
from research_errors import raise_research_error, wrap_error, ErrorCode, ResearchError


class ResearchCheckpointManager:
    """
    Manage fine-grained checkpoints during research operations.

    Saves intermediate state at strategic points (15%, 30%, 50%) to enable
    resume capability if research is interrupted.
    """

    def __init__(self, project_folder: Path, phase_num: int, config: Optional[ResearchConfig] = None):
        """
        Initialize checkpoint manager with configurable settings.

        Args:
            project_folder: Root folder for project outputs
            phase_num: Current phase number (for organizing checkpoints)
            config: Research configuration (uses DEFAULT_CONFIG if not provided)
        """
        self.project_folder = Path(project_folder)
        self.phase_num = phase_num
        self.config = config or DEFAULT_CONFIG

        # Checkpoint directory structure
        self.state_dir = self.project_folder / ".state"
        self.checkpoint_dir = self.state_dir / "research_checkpoints"
        self.backup_dir = self.state_dir / "backups"

        # Create directories
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Locks for preventing concurrent writes to same task
        self._locks: Dict[str, asyncio.Lock] = {}

    def get_checkpoint_file(self, task_name: str) -> Path:
        """Get checkpoint file path for a task."""
        return self.checkpoint_dir / f"phase{self.phase_num}_{task_name}.json"

    async def save_research_checkpoint(
        self,
        task_name: str,
        query: str,
        partial_results: Dict[str, Any],
        sources_collected: List[Dict],
        progress_pct: float,
        resumable: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Save intermediate research state with atomic writes and concurrency protection.

        Args:
            task_name: Unique name for this research task
            query: Original research query
            partial_results: Results collected so far
            sources_collected: List of sources found
            progress_pct: Current progress percentage
            resumable: Whether this checkpoint can be resumed from
            metadata: Optional additional metadata

        Creates a checkpoint file with all necessary state to resume research.
        Uses asyncio locks to prevent concurrent writes and atomic file operations
        to prevent corruption.
        """
        # Get or create lock for this task
        if task_name not in self._locks:
            self._locks[task_name] = asyncio.Lock()

        async with self._locks[task_name]:
            checkpoint = {
                "version": "1.0",
                "task_name": task_name,
                "phase_num": self.phase_num,
                "query": query,
                "created_at": datetime.now().isoformat(),
                "progress_pct": progress_pct,
                "resumable": resumable,
                "partial_results": partial_results,
                "sources_collected": sources_collected,
                "metadata": {
                    "source_count": len(sources_collected),
                    "partial_content_length": len(str(partial_results)),
                    "checkpoint_reason": self._get_checkpoint_reason(progress_pct)
                }
            }

            # Add custom metadata
            if metadata:
                checkpoint["metadata"].update(metadata)

            checkpoint_json = json.dumps(checkpoint, indent=2)

            # Atomic write to checkpoint file (write to temp, then rename)
            checkpoint_file = self.get_checkpoint_file(task_name)
            temp_checkpoint = checkpoint_file.with_suffix('.tmp')
            temp_checkpoint.write_text(checkpoint_json)
            temp_checkpoint.replace(checkpoint_file)  # Atomic on POSIX systems

            # Also backup to timestamped file (atomic write)
            backup_file = self.backup_dir / f"phase{self.phase_num}_{task_name}_{int(datetime.now().timestamp())}.json"
            temp_backup = backup_file.with_suffix('.tmp')
            temp_backup.write_text(checkpoint_json)
            temp_backup.replace(backup_file)  # Atomic on POSIX systems

    def load_research_checkpoint(self, task_name: str) -> Optional[Dict[str, Any]]:
        """
        Load research checkpoint for a task.

        Args:
            task_name: Unique name for the research task

        Returns:
            Checkpoint dictionary if exists, None otherwise
        """
        checkpoint_file = self.get_checkpoint_file(task_name)

        if not checkpoint_file.exists():
            return None

        try:
            checkpoint = json.loads(checkpoint_file.read_text())
            return checkpoint
        except (json.JSONDecodeError, OSError):
            # Corrupted checkpoint
            return None

    def delete_checkpoint(self, task_name: str):
        """
        Delete checkpoint after successful completion.

        Args:
            task_name: Unique name for the research task
        """
        checkpoint_file = self.get_checkpoint_file(task_name)
        if checkpoint_file.exists():
            checkpoint_file.unlink()

    def list_checkpoints(self, resumable_only: bool = False) -> List[Dict[str, Any]]:
        """
        List all checkpoints for current phase.

        Args:
            resumable_only: If True, only return resumable checkpoints

        Returns:
            List of checkpoint summaries
        """
        checkpoints = []

        for checkpoint_file in self.checkpoint_dir.glob(f"phase{self.phase_num}_*.json"):
            try:
                checkpoint = json.loads(checkpoint_file.read_text())

                # Filter by resumable if requested
                if resumable_only and not checkpoint.get("resumable", True):
                    continue

                summary = {
                    "task_name": checkpoint["task_name"],
                    "progress_pct": checkpoint["progress_pct"],
                    "created_at": checkpoint["created_at"],
                    "resumable": checkpoint.get("resumable", True),
                    "source_count": checkpoint.get("metadata", {}).get("source_count", 0)
                }
                checkpoints.append(summary)

            except (json.JSONDecodeError, OSError):
                # Skip corrupted files
                continue

        # Sort by creation time (newest first)
        checkpoints.sort(key=lambda x: x["created_at"], reverse=True)

        return checkpoints

    def build_resume_prompt(
        self,
        task_name: str,
        checkpoint: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Build a resume prompt from checkpoint data.

        Args:
            task_name: Unique name for the research task
            checkpoint: Optional checkpoint dict (will load if not provided)

        Returns:
            Resume prompt string, or None if no checkpoint exists
        """
        if checkpoint is None:
            checkpoint = self.load_research_checkpoint(task_name)

        if not checkpoint:
            return None

        if not checkpoint.get("resumable", True):
            return None

        # Build resume prompt with context
        resume_prompt = f"""Previous research was interrupted at {checkpoint['progress_pct']}% completion.

**IMPORTANT**: You must CONTINUE this research from where it left off. Do NOT start over from scratch.

## Original Query
{checkpoint['query']}

## Progress Summary
- Checkpoint created: {checkpoint['created_at']}
- Progress: {checkpoint['progress_pct']}%
- Sources collected: {checkpoint['metadata']['source_count']}
- Phase: {self._get_checkpoint_reason(checkpoint['progress_pct'])}

## Partial Results Collected So Far
{json.dumps(checkpoint['partial_results'], indent=2)}

## Sources Already Collected
{self._format_sources(checkpoint['sources_collected'])}

## What to Do Next
Based on the {checkpoint['progress_pct']}% completion:
{self._get_next_steps(checkpoint['progress_pct'])}

Please CONTINUE the research by building on these partial results. Focus on completing the remaining analysis and synthesis. Do not duplicate work already done.
"""

        return resume_prompt

    def should_create_checkpoint(
        self,
        elapsed_sec: float,
        estimated_duration_sec: float
    ) -> tuple[bool, float, str, bool]:
        """
        Determine if a checkpoint should be created.

        Args:
            elapsed_sec: Seconds elapsed since research started
            estimated_duration_sec: Estimated total duration

        Returns:
            Tuple of (should_checkpoint, progress_pct, phase_name, resumable)
        """
        progress_pct = (elapsed_sec / estimated_duration_sec) * 100

        # Get checkpoint schedule from config
        checkpoints = self.config.get_checkpoint_schedule_tuples()

        # Find the appropriate checkpoint
        for target_time, pct, phase, resumable in checkpoints:
            # Check if we've reached this checkpoint
            if abs(elapsed_sec - target_time) < 60:  # Within 1 minute window
                return (True, pct, phase, resumable)

        return (False, progress_pct, "in-progress", True)

    def get_resume_estimate(self, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate time savings from resuming.

        Args:
            checkpoint: Checkpoint dictionary

        Returns:
            Dictionary with time saved and remaining estimates
        """
        progress_pct = checkpoint["progress_pct"]
        created_at = datetime.fromisoformat(checkpoint["created_at"])

        # Estimate original time invested (rough heuristic)
        if progress_pct == 15:
            time_invested_min = 15
            time_remaining_min = 45
        elif progress_pct == 30:
            time_invested_min = 30
            time_remaining_min = 30
        elif progress_pct == 50:
            time_invested_min = 50
            time_remaining_min = 10
        else:
            time_invested_min = 0
            time_remaining_min = 60

        return {
            "time_invested_min": time_invested_min,
            "time_remaining_min": time_remaining_min,
            "time_saved_min": time_invested_min,
            "checkpoint_age_hours": (datetime.now() - created_at).total_seconds() / 3600
        }

    def verify_resume_continuation(
        self,
        task_name: str,
        new_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify that new result continued from checkpoint (not restarted).

        Args:
            task_name: Task name
            new_result: New research result

        Returns:
            Verification report with overlap analysis
        """
        checkpoint = self.load_research_checkpoint(task_name)
        if not checkpoint:
            return {
                'verified': False,
                'reason': 'No checkpoint found',
            }

        # Check for duplicate sources (indicates restart)
        checkpoint_sources = set(
            s.get('url', s.get('title', ''))
            for s in checkpoint.get('sources_collected', [])
            if s.get('url') or s.get('title')
        )
        new_sources = set(
            s.get('url', s.get('title', ''))
            for s in new_result.get('sources', [])
            if s.get('url') or s.get('title')
        )

        overlap = checkpoint_sources & new_sources
        overlap_pct = len(overlap) / max(len(checkpoint_sources), 1) * 100 if checkpoint_sources else 0

        # If >50% overlap, likely restarted
        if overlap_pct > 50:
            return {
                'verified': False,
                'reason': 'High source overlap suggests restart',
                'overlap_pct': overlap_pct,
                'checkpoint_sources': len(checkpoint_sources),
                'new_sources': len(new_sources),
                'overlap_count': len(overlap),
            }

        # Check timestamp progression
        checkpoint_time = datetime.fromisoformat(checkpoint['created_at'])
        result_time = datetime.now()
        elapsed = (result_time - checkpoint_time).total_seconds()

        return {
            'verified': True,
            'overlap_pct': overlap_pct,
            'checkpoint_sources': len(checkpoint_sources),
            'new_sources': len(new_sources),
            'unique_new_sources': len(new_sources - overlap),
            'elapsed_min': elapsed / 60,
            'resumed_successfully': True
        }

    def cleanup_old_checkpoints(self, max_age_hours: Optional[int] = None):
        """
        Clean up old checkpoints.

        Args:
            max_age_hours: Maximum age in hours before deletion (uses config if not provided)
        """
        if max_age_hours is None:
            max_age_hours = self.config.checkpoint_cleanup_interval_hours
        cutoff = datetime.now() - timedelta(hours=max_age_hours)

        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                checkpoint = json.loads(checkpoint_file.read_text())
                created_at = datetime.fromisoformat(checkpoint["created_at"])

                if created_at < cutoff:
                    checkpoint_file.unlink()

            except (json.JSONDecodeError, OSError, KeyError, ValueError):
                # Skip problematic files
                continue

    def _get_checkpoint_reason(self, progress_pct: float) -> str:
        """Get human-readable checkpoint reason."""
        if progress_pct <= 20:
            return "Gathering sources"
        elif progress_pct <= 40:
            return "Analyzing literature"
        elif progress_pct <= 60:
            return "Cross-referencing findings"
        elif progress_pct <= 80:
            return "Synthesizing report"
        else:
            return "Finalizing"

    def _get_next_steps(self, progress_pct: float) -> str:
        """Get next steps based on progress percentage."""
        if progress_pct <= 20:
            return """- Continue gathering additional sources from databases and repositories
- Expand search to related topics and adjacent fields
- Verify source credibility and relevance"""
        elif progress_pct <= 40:
            return """- Complete analysis of collected literature
- Extract key findings and insights
- Identify patterns and trends across sources"""
        elif progress_pct <= 60:
            return """- Cross-reference findings across all sources
- Resolve any contradictions or inconsistencies
- Synthesize a coherent narrative"""
        else:
            return """- Complete the final synthesis
- Generate comprehensive conclusions
- Prepare final report structure"""

    def _format_sources(self, sources: List[Dict]) -> str:
        """Format sources list for resume prompt."""
        if not sources:
            return "No sources collected yet."

        formatted = []
        for i, source in enumerate(sources[:10], 1):  # Limit to first 10
            title = source.get("title", "Untitled")
            url = source.get("url", "")
            formatted.append(f"{i}. {title}\n   {url}")

        if len(sources) > 10:
            formatted.append(f"... and {len(sources) - 10} more sources")

        return "\n".join(formatted)


class ResearchResumeHelper:
    """
    Helper class for resuming interrupted research operations.

    Provides utilities for detecting resumable tasks and executing resume operations.
    """

    def __init__(self, checkpoint_manager: ResearchCheckpointManager):
        """Initialize with a checkpoint manager."""
        self.checkpoint_manager = checkpoint_manager

    def find_resumable_tasks(self) -> List[Dict[str, Any]]:
        """
        Find all resumable research tasks for current phase.

        Returns:
            List of resumable task summaries with time estimates
        """
        checkpoints = self.checkpoint_manager.list_checkpoints(resumable_only=True)

        resumable = []
        for cp_summary in checkpoints:
            # Load full checkpoint for time estimates
            checkpoint = self.checkpoint_manager.load_research_checkpoint(
                cp_summary["task_name"]
            )

            if checkpoint:
                estimates = self.checkpoint_manager.get_resume_estimate(checkpoint)
                cp_summary.update(estimates)
                resumable.append(cp_summary)

        return resumable

    def should_auto_resume(self, task_name: str, max_age_hours: int = 24) -> bool:
        """
        Check if a task should be auto-resumed.

        Args:
            task_name: Task name to check
            max_age_hours: Maximum age for auto-resume (default: 24 hours)

        Returns:
            True if should auto-resume, False otherwise
        """
        checkpoint = self.checkpoint_manager.load_research_checkpoint(task_name)

        if not checkpoint or not checkpoint.get("resumable", True):
            return False

        # Check age
        created_at = datetime.fromisoformat(checkpoint["created_at"])
        age_hours = (datetime.now() - created_at).total_seconds() / 3600

        if age_hours > max_age_hours:
            return False  # Too old, better to restart

        return True

    def print_resumable_summary(self):
        """Print a summary of resumable tasks to console."""
        resumable = self.find_resumable_tasks()

        if not resumable:
            print("No resumable research tasks found.")
            return

        print(f"\n{'='*70}")
        print(f"RESUMABLE RESEARCH TASKS (Phase {self.checkpoint_manager.phase_num})")
        print("="*70)

        for task in resumable:
            status = "✅ Resumable" if task["resumable"] else "❌ Not resumable"
            age = task.get("checkpoint_age_hours", 0)

            print(f"\n{status} - {task['task_name']} ({task['progress_pct']}%)")
            print(f"  Created: {task['created_at']}")
            print(f"  Age: {age:.1f} hours")
            print(f"  Time invested: {task.get('time_invested_min', 0)} minutes")
            print(f"  Time saved by resuming: {task.get('time_saved_min', 0)} minutes")
            print(f"  Estimated time remaining: {task.get('time_remaining_min', 0)} minutes")
            print(f"  Sources collected: {task.get('source_count', 0)}")


# Example usage
async def example_usage():
    """Example of how to use ResearchCheckpointManager."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        project_folder = Path(tmpdir)
        phase_num = 1

        # Create manager
        manager = ResearchCheckpointManager(project_folder, phase_num)

        # Save a checkpoint (now async with atomic writes and locking)
        await manager.save_research_checkpoint(
            task_name="competitive-analysis",
            query="Analyze competitive landscape for AI agents",
            partial_results={
                "findings": ["LangChain is popular", "AutoGPT has many stars"],
                "themes": ["Open source dominance", "Python ecosystem"]
            },
            sources_collected=[
                {"title": "LangChain Docs", "url": "https://langchain.com"},
                {"title": "AutoGPT GitHub", "url": "https://github.com/AutoGPT"}
            ],
            progress_pct=30.0,
            resumable=True
        )

        # Load checkpoint
        checkpoint = manager.load_research_checkpoint("competitive-analysis")
        print(f"Loaded checkpoint: {checkpoint['task_name']} ({checkpoint['progress_pct']}%)")

        # Build resume prompt
        resume_prompt = manager.build_resume_prompt("competitive-analysis", checkpoint)
        print(f"\nResume prompt:\n{resume_prompt[:200]}...")

        # Get resume estimate
        estimate = manager.get_resume_estimate(checkpoint)
        print(f"\nTime saved by resuming: {estimate['time_saved_min']} minutes")

        # List all checkpoints
        helper = ResearchResumeHelper(manager)
        helper.print_resumable_summary()


if __name__ == "__main__":
    asyncio.run(example_usage())
