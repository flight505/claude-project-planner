---
name: market-research-reports
description: "Generate comprehensive market research reports (50+ pages) in the style of top consulting firms (McKinsey, BCG, Gartner). Features professional LaTeX formatting, extensive visual generation with project-diagrams and generate-image, deep integration with research-lookup for data gathering, and multi-framework strategic analysis including Porter's Five Forces, PESTLE, SWOT, TAM/SAM/SOM, and BCG Matrix."
allowed-tools: [Read, Write, Edit, Bash]
effort: max
---

# Market Research Reports

## Overview

Market research reports are comprehensive strategic documents that analyze industries, markets, and competitive landscapes to inform business decisions, investment strategies, and strategic planning. This skill generates **professional-grade reports of 50+ pages** with extensive visual content, modeled after deliverables from top consulting firms like McKinsey, BCG, Bain, Gartner, and Forrester.

**Key Features:**
- **Comprehensive length**: Reports are designed to be 50+ pages with no token constraints
- **Visual-rich content**: 5-6 key diagrams generated at start (more added as needed during writing)
- **Data-driven analysis**: Deep integration with research-lookup for market data
- **Multi-framework approach**: Porter's Five Forces, PESTLE, SWOT, BCG Matrix, TAM/SAM/SOM
- **Professional formatting**: Consulting-firm quality typography, colors, and layout
- **Actionable recommendations**: Strategic focus with implementation roadmaps

**Output Format:** LaTeX with professional styling, compiled to PDF. Uses the `market_research.sty` style package for consistent, professional formatting.

## When to Use This Skill

This skill should be used when:
- Creating comprehensive market analysis for investment decisions
- Developing industry reports for strategic planning
- Analyzing competitive landscapes and market dynamics
- Conducting market sizing exercises (TAM/SAM/SOM)
- Evaluating market entry opportunities
- Preparing due diligence materials for M&A activities
- Creating thought leadership content for industry positioning

## Visual Enhancement Requirements

**CRITICAL: Market research reports should include key visual content.**

Every report should generate **6 essential visuals** at the start, with additional visuals added as needed during writing.

### Visual Generation Tools

**Use `project-diagrams` for:** Market growth charts, TAM/SAM/SOM diagrams, Porter's Five Forces, competitive positioning matrices, market segmentation charts, value chain diagrams, technology roadmaps, risk heatmaps, strategic prioritization matrices, implementation timelines, SWOT diagrams, BCG matrices.

```bash
# Example: Generate a TAM/SAM/SOM diagram
python .claude/skills/project-diagrams/scripts/generate_schematic.py \
  "TAM SAM SOM concentric circle diagram showing Total Addressable Market $50B outer circle, Serviceable Addressable Market $15B middle circle, Serviceable Obtainable Market $3B inner circle" \
  -o figures/tam_sam_som.png --doc-type report
```

**Use `generate-image` for:** Executive summary hero infographics, industry/sector conceptual illustrations, abstract technology visualizations, cover page imagery.

### Recommended Visuals by Section

| Section | Priority Visuals | Optional Visuals |
|---------|-----------------|------------------|
| Executive Summary | Executive infographic (START) | - |
| Market Size & Growth | Growth trajectory (START), TAM/SAM/SOM (START) | Regional breakdown, segment growth |
| Competitive Landscape | Porter's Five Forces (START), Positioning matrix (START) | Market share chart, strategic groups |
| Risk Analysis | Risk heatmap (START) | Mitigation matrix |
| Strategic Recommendations | Opportunity matrix | Priority framework |
| Implementation Roadmap | Timeline/Gantt | Milestone tracker |

**Start with 6 priority visuals** (marked as START above), then generate additional visuals as specific sections are written.

---

## Report Structure (50+ Pages)

The report follows an 11-chapter structure. See `references/report_structure_guide.md` for detailed section-by-section content requirements, data points, and visual requirements per chapter.

### Front Matter (~5 pages)
- **Cover Page**: Title, subtitle, hero visualization, date, classification
- **Table of Contents**: Auto-generated with List of Figures and Tables
- **Executive Summary** (2-3 pages): Market snapshot, investment thesis, key findings, strategic recommendations

### Core Analysis (~35 pages)
1. **Market Overview & Definition** (4-5 pages): Market definition, ecosystem mapping, stakeholders, boundaries
2. **Market Size & Growth Analysis** (6-8 pages): TAM/SAM/SOM, historical growth, projections, regional/segment breakdown
3. **Industry Drivers & Trends** (5-6 pages): PESTLE analysis, trend impact assessment, macroeconomic factors
4. **Competitive Landscape** (6-8 pages): Porter's Five Forces, market share, competitive positioning, strategic groups
5. **Customer Analysis & Segmentation** (4-5 pages): Segment definitions, buying behavior, value proposition canvas
6. **Technology & Innovation Landscape** (4-5 pages): Current stack, emerging tech, R&D analysis, patent landscape
7. **Regulatory & Policy Environment** (3-4 pages): Regulatory framework, compliance, upcoming changes
8. **Risk Analysis** (3-4 pages): Risk heatmap, risk register, mitigation matrix

### Strategic Recommendations (~10 pages)
9. **Strategic Opportunities & Recommendations** (4-5 pages): Opportunity sizing, strategic options, priority matrix
10. **Implementation Roadmap** (3-4 pages): Phased plan, milestones, resource requirements, governance
11. **Investment Thesis & Financial Projections** (3-4 pages): Financial projections, scenario analysis, ROI/IRR

### Back Matter (~5 pages)
- Appendix A: Methodology & Data Sources
- Appendix B: Detailed Market Data Tables
- Appendix C: Company Profiles
- References/Bibliography (BibTeX)

---

## Workflow

### Phase 1: Research & Data Gathering

**Step 1: Define Scope** - Clarify market definition, geographic boundaries, time horizon, key questions.

**Step 2: Conduct Deep Research** - Use `research-lookup` extensively:

```bash
# Market size and growth data
python skills/research-lookup/scripts/research_lookup.py \
  "What is the current market size and projected growth rate for [MARKET] industry? Include TAM, SAM, SOM estimates and CAGR projections"

# Competitive landscape
python skills/research-lookup/scripts/research_lookup.py \
  "Who are the top 10 competitors in the [MARKET] market? What is their market share and competitive positioning?"
```

**Step 3: Data Organization** - Create `sources/` folder, organize by section, identify gaps, follow up.

### Phase 2: Analysis & Framework Application

**Step 4: Apply Frameworks** - TAM/SAM/SOM, Porter's Five Forces, PESTLE, SWOT, Competitive Positioning.

**Step 5: Develop Insights** - Synthesize findings, identify strategic implications, develop recommendations.

### Phase 3: Visual Generation

**Step 6: Generate All Visuals** - Generate visuals BEFORE writing. See `references/visual_generation_guide.md` for complete prompts for all visual types.

```bash
# Generate all standard market report visuals
python skills/market-research-reports/scripts/generate_market_visuals.py \
  --topic "[MARKET NAME]" \
  --output-dir figures/
```

### Phase 4: Report Writing

**Step 7: Initialize Project Structure**

```
writing_outputs/YYYYMMDD_HHMMSS_market_report_[topic]/
├── progress.md
├── drafts/
│   └── v1_market_report.tex
├── references/
│   └── references.bib
├── figures/
│   └── [all generated visuals]
├── sources/
│   └── [research notes]
└── final/
```

**Step 8: Write Report** - Use `market_report_template.tex` as starting point. Write each section with comprehensive coverage, data-driven content, visual integration, professional tone, and no token constraints.

### Phase 5: Compilation & Review

**Step 9: Compile LaTeX**

```bash
cd writing_outputs/[project_folder]/drafts/
xelatex v1_market_report.tex
bibtex v1_market_report
xelatex v1_market_report.tex
xelatex v1_market_report.tex
```

**Step 10: Quality Review** - Verify 50+ pages, all visuals render, data has sources, frameworks applied, recommendations actionable, bibliography complete.

**Step 11: Plan Review** - Use the plan-review skill to evaluate comprehensiveness, data accuracy, logical flow, and recommendation quality.

---

## Quality Standards

### Page Count Targets

| Section | Minimum Pages | Target Pages |
|---------|---------------|--------------|
| Front Matter | 4 | 5 |
| Market Overview | 4 | 5 |
| Market Size & Growth | 5 | 7 |
| Industry Drivers | 4 | 6 |
| Competitive Landscape | 5 | 7 |
| Customer Analysis | 3 | 5 |
| Technology Landscape | 3 | 5 |
| Regulatory Environment | 2 | 4 |
| Risk Analysis | 2 | 4 |
| Strategic Recommendations | 3 | 5 |
| Implementation Roadmap | 2 | 4 |
| Investment Thesis | 2 | 4 |
| Back Matter | 4 | 5 |
| **TOTAL** | **43** | **66** |

### Data & Writing Quality
- **Currency**: Data no older than 2 years (prefer current year)
- **Sourcing**: All statistics attributed to specific sources
- **Validation**: Cross-reference multiple sources when possible
- **Objectivity**: Balanced analysis, acknowledge uncertainties
- **Precision**: Use specific numbers over vague qualifiers
- **Actionability**: Recommendations are specific and implementable

---

## LaTeX Formatting

Use the `market_research.sty` package for professional formatting. For complete formatting reference including box environments, figure formatting, and table formatting, see `assets/FORMATTING_GUIDE.md`.

```latex
\documentclass[11pt,letterpaper]{report}
\usepackage{market_research}
```

**Available box environments**: `keyinsightbox` (blue), `marketdatabox` (green), `riskbox` (orange), `recommendationbox` (purple), `calloutbox` (gray).

---

## Integration with Other Skills

- **research-lookup**: Essential for gathering market data, statistics, and competitive intelligence
- **project-diagrams**: Generate all diagrams, charts, and visualizations
- **generate-image**: Create infographics and conceptual illustrations
- **plan-review**: Evaluate report quality and completeness
- **competitive-analysis**: Detailed competitor profiling and market positioning analysis

---

## Resources

### Reference Files
- **`references/report_structure_guide.md`**: Detailed section-by-section content requirements
- **`references/visual_generation_guide.md`**: Complete prompts for generating all visual types
- **`references/data_analysis_patterns.md`**: Templates for Porter's, PESTLE, SWOT, etc.
- **`references/examples.md`**: Example prompts and validation checklists

### Assets
- **`assets/market_research.sty`**: LaTeX style package
- **`assets/market_report_template.tex`**: Complete LaTeX template
- **`assets/FORMATTING_GUIDE.md`**: Quick reference for box environments and styling

### Scripts
- **`scripts/generate_market_visuals.py`**: Batch generate all report visuals

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Report under 50 pages | Expand appendix data tables, add company profiles, include regional breakdowns |
| Visuals not rendering | Check file paths in LaTeX, ensure images in figures/ folder, verify extensions |
| Bibliography missing | Run bibtex after first xelatex pass, check .bib syntax |
| Table/figure overflow | Use `\resizebox` or `adjustbox`, reduce image width percentage |
| Poor visual quality | Use `--doc-type report` flag, increase iterations with `--iterations 5` |

---

Use this skill to create comprehensive, visually-rich market research reports that rival top consulting firm deliverables. The combination of deep research, structured frameworks, and extensive visualization produces documents that inform strategic decisions and demonstrate analytical rigor.
