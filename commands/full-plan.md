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

### Step 2: Background Dependency Installation

While the user fills out the template, the **SessionStart hook** automatically starts installing dependencies in the background:

```bash
# Runs automatically via hooks/SessionStart.sh
nohup "${CLAUDE_PLUGIN_ROOT}/scripts/ensure-dependencies.sh" full &
```

This ensures all required packages are ready before planning begins.

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

### Step 4: Interactive Configuration

Use AskUserQuestion to gather additional preferences:

```python
questions = [
    {
        "question": "Which AI provider do you want to use for research?",
        "header": "AI Provider",
        "multiSelect": False,
        "options": [
            {
                "label": "Google Gemini Deep Research (Recommended)",
                "description": "Comprehensive multi-step research (up to 60 min). Requires GEMINI_API_KEY and Google AI Pro subscription ($19.99/month)"
            },
            {
                "label": "Perplexity via OpenRouter",
                "description": "Fast web-grounded research. Requires OPENROUTER_API_KEY (pay-per-use)"
            },
            {
                "label": "Auto-detect",
                "description": "Automatically choose based on available API keys"
            }
        ]
    },
    {
        "question": "Enable smart parallelization for faster execution?",
        "header": "Performance",
        "multiSelect": False,
        "options": [
            {
                "label": "Yes - Full parallelization (Recommended)",
                "description": "Run independent tasks in parallel. ~14% time savings overall, up to 60% in Phase 3"
            },
            {
                "label": "No - Sequential execution",
                "description": "Run all tasks in order. More predictable but slower"
            }
        ]
    },
    {
        "question": "Enable multi-model architecture validation after design phase?",
        "header": "Validation",
        "multiSelect": False,
        "options": [
            {
                "label": "Yes - Multi-model validation (Recommended)",
                "description": "Validate architecture with multiple AI models (Gemini, GPT-4o, Claude) for consensus"
            },
            {
                "label": "No - Skip validation",
                "description": "Proceed directly to implementation planning"
            }
        ]
    }
]
```

Store user selections for use in planning execution.

### Step 5: Wait for Dependencies

Before starting Phase 1, ensure all dependencies are installed:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-dependencies.py"
```

This blocks until background installation completes, showing a progress bar.

**If installation fails:**
1. Check log: `cat /tmp/claude-planner-deps.log`
2. Manually install: `pip install -r requirements-full-plan.txt`
3. Re-run `/full-plan`

### Step 6: Begin Planning Execution

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

**With `--parallel` flag:**
```
Group 1.1 (PARALLEL): research-lookup + competitive-analysis
Group 1.2 (sequential): market-research-reports (uses Group 1.1 context)
Group 1.3 (sequential): project-diagrams
```

1. **Market Research + Competitive Analysis** *(can run in parallel)*
   - Use `research-lookup` to gather industry data, trends, and benchmarks
   - Use `competitive-analysis` skill to analyze competitors
   - **If `--parallel`**: Launch both skills simultaneously using parallel tool calls
   - Output: `01_market_research/market_data.md`, `01_market_research/competitive_analysis.md`

2. **Market Research Reports** *(sequential - needs prior context)*
   - Use `market-research-reports` for comprehensive market analysis
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