"""
Research Error System - Priority 4.1

Structured errors with context and recovery guidance for research operations.

Usage:
    from research_errors import raise_research_error, ErrorCode, ResearchError

    try:
        # ... operation ...
    except Exception as e:
        raise_research_error(
            ErrorCode.RATE_LIMIT,
            "Rate limit exceeded",
            provider="gemini",
            attempts=3
        )

Features:
- Standard error codes for common failure modes
- Contextual information about what failed
- Recovery suggestions for each error type
- Structured output for debugging and monitoring
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ErrorCode(Enum):
    """Standard error codes for research operations."""
    RATE_LIMIT = "RATE_LIMIT"
    NETWORK = "NETWORK"
    TIMEOUT = "TIMEOUT"
    VALIDATION = "VALIDATION"
    CHECKPOINT_CORRUPT = "CHECKPOINT_CORRUPT"
    CIRCUIT_OPEN = "CIRCUIT_OPEN"
    INVALID_STATE = "INVALID_STATE"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    FILE_IO = "FILE_IO"
    UNKNOWN = "UNKNOWN"


@dataclass
class ResearchError(Exception):
    """
    Structured error with recovery guidance.

    Attributes:
        code: Error code classification
        message: Human-readable error description
        context: Additional contextual information (provider, task, etc.)
        recovery_suggestions: List of recovery steps to try
        timestamp: When error occurred (auto-set)
    """
    code: ErrorCode
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_suggestions: List[str] = field(default_factory=list)
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

        # Make this a proper Exception
        super().__init__(self.message)

    def __str__(self):
        """Format error message with context and recovery suggestions."""
        lines = [
            f"❌ Research Error: {self.code.value}",
            f"   {self.message}",
            "",
        ]

        if self.context:
            lines.append("Context:")
            for key, value in self.context.items():
                # Truncate long values
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:97] + "..."
                lines.append(f"  • {key}: {value_str}")
            lines.append("")

        if self.recovery_suggestions:
            lines.append("Recovery Suggestions:")
            for i, suggestion in enumerate(self.recovery_suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "code": self.code.value,
            "message": self.message,
            "context": self.context,
            "recovery_suggestions": self.recovery_suggestions,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


# Recovery strategy mapping for each error code
RECOVERY_STRATEGIES: Dict[ErrorCode, List[str]] = {
    ErrorCode.RATE_LIMIT: [
        "Wait 60 seconds and retry",
        "Check API quota limits in provider dashboard",
        "Use fallback provider (Perplexity instead of Deep Research)",
        "Reduce request frequency in configuration",
    ],
    ErrorCode.NETWORK: [
        "Check internet connection",
        "Retry in 30 seconds",
        "Verify firewall settings",
        "Check if API endpoint is accessible",
    ],
    ErrorCode.TIMEOUT: [
        "Resume from checkpoint if available (use resume-research.py)",
        "Increase timeout in configuration (research_config.py)",
        "Check network latency to API endpoint",
        "Try with faster provider (Perplexity instead of Deep Research)",
    ],
    ErrorCode.CHECKPOINT_CORRUPT: [
        "Delete corrupt checkpoint file and restart task",
        "Check disk space (df -h)",
        "Verify filesystem permissions",
        "Review checkpoint file manually for JSON errors",
    ],
    ErrorCode.CIRCUIT_OPEN: [
        "Wait 60 seconds for circuit to close",
        "Check recent error logs for root cause",
        "Manually reset circuit with --force-reset flag",
        "Reduce failure threshold in configuration",
    ],
    ErrorCode.INVALID_STATE: [
        "Verify task is not already completed",
        "Check state transition history in progress file",
        "Delete task state and restart from beginning",
        "Review state machine transitions in research_state_machine.py",
    ],
    ErrorCode.PROVIDER_ERROR: [
        "Check API key configuration",
        "Verify provider is available (check status page)",
        "Try fallback provider",
        "Review provider error details in logs",
    ],
    ErrorCode.FILE_IO: [
        "Check file permissions (ls -la)",
        "Verify disk space is available",
        "Check if file path is valid",
        "Review filesystem mount status",
    ],
    ErrorCode.VALIDATION: [
        "Check input parameters for correctness",
        "Review validation error details",
        "Verify configuration file syntax",
        "Consult documentation for required fields",
    ],
    ErrorCode.UNKNOWN: [
        "Review full error traceback",
        "Check system logs for additional context",
        "Enable debug logging for more details",
        "Report issue with full error details",
    ],
}


def raise_research_error(code: ErrorCode, message: str, **context) -> None:
    """
    Raise a structured research error with recovery guidance.

    Args:
        code: Error code classification
        message: Human-readable error description
        **context: Additional context as keyword arguments

    Raises:
        ResearchError: Always raises with structured error information

    Example:
        raise_research_error(
            ErrorCode.RATE_LIMIT,
            "Rate limit exceeded for Gemini Deep Research",
            provider="gemini_deep_research",
            attempts=3,
            next_retry_in_sec=60
        )
    """
    suggestions = RECOVERY_STRATEGIES.get(code, RECOVERY_STRATEGIES[ErrorCode.UNKNOWN])
    raise ResearchError(code, message, context, suggestions)


def wrap_error(original_error: Exception, code: ErrorCode, message: str, **context) -> ResearchError:
    """
    Wrap an existing exception into a ResearchError.

    Args:
        original_error: The original exception
        code: Error code classification
        message: Human-readable error description
        **context: Additional context as keyword arguments

    Returns:
        ResearchError: Wrapped error with recovery guidance

    Example:
        try:
            result = api_call()
        except requests.HTTPError as e:
            wrapped = wrap_error(
                e,
                ErrorCode.RATE_LIMIT,
                "API rate limit exceeded",
                status_code=e.response.status_code
            )
            raise wrapped from e
    """
    # Add original error details to context
    context["original_error_type"] = type(original_error).__name__
    context["original_error_message"] = str(original_error)

    suggestions = RECOVERY_STRATEGIES.get(code, RECOVERY_STRATEGIES[ErrorCode.UNKNOWN])
    return ResearchError(code, message, context, suggestions)


# Example usage
if __name__ == "__main__":
    print("=== Example 1: Rate Limit Error ===")
    try:
        raise_research_error(
            ErrorCode.RATE_LIMIT,
            "Rate limit exceeded for Gemini Deep Research",
            provider="gemini_deep_research",
            attempts=3,
            quota_limit=10,
            next_retry_in_sec=60
        )
    except ResearchError as e:
        print(e)
        print(f"\nJSON: {e.to_dict()}")

    print("\n" + "="*70)
    print("=== Example 2: Timeout with Checkpoint ===")
    try:
        raise_research_error(
            ErrorCode.TIMEOUT,
            "Research operation timed out after 60 minutes",
            task_name="competitive-analysis",
            elapsed_sec=3600,
            checkpoint_available=True,
            checkpoint_progress_pct=75
        )
    except ResearchError as e:
        print(e)

    print("\n" + "="*70)
    print("=== Example 3: Invalid State Transition ===")
    try:
        raise_research_error(
            ErrorCode.INVALID_STATE,
            "Cannot transition from COMPLETED to RUNNING",
            current_state="COMPLETED",
            attempted_state="RUNNING",
            event="start",
            task_id="research-123"
        )
    except ResearchError as e:
        print(e)
