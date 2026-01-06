# Claude Project Planner Instructions

This project is a Claude Code plugin for software project planning.

## Quick Reference

See `.claude/PLANNER.md` for comprehensive system instructions.

## Key Capabilities

| Capability | Skill | Description |
|------------|-------|-------------|
| **Architecture Research** | `architecture-research` | Technology stack research, ADRs, C4 model |
| **Building Blocks** | `building-blocks` | Component specifications for Claude Code |
| **Sprint Planning** | `sprint-planning` | User stories, INVEST criteria, capacity |
| **Cost Analysis** | `service-cost-analysis` | Cloud pricing, ROI projections |
| **Risk Assessment** | `risk-assessment` | Risk registers, mitigation strategies |
| **Diagrams** | `project-diagrams` | C4, sequence, ERD, deployment diagrams |
| **Competitive Analysis** | `competitive-analysis` | Market positioning, competitor profiling |
| **Feasibility** | `feasibility-analysis` | Technical and market viability |
| **Plan Review** | `plan-review` | Project plan validation |
| **Research** | `research-lookup` | Real-time technology research |

## Output Structure

```
planning_outputs/
└── YYYYMMDD_HHMMSS_<project_name>/
    ├── specifications/   # Project & technical specs
    ├── research/         # Market & tech research
    ├── analysis/         # Feasibility, costs, risks
    ├── components/       # Building blocks (YAML)
    ├── planning/         # Sprint plans, timeline
    ├── diagrams/         # Architecture diagrams
    └── SUMMARY.md        # Executive summary
```

## Core Principles

1. **Research before recommending** - Use `research-lookup` for every major decision
2. **Building blocks for Claude Code** - Create specifications that Claude Code can build
3. **Real data only** - No placeholder estimates or invented benchmarks
4. **Generate diagrams extensively** - Use `project-diagrams` for all architectures
5. **Complete tasks fully** - Never stop mid-task to ask permission
