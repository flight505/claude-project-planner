# Changelog

All notable changes to Claude Project Planner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.11] - 2025-01-07

### 🔧 Fixed

#### Comprehensive Code Review Fixes

Multi-agent code review identified and fixed remaining issues from Scientific Writer → Project Planner transformation.

- **CRITICAL: Fixed undefined variable crash** in `generate_market_visuals.py`
  - Line 468: Changed `VISUALS` → `visuals_to_generate`
  - Would have caused runtime crash when using `--only` filter flag

- **Fixed skill name references** across 11 files
  - Changed all `scientific-schematics` → `project-diagrams`
  - Affected files: SKILL.md files, visual_generation_guide.md, market_report_template.tex, docs/*.md

- **Fixed duplicate line** in `generate_market_visuals.py`
  - Lines 113-114 both contained `"project-diagrams"` in tuple definition
  - Removed duplicate entry

- **Added deprecation notice** to `scripts/README.md`
  - Legacy PyPI scripts were for `scientific-writer` package
  - Plugin versioning now via `.claude-plugin/plugin.json` and `marketplace.json`

---

## [1.0.10] - 2025-01-07

### 🔧 Fixed

#### Project Diagrams doc-type Support

- **Fixed `--doc-type` argument mismatch** - Scripts now accept project-planning doc types
  - Added: `specification`, `architecture`, `proposal`, `sprint`
  - Updated both `generate_schematic.py` and `generate_schematic_ai.py`
  - Updated quality thresholds in `QUALITY_THRESHOLDS` dictionary
  - Maintains backward compatibility with scientific writer doc types

**New doc-types with quality thresholds:**
| Type | Threshold | Description |
|------|-----------|-------------|
| `specification` | 8.5/10 | Technical specs, PRDs |
| `architecture` | 8.0/10 | Architecture documents |
| `proposal` | 8.0/10 | Business proposals |
| `sprint` | 7.5/10 | Sprint planning docs |

---

## [1.0.9] - 2025-01-07

### ✨ Added

#### Python Dependency Management

- **`requirements.txt`** - Added Python dependency manifest for plugin scripts
  - `requests` for research-lookup API calls
  - `python-docx`, `python-pptx`, `openpyxl`, `PyPDF2` for document processing
  - `markitdown` for document conversion

- **SessionStart Hook** - Added automatic dependency check on session start
  - `hooks.json` with SessionStart configuration
  - `scripts/check-deps.sh` warns if `requests` or `OPENROUTER_API_KEY` missing
  - Non-blocking warnings (won't fail session start)

### 📝 Documentation

- Updated `research-lookup/SKILL.md` with Python dependency instructions

---

## [1.0.8] - 2025-01-07

### 📝 Documentation

- **Complete Documentation Overhaul**
  - Rewrote CHANGELOG.md for Claude Project Planner (was showing Scientific Writer history)
  - Updated README.md with new commands, skills table, Go-to-Market section
  - Updated CLAUDE.md with orchestration command references and phase descriptions
  - Added version badge to README.md

---

## [1.0.7] - 2025-01-07

### ✨ Added

#### Orchestration Commands

- **`/full-plan` Command** - Master orchestrator for comprehensive project planning
  - Phase 1: Market Research & Competitive Analysis
  - Phase 2: Architecture & Building Blocks
  - Phase 3: Feasibility, Risk & Cost Analysis
  - Phase 4: Sprint Planning & Milestones
  - Phase 5: Go-to-Market & Marketing Campaign
  - Phase 6: Plan Review & Executive Summary
  - Creates structured `planning_outputs/<project>/` folder with all deliverables
  - Systematically invokes all relevant skills in sequence

- **`/tech-plan` Command** - Technical-focused planning (no marketing phases)
  - Architecture design
  - Building blocks decomposition
  - Feasibility & risk analysis
  - Service cost analysis
  - Sprint planning
  - Lighter-weight alternative when business/marketing isn't needed

### 📝 Documentation

- Updated CHANGELOG.md for Claude Project Planner
- Updated README.md with new commands and skills
- Updated CLAUDE.md with orchestration command references

---

## [1.0.6] - 2025-01-07

### ✨ Added

#### Marketing Campaign Skill

- **`marketing-campaign`** - Comprehensive social media and campaign planning toolkit
  - Campaign strategy and brief templates (SMART goals, personas, positioning)
  - Content calendar structure with 60-30-10 rule (Value/Engagement/Promotional)
  - Platform playbooks for LinkedIn, X/Twitter, Instagram, TikTok
  - Influencer tier framework (Nano → Mega) with outreach templates
  - Budget allocation framework (60-30-10: Paid/Content/Tools)
  - KPI tracking and reporting templates
  - Product launch timeline (pre-launch, launch week, post-launch)
  - Integration with `project-diagrams`, `generate-image`, `competitive-analysis`

---

## [1.0.5] - 2025-01-07

### 🔧 Fixed

- **Command Visibility** - Fixed `/project-planner:setup` not appearing in slash commands
  - Simplified command frontmatter to only required `description` field
  - Removed unnecessary `name` and `allowed-tools` fields from commands

---

## [1.0.4] - 2025-01-07

### 🔧 Fixed

- **Conflicting Manifests Error** - Resolved "Plugin has conflicting manifests" error
  - Set `strict: true` in marketplace.json
  - Removed skills array from marketplace.json
  - plugin.json is now the single source of truth for plugin components

---

## [1.0.3] - 2025-01-07

### ✨ Added

#### Setup Command

- **`/project-planner:setup`** - Interactive configuration command
  - Detects existing environment variables (CLAUDE_CODE_OAUTH_TOKEN, ANTHROPIC_API_KEY, OPENROUTER_API_KEY)
  - Explains authentication options for Claude Max vs API users
  - Guides users through API key configuration
  - Optionally creates project-local config (`.claude/project-planner.local.md`)
  - Validates API key format
  - Provides summary of configured features

### 🔧 Changed

- Added `.claude/*.local.md` to .gitignore for safe local configuration

---

## [1.0.2] - 2025-01-07

### 🔧 Fixed

- **Plugin Path Format** - Fixed "Invalid schema: must start with './'" error
  - Changed all skill paths from `../project_planner/...` to `./project_planner/...`
  - Expanded document-skills to individual sub-skill paths (docx, pdf, pptx, xlsx)
  - Created plugin.json file (was missing)

---

## [1.0.1] - 2025-01-07

### 🔧 Fixed

- Initial plugin structure fixes
- Marketplace.json configuration updates

---

## [1.0.0] - 2025-01-07

### 🎉 Initial Release

Forked from [claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer) by K-Dense AI and transformed for software project planning use cases.

### ✨ Core Features

#### Project Planning Skills

- **`architecture-research`** - Technology stack research, ADRs, C4 model documentation
- **`building-blocks`** - Component specifications for Claude Code to build
- **`sprint-planning`** - User stories with INVEST criteria, capacity management
- **`service-cost-analysis`** - Cloud pricing, ROI projections, cost optimization
- **`risk-assessment`** - Risk registers, scoring matrices, mitigation strategies
- **`feasibility-analysis`** - Technical, resource, and market feasibility
- **`plan-review`** - Project plan validation against best practices

#### Research & Analysis Skills

- **`research-lookup`** - Real-time technology research via Perplexity Sonar
- **`competitive-analysis`** - Market positioning, competitor profiling
- **`market-research-reports`** - Comprehensive market analysis reports

#### Visualization Skills

- **`project-diagrams`** - AI-generated C4, sequence, ERD, deployment diagrams
- **`generate-image`** - AI image generation for diagrams and visuals

#### Document Skills

- **`markitdown`** - Document conversion (PDF, DOCX, PPTX to Markdown)
- **`document-skills/docx`** - Word document processing
- **`document-skills/pdf`** - PDF processing
- **`document-skills/pptx`** - PowerPoint processing
- **`document-skills/xlsx`** - Excel processing

### 📝 Documentation

- Complete rebranding from "Scientific Writer" to "Claude Project Planner"
- Updated all skill files, README, and documentation
- New CLAUDE.md with project planner instructions
- New .claude/PLANNER.md with comprehensive system instructions

### 🔧 Technical

- Plugin structure with marketplace.json and plugin.json
- Output directory: `planning_outputs/`
- Building blocks in YAML format for Claude Code consumption
- Sprint planning with INVEST criteria

---

## Origin

This project was created by forking [claude-scientific-writer v2.10.0](https://github.com/K-Dense-AI/claude-scientific-writer) and adapting it for software project planning workflows.

**Key Transformations:**
- Scientific writing → Software architecture research
- Paper generation → Project specification generation
- Literature review → Technology & market research
- Citations → Building block specifications
- LaTeX output → Markdown & YAML output

---

**Legend:**
- ✨ Added - New features
- 🔄 Changed - Changes in existing functionality
- 🗑️ Removed - Removed features
- 🔧 Fixed - Bug fixes
- 📝 Documentation - Documentation changes
