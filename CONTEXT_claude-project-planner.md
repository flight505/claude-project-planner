# CONTEXT: Claude Project Planner - Ground Truth Documentation

**Plugin Version:** 1.3.1
**Repository:** https://github.com/flight505/claude-project-planner
**Origin:** Forked from [claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer) v2.10.0
**Last Updated:** 2026-01-13

---

## Executive Summary

Claude Project Planner is a comprehensive AI-powered project planning toolkit for Claude Code. It transforms ideas into buildable specifications through a 6-phase planning system that includes market research, architecture design, cost analysis, sprint planning, and go-to-market strategy. All recommendations are backed by real-time research via Perplexity Sonar and Google Gemini Deep Research.

**Core Value Proposition:**
- Research-backed planning (no placeholder recommendations)
- Building blocks compatible with Claude Code
- AI-generated diagrams (C4, sequence, ERD, deployment)
- Interactive approval gates with iterative refinement (v1.3.1)
- Comprehensive output formats (Markdown, YAML, PDF, DOCX, PowerPoint)

---

## System Architecture

### 6-Phase Planning System

The plugin orchestrates a comprehensive planning workflow through six sequential phases:

```
Phase 1: Market Research
  ├─ research-lookup (Perplexity/Gemini)
  ├─ competitive-analysis
  └─ market-research-reports
         ↓
Phase 2: Architecture & Technical Design
  ├─ architecture-research (ADRs, C4 model)
  └─ building-blocks (YAML specs for Claude Code)
         ↓
Phase 3: Feasibility & Cost Analysis
  ├─ feasibility-analysis (technical/market viability)
  ├─ risk-assessment (risk registers, mitigation)
  └─ service-cost-analysis (AWS/GCP/Azure pricing)
         ↓
Phase 4: Implementation Planning
  └─ sprint-planning (INVEST criteria, user stories)
         ↓
Phase 5: Go-to-Market (Optional)
  └─ marketing-campaign (social media, content calendars)
         ↓
Phase 6: Review & Analysis
  └─ plan-review (validation, final summary)
```

**Key Design Patterns:**
- **Sequential phase execution** - Each phase builds on prior context
- **Context propagation** - `.context/phaseN_input.md` and `phaseN_output.md` files
- **Checkpoint/resume** - `.checkpoint.json` saves state after each phase
- **Revision tracking** - `.state/backups/` and `.state/revisions/` preserve history

### Parallelization Architecture (v1.0.18+)

Within each phase, independent tasks can run in parallel:

**Phase 1 Parallelization:**
```
research-lookup ──┐
                  ├──> market-research-reports ──> diagrams
competitive-analysis ─┘
```
- ~33% time savings in Phase 1

**Phase 3 Parallelization (Highest Benefit):**
```
building-blocks ──┬──> feasibility-analysis ──┐
                  ├──> risk-assessment ────────┼──> diagrams
                  └──> service-cost-analysis ──┘
```
- ~60% time savings in Phase 3
- **Total estimated savings: 14%** (195 min → 167 min)

**Implementation:**
- `scripts/parallel-orchestrator.py` - Manages parallel task execution
- Error isolation (failed tasks don't cascade)
- Context sharing via `.context/` directory

### Interactive Approval System (v1.3.1)

**Approval Gate Workflow:**
```
Phase N completes
       ↓
System presents:
  • Phase summary
  • Key decisions made
  • Time taken
  • Next phase preview
       ↓
User chooses:
  ├─ [Continue] → Proceed to next phase
  ├─ [Revise] → Provide feedback, re-run with adjustments
  └─ [Pause] → Save checkpoint, resume later
```

**Revision Handling:**
```
User selects "Revise" for Phase 2
       ↓
System identifies dependent phases: [3, 4, 6]
       ↓
User chooses dependency handling:
  ├─ Auto-rerun all (recommended)
  ├─ Review individually
  └─ Only revise Phase 2 (WARNING: inconsistencies)
       ↓
System backs up originals → .state/backups/
       ↓
Re-runs Phase 2 with feedback incorporated
       ↓
Updates dependent phases if selected
```

### AI Provider Abstraction

**Multi-Provider Support:**

| Provider | Capabilities | Requirements | Use Cases |
|----------|-------------|--------------|-----------|
| **Anthropic** | Core planning, text generation | `ANTHROPIC_API_KEY` (required) | All phases |
| **OpenRouter** | Research (Perplexity), Image Gen | `OPENROUTER_API_KEY` | Fast research, Flux images |
| **Google Gemini** | Deep Research, Veo 3.1 videos | `GEMINI_API_KEY` + AI Pro ($19.99/mo) | Comprehensive research |

**Auto-Detection Logic:**
```python
# Research task routing
if GEMINI_API_KEY and user_selected_gemini:
    use_deep_research()  # 60-min research queries
elif OPENROUTER_API_KEY:
    use_perplexity()     # Fast, real-time research
else:
    fallback_to_claude()

# Image generation routing
if OPENROUTER_API_KEY:
    use_flux()           # High-quality via OpenRouter
elif GEMINI_API_KEY:
    use_imagen3()        # Google's image model
else:
    skip_images()
```

---

## Core Components

### Building Blocks System

**Purpose:** Decompose projects into discrete, Claude Code-buildable components.

**YAML Specification Format:**
```yaml
building_blocks:
  - name: "User Authentication Service"
    id: "BB-001"
    type: "backend"  # frontend, backend, infrastructure, integration, shared
    description: "JWT-based auth with OAuth2"

    responsibilities:
      - "User registration with email verification"
      - "Login/logout with JWT tokens"
      - "OAuth2 integration (Google, GitHub)"

    dependencies:
      internal:
        - block_id: "BB-010"
          interface: "Database Service"
      external:
        - name: "PostgreSQL"
          version: ">=14.0"

    interfaces:
      api_endpoints:
        - method: "POST"
          path: "/api/v1/auth/register"
        - method: "POST"
          path: "/api/v1/auth/login"
      events_published:
        - "user.registered"
        - "user.logged_in"

    complexity: "M"  # S, M, L, XL
    estimated_hours: 24
    story_points: 5

    test_criteria:
      - "User can register with valid email"
      - "Invalid credentials return 401"
      - "JWT tokens properly scoped"

    priority: "critical"
    sprint_assignment: "Sprint 1"
```

**Why Building Blocks?**
1. **Claude Code Compatible** - Directly buildable specifications
2. **Clear Dependencies** - Explicit internal and external deps
3. **Testable** - Acceptance criteria included
4. **Estimatable** - Story points and hours
5. **Prioritized** - Sprint assignments

### Sprint Planning System

**INVEST Criteria Enforcement:**
- **I**ndependent - Stories can be developed independently
- **N**egotiable - Details can be adjusted during sprint
- **V**aluable - Delivers user value
- **E**stimable - Team can estimate effort
- **S**mall - Fits within a sprint
- **T**estable - Clear acceptance criteria

**Sprint YAML Format:**
```yaml
sprints:
  - sprint_number: 1
    name: "Foundation Sprint"
    duration_weeks: 2

    goals:
      - "Set up development infrastructure"
      - "Implement core authentication"

    capacity:
      team_size: 3
      available_points: 30
      committed_points: 28

    stories:
      - id: "US-001"
        title: "User Registration"
        description: "As a user, I can register with email and password"
        acceptance_criteria:
          - "Email validation works"
          - "Password meets strength requirements"
          - "Confirmation email sent"
        story_points: 5
        building_block: "BB-001"

    risks:
      - "OAuth integration may take longer"
      - mitigation: "Spike task in previous sprint"
```

### Research-First Approach

**Zero Tolerance Policy:**
- ❌ NO placeholder recommendations ("use a popular framework")
- ❌ NO invented statistics or market data
- ✅ Every decision backed by real research
- ✅ 3-5 sources per major technical decision

**Research Workflow:**
```
Technology Decision Required
       ↓
1. research-lookup (Perplexity/Gemini)
   └─ Find official docs, benchmarks, case studies
       ↓
2. Verify with 2+ sources
   └─ Cross-reference documentation
       ↓
3. Document trade-offs with evidence
   └─ Real-world benchmarks, pricing, limitations
       ↓
4. Save citations to .citations.json
   └─ IEEE-formatted references for reports
```

**Citation Storage:**
- Research skills save to `.citations.json` sidecar files
- `/generate-report` compiles citations into IEEE reference list
- Enables PDF/DOCX reports with proper academic citations

### Diagram Generation System

**Mandatory Diagrams:**
1. **System Architecture** - C4 model, component overview
2. **Data Model** - ERD, entity relationships
3. **Deployment Architecture** - Infrastructure layout

**Additional Diagrams:**
- Sequence diagrams for key workflows
- Component interaction diagrams
- Sprint timeline/Gantt charts
- Cost breakdown charts
- Risk heat maps

**Implementation:**
- `project-diagrams` skill - AI-generated diagrams
- Mermaid → PNG rendering with fallbacks:
  1. Local mmdc (best quality)
  2. Kroki.io API (free online)
  3. Nano Banana AI (AI-generated from description)
  4. Keep markdown (GitHub/GitLab compatible)

---

## File Structure & Organization

### Output Directory Layout

```
planning_outputs/YYYYMMDD_HHMMSS_<project>/
├── SUMMARY.md              # Executive summary
├── progress.md             # Real-time progress log
├── .checkpoint.json        # Resume state
│
├── 01_market_research/
│   ├── research_data.md
│   ├── competitive_analysis.md
│   ├── market_overview.md
│   └── diagrams/
│
├── 02_architecture/
│   ├── architecture_document.md
│   ├── building_blocks.yaml  # Claude Code specs
│   └── diagrams/
│
├── 03_feasibility/
│   ├── feasibility_analysis.md
│   ├── risk_assessment.md
│   ├── service_cost_analysis.md
│   └── diagrams/
│
├── 04_implementation/
│   ├── sprint_plan.md
│   └── diagrams/
│
├── 05_go_to_market/        # Optional (skip with /tech-plan)
│   ├── marketing_campaign.md
│   ├── content_calendar.md
│   └── diagrams/
│
├── 06_review/
│   └── plan_review.md
│
└── .state/                 # Internal state management
    ├── backups/            # Original outputs before revision
    │   └── phase2_original/
    ├── revisions/          # Revision history
    │   └── phase2_revision_001.md
    └── phase*_context.md   # Phase context for propagation
```

### Plugin File Structure

```
claude-project-planner/
├── .claude-plugin/
│   ├── plugin.json         # Plugin manifest
│   ├── marketplace.json    # Marketplace entry
│   └── hooks/
│       └── SessionStart.sh # Dependency checks
│
├── commands/               # Slash commands
│   ├── full-plan.md        # Complete 6-phase planning
│   ├── tech-plan.md        # Technical-only (no marketing)
│   ├── refine-plan.md      # Iterative refinement (v1.3.1)
│   ├── resume-plan.md      # Resume from checkpoint
│   ├── generate-report.md  # PDF/DOCX compilation
│   └── setup.md            # Interactive API key config
│
├── agents/
│   └── architecture-validator.md  # Multi-model validation
│
├── project_planner/        # Python package
│   ├── .claude/
│   │   └── skills/         # 18 specialized skills
│   │       ├── research-lookup/
│   │       ├── architecture-research/
│   │       ├── building-blocks/
│   │       ├── sprint-planning/
│   │       ├── service-cost-analysis/
│   │       ├── risk-assessment/
│   │       ├── feasibility-analysis/
│   │       ├── competitive-analysis/
│   │       ├── market-research-reports/
│   │       ├── plan-review/
│   │       ├── marketing-campaign/
│   │       ├── project-diagrams/
│   │       ├── generate-image/
│   │       ├── markitdown/
│   │       ├── document-skills/  # docx, pdf, pptx, xlsx
│   │       └── report-generation/
│   └── scripts/            # Utilities
│       ├── parallel-orchestrator.py
│       ├── checkpoint-manager.py
│       ├── progress-tracker.py
│       ├── analyze-parallelization.py
│       └── multi-model-validator.py
│
├── docs/                   # Detailed reference documentation
│   ├── FEATURES.md
│   ├── SKILLS.md
│   ├── API.md
│   ├── PARALLELIZATION_GUIDE.md
│   ├── INTERACTIVE_SETUP.md
│   ├── USER_FLOW.md
│   ├── TROUBLESHOOTING.md
│   ├── DEVELOPMENT.md
│   └── DEPENDENCIES.md
│
├── templates/
│   └── plan-input-template.md
│
├── CLAUDE.md               # Developer instructions (this file)
├── README.md               # Public-facing documentation
├── CHANGELOG.md            # Version history
├── pyproject.toml          # Python dependencies
└── requirements.txt        # Minimal dependencies
```

---

## Command Reference

### /full-plan - Comprehensive Planning

**Purpose:** Complete 6-phase project planning with all features.

**Usage:**
```bash
/full-plan my-project-name
```

**Interactive Setup Flow (v1.3.1):**
1. **AI Provider** - Gemini vs Perplexity vs Auto-detect
2. **Parallelization** - Enable for 14% time savings
3. **Interactive Approval** - Pause after each phase (NEW)
4. **Phase Selection** - Choose which phases to run (NEW)
5. **Quality Checks** - Multi-model validation, extra diagrams (NEW)
6. **Output Formats** - PDF, PowerPoint, Markdown (NEW)

**Execution Flow:**
```
Setup UI → Phase 1 → [Approval Gate] → Phase 2 → [Approval Gate] → ... → Phase 6 → Final Summary
```

**Options at Approval Gates:**
- **Continue** - Proceed to next phase
- **Revise** - Provide feedback, re-run with adjustments
- **Pause** - Save checkpoint, resume later with `/resume-plan`

### /tech-plan - Technical Planning Only

**Purpose:** Skip marketing phases for internal tools, APIs, or prototypes.

**Phases Executed:**
1. Market Research (optional, can be skipped)
2. Architecture & Technical Design
3. Feasibility & Cost Analysis
4. Implementation Planning
5. ~~Go-to-Market~~ (SKIPPED)
6. Review & Analysis

### /refine-plan - Iterative Refinement (v1.3.1)

**Purpose:** Revise completed phases with intelligent dependency handling.

**Usage:**
```bash
/refine-plan planning_outputs/20260112_my-project --phase 2 \
  --feedback "Use monolithic architecture instead of microservices"
```

**Workflow:**
```
1. User selects phase to revise
2. System identifies dependent phases (e.g., 3, 4, 6)
3. User chooses dependency handling:
   - Auto-rerun all (recommended)
   - Review individually
   - Only revise Phase 2 (WARNING: inconsistencies)
4. System backs up originals → .state/backups/
5. Re-runs phase with feedback incorporated
6. Updates dependent phases if selected
```

### /generate-report - Professional Report Compilation

**Purpose:** Compile planning outputs into professional reports (PDF/DOCX/MD).

**Features:**
- Interactive section selection (multiSelect)
- IEEE-style citations with numbered references
- AI-generated cover images and diagrams
- Table of contents
- Custom templates

**Output Formats:**
- **PDF** - Via Pandoc/LaTeX (requires Pandoc + TeX)
- **DOCX** - Microsoft Word compatible
- **Markdown** - GitHub/GitLab compatible

**Citation Flow:**
```
research-lookup saves citations
       ↓
.citations.json sidecar files
       ↓
compile_report.py aggregates
       ↓
IEEE reference list in report
       ↓
PDF/DOCX with [1], [2], [3] citations
```

### /resume-plan - Resume from Checkpoint

**Purpose:** Continue interrupted planning sessions.

**Usage:**
```bash
/resume-plan planning_outputs/20260112_my-project
```

**Features:**
- Lists available checkpoints
- Restores context from last completed phase
- Continues from where it stopped
- Option to clear checkpoint and start fresh

---

## Development Workflow

### Version Management

**Critical Files to Update When Releasing:**
1. `pyproject.toml` - Package version
2. `.claude-plugin/plugin.json` - Plugin version
3. `README.md` - Version badge

**Triggering Auto-Update:**
- Version bump in `.claude-plugin/plugin.json` triggers webhook
- Webhook sends `repository_dispatch` to marketplace repo
- Marketplace auto-updates within ~30 seconds
- Users receive update notification

### Testing Checklist

**Before Committing:**
- [ ] Test all 6 phases execute successfully
- [ ] Verify building blocks YAML is valid
- [ ] Check diagrams generate correctly
- [ ] Validate research citations save properly
- [ ] Test approval gates and revision flow (v1.3.1)
- [ ] Confirm checkpoint/resume works
- [ ] Test parallelization flag

**Plugin Testing:**
```bash
# Local testing
cd ../
mkdir test-marketplace
cd test-marketplace
echo '{"plugins": [{"name": "claude-project-planner", "source": "../claude-project-planner"}]}' > .claude-plugin/marketplace.json
claude plugin install claude-project-planner
```

### Adding New Skills

**Skill Directory Structure:**
```
project_planner/.claude/skills/new-skill/
├── SKILL.md            # Skill definition + system prompt
├── scripts/
│   └── main.py         # Implementation
├── references/
│   └── best_practices.md
└── templates/
    └── output_template.md
```

**Register in plugin.json:**
```json
{
  "skills": [
    "./project_planner/.claude/skills/new-skill"
  ]
}
```

---

## Version History & Evolution

### Key Milestones

**v1.3.1 (2026-01-12) - Interactive Approval & Refinement**
- Added interactive approval gates after each phase
- `/refine-plan` command for iterative refinement
- Comprehensive setup UI (6 question groups)
- Revision tracking with dependency handling

**v1.3.0 (2026-01-12) - Post-Plan Analysis**
- Post-plan parallelization analysis
- Time savings recommendations
- Re-execution with `--parallel` flag

**v1.2.0 (2026-01-11) - Interactive Setup**
- Interactive setup UI with file-based input
- Google Gemini integration
- Provider abstraction layer

**v1.0.18 (2025-01-10) - Parallelization**
- Smart parallelization within phases
- `--parallel` flag for `/full-plan`
- Context sharing via `.context/` directory
- ~14% time savings (195 min → 167 min)

**v1.0.17 (2025-01-10) - Quality Gates**
- PostToolUse validation hook
- Live progress dashboard
- Checkpoint/resume system
- Multi-model architecture validation

**v1.0.13 (2025-01-09) - Report Generation**
- `/generate-report` command
- IEEE citation formatting
- PDF/DOCX/Markdown output
- Citation storage in research skills

**v1.0.7 (2025-01-07) - Orchestration Commands**
- `/full-plan` master orchestrator
- `/tech-plan` technical-focused planning
- 6-phase planning system established

**v1.0.6 (2025-01-07) - Marketing Campaign**
- Go-to-market planning
- Social media strategy
- Content calendars
- Influencer outreach

**v1.0.0 (2025-01-07) - Initial Release**
- Forked from claude-scientific-writer v2.10.0
- Complete rebranding for software project planning
- Core skills: architecture, building blocks, sprints, costs, risks

### Transformation from Scientific Writer

**Key Changes:**
- Scientific writing → Software architecture research
- Paper generation → Project specification generation
- Literature review → Technology & market research
- Citations → Building block specifications
- LaTeX output → Markdown & YAML output

**Retained Concepts:**
- Research-first approach
- Multi-pass document creation
- Quality validation hooks
- Comprehensive documentation

---

## Critical Implementation Details

### Context Propagation System

**How Context Flows Between Phases:**
```
Phase 1 completes
       ↓
Extract key findings → .context/phase1_output.md
       ↓
Phase 2 receives:
  • .context/phase1_output.md (prior phase)
  • .context/phase2_input.md (aggregated from all prior)
       ↓
Phase 2 completes
       ↓
Extract key findings → .context/phase2_output.md
       ↓
Phase 3 receives:
  • .context/phase2_output.md (prior phase)
  • .context/phase3_input.md (aggregated from 1+2)
```

**Context File Format:**
```markdown
# Phase N Input Context

## From Phase 1: Market Research
- Key finding 1
- Key finding 2

## From Phase 2: Architecture
- Technology stack: Node.js, PostgreSQL, Redis
- Architecture pattern: Microservices
- Deployment: Kubernetes on AWS EKS

## Key Decisions
- Database: PostgreSQL (based on Phase 1 research)
- Authentication: JWT with OAuth2
```

### Checkpoint System

**Checkpoint JSON Structure:**
```json
{
  "project_name": "b2b_inventory_saas",
  "created_at": "2026-01-12T14:30:22Z",
  "last_phase": 2,
  "completed_phases": [1, 2],
  "revision_number": 1,
  "key_decisions": {
    "architecture_pattern": "microservices",
    "tech_stack": ["Node.js", "PostgreSQL", "Redis"],
    "deployment": "Kubernetes on AWS EKS"
  },
  "context_summaries": {
    "phase_1": "Market analysis identified 5 competitors...",
    "phase_2": "Architecture designed with 8 microservices..."
  },
  "output_files": {
    "phase_1": ["research_data.md", "competitive_analysis.md"],
    "phase_2": ["architecture_document.md", "building_blocks.yaml"]
  }
}
```

### Quality Validation Hooks

**PostToolUse Hook Checks:**
1. **Placeholder Detection** - Scans for [TODO], [TBD], Lorem ipsum
2. **Citation Validation** - Research files must have citations
3. **Building Blocks Validation** - YAML required fields present
4. **Cost Estimate Ranges** - Costs in reasonable ranges
5. **Output Length** - Warns on unusually short outputs

**Non-Blocking Warnings:**
- Hooks provide informational warnings only
- Planning continues even with validation warnings
- Allows flexibility while maintaining quality awareness

---

## API & Programmatic Usage

### Python API

**Basic Usage:**
```python
import asyncio
from project_planner import generate_project

async def main():
    async for update in generate_project(
        query="Plan a task management SaaS with authentication, teams, tasks, notifications",
        output_dir="./planning_outputs",
        enable_interactive=True,
        enable_parallelization=True
    ):
        if update["type"] == "progress":
            print(f"[{update['stage']}] {update['message']}")
        elif update["type"] == "approval_required":
            decision = input("Continue? [y/n/r]: ")
            update["callback"](decision)
        else:
            print(f"✓ Complete: {update['files']['summary']}")

asyncio.run(main())
```

**Update Types:**
- `progress` - Real-time progress updates
- `approval_required` - Interactive approval gate (v1.3.1)
- `phase_complete` - Phase completion notification
- `final_result` - Final summary with all outputs

### Environment Variables

**Required:**
- `ANTHROPIC_API_KEY` - Core planning and text generation

**Optional:**
- `OPENROUTER_API_KEY` - Perplexity research, Flux image generation
- `GEMINI_API_KEY` - Google Gemini Deep Research (requires AI Pro subscription)

**Auto-Detection:**
- Plugin automatically uses best available provider for each task
- Graceful fallback if optional keys missing

---

## Best Practices & Patterns

### When to Use Which Command

| Scenario | Command | Rationale |
|----------|---------|-----------|
| New product/startup | `/full-plan` | Need market validation + go-to-market |
| Internal tool/API | `/tech-plan` | Marketing not needed |
| Quick prototype | `/tech-plan --skip-marketing` | Focus on architecture only |
| Revise decision | `/refine-plan --phase 2` | Iterate on specific phase |
| Resume work | `/resume-plan` | Continue from checkpoint |
| Create presentation | `/generate-report` | Compile outputs to PDF/DOCX |

### Research Strategy

**For Technology Decisions:**
1. Use `research-lookup` BEFORE recommending any technology
2. Find official documentation + 2-3 real-world case studies
3. Document trade-offs with evidence
4. Verify current pricing for cost analysis

**For Market Research:**
1. Use Gemini Deep Research for comprehensive analysis (if available)
2. Fallback to Perplexity for fast research
3. Cross-check competitor claims with multiple sources
4. Save citations for report generation

### Building Block Design

**Good Building Block:**
```yaml
- name: "User Authentication Service"
  responsibilities:
    - "User registration with email verification"
    - "JWT token generation and validation"
  dependencies:
    internal: ["BB-010: Database Service"]
    external: ["PostgreSQL >=14.0"]
  interfaces:
    api_endpoints: ["/auth/register", "/auth/login"]
  test_criteria:
    - "User can register with valid email"
```

**Anti-Patterns:**
```yaml
# ❌ Too vague
- name: "Authentication"
  responsibilities: ["Handle auth"]

# ❌ Too large (should be split)
- name: "Entire Backend"
  responsibilities: ["Everything backend-related"]

# ❌ Missing dependencies
- name: "Payment Service"
  dependencies: []  # Should list Stripe API, Database, etc.
```

---

## Troubleshooting

### Common Issues

**1. Research Lookup Fails**
- **Cause:** Missing `OPENROUTER_API_KEY` or `GEMINI_API_KEY`
- **Solution:** Run `/project-planner:setup` to configure API keys

**2. Diagrams Not Generating**
- **Cause:** mmdc (Mermaid CLI) not installed
- **Solution:** Install via `npm install -g @mermaid-js/mermaid-cli` or use fallback

**3. PDF Generation Fails**
- **Cause:** Pandoc or LaTeX not installed
- **Solution:** Install Pandoc + BasicTeX or use DOCX output instead

**4. Approval Gates Not Appearing**
- **Cause:** `enable_interactive=False` in API or setup UI
- **Solution:** Select "Interactive approval mode" in setup UI

**5. Checkpoint Not Saving**
- **Cause:** Phase completed but checkpoint didn't save
- **Solution:** Check `.checkpoint.json` permissions, re-run phase

### Debug Mode

**Enable Verbose Logging:**
```bash
# Set environment variable
export CLAUDE_DEBUG=1

# Run command
/full-plan my-project
```

**Logs Location:**
```
planning_outputs/YYYYMMDD_HHMMSS_<project>/
├── progress.md       # Real-time progress
└── .state/
    └── debug.log     # Detailed debug logs
```

---

## Future Roadmap Considerations

**Potential Enhancements:**
- **Multi-project comparison** - Compare architectures across projects
- **Template library** - Pre-built templates for common project types
- **Cost tracking** - Track actual vs estimated costs
- **Integration with PM tools** - Export to Jira, Linear, GitHub Projects
- **Automated testing** - Generate test plans from building blocks
- **Deployment automation** - Claude Code integration for direct building

**Community Requests:**
- GraphQL schema generation from building blocks
- Terraform/IaC generation for infrastructure
- OpenAPI spec generation from API designs
- Database migration scripts from data models

---

## References

**External Dependencies:**
- Perplexity Sonar API - Real-time research
- Google Gemini API - Deep Research, image/video generation
- OpenRouter API - Multi-model access
- Pandoc - Document conversion
- Mermaid CLI - Diagram rendering

**Related Documentation:**
- [Full Features Guide](docs/FEATURES.md)
- [All Skills Reference](docs/SKILLS.md)
- [API Documentation](docs/API.md)
- [Parallelization Guide](docs/PARALLELIZATION_GUIDE.md)
- [Interactive Setup Guide](docs/INTERACTIVE_SETUP.md)
- [User Flow Diagrams](docs/USER_FLOW.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Development Guide](docs/DEVELOPMENT.md)

---

**Maintained by:** Jesper Vang (@flight505)
**License:** MIT
**Community:** [GitHub Discussions](https://github.com/flight505/claude-project-planner/discussions)
