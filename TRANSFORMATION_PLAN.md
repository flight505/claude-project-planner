# Claude Project Planner - Transformation Plan

> **Transforming `claude-scientific-writer` into `claude-project-planner`**
> A comprehensive AI-powered project research and planning plugin for Claude Code

---

## Executive Summary

This document outlines the complete transformation of the `claude-scientific-writer` plugin (originally designed for academic papers and literature reviews) into `claude-project-planner` - a tool for software project planning, architecture research, and implementation roadmaps.

### Vision

Create a Claude Code plugin that can:
- 📊 Research business cases and market opportunities
- 🏛️ Design software architectures with ADRs and C4 diagrams
- 🧱 Break projects into Claude Code-buildable components
- 💰 Analyze service costs and ROI projections
- 📋 Generate sprint plans and implementation timelines
- ⚠️ Assess technical and business risks

### Repository

- **Name:** `claude-project-planner`
- **URL:** https://github.com/flight505/claude-project-planner
- **License:** MIT (inherited from original)

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Target Architecture](#2-target-architecture)
3. [Skill Transformation Matrix](#3-skill-transformation-matrix)
4. [Implementation Phases](#4-implementation-phases)
5. [Technical Specifications](#5-technical-specifications)
6. [Output Structure](#6-output-structure)
7. [Testing Strategy](#7-testing-strategy)
8. [Timeline & Milestones](#8-timeline--milestones)
9. [Risk Assessment](#9-risk-assessment)
10. [Success Criteria](#10-success-criteria)

---

## 1. Current State Analysis

### Original Project: claude-scientific-writer

| Aspect | Details |
|--------|---------|
| **Purpose** | Generate publication-ready scientific documents |
| **Skills** | 25 skills for research, writing, citations |
| **Core API** | `generate_paper()` async generator |
| **Output** | LaTeX papers, literature reviews, clinical reports |
| **Research** | Perplexity Sonar integration for literature search |

### Key Strengths to Preserve

1. **Async Generator Pattern** - Streams progress updates, perfect for long-running tasks
2. **Modular Skill System** - Each skill is self-contained with SKILL.md
3. **Research Integration** - Perplexity API for real-time research
4. **Quality Review** - Built-in peer review capability
5. **File Organization** - Structured output with versioning

### What Works Well (Keep)

```
✅ research-lookup/          # Perplexity integration - CRITICAL
✅ generate-image/           # Mockups and visualizations
✅ scientific-schematics/    # Diagram generation (rename to project-diagrams)
✅ markitdown/               # File conversion utility
✅ document-skills/          # docx/pdf/pptx manipulation
✅ market-research-reports/  # Modify for business cases
```

---

## 2. Target Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CLAUDE PROJECT PLANNER                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         CLI / API                                │   │
│   │    project-planner CLI    |    generate_project() async API     │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      CORE PYTHON PACKAGE                         │   │
│   │  project_planner/                                                │   │
│   │    ├── api.py       # Async project generation                   │   │
│   │    ├── cli.py       # Interactive CLI                            │   │
│   │    ├── core.py      # Setup, file handling                       │   │
│   │    ├── models.py    # ProjectResult, BuildingBlock, etc.         │   │
│   │    └── utils.py     # Project scanning, detection                │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         SKILLS (13)                              │   │
│   ├─────────────┬─────────────┬─────────────┬───────────────────────┤   │
│   │  RESEARCH   │  ANALYSIS   │    SPECS    │      PLANNING         │   │
│   ├─────────────┼─────────────┼─────────────┼───────────────────────┤   │
│   │ research-   │ feasibility │ building-   │ sprint-planning       │   │
│   │   lookup    │   -analysis │   blocks    │                       │   │
│   │ architecture│ service-    │ project-    │ risk-assessment       │   │
│   │   -research │   cost-     │   diagrams  │                       │   │
│   │ competitive │   analysis  │             │ plan-review           │   │
│   │   -analysis │             │             │                       │   │
│   │ business-   │             │             │                       │   │
│   │   case      │             │             │                       │   │
│   └─────────────┴─────────────┴─────────────┴───────────────────────┘   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                        UTILITIES                                 │   │
│   │    generate-image  |  markitdown  |  document-skills             │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Workflow Pipeline

```
User Request
     │
     ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ RESEARCH    │───▶│  ANALYSIS   │───▶│   SPECS     │───▶│  PLANNING   │
│             │    │             │    │             │    │             │
│ • Market    │    │ • Feasibil- │    │ • PRD       │    │ • Sprints   │
│ • Tech      │    │   ity       │    │ • Technical │    │ • Timeline  │
│ • Competi-  │    │ • Costs     │    │ • Components│    │ • Risks     │
│   tive      │    │ • ROI       │    │ • API       │    │ • Review    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
                                              ┌─────────────────────────┐
                                              │  planning_outputs/      │
                                              │  └── <project>/         │
                                              │      ├── research/      │
                                              │      ├── analysis/      │
                                              │      ├── specifications/│
                                              │      ├── components/    │
                                              │      ├── planning/      │
                                              │      └── diagrams/      │
                                              └─────────────────────────┘
```

---

## 3. Skill Transformation Matrix

### Skills Overview

| # | Skill Name | Action | Purpose |
|---|------------|--------|---------|
| 1 | `research-lookup` | **KEEP** | Perplexity Sonar for market/tech research |
| 2 | `project-diagrams` | **MODIFY** | Architecture & flow diagrams (from scientific-schematics) |
| 3 | `generate-image` | **KEEP** | Mockups and visualizations |
| 4 | `markitdown` | **KEEP** | File conversion utility |
| 5 | `document-skills` | **KEEP** | docx/pdf/pptx manipulation |
| 6 | `business-case-research` | **MODIFY** | ROI, market analysis (from market-research-reports) |
| 7 | `competitive-analysis` | **MODIFY** | Competitor research (from literature-review) |
| 8 | `feasibility-analysis` | **MODIFY** | Tech/business feasibility (from scientific-critical-thinking) |
| 9 | `plan-review` | **MODIFY** | Project plan quality review (from peer-review) |
| 10 | `architecture-research` | **NEW** | Tech stack comparison, ADRs, C4 model |
| 11 | `building-blocks` | **NEW** | Component breakdown for Claude Code |
| 12 | `service-cost-analysis` | **NEW** | Cloud/API pricing comparison, TCO |
| 13 | `sprint-planning` | **NEW** | Sprint backlogs, timelines, INVEST stories |
| 14 | `risk-assessment` | **NEW** | Technical/business risk analysis |

### Skills to Remove (12)

These are scientific-writing specific and not needed:
- `scientific-writing`, `citation-management`, `venue-templates`
- `clinical-reports`, `clinical-decision-support`, `treatment-plans`
- `hypothesis-generation`, `latex-posters`, `pptx-posters`
- `scientific-slides`, `paper-2-web`, `scholar-evaluation`
- `research-grants` (partially adapted into project-proposals if needed)

---

## 4. Implementation Phases

### Phase 1: Foundation (Days 1-3)

**Objective:** Rename package and establish new structure

| Task | File(s) | Status |
|------|---------|--------|
| Rename `scientific_writer/` → `project_planner/` | Directory | ⬜ |
| Update `pyproject.toml` with new name/version | `pyproject.toml` | ⬜ |
| Update all import statements | `*.py` | ⬜ |
| Rename `WRITER.md` → `PLANNER.md` | `.claude/` | ⬜ |
| Update output folder `writing_outputs/` → `planning_outputs/` | `core.py` | ⬜ |

### Phase 2: Data Models (Days 4-5)

**Objective:** Create new dataclasses for project planning

| Task | File(s) | Status |
|------|---------|--------|
| Create `ProjectMetadata` dataclass | `models.py` | ⬜ |
| Create `ProjectFiles` dataclass | `models.py` | ⬜ |
| Create `ProjectResult` dataclass | `models.py` | ⬜ |
| Create `BuildingBlock` dataclass | `models.py` | ⬜ |
| Create `ServiceCostEstimate` dataclass | `models.py` | ⬜ |
| Create `SprintDefinition` dataclass | `models.py` | ⬜ |
| Create `RiskItem` dataclass | `models.py` | ⬜ |

### Phase 3: API & CLI (Days 6-8)

**Objective:** Update core API and CLI for project planning

| Task | File(s) | Status |
|------|---------|--------|
| Rename `generate_paper()` → `generate_project()` | `api.py` | ⬜ |
| Update `PROGRESS_STAGES` for project workflow | `api.py` | ⬜ |
| Update `_build_project_result()` | `api.py` | ⬜ |
| Rename `find_existing_papers()` → `find_existing_projects()` | `utils.py` | ⬜ |
| Update `detect_project_reference()` keywords | `utils.py` | ⬜ |
| Update CLI welcome message and help | `cli.py` | ⬜ |

### Phase 4: Skills (Days 9-14)

**Objective:** Create and modify skills

#### Keep Unchanged (2 days)
- Copy `research-lookup/`, `generate-image/`, `markitdown/`, `document-skills/`

#### Modify Existing (3 days)
- `scientific-schematics/` → `project-diagrams/`
- `market-research-reports/` → `business-case-research/`
- `literature-review/` → `competitive-analysis/`
- `peer-review/` → `plan-review/`
- `scientific-critical-thinking/` → `feasibility-analysis/`

#### Create New (5 days)
- `architecture-research/` (ADR, C4, tech stack)
- `building-blocks/` (component specs for Claude Code)
- `service-cost-analysis/` (cloud pricing, TCO)
- `sprint-planning/` (INVEST stories, timelines)
- `risk-assessment/` (risk register, mitigation)

### Phase 5: System Instructions (Days 15-16)

**Objective:** Rewrite CLAUDE.md and PLANNER.md

| Task | File(s) | Status |
|------|---------|--------|
| Write new `CLAUDE.md` for project planning | `CLAUDE.md` | ⬜ |
| Write new `PLANNER.md` system instructions | `.claude/PLANNER.md` | ⬜ |
| Update `marketplace.json` | `.claude-plugin/` | ⬜ |

### Phase 6: Testing & Documentation (Days 17-20)

**Objective:** Validate and document

| Task | File(s) | Status |
|------|---------|--------|
| Run unit tests (75+ tests) | `tests/` | ⬜ |
| Run integration tests (15+ tests) | `tests/` | ⬜ |
| Execute smoke test scenarios (5) | Manual | ⬜ |
| Update `README.md` | `README.md` | ⬜ |
| Update `CHANGELOG.md` | `CHANGELOG.md` | ⬜ |
| Create example prompts | `examples/` | ⬜ |

---

## 5. Technical Specifications

### New Progress Stages

```python
PROGRESS_STAGES = [
    "initialization",      # Setting up project structure
    "requirements",        # Gathering and analyzing requirements
    "research",            # Architecture research and patterns lookup
    "architecture",        # Designing system architecture
    "components",          # Defining building blocks
    "cost_analysis",       # Service cost estimation
    "sprint_planning",     # Creating sprint plans
    "risk_assessment",     # Risk analysis and mitigation
    "documentation",       # Writing final documentation
    "complete",            # All done
]
```

### New Data Models

```python
@dataclass
class ProjectMetadata:
    name: str
    type: str  # "saas", "mobile_app", "api", "fullstack", "cli"
    created_at: str
    estimated_complexity: str  # "small", "medium", "large", "enterprise"
    architecture_type: Optional[str]  # "monolith", "microservices", "serverless"
    estimated_cost: Optional[str]
    estimated_timeline: Optional[str]
    tech_stack: Optional[List[str]]

@dataclass
class BuildingBlock:
    name: str
    type: str  # "frontend", "backend", "infrastructure", "integration"
    description: str
    responsibilities: List[str]
    dependencies: List[str]
    interfaces: Dict[str, Any]
    complexity: str  # "S", "M", "L", "XL"
    estimated_hours: Optional[int]
    implementation_notes: Optional[str]

@dataclass
class ProjectResult:
    type: str = "result"
    status: str  # "success", "partial", "failed"
    project_directory: str
    project_name: str
    metadata: ProjectMetadata
    files: ProjectFiles
    components: List[BuildingBlock]
    total_estimated_cost: Optional[str]
    total_estimated_hours: Optional[int]
    sprint_count: Optional[int]
    errors: List[str]
    token_usage: Optional[TokenUsage]
```

### API Signature

```python
async def generate_project(
    query: str,
    output_dir: Optional[str] = None,
    data_files: Optional[List[str]] = None,
    project_type: Literal["full", "architecture", "sprint", "cost", "risk"] = "full",
    effort_level: Literal["low", "medium", "high"] = "medium",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    track_token_usage: bool = False,
    auto_continue: bool = True,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Generate a comprehensive project plan with architecture, components, and sprints.

    Args:
        query: Project description or requirements
        output_dir: Custom output directory (default: ./planning_outputs)
        data_files: Additional context files (specs, mockups, etc.)
        project_type: Type of output ("full" generates everything)
        effort_level: "low" (Haiku), "medium" (Sonnet), "high" (Opus)
        model: Override model selection
        api_key: Anthropic API key (default: from env)
        track_token_usage: Track and return token usage
        auto_continue: Auto-continue on completion (default: True)

    Yields:
        Dict with "type" key: "progress", "text", or "result"
    """
```

---

## 6. Output Structure

### Project Output Directory

```
planning_outputs/
└── 20250106_143022_inventory_saas/
    │
    ├── progress.md                    # Real-time progress log
    ├── SUMMARY.md                     # Executive summary & next steps
    ├── PLAN_REVIEW.md                 # Quality assessment
    │
    ├── research/
    │   ├── market_research.md         # TAM/SAM/SOM, market opportunity
    │   ├── competitive_analysis.md    # Competitor matrix, positioning
    │   ├── technology_research.md     # Tech stack comparison, ADRs
    │   └── sources/                   # Source materials, references
    │
    ├── analysis/
    │   ├── feasibility_analysis.md    # Technical & business feasibility
    │   ├── risk_assessment.md         # Risk register with mitigations
    │   ├── cost_analysis.md           # Service cost comparison
    │   └── roi_projections.md         # 3-year ROI model
    │
    ├── specifications/
    │   ├── project_spec.md            # Main PRD
    │   ├── technical_spec.md          # Architecture document
    │   ├── api_spec.md                # API specifications (OpenAPI)
    │   └── data_model.md              # Database schemas, ERD
    │
    ├── components/                    # Claude Code building blocks
    │   ├── component_breakdown.md     # Overview of all components
    │   ├── dependency_graph.md        # Mermaid dependency diagram
    │   ├── auth_service/
    │   │   ├── spec.md               # Component specification
    │   │   ├── interface.md          # API interface definition
    │   │   └── implementation.md     # Notes for Claude Code
    │   ├── api_gateway/
    │   │   ├── spec.md
    │   │   └── ...
    │   └── [other components]/
    │
    ├── planning/
    │   ├── sprint_plan.md             # Sprint breakdown (INVEST stories)
    │   ├── timeline.md                # Gantt-style timeline
    │   ├── milestones.md              # Key milestones & deliverables
    │   └── resource_plan.md           # Team & resource allocation
    │
    ├── diagrams/
    │   ├── architecture_c4.png        # C4 Context/Container diagram
    │   ├── component_diagram.png      # Component relationships
    │   ├── data_flow.png              # Data flow diagram
    │   ├── sequence_diagrams/         # Key sequence diagrams
    │   └── mockups/                   # UI mockups
    │
    └── data/                          # User-provided input files
        └── [uploaded files]
```

---

## 7. Testing Strategy

### Unit Tests (75+ test cases)

| Module | Test Count | Coverage |
|--------|------------|----------|
| `models.py` | 25 | All dataclasses, serialization |
| `utils.py` | 20 | Project scanning, detection |
| `core.py` | 20 | Setup, file handling |
| `api.py` | 10 | Progress stages, result building |

### Integration Tests (15+ test cases)

- End-to-end project generation
- Skill invocation tests
- Output folder structure validation
- Multi-file project handling

### Smoke Test Scenarios

1. **Basic Planning:** "Plan a simple REST API for a todo app"
2. **Full SaaS:** "Research and plan a B2B inventory management SaaS"
3. **Architecture Only:** "Design the architecture for a real-time chat system"
4. **Cost Analysis:** "Compare AWS vs GCP costs for a 10K user application"
5. **Sprint Planning:** "Break down the auth system into sprint tasks"

---

## 8. Timeline & Milestones

```
Week 1: Foundation & Models
├── Day 1-2: Package rename, pyproject.toml
├── Day 3-4: Data models (7 new dataclasses)
└── Day 5: API signature updates

Week 2: API, CLI & Skills (Part 1)
├── Day 6-7: CLI updates, progress stages
├── Day 8-9: Keep/modify existing skills
└── Day 10: Start new skills

Week 3: Skills (Part 2) & Instructions
├── Day 11-13: Complete 5 new skills
├── Day 14: CLAUDE.md rewrite
└── Day 15: PLANNER.md system instructions

Week 4: Testing & Launch
├── Day 16-17: Unit & integration tests
├── Day 18: Smoke tests & bug fixes
├── Day 19: Documentation updates
└── Day 20: v1.0.0 release
```

### Milestones

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| **M1: Foundation** | Day 5 | Package renamed, models defined |
| **M2: Core API** | Day 10 | `generate_project()` working |
| **M3: Skills Complete** | Day 15 | All 13 skills implemented |
| **M4: Beta** | Day 18 | All tests passing |
| **M5: Release** | Day 20 | v1.0.0 on PyPI |

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Perplexity API changes | Low | High | Abstract API calls, version pin |
| Skill complexity underestimated | Medium | Medium | Start with MVP skills, iterate |
| Breaking existing workflows | Medium | Low | This is a new repo, no backwards compat needed |
| Claude Agent SDK updates | Low | Medium | Pin version, test before upgrade |
| Research quality varies | Medium | Medium | Use plan-review skill for validation |

---

## 10. Success Criteria

### MVP (v1.0.0)

- [ ] `generate_project()` API works end-to-end
- [ ] All 13 skills implemented with SKILL.md
- [ ] Output structure matches specification
- [ ] 5 smoke test scenarios pass
- [ ] README and CHANGELOG updated
- [ ] Published to PyPI as `project-planner`

### Quality Gates

- [ ] 75+ unit tests passing
- [ ] No critical/high security vulnerabilities
- [ ] Documentation complete
- [ ] Example prompts available

### Future Enhancements (v1.1+)

- Jira/Linear export for sprint plans
- GitHub Actions workflow for component scaffolding
- Real-time cloud pricing API integration
- Multi-project dashboard
- Team collaboration features

---

## Appendix A: File Changes Summary

### Files to Create
- `project_planner/` (renamed directory)
- `skills/architecture-research/SKILL.md`
- `skills/building-blocks/SKILL.md`
- `skills/service-cost-analysis/SKILL.md`
- `skills/sprint-planning/SKILL.md`
- `skills/risk-assessment/SKILL.md`
- `.claude/PLANNER.md`
- `tests/` (test suite)
- `examples/` (example prompts)

### Files to Modify
- `pyproject.toml`
- `CLAUDE.md`
- `README.md`
- `CHANGELOG.md`
- `.claude-plugin/marketplace.json`
- All files in renamed `project_planner/`

### Files to Remove
- `scientific_writer/` (after rename)
- 12 scientific-writing specific skills
- `templates/CLAUDE.scientific-writer.md`

---

## Appendix B: Reference Documents

- `PROJECT_PLANNER_MIGRATION_PLAN.md` - Detailed code changes
- Industry standards: ADR, C4 Model, Arc42, INVEST criteria
- Original project: https://github.com/K-Dense-AI/claude-scientific-writer

---

*Document Version: 1.0*
*Created: 2025-01-06*
*Author: UltraThink Analysis*
