"""
Integration tests for user-facing features (Patterns 7-8).

Tests the resume command, monitoring script, and enhanced research integration.
"""

import asyncio
import json
import pytest
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from research_checkpoint_manager import ResearchCheckpointManager
from research_progress_tracker import ResearchProgressTracker
from enhanced_research_integration import EnhancedResearchLookup, HAS_RESEARCH_LOOKUP


# ============================================================================
# Pattern 7: Resume Command Tests
# ============================================================================

class TestResumeCommand:
    """Tests for resume-research.py CLI command."""

    @pytest.mark.asyncio
    async def test_resume_command_list(self):
        """Test resume command --list option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            phase_num = 1

            # Create some checkpoints
            manager = ResearchCheckpointManager(project_folder, phase_num)
            for i in range(3):
                await manager.save_research_checkpoint(
                    task_name=f"task-{i}",
                    query=f"Query {i}",
                    partial_results={"findings": [f"finding {i}"]},
                    sources_collected=[],
                    progress_pct=30.0,
                    resumable=True
                )

            # Run resume command with --list
            result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "resume-research.py"),
                    str(project_folder),
                    str(phase_num),
                    "--list"
                ],
                capture_output=True,
                text=True
            )

            # Verify output
            assert result.returncode == 0
            assert "RESUMABLE RESEARCH TASKS" in result.stdout
            assert "task-0" in result.stdout or "task-1" in result.stdout or "task-2" in result.stdout

    def test_resume_command_no_checkpoints(self):
        """Test resume command with no checkpoints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            phase_num = 1

            # Run resume command with --list (no checkpoints exist)
            result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "resume-research.py"),
                    str(project_folder),
                    str(phase_num),
                    "--list"
                ],
                capture_output=True,
                text=True
            )

            # Verify output
            assert result.returncode == 0
            assert "NO RESUMABLE RESEARCH TASKS FOUND" in result.stdout

    @pytest.mark.asyncio
    async def test_resume_command_specific_task(self):
        """Test resuming a specific task."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            phase_num = 1

            # Create checkpoint
            manager = ResearchCheckpointManager(project_folder, phase_num)
            await manager.save_research_checkpoint(
                task_name="test-task",
                query="Test query",
                partial_results={"findings": ["partial finding"]},
                sources_collected=[{"title": "Source 1", "url": "http://example.com"}],
                progress_pct=30.0,
                resumable=True
            )

            # Run resume command for specific task
            result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "resume-research.py"),
                    str(project_folder),
                    str(phase_num),
                    "--task", "test-task"
                ],
                capture_output=True,
                text=True
            )

            # Verify output
            assert result.returncode == 0
            assert "RESUMING RESEARCH TASK" in result.stdout
            assert "test-task" in result.stdout
            assert "30" in result.stdout  # Progress percentage

    def test_resume_command_nonexistent_task(self):
        """Test resuming a nonexistent task."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            phase_num = 1

            # Run resume command for nonexistent task
            result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "resume-research.py"),
                    str(project_folder),
                    str(phase_num),
                    "--task", "nonexistent"
                ],
                capture_output=True,
                text=True
            )

            # Verify error
            assert result.returncode == 1
            assert "No checkpoint found" in result.stdout


# ============================================================================
# Pattern 8: Monitoring Script Tests
# ============================================================================

class TestMonitoringScript:
    """Tests for monitor-research-progress.py script."""

    @pytest.mark.asyncio
    async def test_monitoring_list_active(self):
        """Test monitoring script --list option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            # Create some active progress files
            for i in range(2):
                task_id = f"test-task-{i}"
                tracker = ResearchProgressTracker(project_folder, task_id)
                await tracker.start(
                    query=f"Query {i}",
                    provider="test_provider",
                    estimated_duration_sec=60
                )

            # Run monitoring script with --list
            result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "monitor-research-progress.py"),
                    str(project_folder),
                    "--list"
                ],
                capture_output=True,
                text=True
            )

            # Verify output
            assert result.returncode == 0
            assert "ACTIVE RESEARCH OPERATIONS" in result.stdout
            assert "test-task-" in result.stdout

    @pytest.mark.asyncio
    async def test_monitoring_specific_task(self):
        """Test monitoring a specific task."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "monitor-test-123"

            # Create progress file
            tracker = ResearchProgressTracker(project_folder, task_id)
            await tracker.start(
                query="Test monitoring query",
                provider="test_provider",
                estimated_duration_sec=60
            )

            # Update progress
            await tracker.update("phase1", "Testing monitoring", 50.0)

            # Run monitoring script
            result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "monitor-research-progress.py"),
                    str(project_folder),
                    task_id
                ],
                capture_output=True,
                text=True
            )

            # Verify output
            assert result.returncode == 0
            assert "RUNNING" in result.stdout
            assert "50" in result.stdout  # Progress percentage
            assert "phase1" in result.stdout

    @pytest.mark.asyncio
    async def test_monitoring_completed_task(self):
        """Test monitoring a completed task."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "completed-test-456"

            # Create and complete progress file
            tracker = ResearchProgressTracker(project_folder, task_id)
            await tracker.start(
                query="Test query",
                provider="test_provider",
                estimated_duration_sec=60
            )
            await tracker.complete(results={"findings": "Complete"})

            # Run monitoring script
            result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "monitor-research-progress.py"),
                    str(project_folder),
                    task_id
                ],
                capture_output=True,
                text=True
            )

            # Verify output
            assert result.returncode == 0
            assert "COMPLETED" in result.stdout
            assert "100" in result.stdout  # Progress percentage

    def test_monitoring_nonexistent_task(self):
        """Test monitoring a nonexistent task."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            # Run monitoring script for nonexistent task
            result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "monitor-research-progress.py"),
                    str(project_folder),
                    "nonexistent-task"
                ],
                capture_output=True,
                text=True
            )

            # Verify error
            assert result.returncode == 1
            assert "No progress file found" in result.stdout


# ============================================================================
# Enhanced Research Integration Tests
# ============================================================================

@pytest.mark.skipif(not HAS_RESEARCH_LOOKUP, reason="research_lookup.py not available")
class TestEnhancedResearchIntegration:
    """Tests for enhanced research integration."""

    @pytest.mark.asyncio
    async def test_enhanced_research_initialization(self):
        """Test EnhancedResearchLookup initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            research = EnhancedResearchLookup(
                project_folder=project_folder,
                phase_num=1,
                research_mode="balanced"
            )

            assert research.project_folder == project_folder
            assert research.phase_num == 1
            assert research.research_mode == "balanced"
            assert research.executor is not None

    @pytest.mark.asyncio
    async def test_enhanced_research_get_stats(self):
        """Test getting statistics from enhanced research."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            research = EnhancedResearchLookup(
                project_folder=project_folder,
                phase_num=1,
                research_mode="perplexity"
            )

            stats = research.get_stats()
            assert "tasks_executed" in stats
            assert "tasks_completed" in stats
            assert "tasks_failed" in stats


# ============================================================================
# End-to-End Workflow Tests
# ============================================================================

class TestEndToEndWorkflow:
    """End-to-end tests combining all user-facing features."""

    @pytest.mark.asyncio
    async def test_complete_workflow_with_resume(self):
        """
        Test complete workflow: research → interrupt → resume → monitor.

        Simulates a realistic user workflow:
        1. Start research
        2. Create checkpoint
        3. Interrupt (simulate)
        4. List resumable tasks
        5. Resume from checkpoint
        6. Monitor progress
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            phase_num = 1
            task_name = "workflow-test"

            # STEP 1: Create checkpoint (simulating interrupted research)
            manager = ResearchCheckpointManager(project_folder, phase_num)
            await manager.save_research_checkpoint(
                task_name=task_name,
                query="Workflow test query",
                partial_results={"findings": ["Partial finding"]},
                sources_collected=[],
                progress_pct=30.0,
                resumable=True
            )

            # STEP 2: List resumable tasks (via CLI)
            list_result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "resume-research.py"),
                    str(project_folder),
                    str(phase_num),
                    "--list"
                ],
                capture_output=True,
                text=True
            )

            assert list_result.returncode == 0
            assert task_name in list_result.stdout

            # STEP 3: Create progress file (simulating resumed research)
            task_id = f"resumed-{task_name}"
            tracker = ResearchProgressTracker(project_folder, task_id)
            await tracker.start(
                query="Workflow test query",
                provider="test_provider",
                estimated_duration_sec=60
            )
            await tracker.update("resumed", "Continuing from checkpoint", 50.0)

            # STEP 4: Monitor progress (via CLI)
            monitor_result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "monitor-research-progress.py"),
                    str(project_folder),
                    task_id
                ],
                capture_output=True,
                text=True
            )

            assert monitor_result.returncode == 0
            assert "RUNNING" in monitor_result.stdout
            assert "50" in monitor_result.stdout

            # STEP 5: Complete research
            await tracker.complete(results={"findings": "Complete"})

            # STEP 6: Delete checkpoint (cleanup)
            manager.delete_checkpoint(task_name)

            # Verify checkpoint deleted
            checkpoint = manager.load_research_checkpoint(task_name)
            assert checkpoint is None


# ============================================================================
# CLI Integration Tests
# ============================================================================

class TestCLIIntegration:
    """Tests for CLI integration scenarios."""

    def test_resume_command_help(self):
        """Test resume command help output."""
        result = subprocess.run(
            [
                "python",
                str(Path(__file__).parent.parent / "scripts" / "resume-research.py"),
                "--help"
            ],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "--list" in result.stdout
        assert "--task" in result.stdout

    def test_monitoring_command_help(self):
        """Test monitoring command help output."""
        result = subprocess.run(
            [
                "python",
                str(Path(__file__).parent.parent / "scripts" / "monitor-research-progress.py"),
                "--help"
            ],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()
        assert "--list" in result.stdout
        assert "--follow" in result.stdout

    def test_resume_command_invalid_phase(self):
        """Test resume command with invalid phase number."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            result = subprocess.run(
                [
                    "python",
                    str(Path(__file__).parent.parent / "scripts" / "resume-research.py"),
                    str(project_folder),
                    "99",  # Invalid phase
                    "--list"
                ],
                capture_output=True,
                text=True
            )

            assert result.returncode == 1
            assert "Invalid phase number" in result.stderr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
