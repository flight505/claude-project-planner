"""
Research Task State Machine

Validates and enforces state transitions for research tasks to prevent invalid
state changes and ensure data consistency.

Usage:
    state_machine = ResearchTaskStateMachine()
    state_machine.transition(ResearchTaskState.RUNNING, "start")
    state_machine.transition(ResearchTaskState.COMPLETED, "complete")

Features:
- Explicit state definitions
- Transition validation
- State history tracking
- Clear error messages for invalid transitions
"""

from enum import Enum
from typing import List, Tuple, Set, Optional
from dataclasses import dataclass
from datetime import datetime


class ResearchTaskState(Enum):
    """States a research task can be in."""
    PENDING = "pending"
    RUNNING = "running"
    CHECKPOINTED = "checkpointed"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StateTransitionRecord:
    """Record of a state transition."""
    from_state: ResearchTaskState
    to_state: ResearchTaskState
    event: str
    timestamp: datetime


class ResearchTaskStateMachine:
    """
    Validates and enforces state transitions for research tasks.

    Prevents invalid state changes like:
    - Marking a completed task as running
    - Resuming from a failed state without acknowledgment
    - Double-completion of tasks

    Maintains a history of all state transitions for debugging and audit purposes.
    """

    # Define allowed transitions: (from_state, to_state, event)
    ALLOWED_TRANSITIONS: Set[Tuple[ResearchTaskState, ResearchTaskState, str]] = {
        # Pending can start
        (ResearchTaskState.PENDING, ResearchTaskState.RUNNING, "start"),

        # Running can checkpoint, complete, or fail
        (ResearchTaskState.RUNNING, ResearchTaskState.CHECKPOINTED, "checkpoint"),
        (ResearchTaskState.RUNNING, ResearchTaskState.COMPLETED, "complete"),
        (ResearchTaskState.RUNNING, ResearchTaskState.FAILED, "fail"),

        # Checkpointed can resume or fail
        (ResearchTaskState.CHECKPOINTED, ResearchTaskState.RUNNING, "resume"),
        (ResearchTaskState.CHECKPOINTED, ResearchTaskState.FAILED, "fail"),

        # Terminal states (completed/failed) are final - no transitions allowed
    }

    def __init__(self, initial_state: ResearchTaskState = ResearchTaskState.PENDING):
        """
        Initialize state machine.

        Args:
            initial_state: Starting state (default: PENDING)
        """
        self.current_state = initial_state
        self.history: List[StateTransitionRecord] = []

        # Record initial state
        self.history.append(StateTransitionRecord(
            from_state=initial_state,
            to_state=initial_state,
            event="init",
            timestamp=datetime.now()
        ))

    def can_transition(self, to_state: ResearchTaskState, event: str) -> bool:
        """
        Check if transition is allowed.

        Args:
            to_state: Target state
            event: Event triggering the transition

        Returns:
            True if transition is allowed, False otherwise
        """
        return (self.current_state, to_state, event) in self.ALLOWED_TRANSITIONS

    def transition(self, to_state: ResearchTaskState, event: str):
        """
        Execute state transition with validation.

        Args:
            to_state: Target state
            event: Event triggering the transition

        Raises:
            ValueError: If transition is invalid

        Example:
            state_machine.transition(ResearchTaskState.RUNNING, "start")
        """
        if not self.can_transition(to_state, event):
            # Build helpful error message
            error_msg = self._build_transition_error(to_state, event)
            raise ValueError(error_msg)

        # Record transition
        record = StateTransitionRecord(
            from_state=self.current_state,
            to_state=to_state,
            event=event,
            timestamp=datetime.now()
        )
        self.history.append(record)

        # Update current state
        self.current_state = to_state

    def is_terminal(self) -> bool:
        """Check if current state is terminal (completed or failed)."""
        return self.current_state in [
            ResearchTaskState.COMPLETED,
            ResearchTaskState.FAILED
        ]

    def get_valid_events(self) -> List[str]:
        """
        Get list of valid events from current state.

        Returns:
            List of event names that can trigger valid transitions
        """
        valid_events = []
        for (from_state, to_state, event) in self.ALLOWED_TRANSITIONS:
            if from_state == self.current_state:
                valid_events.append(event)
        return valid_events

    def get_history(self) -> List[StateTransitionRecord]:
        """Get complete state transition history."""
        return self.history.copy()

    def _build_transition_error(self, to_state: ResearchTaskState, event: str) -> str:
        """Build detailed error message for invalid transition."""
        valid_events = self.get_valid_events()

        error_parts = [
            f"Invalid transition: {self.current_state.value} → {to_state.value} (event: {event})",
            "",
            f"Current state: {self.current_state.value}",
            f"Attempted event: {event}",
            f"Target state: {to_state.value}",
            "",
        ]

        if self.is_terminal():
            error_parts.extend([
                f"State '{self.current_state.value}' is terminal - no further transitions allowed.",
                "The task has already finished and cannot be modified.",
            ])
        elif valid_events:
            error_parts.extend([
                f"Valid events from '{self.current_state.value}': {', '.join(valid_events)}",
                "",
                "Allowed transitions:",
            ])
            for (from_state, to_state_allowed, event_allowed) in self.ALLOWED_TRANSITIONS:
                if from_state == self.current_state:
                    error_parts.append(f"  • {event_allowed}: {from_state.value} → {to_state_allowed.value}")
        else:
            error_parts.append(f"No valid transitions from state '{self.current_state.value}'")

        # Add recent history
        if len(self.history) > 1:
            error_parts.extend([
                "",
                "Recent state history:",
            ])
            for record in self.history[-5:]:
                error_parts.append(
                    f"  [{record.timestamp.strftime('%H:%M:%S')}] "
                    f"{record.event}: {record.from_state.value} → {record.to_state.value}"
                )

        return "\n".join(error_parts)


# Example usage and testing
def example_usage():
    """Example of how to use ResearchTaskStateMachine."""
    print("="*70)
    print("RESEARCH TASK STATE MACHINE EXAMPLE")
    print("="*70)

    # Create state machine
    state_machine = ResearchTaskStateMachine()
    print(f"\nInitial state: {state_machine.current_state.value}")

    # Valid transitions
    print("\n--- Valid Transitions ---")

    # Start research
    state_machine.transition(ResearchTaskState.RUNNING, "start")
    print(f"After 'start': {state_machine.current_state.value}")

    # Create checkpoint
    state_machine.transition(ResearchTaskState.CHECKPOINTED, "checkpoint")
    print(f"After 'checkpoint': {state_machine.current_state.value}")

    # Resume from checkpoint
    state_machine.transition(ResearchTaskState.RUNNING, "resume")
    print(f"After 'resume': {state_machine.current_state.value}")

    # Complete successfully
    state_machine.transition(ResearchTaskState.COMPLETED, "complete")
    print(f"After 'complete': {state_machine.current_state.value}")

    # Invalid transition example
    print("\n--- Invalid Transition Attempt ---")
    try:
        # Try to restart a completed task
        state_machine.transition(ResearchTaskState.RUNNING, "start")
    except ValueError as e:
        print(f"❌ Caught invalid transition:")
        print(f"\n{e}\n")

    # Show history
    print("--- State History ---")
    for record in state_machine.get_history():
        print(
            f"[{record.timestamp.strftime('%H:%M:%S')}] "
            f"{record.event:12s}: {record.from_state.value:12s} → {record.to_state.value}"
        )

    print("\n" + "="*70)


if __name__ == "__main__":
    example_usage()
