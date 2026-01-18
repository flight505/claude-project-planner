#!/bin/bash
# Check and report on dependencies for Claude Project Planner
# This script runs on SessionStart to verify dependencies are available

# Check if requests module is available (required for research-lookup)
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Python 'requests' module not installed."
    echo ""
    echo "   To install all plugin dependencies:"
    # Check if uv is available (preferred)
    if command -v uv &> /dev/null; then
        echo "   uv pip install -r ${CLAUDE_PLUGIN_ROOT}/requirements.txt"
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
