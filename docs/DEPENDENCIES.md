# Dependency Management (v1.3.2+)

This document describes the streamlined dependency management system introduced in v1.3.2.

## Quick Start

```bash
# Run setup once to install all dependencies
/project-planner:setup
```

This single command:
1. **Validates API keys** with real API calls (not just existence checks)
2. **Installs ALL dependencies** synchronously with progress display
3. **Shows capability matrix** based on your available API keys
4. **Configures environment** for optimal performance

## What Gets Installed

The setup installs **all dependencies upfront**, regardless of which providers you have configured. This allows you to switch providers later without re-running setup.

### Core Dependencies
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests
- `pyyaml` - YAML parsing for building blocks
- `jinja2` - Template rendering

### Research Providers
- `openai` - OpenRouter API client (for Perplexity Sonar)
- `google-genai>=1.55.0` - Gemini Deep Research & NanoBanana Pro

### Document Processing
- `markitdown` - Document conversion (PDF, DOCX, PPTX → Markdown)
- `pillow` - Image processing
- `python-pptx` - PowerPoint generation

## Provider Access

| Capability | Required Key | Notes |
|------------|-------------|-------|
| **Deep Research** | `GEMINI_API_KEY` | 60-min autonomous research. **ONLY** via direct Gemini API (NOT OpenRouter) |
| **Fast Research** | `OPENROUTER_API_KEY` or `PERPLEXITY_API_KEY` | Perplexity Sonar (~30 sec/query) |
| **NanoBanana Pro** | `GEMINI_API_KEY` or `OPENROUTER_API_KEY` | Image generation (diagrams + realistic) |
| **Flux Pro** | `OPENROUTER_API_KEY` | Ultra-realistic photos only |
| **Core Planning** | `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` | Required for all operations |

## Setup Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User runs: /project-planner:setup                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Validate API Keys (test-providers.py)              │
│  • Makes REAL API calls to test each key                    │
│  • Tests: CLAUDE_CODE_OAUTH_TOKEN, OPENROUTER_API_KEY,     │
│           GEMINI_API_KEY, PERPLEXITY_API_KEY, etc.         │
│  • Returns capability matrix                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Install ALL Dependencies                           │
│  (install-all-dependencies.py)                              │
│  • Synchronous installation with progress                   │
│  • [1/10] ✓ python-dotenv (already installed)              │
│  • [2/10] ⏳ google-genai ... ✅ installed                  │
│  • ...installs everything regardless of user choice         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Display Capability Summary                         │
│  ✅ Core Planning (Claude Sonnet)                           │
│  ✅ Fast Research (Perplexity Sonar, ~30 sec)               │
│  ❌ Deep Research (Gemini Agent, 60 min) - add key          │
│  ✅ Image Generation (NanoBanana Pro)                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Ready to use: /full-plan, /tech-plan, etc.                │
└─────────────────────────────────────────────────────────────┘
```

## Dynamic UI Filtering

When you run `/full-plan` or `/tech-plan`, the interactive setup UI shows options based on your **available API keys**:

**With GEMINI_API_KEY + OPENROUTER_API_KEY:**
```
AI Provider:
  ✅ Google Gemini Deep Research (Available)
  ✅ Perplexity via OpenRouter (Available)
  ✅ Auto-detect from available keys

Research Depth:
  ✅ Balanced - Deep Research for Phase 1, Perplexity for others (Recommended)
  ✅ Quick - Perplexity only
  ✅ Comprehensive - Deep Research for all
```

**With only OPENROUTER_API_KEY:**
```
AI Provider:
  ❌ Google Gemini Deep Research (Unavailable - Requires GEMINI_API_KEY)
  ✅ Perplexity via OpenRouter (Available)
  ✅ Auto-detect from available keys

Research Depth:
  ❌ Balanced (Requires Gemini)
  ✅ Quick - Perplexity only
  ❌ Comprehensive (Requires Gemini)
```

This dynamic filtering ensures users only see options they can actually use.

## Troubleshooting

### "google-genai not installed" error

**Cause**: You ran `/full-plan` or `/tech-plan` before running setup.

**Solution**:
```bash
/project-planner:setup
```

### "Invalid API key" during setup

**Cause**: API key exists but doesn't work.

**Solutions**:
1. Check for typos in your `~/.zshrc` or `~/.bashrc`
2. Verify the key hasn't been revoked
3. For Gemini: Ensure you're using AI Studio API key (not consumer app key)
4. For OpenRouter: Check your credits balance

### Re-running Setup

You can re-run setup anytime to:
- Add new API keys
- Verify current configuration
- Update dependencies

```bash
/project-planner:setup
```

Already-installed dependencies are skipped automatically (fast re-run).

## Migration from v1.3.1

**Old flow (background installation):**
```bash
# SessionStart hook automatically ran in background
nohup ensure-dependencies.sh full &
# Later waited for completion
python wait-for-dependencies.py
```

**New flow (user-initiated):**
```bash
# User explicitly runs setup first
/project-planner:setup
# Then uses any command
/full-plan
```

**Benefits:**
- ✅ User control and visibility
- ✅ Real API key validation
- ✅ Dynamic UI based on available keys
- ✅ Install all deps upfront (switch providers later without reinstall)
- ✅ No hidden background processes

## See Also

- **Setup Command**: `commands/setup.md`
- **API Key Testing**: `scripts/test-providers.py`
- **Installation Script**: `scripts/install-all-dependencies.py`
- **Old System** (archived): `docs/deprecated/DEPENDENCIES-old.md`
