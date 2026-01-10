#!/bin/bash
# Quality Gate Validator for Planning Outputs
# Runs as PostToolUse hook on Write operations
# Returns warnings but doesn't block (non-zero exit is informational)

FILE_PATH="$1"
CONTENT="$2"

# Only validate files in planning_outputs/
if [[ ! "$FILE_PATH" =~ planning_outputs/ ]]; then
    exit 0
fi

# Skip non-markdown and non-yaml files
if [[ ! "$FILE_PATH" =~ \.(md|yaml|yml|json)$ ]]; then
    exit 0
fi

WARNINGS=""
WARNING_COUNT=0

# ============================================
# Check 1: Placeholder Text Detection
# ============================================
check_placeholders() {
    local placeholders=(
        "\[TODO\]"
        "\[TBD\]"
        "\[PLACEHOLDER\]"
        "\[INSERT\]"
        "\[ADD\]"
        "\[source needed\]"
        "\[citation needed\]"
        "\[FIXME\]"
        "Lorem ipsum"
        "example\.com"
        "xxx"
        "TBD"
    )

    for pattern in "${placeholders[@]}"; do
        if echo "$CONTENT" | grep -iqE "$pattern"; then
            WARNINGS="${WARNINGS}⚠️  Placeholder detected: Pattern '$pattern' found in output\n"
            ((WARNING_COUNT++))
        fi
    done
}

# ============================================
# Check 2: Research Output Validation
# ============================================
check_research_quality() {
    # Only check research-related files
    if [[ "$FILE_PATH" =~ (research|market|competitive|analysis) ]]; then
        # Check for citations (should have [1], [2] style or source links)
        if ! echo "$CONTENT" | grep -qE '\[\d+\]|https?://|Source:|Reference:'; then
            # Only warn if file is substantial (>500 chars)
            if [ ${#CONTENT} -gt 500 ]; then
                WARNINGS="${WARNINGS}⚠️  Research file may be missing citations or sources\n"
                ((WARNING_COUNT++))
            fi
        fi

        # Check for data substantiation (numbers should have context)
        if echo "$CONTENT" | grep -qE '\$[0-9]+[BMK]|\d+%' && ! echo "$CONTENT" | grep -qiE 'source|according|based on|reported|estimated'; then
            WARNINGS="${WARNINGS}ℹ️  Statistics found without attribution - consider adding sources\n"
        fi
    fi
}

# ============================================
# Check 3: Building Blocks Validation
# ============================================
check_building_blocks() {
    if [[ "$FILE_PATH" =~ building_blocks\.(yaml|yml)$ ]]; then
        # Check for required fields in YAML
        if ! echo "$CONTENT" | grep -qE '^  - name:|^    name:'; then
            WARNINGS="${WARNINGS}⚠️  Building blocks YAML may be missing 'name' fields\n"
            ((WARNING_COUNT++))
        fi

        if ! echo "$CONTENT" | grep -qE 'estimated_hours|story_points'; then
            WARNINGS="${WARNINGS}⚠️  Building blocks should include effort estimates (estimated_hours or story_points)\n"
            ((WARNING_COUNT++))
        fi

        if ! echo "$CONTENT" | grep -qE 'dependencies:|interfaces:'; then
            WARNINGS="${WARNINGS}ℹ️  Consider adding dependencies and interfaces to building blocks\n"
        fi
    fi
}

# ============================================
# Check 4: Cost Analysis Validation
# ============================================
check_cost_analysis() {
    if [[ "$FILE_PATH" =~ (cost|pricing|budget) ]]; then
        # Check for unrealistic costs (< $1 or > $1M monthly for typical services)
        if echo "$CONTENT" | grep -qE '\$0\.[0-9]+/month|\$0/month'; then
            WARNINGS="${WARNINGS}⚠️  Cost estimate seems too low - verify pricing data\n"
            ((WARNING_COUNT++))
        fi

        # Check that costs have breakdown
        if echo "$CONTENT" | grep -qE 'Total.*\$' && ! echo "$CONTENT" | grep -qiE 'breakdown|itemized|per service|monthly'; then
            WARNINGS="${WARNINGS}ℹ️  Cost totals should include itemized breakdown\n"
        fi
    fi
}

# ============================================
# Check 5: Sprint Planning Validation
# ============================================
check_sprint_planning() {
    if [[ "$FILE_PATH" =~ (sprint|planning|milestone) ]]; then
        # Check for INVEST criteria mentions or story structure
        if echo "$CONTENT" | grep -qiE 'user story|as a .*, i want' && ! echo "$CONTENT" | grep -qiE 'acceptance criteria|definition of done|story points'; then
            WARNINGS="${WARNINGS}ℹ️  User stories should include acceptance criteria and story points\n"
        fi
    fi
}

# ============================================
# Check 6: General Quality Checks
# ============================================
check_general_quality() {
    # Check for very short outputs (might be incomplete)
    if [ ${#CONTENT} -lt 200 ] && [[ "$FILE_PATH" =~ \.(md)$ ]]; then
        # Skip progress files and small config files
        if [[ ! "$FILE_PATH" =~ (progress|config|index) ]]; then
            WARNINGS="${WARNINGS}ℹ️  Output seems short (${#CONTENT} chars) - may be incomplete\n"
        fi
    fi

    # Check for markdown structure in .md files
    if [[ "$FILE_PATH" =~ \.md$ ]] && [ ${#CONTENT} -gt 1000 ]; then
        if ! echo "$CONTENT" | grep -qE '^#{1,3} '; then
            WARNINGS="${WARNINGS}ℹ️  Long markdown file without headers - consider adding structure\n"
        fi
    fi
}

# ============================================
# Run All Checks
# ============================================
check_placeholders
check_research_quality
check_building_blocks
check_cost_analysis
check_sprint_planning
check_general_quality

# ============================================
# Output Results
# ============================================
if [ -n "$WARNINGS" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Quality Gate Check: $(basename "$FILE_PATH")"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "$WARNINGS"

    if [ $WARNING_COUNT -gt 0 ]; then
        echo "Found $WARNING_COUNT quality warning(s). Output was saved but review recommended."
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# Always exit 0 to not block the Write operation
# Warnings are informational, not blocking
exit 0
