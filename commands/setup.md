---
name: setup
description: Configure Claude Project Planner - detects existing API keys or guides you through setup
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
---

# Project Planner Setup

Help the user configure the Claude Project Planner plugin for their environment.

## Setup Flow

### Step 1: Detect Existing Environment Variables

First, check what API keys are already available in the user's environment:

```bash
# Check for existing keys (don't print values, just check existence)
echo "=== Checking Environment Variables ==="
[ -n "$CLAUDE_CODE_OAUTH_TOKEN" ] && echo "✅ CLAUDE_CODE_OAUTH_TOKEN: Found (Claude Max)" || echo "⬜ CLAUDE_CODE_OAUTH_TOKEN: Not set"
[ -n "$ANTHROPIC_API_KEY" ] && echo "✅ ANTHROPIC_API_KEY: Found" || echo "⬜ ANTHROPIC_API_KEY: Not set"
[ -n "$OPENROUTER_API_KEY" ] && echo "✅ OPENROUTER_API_KEY: Found" || echo "⬜ OPENROUTER_API_KEY: Not set"
[ -n "$PERPLEXITY_API_KEY" ] && echo "✅ PERPLEXITY_API_KEY: Found" || echo "⬜ PERPLEXITY_API_KEY: Not set"
```

### Step 2: Explain Authentication

**For Claude Code CLI:**
- `CLAUDE_CODE_OAUTH_TOKEN` is **preferred** (Claude Max subscribers - automatic via browser login)
- `ANTHROPIC_API_KEY` is the alternative (direct API access)
- If using Claude Max, no API key configuration needed - just run `claude` and authenticate

**For Plugin Features (research, diagrams, images):**
- `OPENROUTER_API_KEY` enables research-lookup, project-diagrams, and generate-image skills
- Get a key at: https://openrouter.ai/keys
- This provides access to Perplexity Sonar models for research

### Step 3: If Keys Are Found

If `OPENROUTER_API_KEY` is already set in the environment, confirm with the user:

"I detected `OPENROUTER_API_KEY` in your environment. This means the research and AI features are ready to use!

Would you like me to:
1. **Use existing environment variables** (recommended if you have keys in ~/.zshrc)
2. **Create a project-local config** (stores in .claude/project-planner.local.md)"

Most developers export keys in their shell profile (~/.zshrc, ~/.bashrc) - this is the recommended approach as it works across all projects.

### Step 4: If Keys Are Missing

If `OPENROUTER_API_KEY` is not found, guide the user:

"The research-lookup skill requires an OpenRouter API key for AI-powered research.

**To set up:**

1. Get your API key at: https://openrouter.ai/keys

2. Add to your shell profile (~/.zshrc or ~/.bashrc):
   ```bash
   export OPENROUTER_API_KEY='sk-or-v1-your-key-here'
   ```

3. Reload your shell:
   ```bash
   source ~/.zshrc
   ```

Or, if you prefer project-local configuration, I can store it in `.claude/project-planner.local.md` (gitignored)."

### Step 5: Offer to Create Local Config (Optional)

If the user wants project-local config, create `.claude/project-planner.local.md`:

```markdown
---
# Project Planner Configuration
# This file is gitignored - safe for API keys

# OpenRouter API Key (for research-lookup, project-diagrams, generate-image)
openrouter_api_key: "USER_PROVIDED_KEY"

# Optional: Force specific research model
# research_model: "pro"  # or "reasoning"
---

# Project Planner Local Configuration

This file contains project-specific configuration for Claude Project Planner.
It is automatically gitignored and safe for storing API keys.

## Configured Features

- Research Lookup: Enabled (via OpenRouter → Perplexity Sonar)
- Project Diagrams: Enabled (via OpenRouter → Nano Banana Pro)
- Image Generation: Enabled (via OpenRouter → FLUX/Gemini)
```

### Step 6: Validate Configuration

After setup, test that the keys work:

```bash
# Quick validation - just check the key format
if [ -n "$OPENROUTER_API_KEY" ]; then
    if [[ "$OPENROUTER_API_KEY" == sk-or-* ]]; then
        echo "✅ OPENROUTER_API_KEY format looks valid"
    else
        echo "⚠️ OPENROUTER_API_KEY doesn't match expected format (sk-or-...)"
    fi
fi
```

### Step 7: Summary

Provide a summary of the configuration:

"## Setup Complete!

**Claude Code Authentication:**
- Using: [CLAUDE_CODE_OAUTH_TOKEN / ANTHROPIC_API_KEY / Browser OAuth]

**Plugin Features:**
- Research Lookup: [✅ Ready / ❌ Needs OPENROUTER_API_KEY]
- Project Diagrams: [✅ Ready / ❌ Needs OPENROUTER_API_KEY]
- Image Generation: [✅ Ready / ❌ Needs OPENROUTER_API_KEY]

**Configuration Source:** [Environment variables (~/.zshrc) / Project-local (.claude/project-planner.local.md)]

You're all set! Try `/research-lookup` to test the research feature."

## Key Points

- **Prefer environment variables** over project-local config (works everywhere)
- **CLAUDE_CODE_OAUTH_TOKEN preferred** over ANTHROPIC_API_KEY for Claude Max users
- **Don't store keys in git** - use .local.md files which are gitignored
- **Validate key format** before saving
- **Be helpful** - provide direct links and copy-paste commands
