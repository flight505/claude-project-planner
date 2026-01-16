# Claude Project Planner Instructions

This project is a Claude Code plugin for software project planning.

## Version Management & Marketplace Sync

**⚠️ CRITICAL: When committing version changes to `.claude-plugin/plugin.json`:**

1. **Bump version** following semantic versioning (MAJOR.MINOR.PATCH)
2. **Commit & push** to trigger webhook: `git commit -m "chore: bump version to X.Y.Z" && git push`
3. **Verify webhook** fired (5 sec): `gh run list --repo flight505/claude-project-planner --limit 1`
   - Success: "✅ Marketplace notification sent successfully (HTTP 204)"
   - Failed: See `../../docs/WEBHOOK-TROUBLESHOOTING.md`
4. **Marketplace auto-syncs** within 30 seconds - no manual `marketplace.json` update needed

**Tip**: Use `../../scripts/bump-plugin-version.sh claude-project-planner X.Y.Z` to automate everything.

---

## Stack 
Here’s the stack for Claude Project Planner, in short:

•  Language & runtime: Python 3.10–3.12, packaged as a Python project with hatchling and a CLI entrypoint project-planner (via project_planner.cli:cli_main).
•  Core libraries:  
◦  claude-agent-sdk for orchestrating AI agents and workflows (btw The Claude Code SDK has been renamed to the Claude Agent SDK)
◦  requests, pyyaml, jinja2, python-dotenv for HTTP, config, templating, and env management  
◦  openai client used for OpenRouter-based research
•  AI providers (external services):  
◦  Anthropic (Claude) – main planning / text generation (ANTHROPIC_API_KEY)  
◦  OpenRouter (Perplexity, others) – fast research and some image gen (OPENROUTER_API_KEY)  
◦  Google Gemini – Deep Research, images, video (GEMINI_API_KEY)
•  Optional features:  
◦  Document/slide outputs via pillow, python-pptx  
◦  Async/performance via aiofiles, httpx
•  System-level tools (optional): Mermaid CLI for diagram rendering and LaTeX (TeX Live/MacTeX) for rich PDF generation.


## Quick Reference

See `.claude/PLANNER.md` for comprehensive system instructions.

## Commands

| Command | Description |
|---------|-------------|
| `/full-plan` | Complete project planning with all phases (market, architecture, costs, sprints, marketing) |
| `/tech-plan` | Technical-only planning (architecture, costs, risks, sprints - no marketing) |
| `/generate-report` | Compile planning outputs into professional report (PDF/DOCX/MD) with optional IEEE citations |
| `/project-planner:setup` | Interactive configuration for API keys and environment |

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
| **Marketing Campaign** | `marketing-campaign` | Social media strategy, content calendars, influencer outreach |
| **Market Research** | `market-research-reports` | Comprehensive market analysis |
| **Report Generation** | `report-generation` | Compile outputs to PDF/DOCX with IEEE citations, TOC, cover page |

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
    ├── marketing/        # Campaign plans, content calendars
    └── SUMMARY.md        # Executive summary
```

## Full Plan Phases

When using `/full-plan`, the following phases are executed in order:

1. **Phase 1: Market Research** - `research-lookup`, `competitive-analysis`, `market-research-reports`
2. **Phase 2: Architecture** - `architecture-research`, `building-blocks`
3. **Phase 3: Feasibility** - `feasibility-analysis`, `risk-assessment`, `service-cost-analysis`
4. **Phase 4: Implementation** - `sprint-planning`
5. **Phase 5: Go-to-Market** - `marketing-campaign`
6. **Phase 6: Review** - `plan-review`

## Core Principles

1. **Research before recommending** - Use `research-lookup` for every major decision
2. **Building blocks for Claude Code** - Create specifications that Claude Code can build
3. **Real data only** - No placeholder estimates or invented benchmarks
4. **Generate diagrams extensively** - Use `project-diagrams` for all architectures
5. **Complete tasks fully** - Never stop mid-task to ask permission

## Progress Tracking & Error Recovery (v1.4.0-alpha)

**New in v1.4.0-alpha:** Complete progress tracking and checkpoint system for long-running operations.

### Key Features

| Feature | Description | CLI Tool |
|---------|-------------|----------|
| **Resume Interrupted Research** | Continue from 15%, 30%, or 50% checkpoints | `scripts/resume-research.py` |
| **External Monitoring** | Track progress from separate terminal | `scripts/monitor-research-progress.py` |
| **Intelligent Retry** | Exponential backoff with circuit breaker | Automatic |
| **Graceful Degradation** | Deep Research → Perplexity fallback | Automatic |

### CLI Tools

**Monitor active research:**
```bash
# List all active operations
python scripts/monitor-research-progress.py <project_folder> --list

# Monitor specific operation with live updates
python scripts/monitor-research-progress.py <project_folder> <task_id> --follow
```

**Resume interrupted research:**
```bash
# List resumable tasks with time estimates
python scripts/resume-research.py <project_folder> <phase_num> --list

# Resume from checkpoint (saves up to 50 minutes)
python scripts/resume-research.py <project_folder> <phase_num> --task <task_name>
```

### Architecture

**3-Tier System:**
1. **Streaming Progress** (Perplexity ~30s) - Real-time callbacks
2. **Progress Files** (Deep Research ~60 min) - JSON tracking + external monitoring
3. **Phase Checkpoints** - Research task statuses at phase boundaries

**8 Core Patterns:**
- Pattern 1: Streaming progress wrapper (`streaming_research_wrapper.py`)
- Pattern 2: Progress file tracking (`research_progress_tracker.py`)
- Pattern 3: Error handling with retry (`research_error_handling.py`)
- Pattern 4: Research checkpoint manager (`research_checkpoint_manager.py`)
- Pattern 5: Resumable research executor (`resumable_research.py`)
- Pattern 6: Enhanced phase checkpoints (`checkpoint-manager.py`)
- Pattern 7: Resume command CLI (`resume-research.py`)
- Pattern 8: Monitoring script CLI (`monitor-research-progress.py`)

**See Also:**
- `docs/WORKFLOWS.md` - Complete workflow examples
- `scripts/enhanced_research_integration.py` - Python API integration
- `CHANGELOG.md` - Full v1.4.0-alpha details

## Development

**Before committing changes**, bump the version number in these files:
- `pyproject.toml` - Package version
- `.claude-plugin/plugin.json` - Plugin version
- `README.md` - Version badge

This triggers auto-update for users who have the plugin installed.

## Claude Code SDK / Claude Agents SDK documentation.

Here are all the Agent SDK links from the Claude documentation:
Agent SDK Documentation Links
Main Overview:

https://platform.claude.com/docs/en/agent-sdk/overview

Getting Started:

https://platform.claude.com/docs/en/agent-sdk/quickstart

Language Implementations:

https://platform.claude.com/docs/en/agent-sdk/typescript
https://platform.claude.com/docs/en/agent-sdk/typescript-v2-preview
https://platform.claude.com/docs/en/agent-sdk/python

Guides & Features:

https://platform.claude.com/docs/en/agent-sdk/migration-guide
https://platform.claude.com/docs/en/agent-sdk/streaming-vs-single-mode
https://platform.claude.com/docs/en/agent-sdk/permissions
https://platform.claude.com/docs/en/agent-sdk/user-input
https://platform.claude.com/docs/en/agent-sdk/hooks
https://platform.claude.com/docs/en/agent-sdk/sessions
https://platform.claude.com/docs/en/agent-sdk/file-checkpointing
https://platform.claude.com/docs/en/agent-sdk/structured-outputs
https://platform.claude.com/docs/en/agent-sdk/hosting

Related Resources:

https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
https://platform.claude.com/docs/en/build-with-claude/skills-guide

That's 18 Agent SDK-specific links plus 4 related agent skills and tools guides. All of these are from the Claude documentation platform.
