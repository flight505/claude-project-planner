"""
Unit tests for progress tracking infrastructure.

Tests Pattern 1 (streaming), Pattern 2 (progress files), and Pattern 3 (error handling).
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from research_progress_tracker import ResearchProgressTracker, ProgressMonitor
from research_error_handling import (
    ResearchErrorHandler,
    CircuitBreaker,
    ErrorType,
    CircuitBreakerState,
    ErrorRecoveryStrategy
)
from research_errors import ResearchError


# ============================================================================
# Pattern 2: Research Progress Tracker Tests
# ============================================================================

class TestResearchProgressTracker:
    """Tests for ResearchProgressTracker class."""

    @pytest.mark.asyncio
    async def test_progress_file_created(self):
        """Verify progress file is created with correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "test-task-123"

            tracker = ResearchProgressTracker(project_folder, task_id)

            await tracker.start(
                query="test query",
                provider="test_provider",
                estimated_duration_sec=3600
            )

            # Verify file exists
            assert tracker.progress_file.exists()

            # Read and verify content
            progress = json.loads(tracker.progress_file.read_text())
            assert progress["task_id"] == task_id
            assert progress["query"] == "test query"
            assert progress["provider"] == "test_provider"
            assert progress["status"] == "running"
            assert progress["progress_pct"] == 0
            assert "checkpoints" in progress

    @pytest.mark.asyncio
    async def test_progress_update(self):
        """Verify progress updates work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "test-task-123"

            tracker = ResearchProgressTracker(project_folder, task_id)
            await tracker.start("test query", "test_provider")

            # Update progress
            await tracker.update(
                phase="test_phase",
                action="test action",
                progress_pct=50.0
            )

            # Read and verify
            progress = tracker.read_progress()
            assert progress["phase"] == "test_phase"
            assert progress["current_action"] == "test action"
            assert progress["progress_pct"] == 50.0
            assert progress["status"] == "running"

    @pytest.mark.asyncio
    async def test_checkpoint_history_preserved(self):
        """Verify checkpoints accumulate in history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "test-task-123"

            tracker = ResearchProgressTracker(project_folder, task_id)
            await tracker.start("test query", "test_provider")

            # Create multiple checkpoints
            await tracker.update("phase1", "action1", 15.0, save_checkpoint=True)
            await tracker.update("phase2", "action2", 30.0, save_checkpoint=True)
            await tracker.update("phase3", "action3", 50.0, save_checkpoint=True)

            # Verify checkpoints
            progress = tracker.read_progress()
            assert len(progress["checkpoints"]) == 3
            assert progress["checkpoints"][0]["progress_pct"] == 15.0
            assert progress["checkpoints"][1]["progress_pct"] == 30.0
            assert progress["checkpoints"][2]["progress_pct"] == 50.0

    @pytest.mark.asyncio
    async def test_complete_marks_completed(self):
        """Verify complete() marks research as completed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "test-task-123"

            tracker = ResearchProgressTracker(project_folder, task_id)
            await tracker.start("test query", "test_provider")
            await tracker.complete(results={"findings": "test findings"})

            # Verify completion
            progress = tracker.read_progress()
            assert progress["status"] == "completed"
            assert progress["progress_pct"] == 100
            assert "results" in progress
            assert progress["results"]["findings"] == "test findings"

    @pytest.mark.asyncio
    async def test_fail_marks_failed(self):
        """Verify fail() marks research as failed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "test-task-123"

            tracker = ResearchProgressTracker(project_folder, task_id)
            await tracker.start("test query", "test_provider")
            await tracker.fail("Test error", error_type="timeout")

            # Verify failure
            progress = tracker.read_progress()
            assert progress["status"] == "failed"
            assert progress["error"] == "Test error"
            assert progress["error_type"] == "timeout"

    @pytest.mark.asyncio
    async def test_list_active_research(self):
        """Verify list_active_research finds running tasks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)

            # Create multiple progress files
            trackers = []
            for i in range(3):
                task_id = f"task-{i}"
                tracker = ResearchProgressTracker(project_folder, task_id)
                await tracker.start(f"query {i}", "test_provider")
                trackers.append(tracker)

            # List active
            active = ResearchProgressTracker.list_active_research(project_folder)
            assert len(active) == 3

            # Complete one task using the original tracker instance
            await trackers[0].complete()

            # List active again
            active = ResearchProgressTracker.list_active_research(project_folder)
            assert len(active) == 2  # One completed, two still running


class TestProgressMonitor:
    """Tests for ProgressMonitor class."""

    @pytest.mark.asyncio
    async def test_get_status(self):
        """Verify get_status returns correct status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "test-task-123"

            tracker = ResearchProgressTracker(project_folder, task_id)
            await tracker.start("test query", "test_provider")

            monitor = ProgressMonitor(tracker)
            status = monitor.get_status()
            assert status == "running"

    @pytest.mark.asyncio
    async def test_get_progress_pct(self):
        """Verify get_progress_pct returns correct percentage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "test-task-123"

            tracker = ResearchProgressTracker(project_folder, task_id)
            await tracker.start("test query", "test_provider")
            await tracker.update("phase", "action", 75.0)

            monitor = ProgressMonitor(tracker)
            progress = monitor.get_progress_pct()
            assert progress == 75.0


# ============================================================================
# Pattern 3: Research Error Handler Tests
# ============================================================================

class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    def test_initial_state_closed(self):
        """Verify circuit breaker starts in closed state."""
        breaker = CircuitBreaker(failure_threshold=3)
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.can_attempt()

    def test_opens_after_threshold_failures(self):
        """Verify circuit opens after failure threshold."""
        breaker = CircuitBreaker(failure_threshold=3)

        # Record failures
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.CLOSED
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.CLOSED
        breaker.record_failure()
        assert breaker.state == CircuitBreakerState.OPEN

        # Cannot attempt when open
        assert not breaker.can_attempt()

    def test_success_resets_failure_count(self):
        """Verify success resets failure count."""
        breaker = CircuitBreaker(failure_threshold=3)

        # Record some failures
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.failure_count == 2

        # Success resets
        breaker.record_success()
        assert breaker.failure_count == 0

    def test_half_open_after_timeout(self):
        """Verify circuit goes to half-open after timeout."""
        breaker = CircuitBreaker(failure_threshold=3, timeout_sec=0)  # Instant timeout

        # Open the circuit
        for _ in range(3):
            breaker.record_failure()

        assert breaker.state == CircuitBreakerState.OPEN

        # Should be able to attempt (moves to half-open)
        assert breaker.can_attempt()
        assert breaker.state == CircuitBreakerState.HALF_OPEN


class TestResearchErrorHandler:
    """Tests for ResearchErrorHandler class."""

    def test_classify_error_rate_limit(self):
        """Verify rate limit errors are classified correctly."""
        handler = ResearchErrorHandler()

        error = Exception("Rate limit exceeded (429)")
        error_type = handler.classify_error(error)
        assert error_type == ErrorType.RATE_LIMIT

    def test_classify_error_transient(self):
        """Verify transient errors are classified correctly."""
        handler = ResearchErrorHandler()

        error = asyncio.TimeoutError("Connection timeout")
        error_type = handler.classify_error(error)
        assert error_type == ErrorType.TRANSIENT

    def test_classify_error_fatal(self):
        """Verify fatal errors are classified correctly."""
        handler = ResearchErrorHandler()

        error = Exception("Invalid API key (401)")
        error_type = handler.classify_error(error)
        assert error_type == ErrorType.FATAL

    def test_exponential_backoff_calculation(self):
        """Verify exponential backoff delays increase correctly."""
        handler = ResearchErrorHandler(base_delay=2.0)

        delay0 = handler.calculate_delay(0)
        delay1 = handler.calculate_delay(1)
        delay2 = handler.calculate_delay(2)

        # Delays should increase exponentially
        assert 2.0 <= delay0 < 3.5  # ~2-3s
        assert 4.0 <= delay1 < 5.5  # ~4-5s
        assert 8.0 <= delay2 < 9.5  # ~8-9s

    @pytest.mark.asyncio
    async def test_retry_succeeds_after_transient_failure(self):
        """Verify retry succeeds after transient failure."""
        handler = ResearchErrorHandler(max_retries=3, base_delay=0.1)

        attempt_count = [0]

        async def flaky_func():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise asyncio.TimeoutError("Temporary failure")
            return "success"

        result = await handler.retry_with_backoff(flaky_func)

        assert result == "success"
        assert attempt_count[0] == 2  # Failed once, then succeeded

    @pytest.mark.asyncio
    async def test_retry_callback_invoked(self):
        """Verify retry callback is called with correct parameters."""
        handler = ResearchErrorHandler(max_retries=3, base_delay=0.1)

        retry_events = []

        async def on_retry(attempt, max_retries, delay, error_type, error_msg):
            retry_events.append({
                "attempt": attempt,
                "max_retries": max_retries,
                "delay": delay,
                "error_type": error_type
            })

        async def flaky_func():
            if len(retry_events) < 1:
                raise asyncio.TimeoutError("Transient error")
            return "success"

        await handler.retry_with_backoff(flaky_func, on_retry=on_retry)

        # Verify callback was called
        assert len(retry_events) == 1
        assert retry_events[0]["attempt"] == 1
        assert retry_events[0]["error_type"] == "transient"

    @pytest.mark.asyncio
    async def test_fatal_error_not_retried(self):
        """Verify fatal errors are not retried."""
        handler = ResearchErrorHandler(max_retries=3)

        async def fatal_func():
            raise ValueError("Invalid request")

        with pytest.raises(ResearchError):
            await handler.retry_with_backoff(fatal_func)

        # Should fail immediately (1 attempt, no retries)
        stats = handler.get_stats()
        assert stats["total_attempts"] == 1
        assert stats["retries"] == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_rate_limits(self):
        """Verify circuit breaker opens after rate limit errors."""
        handler = ResearchErrorHandler(
            max_retries=3,
            base_delay=0.1,
            enable_circuit_breaker=True
        )

        async def rate_limited_func():
            raise Exception("Rate limit exceeded (429)")

        # First call should exhaust retries
        with pytest.raises(Exception):
            await handler.retry_with_backoff(rate_limited_func)

        # Circuit should be open
        breaker_state = handler.circuit_breaker.get_state_info()
        assert breaker_state["state"] == "open"


class TestErrorRecoveryStrategy:
    """Tests for ErrorRecoveryStrategy class."""

    @pytest.mark.asyncio
    async def test_graceful_degradation_uses_fallback(self):
        """Verify graceful degradation falls back on failure."""

        async def primary_func():
            raise Exception("Primary failed")

        async def fallback_func():
            return "fallback result"

        fallback_called = [False]

        async def on_fallback(error):
            fallback_called[0] = True

        result = await ErrorRecoveryStrategy.with_graceful_degradation(
            primary_func=primary_func,
            fallback_func=fallback_func,
            on_fallback=on_fallback
        )

        assert result == "fallback result"
        assert fallback_called[0]

    @pytest.mark.asyncio
    async def test_graceful_degradation_returns_primary_on_success(self):
        """Verify graceful degradation returns primary result on success."""

        async def primary_func():
            return "primary result"

        async def fallback_func():
            return "fallback result"

        result = await ErrorRecoveryStrategy.with_graceful_degradation(
            primary_func=primary_func,
            fallback_func=fallback_func
        )

        assert result == "primary result"


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple patterns."""

    @pytest.mark.asyncio
    async def test_progress_tracker_with_error_handling(self):
        """Test progress tracker combined with error handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_folder = Path(tmpdir)
            task_id = "integration-test-123"

            tracker = ResearchProgressTracker(project_folder, task_id)
            handler = ResearchErrorHandler(max_retries=2, base_delay=0.1)

            # Start tracking
            await tracker.start("test query", "test_provider", estimated_duration_sec=60)

            # Simulate research with retries
            attempt_count = [0]

            async def research_with_failure():
                attempt_count[0] += 1
                await tracker.update(f"attempt_{attempt_count[0]}", "researching", 25.0)

                if attempt_count[0] < 2:
                    raise asyncio.TimeoutError("Transient failure")

                return "success"

            result = await handler.retry_with_backoff(research_with_failure)

            assert result == "success"
            assert attempt_count[0] == 2

            # Mark complete
            await tracker.complete()

            # Verify final state
            progress = tracker.read_progress()
            assert progress["status"] == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
