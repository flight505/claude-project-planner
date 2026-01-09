---
description: Compile project planning outputs into a professional report with optional IEEE citations, table of contents, and cover page. Supports PDF, DOCX, and Markdown output.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "AskUserQuestion", "TodoWrite"]
argument-hint: "[planning_folder]"
---

# Generate Report Command

When the user invokes `/generate-report`, compile the project planning outputs into a professional, well-formatted deliverable document.

## Workflow Overview

1. **Locate** planning outputs folder
2. **Scan** available content and citations
3. **Ask** user preferences via interactive menu
4. **Compile** report based on selections
5. **Generate** output in requested format

## Step 1: Locate Planning Outputs

If user provided a folder path argument, use that. Otherwise:

1. Look for `planning_outputs/` directory in current project
2. List available project folders (format: `YYYYMMDD_HHMMSS_<project_name>/`)
3. If multiple exist, use the most recent OR ask user which one

```bash
ls -la planning_outputs/ 2>/dev/null || echo "No planning_outputs folder found"
```

If no planning outputs found, inform user:
> "No planning outputs found. Run `/full-plan` or `/tech-plan` first to generate content, then use `/generate-report` to compile it."

## Step 2: Scan Available Content

Read the planning folder to identify what sections exist:

```bash
# List all directories and key files
find <planning_folder> -type d -maxdepth 1
find <planning_folder> -name "*.md" -maxdepth 2
find <planning_folder> -name "*.citations.json"
```

Map found content to logical groups:

| Found Path | Content Group |
|------------|---------------|
| `research/`, `specifications/` | Research & Market Analysis |
| `components/`, `diagrams/` | Architecture & Components |
| `planning/`, `analysis/` | Planning & Analysis |
| `marketing/` | Marketing & Go-to-Market |
| `SUMMARY.md` | Executive Summary |
| `*.citations.json` | Has citations available |

Note which groups have content and whether citations are available.

## Step 3: Present Interactive Menu

Use `AskUserQuestion` to gather preferences. **Adapt questions based on what content exists.**

### Question 1: Content Selection

Present only groups that have content. Use `multiSelect: true`.

```
header: "Sections"
question: "Which sections should be included in the report?"
multiSelect: true
options:
  - label: "Research & Market Analysis"
    description: "Market research, competitive analysis, specifications"
  - label: "Architecture & Components"
    description: "System design, building blocks, diagrams"
  - label: "Planning & Analysis"
    description: "Sprint plans, feasibility, costs, risks"
  - label: "Marketing & Go-to-Market"
    description: "Campaign plans, content calendars (if exists)"
```

The user can also select "Other" to provide custom input such as:
- Exclude specific files: "Don't include risk_assessment.md"
- Add external content: "Also include ./extra_notes.md"
- Custom ordering: "Put architecture before research"
- Any other special requests

### Question 2: Citations (only if citations exist)

If `*.citations.json` files were found:

```
header: "Citations"
question: "Include citations and references?"
multiSelect: false
options:
  - label: "Yes - IEEE style citations (Recommended)"
    description: "Inline [1] citations with numbered reference list at end"
  - label: "No citations"
    description: "Plain report without citation markers or references"
```

If no citation files found, skip this question and proceed without citations.

### Question 3: Output Format

```
header: "Format"
question: "What output format do you need?"
multiSelect: false
options:
  - label: "PDF (Recommended)"
    description: "Professional formatting, requires Pandoc + LaTeX"
  - label: "Word Document (.docx)"
    description: "Editable format for collaboration"
  - label: "Markdown"
    description: "Single compiled .md file"
```

## Step 4: Process User Selections

After receiving answers, parse the selections:

### Handle Custom Input

If user provided custom input via "Other":

1. **Exclusions**: Note files to skip during compilation
2. **Additions**: Queue external files to include
3. **Ordering**: Adjust section order as requested
4. **Other requests**: Apply any special formatting or content changes

### Determine Compilation Parameters

Build the compilation command based on selections:

```python
sections = []
if "Research & Market Analysis" selected:
    sections.extend(["research", "specifications"])
if "Architecture & Components" selected:
    sections.extend(["components", "diagrams"])
if "Planning & Analysis" selected:
    sections.extend(["planning", "analysis"])
if "Marketing & Go-to-Market" selected:
    sections.append("marketing")

citations_enabled = (Q2 answer == "Yes - IEEE style")
output_format = "pdf" | "docx" | "md"  # based on Q3
```

## Step 5: Compile the Report

Execute the compilation script:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/report-generation/scripts/compile_report.py" \
  --input-dir "<planning_folder>" \
  --output "<planning_folder>/REPORT.<format>" \
  --format <pdf|docx|md> \
  --sections "<comma-separated-sections>" \
  $([ "$citations_enabled" = true ] && echo "--citations") \
  --toc \
  --cover-title "<Project Name>"
```

### If Script Not Available

If the compile script doesn't exist or fails, perform manual compilation:

1. **Create output file** in the planning folder
2. **Add cover page** with project name and date
3. **Generate TOC** from section headings
4. **Merge content** in order:
   - Executive Summary (SUMMARY.md)
   - Selected sections in logical order
5. **Process citations** (if enabled):
   - Read all `.citations.json` files
   - Assign IEEE numbers [1], [2], etc. in order of appearance
   - Replace citation markers in text
   - Append References section
6. **Convert to output format**:
   - PDF: `pandoc output.md -o output.pdf --toc --pdf-engine=xelatex`
   - DOCX: `pandoc output.md -o output.docx --toc`
   - MD: Keep as-is

## Step 6: Report Completion

After successful generation:

1. **Confirm output location**: Tell user where the report was saved
2. **Summarize contents**: List what sections were included
3. **Note citations**: If citations were processed, mention count
4. **Provide next steps**: Suggest reviewing the output

Example completion message:
```
Report generated successfully!

📄 Output: planning_outputs/20240615_inventory_saas/REPORT.pdf

Included sections:
- Executive Summary
- Market Research & Competitive Analysis
- Architecture & Building Blocks
- Sprint Plan & Timeline
- Cost Analysis & Risk Assessment

Citations: 12 references in IEEE format

The report includes a cover page, table of contents, and numbered sections.
```

## Section Ordering (Default)

When compiling, use this default order unless user specifies otherwise:

1. Cover Page
2. Table of Contents
3. Executive Summary
4. Market Research
5. Competitive Analysis
6. Technical Specifications
7. Architecture Design
8. Building Blocks / Components
9. Implementation Plan / Sprints
10. Feasibility Analysis
11. Cost Analysis
12. Risk Assessment
13. Marketing Campaign (if included)
14. References (if citations enabled)

## Error Handling

| Situation | Response |
|-----------|----------|
| No planning_outputs/ folder | Guide user to run `/full-plan` first |
| Pandoc not installed | Offer Markdown output, provide install instructions |
| LaTeX not installed | Offer DOCX or Markdown, provide install instructions |
| Empty sections selected | Warn user and confirm they want to proceed |
| Citation files missing | Skip citations, note in output |

## Dependencies Check

Before PDF generation, verify:

```bash
# Check Pandoc
pandoc --version || echo "Pandoc not installed"

# Check LaTeX (for PDF)
xelatex --version || echo "LaTeX not installed"
```

If dependencies missing, offer alternatives:
> "PDF generation requires Pandoc and LaTeX. Would you like me to:
> 1. Generate as Word document instead
> 2. Generate as Markdown
> 3. Show installation instructions for Pandoc/LaTeX"

## Example Usage

```
User: /generate-report

Claude: Found planning outputs in: planning_outputs/20240615_143022_inventory_saas/

Available content:
- research/ (5 files)
- specifications/ (3 files)
- components/ (2 files)
- diagrams/ (8 files)
- planning/ (3 files)
- analysis/ (4 files)
- Citations available: Yes (23 sources)

[Presents AskUserQuestion with content, citation, and format options]

User: [Selects options]

Claude: Compiling report with selected options...
[Runs compilation]

Report generated: planning_outputs/20240615_143022_inventory_saas/REPORT.pdf
```
