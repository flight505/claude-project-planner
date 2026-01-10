---
description: Generate a comprehensive project plan using all planning skills - architecture, research, building blocks, costs, risks, sprints, and go-to-market strategy
---

# Full Project Plan Command

When the user invokes `/full-plan`, generate a **comprehensive project plan** by systematically using all relevant planning skills.

## Required Input

Before starting, gather from the user:
1. **Project name and description** - What are we building?
2. **Target audience** - Who is this for?
3. **Key goals** - What problem does it solve?
4. **Timeline constraints** - Any deadlines?
5. **Budget constraints** - Any budget limits?

If any critical information is missing, ask before proceeding.

## Optional Flags

| Flag | Description |
|------|-------------|
| `--validate` | Run multi-model architecture validation after Phase 2 |
| `--skip-marketing` | Skip Phase 5 (Go-to-Market) - equivalent to `/tech-plan` |

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
  --architecture-file "planning_outputs/<project>/02_architecture/architecture_document.md" \
  --building-blocks "planning_outputs/<project>/02_architecture/building_blocks.md" \
  --output "planning_outputs/<project>/02_architecture/validation_report.md"
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

1. **Market Research**
   - Use `research-lookup` to gather industry data, trends, and benchmarks
   - Use `market-research-reports` for comprehensive market analysis
   - Output: `01_market_research/market_overview.md`

2. **Competitive Analysis**
   - Use `competitive-analysis` skill to analyze competitors
   - Identify market gaps and opportunities
   - Output: `01_market_research/competitive_analysis.md`

3. **Generate Diagrams**
   - Use `project-diagrams` for market positioning charts
   - Use `project-diagrams` for competitive landscape visualization
   - Output: `01_market_research/diagrams/`

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

1. **Feasibility Analysis**
   - Use `feasibility-analysis` skill to assess viability
   - Evaluate technical, financial, and operational feasibility
   - Output: `03_feasibility/feasibility_analysis.md`

2. **Risk Assessment**
   - Use `risk-assessment` skill to identify and mitigate risks
   - Create risk matrix and mitigation strategies
   - Output: `03_feasibility/risk_assessment.md`

3. **Service Cost Analysis**
   - Use `service-cost-analysis` skill for infrastructure costs
   - Calculate TCO for cloud services, APIs, tools
   - Output: `03_feasibility/service_cost_analysis.md`

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
  - content: "Phase 1: Market Research & Competitive Analysis"
    status: "completed"
  - content: "Phase 2: Architecture & Building Blocks"
    status: "in_progress"
  - content: "Phase 3: Feasibility, Costs & Risk Assessment"
    status: "pending"
  - content: "Phase 4: Implementation Planning & Sprints"
    status: "pending"
  - content: "Phase 5: Go-to-Market Strategy"
    status: "pending"
  - content: "Phase 6: Review & Executive Summary"
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