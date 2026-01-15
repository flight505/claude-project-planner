---
description: Generate a comprehensive project plan using all planning skills - architecture, research, building blocks, costs, risks, sprints, and go-to-market strategy
---

# Full Project Plan Command

When the user invokes `/full-plan`, generate a **comprehensive project plan** by systematically using all relevant planning skills.

## Interactive Setup Workflow

The `/full-plan` command uses an interactive setup process to gather comprehensive project details:

### Step 1: Create Planning Input Template

Generate and open a detailed planning input template:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/create-plan-input.sh" "<project_name>"
```

This creates a `.{project_name}-plan-input.md` file and opens it in the user's editor (`$EDITOR` or nano).

**The template includes sections for:**
- Project Overview (name, description)
- Target Audience (users, personas, market)
- Goals & Success Metrics
- Technical Requirements (features, integrations, data, compliance)
- Constraints (timeline, budget, team, scalability)
- Technology Preferences (stack, cloud, approach)
- Go-to-Market Strategy
- Additional Context (risks, assumptions, etc.)

**User Action Required:** User fills out the template with their project details and saves the file.

### Step 2: Dependency Check

The **SessionStart hook** checks if dependencies are installed:

```bash
# Runs automatically via hooks/SessionStart.sh
# Checks if google-genai is installed (indicator that setup was run)
if ! python3 -c "import google.genai" 2>/dev/null; then
    echo "⚠️  Setup Required"
    echo "Please run: /project-planner:setup"
fi
```

**If dependencies are missing**, user must run `/project-planner:setup` first, which:
- Validates API keys with real API calls
- Installs ALL dependencies (google-genai, openai, markitdown, etc.)
- Shows capability matrix based on available providers
- Configures the environment

### Step 3: Parse and Validate Input

After the user saves and closes the template, parse and validate their input:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/parse-plan-input.py" \
  ".{project_name}-plan-input.md" \
  --validate \
  --output ".{project_name}-plan-data.json"
```

**Validation checks:**
- Project Name (required)
- Description (required)
- Primary Users (required)
- Primary Objective (required)
- Core Features (required)

If validation fails, prompt the user to complete missing fields.

### Step 4: Comprehensive Interactive Configuration

Present **all planning capabilities** in one guided setup flow, eliminating need to remember flags:

```bash
# Generate comprehensive setup questions
SETUP_QUESTIONS=$(python "${CLAUDE_PLUGIN_ROOT}/scripts/setup-planning-config.py")

# Present to user via AskUserQuestion
# (This displays 6 question groups covering all features)
```

**Setup Questions Presented:**

1. **AI Provider Selection**
   - Google Gemini Deep Research (most comprehensive, requires API key + subscription)
   - Perplexity via OpenRouter (fast, pay-per-use)
   - Auto-detect from available keys

2. **Performance Optimization**
   - Enable parallelization (~14% overall time savings, 60% in Phase 3)
   - Sequential execution (simpler, more predictable)

3. **Interactive Approval Gates** ⭐ **NEW**
   - Pause after each phase for review and approval
   - Ability to revise phases if direction needs adjustment
   - Best for critical projects where user wants control

4. **Phase Selection** ⭐ **NEW**
   - Choose which phases to include (multiSelect)
   - Phase 1: Market Research (required)
   - Phase 2: Architecture (required)
   - Phase 3: Feasibility & Costs (recommended)
   - Phase 4: Implementation Planning (required)
   - Phase 5: Go-to-Market Strategy (optional - skip for internal tools)
   - Phase 6: Plan Review (recommended)

5. **Quality Checks** ⭐ **NEW**
   - Multi-model architecture validation
   - Comprehensive diagram generation
   - Real-time research verification
   - None (standard quality only)

6. **Output Formats** ⭐ **NEW**
   - Markdown + YAML (always included)
   - Generate PDF report (professional documentation)
   - Generate PowerPoint presentation (executive summary)

**Parse User Selections:**

```bash
# Parse answers into configuration
CONFIG=$(python "${CLAUDE_PLUGIN_ROOT}/scripts/setup-planning-config.py" parse "$USER_ANSWERS")

# Save configuration for execution
CONFIG_FILE=".${project_name}-config.json"
echo "$CONFIG" > "$CONFIG_FILE"

# Display configuration summary
python "${CLAUDE_PLUGIN_ROOT}/scripts/setup-planning-config.py" summary "$CONFIG_FILE"
```

**Example Configuration Summary:**

```
======================================================================
Planning Configuration Summary
======================================================================

AI Provider: GEMINI
Parallelization: ENABLED
Interactive Mode: ENABLED

Phases:
  ✓ Phase 1: Market Research
  ✓ Phase 2: Architecture & Design
  ✓ Phase 3: Feasibility & Costs
  ✓ Phase 4: Implementation Planning
  ✗ Phase 5: Go-to-Market Strategy (skipped)
  ✓ Phase 6: Plan Review

Quality Checks:
  ✓ Multi-model validation
  ✓ Comprehensive diagrams

Output Formats:
  ✓ Markdown (always)
  ✓ YAML building blocks (always)
  ✓ PDF report

======================================================================
```

This setup replaces all command-line flags. Users discover all features interactively without reading documentation.

### Step 5: Begin Planning Execution

With all input gathered and dependencies ready, proceed to Phase 1.

## Legacy Input Method (Backward Compatible)

For quick planning without the interactive template, you can still provide input via command arguments:

```
/full-plan <project_name> --description "Brief description" --users "Target users"
```

Or the system will prompt for required fields using AskUserQuestion if not provided.

## Required Input (Summary)

Before starting execution, ensure you have:
1. **Project name and description** - What are we building?
2. **Target audience** - Who is this for?
3. **Key goals** - What problem does it solve?
4. **Timeline constraints** - Any deadlines?
5. **Budget constraints** - Any budget limits?

These are gathered via the interactive template or legacy prompts.

## Optional Flags

| Flag | Description |
|------|-------------|
| `--parallel` | Enable smart parallelization of independent tasks within phases |
| `--validate` | Run multi-model architecture validation after Phase 2 |
| `--skip-marketing` | Skip Phase 5 (Go-to-Market) - equivalent to `/tech-plan` |

### Smart Parallelization (--parallel)

When `--parallel` is specified, independent tasks within each phase run concurrently:

**Parallel Task Groups:**

| Phase | Parallel Tasks | Sequential Tasks | Time Savings |
|-------|---------------|------------------|--------------|
| Phase 1 | research-lookup + competitive-analysis | market-research-reports, diagrams | ~33% |
| Phase 2 | *(none - sequential dependencies)* | all | 0% |
| Phase 3 | feasibility + risk + cost | diagrams | ~60% |
| Phase 4 | *(none - sequential dependencies)* | all | 0% |
| Phase 5 | *(none - sequential dependencies)* | all | 0% |
| Phase 6 | *(none - sequential dependencies)* | all | 0% |

**Total estimated time savings: ~14%** (biggest win in Phase 3)

**How it works:**

1. Before each phase, prepare input context from previous phases:
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/parallel-orchestrator.py" input-context \
     "planning_outputs/<project_name>" <phase_num>
   ```

2. Get execution plan showing parallel/sequential groups:
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/parallel-orchestrator.py" plan \
     "planning_outputs/<project_name>" <phase_num>
   ```

3. **For parallel groups**: Launch all tasks simultaneously using parallel tool calls
4. **For sequential groups**: Wait for dependencies, then execute in order
5. After each group, merge outputs into phase context:
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/parallel-orchestrator.py" merge-context \
     "planning_outputs/<project_name>" <phase_num>
   ```

**Context Sharing:**

Parallel tasks share context via `.context/` directory:
```
planning_outputs/<project_name>/
├── .context/
│   ├── phase1_input.md    # Context from prior phases
│   ├── phase1_output.md   # Key findings from Phase 1
│   ├── phase2_input.md    # = phase1_output + additions
│   └── ...
```

**Error Handling:**
- Failed parallel tasks don't cascade to other parallel tasks
- Failed tasks are marked in state for retry
- Phase continues with successful tasks, reports failures at end

### Multi-Model Validation (--validate)

When `--validate` is specified, after completing Phase 2 (Architecture):

1. **Invoke the `architecture-validator` agent**
2. The agent queries multiple AI models (Gemini, GPT-4o, Claude) for consensus
3. Each model evaluates architecture decisions on:
   - Scalability (1-10)
   - Security risk (1-10)
   - Cost effectiveness (1-10)
   - Maintainability (1-10)
4. A validation report is generated: `02_architecture/validation_report.md`

**If any decision is "rejected" by consensus**, pause and ask user before proceeding to Phase 3.

```bash
# Run validation script directly
python "${CLAUDE_PLUGIN_ROOT}/scripts/multi-model-validator.py" \
  --architecture-file "planning_outputs/<project_name>/02_architecture/architecture_document.md" \
  --building-blocks "planning_outputs/<project_name>/02_architecture/building_blocks.md" \
  --output "planning_outputs/<project_name>/02_architecture/validation_report.md"
```

## Output Structure

Create all outputs in: `planning_outputs/<project_name>/`

```
planning_outputs/<project_name>/
├── 00_executive_summary.md          # High-level overview
├── 01_market_research/
│   ├── competitive_analysis.md      # From competitive-analysis skill
│   ├── market_overview.md           # From market-research-reports skill
│   └── diagrams/
├── 02_architecture/
│   ├── architecture_document.md     # From architecture-research skill
│   ├── building_blocks.md           # From building-blocks skill
│   └── diagrams/
├── 03_feasibility/
│   ├── feasibility_analysis.md      # From feasibility-analysis skill
│   ├── risk_assessment.md           # From risk-assessment skill
│   └── service_cost_analysis.md     # From service-cost-analysis skill
├── 04_implementation/
│   ├── sprint_plan.md               # From sprint-planning skill
│   └── milestones.md
├── 05_go_to_market/
│   ├── marketing_campaign.md        # From marketing-campaign skill
│   ├── content_calendar.md
│   └── diagrams/
├── 06_review/
│   └── plan_review.md               # From plan-review skill
└── diagrams/                         # All generated diagrams
```

## Execution Phases

Execute these phases IN ORDER. Each phase uses specific skills.

### Phase 1: Research & Market Analysis
**Skills to use:** `research-lookup`, `competitive-analysis`, `market-research-reports`

**Research Mode Configuration:**

Read the `research_mode` from the configuration file:

```bash
RESEARCH_MODE=$(jq -r '.research_mode' "$CONFIG_FILE")
```

**Research mode affects how Phase 1 research is conducted:**

- **`balanced` (Recommended)**: Use Gemini Deep Research for `competitive-analysis` and `market-research-reports`. Use Perplexity for quick `research-lookup` queries.
- **`perplexity`**: Use Perplexity for all research (fast, 30 seconds/query)
- **`deep_research`**: Use Gemini Deep Research for all tasks (comprehensive, 60 min/query)
- **`auto`**: Let ResearchLookup automatically select based on query complexity

**With `--parallel` flag:**
```
Group 1.1 (PARALLEL): research-lookup + competitive-analysis
Group 1.2 (sequential): market-research-reports (uses Group 1.1 context)
Group 1.3 (sequential): project-diagrams
```

1. **Market Research + Competitive Analysis** *(can run in parallel)*

   **Quick lookups (research-lookup):**
   - Use `research-lookup` to gather industry data, trends, and benchmarks
   - Pass research mode context: `--research-mode "$RESEARCH_MODE" --phase 1 --task-type research-lookup`
   - For balanced/auto modes, this uses Perplexity (fast queries)
   - Output: `01_market_research/market_data.md`

   **Competitive analysis:**
   - Use `competitive-analysis` skill to analyze competitors
   - Pass research mode context: `--research-mode "$RESEARCH_MODE" --phase 1 --task-type competitive-analysis`
   - For balanced/deep_research modes, this uses Gemini Deep Research (60 min comprehensive analysis)
   - For perplexity mode, uses Perplexity Sonar
   - Output: `01_market_research/competitive_analysis.md`

   - **If `--parallel`**: Launch both skills simultaneously using parallel tool calls

2. **Market Research Reports** *(sequential - needs prior context)*
   - Use `market-research-reports` for comprehensive market analysis
   - Pass research mode context: `--research-mode "$RESEARCH_MODE" --phase 1 --task-type market-research-reports`
   - For balanced/deep_research modes, this uses Gemini Deep Research for comprehensive market landscape
   - This task uses findings from parallel group above
   - Output: `01_market_research/market_overview.md`

3. **Generate Diagrams** *(sequential)*
   - Use `project-diagrams` for market positioning charts
   - Use `project-diagrams` for competitive landscape visualization
   - Output: `01_market_research/diagrams/`

**Parallel Execution (if `--parallel`):**
```bash
# Get execution plan
python "${CLAUDE_PLUGIN_ROOT}/scripts/parallel-orchestrator.py" plan \
  "planning_outputs/<project_name>" 1

# After parallel tasks complete, merge context
python "${CLAUDE_PLUGIN_ROOT}/scripts/parallel-orchestrator.py" merge-context \
  "planning_outputs/<project_name>" 1
```

**Log:** `[HH:MM:SS] PHASE 1 COMPLETE: Market research and competitive analysis`

**Checkpoint:** Save progress after Phase 1:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py" save \
  "planning_outputs/<project_name>" 1 \
  --context "Market research complete. Key findings: <summary>" \
  --decisions "Target market: <segment>;Key competitors: <list>;Market opportunity: <insight>"
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" complete "planning_outputs/<project_name>" 1
```

**Interactive Approval Gate (if enabled):**

```bash
# Generate phase summary
SUMMARY=$(python "${CLAUDE_PLUGIN_ROOT}/scripts/generate-phase-summary.py" \
  "planning_outputs/<project_name>" 1 "Market Research" --duration 23)

# Display summary
echo "$SUMMARY"

# Generate approval question
QUESTION=$(python "${CLAUDE_PLUGIN_ROOT}/scripts/generate-phase-summary.py" \
  "planning_outputs/<project_name>" 1 "Market Research" --format question)

# Ask user via AskUserQuestion
# Options: "Continue" | "Revise" | "Pause"
```

**Handle User Response:**

- **Continue**: Proceed to Phase 2
- **Revise**: Collect feedback, re-run Phase 1 with adjustments
- **Pause**: Save state, exit (resume later with `/resume-plan`)

**Revision Workflow (if "Revise" selected):**

```bash
# Collect revision feedback
FEEDBACK=$(AskUserQuestion: "What would you like to change about Phase 1?")

# Re-run Phase 1 with feedback
/refine-plan "planning_outputs/<project_name>" --phase 1 --feedback "$FEEDBACK"

# After revision, show summary again and ask approval
```

### Phase 2: Architecture & Technical Design
**Skills to use:** `architecture-research`, `building-blocks`, `research-lookup`

1. **Architecture Research**
   - Use `architecture-research` skill for system design
   - Research best practices for the technology stack
   - Output: `02_architecture/architecture_document.md`

2. **Building Blocks**
   - Use `building-blocks` skill to decompose into components
   - Define clear interfaces and dependencies
   - Output: `02_architecture/building_blocks.md`

3. **Generate Diagrams**
   - Use `project-diagrams` for system architecture diagram
   - Use `project-diagrams` for component interaction diagrams
   - Use `project-diagrams` for data flow diagrams
   - Output: `02_architecture/diagrams/`

**Log:** `[HH:MM:SS] PHASE 2 COMPLETE: Architecture and building blocks defined`

**Checkpoint:** Save progress after Phase 2:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py" save \
  "planning_outputs/<project_name>" 2 \
  --context "Architecture defined. Stack: <tech_stack>. Components: <count>" \
  --decisions "Stack: <tech>;Pattern: <pattern>;Database: <db>;Cloud: <provider>"
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" complete "planning_outputs/<project_name>" 2
```

### Phase 3: Feasibility & Risk Analysis
**Skills to use:** `feasibility-analysis`, `risk-assessment`, `service-cost-analysis`

**With `--parallel` flag (HIGHEST parallelization - 60% time savings):**
```
Group 3.1 (PARALLEL): feasibility-analysis + risk-assessment + service-cost-analysis
Group 3.2 (sequential): project-diagrams
```

1. **Feasibility + Risk + Cost Analysis** *(ALL can run in parallel)*

   These three analyses are independent and can run simultaneously:

   - **Feasibility Analysis**: Use `feasibility-analysis` skill to assess viability
     - Output: `03_feasibility/feasibility_analysis.md`

   - **Risk Assessment**: Use `risk-assessment` skill to identify and mitigate risks
     - Output: `03_feasibility/risk_assessment.md`

   - **Service Cost Analysis**: Use `service-cost-analysis` skill for infrastructure costs
     - Output: `03_feasibility/service_cost_analysis.md`

   **If `--parallel`**: Launch ALL THREE skills simultaneously using parallel tool calls

2. **Generate Diagrams** *(sequential - needs analysis results)*
   - Use `project-diagrams` for cost breakdown visualization
   - Use `project-diagrams` for risk matrix diagram
   - Output: `03_feasibility/diagrams/`

**Parallel Execution (if `--parallel`):**
```bash
# Prepare input context from Phase 2
python "${CLAUDE_PLUGIN_ROOT}/scripts/parallel-orchestrator.py" input-context \
  "planning_outputs/<project_name>" 3

# Get execution plan
python "${CLAUDE_PLUGIN_ROOT}/scripts/parallel-orchestrator.py" plan \
  "planning_outputs/<project_name>" 3

# After parallel tasks complete, merge context
python "${CLAUDE_PLUGIN_ROOT}/scripts/parallel-orchestrator.py" merge-context \
  "planning_outputs/<project_name>" 3
```

**Log:** `[HH:MM:SS] PHASE 3 COMPLETE: Feasibility and costs analyzed`

**Checkpoint:** Save progress after Phase 3:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py" save \
  "planning_outputs/<project_name>" 3 \
  --context "Feasibility confirmed. Monthly cost: $<cost>. Risks: <count>" \
  --decisions "Budget: $<amount>;Top risk: <risk>;Feasibility: <score>"
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" complete "planning_outputs/<project_name>" 3
```

### Phase 4: Implementation Planning
**Skills to use:** `sprint-planning`, `building-blocks`

1. **Sprint Planning**
   - Use `sprint-planning` skill to create development roadmap
   - Break building blocks into sprint-sized tasks
   - Define milestones and dependencies
   - Output: `04_implementation/sprint_plan.md`

2. **Milestone Definition**
   - Define MVP, beta, and launch milestones
   - Create timeline visualization
   - Output: `04_implementation/milestones.md`

3. **Generate Diagrams**
   - Use `project-diagrams` for Gantt chart / timeline
   - Use `project-diagrams` for dependency graph
   - Output: `04_implementation/diagrams/`

**Log:** `[HH:MM:SS] PHASE 4 COMPLETE: Sprint plan and milestones defined`

**Checkpoint:** Save progress after Phase 4:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py" save \
  "planning_outputs/<project_name>" 4 \
  --context "Sprint plan complete. Sprints: <count>. MVP in Sprint <num>" \
  --decisions "MVP scope: <features>;Timeline: <weeks> weeks;Team size: <size>"
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" complete "planning_outputs/<project_name>" 4
```

### Phase 5: Go-to-Market Strategy
**Skills to use:** `marketing-campaign`, `research-lookup`

1. **Marketing Campaign**
   - Use `marketing-campaign` skill for launch strategy
   - Define target channels and messaging
   - Output: `05_go_to_market/marketing_campaign.md`

2. **Content Calendar**
   - Create 30/60/90 day content plan
   - Define platform-specific strategies
   - Output: `05_go_to_market/content_calendar.md`

3. **Generate Diagrams**
   - Use `project-diagrams` for campaign timeline
   - Use `project-diagrams` for funnel visualization
   - Output: `05_go_to_market/diagrams/`

**Log:** `[HH:MM:SS] PHASE 5 COMPLETE: Go-to-market strategy defined`

**Checkpoint:** Save progress after Phase 5:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py" save \
  "planning_outputs/<project_name>" 5 \
  --context "GTM strategy complete. Channels: <list>. Launch timeline: <days> days" \
  --decisions "Primary channel: <channel>;Launch budget: $<amount>;KPIs: <metrics>"
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" complete "planning_outputs/<project_name>" 5
```

### Phase 6: Review & Executive Summary
**Skills to use:** `plan-review`

1. **Plan Review**
   - Use `plan-review` skill to evaluate the complete plan
   - Identify gaps, inconsistencies, or improvements
   - Output: `06_review/plan_review.md`

2. **Executive Summary**
   - Synthesize all phases into a 2-3 page executive summary
   - Include key decisions, costs, timeline, and risks
   - Output: `00_executive_summary.md`

**Log:** `[HH:MM:SS] PHASE 6 COMPLETE: Plan reviewed and summarized`

**Final Checkpoint:** Mark plan as complete:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py" save \
  "planning_outputs/<project_name>" 6 \
  --context "Plan complete. All phases executed successfully." \
  --decisions "Review status: <pass/fail>;Critical gaps: <count>;Recommended next steps: <action>"
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" complete "planning_outputs/<project_name>" 6
```

## Post-Plan Analysis: Parallelization Recommendations

**IMPORTANT:** After Phase 6 completes, if the plan was executed WITHOUT the `--parallel` flag, analyze parallelization opportunities and present recommendations to the user.

### Step 1: Run Parallelization Analysis

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/analyze-parallelization.py" \
  "planning_outputs/<timestamp>_<project_name>"
```

This analyzes the completed plan and calculates:
- Sequential execution time (actual)
- Parallel execution time (estimated)
- Time savings percentage
- Recommendation level (full, conservative, none)

**Example Output:**
```
Parallelization Analysis
Plan: 20260112_143022_my-saas-app

Time Comparison:
  Sequential execution: 120 minutes
  Parallel execution:   103 minutes
  Time savings:         17 minutes (14.2%)

Recommendation: CONSERVATIVE
  Moderate time savings (14%) with 2 parallel task groups. Worth considering.
```

### Step 2: Present Recommendation to User

Based on the analysis result, use AskUserQuestion to present parallelization options:

#### Scenario A: Significant Savings (≥20%)

```python
AskUserQuestion({
    "questions": [
        {
            "question": "Your plan could save ~22% time with parallelization. Enable it for future similar projects?",
            "header": "Optimize Planning",
            "multiSelect": False,
            "options": [
                {
                    "label": "Yes - Full parallelization (Recommended)",
                    "description": "Run 3 task groups in parallel. Estimated time: 98 min vs 125 min sequential. Savings: 27 minutes"
                },
                {
                    "label": "Conservative - Only 100% safe parallel tasks",
                    "description": "Run 2 task groups in parallel. Estimated time: 110 min. Savings: 15 minutes"
                },
                {
                    "label": "No - Keep sequential execution",
                    "description": "No changes to planning workflow"
                }
            ]
        }
    ]
})
```

#### Scenario B: Moderate Savings (10-19%)

```python
AskUserQuestion({
    "questions": [
        {
            "question": "Your plan could save ~14% time with parallelization. Consider enabling for future projects?",
            "header": "Optimize Planning",
            "multiSelect": False,
            "options": [
                {
                    "label": "Conservative - Only critical parallel tasks (Recommended)",
                    "description": "Run Phase 3 analysis tasks in parallel only. Savings: 12 minutes (10%)"
                },
                {
                    "label": "Yes - Full parallelization",
                    "description": "Run 2 task groups in parallel. Savings: 17 minutes (14%)"
                },
                {
                    "label": "No - Sequential is fine",
                    "description": "Minimal savings, keep current workflow"
                }
            ]
        }
    ]
})
```

#### Scenario C: Minimal Savings (<10%)

```python
AskUserQuestion({
    "questions": [
        {
            "question": "Your plan would save only ~7% time with parallelization. Sequential execution is fine.",
            "header": "Parallelization Analysis",
            "multiSelect": False,
            "options": [
                {
                    "label": "No - Sequential execution (Recommended)",
                    "description": "Minimal savings (5 minutes), not worth complexity"
                },
                {
                    "label": "Yes - Try parallelization anyway",
                    "description": "Enable for learning/testing purposes"
                }
            ]
        }
    ]
})
```

### Step 3: Handle User Selection

Based on the user's choice:

**If "Yes - Full parallelization" or "Conservative":**
1. Save preference to `.claude/project-planner.local.md`:
   ```bash
   echo "prefer_parallelization: true" >> .claude/project-planner.local.md
   ```
2. Show example command for next time:
   ```
   ✓ Preference saved! For your next similar project, the system will use:
     /full-plan my-next-project --parallel
   ```

**If "No - Keep sequential":**
1. No action needed
2. Inform user they can always enable with `--parallel` flag

### When to Skip Analysis

**Skip post-plan analysis if:**
- Plan was already executed with `--parallel` flag
- Plan is very simple (<10 phases/tasks)
- User explicitly passed `--no-analysis` flag

### See Also

For detailed information about parallelization analysis:
- **Guide:** `docs/PARALLELIZATION_GUIDE.md`
- **Script:** `scripts/analyze-parallelization.py`
- **Examples:** Real-world savings scenarios for different project types

## Progress Tracking

**IMPORTANT:** Use the progress tracker to maintain real-time progress visibility.

### Initialize Progress (at start)

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" init \
  "planning_outputs/<project_name>" "full" --name "<Project Name>"
```

### Update Progress (during execution)

Before each phase:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" start \
  "planning_outputs/<project_name>" <phase_num> --activity "Starting <phase_name>..."
```

During a phase (for major activities):
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" activity \
  "planning_outputs/<project_name>" "Generating architecture diagrams..."
```

After each phase:
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" complete \
  "planning_outputs/<project_name>" <phase_num>
```

### Progress Dashboard

The tracker automatically generates `progress.md` with:

```
[████████████░░░░░░░░] 60%

| Phase | Status | Duration | Skills |
|-------|--------|----------|--------|
| ✅ 1. Market Research | Completed | 25 min | research-lookup, competitive... |
| ✅ 2. Architecture Design | Completed | 38 min | architecture-research... |
| ✅ 3. Feasibility & Costs | Completed | 22 min | feasibility-analysis... |
| 🔄 4. Implementation Planning | In Progress | 12 min (running) | sprint-planning... |
| ⏳ 5. Go-to-Market | Pending | - | marketing-campaign... |
| ⏳ 6. Review & Synthesis | Pending | - | plan-review |

> Current Activity: Creating sprint plan with user stories...
```

### TodoWrite Integration

Also use TodoWrite to track phases for the user's visibility:

```
todos:
  - content: "Complete Phase 1: Market Research & Competitive Analysis"
    activeForm: "Completing Phase 1: Market Research"
    status: "completed"
  - content: "Complete Phase 2: Architecture & Building Blocks"
    activeForm: "Completing Phase 2: Architecture Design"
    status: "in_progress"
  - content: "Complete Phase 3: Feasibility, Costs & Risk Assessment"
    activeForm: "Completing Phase 3: Feasibility Analysis"
    status: "pending"
  - content: "Complete Phase 4: Implementation Planning & Sprints"
    activeForm: "Completing Phase 4: Sprint Planning"
    status: "pending"
  - content: "Complete Phase 5: Go-to-Market Strategy"
    activeForm: "Completing Phase 5: Go-to-Market"
    status: "pending"
  - content: "Complete Phase 6: Review & Executive Summary"
    activeForm: "Completing Phase 6: Plan Review"
    status: "pending"
```

## Completion Checklist

Before marking complete, verify:
- [ ] All 6 phases executed
- [ ] All output files created
- [ ] Diagrams generated for each section
- [ ] Executive summary synthesizes all findings
- [ ] Plan review identifies no critical gaps
- [ ] Progress.md shows all phases complete

## Example Usage

User: `/full-plan`