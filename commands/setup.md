---
description: Configure Claude Project Planner - validates API keys and installs all dependencies
---

# Project Planner Setup

Help the user configure the Claude Project Planner plugin for optimal performance.

## Setup Flow

### Step 1: Test and Validate API Keys

First, validate that API keys not only exist, but actually work by making real API calls:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/run-in-env.sh" "${CLAUDE_PLUGIN_ROOT}/scripts/test-providers.py"
```

This will:
- Test each API key with actual API calls (not just existence checks)
- Show which capabilities are available
- Display a capability matrix
- Provide guidance for missing keys

**Expected Output:**
```
Testing API keys...

  ✅  CLAUDE_CODE_OAUTH_TOKEN     Found (Claude Max)
  ✅  OPENROUTER_API_KEY          Valid ($50.00 credits)
  ❌  GEMINI_API_KEY              Not set
  ⬜  PERPLEXITY_API_KEY          Not set

Available Capabilities:
✅  Core Planning (Claude Sonnet)
✅  Fast Research (Perplexity Sonar, ~30 sec)
❌  Deep Research (Gemini Agent, 60 min)
✅  Image Generation (NanoBanana Pro)
✅  Photo Generation (Flux Pro)

Research Modes:
  ✅  Quick - Perplexity only
  ❌  Balanced - Deep Research for Phase 1
  ❌  Comprehensive - Deep Research for all
  ✅  Auto - Use best available
```

### Step 2: Install ALL Dependencies

Install all dependencies from `requirements-full-plan.txt` regardless of which providers are configured. This ensures users can switch providers later without re-running setup:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/run-in-env.sh" "${CLAUDE_PLUGIN_ROOT}/scripts/install-all-dependencies.py"
```

**What gets installed:**
- Core: `claude-agent-sdk`, `requests`, `pyyaml`, `jinja2`, `python-dotenv`
- Research: `openai` (for OpenRouter)
- Documents: `markitdown`, `pillow`, `python-pptx`
- **Gemini: `google-genai>=1.55.0`** ⭐ Now included (required for Deep Research)

**Rationale:** Install everything upfront so users can:
- Switch between Perplexity and Deep Research without reinstalling
- Change image providers (NanoBanana vs Flux) seamlessly
- Try different research modes without dependency issues

**Progress Display:**
```
[1/10] ✓ claude-agent-sdk       (already installed)
[2/10] ✓ python-dotenv          (already installed)
[3/10] ⏳ google-genai           ✅ installed
...
✨ All dependencies installed successfully!
```

### Step 3: Provider Availability Summary

After validation and installation, show what's available:

```bash
echo ""
echo "======================================================================"
echo "  Setup Complete!"
echo "======================================================================"
echo ""
```

Display summary based on test results:

**If GEMINI_API_KEY is available:**
```
✅ Core Planning: Claude Sonnet (via Claude Max)
✅ Research: Perplexity Sonar + Gemini Deep Research
✅ Images: NanoBanana Pro (recommended for diagrams & realistic)
✅ Photos: Flux Pro (ultra-realistic, different prompting)

You can use all research modes:
  • Quick (Perplexity, ~30 sec/query)
  • Balanced (Deep Research Phase 1, Perplexity for others)
  • Comprehensive (Deep Research for all)
  • Auto (context-aware selection)
```

**If only OPENROUTER_API_KEY:**
```
✅ Core Planning: Claude Sonnet (via Claude Max)
✅ Research: Perplexity Sonar (fast, ~30 sec)
⚠️  Deep Research: Unavailable (add GEMINI_API_KEY)
✅ Images: NanoBanana Pro (via OpenRouter)
✅ Photos: Flux Pro (via OpenRouter)

Available research modes:
  • Quick (Perplexity only)
  • Auto (will use Perplexity)
```

### Step 4: Guidance for Missing Capabilities

If GEMINI_API_KEY is missing, provide clear guidance:

```bash
echo "💡 To enable Gemini Deep Research:"
echo ""
echo "1. Get your API key:"
echo "   https://aistudio.google.com/apikey"
echo ""
echo "2. Add to your shell profile (~/.zshrc or ~/.bashrc):"
echo "   export GEMINI_API_KEY='your-key-here'"
echo ""
echo "3. Reload and re-run setup:"
echo "   source ~/.zshrc"
echo "   /project-planner:setup"
echo ""
echo "Cost Options:"
echo "  • Free tier: 20 requests/day"
echo "  • Google Gemini API: Pay-as-you-go (~$2-5/task for Deep Research)"
echo ""
```

### Step 5: Next Steps

Guide the user on what to do next:

```
Ready to use:
  • /full-plan <project-name>   - Complete 6-phase planning
  • /tech-plan <project-name>   - Technical planning only (skip marketing)
  • /research-lookup <query>    - Test research capabilities
  • /generate-report            - Create PDF/DOCX reports

Try it out:
  /research-lookup "Latest trends in AI agents 2025"
```

## Provider Access Matrix

Show users what each key unlocks:

```
┌────────────────────┬─────────────────┬──────────────────────────────┐
│ Capability         │ Access Method   │ Notes                        │
├────────────────────┼─────────────────┼──────────────────────────────┤
│ Deep Research      │ GEMINI_API_KEY  │ ONLY via direct Google API   │
│ (60 min agent)     │                 │ NOT available via OpenRouter │
├────────────────────┼─────────────────┼──────────────────────────────┤
│ Fast Research      │ OPENROUTER_API  │ Perplexity Sonar (~30 sec)   │
│ (Perplexity)       │    OR           │ $5/1M + 5.5% OR fee          │
│                    │ PERPLEXITY_KEY  │ OR $5/1M direct              │
├────────────────────┼─────────────────┼──────────────────────────────┤
│ NanoBanana Pro     │ GEMINI_API_KEY  │ Best for diagrams + realistic│
│ (Images 4K)        │    OR           │ Via Gemini: $2-12/1M tokens  │
│                    │ OPENROUTER_API  │ Via OR: pricing + 5.5% fee   │
├────────────────────┼─────────────────┼──────────────────────────────┤
│ Flux Pro           │ OPENROUTER_API  │ Ultra-realistic photos only  │
│ (Photos)           │                 │ Different prompting style    │
└────────────────────┴─────────────────┴──────────────────────────────┘
```

## Important Notes

### Authentication Priority

The plugin checks for authentication in this order:
1. **CLAUDE_CODE_OAUTH_TOKEN** (preferred) - Claude Max subscribers
2. **ANTHROPIC_API_KEY** - Direct API access

### Deep Research Requirements

**Critical:** Deep Research is ONLY available via direct `GEMINI_API_KEY`:
- ❌ NOT available through OpenRouter
- ✅ Requires Google AI Studio API key
- ✅ Works with free tier or pay-as-you-go API

### Image Generation Defaults

**Default:** NanoBanana Pro
- ✅ Excellent for diagrams, slides, text rendering
- ✅ Also good for realistic images (competitive with Imagen 4)
- ✅ 4K resolution support
- ✅ Thinking capability for complex compositions

**Alternative:** Flux Pro
- Use only for ultra-realistic photos (report covers, presentations)
- Note: Different prompting style than NanoBanana
- Requires OpenRouter API key

### Cost Transparency

Always show users the costs:
- OpenRouter: Provider pricing + 5.5% fee
- Gemini Direct: Provider pricing (no markup)
- Perplexity Direct: $5/1M tokens (no markup)

## Troubleshooting

### "google-genai not installed" Error

If users get this error after running old `/full-plan` before setup:
1. They ran `/full-plan` BEFORE running `/project-planner:setup`
2. Solution: Run `/project-planner:setup` first to install all dependencies

### Invalid API Key

If `test-providers.py` shows "Invalid key":
- Check for typos in environment variable
- Verify key is active (not revoked)
- For Gemini: Ensure you're using AI Studio API key, not consumer app key
- For OpenRouter: Check credits balance

### Connection Failed

If tests show "Connection failed":
- Check internet connection
- Verify firewall/proxy settings
- Try again in a few minutes (temporary API outage)

## Re-running Setup

Users can re-run setup anytime to:
- Add new API keys
- Verify current configuration
- Update dependencies

```bash
/project-planner:setup
```

Dependencies that are already installed will be skipped (fast re-run).
