# Smart Parallelization Strategy

This document explains how the Claude Project Planner parallelizes tasks within phases while maintaining context integrity between phases.

## Core Principle

**Phases are sequential, tasks within phases can be parallel.**

```
Phase 1 ──────────────────────> Phase 2 ──────────────────────> Phase 3 ...
    │                               │                               │
    ├── Task A ──┐                  ├── Task D                      ├── Task G ──┐
    ├── Task B ──┼── parallel       │                               ├── Task H ──┼── parallel
    └── Task C ──┘                  └── Task E ─> Task F            └── Task I ──┘
                                        (sequential)
```

## Phase-by-Phase Analysis

### Phase 1: Market Research

| Task | Skill | Dependencies | Can Parallelize With |
|------|-------|--------------|---------------------|
| Market data lookup | `research-lookup` | None | ✅ competitive-analysis |
| Competitive analysis | `competitive-analysis` | None | ✅ research-lookup |
| Market research report | `market-research-reports` | Prefers market data | After parallel batch |
| Market diagrams | `project-diagrams` | All research complete | After report |

**Parallel Groups:**
```
Group 1.1 (parallel): research-lookup + competitive-analysis
Group 1.2 (sequential): market-research-reports (uses Group 1.1 context)
Group 1.3 (sequential): diagrams (uses all above)
```

**Time Savings:** ~30% of Phase 1 (research tasks run in parallel)

---

### Phase 2: Architecture Design

| Task | Skill | Dependencies | Can Parallelize With |
|------|-------|--------------|---------------------|
| Architecture research | `architecture-research` | Phase 1 context | None (first task) |
| Building blocks | `building-blocks` | Architecture decisions | None (needs arch) |
| Architecture diagrams | `project-diagrams` | Building blocks | None (needs blocks) |

**Parallel Groups:**
```
Group 2.1 (sequential): architecture-research
Group 2.2 (sequential): building-blocks
Group 2.3 (sequential): diagrams
```

**Time Savings:** Minimal (sequential dependencies)

---

### Phase 3: Feasibility & Costs

| Task | Skill | Dependencies | Can Parallelize With |
|------|-------|--------------|---------------------|
| Feasibility analysis | `feasibility-analysis` | Architecture only | ✅ risk + cost |
| Risk assessment | `risk-assessment` | Architecture only | ✅ feasibility + cost |
| Service cost analysis | `service-cost-analysis` | Architecture only | ✅ feasibility + risk |
| Analysis diagrams | `project-diagrams` | All analyses | After parallel batch |

**Parallel Groups:**
```
Group 3.1 (parallel): feasibility + risk-assessment + service-cost
Group 3.2 (sequential): diagrams (uses Group 3.1 context)
```

**Time Savings:** ~60% of Phase 3 (3 tasks run in parallel instead of sequential)

---

### Phase 4: Implementation Planning

| Task | Skill | Dependencies | Can Parallelize With |
|------|-------|--------------|---------------------|
| Sprint planning | `sprint-planning` | Building blocks + costs | None (needs prior phases) |
| Milestone definition | Part of sprint | Sprint plan | None |
| Timeline diagrams | `project-diagrams` | Sprint plan | None |

**Parallel Groups:**
```
Group 4.1 (sequential): sprint-planning + milestones
Group 4.2 (sequential): diagrams
```

**Time Savings:** Minimal (sequential dependencies)

---

### Phase 5: Go-to-Market

| Task | Skill | Dependencies | Can Parallelize With |
|------|-------|--------------|---------------------|
| Marketing campaign | `marketing-campaign` | Phase 1-4 context | None (first task) |
| Content calendar | Part of marketing | Campaign strategy | None |
| Campaign diagrams | `project-diagrams` | Campaign plan | None |

**Parallel Groups:**
```
Group 5.1 (sequential): marketing-campaign + content-calendar
Group 5.2 (sequential): diagrams
```

**Time Savings:** Minimal (sequential dependencies)

---

### Phase 6: Review & Synthesis

| Task | Skill | Dependencies | Can Parallelize With |
|------|-------|--------------|---------------------|
| Plan review | `plan-review` | All phases | None |
| Executive summary | Synthesis | All phases | None |

**Parallel Groups:**
```
Group 6.1 (sequential): plan-review
Group 6.2 (sequential): executive-summary
```

**Time Savings:** None (requires all context)

---

## Context Sharing Strategy

### How Parallel Tasks Share Context

When tasks run in parallel, they need access to:
1. **Input context** - What they need to start (from prior phases)
2. **Output context** - What they produce (for subsequent tasks)

**Mechanism: Shared Context File**

```
planning_outputs/<project>/
├── .context/
│   ├── phase1_input.md       # Context entering Phase 1
│   ├── phase1_output.md      # Context produced by Phase 1
│   ├── phase2_input.md       # = phase1_output.md + any additions
│   ├── phase2_output.md      # Context produced by Phase 2
│   └── ...
```

**Before parallel group:**
```python
# Merge all prior context into shared input
shared_context = merge_context(prior_phases)
write_context_file(f"phase{N}_input.md", shared_context)
```

**After parallel group:**
```python
# Collect outputs from all parallel tasks
for task in completed_tasks:
    task_output = extract_key_findings(task.output_file)
    append_to_context(f"phase{N}_output.md", task_output)
```

### Key Findings Extraction

Each skill extracts key findings for context:

| Skill | Key Findings Extracted |
|-------|----------------------|
| `research-lookup` | Market size, trends, key stats |
| `competitive-analysis` | Competitor names, differentiators, gaps |
| `architecture-research` | Tech stack, patterns, trade-offs |
| `building-blocks` | Component names, dependencies, estimates |
| `feasibility-analysis` | Viability score, blockers, recommendations |
| `risk-assessment` | Top 3-5 risks with mitigations |
| `service-cost-analysis` | Monthly cost estimate, breakdown |
| `sprint-planning` | Sprint count, MVP milestone, timeline |

---

## Implementation Details

### Parallel Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         /full-plan --parallel                    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: Market Research                                         │
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │ research-lookup  │    │ competitive-     │   ← Parallel      │
│  │                  │    │ analysis         │                   │
│  └────────┬─────────┘    └────────┬─────────┘                   │
│           │                       │                              │
│           └───────────┬───────────┘                              │
│                       ▼                                          │
│           ┌──────────────────────┐                               │
│           │ Merge context        │   ← Context sync point        │
│           └──────────┬───────────┘                               │
│                      ▼                                           │
│           ┌──────────────────────┐                               │
│           │ market-research-     │   ← Uses merged context       │
│           │ reports              │                               │
│           └──────────┬───────────┘                               │
│                      ▼                                           │
│           ┌──────────────────────┐                               │
│           │ project-diagrams     │                               │
│           └──────────────────────┘                               │
│                                                                  │
│  Save Phase 1 context → .context/phase1_output.md               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 2: Architecture (mostly sequential)                        │
│                                                                  │
│  Load Phase 1 context                                           │
│  architecture-research → building-blocks → diagrams             │
│  Save Phase 2 context                                           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 3: Feasibility (HIGH parallelization)                      │
│                                                                  │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│  │ feasibility-     │ │ risk-assessment  │ │ service-cost-    │ │
│  │ analysis         │ │                  │ │ analysis         │ │
│  └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘ │
│           │                    │                    │            │
│           └────────────────────┼────────────────────┘            │
│                                ▼                                 │
│                    ┌──────────────────────┐                      │
│                    │ Merge context        │                      │
│                    └──────────┬───────────┘                      │
│                               ▼                                  │
│                    ┌──────────────────────┐                      │
│                    │ diagrams             │                      │
│                    └──────────────────────┘                      │
│                                                                  │
│  Save Phase 3 context                                           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
                    ... Phases 4, 5, 6 (mostly sequential) ...
```

---

## Expected Time Savings

| Phase | Sequential Time | Parallel Time | Savings |
|-------|-----------------|---------------|---------|
| Phase 1 | 30 min | 20 min | 33% |
| Phase 2 | 45 min | 45 min | 0% |
| Phase 3 | 30 min | 12 min | 60% |
| Phase 4 | 30 min | 30 min | 0% |
| Phase 5 | 30 min | 30 min | 0% |
| Phase 6 | 30 min | 30 min | 0% |
| **Total** | **195 min** | **167 min** | **14%** |

**Note:** The biggest win is Phase 3 where three analysis tasks run in parallel.

---

## Usage

```bash
# Standard sequential execution
/full-plan

# Enable smart parallelization
/full-plan --parallel

# Parallel with multi-model validation
/full-plan --parallel --validate
```

---

## Error Handling

If a parallel task fails:
1. Other parallel tasks continue (don't cascade failure)
2. Failed task is marked in progress tracker
3. After parallel group completes, report which tasks failed
4. Offer to retry failed tasks or continue without them
