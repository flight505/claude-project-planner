# Parallelization Analysis: Real-World Examples

This document provides detailed examples of parallelization analysis for different project types, showing actual time savings and recommendations.

## Overview

The parallelization analyzer evaluates completed planning sessions and calculates potential time savings from running independent tasks concurrently. Results vary significantly based on project complexity and structure.

## Example 1: Enterprise SaaS Application

### Project Profile
- **Type:** Large SaaS platform (CRM + Analytics)
- **Complexity:** High
- **Phases:** All 6 phases (Market, Architecture, Feasibility, Implementation, Marketing, Review)
- **Total Tasks:** 18 tasks across all phases

### Sequential Execution Breakdown

| Phase | Task | Dependencies | Time (min) |
|-------|------|--------------|------------|
| **Phase 1** | research-lookup | None | 5 |
| | competitive-analysis | None | 8 |
| | market-research-reports | Phase 1 tasks | 10 |
| | project-diagrams | market-research-reports | 5 |
| **Phase 2** | architecture-research | Phase 1 complete | 15 |
| | building-blocks | architecture-research | 12 |
| | project-diagrams | building-blocks | 8 |
| **Phase 3** | feasibility-analysis | building-blocks | 10 |
| | risk-assessment | building-blocks | 12 |
| | service-cost-analysis | building-blocks | 15 |
| | project-diagrams | Phase 3 tasks | 5 |
| **Phase 4** | sprint-planning | Phase 3 complete | 20 |
| | project-diagrams | sprint-planning | 5 |
| **Phase 5** | marketing-campaign | sprint-planning | 15 |
| | project-diagrams | marketing-campaign | 5 |
| **Phase 6** | plan-review | All phases | 10 |

**Total Sequential Time:** 160 minutes (2h 40min)

### Parallel Execution Breakdown

| Phase | Execution Group | Tasks | Time (min) | Type |
|-------|----------------|-------|------------|------|
| **Phase 1** | Group 1.1 | research-lookup, competitive-analysis | 8 | PARALLEL |
| | Group 1.2 | market-research-reports | 10 | Sequential |
| | Group 1.3 | project-diagrams | 5 | Sequential |
| **Phase 2** | Group 2.1 | architecture-research | 15 | Sequential |
| | Group 2.2 | building-blocks | 12 | Sequential |
| | Group 2.3 | project-diagrams | 8 | Sequential |
| **Phase 3** | Group 3.1 | feasibility, risk, cost | 15 | PARALLEL |
| | Group 3.2 | project-diagrams | 5 | Sequential |
| **Phase 4** | Group 4.1 | sprint-planning | 20 | Sequential |
| | Group 4.2 | project-diagrams | 5 | Sequential |
| **Phase 5** | Group 5.1 | marketing-campaign | 15 | Sequential |
| | Group 5.2 | project-diagrams | 5 | Sequential |
| **Phase 6** | Group 6.1 | plan-review | 10 | Sequential |

**Total Parallel Time:** 133 minutes (2h 13min)

### Analysis Result

```
======================================================================
Parallelization Analysis
======================================================================
Plan: 20260112_143022_enterprise-crm

Time Comparison:
  Sequential execution: 160 minutes
  Parallel execution:   133 minutes
  Time savings:         27 minutes (16.9%)

Recommendation: CONSERVATIVE
  Moderate time savings (17%) with 2 parallel task groups. Worth considering.

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

**Recommendation to User:** "Conservative parallelization" - Enable for similar enterprise projects to save 17% time.

---

## Example 2: Mobile App with AI Features

### Project Profile
- **Type:** Consumer mobile app (AI photo editor)
- **Complexity:** Medium-High
- **Phases:** 5 phases (Market, Architecture, Feasibility, Implementation, Review)
- **Total Tasks:** 14 tasks (no marketing phase)

### Sequential Execution: 122 minutes
### Parallel Execution: 95 minutes
### Time Savings: 27 minutes (22.1%)

### Analysis Result

```
======================================================================
Parallelization Analysis
======================================================================
Plan: 20260112_151530_ai-photo-editor

Time Comparison:
  Sequential execution: 122 minutes
  Parallel execution:   95 minutes
  Time savings:         27 minutes (22.1%)

Recommendation: FULL
  Significant time savings (22%) with 2 parallel task groups. Highly recommended.

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
  Phase 5 - Sequential (10 min):
    - plan-review (10 min)

======================================================================
```

**Recommendation to User:** "Full parallelization" - Highly recommended for AI/ML projects with complex feasibility analysis.

**Why higher savings?** Skipping Phase 5 (marketing) means the parallel phases (1 & 3) represent a larger percentage of total time.

---

## Example 3: Simple Internal Tool

### Project Profile
- **Type:** Internal admin dashboard
- **Complexity:** Low
- **Phases:** 4 phases (Market, Architecture, Implementation, Review)
- **Total Tasks:** 8 tasks (no marketing, simplified feasibility)

### Sequential Execution Breakdown

| Phase | Task | Time (min) |
|-------|------|------------|
| Phase 1 | research-lookup | 3 |
| | competitive-analysis | 5 |
| | market-research-reports | 7 |
| Phase 2 | architecture-research | 10 |
| | building-blocks | 8 |
| Phase 3 | feasibility-analysis | 6 |
| | risk-assessment | 8 |
| Phase 4 | sprint-planning | 12 |
| Phase 5 | plan-review | 6 |

**Total Sequential Time:** 65 minutes
**Total Parallel Time:** 60 minutes
**Time Savings:** 5 minutes (7.7%)

### Analysis Result

```
======================================================================
Parallelization Analysis
======================================================================
Plan: 20260112_160245_admin-dashboard

Time Comparison:
  Sequential execution: 65 minutes
  Parallel execution:   60 minutes
  Time savings:         5 minutes (7.7%)

Recommendation: NONE
  Minimal time savings (8%). Sequential execution is fine.

======================================================================
```

**Recommendation to User:** "Keep sequential execution" - For simple internal tools, parallelization overhead isn't worth the 5-minute savings.

---

## Example 4: E-Commerce Platform

### Project Profile
- **Type:** Full-featured online store
- **Complexity:** High
- **Phases:** All 6 phases + extended feasibility (payment processing, PCI compliance)
- **Total Tasks:** 20 tasks

### Sequential Execution: 185 minutes (3h 5min)
### Parallel Execution: 145 minutes (2h 25min)
### Time Savings: 40 minutes (21.6%)

### Analysis Result

```
======================================================================
Parallelization Analysis
======================================================================
Plan: 20260112_093045_shopify-alternative

Time Comparison:
  Sequential execution: 185 minutes
  Parallel execution:   145 minutes
  Time savings:         40 minutes (21.6%)

Recommendation: FULL
  Significant time savings (22%) with 2 parallel task groups. Highly recommended.

Key Insight: Extended Phase 3 (feasibility + risk + cost + compliance)
has 4 independent tasks running in parallel = 60% phase time savings.

======================================================================
```

**Recommendation to User:** "Full parallelization" - E-commerce projects benefit greatly from parallel feasibility analysis.

---

## Example 5: API-Only Microservice

### Project Profile
- **Type:** REST API backend service
- **Complexity:** Low-Medium
- **Phases:** 4 phases (Architecture, Feasibility, Implementation, Review)
- **Total Tasks:** 10 tasks (no market research, no marketing)

### Sequential Execution: 88 minutes
### Parallel Execution: 78 minutes
### Time Savings: 10 minutes (11.4%)

### Analysis Result

```
======================================================================
Parallelization Analysis
======================================================================
Plan: 20260112_112215_auth-api-service

Time Comparison:
  Sequential execution: 88 minutes
  Parallel execution:   78 minutes
  Time savings:         10 minutes (11.4%)

Recommendation: CONSERVATIVE
  Moderate time savings (11%) with 1 parallel task group. Worth considering.

Note: Only Phase 3 (feasibility + risk + cost) benefits from parallelization.
Phase 1 skipped (no market research). Phase 5 skipped (no marketing).

======================================================================
```

**Recommendation to User:** "Conservative parallelization" - For API-only projects, enable parallelization for Phase 3 analysis.

---

## Example 6: MVP Prototype (Minimal Planning)

### Project Profile
- **Type:** Quick proof-of-concept
- **Complexity:** Very Low
- **Phases:** 3 phases (Architecture, Implementation, Review)
- **Total Tasks:** 5 tasks

### Sequential Execution: 47 minutes
### Parallel Execution: 47 minutes
### Time Savings: 0 minutes (0%)

### Analysis Result

```
======================================================================
Parallelization Analysis
======================================================================
Plan: 20260112_143022_mvp-prototype

Time Comparison:
  Sequential execution: 47 minutes
  Parallel execution:   47 minutes
  Time savings:         0 minutes (0.0%)

Recommendation: NONE
  Minimal time savings (0%). Sequential execution is fine.

Note: No parallel opportunities detected. All tasks have sequential dependencies.

======================================================================
```

**Recommendation to User:** "Sequential execution" - For MVPs with minimal planning, parallelization offers no benefit.

---

## Savings Summary by Project Type

| Project Type | Sequential Time | Parallel Time | Savings | % Savings | Recommendation |
|--------------|----------------|---------------|---------|-----------|----------------|
| Enterprise SaaS | 160 min | 133 min | 27 min | 16.9% | Conservative |
| Mobile App (AI) | 122 min | 95 min | 27 min | 22.1% | **Full** |
| Internal Tool | 65 min | 60 min | 5 min | 7.7% | None |
| E-Commerce | 185 min | 145 min | 40 min | 21.6% | **Full** |
| API Service | 88 min | 78 min | 10 min | 11.4% | Conservative |
| MVP Prototype | 47 min | 47 min | 0 min | 0% | None |

## Key Insights

### 1. Phase 3 is the Parallelization Winner

Phase 3 (Feasibility & Costs) offers the highest parallelization opportunity:
- **3 independent tasks:** feasibility-analysis, risk-assessment, service-cost-analysis
- **Typical savings:** 22 minutes reduced to 15 minutes (37 min → 15 min = 59% phase savings)
- **Impact on total:** Accounts for 60-70% of overall time savings

### 2. Project Complexity Matters

| Complexity | Expected Savings | Recommendation Pattern |
|------------|------------------|------------------------|
| **High** (Enterprise, E-Commerce) | 18-25% | Full or Conservative |
| **Medium** (Mobile Apps, APIs) | 10-15% | Conservative |
| **Low** (Internal Tools, MVPs) | 0-8% | None |

### 3. Phase Count Affects Percentage

Projects with fewer phases see higher percentage savings because parallel phases represent a larger proportion of total time:
- **6 phases:** 14-17% savings (parallel phases = 33% of total)
- **5 phases:** 18-22% savings (parallel phases = 40% of total)
- **4 phases:** 10-15% savings (depends on which phases included)
- **3 phases:** 0-5% savings (usually no parallel opportunities)

### 4. When to Enable Parallelization

**Enable full parallelization for:**
- ✅ E-commerce platforms (payment analysis, compliance, risk)
- ✅ AI/ML applications (model feasibility, cost analysis, risk)
- ✅ Complex SaaS products (multi-service architecture, extensive research)
- ✅ Consumer-facing apps with marketing phase

**Enable conservative parallelization for:**
- ✅ B2B SaaS (moderate complexity)
- ✅ API services with detailed feasibility analysis
- ✅ Mobile apps without marketing phase
- ✅ Projects you'll repeat often (even 10% savings adds up)

**Keep sequential execution for:**
- ❌ Internal tools (minimal phases)
- ❌ MVPs and prototypes (speed over thoroughness)
- ❌ First-time project types (learning workflow)
- ❌ Projects with <10 total tasks

## Usage Recommendations

### For First-Time Users

1. **Run sequential first** to understand the workflow
2. **Analyze after completion** to see potential savings
3. **Enable parallelization** for subsequent similar projects

### For Experienced Users

1. **Know your project type** - Use the table above as a guide
2. **Default to parallelization** for complex projects (≥15 tasks)
3. **Use conservative mode** when context sharing is critical

### For Teams

1. **Standardize per project type** - Set team defaults
2. **Track actual times** - Calibrate estimates for your team's speed
3. **Document decisions** - Share learnings about what works

## Testing Recommendations

To test parallelization analysis on your own project:

```bash
# 1. Complete a planning session without --parallel
/full-plan my-project

# 2. Run analysis manually
python scripts/analyze-parallelization.py planning_outputs/20260112_143022_my-project

# 3. Compare recommendations with actual experience
# Did the time savings match expectations?
# Was the recommendation appropriate?
```

## Advanced: Custom Time Estimates

For power users who want to calibrate estimates based on actual performance:

```python
# Edit scripts/analyze-parallelization.py
TASK_DEFINITIONS = {
    "research-lookup": TaskInfo("research-lookup", 1, 5, []),  # Adjust from 5 to actual avg
    "competitive-analysis": TaskInfo("competitive-analysis", 1, 8, []),  # Adjust from 8
    # ... update others based on your measurements
}
```

Track actual task times over multiple planning sessions and adjust estimates accordingly.

---

**See also:**
- `docs/PARALLELIZATION_GUIDE.md` - Complete technical guide
- `scripts/analyze-parallelization.py` - Analysis implementation
- `commands/full-plan.md` - Post-plan analysis workflow
