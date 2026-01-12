# Post-Plan Parallelization Analysis Guide

This guide explains how the post-plan parallelization analysis works and how to use it to optimize future planning sessions.

## Overview

After generating a project plan, the system can analyze the completed work and calculate potential time savings from parallelizing independent tasks. This helps you decide whether to re-run planning with parallelization enabled for similar projects.

## When to Use Post-Plan Analysis

✅ **Use parallelization analysis when:**
- You've completed a `/full-plan` without `--parallel` flag
- You want to understand time savings potential
- You're planning to create similar projects in the future
- You want to optimize your planning workflow

❌ **Skip analysis when:**
- You already used `--parallel` flag
- This was a quick test or prototype
- The plan is very simple (<10 phases/tasks)

## How It Works

```
Plan completes (Phase 6 finished)
        │
        ├─ Analyze plan structure
        │  └─ scripts/analyze-parallelization.py
        │
        ├─ Detect completed tasks
        │  ├─ research-lookup ✓
        │  ├─ competitive-analysis ✓
        │  ├─ architecture-research ✓
        │  └─ ... (all tasks)
        │
        ├─ Identify parallel opportunities
        │  ├─ Phase 1: research + competitive (parallel)
        │  ├─ Phase 2: architecture (sequential)
        │  ├─ Phase 3: feasibility + risk + cost (parallel)
        │  └─ ... (all phases)
        │
        ├─ Calculate time savings
        │  ├─ Sequential: 120 minutes
        │  ├─ Parallel: 103 minutes
        │  └─ Savings: 17 minutes (14%)
        │
        ├─ Generate recommendation
        │  └─ "full" / "conservative" / "none"
        │
        └─ Present to user via AskUserQuestion
           └─ Re-execute with --parallel if accepted
```

## Analysis Algorithm

### Task Dependencies

The analyzer understands these dependency chains:

**Phase 1: Market Research**
```
research-lookup ──┐
                  ├──> market-research-reports ──> diagrams
competitive-analysis ─┘
```
- `research-lookup` + `competitive-analysis` can run in **PARALLEL**
- `market-research-reports` depends on both (sequential)
- `diagrams` depend on reports (sequential)

**Phase 2: Architecture**
```
market-research ──> architecture-research ──> building-blocks ──> diagrams
```
- All sequential (each step depends on previous)

**Phase 3: Feasibility & Costs** (HIGHEST parallelization opportunity)
```
building-blocks ──┬──> feasibility-analysis ──┐
                  ├──> risk-assessment ────────┼──> diagrams
                  └──> service-cost-analysis ──┘
```
- `feasibility`, `risk`, `cost` can ALL run in **PARALLEL** (60% time savings!)
- `diagrams` depend on all three (sequential)

**Phase 4-6: Sequential**
- Sprint planning, marketing, review all have dependencies
- No parallelization opportunities

### Time Estimation

Each task has an estimated completion time:

| Task | Estimated Time |
|------|----------------|
| research-lookup | 5 min |
| competitive-analysis | 8 min |
| market-research-reports | 10 min |
| architecture-research | 15 min |
| building-blocks | 12 min |
| feasibility-analysis | 10 min |
| risk-assessment | 12 min |
| service-cost-analysis | 15 min |
| sprint-planning | 20 min |
| marketing-campaign | 15 min |
| plan-review | 10 min |
| project-diagrams | 5 min each phase |

**Sequential time:** Sum of all tasks

**Parallel time:** For parallel groups, use MAX(task times) instead of SUM

### Recommendation Logic

| Time Savings | Recommendation | Reasoning |
|--------------|----------------|-----------|
| ≥ 20% | **full** | Significant savings, highly recommended |
| 10-19% | **conservative** | Moderate savings, worth considering |
| < 10% | **none** | Minimal savings, sequential is fine |

## Using the Analyzer

### Command Line Usage

```bash
# Analyze a completed plan
python scripts/analyze-parallelization.py planning_outputs/20260112_143022_my-saas-app

# Output to file
python scripts/analyze-parallelization.py \
  planning_outputs/20260112_143022_my-saas-app \
  --output parallelization-analysis.txt

# JSON format (for programmatic use)
python scripts/analyze-parallelization.py \
  planning_outputs/20260112_143022_my-saas-app \
  --json
```

### Example Output (Text Format)

```
======================================================================
Parallelization Analysis
======================================================================
Plan: 20260112_143022_my-saas-app

Time Comparison:
  Sequential execution: 120 minutes
  Parallel execution:   103 minutes
  Time savings:         17 minutes (14.2%)

Recommendation: CONSERVATIVE
  Moderate time savings (14%) with 2 parallel task groups. Worth considering.

Parallel Execution Groups:
  Phase 1 - PARALLEL (8 min):
    - research-lookup (5 min)
    - competitive-analysis (8 min)
  Phase 1 - Sequential (15 min):
    - market-research-reports (10 min)
    - project-diagrams (5 min)
  Phase 2 - Sequential (35 min):
    - architecture-research (15 min)
    - building-blocks (12 min)
    - project-diagrams (8 min)
  Phase 3 - PARALLEL (15 min):
    - feasibility-analysis (10 min)
    - risk-assessment (12 min)
    - service-cost-analysis (15 min)
  Phase 3 - Sequential (5 min):
    - project-diagrams (5 min)
  Phase 4 - Sequential (25 min):
    - sprint-planning (20 min)
    - project-diagrams (5 min)
  Phase 5 - Sequential (20 min):
    - marketing-campaign (15 min)
    - project-diagrams (5 min)
  Phase 6 - Sequential (10 min):
    - plan-review (10 min)

======================================================================
```

### Example Output (JSON Format)

```json
{
  "plan_name": "20260112_143022_my-saas-app",
  "sequential_time_minutes": 120,
  "parallel_time_minutes": 103,
  "time_savings_minutes": 17,
  "time_savings_percent": 14.2,
  "recommendation": "conservative",
  "reasoning": "Moderate time savings (14%) with 2 parallel task groups. Worth considering.",
  "parallel_groups": [
    {
      "phase": 1,
      "type": "parallel",
      "estimated_time": 8,
      "tasks": ["research-lookup", "competitive-analysis"]
    },
    {
      "phase": 3,
      "type": "parallel",
      "estimated_time": 15,
      "tasks": ["feasibility-analysis", "risk-assessment", "service-cost-analysis"]
    }
  ]
}
```

## Interactive Recommendation

After plan completion, the system presents recommendations via AskUserQuestion:

### Scenario 1: Significant Savings (≥20%)

```
┌─────────────────────────────────────────────────────┐
│ Optimize Planning                                   │
├─────────────────────────────────────────────────────┤
│ Your plan could save ~22% time with parallelization.│
│ Enable it for future similar projects?              │
│                                                      │
│ ● Yes - Full parallelization (Recommended)          │
│   Run 3 task groups in parallel                     │
│   Estimated time: 98 min vs 125 min sequential      │
│   Savings: 27 minutes                               │
│                                                      │
│ ○ Conservative - Only 100% safe parallel tasks      │
│   Run 2 task groups in parallel                     │
│   Estimated time: 110 min                           │
│   Savings: 15 minutes                               │
│                                                      │
│ ○ No - Keep sequential execution                    │
│   No changes to planning workflow                   │
└─────────────────────────────────────────────────────┘
```

### Scenario 2: Moderate Savings (10-19%)

```
┌─────────────────────────────────────────────────────┐
│ Optimize Planning                                   │
├─────────────────────────────────────────────────────┤
│ Your plan could save ~14% time with parallelization.│
│ Consider enabling for future projects?              │
│                                                      │
│ ○ Yes - Full parallelization                        │
│   Run 2 task groups in parallel                     │
│   Savings: 17 minutes (14%)                         │
│                                                      │
│ ● Conservative - Only critical parallel tasks       │
│   Run Phase 3 analysis tasks in parallel only       │
│   Savings: 12 minutes (10%)                         │
│                                                      │
│ ○ No - Sequential is fine                           │
│   Minimal savings, keep current workflow            │
└─────────────────────────────────────────────────────┘
```

### Scenario 3: Minimal Savings (<10%)

```
┌─────────────────────────────────────────────────────┐
│ Parallelization Analysis                            │
├─────────────────────────────────────────────────────┤
│ Your plan would save only ~7% time with             │
│ parallelization. Sequential execution is fine.      │
│                                                      │
│ ● No - Sequential execution (Recommended)           │
│   Minimal savings (5 minutes), not worth complexity │
│                                                      │
│ ○ Yes - Try parallelization anyway                  │
│   Enable for learning/testing purposes              │
└─────────────────────────────────────────────────────┘
```

## Re-Executing with Parallelization

If user accepts the recommendation, the system can:

**Option 1: Save preference for future runs**
```bash
# Save to .claude/project-planner.local.md
echo "prefer_parallelization: true" >> .claude/project-planner.local.md
```

**Option 2: Re-run current plan (not implemented - would require significant rework)**

**Option 3: Show example command for next time**
```
For your next similar project, use:
  /full-plan my-next-project --parallel
```

## Real-World Examples

### Example 1: Large SaaS Application

**Plan structure:**
- Market research: 3 tasks (23 min sequential, 13 min parallel)
- Architecture: 3 tasks (35 min sequential)
- Feasibility: 4 tasks (42 min sequential, 20 min parallel)
- Implementation: 2 tasks (25 min sequential)
- Marketing: 2 tasks (20 min sequential)
- Review: 1 task (10 min sequential)

**Analysis:**
- Sequential: 155 minutes
- Parallel: 123 minutes
- Savings: 32 minutes (21%)
- **Recommendation: FULL** - Highly recommended

### Example 2: Simple Mobile App

**Plan structure:**
- Market research: 2 tasks (13 min sequential, 8 min parallel)
- Architecture: 2 tasks (27 min sequential)
- Feasibility: 2 tasks (22 min sequential, 12 min parallel)
- Implementation: 2 tasks (25 min sequential)
- Review: 1 task (10 min sequential)
- *(No marketing phase)*

**Analysis:**
- Sequential: 97 minutes
- Parallel: 82 minutes
- Savings: 15 minutes (15%)
- **Recommendation: CONSERVATIVE** - Worth considering

### Example 3: Quick Prototype

**Plan structure:**
- Market research: 1 task (10 min)
- Architecture: 2 tasks (27 min)
- Implementation: 1 task (20 min)
- *(No feasibility, no marketing, no review)*

**Analysis:**
- Sequential: 57 minutes
- Parallel: 57 minutes (no parallel opportunities)
- Savings: 0 minutes (0%)
- **Recommendation: NONE** - No parallelization possible

## Best Practices

### 1. Analyze After First Run

For a new project type:
1. Run `/full-plan` without `--parallel` first
2. Review the plan quality
3. Analyze parallelization opportunities
4. Use `--parallel` for subsequent similar projects

### 2. Different Project Types Have Different Savings

| Project Type | Expected Savings |
|--------------|------------------|
| **Enterprise SaaS** | 18-25% (many analysis tasks) |
| **Consumer Mobile App** | 12-18% (moderate complexity) |
| **Internal Tool** | 8-15% (simpler structure) |
| **Quick Prototype** | 0-5% (minimal tasks) |

### 3. Balance Quality and Speed

**When to prioritize parallelization:**
- Recurring project types (you'll run many times)
- Large, complex projects (more tasks = more savings)
- Time-sensitive planning (need results fast)

**When sequential is better:**
- First-time project types (quality over speed)
- Critical projects (want careful review)
- Learning/exploration (easier to follow sequentially)

### 4. Monitor Actual vs Estimated Times

The analyzer uses estimated times. Real times may vary:
- Research tasks can take longer with complex topics
- Simple architectures may complete faster
- Team size affects sprint planning time

Track actual times and adjust estimates for your use case.

## Troubleshooting

### Analysis Returns "No tasks found"

**Problem:** Analyzer can't detect completed tasks

**Solution:**
1. Check directory structure matches expected format:
   ```
   planning_outputs/YYYYMMDD_HHMMSS_project/
   ├── 01_market_research/
   ├── 02_architecture/
   └── ...
   ```
2. Ensure output files have standard names:
   - `research_data.md`
   - `competitive_analysis.md`
   - `architecture_document.md`
   - etc.

### Savings Calculation Seems Wrong

**Problem:** Time savings don't match expectations

**Solution:**
1. Check which tasks actually completed
2. Verify task time estimates are reasonable for your project
3. Remember: Parallel time uses MAX(tasks) not SUM(tasks)

Example:
- Task A: 10 min
- Task B: 15 min
- Sequential: 10 + 15 = 25 min
- Parallel: MAX(10, 15) = 15 min ✓

### "Conservative" vs "Full" Unclear

**Conservative:**
- Only parallelize tasks with ZERO risk of context loss
- Typically: Phase 1 research + Phase 3 analysis only
- Safest option

**Full:**
- Parallelize all independent tasks
- Includes tasks that share some context
- Maximum time savings
- May have subtle context-sharing edge cases

**When in doubt, start with Conservative.**

## Integration with /full-plan

The post-plan analysis is automatically offered after plan completion:

```bash
$ /full-plan my-project --skip-marketing

# ... plan executes ...

✓ Phase 6 complete! Plan saved to: planning_outputs/20260112_143022_my-project/

Analyzing parallelization opportunities...

Your plan took ~103 minutes. With parallelization, it could complete in ~88 minutes.
Time savings: 15 minutes (15%)

[AskUserQuestion prompt appears]

Enable parallelization for future similar projects? ...
```

User selection is saved and applied to future runs.

## Advanced: Custom Time Estimates

For power users who want custom time estimates:

```python
# Edit scripts/analyze-parallelization.py
TASK_DEFINITIONS = {
    "research-lookup": TaskInfo("research-lookup", 1, 8, []),  # Changed from 5 to 8
    "competitive-analysis": TaskInfo("competitive-analysis", 1, 12, []),  # Changed from 8 to 12
    # ... update others ...
}
```

This allows you to calibrate estimates based on your actual planning times.

## Summary

**Post-plan parallelization analysis helps you:**
- ✅ Understand time-saving opportunities
- ✅ Make informed decisions about parallelization
- ✅ Optimize future planning sessions
- ✅ Balance speed and quality

**Key takeaway:** Run analysis after your first plan, then use parallelization for similar projects to save 10-25% time.
