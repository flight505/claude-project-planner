#!/usr/bin/env bash
#
# SessionStart Hook for claude-project-planner
#
# This hook runs at the start of every Claude Code session.
# Provides helpful reminders about setup if dependencies are missing.
#

# Get the last user message to detect command invocation
LAST_MESSAGE="${CLAUDE_LAST_USER_MESSAGE:-}"

# Check if this is a /full-plan or /tech-plan invocation
if [[ "$LAST_MESSAGE" == *"/full-plan"* ]] || [[ "$LAST_MESSAGE" == *"full-plan"* ]] || \
   [[ "$LAST_MESSAGE" == *"/tech-plan"* ]] || [[ "$LAST_MESSAGE" == *"tech-plan"* ]]; then

    # Check if google-genai is installed (indicator that setup was run)
    if ! python3 -c "import google.genai" 2>/dev/null; then
        echo ""
        echo "⚠️  Setup Required"
        echo ""
        echo "Dependencies not found. Please run setup first:"
        echo "  /project-planner:setup"
        echo ""
        echo "This will:"
        echo "  • Validate your API keys"
        echo "  • Install all dependencies (including google-genai)"
        echo "  • Show available capabilities"
        echo ""
        echo "(This message appears because google-genai is not installed)"
        echo ""
    fi
fi

# Exit successfully (don't block session start)
exit 0
