"""
Research Configuration System

Centralized configuration for all research tracking and error recovery settings.
Eliminates hardcoded values and enables runtime configuration.

Usage:
    # Use defaults
    from research_config import DEFAULT_CONFIG

    # Or load from file
    config = ResearchConfig.from_file("custom_config.json")

    # Or create custom
    config = ResearchConfig(
        checkpoint_schedule=[...],
        max_retries=5
    )

Features:
- Checkpoint scheduling configuration
- Error handling and retry settings
- Circuit breaker configuration
- Timeout values
- File cleanup intervals
- JSON serialization support
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from pathlib import Path


@dataclass
class CheckpointScheduleEntry:
    """Single checkpoint milestone definition."""
    elapsed_sec: int       # Time elapsed when checkpoint triggers
    progress_pct: int      # Progress percentage to report
    phase_name: str        # Human-readable phase name
    resumable: bool        # Whether this checkpoint can be resumed from

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "elapsed_sec": self.elapsed_sec,
            "progress_pct": self.progress_pct,
            "phase_name": self.phase_name,
            "resumable": self.resumable
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckpointScheduleEntry':
        """Create from dictionary (JSON deserialization)."""
        return cls(**data)


@dataclass
class ResearchConfig:
    """
    Centralized configuration for research operations.

    All hardcoded values from the progress tracking system are consolidated here.
    Can be loaded from JSON files or created programmatically.
    """

    # ========== Checkpoint Configuration ==========
    checkpoint_schedule: List[CheckpointScheduleEntry] = field(default_factory=lambda: [
        CheckpointScheduleEntry(900, 15, "Gathering sources", True),         # 15 min
        CheckpointScheduleEntry(1800, 30, "Analyzing literature", True),     # 30 min
        CheckpointScheduleEntry(3000, 50, "Cross-referencing", True),        # 50 min
        CheckpointScheduleEntry(3600, 75, "Synthesizing report", False),     # 60 min (not resumable)
    ])

    checkpoint_check_interval_sec: int = 60       # How often to check if checkpoint needed
    checkpoint_max_age_hours: int = 24            # Max age for auto-resume
    checkpoint_cleanup_interval_hours: int = 168  # Clean up after 7 days

    # ========== Error Handling Configuration ==========
    max_retries: int = 3                          # Maximum retry attempts
    base_retry_delay_sec: float = 2.0            # Initial retry delay
    max_retry_delay_sec: float = 60.0            # Maximum retry delay
    retry_backoff_multiplier: float = 2.0        # Exponential backoff multiplier

    # ========== Circuit Breaker Configuration ==========
    circuit_breaker_failure_threshold: int = 3   # Failures before opening circuit
    circuit_breaker_timeout_sec: int = 60        # Time before trying again
    circuit_breaker_half_open_max_calls: int = 1 # Max calls in half-open state

    # ========== Progress Tracking Configuration ==========
    progress_update_interval_sec: float = 5.0   # Update interval for monitoring
    progress_file_cleanup_days: int = 7          # Delete old progress files after N days
    progress_default_estimated_duration_sec: int = 3600  # Default: 60 minutes

    # ========== Timeout Configuration ==========
    user_prompt_timeout_sec: int = 30            # Timeout for user input prompts
    research_default_timeout_sec: int = 3600     # Default research timeout
    deep_research_timeout_sec: int = 4000        # Deep Research timeout (66 min)
    perplexity_timeout_sec: int = 60             # Perplexity timeout

    # ========== Resume Configuration ==========
    resume_checkpoint_warning_age_hours: int = 168  # Warn if checkpoint > 7 days old
    resume_auto_max_age_hours: int = 24          # Auto-resume only if < 24 hours

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary for JSON serialization.

        Returns:
            Dictionary representation of config
        """
        data = asdict(self)

        # Convert checkpoint schedule entries to dicts
        data['checkpoint_schedule'] = [
            entry.to_dict() for entry in self.checkpoint_schedule
        ]

        return data

    def to_json(self, indent: int = 2) -> str:
        """
        Convert configuration to JSON string.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent)

    def to_file(self, path: Path):
        """
        Save configuration to JSON file.

        Args:
            path: Path to save configuration file

        Example:
            config.to_file(Path("custom_research_config.json"))
        """
        path.write_text(self.to_json())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchConfig':
        """
        Create configuration from dictionary.

        Args:
            data: Dictionary representation (from JSON)

        Returns:
            ResearchConfig instance
        """
        # Convert checkpoint schedule dicts to dataclasses
        if 'checkpoint_schedule' in data:
            data['checkpoint_schedule'] = [
                CheckpointScheduleEntry.from_dict(entry)
                for entry in data['checkpoint_schedule']
            ]

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'ResearchConfig':
        """
        Create configuration from JSON string.

        Args:
            json_str: JSON string representation

        Returns:
            ResearchConfig instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, path: Path) -> 'ResearchConfig':
        """
        Load configuration from JSON file.

        Args:
            path: Path to configuration file

        Returns:
            ResearchConfig instance

        Example:
            config = ResearchConfig.from_file(Path("my_config.json"))
        """
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        return cls.from_json(path.read_text())

    def get_checkpoint_schedule_tuples(self) -> List[tuple]:
        """
        Get checkpoint schedule as tuples for backward compatibility.

        Returns:
            List of (elapsed_sec, progress_pct, phase_name, resumable) tuples
        """
        return [
            (entry.elapsed_sec, entry.progress_pct, entry.phase_name, entry.resumable)
            for entry in self.checkpoint_schedule
        ]

    def validate(self) -> List[str]:
        """
        Validate configuration values.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate retry settings
        if self.max_retries < 1:
            errors.append("max_retries must be >= 1")
        if self.base_retry_delay_sec <= 0:
            errors.append("base_retry_delay_sec must be > 0")
        if self.max_retry_delay_sec < self.base_retry_delay_sec:
            errors.append("max_retry_delay_sec must be >= base_retry_delay_sec")

        # Validate circuit breaker
        if self.circuit_breaker_failure_threshold < 1:
            errors.append("circuit_breaker_failure_threshold must be >= 1")
        if self.circuit_breaker_timeout_sec <= 0:
            errors.append("circuit_breaker_timeout_sec must be > 0")

        # Validate checkpoint schedule
        if not self.checkpoint_schedule:
            errors.append("checkpoint_schedule cannot be empty")
        else:
            prev_time = 0
            for i, entry in enumerate(self.checkpoint_schedule):
                if entry.elapsed_sec <= prev_time:
                    errors.append(
                        f"checkpoint_schedule[{i}]: elapsed_sec must be increasing "
                        f"(got {entry.elapsed_sec} after {prev_time})"
                    )
                if entry.progress_pct < 0 or entry.progress_pct > 100:
                    errors.append(
                        f"checkpoint_schedule[{i}]: progress_pct must be 0-100 "
                        f"(got {entry.progress_pct})"
                    )
                prev_time = entry.elapsed_sec

        # Validate timeouts
        if self.user_prompt_timeout_sec <= 0:
            errors.append("user_prompt_timeout_sec must be > 0")

        # Validate cleanup intervals
        if self.checkpoint_cleanup_interval_hours < 1:
            errors.append("checkpoint_cleanup_interval_hours must be >= 1")
        if self.progress_file_cleanup_days < 1:
            errors.append("progress_file_cleanup_days must be >= 1")

        return errors


# Global default configuration instance
DEFAULT_CONFIG = ResearchConfig()


# Example usage and testing
def example_usage():
    """Example of how to use ResearchConfig."""
    print("="*70)
    print("RESEARCH CONFIGURATION EXAMPLE")
    print("="*70)

    # 1. Use default configuration
    print("\n--- Default Configuration ---")
    print(f"Max retries: {DEFAULT_CONFIG.max_retries}")
    print(f"Circuit breaker threshold: {DEFAULT_CONFIG.circuit_breaker_failure_threshold}")
    print(f"Checkpoint intervals: {len(DEFAULT_CONFIG.checkpoint_schedule)} checkpoints")
    for entry in DEFAULT_CONFIG.checkpoint_schedule:
        print(f"  • {entry.phase_name} @ {entry.elapsed_sec}s ({entry.progress_pct}%) - {'resumable' if entry.resumable else 'not resumable'}")

    # 2. Create custom configuration
    print("\n--- Custom Configuration ---")
    custom_config = ResearchConfig(
        max_retries=5,
        base_retry_delay_sec=1.0,
        circuit_breaker_failure_threshold=5,
        checkpoint_schedule=[
            CheckpointScheduleEntry(600, 25, "Initial analysis", True),
            CheckpointScheduleEntry(1200, 50, "Deep analysis", True),
            CheckpointScheduleEntry(1800, 75, "Synthesis", True),
        ]
    )
    print(f"Custom max retries: {custom_config.max_retries}")
    print(f"Custom checkpoint count: {len(custom_config.checkpoint_schedule)}")

    # 3. Validate configuration
    print("\n--- Validation ---")
    errors = custom_config.validate()
    if errors:
        print("❌ Validation errors:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("✅ Configuration valid")

    # 4. Save and load from file
    print("\n--- File I/O ---")
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)

    try:
        # Save
        custom_config.to_file(temp_path)
        print(f"✅ Saved to: {temp_path}")

        # Load
        loaded_config = ResearchConfig.from_file(temp_path)
        print(f"✅ Loaded from file")
        print(f"   Max retries: {loaded_config.max_retries}")
        print(f"   Checkpoints: {len(loaded_config.checkpoint_schedule)}")

        # Show JSON
        print("\n--- JSON Representation (first 400 chars) ---")
        print(loaded_config.to_json()[:400] + "...")

    finally:
        temp_path.unlink()

    print("\n" + "="*70)


if __name__ == "__main__":
    example_usage()
