"""
Research Error Handling - Pattern 3

Intelligent retry logic with exponential backoff and circuit breaker.

Usage:
    handler = ResearchErrorHandler(max_retries=3)
    result = await handler.retry_with_backoff(
        func, *args,
        on_retry=my_callback,
        **kwargs
    )

Features:
- Exponential backoff with jitter
- Circuit breaker for rate limiting
- Retry callbacks for progress updates
- Error classification (transient vs fatal)
"""

import asyncio
import random
from typing import Callable, Optional, Any, Dict
from datetime import datetime, timedelta
from enum import Enum


class ErrorType(Enum):
    """Classification of error types."""
    TRANSIENT = "transient"  # Temporary issues (network, timeout)
    RATE_LIMIT = "rate_limit"  # API rate limiting (429, quota exceeded)
    FATAL = "fatal"  # Permanent failures (auth, not found, invalid request)
    UNKNOWN = "unknown"  # Unclassified errors


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocking requests (too many failures)
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Opens circuit after consecutive failures to prevent cascade effects.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        timeout_sec: int = 60,
        half_open_attempts: int = 1
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of consecutive failures before opening (default: 3)
            timeout_sec: Seconds to wait before attempting half-open (default: 60)
            half_open_attempts: Number of attempts in half-open state (default: 1)
        """
        self.failure_threshold = failure_threshold
        self.timeout_sec = timeout_sec
        self.half_open_attempts = half_open_attempts

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None

    def record_success(self):
        """Record a successful operation."""
        self.failure_count = 0
        self.success_count += 1

        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.success_count >= self.half_open_attempts:
                # Service recovered, close circuit
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0

    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def can_attempt(self) -> bool:
        """
        Check if circuit allows attempts.

        Returns:
            True if can attempt, False if circuit is open
        """
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.HALF_OPEN:
            return True

        if self.state == CircuitBreakerState.OPEN:
            # Check if timeout has elapsed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout_sec:
                    # Try half-open
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                    return True

            return False

        return False

    def get_state_info(self) -> Dict[str, Any]:
        """Get current circuit breaker state information."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


class ResearchErrorHandler:
    """
    Sophisticated error handling for research operations.

    Provides exponential backoff, circuit breaker, and intelligent retry logic.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 2.0,
        max_delay: float = 60.0,
        enable_circuit_breaker: bool = True,
        circuit_breaker_failure_threshold: int = 3,
        circuit_breaker_timeout_sec: int = 60,
        circuit_breaker_half_open_attempts: int = 1
    ):
        """
        Initialize error handler with configurable settings.

        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay for exponential backoff in seconds (default: 2.0)
            max_delay: Maximum delay between retries in seconds (default: 60.0)
            enable_circuit_breaker: Enable circuit breaker for rate limiting (default: True)
            circuit_breaker_failure_threshold: Failures before opening circuit (default: 3)
            circuit_breaker_timeout_sec: Timeout before half-open (default: 60)
            circuit_breaker_half_open_attempts: Attempts in half-open state (default: 1)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.enable_circuit_breaker = enable_circuit_breaker

        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_failure_threshold,
            timeout_sec=circuit_breaker_timeout_sec,
            half_open_attempts=circuit_breaker_half_open_attempts
        )
        self.retry_stats = {
            "total_attempts": 0,
            "successful": 0,
            "failed": 0,
            "retries": 0
        }

    def classify_error(self, error: Exception) -> ErrorType:
        """
        Classify an error into a type.

        Args:
            error: The exception that occurred

        Returns:
            ErrorType classification
        """
        error_str = str(error).lower()

        # Rate limiting errors
        if any(term in error_str for term in ["rate", "429", "quota", "throttle"]):
            return ErrorType.RATE_LIMIT

        # Transient errors
        if any(term in error_str for term in [
            "timeout", "connection", "network", "temporary",
            "503", "502", "504", "retry"
        ]):
            return ErrorType.TRANSIENT

        # Fatal errors
        if any(term in error_str for term in [
            "auth", "401", "403", "404", "invalid", "not found",
            "permission", "forbidden"
        ]):
            return ErrorType.FATAL

        # Check exception type
        if isinstance(error, asyncio.TimeoutError):
            return ErrorType.TRANSIENT

        if isinstance(error, (ValueError, TypeError, AttributeError)):
            return ErrorType.FATAL

        return ErrorType.UNKNOWN

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for exponential backoff with jitter.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds

        Formula: min(max_delay, base_delay * 2^attempt + random(0, 1))
        """
        delay = self.base_delay * (2 ** attempt)
        jitter = random.uniform(0, 1)
        delay = min(self.max_delay, delay + jitter)
        return delay

    async def retry_with_backoff(
        self,
        func: Callable,
        *args,
        on_retry: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with exponential backoff retry.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            on_retry: Optional callback(attempt, max_retries, delay, error_type)
            **kwargs: Keyword arguments for func

        Returns:
            Result of func

        Raises:
            Exception: If all retries exhausted or circuit breaker open
        """
        self.retry_stats["total_attempts"] += 1

        for attempt in range(self.max_retries):
            # Check circuit breaker
            if self.enable_circuit_breaker and not self.circuit_breaker.can_attempt():
                raise Exception(
                    f"Circuit breaker is {self.circuit_breaker.state.value}. "
                    f"Too many rate limit failures. Try again later."
                )

            try:
                result = await func(*args, **kwargs)

                # Success!
                self.retry_stats["successful"] += 1
                if self.enable_circuit_breaker:
                    self.circuit_breaker.record_success()

                return result

            except Exception as e:
                # Classify error
                error_type = self.classify_error(e)

                # Fatal errors don't get retried
                if error_type == ErrorType.FATAL:
                    self.retry_stats["failed"] += 1
                    raise

                # Rate limit errors update circuit breaker
                if error_type == ErrorType.RATE_LIMIT and self.enable_circuit_breaker:
                    self.circuit_breaker.record_failure()

                # Last attempt - don't retry
                if attempt == self.max_retries - 1:
                    self.retry_stats["failed"] += 1
                    raise

                # Calculate delay
                delay = self.calculate_delay(attempt)

                # Call retry callback if provided
                if on_retry:
                    await on_retry(
                        attempt + 1,
                        self.max_retries,
                        delay,
                        error_type.value,
                        str(e)
                    )

                # Track retry
                self.retry_stats["retries"] += 1

                # Wait before retry
                await asyncio.sleep(delay)

        # Should never reach here
        raise Exception("Max retries exceeded")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get retry statistics.

        Returns:
            Dictionary with attempt counts and circuit breaker state
        """
        stats = self.retry_stats.copy()
        if self.enable_circuit_breaker:
            stats["circuit_breaker"] = self.circuit_breaker.get_state_info()
        return stats

    def reset_stats(self):
        """Reset statistics counters."""
        self.retry_stats = {
            "total_attempts": 0,
            "successful": 0,
            "failed": 0,
            "retries": 0
        }


class ErrorRecoveryStrategy:
    """
    High-level error recovery strategies.

    Combines multiple error handling techniques.
    """

    @staticmethod
    async def with_graceful_degradation(
        primary_func: Callable,
        fallback_func: Optional[Callable] = None,
        error_handler: Optional[ResearchErrorHandler] = None,
        on_fallback: Optional[Callable] = None
    ) -> Any:
        """
        Execute primary function with fallback on failure.

        Args:
            primary_func: Primary async function to try
            fallback_func: Fallback async function if primary fails
            error_handler: Optional error handler for retry logic
            on_fallback: Optional callback when falling back

        Returns:
            Result from primary or fallback function

        Example:
            result = await ErrorRecoveryStrategy.with_graceful_degradation(
                primary_func=deep_research,
                fallback_func=perplexity_research,
                on_fallback=lambda e: print(f"Falling back due to: {e}")
            )
        """
        if error_handler is None:
            error_handler = ResearchErrorHandler()

        try:
            # Try primary function with retry logic
            return await error_handler.retry_with_backoff(primary_func)

        except Exception as e:
            # Primary failed, try fallback
            if fallback_func:
                if on_fallback:
                    await on_fallback(e)

                # Try fallback (without retries to avoid long delays)
                return await fallback_func()

            # No fallback available
            raise


# Example usage
async def example_usage():
    """Example of how to use ResearchErrorHandler."""

    # Simulated research function that fails 2 times then succeeds
    attempt_count = 0

    async def flaky_research(query: str) -> str:
        nonlocal attempt_count
        attempt_count += 1

        if attempt_count <= 2:
            raise asyncio.TimeoutError(f"Network timeout (attempt {attempt_count})")

        return f"Research results for: {query}"

    # Custom retry callback
    async def on_retry(attempt, max_retries, delay, error_type, error_msg):
        print(f"  ⚠️  Retry {attempt}/{max_retries} after {delay:.1f}s ({error_type})")
        print(f"      Error: {error_msg}")

    # Create error handler
    handler = ResearchErrorHandler(max_retries=3, base_delay=2.0)

    # Execute with retry
    print("Attempting research with retry logic...")
    try:
        result = await handler.retry_with_backoff(
            flaky_research,
            "AI agent frameworks",
            on_retry=on_retry
        )
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Show statistics
    stats = handler.get_stats()
    print(f"\nStatistics:")
    print(f"  Total attempts: {stats['total_attempts']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Retries: {stats['retries']}")


async def example_graceful_degradation():
    """Example of graceful degradation with fallback."""

    async def deep_research(query: str) -> str:
        # Simulate failure
        raise Exception("Deep Research quota exceeded (rate limit)")

    async def perplexity_research(query: str) -> str:
        return f"[Perplexity] Quick research for: {query}"

    async def on_fallback(error: Exception):
        print(f"⚠️  Primary failed: {error}")
        print(f"🔄 Falling back to Perplexity...")

    # Execute with graceful degradation
    result = await ErrorRecoveryStrategy.with_graceful_degradation(
        primary_func=lambda: deep_research("AI agents"),
        fallback_func=lambda: perplexity_research("AI agents"),
        on_fallback=on_fallback
    )

    print(f"✅ Result: {result}")


if __name__ == "__main__":
    print("=== Example 1: Retry with Backoff ===")
    asyncio.run(example_usage())

    print("\n=== Example 2: Graceful Degradation ===")
    asyncio.run(example_graceful_degradation())
