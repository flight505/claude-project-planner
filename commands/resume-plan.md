---
description: Resume an interrupted project plan from the last checkpoint. Lists available checkpoints if no folder specified.
argument-hint: "[planning_folder]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebFetch", "WebSearch", "AskUserQuestion", "TodoWrite"]
---

# Resume Plan Command

When the user invokes `/resume-plan`, resume an interrupted project planning session from the last checkpoint.

## Workflow

1. **Find Checkpoint** - Locate the checkpoint to resume
2. **Load Context** - Restore context from completed phases
3. **Show Status** - Display progress and what remains
4. **Confirm** - Ask user to confirm resumption
5. **Continue** - Execute remaining phases

## Step 1: Find Checkpoint

### If folder path provided:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" status "<folder>" --json
```

### If no folder provided:

List all available checkpoints:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" list planning_outputs/ --json
```

If multiple checkpoints found, present options to user:

```
header: "Resume"
question: "Which project would you like to resume?"
multiSelect: false
options:
  - label: "<project_name_1> (Phase 3/6, 50%)"
    description: "Last updated: 2025-01-10 14:30"
  - label: "<project_name_2> (Phase 2/4, 50%)"
    description: "Last updated: 2025-01-09 18:22"
```

If no checkpoints found:

> "No checkpoints found in planning_outputs/. Run `/full-plan` or `/tech-plan` to start a new project plan."

## Step 2: Load Context

Once a checkpoint is identified, load the resume context:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" context "<folder>"
```

This generates a context summary including:
- Project name and plan type
- Last completed phase
- Key decisions from previous phases
- Context summary
- List of completed outputs

**Read completed outputs** to restore context:
- Read `SUMMARY.md` or `00_executive_summary.md` if exists
- Read key outputs from completed phases
- Understand the project scope and decisions made

## Step 3: Show Status

Present the current status to the user:

```markdown
## Resume Status: <Project Name>

**Plan Type:** Full Plan
**Progress:** 50% (3/6 phases complete)
**Last Activity:** 2025-01-10 14:30

### Completed Phases
✅ Phase 1: Market Research - 25 outputs
✅ Phase 2: Architecture Design - 18 outputs
✅ Phase 3: Feasibility & Costs - 12 outputs

### Remaining Phases
⏳ Phase 4: Implementation Planning
⏳ Phase 5: Go-to-Market Strategy
⏳ Phase 6: Review & Executive Summary

### Key Decisions from Previous Phases
- Technology stack: React, Node.js, PostgreSQL
- Architecture: Microservices with API Gateway
- Target: $50k MVP budget, 6-month timeline
```

## Step 4: Confirm Resumption

Ask user to confirm:

```
header: "Resume"
question: "Resume <project_name> from Phase <next_phase>?"
multiSelect: false
options:
  - label: "Yes, continue from Phase <next_phase>"
    description: "Will execute remaining phases with existing context"
  - label: "Start over (clear checkpoint)"
    description: "Delete checkpoint and begin fresh with /full-plan"
```

### If user chooses "Start over":

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" clear "<folder>"
```

Then inform user:
> "Checkpoint cleared. Run `/full-plan` to start a fresh plan."

## Step 5: Continue Execution

### Restore Progress Tracking

```bash
# Update progress tracker to match checkpoint state
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" status "<folder>"
```

### Set Up TodoWrite

Create todos for remaining phases:

```
todos:
  - content: "Phase 4: Implementation Planning & Sprints"
    status: "in_progress"
    activeForm: "Executing Phase 4"
  - content: "Phase 5: Go-to-Market Strategy"
    status: "pending"
    activeForm: "Executing Phase 5"
  - content: "Phase 6: Review & Executive Summary"
    status: "pending"
    activeForm: "Executing Phase 6"
```

### Execute Remaining Phases

Continue from the next phase, following the same process as `/full-plan` or `/tech-plan`:

**For Full Plan:**

| Next Phase | Actions |
|------------|---------|
| 4 | `sprint-planning`, milestone definition, timeline diagrams |
| 5 | `marketing-campaign`, content calendar, campaign diagrams |
| 6 | `plan-review`, executive summary synthesis |

**For Tech Plan:**

| Next Phase | Actions |
|------------|---------|
| 3 | `sprint-planning`, milestone definition |
| 4 | `plan-review`, executive summary synthesis |

### Update Checkpoint After Each Phase

After completing each remaining phase:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" save \
  "<folder>" <phase_num> \
  --context "Summary of what was done in this phase" \
  --decisions "Decision 1;Decision 2;Decision 3"
```

### Update Progress

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/progress-tracker.py" complete "<folder>" <phase_num>
```

## Context Retention

When resuming, ensure continuity by:

1. **Reading key outputs** from completed phases:
   - `building_blocks.yaml` - Component specs
   - `architecture_document.md` - Technical decisions
   - `service_cost_analysis.md` - Budget constraints
   - `risk_assessment.md` - Known risks

2. **Referencing previous decisions** in new outputs:
   - Sprint plans should reference building blocks by name
   - Go-to-market should align with target audience from market research
   - Review should validate against all prior phases

3. **Maintaining naming consistency**:
   - Use same component names as in building blocks
   - Use same terminology as in architecture document
   - Reference same costs as in cost analysis

## Error Handling

| Situation | Response |
|-----------|----------|
| Checkpoint file corrupted | Offer to clear and start fresh |
| Missing output files | Warn user, offer to regenerate phase |
| Phase partially complete | Ask user which outputs to regenerate |
| Context too large | Summarize key decisions only |

## Example Usage

### List Available Checkpoints

```
User: /resume-plan

Claude: Found 2 projects with checkpoints:

1. **inventory-saas** (Phase 3/6, 50%)
   Last updated: 2025-01-10 14:30

2. **healthcare-app** (Phase 2/4, 50%)
   Last updated: 2025-01-09 18:22

Which project would you like to resume?
```

### Resume Specific Project

```
User: /resume-plan planning_outputs/20250110_inventory_saas

Claude:
## Resume Status: Inventory Management SaaS

Progress: 50% (3/6 phases complete)

### Completed:
✅ Market Research - Competitive analysis, market sizing
✅ Architecture - Microservices design, PostgreSQL, React
✅ Feasibility - $2,900/mo infrastructure, 8 risks identified

### Remaining:
⏳ Phase 4: Sprint Planning
⏳ Phase 5: Go-to-Market
⏳ Phase 6: Review

Resume from Phase 4?

[User confirms]

Claude: Resuming from Phase 4: Implementation Planning...
[Continues execution]
```

## Checkpoint Best Practices

1. **Save checkpoint after EVERY phase** - Don't skip
2. **Include key decisions** - Technology choices, budget constraints, timeline changes
3. **Write context summary** - What was learned, what affects future phases
4. **Reference completed outputs** - When continuing, read prior outputs to maintain consistency
