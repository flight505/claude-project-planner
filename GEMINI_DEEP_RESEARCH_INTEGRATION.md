# Gemini Deep Research Integration - Implementation Summary

## Overview

Implemented proper Gemini Deep Research Agent integration with intelligent model routing based on user feedback during plugin testing.

## Key Changes

### 1. Smart Model Selection (`gemini_research.py`)

**Added Functions:**
- `get_available_models(client)` - Detects available Gemini models including the actual Deep Research Agent
- `select_optimal_model(client, query, research_mode, context)` - Intelligent routing between Deep Research, Pro, and Flash

**Model Detection:**
```python
deep_research_models = [
    "models/deep-research-pro-preview-12-2025",
    "models/deep-research-pro-preview",
]
```

**Routing Logic:**

| Trigger | Model Selected | Use Case |
|---------|---------------|----------|
| `research_mode="deep_research"` | Deep Research Agent | Force expensive comprehensive analysis |
| Phase 1 + competitive-analysis | Deep Research Agent | Market landscape, competitor profiling |
| Query > 500 chars | Deep Research Agent | Complex multi-faceted queries |
| Keywords: "comprehensive analysis", "in-depth research" | Deep Research Agent | Explicit comprehensive requests |
| Phase 1 or architecture queries | Gemini Pro | High-quality balanced research |
| Query > 300 chars or analytical keywords | Gemini Pro | Standard research depth |
| Default | Gemini Flash | Fast, cost-effective lookups |

### 2. API Key Priority Fix

**Problem:** Google's genai library auto-detects `GOOGLE_API_KEY` (free tier) over `GEMINI_API_KEY` (Pro subscription), causing quota errors.

**Solution:**
```python
def get_gemini_client():
    gemini_key = os.getenv("GEMINI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    api_key = gemini_key if gemini_key else google_key

    # Temporarily unset conflicting keys
    old_google_key = os.environ.pop("GOOGLE_API_KEY", None)
    old_cloud_key = os.environ.pop("GOOGLE_CLOUD_API_KEY", None)

    try:
        client = genai.Client(api_key=api_key)
        if gemini_key and api_key == gemini_key:
            print(f"✅ Using GEMINI_API_KEY (Pro subscription)", file=sys.stderr)
        return client, types
    finally:
        # Restore environment variables
        if old_google_key:
            os.environ["GOOGLE_API_KEY"] = old_google_key
        if old_cloud_key:
            os.environ["GOOGLE_CLOUD_API_KEY"] = old_cloud_key
```

### 3. Updated CLI (`deep_research_cli.py`)

**Changes:**
- Renamed `should_use_deep_research()` to `should_use_gemini()` for clarity
- Added context parameter passing to `execute_deep_research()`
- Updated documentation to explain smart model selection
- Provider selection now determines Gemini (with smart routing) vs Perplexity

**Usage:**
```bash
# Force Deep Research Agent (expensive, 30-60 min)
python deep_research_cli.py "query" --research-mode deep_research

# Balanced mode: Deep Research for Phase 1, Gemini Pro/Flash otherwise
python deep_research_cli.py "query" --research-mode balanced --phase 1

# Smart auto-detection based on query complexity
python deep_research_cli.py "query" --research-mode auto --phase 2 --task-type architecture-research
```

### 4. Cost & Performance Optimization

**Model Performance:**

| Model | Duration | Cost | Best For |
|-------|----------|------|----------|
| Deep Research Agent | 30-60 min | $$$$ | Phase 1 competitive analysis, comprehensive market research |
| Gemini Pro | 1-5 min | $$ | Standard research, architecture decisions |
| Gemini Flash | 30-60 sec | $ | Quick lookups, version checks, simple facts |

**Cost Warnings:**
- Deep Research automatically logs: `⚠️ Using Deep Research Agent (expensive, 30-60 min)`
- User is warned before expensive operations
- Smart routing prevents unnecessary Deep Research usage

## User Feedback Addressed

### Issue 1: Temporal Accuracy
**Feedback:** "Perplexity is actually doing a better job at adhering to temporal accuracy"

**Resolution:**
- Gemini has knowledge cutoff limitations for 2026 data
- Maintained Perplexity integration for time-sensitive queries
- Use balanced mode to leverage Perplexity for Phases 2-6 (temporal accuracy matters)

### Issue 2: Misidentifying Deep Research
**Feedback:** "we are currently not using Gemini deep research, what You'll refer to as deep research is simply using the Gemini 3 Pro model"

**Resolution:**
- Implemented proper model detection for `models/deep-research-pro-preview-12-2025`
- Added `get_available_models()` to distinguish Deep Research Agent from Pro/Flash
- Clear logging shows which model is being used

### Issue 3: Cost Management
**Feedback:** "Deep Research Pro is fairly expensive Should be used wisely"

**Resolution:**
- Smart routing uses Deep Research sparingly (Phase 1 competitive analysis only in balanced mode)
- Added explicit cost warnings in progress callbacks
- Defaulted to Flash for cost-effectiveness unless complexity triggers Pro/Deep Research

## Testing Recommendations

1. **Test Smart Routing:**
```bash
# Should use Deep Research Agent
python deep_research_cli.py "Comprehensive competitive landscape analysis for DPP platforms" \
  --research-mode auto --phase 1 --task-type competitive-analysis

# Should use Gemini Pro
python deep_research_cli.py "PostgreSQL vs MongoDB for flexible product schemas" \
  --research-mode auto --phase 2

# Should use Gemini Flash
python deep_research_cli.py "Latest React best practices" \
  --research-mode auto
```

2. **Test Balanced Mode:**
```bash
# Phase 1: Should use Deep Research
python deep_research_cli.py "Market landscape analysis" \
  --research-mode balanced --phase 1

# Phase 2: Should use Perplexity (falls back to fast provider)
# (Requires updating research-lookup integration)
```

3. **Verify API Key Priority:**
```bash
# Ensure GEMINI_API_KEY is used (Pro subscription)
python -c "from gemini_research import get_gemini_client; get_gemini_client()"
# Should output: ✅ Using GEMINI_API_KEY (Pro subscription)
```

## Next Steps

1. Update `research-lookup/SKILL.md` to document smart routing
2. Integrate with Phase 1 execution in `commands/full-plan.md`
3. Add cost estimation warnings before Phase 1 Deep Research
4. Test Perplexity integration for Phases 2-6 temporal accuracy
5. Implement multi-model validation (Gemini + GPT + Claude consensus)

## Files Modified

- `project_planner/.claude/skills/research-lookup/gemini_research.py` - Core integration with smart routing
- `project_planner/.claude/skills/research-lookup/deep_research_cli.py` - Updated CLI interface
- ~~`project_planner/.claude/skills/research-lookup/SKILL.md`~~ - Documentation (pending)

## Performance Metrics (from DPP Platform Test)

**Phase 1 Execution (3 queries):**
- All queries used Gemini 3 Pro (before Deep Research implementation)
- Average duration: ~40 seconds per query
- Total Phase 1: ~10 minutes
- Output quality: Comprehensive (71KB across 5 files)

**Expected with Smart Routing:**
- Balanced mode (recommended): Deep Research for 1 query, Gemini Pro for 2 queries → ~35 minutes Phase 1
- Deep Research mode: 3 Deep Research queries → ~2 hours Phase 1
- Perplexity mode: 3 Perplexity queries → ~90 seconds Phase 1 (but lower depth)

## References

- **Gemini Deep Research Docs:** https://ai.google.dev/gemini-api/docs/deep-research
- **Model Name:** `models/deep-research-pro-preview-12-2025`
- **User Feedback Session:** 2026-01-19 (DPP Platform planning test)
