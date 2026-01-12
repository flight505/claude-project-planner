#!/usr/bin/env bash
#
# create-plan-input.sh
# Creates a project planning input template and opens it for editing
#
# Usage:
#   ./scripts/create-plan-input.sh [project-name]
#

set -euo pipefail

# Get plugin root directory
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$0")")}"
TEMPLATE_FILE="$PLUGIN_ROOT/templates/plan-input-template.md"

# Get project name from argument or use default
PROJECT_NAME="${1:-.plan-input}"

# Determine output file location
if [[ "$PROJECT_NAME" == .* ]]; then
    # Hidden file in current directory
    OUTPUT_FILE="$PROJECT_NAME.md"
else
    # Use project name
    OUTPUT_FILE=".${PROJECT_NAME}-plan-input.md"
fi

# Check if template exists
if [[ ! -f "$TEMPLATE_FILE" ]]; then
    echo "Error: Template file not found: $TEMPLATE_FILE" >&2
    exit 1
fi

# Check if output file already exists
if [[ -f "$OUTPUT_FILE" ]]; then
    echo "File $OUTPUT_FILE already exists."
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Using existing file: $OUTPUT_FILE"
        # Still open the existing file
        exec "${EDITOR:-nano}" "$OUTPUT_FILE"
    fi
fi

# Copy template to output file
cp "$TEMPLATE_FILE" "$OUTPUT_FILE"
echo "Created planning input file: $OUTPUT_FILE"

# Determine editor to use
EDITOR_CMD="${EDITOR:-nano}"

# Special handling for common editors
case "$EDITOR_CMD" in
    code|"code --wait")
        # VS Code
        code --wait "$OUTPUT_FILE"
        ;;
    vim|nvim|vi)
        # Vim family
        "$EDITOR_CMD" "$OUTPUT_FILE"
        ;;
    emacs)
        # Emacs
        emacs "$OUTPUT_FILE"
        ;;
    nano|pico)
        # Nano/Pico
        nano "$OUTPUT_FILE"
        ;;
    *)
        # Default: use whatever is in $EDITOR
        "$EDITOR_CMD" "$OUTPUT_FILE"
        ;;
esac

# Validate the file was actually edited
if [[ ! -s "$OUTPUT_FILE" ]]; then
    echo "Warning: File appears to be empty" >&2
    exit 1
fi

# Check if file still has template placeholders
if grep -q "\[Your project name\]" "$OUTPUT_FILE"; then
    echo ""
    echo "⚠️  Warning: It looks like you haven't filled out the template."
    echo "   Please replace the [placeholder] values with your actual project details."
    echo ""
    read -p "Edit again? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # Re-open the file
        exec "$0" "$PROJECT_NAME"
    fi
fi

echo ""
echo "✓ Planning input saved to: $OUTPUT_FILE"
echo ""
echo "Next step: Run the parser to validate and extract your input:"
echo "  python ${PLUGIN_ROOT}/scripts/parse-plan-input.py $OUTPUT_FILE"
echo ""
