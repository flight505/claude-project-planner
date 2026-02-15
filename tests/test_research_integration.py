"""
Integration tests for research operations with progress tracking.

Tests end-to-end flows combining all three patterns:
- Pattern 1: Streaming progress
- Pattern 2: Progress file tracking
- Pattern 3: Error handling with retry
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from research_progress_tracker import ResearchProgressTracker
from research_error_handling import ResearchErrorHandler, ErrorRecoveryStrategy


class TestDeepResearchProgressFileIntegration:
    """
    Integration tests for Deep Research with progress file tracking.

    Tests Pattern 2 (progress files) combined with Pattern 3 (error handling).
    """

    @pytest.mark.asyncio
    async def test_deep_research_with_progress_file(self):
        """
        Test Deep Research operation with progress file updates.

        Simulates a long-running research task with periodic progress updates.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "dr-test-123"

            # Create tracker
            tracker = ResearchProgressTracker(project_folder, task_id)

            # Start research
            await tracker.start(
                query="Competitive analysis for AI agents",
                provider="gemini_deep_research",
                estimated_duration_sec=3600
            )

            # Verify progress file exists
            assert tracker.progress_file.exists()

            # Simulate progress updates at checkpoints
            checkpoints = [
                (15, "Gathering sources", "Searching academic databases..."),
                (30, "Analyzing literature", "Reviewing 25 papers..."),
                (50, "Cross-referencing", "Comparing frameworks..."),
            ]

            for pct, phase, action in checkpoints:
                await tracker.update(phase, action, pct, save_checkpoint=True)
                await asyncio.sleep(0.1)  # Small delay to simulate work

                # Verify progress file is updated
                progress = tracker.read_progress()
                assert progress["progress_pct"] == pct
                assert progress["phase"] == phase
                assert progress["current_action"] == action

            # Verify checkpoint history
            progress = tracker.read_progress()
            assert len(progress["checkpoints"]) == 3

            # Complete research
            await tracker.complete(results={"findings": "Comprehensive analysis complete"})

            # Verify completion
            final = tracker.read_progress()
            assert final["status"] == "completed"
            assert final["progress_pct"] == 100
            assert "results" in final

    @pytest.mark.asyncio
    async def test_deep_research_with_failure_and_retry(self):
        """
        Test Deep Research with failure and retry using error handler.

        Combines Pattern 2 (progress) and Pattern 3 (error handling).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "dr-retry-test-123"

            tracker = ResearchProgressTracker(project_folder, task_id)
            handler = ResearchErrorHandler(max_retries=3, base_delay=0.1)

            # Start research
            await tracker.start(
                query="Test research",
                provider="gemini_deep_research",
                estimated_duration_sec=3600
            )

            # Simulate research function that fails then succeeds
            attempt_count = [0]

            async def research_with_transient_failure():
                attempt_count[0] += 1

                # Update progress
                await tracker.update(
                    phase=f"attempt_{attempt_count[0]}",
                    action=f"Research attempt {attempt_count[0]}",
                    progress_pct=25.0
                )

                # First two attempts fail
                if attempt_count[0] <= 2:
                    raise asyncio.TimeoutError("Transient network error")

                # Third attempt succeeds
                return {"findings": "Research complete"}

            # Track retry events
            retry_events = []

            async def on_retry(attempt, max_retries, delay, error_type, error_msg):
                retry_events.append({
                    "attempt": attempt,
                    "error_type": error_type
                })

            # Execute with retry
            result = await handler.retry_with_backoff(
                research_with_transient_failure,
                on_retry=on_retry
            )

            # Verify success
            assert result["findings"] == "Research complete"
            assert attempt_count[0] == 3
            assert len(retry_events) == 2  # Failed twice, then succeeded

            # Mark complete
            await tracker.complete(results=result)

            # Verify final state
            progress = tracker.read_progress()
            assert progress["status"] == "completed"


class TestGracefulDegradationIntegration:
    """
    Integration tests for graceful degradation (Deep Research → Perplexity).

    Tests the full error recovery flow using ErrorRecoveryStrategy.
    """

    @pytest.mark.asyncio
    async def test_deep_research_fallback_to_perplexity(self):
        """
        Test Deep Research falling back to Perplexity on failure.

        Simulates Deep Research quota exceeded, falling back to Perplexity.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            # Track which provider was used
            provider_used = []

            async def deep_research_func():
                provider_used.append("deep_research")

                # Create tracker for Deep Research
                tracker = ResearchProgressTracker(project_folder, "dr-task-123")
                await tracker.start(
                    "Test query",
                    "gemini_deep_research",
                    estimated_duration_sec=3600
                )

                # Simulate failure
                await tracker.fail("Quota exceeded", error_type="rate_limit")

                raise Exception("Deep Research quota exceeded (rate limit)")

            async def perplexity_func():
                provider_used.append("perplexity")

                # Create tracker for Perplexity
                tracker = ResearchProgressTracker(project_folder, "perplexity-task-123")
                await tracker.start(
                    "Test query",
                    "perplexity_sonar",
                    estimated_duration_sec=30
                )

                # Simulate success
                await tracker.update("research", "Researching...", 50.0)
                await tracker.complete(results={"findings": "Perplexity results"})

                return {"findings": "Perplexity results"}

            fallback_triggered = [False]

            async def on_fallback(error):
                fallback_triggered[0] = True

            # Execute with graceful degradation
            result = await ErrorRecoveryStrategy.with_graceful_degradation(
                primary_func=deep_research_func,
                fallback_func=perplexity_func,
                on_fallback=on_fallback
            )

            # Verify fallback was used
            assert fallback_triggered[0]
            assert "deep_research" in provider_used
            assert "perplexity" in provider_used
            assert result["findings"] == "Perplexity results"

            # Verify both progress files exist
            dr_progress_files = list(project_folder.glob(".research-progress-dr-*.json"))
            perplexity_progress_files = list(project_folder.glob(".research-progress-perplexity-*.json"))

            assert len(dr_progress_files) == 1
            assert len(perplexity_progress_files) == 1

            # Verify Deep Research marked as failed
            dr_progress = json.loads(dr_progress_files[0].read_text())
            assert dr_progress["status"] == "failed"

            # Verify Perplexity marked as completed
            perplexity_progress = json.loads(perplexity_progress_files[0].read_text())
            assert perplexity_progress["status"] == "completed"


class TestFullPlanPhaseIntegration:
    """
    Integration tests simulating full-plan phase execution.

    Tests all three patterns working together in a realistic scenario.
    """

    @pytest.mark.asyncio
    async def test_phase_1_research_tasks_with_progress(self):
        """
        Test Phase 1 research tasks with full progress tracking.

        Simulates multiple research tasks with streaming, progress files,
        and error recovery.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            # Define Phase 1 research tasks
            tasks = [
                {
                    "name": "market-overview",
                    "query": "AI agent market overview",
                    "provider": "perplexity_sonar",
                    "duration": 30
                },
                {
                    "name": "competitive-analysis",
                    "query": "Competitive landscape analysis",
                    "provider": "gemini_deep_research",
                    "duration": 3600
                }
            ]

            completed_tasks = []

            # Execute each task
            for task in tasks:
                task_id = f"{task['provider']}-{task['name']}"
                tracker = ResearchProgressTracker(project_folder, task_id)
                handler = ResearchErrorHandler(max_retries=3, base_delay=0.1)

                # Start tracking
                await tracker.start(
                    task["query"],
                    task["provider"],
                    estimated_duration_sec=task["duration"]
                )

                # Simulate research execution
                async def execute_research():
                    # Simulate progress
                    for pct in [25, 50, 75]:
                        await tracker.update(
                            "research",
                            f"Researching {task['name']}...",
                            pct,
                            save_checkpoint=(pct in [30, 50])
                        )
                        await asyncio.sleep(0.05)

                    return {"findings": f"Results for {task['name']}"}

                # Execute with retry
                result = await handler.retry_with_backoff(execute_research)

                # Mark complete
                await tracker.complete(results=result)

                completed_tasks.append(task["name"])

            # Verify all tasks completed
            assert len(completed_tasks) == 2
            assert "market-overview" in completed_tasks
            assert "competitive-analysis" in completed_tasks

            # Verify progress files exist
            progress_files = list(project_folder.glob(".research-progress-*.json"))
            assert len(progress_files) == 2

            # Verify all marked as completed
            for progress_file in progress_files:
                progress = json.loads(progress_file.read_text())
                assert progress["status"] == "completed"
                assert progress["progress_pct"] == 100


class TestExternalMonitoring:
    """
    Integration tests for external monitoring of research progress.

    Tests the ability to monitor progress from separate processes/terminals.
    """

    @pytest.mark.asyncio
    async def test_monitor_research_from_external_process(self):
        """
        Test monitoring research progress from a separate process.

        Simulates the user running a monitoring script while research executes.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "monitored-task-123"

            tracker = ResearchProgressTracker(project_folder, task_id)

            # Start research
            await tracker.start(
                "Test query",
                "gemini_deep_research",
                estimated_duration_sec=60
            )

            # Simulate research in "background"
            research_task = asyncio.create_task(self._simulate_research(tracker))

            # Monitor progress (simulating external monitoring)
            monitor_events = []

            for _ in range(5):
                await asyncio.sleep(0.2)

                progress = tracker.read_progress()
                if progress:
                    monitor_events.append({
                        "progress_pct": progress["progress_pct"],
                        "phase": progress["phase"],
                        "status": progress["status"]
                    })

            # Wait for research to complete
            await research_task

            # Verify monitoring captured progress
            assert len(monitor_events) > 0

            # Verify progression (progress should increase over time)
            progress_values = [e["progress_pct"] for e in monitor_events]
            # At least some progress values should be different (showing progression)
            assert len(set(progress_values)) > 1

            # Verify final status
            final_progress = tracker.read_progress()
            assert final_progress["status"] == "completed"

    async def _simulate_research(self, tracker: ResearchProgressTracker):
        """Helper to simulate research with progress updates."""
        for pct in [15, 30, 50, 75, 100]:
            await asyncio.sleep(0.15)
            if pct < 100:
                await tracker.update(
                    f"phase_{pct}",
                    f"Working on {pct}%...",
                    pct
                )
            else:
                await tracker.complete(results={"findings": "Complete"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
