#!/usr/bin/env python3
"""
Wait for background dependency installation to complete.

This script blocks until the ensure-dependencies.sh background process
completes or times out. It displays progress to the user and handles
various completion states (success, failure, timeout).

Usage:
    python scripts/wait-for-dependencies.py [--timeout SECONDS] [--quiet]

Exit codes:
    0 - Dependencies installed successfully
    1 - Installation failed
    2 - Installation timed out
    3 - Installation not started
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional


# Default configuration
DEFAULT_STATUS_FILE = Path(f"{Path.home()}/../../../tmp/claude-planner-deps-status.json")
if not DEFAULT_STATUS_FILE.exists():
    # Fallback to /tmp
    DEFAULT_STATUS_FILE = Path("/tmp/claude-planner-deps-status.json")

DEFAULT_LOG_FILE = Path(f"{Path.home()}/../../../tmp/claude-planner-deps.log")
if not DEFAULT_LOG_FILE.exists():
    DEFAULT_LOG_FILE = Path("/tmp/claude-planner-deps.log")

DEFAULT_TIMEOUT = 600  # 10 minutes
POLL_INTERVAL = 2  # Check every 2 seconds


def read_status(status_file: Path) -> Optional[dict]:
    """Read the current status from the status file."""
    try:
        if not status_file.exists():
            return None

        with open(status_file, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not read status file: {e}", file=sys.stderr)
        return None


def format_progress_bar(progress: int, width: int = 40) -> str:
    """Format a text-based progress bar."""
    filled = int(width * progress / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress}%"


def display_progress(status: dict, quiet: bool = False) -> None:
    """Display current installation progress."""
    if quiet:
        return

    progress = status.get("progress", 0)
    current = status.get("current", "")
    status_text = status.get("status", "unknown")

    # Clear line and display progress
    print(f"\r{format_progress_bar(progress)}", end="")

    if current and status_text == "installing":
        print(f" Installing: {current}", end="")

    sys.stdout.flush()


def wait_for_completion(
    status_file: Path,
    timeout: int = DEFAULT_TIMEOUT,
    quiet: bool = False,
) -> int:
    """
    Wait for dependency installation to complete.

    Returns:
        Exit code (0 = success, 1 = failure, 2 = timeout, 3 = not started)
    """
    start_time = time.time()
    last_progress = -1

    # Check if installation has started
    initial_status = read_status(status_file)
    if initial_status is None:
        if not quiet:
            print("Dependency installation has not started yet.")
            print("Waiting for background installer to initialize...")

        # Wait a bit for installer to start
        for _ in range(10):  # Wait up to 10 seconds
            time.sleep(1)
            initial_status = read_status(status_file)
            if initial_status is not None:
                break

        if initial_status is None:
            print("\nError: Dependency installation did not start.", file=sys.stderr)
            print("Run this command to start installation:", file=sys.stderr)
            print("  ./scripts/ensure-dependencies.sh", file=sys.stderr)
            return 3

    if not quiet:
        print("Waiting for dependency installation to complete...")
        print()

    # Poll for completion
    while True:
        # Check timeout
        elapsed = time.time() - start_time
        if elapsed > timeout:
            if not quiet:
                print("\n")
                print(f"Error: Installation timed out after {timeout} seconds.", file=sys.stderr)
            return 2

        # Read current status
        status = read_status(status_file)
        if status is None:
            time.sleep(POLL_INTERVAL)
            continue

        current_status = status.get("status", "unknown")
        progress = status.get("progress", 0)

        # Display progress if changed
        if progress != last_progress:
            display_progress(status, quiet)
            last_progress = progress

        # Check completion states
        if current_status == "complete":
            if not quiet:
                print("\n")
                print("✓ All dependencies installed successfully!")
            return 0

        elif current_status == "partial":
            if not quiet:
                print("\n")
                print("⚠ Installation completed with some failures.", file=sys.stderr)
                failed = status.get("current", "")
                if failed:
                    print(f"Failed packages: {failed}", file=sys.stderr)

                log_file = status.get("log_file", str(DEFAULT_LOG_FILE))
                print(f"\nCheck log file for details: {log_file}", file=sys.stderr)
            return 1

        elif current_status == "timeout":
            if not quiet:
                print("\n")
                print("Error: Installation timed out.", file=sys.stderr)
            return 2

        elif current_status in ["installing", "starting"]:
            # Still in progress, continue waiting
            time.sleep(POLL_INTERVAL)
            continue

        else:
            # Unknown status
            if not quiet:
                print(f"\nWarning: Unknown status: {current_status}", file=sys.stderr)
            time.sleep(POLL_INTERVAL)


def main():
    parser = argparse.ArgumentParser(
        description="Wait for background dependency installation to complete"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Maximum time to wait in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--status-file",
        type=Path,
        default=DEFAULT_STATUS_FILE,
        help="Path to status file",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Check status and exit immediately (don't wait)",
    )

    args = parser.parse_args()

    if args.check_only:
        # Just check current status
        status = read_status(args.status_file)
        if status is None:
            print("Status: Not started")
            return 3
        else:
            print(f"Status: {status.get('status', 'unknown')}")
            print(f"Progress: {status.get('progress', 0)}%")
            if status.get("current"):
                print(f"Current: {status['current']}")
            return 0 if status.get("status") == "complete" else 1

    # Wait for completion
    return wait_for_completion(
        status_file=args.status_file,
        timeout=args.timeout,
        quiet=args.quiet,
    )


if __name__ == "__main__":
    sys.exit(main())
