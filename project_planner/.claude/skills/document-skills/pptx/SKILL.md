---
name: pptx
description: "Presentation toolkit (.pptx). Create/edit slides, layouts, content, speaker notes, comments, for programmatic presentation creation and modification."
allowed-tools: [Read, Write, Bash]
---

# PPTX creation, editing, and analysis

## Overview

A .pptx file is a ZIP archive containing XML files and resources. Create, edit, or analyze PowerPoint presentations using text extraction, raw XML access, or html2pptx workflows. Apply this skill for programmatic presentation creation and modification.

## Visual Enhancement with Project Diagrams

**When creating documents with this skill, always consider adding diagrams to enhance visual communication.**

If your document does not already contain diagrams:
- Use the **project-diagrams** skill to generate AI-powered publication-quality diagrams
- Simply describe your desired diagram in natural language

```bash
python .claude/skills/project-diagrams/scripts/generate_schematic.py "your diagram description" -o figures/output.png
```

**When to add schematics:** Presentation workflow diagrams, slide design process flowcharts, content organization diagrams, system architecture illustrations, process flow visualizations.

---

## Reading and analyzing content

### Text extraction
```bash
python -m markitdown path-to-file.pptx
```

### Raw XML access
Raw XML access is required for: comments, speaker notes, slide layouts, animations, design elements, and complex formatting. Unpack a presentation and read its raw XML contents.

#### Unpacking a file
`python ooxml/scripts/unpack.py <office_file> <output_dir>`

**Note**: The unpack.py script is located at `skills/pptx/ooxml/scripts/unpack.py` relative to the project root. If the script doesn't exist at this path, use `find . -name "unpack.py"` to locate it.

#### Key file structures
* `ppt/presentation.xml` - Main presentation metadata and slide references
* `ppt/slides/slide{N}.xml` - Individual slide contents
* `ppt/notesSlides/notesSlide{N}.xml` - Speaker notes for each slide
* `ppt/comments/modernComment_*.xml` - Comments for specific slides
* `ppt/slideLayouts/` - Layout templates
* `ppt/slideMasters/` - Master slide templates
* `ppt/theme/` - Theme and styling information
* `ppt/media/` - Images and other media files

#### Typography and color extraction
**When given an example design to emulate**: Always analyze the presentation's typography and colors first:
1. **Read theme file**: Check `ppt/theme/theme1.xml` for colors (`<a:clrScheme>`) and fonts (`<a:fontScheme>`)
2. **Sample slide content**: Examine `ppt/slides/slide1.xml` for actual font usage (`<a:rPr>`) and colors
3. **Search for patterns**: Use grep to find color (`<a:solidFill>`, `<a:srgbClr>`) and font references across all XML files

## Creating a new PowerPoint presentation **without a template**

Use the **html2pptx** workflow to convert HTML slides to PowerPoint with accurate positioning.

### Design Principles

**CRITICAL**: Before creating any presentation, analyze the content and choose appropriate design elements:
1. **Consider the subject matter**: What tone, industry, or mood does it suggest?
2. **Check for branding**: If the user mentions a company/organization, consider their brand colors
3. **Match palette to content**: Select colors that reflect the subject
4. **State your approach**: Explain your design choices before writing code

**Requirements**:
- State your content-informed design approach BEFORE writing code
- Use web-safe fonts only: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact
- Create clear visual hierarchy through size, weight, and color
- Ensure readability: strong contrast, appropriately sized text, clean alignment
- Be consistent: repeat patterns, spacing, and visual language across slides

For color palette options (18 curated palettes), visual detail options (geometric patterns, border treatments, typography treatments, chart styling, layout innovations, background treatments), see `references/design_reference.md`.

### Layout Tips
**For slides with charts or tables:**
- **Two-column layout (PREFERRED)**: Header spanning full width, then two columns below - text/bullets in one, featured content in the other. Use flexbox with unequal column widths (e.g., 40%/60%)
- **Full-slide layout**: Let featured content take up entire slide for maximum impact
- **NEVER vertically stack**: Do not place charts/tables below text in a single column

### Workflow
1. **MANDATORY - READ ENTIRE FILE**: Read [`html2pptx.md`](html2pptx.md) completely from start to finish. **NEVER set any range limits when reading this file.**
2. Create an HTML file for each slide with proper dimensions (e.g., 720pt x 405pt for 16:9)
   - Use `<p>`, `<h1>`-`<h6>`, `<ul>`, `<ol>` for all text content
   - Use `class="placeholder"` for chart/table areas
   - **CRITICAL**: Rasterize gradients and icons as PNG images FIRST using Sharp
   - **LAYOUT**: Use full-slide or two-column layout for slides with charts/tables/images
3. Create and run a JavaScript file using [`html2pptx.js`](scripts/html2pptx.js) to convert HTML slides to PowerPoint
4. **Visual validation**: Generate thumbnails and inspect for layout issues
   - Create thumbnail grid: `python .claude/skills/document-skills/pptx/scripts/thumbnail.py output.pptx workspace/thumbnails --cols 4`
   - Check for: text cutoff, text overlap, positioning issues, contrast issues
   - If issues found, adjust HTML and regenerate

## Editing an existing PowerPoint presentation

Work with the raw Office Open XML (OOXML) format: unpack, edit XML, repack.

### Workflow
1. **MANDATORY - READ ENTIRE FILE**: Read [`ooxml.md`](ooxml.md) (~500 lines) completely from start to finish. **NEVER set any range limits when reading this file.**
2. Unpack: `python ooxml/scripts/unpack.py <office_file> <output_dir>`
3. Edit the XML files (primarily `ppt/slides/slide{N}.xml`)
4. **CRITICAL**: Validate after each edit: `python ooxml/scripts/validate.py <dir> --original <file>`
5. Pack: `python ooxml/scripts/pack.py <input_directory> <office_file>`

## Creating a new PowerPoint presentation **using a template**

Duplicate and re-arrange template slides before replacing placeholder content.

### Workflow
1. **Extract template text AND create visual thumbnail grid**:
   * `python -m markitdown template.pptx > template-content.md`
   * Read `template-content.md` completely
   * `python .claude/skills/document-skills/pptx/scripts/thumbnail.py template.pptx`

2. **Analyze template and save inventory**:
   * Review thumbnails for layout patterns, design, visual structure
   * Save `template-inventory.md` with slide index, layout code, and description for every slide
   * **IMPORTANT**: Slides are 0-indexed (first slide = 0)

3. **Create presentation outline**:
   * Match layout structure to actual content (single-column, two-column, three-column as appropriate)
   * Count actual content pieces BEFORE selecting layouts
   * Never use layouts with more placeholders than available content
   * Save `outline.md` with template mapping

4. **Rearrange slides**: `python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52`

5. **Extract text inventory**: `python scripts/inventory.py working.pptx text-inventory.json`
   * Read the entire text-inventory.json file

6. **Generate replacement text** and save to `replacement-text.json`:
   * Verify which shapes exist in inventory before referencing them
   * Shapes without "paragraphs" in replacement JSON are cleared automatically
   * Include paragraph properties (bold, bullet, alignment, font) from original
   * When `bullet: true`, do NOT include bullet symbols in text
   * When `bullet: true`, do NOT set alignment (auto left-aligned)

   ```json
   "paragraphs": [
     {"text": "Title text", "alignment": "CENTER", "bold": true},
     {"text": "Bullet point", "bullet": true, "level": 0},
     {"text": "Regular text"}
   ]
   ```

7. **Apply replacements**: `python scripts/replace.py working.pptx replacement-text.json output.pptx`

## Creating Thumbnail Grids

```bash
python .claude/skills/document-skills/pptx/scripts/thumbnail.py template.pptx [output_prefix]
```

- Default: 5 columns, max 30 slides per grid (5x6)
- Custom columns: `--cols 4` (range: 3-6)
- Grid limits: 3 cols = 12 slides/grid, 4 cols = 20, 5 cols = 30, 6 cols = 42
- Slides are zero-indexed

## Converting Slides to Images

```bash
# Convert PPTX to PDF, then PDF pages to JPEG
soffice --headless --convert-to pdf template.pptx
pdftoppm -jpeg -r 150 template.pdf slide
# Specific range: pdftoppm -jpeg -r 150 -f 2 -l 5 template.pdf slide
```

## Code Style Guidelines
**IMPORTANT**: Write concise code. Avoid verbose variable names, redundant operations, and unnecessary print statements.

## Dependencies

- **markitdown**: `pip install "markitdown[pptx]"` (text extraction)
- **pptxgenjs**: `npm install -g pptxgenjs` (creating presentations)
- **playwright**: `npm install -g playwright` (HTML rendering)
- **react-icons**: `npm install -g react-icons react react-dom` (icons)
- **sharp**: `npm install -g sharp` (SVG rasterization)
- **LibreOffice**: `sudo apt-get install libreoffice` (PDF conversion)
- **Poppler**: `sudo apt-get install poppler-utils` (pdftoppm)
- **defusedxml**: `pip install defusedxml` (secure XML parsing)
