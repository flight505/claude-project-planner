---
description: Generate a comprehensive project plan - accepts direct input, file reference, or interactive template
disable-model-invocation: false
---

# Full Project Plan Command

Generate a comprehensive project plan using all planning capabilities.

## Usage

```bash
# Option 1: Direct text input
/full-plan Build a DPP platform for EU compliance...

# Option 2: File reference
/full-plan @test_prompt.txt

# Option 3: No args (interactive template)
/full-plan
```

All options follow the same workflow:
1. **Create guide file** - Organize input into simple structure
2. **User reviews** - Verify guide captures intent
3. **Configuration** - 8 question groups for setup
4. **Generate plan** - Execute research and planning phases

## Workflow

### Step 1: Gather Input

**If args provided** (options 1 & 2):
- Parse the input text or file content
- Extract project name if possible (or generate one)
- Store raw input

**If no args** (option 3):
- Create planning template: `.{project_name}-plan-input.md`
- Open in user's editor ($EDITOR or nano)
- User fills template and saves
- Read completed template

### Step 2: Create Simple Guide File

Transform input into organized guide WITHOUT adding/assuming anything:

```bash
# Generate guide from raw input
python "${CLAUDE_PLUGIN_ROOT}/scripts/create-planning-guide.py" \
  --input "$RAW_INPUT" \
  --output ".{project_name}-guide.md"
```

**Guide format** (simple structured markdown):

```markdown
# Project Planning Guide
*Auto-generated from your input*

## What We're Building
[User's core description]

## Mentioned Details
**Target Users**: [extracted or "Not specified"]
**Goals**: [extracted or "Not specified"]
**Technical Notes**: [extracted or "Not specified"]
**Constraints**: [extracted or "Not specified"]
**Budget**: [extracted or "Not specified"]

---
## Original Input
[Complete raw input preserved here]
---

This guide will be used to create research prompts.
NO additional information has been added.
```

**Rules for guide creation**:
- ✅ Extract and organize what user provided
- ✅ Label things as "Not specified" if not mentioned
- ✅ Preserve complete original input
- ❌ NO assumptions or gap-filling
- ❌ NO adding information user didn't provide
- ❌ NO expanding on what was said

### Step 3: Review Guide (AskUserQuestion)

Show guide to user for approval:

```python
AskUserQuestion({
    "questions": [{
        "question": "Review your project guide. Does it accurately capture your input?",
        "header": "Verify Guide",
        "multiSelect": False,
        "options": [
            {
                "label": "Accept and proceed",
                "description": "Guide looks good, continue to configuration"
            },
            {
                "label": "Let me edit it",
                "description": "Open guide in editor for changes"
            },
            {
                "label": "Start over",
                "description": "Discard and re-enter project information"
            }
        ]
    }]
})
```

Display guide content in the question context so user can read it.

**Handle response**:
- **Accept**: Continue to Step 4
- **Edit**: Open `.{project_name}-guide.md` in editor, then re-show for approval
- **Start over**: Go back to Step 1

### Step 4: Configuration (8 Question Groups)

Present interactive setup covering ALL features:

```python
AskUserQuestion({
    "questions": [
        {
            "question": "Which AI provider for research?",
            "header": "Research Engine",
            "multiSelect": False,
            "options": [
                {
                    "label": "Balanced (Recommended)",
                    "description": "Gemini Deep Research for Phase 1, Perplexity for others"
                },
                {
                    "label": "Gemini Deep Research only",
                    "description": "Comprehensive 60-min research for all phases"
                },
                {
                    "label": "Perplexity only",
                    "description": "Fast 30-sec research for all phases"
                }
            ]
        },
        {
            "question": "Enable parallelization for faster execution?",
            "header": "Performance",
            "multiSelect": False,
            "options": [
                {
                    "label": "Yes (Recommended)",
                    "description": "Run independent tasks concurrently (~14% faster)"
                },
                {
                    "label": "No",
                    "description": "Sequential execution (simpler, more predictable)"
                }
            ]
        },
        {
            "question": "Pause for approval after each phase?",
            "header": "Workflow",
            "multiSelect": False,
            "options": [
                {
                    "label": "No - run all phases",
                    "description": "Fully autonomous execution (faster)"
                },
                {
                    "label": "Yes - interactive approval",
                    "description": "Review and approve after each phase"
                }
            ]
        },
        {
            "question": "Which planning phases to include?",
            "header": "Phases",
            "multiSelect": True,
            "options": [
                {
                    "label": "Phase 1: Market Research (Required)",
                    "description": "Competitive analysis, market sizing, trends"
                },
                {
                    "label": "Phase 2: Architecture (Required)",
                    "description": "System design, tech stack, building blocks"
                },
                {
                    "label": "Phase 3: Feasibility & Costs",
                    "description": "Risk assessment, cloud costs, ROI"
                },
                {
                    "label": "Phase 4: Implementation (Required)",
                    "description": "Sprint planning, milestones, timeline"
                },
                {
                    "label": "Phase 5: Go-to-Market",
                    "description": "Marketing strategy (skip for internal tools)"
                },
                {
                    "label": "Phase 6: Plan Review",
                    "description": "Final validation and gap analysis"
                }
            ]
        },
        {
            "question": "Enable quality checks?",
            "header": "Quality",
            "multiSelect": True,
            "options": [
                {
                    "label": "Multi-model architecture validation",
                    "description": "Validate architecture with Gemini + GPT + Claude consensus"
                },
                {
                    "label": "Generate comprehensive diagrams",
                    "description": "Create C4, sequence, ERD, deployment diagrams"
                },
                {
                    "label": "Building blocks for Claude Code",
                    "description": "Component specs in buildable YAML format"
                }
            ]
        },
        {
            "question": "Output formats?",
            "header": "Deliverables",
            "multiSelect": True,
            "options": [
                {
                    "label": "Markdown (always included)",
                    "description": "Human-readable documentation"
                },
                {
                    "label": "Generate PDF report",
                    "description": "Professional PDF with TOC, citations"
                },
                {
                    "label": "Generate PowerPoint slides",
                    "description": "Executive presentation deck"
                }
            ]
        }
    ]
})
```

Save configuration to `.{project_name}-config.json`.

### Step 5: Dependency Check

```bash
# Check dependencies are installed
if ! python -c "import google.genai" 2>/dev/null; then
    echo "⚠️ Dependencies not installed. Run: /project-planner:setup"
    exit 1
fi
```

### Step 5.5: Deep Research Budget Reminder

**⚠️ CRITICAL: Before starting execution, remember your Deep Research budget.**

You have **2 Deep Research queries maximum** for this entire `/full-plan` session.

**Budget Allocation Strategy:**

**Conservative (Recommended):**
- Phase 1: Use 1 Deep Research for competitive landscape/market analysis
- Phase 1: Use Perplexity for regulatory timeline (better temporal accuracy)
- Phase 2+: Use Perplexity or Gemini Pro only

**Aggressive (High-Stakes/Novel Projects):**
- Phase 1: Use 2 Deep Research for comprehensive market + competitive analysis
- Phase 2+: Use Perplexity or Gemini Pro only

**Rules:**
1. Deep Research is ONLY justified for:
   - Phase 1 competitive landscape with multiple competitors
   - Phase 1 market analysis requiring deep multi-source synthesis
   - Phase 2 architecture decisions IF technology is highly novel/uncertain

2. DEFAULT to Perplexity for:
   - Phase 1 regulatory timelines (better 2026 temporal accuracy)
   - Phase 2+ technology research (unless extremely novel)
   - All pricing, cost, version, feature lookups
   - Phases 3-6 research (Perplexity's real-time data is superior)

3. Track usage in: `planning_outputs/<project>/DEEP_RESEARCH_BUDGET.json`

**Before each Phase 1 query, explicitly decide:**
- "Is this query worth 30-60 minutes and 50% of my Deep Research budget?"
- "Can Perplexity or Gemini Pro provide sufficient depth?"

### Step 6: Execute Planning

Initialize progress tracking and budget:

```bash
PROJECT_DIR="planning_outputs/$(date +%Y%m%d_%H%M%S)_${PROJECT_NAME}"
mkdir -p "$PROJECT_DIR"

# Initialize progress tracker
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" init \
  "$PROJECT_DIR" "full" --name "$PROJECT_NAME"

# Initialize Deep Research budget tracker
python "${CLAUDE_PLUGIN_ROOT}/scripts/budget-tracker.py" init \
  "$PROJECT_DIR" --limit 2
```

Execute phases based on configuration:

**Phase 1: Market Research** (Required)
- Skills: `research-lookup`, `competitive-analysis`, `market-research-reports`
- Research mode from config (balanced/deep/perplexity)
- **Budget check**: Verify Deep Research budget before each query
- **Recommended allocation**: 1-2 Deep Research max, rest Perplexity
- If parallelization enabled: run research-lookup + competitive-analysis concurrently
- Output: `01_market_research/`

**Phase 2: Architecture** (Required)
- Skills: `architecture-research`, `building-blocks`, `project-diagrams`
- Uses findings from Phase 1
- If validation enabled: invoke `architecture-validator` agent
- Output: `02_architecture/`

**Phase 3: Feasibility & Costs** (Optional)
- Skills: `feasibility-analysis`, `risk-assessment`, `service-cost-analysis`
- If parallelization enabled: run all 3 concurrently (60% time savings!)
- Output: `03_feasibility/`

**Phase 4: Implementation** (Required)
- Skills: `sprint-planning`
- Creates sprints from building blocks
- Output: `04_implementation/`

**Phase 5: Go-to-Market** (Optional)
- Skills: `marketing-campaign`
- Skip for internal tools
- Output: `05_go_to_market/`

**Phase 6: Plan Review** (Optional)
- Skills: `plan-review`
- Final validation
- Output: `06_review/`

### Step 7: Generate Reports (if configured)

```bash
if [[ "$OUTPUTS" == *"PDF"* ]]; then
    /generate-report "$PROJECT_DIR" --format pdf
fi

if [[ "$OUTPUTS" == *"PowerPoint"* ]]; then
    /generate-report "$PROJECT_DIR" --format pptx
fi
```

### Step 8: Completion

```bash
# Finalize progress tracker
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" complete "$PROJECT_DIR" 6

# Show summary
echo ""
echo "✅ Planning complete!"
echo ""
echo "📁 Output directory: $PROJECT_DIR"
echo "📄 Executive summary: $PROJECT_DIR/00_executive_summary.md"
echo "📊 Progress report: $PROJECT_DIR/progress.md"
echo ""
```

## Example: test_prompt.txt Usage

```bash
/full-plan @test_prompt.txt
```

**Workflow**:
1. Reads test_prompt.txt content
2. Creates `.dpp-platform-guide.md` with extracted info
3. Shows guide: "Building DPP platform for EU compliance..."
4. User reviews → Accept
5. 8 configuration questions
6. Generates comprehensive plan in `planning_outputs/20260119_XXXXXX_dpp-platform/`

**No complex template, no gap-filling - just reorganize → review → configure → generate.**

## Notes

- Guide file is SIMPLE reorganization of input
- NO assumptions or additions made
- Original input always preserved
- User can edit guide before proceeding
- All 3 input methods follow same workflow
- Configuration happens AFTER guide approval
