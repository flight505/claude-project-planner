# Claude Project Planner

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**An AI-powered project planning toolkit** that combines deep research with comprehensive software architecture design. Generate complete project specifications, architecture documents, sprint plans, building blocks, cost analyses, and implementation roadmaps—all backed by real-time research and verified data.

Project Planner breaks down complex software projects into Claude Code-buildable components, enabling incremental delivery with clear specifications and acceptance criteria.

## Key Features

### 📋 Project Planning
- **Building Blocks** - Decompose projects into discrete, buildable components
- **Sprint Planning** - User stories with INVEST criteria and capacity management
- **Architecture Design** - C4 model diagrams, ADRs, technology research
- **Implementation Roadmaps** - Milestones, dependencies, critical path

### 💰 Cost & Risk Analysis
- **Service Cost Estimation** - AWS, GCP, Azure pricing with ROI projections
- **Risk Assessment** - Risk registers with scoring and mitigation strategies
- **Feasibility Analysis** - Technical, resource, and market viability

### 🔍 Research-Backed
- **Technology Research** - Stack comparisons with real benchmarks
- **Competitive Analysis** - Market positioning and differentiation
- **AI-Powered Diagrams** - C4, sequence, ERD, deployment diagrams via Nano Banana Pro

## Quick Start

### Prerequisites
- Python 3.10-3.12
- `ANTHROPIC_API_KEY` (required)
- `OPENROUTER_API_KEY` (optional, for research-lookup and diagrams)

### Installation

#### Option 1: Claude Code Plugin (Recommended) ⭐

```bash
# Add the plugin marketplace
/plugin marketplace add https://github.com/flight505/claude-project-planner

# Install the plugin
/plugin install claude-project-planner

# Restart Claude Code when prompted
```

#### Option 2: Install from PyPI

```bash
pip install project-planner
```

#### Option 3: Install from source

```bash
git clone https://github.com/flight505/claude-project-planner.git
cd claude-project-planner
uv sync
```

### Configure API Keys

```bash
# .env file (recommended)
echo "ANTHROPIC_API_KEY=your_key" > .env
echo "OPENROUTER_API_KEY=your_openrouter_key" >> .env

# or export in your shell
export ANTHROPIC_API_KEY='your_key'
```

## Usage

### Plugin Usage (Recommended)

After installing the plugin, simply ask Claude:

```bash
# Full project planning
> Plan a B2B SaaS inventory management system with multi-tenant architecture,
  PostgreSQL database, React frontend, and deployment on AWS.

# Architecture research
> Research the best technology stack for a real-time collaboration app.
  Compare WebSockets vs SSE vs polling for our use case.

# Building blocks specification
> Break down an e-commerce platform into buildable components.
  Include user authentication, product catalog, cart, checkout, and admin dashboard.

# Sprint planning
> Create a sprint plan for the authentication service.
  Include user registration, login, OAuth, and password reset features.

# Cost analysis
> Estimate monthly infrastructure costs for a SaaS app with 10,000 users.
  Consider compute, database, storage, and third-party services.

# Risk assessment
> Identify technical and business risks for migrating from monolith to microservices.
  Include mitigation strategies and contingency plans.
```

### CLI Usage

```bash
# If installed via pip
project-planner

# If installed from source with uv
uv run project-planner
```

### Python API

```python
import asyncio
from project_planner import generate_project

async def main():
    async for update in generate_project(
        query=(
            "Plan a task management SaaS application. "
            "Include user authentication, team management, "
            "task CRUD operations, notifications, and analytics dashboard. "
            "Target: 5,000 users in year 1, growing to 50,000 by year 3."
        ),
        output_dir="./planning_outputs"
    ):
        if update["type"] == "progress":
            print(f"[{update['stage']}] {update['message']}")
        else:
            print(f"✓ Plan complete: {update['files']['summary']}")

asyncio.run(main())
```

## Available Skills

When installed as a plugin, you get access to 14 specialized skills:

### Core Research
| Skill | Description |
|-------|-------------|
| `research-lookup` | Real-time technology and market research via Perplexity |
| `competitive-analysis` | Market positioning, competitor profiling, feature comparison |

### Architecture & Design
| Skill | Description |
|-------|-------------|
| `architecture-research` | Technology stack research, ADRs, C4 model documentation |
| `project-diagrams` | AI-generated C4, sequence, ERD, deployment diagrams |
| `building-blocks` | Component specifications for Claude Code to build |

### Planning & Estimation
| Skill | Description |
|-------|-------------|
| `sprint-planning` | User stories (INVEST), capacity management, timelines |
| `service-cost-analysis` | Cloud pricing, ROI projections, cost optimization |
| `risk-assessment` | Risk registers, scoring matrices, mitigation strategies |

### Quality & Review
| Skill | Description |
|-------|-------------|
| `feasibility-analysis` | Technical, resource, and market feasibility |
| `plan-review` | Project plan validation against best practices |
| `market-research-reports` | Comprehensive market analysis reports |

### Utilities
| Skill | Description |
|-------|-------------|
| `generate-image` | AI image generation for diagrams and visuals |
| `markitdown` | Document conversion (PDF, DOCX, PPTX to Markdown) |
| `document-skills` | General document processing utilities |

## Output Structure

Project Planner creates organized output folders:

```
planning_outputs/
└── YYYYMMDD_HHMMSS_<project_name>/
    ├── progress.md              # Real-time progress log
    ├── SUMMARY.md               # Executive summary
    ├── PLAN_REVIEW.md           # Quality review
    │
    ├── specifications/          # Project requirements
    │   ├── project_spec.md      # Business requirements
    │   ├── technical_spec.md    # Technical specifications
    │   └── api_spec.md          # API contracts
    │
    ├── research/                # Research findings
    │   ├── market_research.md   # Market analysis
    │   ├── technology_research.md
    │   └── competitive_analysis.md
    │
    ├── analysis/                # Feasibility & costs
    │   ├── feasibility.md
    │   ├── cost_analysis.md
    │   ├── risk_assessment.md
    │   └── roi_projections.md
    │
    ├── components/              # Building blocks
    │   ├── building_blocks.yaml # Component specifications
    │   └── component_specs/     # Detailed specs per component
    │
    ├── planning/                # Sprint plans
    │   ├── sprint_plan.md
    │   ├── timeline.md
    │   └── milestones.md
    │
    ├── diagrams/                # Architecture diagrams
    │   ├── architecture.png
    │   ├── data_model.png
    │   └── sequence_diagrams/
    │
    └── data/                    # Input data and references
```

## Building Blocks Format

Building blocks are specified in YAML for Claude Code to build:

```yaml
building_blocks:
  - name: "User Authentication Service"
    id: "BB-001"
    type: "backend"
    description: "Handles authentication, authorization, and sessions"

    responsibilities:
      - "User registration with email verification"
      - "Login/logout with JWT tokens"
      - "OAuth2 integration (Google, GitHub)"
      - "Password reset flow"

    dependencies:
      internal:
        - block_id: "BB-010"
          interface: "Database Service"
      external:
        - name: "PostgreSQL"
          version: ">=14.0"
        - name: "Redis"
          version: ">=6.0"

    interfaces:
      api_endpoints:
        - method: "POST"
          path: "/api/v1/auth/register"
          description: "Register new user"
        - method: "POST"
          path: "/api/v1/auth/login"
          description: "Authenticate and get tokens"
      events_published:
        - name: "user.registered"
        - name: "user.logged_in"

    complexity: "M"  # S, M, L, XL
    estimated_hours: 24
    story_points: 5

    test_criteria:
      - "User can register with valid email/password"
      - "Invalid credentials return 401"
      - "JWT tokens are valid and properly scoped"
      - "Rate limiting prevents brute force"

    priority: "critical"
    sprint_assignment: "Sprint 1"
```

## Sprint Planning Format

Sprint plans follow INVEST criteria:

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
          - "Confirmation email is sent"
        story_points: 5
        building_block: "BB-001"

    risks:
      - "OAuth integration may take longer"
```

## Example Workflow

**Request:** "Plan a B2B SaaS inventory management system"

**Project Planner will:**
1. ✅ Create project folder: `planning_outputs/20250106_143022_b2b_inventory_saas/`
2. 🔍 Research competitive landscape and market size
3. 🔍 Research technology options (frameworks, databases, cloud)
4. 📐 Design system architecture with C4 diagrams
5. 🧱 Break down into 15-20 building blocks
6. 📅 Create 6-sprint implementation plan
7. 💰 Analyze costs with AWS/GCP pricing
8. ⚠️ Assess 10-15 risks with mitigations
9. ✅ Conduct plan review
10. 📋 Deliver comprehensive SUMMARY.md

## Documentation

- [Features Guide](docs/FEATURES.md) - Comprehensive overview
- [API Reference](docs/API.md) - Python API documentation
- [Skills Overview](docs/SKILLS.md) - All available skills
- [Development Guide](docs/DEVELOPMENT.md) - Contributing guide

## License

MIT - see [LICENSE](LICENSE)

## Support

- Open an issue on [GitHub](https://github.com/flight505/claude-project-planner/issues)
- See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common problems

## Credits

Forked from [claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer) by K-Dense AI. Transformed for software project planning use cases.

---

⭐ **If you find this useful, please star the repo!** It helps others discover the tool.
