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

## Progress Tracking

Create `planning_outputs/<project_name>/progress.md` and update it after each phase:

```markdown
# Project Plan Progress

## Project: [Name]
## Started: [Timestamp]

### Phase Status
- [ ] Phase 1: Market Research
- [ ] Phase 2: Architecture
- [ ] Phase 3: Feasibility
- [ ] Phase 4: Implementation
- [ ] Phase 5: Go-to-Market
- [ ] Phase 6: Review

### Activity Log
[Timestamp entries here]
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