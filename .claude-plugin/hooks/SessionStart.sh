#!/usr/bin/env bash
#
# SessionStart Hook for claude-project-planner
#
# This hook runs at the start of every Claude Code session.
# It detects if /full-plan is being invoked and starts background
# dependency installation to ensure all requirements are met.
#

# Get the last user message to detect command invocation
LAST_MESSAGE="${CLAUDE_LAST_USER_MESSAGE:-}"

# Check if this is a /full-plan invocation
if [[ "$LAST_MESSAGE" == *"/full-plan"* ]] || [[ "$LAST_MESSAGE" == *"full-plan"* ]]; then
    echo "[SessionStart] Detected /full-plan invocation"

    # Check if dependency installation should run
    # Skip if already running or recently completed
    STATUS_FILE="${TMPDIR:-/tmp}/claude-planner-deps-status.json"

    if [[ -f "$STATUS_FILE" ]]; then
        # Check if installation is already complete or in progress
        STATUS=$(python3 -c "import json; print(json.load(open('$STATUS_FILE')).get('status', 'unknown'))" 2>/dev/null || echo "unknown")

        if [[ "$STATUS" == "complete" ]]; then
            # Check if status is recent (less than 1 hour old)
            if [[ $(find "$STATUS_FILE" -mmin -60 2>/dev/null) ]]; then
                echo "[SessionStart] Dependencies already installed (status file is recent)"
                exit 0
            fi
        elif [[ "$STATUS" == "installing" ]]; then
            echo "[SessionStart] Dependency installation already in progress"
            exit 0
        fi
    fi

    # Start background dependency installation
    echo "[SessionStart] Starting background dependency installation..."

    # Run installer in background with nohup
    nohup "${CLAUDE_PLUGIN_ROOT}/scripts/ensure-dependencies.sh" full \
        > "${TMPDIR:-/tmp}/claude-planner-deps.log" 2>&1 &

    # Store PID for potential cleanup
    echo $! > "${TMPDIR:-/tmp}/claude-planner-deps.pid"

    echo "[SessionStart] Background installation started (PID: $!)"
    echo "[SessionStart] Check status with: python ${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-dependencies.py --check-only"
fi

# Exit successfully (don't block session start)
exit 0
