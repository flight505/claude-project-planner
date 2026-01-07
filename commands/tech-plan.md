---
description: Generate a technical project plan - architecture, building blocks, costs, risks, and sprint planning (no marketing)
---

# Technical Project Plan Command

When the user invokes `/tech-plan`, generate a **technical-focused project plan** covering architecture, implementation, and costs.

## Required Input

Before starting, gather from the user:
1. **Project name and description** - What are we building?
2. **Technical requirements** - Key features, scale, integrations?
3. **Technology preferences** - Any stack requirements or constraints?
4. **Timeline constraints** - Any deadlines?

## Output Structure

Create outputs in: `planning_outputs/<project_name>/`

```
planning_outputs/<project_name>/
├── 00_technical_summary.md           # High-level technical overview
├── 01_architecture/
│   ├── architecture_document.md      # From architecture-research skill
│   ├── building_blocks.md            # From building-blocks skill
│   └── diagrams/
├── 02_analysis/
│   ├── feasibility_analysis.md       # From feasibility-analysis skill
│   ├── risk_assessment.md            # From risk-assessment skill
│   └── service_cost_analysis.md      # From service-cost-analysis skill
├── 03_implementation/
│   ├── sprint_plan.md                # From sprint-planning skill
│   └── milestones.md
├── 04_review/
│   └── plan_review.md                # From plan-review skill
└── diagrams/
```

## Execution Phases

### Phase 1: Architecture & Technical Design
**Skills:** `architecture-research`, `building-blocks`, `research-lookup`

1. Research best practices and patterns for the problem domain
2. Design system architecture with components and interactions
3. Break down into buildable blocks with clear interfaces
4. Generate architecture diagrams

### Phase 2: Feasibility & Risk Analysis
**Skills:** `feasibility-analysis`, `risk-assessment`, `service-cost-analysis`

1. Assess technical feasibility
2. Identify technical risks and mitigation strategies
3. Calculate infrastructure and service costs

### Phase 3: Implementation Planning
**Skills:** `sprint-planning`

1. Create sprint-by-sprint development roadmap
2. Define milestones (MVP, beta, launch)
3. Generate timeline visualizations

### Phase 4: Review
**Skills:** `plan-review`

1. Review complete technical plan
2. Create technical summary document

## Completion Checklist

- [ ] Architecture document complete with diagrams
- [ ] Building blocks defined with interfaces
- [ ] Costs calculated with TCO breakdown
- [ ] Risks identified with mitigations
- [ ] Sprint plan with clear milestones
- [ ] Technical summary synthesizes all sections
