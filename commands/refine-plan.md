---
description: Refine a specific phase of an existing plan with user feedback, handling dependent phases intelligently
---

# Refine Plan Command

When the user invokes `/refine-plan`, revise a completed phase based on user feedback, with intelligent handling of dependent phases.

## Usage

```
/refine-plan <plan-directory> --phase <phase-num> --feedback "<feedback>"
```

**Arguments:**
- `plan-directory`: Path to existing plan (e.g., `planning_outputs/20260112_143022_my-project`)
- `--phase`: Phase number to revise (1-6)
- `--feedback`: User feedback describing what to change

**Example:**
```
/refine-plan planning_outputs/20260112_143022_my-saas --phase 2 \
  --feedback "Use monolithic architecture instead of microservices. Keep it simple for MVP."
```

## Phase Dependencies

Understanding dependencies is critical for handling revisions:

```
Phase 1 (Market Research)
   ↓
Phase 2 (Architecture) ← depends on Phase 1
   ↓
Phase 3 (Feasibility) ← depends on Phase 2
   ↓
Phase 4 (Implementation) ← depends on Phase 3
   ↓
Phase 5 (Marketing) ← depends on Phase 4
   ↓
Phase 6 (Review) ← depends on all phases
```

**Dependency Matrix:**

| Phase Revised | Affected Phases | Rationale |
|---------------|-----------------|-----------|
| Phase 1 | 2, 3, 4, 5, 6 | Market research influences everything downstream |
| Phase 2 | 3, 4, 6 | Architecture changes affect feasibility, implementation, review |
| Phase 3 | 4, 6 | Feasibility/cost changes affect implementation plan |
| Phase 4 | 5, 6 | Implementation plan affects marketing strategy |
| Phase 5 | 6 | Marketing changes only affect final review |
| Phase 6 | None | Review is terminal phase |

## Execution Workflow

### Step 1: Load Existing Plan

```bash
# Validate plan directory exists
if [[ ! -d "$PLAN_DIR" ]]; then
  echo "❌ Error: Plan directory not found: $PLAN_DIR"
  exit 1
fi

# Load checkpoint to get plan state
CHECKPOINT=$(python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" load "$PLAN_DIR")
```

### Step 2: Validate Phase Number

```bash
PHASE_NUM=$1

if [[ $PHASE_NUM -lt 1 ]] || [[ $PHASE_NUM -gt 6 ]]; then
  echo "❌ Error: Phase number must be 1-6"
  exit 1
fi

# Check if phase was completed
LAST_COMPLETED=$(echo "$CHECKPOINT" | jq -r '.last_completed_phase')

if [[ $PHASE_NUM -gt $LAST_COMPLETED ]]; then
  echo "❌ Error: Phase $PHASE_NUM has not been completed yet"
  echo "Last completed phase: $LAST_COMPLETED"
  exit 1
fi
```

### Step 3: Store Revision Feedback

```bash
# Create revision context file
REVISION_DIR="$PLAN_DIR/.state/revisions"
mkdir -p "$REVISION_DIR"

REVISION_FILE="$REVISION_DIR/phase${PHASE_NUM}_revision_$(date +%Y%m%d_%H%M%S).md"

cat > "$REVISION_FILE" <<EOF
---
phase: $PHASE_NUM
revision_number: $(ls $REVISION_DIR/phase${PHASE_NUM}_* 2>/dev/null | wc -l)
timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
---

# Revision Feedback for Phase $PHASE_NUM

$FEEDBACK

## Instructions for Re-execution

- Review existing phase outputs carefully
- Preserve valid insights and research
- Adjust direction based on feedback above
- Maintain consistency with non-revised phases where possible
EOF

echo "✓ Revision feedback stored: $REVISION_FILE"
```

### Step 4: Identify Affected Phases

```bash
# Get list of dependent phases
python "${CLAUDE_PLUGIN_ROOT}/scripts/analyze-dependencies.py" \
  --phase "$PHASE_NUM" \
  --plan-dir "$PLAN_DIR"
```

This outputs:
```json
{
  "revised_phase": 2,
  "dependent_phases": [3, 4, 6],
  "cascade_recommendation": "ask",
  "estimated_time": "45 minutes"
}
```

### Step 5: Ask User About Dependent Phases

Use `AskUserQuestion` to determine cascade strategy:

```python
{
  "question": f"Phase {phase_num} revision will affect Phases {dependent_phases}. How should we handle dependencies?",
  "header": "Dependencies",
  "multiSelect": False,
  "options": [
    {
      "label": "Auto-rerun dependent phases (Recommended)",
      "description": f"Automatically rerun Phases {dependent_phases} to maintain consistency. Estimated time: {estimated_time}"
    },
    {
      "label": "Review each dependent phase individually",
      "description": "I'll ask before rerunning each phase. More control, takes longer"
    },
    {
      "label": "Only revise Phase {phase_num}",
      "description": "Skip dependent phases for now. WARNING: May cause inconsistencies. You'll need to manually review"
    }
  ]
}
```

### Step 6: Re-execute Phase with Feedback

```bash
# Backup original phase outputs
BACKUP_DIR="$PLAN_DIR/.state/backups/phase${PHASE_NUM}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r "$PLAN_DIR/0${PHASE_NUM}_"* "$BACKUP_DIR/" 2>/dev/null || true

echo "✓ Original outputs backed up to: $BACKUP_DIR"

# Prepare phase context with revision feedback
PHASE_CONTEXT="$PLAN_DIR/.state/phase${PHASE_NUM}_context_revised.md"

cat > "$PHASE_CONTEXT" <<EOF
# Phase $PHASE_NUM Context (Revised)

## Previous Phase Outputs
$(cat $PLAN_DIR/.state/phase$((PHASE_NUM-1))_output.md 2>/dev/null || echo "None")

## Revision Feedback
$(cat $REVISION_FILE)

## Original Phase Outputs (for reference)
$(ls -lh $BACKUP_DIR/)

Incorporate the revision feedback while preserving valid research and insights.
EOF

# Re-run the phase with revision context
case $PHASE_NUM in
  1)
    # Re-run Phase 1: Market Research
    echo "♻️  Re-running Phase 1: Market Research with feedback..."
    # Invoke research-lookup, competitive-analysis, market-research-reports skills
    # Pass revision context to each skill
    ;;
  2)
    # Re-run Phase 2: Architecture
    echo "♻️  Re-running Phase 2: Architecture with feedback..."
    # Invoke architecture-research, building-blocks skills
    ;;
  3)
    # Re-run Phase 3: Feasibility
    echo "♻️  Re-running Phase 3: Feasibility with feedback..."
    # Invoke feasibility-analysis, risk-assessment, service-cost-analysis skills
    ;;
  4)
    # Re-run Phase 4: Implementation
    echo "♻️  Re-running Phase 4: Implementation with feedback..."
    # Invoke sprint-planning skill
    ;;
  5)
    # Re-run Phase 5: Marketing
    echo "♻️  Re-running Phase 5: Marketing with feedback..."
    # Invoke marketing-campaign skill
    ;;
  6)
    # Re-run Phase 6: Review
    echo "♻️  Re-running Phase 6: Review with feedback..."
    # Invoke plan-review skill
    ;;
esac
```

### Step 7: Handle Dependent Phases

Based on user's cascade choice:

**Auto-rerun:**
```bash
for dep_phase in "${DEPENDENT_PHASES[@]}"; do
  echo "♻️  Auto-rerunning Phase $dep_phase (depends on revised Phase $PHASE_NUM)"

  # Re-run dependent phase with updated context
  # (Same process as Step 6, but for dependent phase)

  # Update checkpoint
  python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" save \
    "$PLAN_DIR" "$dep_phase" \
    --context "Re-executed after Phase $PHASE_NUM revision" \
    --revision "$((REVISION_NUM + 1))"
done
```

**Review individually:**
```bash
for dep_phase in "${DEPENDENT_PHASES[@]}"; do
  # Show summary of current phase
  python "${CLAUDE_PLUGIN_ROOT}/scripts/generate-phase-summary.py" \
    "$PLAN_DIR" "$dep_phase" "Phase $dep_phase"

  # Ask user
  AskUserQuestion: "Phase $dep_phase depends on revised Phase $PHASE_NUM. Rerun?"

  if [[ "$USER_RESPONSE" == "Yes" ]]; then
    # Rerun phase
  else
    # Mark as potentially inconsistent
    echo "⚠️  Phase $dep_phase kept as-is. May be inconsistent with revised Phase $PHASE_NUM"
    touch "$PLAN_DIR/.state/phase${dep_phase}_stale"
  fi
done
```

**Only revise target phase:**
```bash
# Mark dependent phases as potentially stale
for dep_phase in "${DEPENDENT_PHASES[@]}"; do
  touch "$PLAN_DIR/.state/phase${dep_phase}_stale"
  echo "⚠️  Phase $dep_phase marked as potentially inconsistent"
done

echo ""
echo "⚠️  WARNING: Dependent phases not updated"
echo "Review manually for inconsistencies:"
for dep_phase in "${DEPENDENT_PHASES[@]}"; do
  echo "  - Phase $dep_phase: $PLAN_DIR/0${dep_phase}_*/"
done
```

### Step 8: Update Checkpoint

```bash
# Update checkpoint with revision information
python "${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint_manager.py" save \
  "$PLAN_DIR" "$PHASE_NUM" \
  --context "Phase $PHASE_NUM revised based on user feedback" \
  --revision "$((REVISION_NUM + 1))" \
  --feedback "$FEEDBACK"
```

### Step 9: Generate Revision Summary

```bash
echo ""
echo "=" * 70
echo "✓ Phase $PHASE_NUM Revision Complete"
echo "=" * 70
echo ""
echo "Revised Phase: Phase $PHASE_NUM"
echo "Revision Number: $((REVISION_NUM + 1))"
echo "Original outputs backed up to: $BACKUP_DIR"
echo ""

if [[ ${#RERUN_PHASES[@]} -gt 0 ]]; then
  echo "Dependent phases re-executed:"
  for phase in "${RERUN_PHASES[@]}"; do
    echo "  ✓ Phase $phase"
  done
fi

if [[ ${#STALE_PHASES[@]} -gt 0 ]]; then
  echo ""
  echo "⚠️  Phases marked as potentially inconsistent:"
  for phase in "${STALE_PHASES[@]}"; do
    echo "  ⚠️  Phase $phase (review manually)"
  done
fi

echo ""
echo "Next steps:"
echo "  1. Review revised outputs: $PLAN_DIR/0${PHASE_NUM}_*/"
echo "  2. If satisfied, continue or finalize plan"
echo "  3. If further changes needed, run /refine-plan again"
echo ""
```

## Dependency Resolution Script

Create `scripts/analyze-dependencies.py`:

```python
#!/usr/bin/env python3
"""Analyze phase dependencies for revision planning."""

# Phase dependency graph
PHASE_DEPENDENCIES = {
    1: [],  # Market research - no dependencies
    2: [1],  # Architecture depends on market research
    3: [2],  # Feasibility depends on architecture
    4: [3],  # Implementation depends on feasibility
    5: [4],  # Marketing depends on implementation plan
    6: [1, 2, 3, 4, 5],  # Review depends on everything
}

# Reverse mapping: which phases depend on each phase?
DEPENDENT_PHASES = {
    1: [2, 3, 4, 5, 6],
    2: [3, 4, 6],
    3: [4, 6],
    4: [5, 6],
    5: [6],
    6: [],
}

# Estimated time to re-run each phase (minutes)
PHASE_TIMES = {
    1: 23,  # Market research
    2: 35,  # Architecture
    3: 37,  # Feasibility
    4: 25,  # Implementation
    5: 20,  # Marketing
    6: 10,  # Review
}

def analyze_revision_impact(phase_num: int) -> dict:
    dependent = DEPENDENT_PHASES[phase_num]
    total_time = PHASE_TIMES[phase_num] + sum(PHASE_TIMES[p] for p in dependent)

    return {
        "revised_phase": phase_num,
        "dependent_phases": dependent,
        "estimated_time_minutes": total_time,
        "cascade_recommendation": "ask" if len(dependent) > 2 else "auto"
    }
```

## Best Practices

1. **Always backup before revision** - Original outputs preserved in `.state/backups/`
2. **Understand cascading effects** - Architecture changes ripple through all later phases
3. **Start with targeted feedback** - Be specific about what to change
4. **Review dependent phases** - Even auto-rerun may need tweaking
5. **Track revision history** - Checkpoint system maintains full history

## Example Workflows

### Scenario 1: Architecture Change

```bash
# User realizes monolith is better than microservices after seeing architecture
/refine-plan planning_outputs/20260112_143022_my-project --phase 2 \
  --feedback "Switch to monolithic architecture. Microservices add unnecessary complexity for MVP."

# System: "This will affect Phases 3 (feasibility), 4 (implementation), 6 (review)"
# User selects: "Auto-rerun dependent phases"
# Result: Phases 2, 3, 4, 6 all regenerated with monolithic approach
```

### Scenario 2: Target Market Adjustment

```bash
# User wants to focus on enterprise instead of SMB
/refine-plan planning_outputs/20260112_143022_my-project --phase 1 \
  --feedback "Target enterprise customers (500+ employees) instead of small businesses. Adjust competitive analysis and pricing accordingly."

# System: "This will affect ALL downstream phases (2-6)"
# User selects: "Review each phase individually"
# Result: User approves Phase 2 rerun, skips Phase 3, reruns Phase 4-6
```

### Scenario 3: Cost Optimization

```bash
# User finds costs too high in Phase 3
/refine-plan planning_outputs/20260112_143022_my-project --phase 3 \
  --feedback "Infrastructure costs are too high ($15K/month). Explore serverless options and managed services to reduce to <$5K/month."

# System: "This will affect Phases 4 (implementation), 6 (review)"
# User selects: "Auto-rerun dependent phases"
# Result: Phases 3, 4, 6 regenerated with cost-optimized infrastructure
```

## Completion

After refinement completes:

```bash
echo "✓ Plan refinement complete!"
echo ""
echo "Updated plan: $PLAN_DIR"
echo "Revision history: $PLAN_DIR/.state/revisions/"
echo ""
echo "Generate final report: /generate-report $(basename $PLAN_DIR)"
```

## Important Notes

- **Checkpoint system integration**: All revisions tracked in checkpoint history
- **Backup preservation**: Original outputs never deleted, always in `.state/backups/`
- **Revision visibility**: Clear revision numbers and timestamps in checkpoint
- **Dependency awareness**: System understands phase relationships
- **Flexibility**: User controls cascade behavior (auto/ask/none)

This command enables iterative refinement while maintaining plan consistency and providing full revision history.
