#!/bin/bash
# Check and report on dependencies for Claude Project Planner
# This script runs on SessionStart to verify dependencies are available

# Check if requests module is available (required for research-lookup)
# Use uv if available (checks project virtual environment), otherwise fall back to python3
if command -v uv &> /dev/null && [ -f "${CLAUDE_PLUGIN_ROOT}/pyproject.toml" ]; then
    # Check in uv environment
    cd "${CLAUDE_PLUGIN_ROOT}" && uv run python -c "import requests" 2>/dev/null
    CHECK_RESULT=$?
else
    # Fall back to system python3
    python3 -c "import requests" 2>/dev/null
    CHECK_RESULT=$?
fi

if [ $CHECK_RESULT -ne 0 ]; then
    echo "⚠️  Python 'requests' module not installed."
    echo ""
    echo "   To install all plugin dependencies:"
    # Check if uv is available (preferred)
    if command -v uv &> /dev/null; then
        echo "   cd ${CLAUDE_PLUGIN_ROOT} && uv pip install -r requirements.txt"
    else
        echo "   pip install -r ${CLAUDE_PLUGIN_ROOT}/requirements.txt"
    fi
    echo ""
    echo "   Or run the setup command:"
    echo "   /project-planner:setup"
fi

# Check for OPENROUTER_API_KEY (required for research-lookup and AI diagrams)
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "ℹ️  OPENROUTER_API_KEY not set. Research-lookup and AI diagram generation will not work."
    echo "   Get an API key at: https://openrouter.ai/keys"
fi

# Check for Mermaid CLI (optional but recommended for diagram rendering)
if ! command -v mmdc &> /dev/null; then
    echo "ℹ️  Mermaid CLI (mmdc) not installed. Diagram rendering will use Kroki.io fallback."
    echo "   For best quality local rendering, install: npm install -g @mermaid-js/mermaid-cli"
fi

# Check for Pandoc (required for PDF/DOCX report generation)
if ! command -v pandoc &> /dev/null; then
    echo "ℹ️  Pandoc not installed. Report generation will be limited to Markdown format."
    echo "   For PDF/DOCX reports, install: brew install pandoc (macOS) or apt install pandoc (Linux)"
fi

# Silent success - don't clutter output if everything is fine
exit 0
