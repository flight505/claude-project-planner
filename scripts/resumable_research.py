"""
Resumable Research Integration - Pattern 5

Integrates checkpoint manager, progress tracker, and error handler to enable
resumable Deep Research operations.

Usage:
    research = ResumableResearchExecutor(project_folder, phase_num)
    result = await research.execute(
        task_name="competitive-analysis",
        query="Analyze competitive landscape",
        provider="gemini_deep_research"
    )

Features:
- Automatic checkpoint detection and resume
- Progress tracking with file updates
- Error handling with retry logic
- Resume prompt generation from checkpoints
- Graceful degradation on failure
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from datetime import datetime

# Import infrastructure modules
from research_checkpoint_manager import ResearchCheckpointManager, ResearchResumeHelper
from research_progress_tracker import ResearchProgressTracker
from research_error_handling import ResearchErrorHandler, ErrorRecoveryStrategy
from research_config import ResearchConfig, DEFAULT_CONFIG


class ResumableResearchExecutor:
    """
    Executor for resumable research operations.

    Combines checkpointing, progress tracking, and error handling to provide
    a complete resumable research experience.
    """

    def __init__(
        self,
        project_folder: Path,
        phase_num: int,
        config: Optional[ResearchConfig] = None,
        auto_resume: bool = True,
        max_checkpoint_age_hours: Optional[int] = None
    ):
        """
        Initialize resumable research executor with configurable settings.

        Args:
            project_folder: Root folder for project outputs
            phase_num: Current phase number
            config: Research configuration (uses DEFAULT_CONFIG if not provided)
            auto_resume: Automatically resume from checkpoints (default: True)
            max_checkpoint_age_hours: Max age for auto-resume (uses config if not provided)
        """
        self.project_folder = Path(project_folder)
        self.phase_num = phase_num
        self.config = config or DEFAULT_CONFIG
        self.auto_resume = auto_resume
        self.max_checkpoint_age_hours = (
            max_checkpoint_age_hours
            if max_checkpoint_age_hours is not None
            else self.config.checkpoint_max_age_hours
        )

        # Initialize managers with config
        self.checkpoint_mgr = ResearchCheckpointManager(project_folder, phase_num, config=self.config)
        self.resume_helper = ResearchResumeHelper(self.checkpoint_mgr)
        self.error_handler = ResearchErrorHandler(
            max_retries=self.config.max_retries,
            base_delay=self.config.base_retry_delay_sec,
            max_delay=self.config.max_retry_delay_sec,
            circuit_breaker_failure_threshold=self.config.circuit_breaker_failure_threshold,
            circuit_breaker_timeout_sec=self.config.circuit_breaker_timeout_sec,
            circuit_breaker_half_open_attempts=self.config.circuit_breaker_half_open_max_calls
        )

        # Statistics
        self.stats = {
            "tasks_executed": 0,
            "tasks_resumed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_time_saved_min": 0
        }

    async def execute(
        self,
        task_name: str,
        query: str,
        provider: str,
        estimated_duration_sec: int = 3600,
        research_func: Optional[Callable] = None,
        fallback_func: Optional[Callable] = None,
        on_progress: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute research with full resumability.

        Args:
            task_name: Unique name for this research task
            query: Research question
            provider: Provider name (gemini_deep_research, perplexity_sonar)
            estimated_duration_sec: Estimated duration (default: 3600 = 60 min)
            research_func: Async function to execute research
            fallback_func: Optional fallback function if primary fails
            on_progress: Optional progress callback

        Returns:
            Research results dictionary

        Raises:
            Exception: If research fails after all retries
        """
        self.stats["tasks_executed"] += 1

        # Check for existing checkpoint
        checkpoint = self.checkpoint_mgr.load_research_checkpoint(task_name)
        resumed = False

        if checkpoint and self.auto_resume:
            # Check if should auto-resume
            should_resume = self.resume_helper.should_auto_resume(
                task_name,
                max_age_hours=self.max_checkpoint_age_hours
            )

            if should_resume:
                print(f"🔄 Resuming from checkpoint ({checkpoint['progress_pct']}%)")
                print(f"   Time saved: {checkpoint['progress_pct'] * estimated_duration_sec / 100 / 60:.0f} minutes")

                # Update query with resume prompt
                query = self.checkpoint_mgr.build_resume_prompt(task_name, checkpoint)
                resumed = True
                self.stats["tasks_resumed"] += 1

                # Update stats
                estimate = self.checkpoint_mgr.get_resume_estimate(checkpoint)
                self.stats["total_time_saved_min"] += estimate["time_saved_min"]

        # Create progress tracker
        task_id = f"{provider}-{task_name}-{int(datetime.now().timestamp())}"
        tracker = ResearchProgressTracker(self.project_folder, task_id)

        # Start tracking
        await tracker.start(
            query=query if not resumed else checkpoint["query"],
            provider=provider,
            estimated_duration_sec=estimated_duration_sec,
            metadata={
                "task_name": task_name,
                "phase_num": self.phase_num,
                "resumed": resumed
            }
        )

        try:
            # Execute with checkpointing and progress
            result = await self._execute_with_checkpoints(
                task_name=task_name,
                query=query,
                estimated_duration_sec=estimated_duration_sec,
                tracker=tracker,
                research_func=research_func,
                fallback_func=fallback_func,
                on_progress=on_progress
            )

            # Mark complete
            await tracker.complete(results=result)

            # Clean up checkpoint on success
            self.checkpoint_mgr.delete_checkpoint(task_name)

            self.stats["tasks_completed"] += 1

            return result

        except Exception as e:
            # Mark failed
            await tracker.fail(str(e), error_type=self.error_handler.classify_error(e).value)

            self.stats["tasks_failed"] += 1

            raise

    async def _execute_with_checkpoints(
        self,
        task_name: str,
        query: str,
        estimated_duration_sec: int,
        tracker: ResearchProgressTracker,
        research_func: Optional[Callable],
        fallback_func: Optional[Callable],
        on_progress: Optional[Callable]
    ) -> Dict[str, Any]:
        """
        Execute research with checkpoint saves during execution.

        This is the core execution loop that periodically checks if
        checkpoints should be created.
        """
        start_time = datetime.now()

        # Get checkpoint schedule from config
        checkpoint_schedule = self.config.get_checkpoint_schedule_tuples()

        last_checkpoint_time = 0

        # Create checkpoint save task that runs periodically
        async def checkpoint_saver():
            nonlocal last_checkpoint_time

            while True:
                # Use configured check interval
                await asyncio.sleep(self.config.checkpoint_check_interval_sec)

                elapsed = (datetime.now() - start_time).total_seconds()

                # Check if we should create a checkpoint
                for target_time, progress_pct, phase, resumable in checkpoint_schedule:
                    if abs(elapsed - target_time) < 60 and elapsed > last_checkpoint_time:
                        # Time to checkpoint!
                        print(f"💾 Checkpoint: {phase} ({progress_pct}%)")

                        # Update progress tracker
                        await tracker.update(
                            phase=phase,
                            action=f"Checkpoint: {phase}",
                            progress_pct=progress_pct,
                            save_checkpoint=True
                        )

                        # Save research checkpoint (now async with atomic writes)
                        await self.checkpoint_mgr.save_research_checkpoint(
                            task_name=task_name,
                            query=query,
                            partial_results={"phase": phase, "progress_pct": progress_pct},
                            sources_collected=[],  # NOTE: Sources unavailable during execution - only known at completion
                            progress_pct=progress_pct,
                            resumable=resumable,
                            metadata={"elapsed_sec": elapsed}
                        )

                        last_checkpoint_time = elapsed
                        break

        # Start checkpoint saver task
        checkpoint_task = asyncio.create_task(checkpoint_saver())

        try:
            # Execute research with error handling
            if research_func:
                # Use provided research function
                if fallback_func:
                    # Execute with graceful degradation
                    result = await ErrorRecoveryStrategy.with_graceful_degradation(
                        primary_func=research_func,
                        fallback_func=fallback_func,
                        error_handler=self.error_handler,
                        on_fallback=lambda e: print(f"⚠️  Falling back: {e}")
                    )
                else:
                    # Execute with retry only
                    result = await self.error_handler.retry_with_backoff(
                        research_func,
                        on_retry=self._create_retry_callback(tracker)
                    )
            else:
                # Default behavior: simulate research
                result = await self._simulate_research(query, estimated_duration_sec)

            return result

        finally:
            # Cancel checkpoint saver
            checkpoint_task.cancel()
            try:
                await checkpoint_task
            except asyncio.CancelledError:
                pass

    async def _simulate_research(self, query: str, duration_sec: int) -> Dict[str, Any]:
        """
        Simulate research for testing purposes.

        In production, this would be replaced with actual research provider calls.
        """
        await asyncio.sleep(min(duration_sec, 10))  # Cap simulation at 10 seconds

        return {
            "query": query,
            "findings": [
                "Simulated finding 1",
                "Simulated finding 2"
            ],
            "sources": [],
            "simulated": True
        }

    def _create_retry_callback(self, tracker: ResearchProgressTracker) -> Callable:
        """Create a retry callback that updates progress."""
        async def on_retry(attempt, max_retries, delay, error_type, error_msg):
            print(f"  ⚠️  Retry {attempt}/{max_retries} after {delay:.1f}s")
            print(f"      Error: {error_msg[:80]}")

            # Update progress tracker
            await tracker.update(
                phase="retry",
                action=f"Retrying after {error_type} error (attempt {attempt})",
                progress_pct=0,
                metadata={"error_type": error_type, "attempt": attempt}
            )

        return on_retry

    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return self.stats.copy()

    def print_resume_summary(self):
        """Print summary of resumable tasks."""
        self.resume_helper.print_resumable_summary()


# Convenience functions for integration

async def execute_resumable_research(
    project_folder: Path,
    phase_num: int,
    task_name: str,
    query: str,
    provider: str = "gemini_deep_research",
    estimated_duration_sec: int = 3600,
    research_func: Optional[Callable] = None,
    fallback_func: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Convenience function to execute resumable research.

    Args:
        project_folder: Root folder for project outputs
        phase_num: Current phase number
        task_name: Unique name for this research task
        query: Research question
        provider: Provider name (default: gemini_deep_research)
        estimated_duration_sec: Estimated duration (default: 3600)
        research_func: Optional research function
        fallback_func: Optional fallback function

    Returns:
        Research results dictionary
    """
    executor = ResumableResearchExecutor(project_folder, phase_num)

    result = await executor.execute(
        task_name=task_name,
        query=query,
        provider=provider,
        estimated_duration_sec=estimated_duration_sec,
        research_func=research_func,
        fallback_func=fallback_func
    )

    return result


# Example usage
async def example_usage():
    """Example of how to use ResumableResearchExecutor."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        project_folder = Path(tmpdir)
        phase_num = 1

        # Create executor
        executor = ResumableResearchExecutor(project_folder, phase_num)

        # Example research function
        async def my_research_func():
            print("Executing research...")
            await asyncio.sleep(2)
            return {
                "findings": ["Finding 1", "Finding 2"],
                "sources": []
            }

        # Example fallback function
        async def my_fallback_func():
            print("Using fallback...")
            await asyncio.sleep(1)
            return {
                "findings": ["Quick finding"],
                "sources": []
            }

        # Execute research
        result = await executor.execute(
            task_name="example-research",
            query="Example research query",
            provider="gemini_deep_research",
            estimated_duration_sec=120,
            research_func=my_research_func,
            fallback_func=my_fallback_func
        )

        print(f"\nResult: {result}")
        print(f"\nStats: {executor.get_stats()}")


if __name__ == "__main__":
    asyncio.run(example_usage())
