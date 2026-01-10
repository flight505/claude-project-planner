# Changelog

All notable changes to Claude Project Planner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.18] - 2025-01-10

### ✨ Added

#### Smart Parallelization for Planning Phases

- **`parallel-orchestrator.py` script** - Orchestrates parallel task execution within phases
  - Identifies independent tasks that can run simultaneously
  - Maintains sequential execution between phases for context integrity
  - Context sharing via `.context/` directory (phase input/output files)
  - Key findings extraction for context propagation
  - Error isolation (failed parallel tasks don't cascade)

- **`--parallel` flag for `/full-plan`** - Enable smart parallelization
  - Phase 1: research-lookup + competitive-analysis run in parallel (~33% savings)
  - Phase 3: feasibility + risk + cost analyses run in parallel (~60% savings)
  - Total estimated time savings: ~14% (195 min → 167 min)
  - Sequential tasks respect dependencies within each phase

- **Context sharing mechanism**
  - `.context/phase{N}_input.md` - Aggregated context from prior phases
  - `.context/phase{N}_output.md` - Key findings extracted from phase tasks
  - Automatic context merge after parallel task groups complete

### 📝 Documentation

- Added `docs/PARALLELIZATION.md` - Comprehensive parallelization strategy guide
- Updated `/full-plan` command with parallel execution instructions
- Added phase-by-phase parallelization analysis and time savings estimates

---

## [1.0.17] - 2025-01-10

### ✨ Added

#### Quality Gate Hooks
- **PostToolUse validation hook** - Validates planning outputs before they're saved
  - Detects placeholder text ([TODO], [TBD], Lorem ipsum)
  - Validates research files have citations
  - Checks building blocks YAML for required fields
  - Validates cost estimates are in reasonable ranges
  - Warns on short outputs or missing structure
- Non-blocking warnings (informational, doesn't stop execution)

#### Live Progress Dashboard
- **`progress-tracker.py` script** - Real-time progress tracking for planning phases
  - Visual progress bar with percentage complete
  - Phase-by-phase status table (pending, in_progress, completed)
  - Current activity display
  - Elapsed time and estimated remaining time
  - Generates live-updating `progress.md` file

#### Checkpoint/Resume System
- **`checkpoint-manager.py` script** - Save and restore planning state
  - Checkpoints saved after each phase completion
  - Stores key decisions and context summaries
  - Tracks all completed outputs
- **`/resume-plan` command** - Resume interrupted planning sessions
  - Lists available checkpoints
  - Restores context from last completed phase
  - Continues from where it stopped
  - Can clear checkpoint to start fresh

#### Multi-Model Architecture Validation
- **`architecture-validator` agent** - Coordinates multi-model consensus
- **`multi-model-validator.py` script** - Queries multiple AI models for validation
  - Validates architecture decisions with Gemini, GPT-4o, Claude
  - Scores decisions on scalability, security, cost, maintainability
  - Generates consensus report with confidence levels
  - Identifies decisions that need review
- **`--validate` flag for `/full-plan`** - Enable multi-model validation after Phase 2

### 🔧 Changed

- `/full-plan` command now includes checkpoint instructions after each phase
- `/full-plan` command includes progress tracking integration
- SessionStart hook checks remain non-blocking and informational

### 📝 Documentation

- Updated `/full-plan` with Optional Flags section
- Added checkpoint save commands after each phase
- Added progress tracker integration instructions
- Created `/resume-plan` command documentation

---

## [1.0.16] - 2025-01-09

### ✨ Added

#### Mermaid Diagram Rendering with Multi-Tier Fallback

- **`render_mermaid.py` Script** - Robust Mermaid-to-PNG converter with automatic fallbacks
  - **Priority 1: Local mmdc** - Best quality, offline (requires `npm install -g @mermaid-js/mermaid-cli`)
  - **Priority 2: Kroki.io API** - Free online renderer, no installation needed
  - **Priority 3: Nano Banana AI** - AI-generated diagram from Mermaid description
  - **Priority 4: Keep markdown** - Last resort, works in GitHub/GitLab viewers

- **Batch Rendering** - Render all Mermaid files in a directory
  ```bash
  python render_mermaid.py diagrams/ --batch
  ```

- **Step 5.4 in `/generate-report`** - Automatically renders Mermaid diagrams before report compilation
  - Ensures diagrams are available as PNG for PDF/DOCX reports
  - Reports rendering results and suggests mmdc installation if needed

### 🔧 Changed

- **SessionStart Hook** - Now checks for mmdc, Pandoc, and OPENROUTER_API_KEY
  - Provides helpful installation instructions when dependencies are missing
  - Non-blocking warnings (won't fail session start)

### 📝 Documentation

- Updated `project-diagrams/SKILL.md` with automatic rendering documentation
- Added fallback system table explaining rendering priorities
- Updated `commands/generate-report.md` with Step 5.4 for Mermaid rendering

---

## [1.0.15] - 2025-01-09

### ✨ Added

#### Content-Aware Diagram Suggestions

- **Redesigned Q4c in `/generate-report`** - Diagram suggestions now analyze actual report content
  - **Step 4c.1: Extract Content Context** - Reads SUMMARY.md, building_blocks.yaml, and tech specs
  - **Step 4c.2: Generate Contextual Suggestions** - Maps discovered keywords to relevant diagrams
  - **Step 4c.3: Present Dynamic Options** - Shows project-specific options, not generic types

- **Content-to-Diagram Mapping** - Intelligent suggestion based on discovered content:
  | Content Found | Suggested Diagram |
  |---------------|-------------------|
  | Microservices, API Gateway | "[Project] Microservices Architecture" |
  | PostgreSQL, MongoDB, Redis | "[Project] Data Storage Architecture" |
  | Auth, Login, OAuth | "User Authentication Flow" |
  | Cart, Checkout, Payment | "E-commerce Transaction Flow" |
  | AWS Lambda, S3, DynamoDB | "AWS Serverless Infrastructure" |
  | Kubernetes, Docker | "Container Orchestration Diagram" |

- **Industry-Specific Examples** - Dynamic options differ by project type:
  - E-commerce: "Order Processing Flow", "Inventory Management Architecture"
  - Healthcare SaaS: "Patient Data Flow Architecture", "Clinical Decision Support System"

### 📝 Documentation

- Updated `commands/generate-report.md` with 3-step content-aware workflow
- Added content extraction examples using grep/cat patterns
- Added explanation of why content-awareness matters for AI image quality

---

## [1.0.14] - 2025-01-09

### ✨ Added

#### AI Visual Generation (Nano Banana Integration)

- **Visual generation in `/generate-report`** - Interactive menu for AI-generated visuals
  - Question 4: "Generate AI visuals for the report?" (Yes/Cover only/No)
  - Question 4b: Cover image style selection (Modern Tech, Corporate, Industry-Specific, Custom)
  - Question 4c: Diagram type selection (Architecture, Component, Data Flow)

- **Cover image generation** - Professional cover images via Gemini 3 Pro
  - Style-specific prompts (tech, corporate, healthcare, finance, SaaS)
  - Custom style option for user-defined aesthetics
  - Automatic project context extraction for relevant imagery

- **Diagram generation** - AI-generated technical diagrams
  - Architecture overview diagrams
  - Component/building block diagrams
  - Data flow diagrams
  - Prompts enhanced with project-specific context from planning outputs

- **Integration with `generate-image` skill**
  - Uses existing `scripts/generate_image.py` infrastructure
  - Requires `OPENROUTER_API_KEY` environment variable
  - Graceful degradation if API unavailable

### 📝 Documentation

- Updated `report-generation/SKILL.md` with visual generation section
- Added style prompt reference table
- Documented diagram generation patterns

---

## [1.0.13] - 2025-01-09

### ✨ Added

#### Report Generation with IEEE Citations

- **`/generate-report` Command** - Interactive report compilation wizard
  - Scans planning outputs folder and presents interactive menu
  - User selects which sections to include (multiSelect)
  - Optional IEEE-style citations with numbered reference list
  - Output formats: PDF (via Pandoc/LaTeX), DOCX, or Markdown
  - Generates cover page, table of contents, and numbered sections

- **`report-generation` Skill** - Comprehensive report compilation capabilities
  - `compile_report.py` - Main compilation script
    - Merges markdown files in logical section order
    - Processes citations and generates IEEE reference list
    - Supports custom templates and exclusions
  - `citation_formatter.py` - IEEE citation formatting utility
    - Formats citations as `[1]`, `[2]`, etc. in order of appearance
    - Generates BibTeX output for Pandoc citeproc
  - Assets: `ieee.csl`, `report_template.tex`, `cover_page.md`
  - References: `ieee_format.md`, `pandoc_options.md`

- **Citation Storage in Research Lookup**
  - New `save_citations()` method saves citations to sidecar `.citations.json` files
  - New `lookup_and_save()` method for combined markdown + citations output
  - New CLI options: `--save-citations`, `--save-markdown`
  - Citations flow: research skills → `.citations.json` → report generation

### 📝 Documentation

- Updated CLAUDE.md with `/generate-report` command and `report-generation` skill
- Added Development section with version bump reminder (triggers auto-update)

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
