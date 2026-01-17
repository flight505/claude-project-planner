# Claude Project Planner

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.4.2-blue.svg)](https://github.com/flight505/claude-project-planner)

<p align="center">
  <img src="assets/hero.png" alt="Claude Project Planner - AI-powered project planning command center" width="100%">
</p>

**AI-powered project planning toolkit** that transforms ideas into comprehensive, buildable specifications. Generate complete project plans including architecture documents, sprint plans, cost analyses, and implementation roadmaps—all backed by real-time research.

**✨ New in v1.4.0:** Production-ready progress tracking & error recovery system! Monitor long-running Deep Research operations in real-time, resume interrupted research from checkpoints, and track progress with granular activity-based updates. Includes structured error handling with recovery suggestions, automatic cleanup, state machine validation, and comprehensive CLI tools.

---

## 🚀 Quick Start

### Installation

```bash
# Install as Claude Code plugin (recommended)
claude plugin install flight505/claude-project-planner

# Restart Claude Code when prompted
```

### Prerequisites

- Python 3.10-3.12
- `ANTHROPIC_API_KEY` (required)
- `OPENROUTER_API_KEY` (recommended, for research)
- `GEMINI_API_KEY` (optional, for Deep Research)

```bash
# Configure API keys
export ANTHROPIC_API_KEY='your_key'
export OPENROUTER_API_KEY='your_key'  # Recommended for research
```

### Usage

```bash
# Start comprehensive planning with interactive setup
/full-plan my-project

# You'll see 8 question groups covering ALL features:
# 1. AI Provider (Gemini vs Perplexity)
# 2. Research Depth (balanced/quick/comprehensive)
# 3. Parallelization (fast vs sequential)
# 4. Interactive Approval (pause after each phase)
# 5. Core Phases (Market Research, Architecture, Implementation)
# 6. Optional Phases (Feasibility, Go-to-Market, Review)
# 7. Quality Checks (multi-model validation, diagrams)
# 8. Output Formats (PDF, PowerPoint)
```

**That's it!** No flags to remember—discover all features through the interactive UI.

---

## ✨ What's New in v1.4.0-alpha

### 📊 Complete Progress Tracking & Error Recovery System

**Never lose Deep Research progress again!** v1.4.0-alpha introduces a comprehensive 3-tier progress tracking and checkpoint system:

**3-Tier Architecture:**

```
┌─────────────────────────────────────────────────────┐
│ Tier 1: Streaming Progress (Perplexity ~30s)       │
│ Real-time event callbacks with instant feedback    │
├─────────────────────────────────────────────────────┤
│ Tier 2: Progress Files (Deep Research ~60 min)     │
│ JSON progress tracking + external monitoring       │
├─────────────────────────────────────────────────────┤
│ Tier 3: Phase Checkpoints                          │
│ Research task statuses saved at phase boundaries   │
└─────────────────────────────────────────────────────┘
```

**Key Features:**

| Feature | Benefit | Time Saved |
|---------|---------|------------|
| **Resume Interrupted Research** | Continue from 15%, 30%, or 50% checkpoints | Up to 50 minutes |
| **External Monitoring** | Track progress from separate terminal | Real-time visibility |
| **Intelligent Retry** | Exponential backoff with circuit breaker | 80% fewer transient failures |
| **Graceful Degradation** | Deep Research → Perplexity fallback | No research failures |

**Dual-Terminal Workflow:**

```bash
# Terminal 1: Run planning
/full-plan my-saas-project

# Terminal 2: Monitor research (while it runs)
python scripts/monitor-research-progress.py planning_outputs/20260115_my-saas --follow

# See live progress:
# [14:23:45] 🔄 [████████████░░░░░] 30% | analyzing: Cross-referencing...
# [14:38:12] 🔄 [████████████████░░] 50% | synthesizing: Compiling results...
# [14:52:30] ✅ [████████████████████] 100% | Research complete!
```

**Resume Interrupted Research:**

```bash
# List resumable tasks with time estimates
python scripts/resume-research.py planning_outputs/20260115_my-saas 1 --list

# Output:
# RESUMABLE RESEARCH TASKS (Phase 1)
# 1. ✅ Resumable - competitive-analysis
#    Progress: 30%
#    Time invested: ~18 minutes
#    Time saved by resuming: ~18 minutes
#    Estimated time remaining: ~42 minutes

# Resume from checkpoint
python scripts/resume-research.py planning_outputs/20260115_my-saas 1 --task competitive-analysis
```

**8 Core Patterns Implemented:**
- Pattern 1: Streaming progress wrapper
- Pattern 2: Progress file tracking
- Pattern 3: Error handling with exponential backoff
- Pattern 4: Research checkpoint manager
- Pattern 5: Resumable research executor
- Pattern 6: Enhanced phase checkpoints
- Pattern 7: Resume command CLI
- Pattern 8: Monitoring script CLI

**Documentation:** See `docs/WORKFLOWS.md` for complete workflow examples and diagrams.

---

## ✨ What's New in v1.3.1

### 🎯 Interactive Approval Mode

Pause after each phase to review and approve before continuing:

```
✓ PHASE 2 COMPLETE: Architecture & Technical Design (35 min)

Key Decisions:
  • Architecture Pattern: Microservices
  • Tech Stack: Node.js, PostgreSQL, Redis
  • Deployment: Kubernetes on AWS EKS

Continue to next phase? [Continue | Revise | Pause]
```

**Choose:**
- **Continue** → Proceed to next phase
- **Revise** → Provide feedback and re-run with adjustments
- **Pause** → Save state and resume later

### 🔄 Iterative Refinement

Revise completed phases with intelligent dependency handling:

```bash
# Revise a completed phase
/refine-plan planning_outputs/20260112_my-project --phase 2 \
  --feedback "Use monolithic architecture instead of microservices"

# System automatically:
# 1. Backs up original outputs
# 2. Identifies dependent phases (3, 4, 6)
# 3. Asks how to handle dependencies
# 4. Re-runs with feedback incorporated
```

### 🎨 Comprehensive Setup UI

No more command-line flags! Interactive UI presents all features:

- **AI Provider Selection** - Gemini Deep Research vs Perplexity
- **Performance** - Enable parallelization for 14% time savings
- **Interactive Mode** - Approval gates after each phase
- **Phase Selection** - Skip marketing for internal tools
- **Quality Checks** - Multi-model validation, extra diagrams
- **Output Formats** - PDF reports, PowerPoint slides

<details>
<summary><b>📸 See Setup UI Example</b></summary>

```
Starting /full-plan...

┌─────────────────────────────────────────────────────┐
│ 1. AI Provider                                      │
│ ● Google Gemini Deep Research (Recommended)         │
│ ○ Perplexity via OpenRouter                         │
│ ○ Auto-detect from available keys                   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 3. Workflow ⭐ NEW                                  │
│ ● Yes - Interactive approval mode                   │
│   Pause after each phase for review                 │
│ ○ No - Fully autonomous                             │
└─────────────────────────────────────────────────────┘

Configuration Summary:
  AI Provider: GEMINI
  Parallelization: ENABLED
  Interactive Mode: ENABLED ⭐
  Phases: 1, 2, 3, 4, 6 (marketing skipped)
  Quality: Multi-model validation + diagrams
  Outputs: Markdown, YAML, PDF
```

</details>

---

## 🎯 Key Features

- **📋 Comprehensive Planning** - Market research, architecture, costs, risks, sprints, marketing
- **🧠 Deep Research** - Gemini 60-min comprehensive or Perplexity 30-sec fast research (v1.3.2)
- **🏗️ Building Blocks** - Decompose projects into Claude Code-buildable components
- **💰 Cost Analysis** - AWS/GCP/Azure pricing with ROI projections
- **📊 AI-Generated Diagrams** - C4 model, sequence, ERD, deployment diagrams
- **🔍 Research-Backed** - Real-time technology and market research with intelligent routing
- **🎯 Interactive Approval** - Review and revise after each phase (v1.3.1)
- **🔄 Iterative Refinement** - Revise any phase with dependency handling (v1.3.1)
- **📣 Go-to-Market** - Marketing campaigns, content calendars, influencer strategy

---

## 📚 Commands

| Command | Description |
|---------|-------------|
| `/full-plan` | Complete project planning (all 6 phases) with interactive setup |
| `/tech-plan` | Technical planning only (no marketing) |
| `/refine-plan` | Revise a completed phase with feedback ⭐ NEW |
| `/generate-report` | Compile outputs into PDF/DOCX with IEEE citations |
| `/project-planner:setup` | Configure API keys |

<details>
<summary><b>📖 See Usage Examples</b></summary>

### Full Planning

```bash
/full-plan my-saas-app

# Interactive setup will ask about:
# - AI provider preference
# - Parallelization (14% faster)
# - Interactive approval gates
# - Which phases to include
# - Quality checks to enable
# - Output formats needed

# Then executes 6 phases:
# Phase 1: Market Research → Approval gate
# Phase 2: Architecture → Approval gate
# Phase 3: Feasibility & Costs → Approval gate
# Phase 4: Implementation Planning → Approval gate
# Phase 5: Go-to-Market → Approval gate
# Phase 6: Review & Analysis
```

### Iterative Refinement

```bash
# After reviewing architecture, realize monolith is better
/refine-plan planning_outputs/20260112_143022_my-saas --phase 2 \
  --feedback "Use monolithic architecture. Microservices add unnecessary complexity for MVP."

# System responds:
# "Phase 2 revision will affect Phases 3, 4, 6. How to handle?"
# - Auto-rerun all (fastest, most consistent)
# - Review individually (more control)
# - Only revise Phase 2 (WARNING: inconsistencies)
```

### Technical Planning (Skip Marketing)

```bash
/tech-plan internal-tool

# Same as /full-plan but skips Phase 5 (marketing)
# Perfect for internal tools, APIs, or prototypes
```

</details>

---

## 🔧 Advanced Features

<details>
<summary><b>🤖 AI Provider Options</b></summary>

### Supported Providers

| Provider | Features | Requirements | Best For |
|----------|----------|--------------|----------|
| **Anthropic** | Core planning, text generation | `ANTHROPIC_API_KEY` (required) | Everything |
| **OpenRouter** | Research (Perplexity), Image Gen | `OPENROUTER_API_KEY` | Fast research |
| **Google Gemini** | Deep Research, Veo 3.1 videos | `GEMINI_API_KEY` + AI Pro ($19.99/mo) | Comprehensive research |

### Google Gemini Setup (Optional)

**Requirements:**
1. Google AI Pro subscription ($19.99/month)
   - Visit: https://one.google.com/intl/en/about/google-ai-plans/
2. Get API key: https://ai.google.dev/

**Features:**
- ✅ **Deep Research**: 60-minute comprehensive research queries
- ✅ **Veo 3.1**: 8-second videos with audio ($0.75/second)
- ✅ **Imagen 3**: High-quality image generation
- ✅ **1M Token Context**: Industry-leading context window

```bash
export GEMINI_API_KEY='your-key'
```

**Auto-Detection:**

Plugin automatically uses best provider for each task:
- **Research**: Gemini Deep Research → Perplexity
- **Text**: Gemini 2.0 Flash Thinking → Claude 3.5
- **Images**: Flux (OpenRouter) → Imagen 3 (Gemini)
- **Videos**: Veo 3.1 (Gemini only)

</details>

<details>
<summary><b>📁 Output Structure</b></summary>

### Directory Layout

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
├── 05_go_to_market/        # Optional
│   ├── marketing_campaign.md
│   ├── content_calendar.md
│   └── diagrams/
│
├── 06_review/
│   └── plan_review.md
│
└── .state/                 # Internal
    ├── backups/            # Original outputs before revision
    ├── revisions/          # Revision history
    └── phase*_context.md   # Phase context
```

### Revision Tracking

When using `/refine-plan`:
- Originals backed up to `.state/backups/`
- Revision history in `.state/revisions/`
- Checkpoint tracks revision numbers

</details>

<details>
<summary><b>🧱 Building Blocks Format</b></summary>

### YAML Specification

Building blocks are Claude Code-buildable components:

```yaml
building_blocks:
  - name: "User Authentication Service"
    id: "BB-001"
    type: "backend"
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

### Why Building Blocks?

1. **Claude Code Compatible** - Directly buildable specifications
2. **Clear Dependencies** - Explicit internal and external deps
3. **Testable** - Acceptance criteria included
4. **Estimatable** - Story points and hours
5. **Prioritized** - Sprint assignments

</details>

<details>
<summary><b>📅 Sprint Planning Format</b></summary>

### INVEST Criteria

Sprints follow INVEST principles (Independent, Negotiable, Valuable, Estimable, Small, Testable):

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

</details>

<details>
<summary><b>🎓 Available Skills</b></summary>

### 18 Specialized Skills

**Core Research:**
- `research-lookup` - Real-time tech/market research
- `competitive-analysis` - Market positioning
- `market-research-reports` - Comprehensive analysis

**Architecture & Design:**
- `architecture-research` - Stack research, ADRs, C4 model
- `building-blocks` - Component specifications
- `project-diagrams` - AI-generated diagrams

**Planning & Estimation:**
- `sprint-planning` - User stories, INVEST criteria
- `service-cost-analysis` - Cloud pricing, ROI
- `risk-assessment` - Risk registers, mitigation

**Quality & Review:**
- `feasibility-analysis` - Technical/market feasibility
- `plan-review` - Plan validation

**Go-to-Market:**
- `marketing-campaign` - Social media strategy, content calendars

**Utilities:**
- `generate-image` - AI image generation
- `markitdown` - Document conversion
- `document-skills/docx`, `pdf`, `pptx`, `xlsx` - Document processing
- `report-generation` - Compile outputs to PDF/DOCX

</details>

<details>
<summary><b>🐍 Python API</b></summary>

### Programmatic Access

```python
import asyncio
from project_planner import generate_project

async def main():
    async for update in generate_project(
        query=(
            "Plan a task management SaaS. "
            "Include authentication, team management, "
            "task CRUD, notifications, analytics. "
            "Target: 5,000 users year 1."
        ),
        output_dir="./planning_outputs",
        enable_interactive=True,  # v1.3.1
        enable_parallelization=True
    ):
        if update["type"] == "progress":
            print(f"[{update['stage']}] {update['message']}")
        elif update["type"] == "approval_required":
            # Handle approval gate
            decision = input("Continue? [y/n/r]: ")
            update["callback"](decision)
        else:
            print(f"✓ Complete: {update['files']['summary']}")

asyncio.run(main())
```

</details>

---

## 📖 Documentation

- **[Interactive Mode Guide](docs/INTERACTIVE_SETUP.md)** - Complete workflow for v1.3.1
- **[Parallelization Guide](docs/PARALLELIZATION_GUIDE.md)** - Performance optimization
- **[Refine Command](commands/refine-plan.md)** - Iterative refinement
- **[User Flow Diagrams](docs/USER_FLOW.md)** - Visual workflow
- **[Features Guide](docs/FEATURES.md)** - Comprehensive overview
- **[API Reference](docs/API.md)** - Python API
- **[Skills Overview](docs/SKILLS.md)** - All 18 skills
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing
- **[Changelog](CHANGELOG.md)** - Version history

---

## 🎬 Example Workflow

**Request:** "Plan a B2B SaaS inventory management system"

**With Interactive Mode (v1.3.1):**

1. **Setup UI** - Choose options (AI provider, parallelization, approval gates)
2. **Phase 1: Market Research** → Review → Approve/Revise/Pause
3. **Phase 2: Architecture** → Review → *User selects "Revise"*
   - Feedback: "Use PostgreSQL instead of MongoDB"
   - System re-runs Phase 2 with feedback
4. **Phase 3: Feasibility & Costs** → Review → Approve
5. **Phase 4: Implementation Planning** → Review → Approve
6. **Phase 5: Go-to-Market** → Review → Approve
7. **Phase 6: Review & Analysis** → Final summary
8. **Post-Plan Analysis** - Parallelization recommendations

**Output:**
```
planning_outputs/20260112_143022_b2b_inventory_saas/
├── SUMMARY.md (executive summary)
├── 01_market_research/ (competitive landscape)
├── 02_architecture/ (revised PostgreSQL design)
├── 03_feasibility/ (costs, risks, ROI)
├── 04_implementation/ (6 sprints, 18 building blocks)
├── 05_go_to_market/ (launch campaign)
├── 06_review/ (validation report)
└── .state/
    ├── backups/phase2_original/ (MongoDB design)
    └── revisions/phase2_revision_001.md
```

---

## 🔄 Version History

- **v1.3.1** (2026-01-12) - Interactive approval gates, `/refine-plan` command, comprehensive setup UI
- **v1.3.0** (2026-01-12) - Post-plan parallelization analysis
- **v1.2.0** (2026-01-11) - Interactive setup UI with file-based input
- **v1.1.0** (2026-01-10) - Google Gemini integration, provider abstraction
- **v1.0.18** (2026-01-09) - Enhanced dependency management
- **v1.0.6** - Go-to-market strategy and marketing campaigns
- **v1.0.0** - Initial release

[Full Changelog](CHANGELOG.md)

---

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/flight505/claude-project-planner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flight505/claude-project-planner/discussions)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📜 License

MIT - see [LICENSE](LICENSE)

---

## 🙏 Credits

Forked from [claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer) by K-Dense AI.
Transformed for software project planning use cases.

---

⭐ **If you find this useful, please star the repo!** It helps others discover the tool.
