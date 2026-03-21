---
name: research-lookup
description: "Multi-provider research lookup supporting Gemini Deep Research (60-min comprehensive analysis) and Perplexity Sonar (fast web-grounded research). Intelligently routes between providers based on research mode and query complexity. Supports balanced mode for optimal quality/time tradeoff."
allowed-tools: [Read, Write, Edit, Bash]
effort: max
---

# Research Information Lookup

## Overview

This skill provides **multi-provider research lookup** with intelligent routing between:

- **Gemini Deep Research**: 60-minute comprehensive research with extensive citations (requires GEMINI_API_KEY + pay-as-you-go API)
- **Perplexity Sonar**: Fast web-grounded research in 30 seconds (requires OPENROUTER_API_KEY)

The skill automatically selects the best provider and model based on:
- **Research mode** configuration (balanced, perplexity, deep_research, auto)
- **Query complexity** (keywords, length, structure)
- **Context** (planning phase, task type)

## Research Modes

| Mode | Provider Selection | Best For | Total Plan Time |
|------|-------------------|----------|-----------------|
| `balanced` | Deep Research for Phase 1 analysis, Perplexity for others | Most projects (recommended) | ~90 min |
| `perplexity` | Always use Perplexity | Quick planning, well-known tech | ~30 min |
| `deep_research` | Always use Gemini Deep Research | Novel domains, high-stakes | ~4 hours |
| `auto` | Automatic based on keywords/context | Let the system decide | Varies |

## Deep Research Budget Constraints

**CRITICAL: You have a strict budget of 2 Deep Research queries per `/full-plan` session.**

### Budget Allocation Strategy

**Deep Research is expensive (30-60 min per query, high API cost). Use it ONLY for:**

1. **Phase 1: Competitive Landscape/Analysis** (Highest Priority)
   - Comprehensive market analysis with multiple competitors
   - Industry trends and adoption patterns
   - Regulatory landscape with complex timelines

2. **Phase 2: Novel Architecture Decisions** (Use Sparingly)
   - ONLY if technology stack is highly uncertain or cutting-edge
   - DEFAULT to Gemini Pro or Perplexity for standard tech stack research

### DO NOT Use Deep Research For:
- Version checks or feature comparisons (use Perplexity)
- Pricing lookups or cost estimates (use Perplexity)
- Quick technical documentation (use Perplexity)
- Simple "what is X" queries (use Gemini Flash/Perplexity)
- Phases 3-6 research (use Perplexity - better temporal accuracy)

### Budget Tracking

The system automatically tracks usage in `planning_outputs/<project>/DEEP_RESEARCH_BUDGET.json`. Falls back to Gemini Pro if budget exhausted.

**Before using Deep Research, ask:** Is this critical to project viability? Does it require 30-60 min multi-source analysis? Can Perplexity provide sufficient depth?

**Remember: Perplexity has better temporal accuracy for 2026 data, so prefer it for time-sensitive queries even in Phase 1.**

## When to Use This Skill

- **Current Research Information**: Latest studies, papers, and findings
- **Literature Verification**: Check facts, statistics, or claims
- **Background Research**: Context and supporting evidence for planning
- **Citation Sources**: Find relevant papers and studies to cite
- **Technical Documentation**: Specifications, protocols, methodologies
- **Recent Developments**: Emerging trends and breakthroughs
- **Statistical Data**: Survey results, research findings

## Visual Enhancement with Project Diagrams

**When creating documents with this skill, always consider adding diagrams to enhance visual communication.**

Use the **project-diagrams** skill for system architecture, data flow, integration workflow, and process pipeline diagrams:

```bash
python .claude/skills/project-diagrams/scripts/generate_schematic.py "your diagram description" -o figures/output.png
```

---

## Usage

### Command-Line Interface

```bash
# Basic usage with auto mode (context-aware selection)
python research_lookup.py "Your research query here"

# Specify research mode explicitly
python research_lookup.py "Competitive landscape for SaaS market" \
  --research-mode deep_research

# Provide context for smart routing
python research_lookup.py "Latest PostgreSQL features" \
  --research-mode balanced \
  --phase 2 \
  --task-type architecture-research

# Force specific Perplexity model
python research_lookup.py "Quick fact check" \
  --research-mode perplexity \
  --force-model pro

# Save output to file / JSON format
python research_lookup.py "your query" -o results.txt
python research_lookup.py "your query" --json -o results.json
```

### API Requirements

**For Perplexity (required for perplexity and balanced modes):**
```bash
export OPENROUTER_API_KEY='your_openrouter_key'
```

**For Gemini Deep Research (required for deep_research and balanced modes):**
```bash
export GEMINI_API_KEY='your_gemini_key'
# Requires pay-as-you-go API ($19.99/month)
```

---

## Progress Tracking & Monitoring (v1.4.0+)

**For long-running Deep Research operations (60+ minutes)**, comprehensive progress tracking and checkpoint capabilities are available.

### Monitor Active Research

```bash
# List all active research operations
python scripts/monitor-research-progress.py <project_folder> --list

# Monitor specific operation with live updates
python scripts/monitor-research-progress.py <project_folder> <task_id> --follow
```

### Resume Interrupted Research

If Deep Research is interrupted (network issues, timeout), resume from checkpoints:

```bash
# List resumable tasks with time estimates
python scripts/resume-research.py <project_folder> 1 --list

# Resume from checkpoint (saves up to 50 minutes)
python scripts/resume-research.py <project_folder> 1 --task <task_name>
```

**Checkpoint Strategy:** 15% (~9 min saved), 30% (~18 min saved), 50% (~30 min saved).

**Key Features:** Automatic checkpoints at milestones, graceful degradation (Deep Research to Perplexity fallback), error recovery with exponential backoff, external monitoring support.

**See Also:** `docs/WORKFLOWS.md`, `scripts/enhanced_research_integration.py`, `scripts/resumable_research.py`

---

## Automatic Model Selection

### Model Types

| Model | Use Case | Context | Pricing | Speed |
|-------|----------|---------|---------|-------|
| **Sonar Pro** (`perplexity/sonar-pro`) | Straightforward lookup | 200K tokens | $3/1M prompt + $15/1M completion + $5/1K searches | Fast (5-15s) |
| **Sonar Reasoning Pro** (`perplexity/sonar-reasoning-pro`) | Complex analytical queries | 128K tokens | $2/1M prompt + $8/1M completion + $5/1K searches | Slower (15-45s) |

### Complexity Assessment

**Reasoning Keywords** (triggers Sonar Reasoning Pro):
- Analytical: `compare`, `contrast`, `analyze`, `evaluate`, `critique`
- Comparative: `versus`, `vs`, `compared to`, `differences between`
- Synthesis: `meta-analysis`, `systematic review`, `synthesis`
- Causal: `mechanism`, `why`, `how does`, `explain`, `relationship`
- Debate: `controversy`, `conflicting`, `paradox`, `debate`
- Trade-offs: `pros and cons`, `advantages and disadvantages`, `trade-off`

**Scoring:** Reasoning keywords = 3 pts each; Multiple questions = 2 pts per `?`; Complex clauses = 1.5 pts; Long queries (>150 chars) = 1 pt. Threshold: >= 3 pts triggers Reasoning Pro.

**Example Classifications:**

Sonar Pro Search (straightforward):
- "Recent advances in CRISPR gene editing 2024"
- "Prevalence of diabetes in US population"

Sonar Reasoning Pro (complex):
- "Compare and contrast mRNA vaccines vs traditional vaccines for cancer treatment"
- "Analyze the controversy surrounding AI in medical diagnosis and evaluate trade-offs"

### Manual Override

```bash
python research_lookup.py "your query" --force-model pro       # Force Sonar Pro
python research_lookup.py "your query" --force-model reasoning  # Force Reasoning Pro
```

---

## Query Best Practices

### Structured Query Format

```
[Topic] + [Specific Aspect] + [Time Frame] + [Type of Information]
```

**Good Queries:**
- "CRISPR gene editing + off-target effects + 2024 + clinical trials"
- "Quantum computing + error correction + recent advances + review papers"
- "Renewable energy + solar efficiency + 2023-2024 + statistical data"

**Poor Queries:** "Tell me about AI" (too broad), "Cancer research" (lacks specificity)

For detailed query examples, capability descriptions, and paper quality standards, see `references/query_guide.md`.

## Integration with Project Planning

1. **Technology Research**: Current information on frameworks, tools, best practices
2. **Architecture Validation**: Verify patterns against current standards
3. **Competitive Analysis**: Compare solutions with similar projects
4. **Decision Support**: Inform architectural decisions with latest evidence
5. **Cost Research**: Pricing and service comparisons

## Error Handling and Limitations

**Known Limitations:** Information cutoff, paywall content, very recent unindexed papers, proprietary databases.

**Fallback Strategies:** Rephrase queries, break complex queries into simpler components, use broader time frames, cross-reference with multiple variations.

For provider-specific technical details, API configuration, performance/cost considerations, and complementary tool guidance, see `references/provider_details.md`.

---

## Summary

This skill serves as a powerful research assistant with intelligent dual-model selection:

- **Automatic Intelligence**: Analyzes query complexity and selects the optimal model
- **Cost-Effective**: Uses faster Sonar Pro Search for straightforward lookups
- **Deep Analysis**: Engages Sonar Reasoning Pro for complex analytical queries
- **Flexible Control**: Manual override available when needed
- **Academic Focus**: Both models configured to prioritize peer-reviewed sources
- **Complementary WebSearch**: Use alongside WebSearch for metadata verification and non-academic sources
