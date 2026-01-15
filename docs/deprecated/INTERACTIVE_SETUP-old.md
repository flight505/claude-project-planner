# Interactive Setup Workflow

This document describes the enhanced interactive setup process for `/full-plan` introduced in v1.2.0.

## Overview

The interactive setup provides a guided, user-friendly way to gather comprehensive project details before planning begins. It combines:

1. **File-based input** - Detailed template for project information
2. **Background dependency installation** - Automatic setup while you work
3. **Interactive configuration** - Choice-based setup for preferences
4. **Validation** - Ensures required information is provided

## Workflow Diagram

```
User invokes /full-plan
        │
        ├─ SessionStart Hook triggers
        │  └─ Background: Install dependencies
        │
        ├─ Step 1: Generate and open planning template
        │  └─ User fills out project details in editor
        │
        ├─ Step 2: Dependencies install (parallel to user input)
        │  └─ Status tracked in /tmp/claude-planner-deps-status.json
        │
        ├─ Step 3: Parse and validate user input
        │  ├─ Extract structured data to JSON
        │  └─ Validate required fields
        │
        ├─ Step 4: Interactive configuration (AskUserQuestion)
        │  ├─ AI Provider selection (Gemini vs OpenRouter)
        │  ├─ Parallelization preference
        │  └─ Validation preference
        │
        ├─ Step 5: Wait for dependencies to complete
        │  └─ Block until all packages installed
        │
        └─ Step 6: Begin planning execution
           └─ Proceed to Phase 1 with full context
```

## Step-by-Step Example

### 1. User Invokes Command

```bash
/full-plan my-saas-app
```

### 2. Template Opens in Editor

The system creates `.my-saas-app-plan-input.md` and opens it:

```markdown
---
# Claude Project Planner - Interactive Setup
---

## Project Overview *

**Project Name**: My SaaS App

**Description**:
[User fills this in with detailed project description...]

## Target Audience *

**Primary Users**: [Who will use this?]
...
```

**Meanwhile, in background:**
```bash
[SessionStart] Detected /full-plan invocation
[SessionStart] Starting background dependency installation...
[SessionStart] Background installation started (PID: 12345)
```

### 3. User Fills Out Template

User replaces placeholders with actual project details:

```markdown
## Project Overview *

**Project Name**: TeamSync

**Description**:
A real-time collaboration platform for remote teams. Features include
video conferencing, shared workspaces, task management, and integrations
with Slack, GitHub, and Google Workspace. Targets startups and small
businesses (5-50 employees) with remote or hybrid teams.

## Target Audience *

**Primary Users**: Remote team managers and knowledge workers

**User Personas**:
1. Team Lead: Needs project overview, task assignment, team coordination
2. Developer: Needs task tracking, code reviews, integration with GitHub
3. Designer: Needs file sharing, feedback collection, version control

**Geographic Focus**: North America and Europe initially

**Market Size**: 2 million small businesses with remote teams
...
```

User saves and closes the file.

### 4. System Parses Input

```bash
python scripts/parse-plan-input.py .my-saas-app-plan-input.md --validate
```

**Output:**
```json
{
  "project_name": "TeamSync",
  "description": "A real-time collaboration platform for remote teams...",
  "target_audience": {
    "primary_users": "Remote team managers and knowledge workers",
    ...
  },
  ...
}
```

✓ Validation passed - all required fields present

### 5. Interactive Configuration

**AI Provider Selection:**

```
┌─────────────────────────────────────┐
│ AI Provider                         │
├─────────────────────────────────────┤
│ Which AI provider for research?     │
│                                     │
│ ○ Google Gemini Deep Research       │
│   (Recommended)                     │
│   Comprehensive research (60 min)  │
│   Requires GEMINI_API_KEY +         │
│   Google AI Pro ($19.99/month)      │
│                                     │
│ ● Perplexity via OpenRouter         │
│   Fast web-grounded research        │
│   Requires OPENROUTER_API_KEY       │
│                                     │
│ ○ Auto-detect                       │
│   Choose based on available keys    │
└─────────────────────────────────────┘
```

**Parallelization:**

```
┌─────────────────────────────────────┐
│ Performance                         │
├─────────────────────────────────────┤
│ Enable smart parallelization?       │
│                                     │
│ ● Yes - Full parallelization        │
│   Run independent tasks in parallel │
│   ~14% time savings, 60% in Phase 3│
│                                     │
│ ○ No - Sequential execution         │
│   Run tasks in order (slower)       │
└─────────────────────────────────────┘
```

**Validation:**

```
┌─────────────────────────────────────┐
│ Validation                          │
├─────────────────────────────────────┤
│ Multi-model architecture validation?│
│                                     │
│ ○ Yes - Multi-model validation      │
│   Validate with 3 AI models         │
│                                     │
│ ● No - Skip validation              │
│   Proceed to implementation         │
└─────────────────────────────────────┘
```

### 6. Dependency Check

```bash
Waiting for dependency installation to complete...

[████████████████████████████████] 100%

✓ All dependencies installed successfully!
```

### 7. Planning Begins

```
✓ Setup complete! Beginning project planning for: TeamSync

Phase 1: Market Research & Competitive Analysis
  🔍 research-lookup: Analyzing collaboration platform market...
  🔍 competitive-analysis: Comparing with Slack, Teams, Notion...
  ...
```

## Template Fields Reference

### Required Fields (*)

- **Project Name** - Brief, memorable name
- **Description** - Detailed explanation (2-3 paragraphs recommended)
- **Primary Users** - Target user demographic
- **Primary Objective** - Main goal/problem being solved
- **Core Features** - List of 3-10 key features

### Recommended Fields

- **User Personas** - 2-3 detailed user types
- **Success Metrics** - Measurable goals
- **Budget** - Budget range or constraints
- **Timeline** - Deadlines or milestones
- **Tech Stack Preferences** - Technology requirements
- **Competition** - Key competitors and differentiation

### Optional Fields

- **Market Size** - TAM/SAM/SOM
- **Integrations** - Third-party services
- **Compliance** - Security/regulatory requirements
- **Launch Strategy** - Go-to-market approach
- **Additional Context** - Any other relevant info

## Configuration Choices

### AI Provider

| Choice | When to Use | Cost | Capabilities |
|--------|-------------|------|--------------|
| **Gemini Deep Research** | Best for comprehensive research, complex projects | $19.99/month + API usage | Multi-step research, 60min queries, citations |
| **Perplexity (OpenRouter)** | Quick research, cost-sensitive | Pay-per-use (~$0.01/query) | Fast web search, good summaries |
| **Auto-detect** | Unsure or want automatic selection | Varies | Uses best available |

### Parallelization

| Choice | Time Savings | Trade-offs |
|--------|--------------|------------|
| **Yes (Recommended)** | ~14% overall, 60% in Phase 3 | Slightly more complex logs |
| **No** | 0% (baseline) | Simpler, more predictable |

### Multi-Model Validation

| Choice | Quality Impact | Cost Impact |
|--------|----------------|-------------|
| **Yes** | Higher confidence in architecture | 3x API calls for validation |
| **No** | Standard quality | Lower cost |

## Background Dependency Installation

### How It Works

1. **SessionStart Hook** detects `/full-plan` in user message
2. Triggers `ensure-dependencies.sh` with `nohup` in background
3. Writes progress to `/tmp/claude-planner-deps-status.json`
4. Main process checks status before Phase 1

### Status File Format

```json
{
  "status": "installing",
  "progress": 65,
  "current": "markitdown",
  "timestamp": "2026-01-12T14:35:22Z",
  "log_file": "/tmp/claude-planner-deps.log"
}
```

**Possible Status Values:**
- `starting` - Initialization
- `installing` - In progress
- `complete` - All packages installed
- `partial` - Some packages failed
- `timeout` - Exceeded 10 minutes

### Manual Intervention

If dependency installation fails:

```bash
# Check what failed
cat /tmp/claude-planner-deps.log

# Install manually
pip install -r requirements-full-plan.txt
# or
uv pip install -r requirements-full-plan.txt

# Verify
python scripts/check-dependencies.py
```

## File Locations

| File | Purpose | Auto-cleanup? |
|------|---------|---------------|
| `.{project}-plan-input.md` | User's filled template | No (keep for reference) |
| `.{project}-plan-data.json` | Parsed structured data | No (used by planner) |
| `/tmp/claude-planner-deps-status.json` | Dependency install status | Yes (1 hour expiry) |
| `/tmp/claude-planner-deps.log` | Installation log | Yes (manual cleanup) |
| `/tmp/claude-planner-deps.pid` | Background process ID | Yes (on completion) |

## Troubleshooting

### Template Not Opening

**Problem:** `create-plan-input.sh` doesn't open editor

**Solution:**
```bash
# Set your preferred editor
export EDITOR=nano  # or code, vim, emacs
```

### Validation Fails

**Problem:** Parser reports missing required fields

**Solution:**
1. Re-open template: `nano .{project}-plan-input.md`
2. Look for `[placeholder]` values
3. Replace with actual content
4. Save and re-run parser

### Dependencies Timeout

**Problem:** Installation exceeds 10 minutes

**Solution:**
```bash
# Kill background process
pkill -f ensure-dependencies.sh

# Install manually with verbose output
pip install -r requirements-full-plan.txt -v
```

### Wrong API Provider Selected

**Problem:** Using OpenRouter but want Gemini

**Solution:**
1. Set `GEMINI_API_KEY` environment variable
2. Re-run `/full-plan`
3. Select "Google Gemini Deep Research" when prompted

## Backward Compatibility

The old workflow still works:

```bash
# Legacy: Direct invocation without template
/full-plan my-project --description "A brief description"
```

This will prompt for missing fields using AskUserQuestion instead of the template.

**Recommendation:** Use the interactive template for complex projects, legacy method for quick prototypes.

## Best Practices

1. **Be Detailed in Description** - More context = better planning
2. **Specify Core Features** - List 5-10 specific features, not categories
3. **Provide Budget & Timeline** - Helps with realistic planning
4. **Describe Users Clearly** - Include pain points and needs
5. **Review Template Before Submitting** - Check for placeholders
6. **Save Template File** - Keep for future reference and updates

## Example: Complete Flow

```bash
$ /full-plan shopify-competitor

# Template opens, user fills it out:
#   Project: EasyStore
#   Description: Simplified e-commerce platform for small businesses...
#   Features: Product catalog, shopping cart, payment processing...
#   Users: Small business owners (1-10 employees)...
#   Budget: $50k development, $5k/month operations...

# User saves and closes editor

Parsing input...
✓ Validation passed

# AskUserQuestion prompts appear
AI Provider: [User selects "Perplexity via OpenRouter"]
Parallelization: [User selects "Yes"]
Validation: [User selects "No"]

Waiting for dependencies...
[████████████████████████████████] 100%

✓ Setup complete! Beginning planning...

Phase 1: Market Research
  ✓ research-lookup (3 min)
  ✓ competitive-analysis (5 min)
  ✓ market-research-reports (7 min)

...

✓ Planning complete!
Results: planning_outputs/20260112_143022_easystore/
```

## Next Steps

After setup completes and planning finishes:

1. Review executive summary: `planning_outputs/{timestamp}_{project}/SUMMARY.md`
2. Check building blocks: `planning_outputs/{timestamp}_{project}/components/building_blocks.yaml`
3. Review sprint plan: `planning_outputs/{timestamp}_{project}/planning/sprint_plan.md`
4. Generate report: `/generate-report {project}`
