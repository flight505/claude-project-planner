# Deep Research Budget System - Implementation Summary

## Overview

Implemented a 3-layer budget enforcement system to ensure Claude respects the **2 Deep Research query limit** per `/full-plan` session.

## Implementation Layers

### Layer 1: Documentation (Skill & Command Instructions)

**File: `project_planner/.claude/skills/research-lookup/SKILL.md`**

Added prominent "⚠️ Deep Research Budget Constraints" section with:
- Clear statement of 2-query limit
- Budget allocation strategies (conservative vs aggressive)
- Explicit DO NOT use list (version checks, pricing, simple queries)
- Recommended allocations for different scenarios
- Pre-query checklist: "Is this worth 30-60 min and 50% of my budget?"

**File: `commands/full-plan.md`**

Added "Step 5.5: Deep Research Budget Reminder" with:
- Pre-execution reminder about budget constraints
- Conservative vs Aggressive allocation strategies
- Explicit rules for when Deep Research is justified
- Default recommendations (prefer Perplexity for temporal accuracy)
- Budget initialization in Step 6

### Layer 2: Runtime Tracking System

**File: `scripts/budget-tracker.py`**

Complete CLI tool for budget management:

**Commands:**
```bash
# Initialize budget for new project
budget-tracker.py init <project_dir> --limit 2

# Check remaining budget before query
budget-tracker.py check <project_dir>

# Record Deep Research usage
budget-tracker.py record <project_dir> <query_summary> --duration <secs> --phase <n> --task-type <type>

# Get current status with query history
budget-tracker.py status <project_dir>
```

**Budget File Format:** `DEEP_RESEARCH_BUDGET.json`
```json
{
  "limit": 2,
  "used": 1,
  "remaining": 1,
  "queries": [
    {
      "timestamp": "2026-01-19T12:34:56",
      "query_summary": "Competitive landscape analysis for DPP...",
      "duration_seconds": 3600,
      "duration_minutes": 60.0,
      "model": "models/deep-research-pro-preview-12-2025",
      "phase": 1,
      "task_type": "competitive-analysis"
    }
  ],
  "created_at": "2026-01-19T11:00:00",
  "last_updated": "2026-01-19T12:34:56"
}
```

**Features:**
- ✅ Budget initialization with configurable limit
- ✅ Pre-query budget checking (exit code 0 = available, 1 = exhausted)
- ✅ Usage recording with full metadata
- ✅ Status display with query history
- ✅ Progressive warnings (1/2 used → "Last query available!")
- ✅ Clear fallback guidance when budget exhausted

### Layer 3: Automatic Integration

**File: `project_planner/.claude/skills/research-lookup/gemini_research.py`**

Integrated budget tracking directly into research execution:

**New Functions:**
1. `check_deep_research_budget(project_folder)` - Pre-query budget check
2. `record_deep_research_usage(project_folder, query, duration, ...)` - Post-query recording

**Integration in `execute_deep_research()`:**
```python
# Before execution
if model_type == "deep_research":
    if not check_deep_research_budget(project_folder):
        # Auto-fallback to Gemini Pro
        print("⚠️ Falling back to Gemini Pro due to budget constraints")
        model_type = "pro"
        model = available.get("pro")

# After successful execution
if result["success"] and model_type == "deep_research":
    record_deep_research_usage(project_folder, query, duration, model, phase, task_type)
```

**Behavior:**
- Automatically checks budget before Deep Research execution
- Falls back to Gemini Pro if budget exhausted (graceful degradation)
- Records usage with full context (phase, task type, duration)
- Displays budget warnings during execution
- No blocking for standalone CLI usage (project_folder optional)

## User Experience Flow

### Scenario 1: First Deep Research Query

```
📊 Phase 1: Market Research
Running query: "Comprehensive competitive landscape analysis..."

✅ Deep Research budget: 0/2 used, 2 remaining
⚠️  Using Deep Research Agent (expensive, 30-60 min)
[Research executes for 45 minutes...]
✅ Results saved to: planning_outputs/.../research/competitive_analysis.md

📊 Deep Research budget updated:
   Used: 1/2
   Remaining: 1

⚠️  Only 1 query remaining - use it for the most critical analysis!
```

### Scenario 2: Second Deep Research Query

```
Running query: "Market landscape and adoption trends..."

⚠️  Deep Research budget: 1/2 used - LAST QUERY AVAILABLE
⚠️  Use this query wisely! Consider if Perplexity/Gemini Pro would suffice.
⚠️  Using Deep Research Agent (expensive, 30-60 min)
[Research executes...]

📊 Deep Research budget updated:
   Used: 2/2
   Remaining: 0

⚠️  Budget exhausted! All future research will use Gemini Pro or Perplexity.
```

### Scenario 3: Budget Exhausted - Auto-Fallback

```
Running query: "PostgreSQL vs MongoDB database comparison..."

❌ Deep Research budget exhausted (2/2 used)

Fallback options:
  1. Use Gemini Pro (high quality, 1-5 min)
  2. Use Perplexity Sonar (fast, 30 sec)

⚠️  Falling back to Gemini Pro due to budget constraints
Using Gemini Pro (high quality, 1-5 min)
[Research executes with Pro model instead...]
```

## Testing

### Manual Testing Performed

```bash
# Test 1: Initialize budget
python scripts/budget-tracker.py init /tmp/test-project --limit 2
# ✅ Budget initialized: 2 Deep Research queries available

# Test 2: Check budget (unused)
python scripts/budget-tracker.py check /tmp/test-project
# ✅ Deep Research budget: 0/2 used, 2 remaining

# Test 3: Record first usage
python scripts/budget-tracker.py record /tmp/test-project "Competitive analysis" \
  --duration 3600 --phase 1 --task-type competitive-analysis
# 📊 Used: 1/2, Remaining: 1
# ⚠️  Only 1 query remaining

# Test 4: View status
python scripts/budget-tracker.py status /tmp/test-project
# Shows full query history with Phase 1 - 60.0 min

# Test 5: Exhaust budget
python scripts/budget-tracker.py record /tmp/test-project "Market research" \
  --duration 3000 --phase 1 --task-type market-research
# 📊 Used: 2/2, Remaining: 0
# ⚠️  Budget exhausted!

# Test 6: Check when exhausted
python scripts/budget-tracker.py check /tmp/test-project
# ❌ Deep Research budget exhausted (2/2 used)
# (exit code 1 - fallback required)
```

All tests passed successfully! ✅

## Decision-Making Framework

The system guides Claude through explicit decision-making:

**Before Each Query:**
1. Is this query critical to project viability/direction?
2. Does it require 30-60 min comprehensive multi-source analysis?
3. Can Perplexity (30 sec, better temporal accuracy) suffice?
4. Can Gemini Pro (1-5 min, high quality) suffice?
5. What's my remaining budget?

**Phase-Specific Guidance:**
- **Phase 1**: Maximum 2 Deep Research queries
  - Conservative: 1 for competitive landscape
  - Aggressive: 2 for market + competitive analysis
- **Phase 2**: Use Deep Research ONLY if highly novel/uncertain tech stack
  - DEFAULT to Gemini Pro for standard architecture research
- **Phase 3-6**: Use Perplexity (better temporal accuracy for 2026 data)

## Benefits

1. **Hard Enforcement**: Budget tracker provides exit codes, enabling programmatic checking
2. **Graceful Degradation**: Automatic fallback to Gemini Pro prevents blocking
3. **Full Transparency**: Claude sees budget status before/after each query
4. **Query History**: Full audit trail with phase, task type, duration
5. **Progressive Warnings**: Escalating reminders as budget depletes
6. **User Visibility**: Budget status in progress files and terminal output

## Files Modified/Created

### Created:
- `scripts/budget-tracker.py` - Complete budget management CLI (252 lines)
- `DEEP_RESEARCH_BUDGET_SYSTEM.md` - This documentation

### Modified:
- `project_planner/.claude/skills/research-lookup/SKILL.md` - Added budget constraints section
- `commands/full-plan.md` - Added Step 5.5 budget reminder + initialization
- `project_planner/.claude/skills/research-lookup/gemini_research.py` - Integrated budget checking/recording

## Integration Example

When running `/full-plan`:

```markdown
Step 5.5: Deep Research Budget Reminder
⚠️ CRITICAL: You have 2 Deep Research queries maximum for this session.

Step 6: Execute Planning
# Initialize budget
budget-tracker.py init planning_outputs/20260119_project --limit 2

Phase 1: Market Research
# Before query 1
budget-tracker.py check planning_outputs/20260119_project
# Execute query...
# After query 1
budget-tracker.py record planning_outputs/20260119_project "..." --duration 3600

# Auto-checking continues for subsequent queries...
```

## Future Enhancements

**Potential Additions:**
1. **Cost Tracking**: Add estimated API costs per query
2. **Phase Limits**: Separate budgets per phase (e.g., max 2 in Phase 1, 1 in Phase 2)
3. **Soft Warnings**: Display cost estimates before execution
4. **Budget Config**: User-adjustable limits in configuration
5. **Time Estimates**: Display expected duration before execution

**Not Implemented (by design):**
- Blocking execution (graceful fallback preferred)
- Budget reset mid-session (enforce 2-query hard limit)
- Cross-session budgets (each /full-plan gets fresh budget)

## Summary

The 3-layer approach ensures comprehensive budget enforcement:

1. **Documentation** educates Claude about budget constraints
2. **Runtime tracking** provides programmatic enforcement
3. **Automatic integration** enables graceful degradation

Result: Claude will naturally respect the 2-query Deep Research limit while maintaining high-quality research outputs through intelligent fallback strategies.
