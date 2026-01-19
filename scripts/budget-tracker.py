#!/usr/bin/env python3
"""
Deep Research Budget Tracker

Enforces the 2-query limit for Deep Research per /full-plan session.

Usage:
    # Initialize budget for new project
    python budget-tracker.py init <project_dir> --limit 2

    # Check remaining budget before query
    python budget-tracker.py check <project_dir> [--model deep-research-pro-preview]

    # Record Deep Research usage
    python budget-tracker.py record <project_dir> <query_summary> --duration 3600

    # Get current status
    python budget-tracker.py status <project_dir>
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


BUDGET_FILENAME = "DEEP_RESEARCH_BUDGET.json"


def init_budget(project_dir: Path, limit: int = 2) -> Dict:
    """Initialize budget tracker for a new project."""
    # Create project directory if it doesn't exist
    project_dir.mkdir(parents=True, exist_ok=True)

    budget_file = project_dir / BUDGET_FILENAME

    if budget_file.exists():
        print(f"⚠️  Budget file already exists: {budget_file}", file=sys.stderr)
        return json.loads(budget_file.read_text())

    budget_data = {
        "limit": limit,
        "used": 0,
        "remaining": limit,
        "queries": [],
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }

    budget_file.write_text(json.dumps(budget_data, indent=2))
    print(f"✅ Budget initialized: {limit} Deep Research queries available")
    print(f"📁 Tracker: {budget_file}")

    return budget_data


def load_budget(project_dir: Path) -> Optional[Dict]:
    """Load existing budget data."""
    budget_file = project_dir / BUDGET_FILENAME

    if not budget_file.exists():
        return None

    return json.loads(budget_file.read_text())


def save_budget(project_dir: Path, budget_data: Dict):
    """Save updated budget data."""
    budget_file = project_dir / BUDGET_FILENAME
    budget_data["last_updated"] = datetime.now().isoformat()
    budget_file.write_text(json.dumps(budget_data, indent=2))


def check_budget(project_dir: Path, model_name: Optional[str] = None) -> bool:
    """Check if Deep Research budget is available.

    Returns:
        True if budget available, False if exhausted
    """
    budget_data = load_budget(project_dir)

    if not budget_data:
        print(f"⚠️  No budget file found. Run: budget-tracker.py init {project_dir}", file=sys.stderr)
        return False

    remaining = budget_data["remaining"]
    used = budget_data["used"]
    limit = budget_data["limit"]

    if remaining <= 0:
        print(f"❌ Deep Research budget exhausted ({used}/{limit} used)", file=sys.stderr)
        print(f"", file=sys.stderr)
        print(f"Fallback options:", file=sys.stderr)
        print(f"  1. Use Gemini Pro (high quality, 1-5 min)", file=sys.stderr)
        print(f"  2. Use Perplexity Sonar (fast, 30 sec)", file=sys.stderr)
        print(f"", file=sys.stderr)
        return False

    # Display warning if on last query
    if remaining == 1:
        print(f"⚠️  Deep Research budget: {used}/{limit} used - LAST QUERY AVAILABLE", file=sys.stderr)
        print(f"⚠️  Use this query wisely! Consider if Perplexity/Gemini Pro would suffice.", file=sys.stderr)
    else:
        print(f"✅ Deep Research budget: {used}/{limit} used, {remaining} remaining", file=sys.stderr)

    return True


def record_usage(
    project_dir: Path,
    query_summary: str,
    duration_seconds: float,
    model_name: str = "gemini-deep-research",
    phase: Optional[int] = None,
    task_type: Optional[str] = None
):
    """Record Deep Research query usage."""
    budget_data = load_budget(project_dir)

    if not budget_data:
        print(f"⚠️  No budget file found. Initializing with limit 2...", file=sys.stderr)
        budget_data = init_budget(project_dir, limit=2)

    # Record query
    query_entry = {
        "timestamp": datetime.now().isoformat(),
        "query_summary": query_summary[:200],  # Truncate for storage
        "duration_seconds": duration_seconds,
        "duration_minutes": round(duration_seconds / 60, 1),
        "model": model_name,
        "phase": phase,
        "task_type": task_type
    }

    budget_data["queries"].append(query_entry)
    budget_data["used"] = len(budget_data["queries"])
    budget_data["remaining"] = budget_data["limit"] - budget_data["used"]

    save_budget(project_dir, budget_data)

    # Display status
    used = budget_data["used"]
    limit = budget_data["limit"]
    remaining = budget_data["remaining"]

    print(f"", file=sys.stderr)
    print(f"📊 Deep Research budget updated:", file=sys.stderr)
    print(f"   Used: {used}/{limit}", file=sys.stderr)
    print(f"   Remaining: {remaining}", file=sys.stderr)

    if remaining == 0:
        print(f"", file=sys.stderr)
        print(f"⚠️  Budget exhausted! All future research will use Gemini Pro or Perplexity.", file=sys.stderr)
    elif remaining == 1:
        print(f"", file=sys.stderr)
        print(f"⚠️  Only 1 query remaining - use it for the most critical analysis!", file=sys.stderr)


def get_status(project_dir: Path) -> Dict:
    """Get current budget status."""
    budget_data = load_budget(project_dir)

    if not budget_data:
        print(f"❌ No budget file found: {project_dir / BUDGET_FILENAME}", file=sys.stderr)
        sys.exit(1)

    used = budget_data["used"]
    limit = budget_data["limit"]
    remaining = budget_data["remaining"]

    print(f"")
    print(f"📊 Deep Research Budget Status")
    print(f"{'=' * 50}")
    print(f"Project: {project_dir.name}")
    print(f"Limit: {limit} queries")
    print(f"Used: {used}")
    print(f"Remaining: {remaining}")
    print(f"")

    if budget_data["queries"]:
        print(f"Query History:")
        print(f"{'-' * 50}")
        for i, query in enumerate(budget_data["queries"], 1):
            duration = query.get("duration_minutes", "?")
            phase = query.get("phase", "?")
            task = query.get("task_type", "general")
            summary = query["query_summary"][:60]
            print(f"{i}. [{duration} min] Phase {phase} - {task}")
            print(f"   {summary}...")
            print(f"")
    else:
        print(f"No queries recorded yet.")
        print(f"")

    return budget_data


def main():
    parser = argparse.ArgumentParser(
        description="Deep Research Budget Tracker"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize budget tracker")
    init_parser.add_argument("project_dir", type=Path)
    init_parser.add_argument("--limit", type=int, default=2)

    # Check command
    check_parser = subparsers.add_parser("check", help="Check remaining budget")
    check_parser.add_argument("project_dir", type=Path)
    check_parser.add_argument("--model", type=str, default="deep-research-pro-preview")

    # Record command
    record_parser = subparsers.add_parser("record", help="Record query usage")
    record_parser.add_argument("project_dir", type=Path)
    record_parser.add_argument("query_summary", type=str)
    record_parser.add_argument("--duration", type=float, required=True, help="Duration in seconds")
    record_parser.add_argument("--model", type=str, default="gemini-deep-research")
    record_parser.add_argument("--phase", type=int)
    record_parser.add_argument("--task-type", type=str)

    # Status command
    status_parser = subparsers.add_parser("status", help="Get current status")
    status_parser.add_argument("project_dir", type=Path)

    args = parser.parse_args()

    # Execute command
    if args.command == "init":
        init_budget(args.project_dir, args.limit)

    elif args.command == "check":
        available = check_budget(args.project_dir, args.model)
        sys.exit(0 if available else 1)

    elif args.command == "record":
        record_usage(
            args.project_dir,
            args.query_summary,
            args.duration,
            args.model,
            args.phase,
            getattr(args, 'task_type', None)
        )

    elif args.command == "status":
        get_status(args.project_dir)


if __name__ == "__main__":
    main()
