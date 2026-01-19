#!/bin/bash
# Smart Python executor - runs Python in the correct environment
# Uses uv if available, otherwise falls back to system Python
#
# Usage: ./scripts/run-in-env.sh <python-script> [args...]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Detect available tools
if command -v uv &> /dev/null; then
    # Use uv run to execute in project's virtual environment
    exec uv run python "$@"
elif [ -f ".venv/bin/python" ]; then
    # Use project's venv directly
    exec .venv/bin/python "$@"
else
    # Fall back to system Python
    exec python3 "$@"
fi
