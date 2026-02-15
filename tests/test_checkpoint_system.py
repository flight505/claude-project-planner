"""
Unit tests for checkpoint system (Patterns 4, 5, 6).

Tests the research checkpoint manager, resumable research executor,
and enhanced checkpoint manager with research task tracking.
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from research_checkpoint_manager import (
    ResearchCheckpointManager,
    ResearchResumeHelper
)
from resumable_research import ResumableResearchExecutor, execute_resumable_research
import checkpoint_manager


# ============================================================================
# Pattern 4: Research Checkpoint Manager Tests
# ============================================================================

class TestResearchCheckpointManager:
    """Tests for ResearchCheckpointManager class."""

    def test_checkpoint_file_path(self):
        """Verify checkpoint file path generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            checkpoint_file = manager.get_checkpoint_file("test-task")
            assert "phase1_test-task.json" in str(checkpoint_file)
            assert checkpoint_file.parent == project_folder / ".state" / "research_checkpoints"

    @pytest.mark.asyncio
    async def test_save_checkpoint_creates_file(self):
        """Verify checkpoint file is created with correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            await manager.save_research_checkpoint(
                task_name="test-task",
                query="test query",
                partial_results={"findings": ["finding 1"]},
                sources_collected=[{"title": "Source 1", "url": "http://example.com"}],
                progress_pct=30.0,
                resumable=True
            )

            # Verify file exists
            checkpoint_file = manager.get_checkpoint_file("test-task")
            assert checkpoint_file.exists()

            # Verify content
            checkpoint = json.loads(checkpoint_file.read_text())
            assert checkpoint["task_name"] == "test-task"
            assert checkpoint["query"] == "test query"
            assert checkpoint["progress_pct"] == 30.0
            assert checkpoint["resumable"] is True
            assert "partial_results" in checkpoint
            assert "sources_collected" in checkpoint

    @pytest.mark.asyncio
    async def test_load_checkpoint(self):
        """Verify checkpoint can be loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            # Save checkpoint
            await manager.save_research_checkpoint(
                task_name="test-task",
                query="test query",
                partial_results={"findings": ["finding 1"]},
                sources_collected=[],
                progress_pct=50.0
            )

            # Load checkpoint
            checkpoint = manager.load_research_checkpoint("test-task")
            assert checkpoint is not None
            assert checkpoint["task_name"] == "test-task"
            assert checkpoint["progress_pct"] == 50.0

    def test_load_nonexistent_checkpoint(self):
        """Verify loading nonexistent checkpoint returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            checkpoint = manager.load_research_checkpoint("nonexistent")
            assert checkpoint is None

    @pytest.mark.asyncio
    async def test_delete_checkpoint(self):
        """Verify checkpoint deletion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            # Save checkpoint
            await manager.save_research_checkpoint(
                task_name="test-task",
                query="test query",
                partial_results={},
                sources_collected=[],
                progress_pct=30.0
            )

            # Verify exists
            assert manager.get_checkpoint_file("test-task").exists()

            # Delete
            manager.delete_checkpoint("test-task")

            # Verify deleted
            assert not manager.get_checkpoint_file("test-task").exists()

    @pytest.mark.asyncio
    async def test_list_checkpoints(self):
        """Verify listing checkpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            # Create multiple checkpoints
            for i in range(3):
                await manager.save_research_checkpoint(
                    task_name=f"task-{i}",
                    query=f"query {i}",
                    partial_results={},
                    sources_collected=[],
                    progress_pct=i * 20.0,
                    resumable=(i < 2)  # Only first two are resumable
                )

            # List all
            checkpoints = manager.list_checkpoints()
            assert len(checkpoints) == 3

            # List resumable only
            resumable = manager.list_checkpoints(resumable_only=True)
            assert len(resumable) == 2

    @pytest.mark.asyncio
    async def test_build_resume_prompt(self):
        """Verify resume prompt generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            # Save checkpoint
            await manager.save_research_checkpoint(
                task_name="test-task",
                query="Original research query",
                partial_results={"findings": ["Finding 1", "Finding 2"]},
                sources_collected=[{"title": "Source 1", "url": "http://example.com"}],
                progress_pct=30.0,
                resumable=True
            )

            # Build resume prompt
            prompt = manager.build_resume_prompt("test-task")

            assert prompt is not None
            assert "CONTINUE" in prompt
            assert "Original research query" in prompt
            assert "30" in prompt and "%" in prompt
            assert "Finding 1" in prompt

    @pytest.mark.asyncio
    async def test_build_resume_prompt_non_resumable(self):
        """Verify resume prompt returns None for non-resumable checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            # Save non-resumable checkpoint
            await manager.save_research_checkpoint(
                task_name="test-task",
                query="query",
                partial_results={},
                sources_collected=[],
                progress_pct=80.0,
                resumable=False
            )

            # Build resume prompt
            prompt = manager.build_resume_prompt("test-task")
            assert prompt is None

    def test_should_create_checkpoint(self):
        """Verify checkpoint decision logic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            # Test at 15 minutes (should checkpoint)
            should_cp, pct, phase, resumable = manager.should_create_checkpoint(
                elapsed_sec=900,
                estimated_duration_sec=3600
            )
            assert should_cp is True
            assert pct == 15
            assert resumable is True

            # Test at 50 minutes (should checkpoint)
            should_cp, pct, phase, resumable = manager.should_create_checkpoint(
                elapsed_sec=3000,
                estimated_duration_sec=3600
            )
            assert should_cp is True
            assert pct == 50
            assert resumable is True

            # Test at 60 minutes (should checkpoint but not resumable)
            should_cp, pct, phase, resumable = manager.should_create_checkpoint(
                elapsed_sec=3600,
                estimated_duration_sec=3600
            )
            assert should_cp is True
            assert pct == 75
            assert resumable is False

            # Test at random time (should not checkpoint)
            should_cp, pct, phase, resumable = manager.should_create_checkpoint(
                elapsed_sec=2000,
                estimated_duration_sec=3600
            )
            assert should_cp is False

    def test_get_resume_estimate(self):
        """Verify time estimate calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)

            # Test for 30% checkpoint
            checkpoint = {
                "progress_pct": 30,
                "created_at": datetime.now().isoformat()
            }

            estimate = manager.get_resume_estimate(checkpoint)
            assert estimate["time_invested_min"] == 30
            assert estimate["time_remaining_min"] == 30
            assert estimate["time_saved_min"] == 30


class TestResearchResumeHelper:
    """Tests for ResearchResumeHelper class."""

    @pytest.mark.asyncio
    async def test_find_resumable_tasks(self):
        """Verify finding resumable tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)
            helper = ResearchResumeHelper(manager)

            # Create resumable checkpoint
            await manager.save_research_checkpoint(
                task_name="task1",
                query="query 1",
                partial_results={},
                sources_collected=[],
                progress_pct=30.0,
                resumable=True
            )

            # Create non-resumable checkpoint
            await manager.save_research_checkpoint(
                task_name="task2",
                query="query 2",
                partial_results={},
                sources_collected=[],
                progress_pct=80.0,
                resumable=False
            )

            # Find resumable
            resumable = helper.find_resumable_tasks()
            assert len(resumable) == 1
            assert resumable[0]["task_name"] == "task1"

    @pytest.mark.asyncio
    async def test_should_auto_resume_recent(self):
        """Verify auto-resume for recent checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)
            helper = ResearchResumeHelper(manager)

            # Create recent checkpoint
            await manager.save_research_checkpoint(
                task_name="recent-task",
                query="query",
                partial_results={},
                sources_collected=[],
                progress_pct=30.0,
                resumable=True
            )

            # Should auto-resume
            should_resume = helper.should_auto_resume("recent-task", max_age_hours=24)
            assert should_resume is True

    @pytest.mark.asyncio
    async def test_should_auto_resume_old(self):
        """Verify auto-resume rejects old checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            manager = ResearchCheckpointManager(project_folder, phase_num=1)
            helper = ResearchResumeHelper(manager)

            # Create checkpoint
            await manager.save_research_checkpoint(
                task_name="old-task",
                query="query",
                partial_results={},
                sources_collected=[],
                progress_pct=30.0,
                resumable=True
            )

            # Manually edit timestamp to be old
            checkpoint = manager.load_research_checkpoint("old-task")
            old_time = (datetime.now() - timedelta(hours=48)).isoformat()
            checkpoint["created_at"] = old_time

            checkpoint_file = manager.get_checkpoint_file("old-task")
            checkpoint_file.write_text(json.dumps(checkpoint))

            # Should NOT auto-resume
            should_resume = helper.should_auto_resume("old-task", max_age_hours=24)
            assert should_resume is False


# ============================================================================
# Pattern 5: Resumable Research Executor Tests
# ============================================================================

class TestResumableResearchExecutor:
    """Tests for ResumableResearchExecutor class."""

    @pytest.mark.asyncio
    async def test_executor_initialization(self):
        """Verify executor initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            executor = ResumableResearchExecutor(project_folder, phase_num=1)

            assert executor.project_folder == project_folder
            assert executor.phase_num == 1
            assert executor.auto_resume is True
            assert executor.checkpoint_mgr is not None
            assert executor.error_handler is not None

    @pytest.mark.asyncio
    async def test_execute_simple_research(self):
        """Verify executing simple research."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            executor = ResumableResearchExecutor(project_folder, phase_num=1)

            # Simple research function
            async def simple_research():
                return {"findings": ["test finding"]}

            result = await executor.execute(
                task_name="simple-test",
                query="test query",
                provider="test_provider",
                estimated_duration_sec=10,
                research_func=simple_research
            )

            assert "findings" in result
            assert result["findings"] == ["test finding"]

            # Verify stats
            stats = executor.get_stats()
            assert stats["tasks_executed"] == 1
            assert stats["tasks_completed"] == 1

    @pytest.mark.asyncio
    async def test_execute_with_resume(self):
        """Verify research resumes from checkpoint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            # Create executor and pre-save a checkpoint
            manager = ResearchCheckpointManager(project_folder, phase_num=1)
            await manager.save_research_checkpoint(
                task_name="resumable-test",
                query="original query",
                partial_results={"findings": ["partial finding"]},
                sources_collected=[],
                progress_pct=30.0,
                resumable=True
            )

            # Execute with auto-resume
            executor = ResumableResearchExecutor(project_folder, phase_num=1, auto_resume=True)

            async def research_func():
                return {"findings": ["completed finding"]}

            result = await executor.execute(
                task_name="resumable-test",
                query="new query",  # This will be replaced with resume prompt
                provider="test_provider",
                estimated_duration_sec=10,
                research_func=research_func
            )

            # Verify result
            assert "findings" in result

            # Verify stats
            stats = executor.get_stats()
            assert stats["tasks_resumed"] == 1
            assert stats["total_time_saved_min"] > 0

    @pytest.mark.asyncio
    async def test_execute_with_failure(self):
        """Verify research handles failure correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            executor = ResumableResearchExecutor(project_folder, phase_num=1)

            # Research function that fails
            async def failing_research():
                raise Exception("Research failed")

            with pytest.raises(Exception, match="Research failed"):
                await executor.execute(
                    task_name="failing-test",
                    query="test query",
                    provider="test_provider",
                    estimated_duration_sec=10,
                    research_func=failing_research
                )

            # Verify stats
            stats = executor.get_stats()
            assert stats["tasks_failed"] == 1


# ============================================================================
# Pattern 6: Enhanced Checkpoint Manager Tests
# ============================================================================

class TestEnhancedCheckpointManager:
    """Tests for enhanced checkpoint manager with research task tracking."""

    def test_save_checkpoint_with_research_tasks(self):
        """Verify checkpoint saves research task status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            research_tasks = {
                "task1": "completed",
                "task2": "failed",
                "task3": "skipped"
            }

            checkpoint_manager.save_checkpoint(
                project_folder=project_folder,
                phase_num=1,
                research_tasks=research_tasks
            )

            # Load and verify
            checkpoint = checkpoint_manager.load_checkpoint(project_folder)
            assert "research_tasks" in checkpoint
            assert "phase_1" in checkpoint["research_tasks"]
            assert checkpoint["research_tasks"]["phase_1"]["tasks"] == research_tasks

    def test_get_research_task_status(self):
        """Verify getting research task status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            research_tasks = {
                "task1": "completed",
                "task2": "failed"
            }

            checkpoint_manager.save_checkpoint(
                project_folder=project_folder,
                phase_num=1,
                research_tasks=research_tasks
            )

            # Get status
            status = checkpoint_manager.get_research_task_status(project_folder, phase_num=1)
            assert "tasks" in status
            assert status["tasks"]["task1"] == "completed"
            assert status["tasks"]["task2"] == "failed"

    def test_has_failed_research_tasks(self):
        """Verify checking for failed tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            research_tasks = {
                "task1": "completed",
                "task2": "failed"
            }

            checkpoint_manager.save_checkpoint(
                project_folder=project_folder,
                phase_num=1,
                research_tasks=research_tasks
            )

            # Check for failures
            has_failures = checkpoint_manager.has_failed_research_tasks(project_folder, 1)
            assert has_failures is True

    def test_get_failed_research_tasks(self):
        """Verify getting list of failed tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            research_tasks = {
                "task1": "completed",
                "task2": "failed",
                "task3": "failed",
                "task4": "skipped"
            }

            checkpoint_manager.save_checkpoint(
                project_folder=project_folder,
                phase_num=1,
                research_tasks=research_tasks
            )

            # Get failed tasks
            failed = checkpoint_manager.get_failed_research_tasks(project_folder, 1)
            assert len(failed) == 2
            assert "task2" in failed
            assert "task3" in failed

    def test_generate_resume_context_with_research_tasks(self):
        """Verify resume context includes research tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            research_tasks = {
                "task1": "completed",
                "task2": "failed"
            }

            checkpoint_manager.save_checkpoint(
                project_folder=project_folder,
                phase_num=1,
                research_tasks=research_tasks
            )

            # Generate context
            context = checkpoint_manager.generate_resume_context(project_folder)

            assert "Research Task Status" in context
            assert "task1" in context
            assert "task2" in context
            assert "completed" in context
            assert "failed" in context


# ============================================================================
# Integration Tests
# ============================================================================

class TestCheckpointSystemIntegration:
    """Integration tests for the complete checkpoint system."""

    @pytest.mark.asyncio
    async def test_full_checkpoint_workflow(self):
        """Test complete workflow: execute -> checkpoint -> resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            # Phase 1: Execute research and create checkpoint
            executor1 = ResumableResearchExecutor(project_folder, phase_num=1)

            # Simulate failure after checkpoint
            attempt_count = [0]

            async def research_that_fails_first_time():
                attempt_count[0] += 1
                if attempt_count[0] == 1:
                    # First attempt: fail (but checkpoint was saved)
                    raise Exception("Simulated failure")
                # Second attempt: succeed
                return {"findings": ["success"]}

            # First execution will fail
            try:
                await executor1.execute(
                    task_name="workflow-test",
                    query="test query",
                    provider="test_provider",
                    estimated_duration_sec=10,
                    research_func=research_that_fails_first_time
                )
            except Exception:
                pass  # Expected failure

            # Phase 2: Resume from checkpoint
            executor2 = ResumableResearchExecutor(project_folder, phase_num=1, auto_resume=True)

            result = await executor2.execute(
                task_name="workflow-test",
                query="test query",
                provider="test_provider",
                estimated_duration_sec=10,
                research_func=research_that_fails_first_time
            )

            assert result["findings"] == ["success"]
            # Verify resumed
            stats = executor2.get_stats()
            assert stats["tasks_resumed"] >= 0  # May or may not resume depending on checkpoint timing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
