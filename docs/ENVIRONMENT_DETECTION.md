# Environment Detection - Smart Python Execution

## Overview

The Claude Project Planner supports **both pip and uv** with automatic detection and preference ordering.

## How It Works

### Installation (`install-all-dependencies.py`)

The installation script already has smart detection:

```python
def has_uv() -> bool:
    """Check if uv is available on the system."""
    return shutil.which("uv") is not None

# In main():
use_uv = has_uv()
if use_uv:
    cmd = ["uv", "pip", "install", package]
else:
    cmd = [sys.executable, "-m", "pip", "install", package]
```

**Priority:**
1. ✅ If `uv` is available → use `uv pip install` (faster)
2. ✅ If `uv` is not available → use `pip install` (fallback)

### Execution (`run-in-env.sh`)

The execution wrapper ensures scripts run in the correct environment:

```bash
# scripts/run-in-env.sh

if command -v uv &> /dev/null; then
    # Use uv run to execute in project's virtual environment
    exec uv run python "$@"
elif [ -f ".venv/bin/python" ]; then
    # Use project's venv directly
    exec .venv/bin/python "$@"
else
    # Fall back to system Python
    exec python3 "$@"
fi
```

**Priority:**
1. ✅ If `uv` is available → use `uv run python` (uses project's .venv)
2. ✅ If `.venv/bin/python` exists → use `.venv/bin/python` (direct venv)
3. ✅ Otherwise → use `python3` (system Python)

## Why This Matters

### The Problem (Before)

```bash
# Setup command called:
python scripts/test-providers.py  # Used system Python (3.14.2)

# But dependencies installed to:
.venv/bin/python3  # Project venv (3.12.8)

# Result: "ModuleNotFoundError: No module named 'requests'"
```

### The Solution (After)

```bash
# Setup command now calls:
./scripts/run-in-env.sh scripts/test-providers.py

# Smart wrapper detects environment:
# - If uv available: runs "uv run python scripts/test-providers.py"
# - Uses project's .venv (3.12.8) where packages are installed
# - Result: ✅ All modules found!
```

## Usage Examples

### Running Tests

```bash
# Old way (would fail):
python scripts/test-providers.py

# New way (always works):
./scripts/run-in-env.sh scripts/test-providers.py
```

### Running Install

```bash
# Old way (environment mismatch):
python scripts/install-all-dependencies.py

# New way (consistent environment):
./scripts/run-in-env.sh scripts/install-all-dependencies.py
```

### From Setup Command

The `/project-planner:setup` command now uses the wrapper automatically:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/run-in-env.sh" "${CLAUDE_PLUGIN_ROOT}/scripts/test-providers.py"
"${CLAUDE_PLUGIN_ROOT}/scripts/run-in-env.sh" "${CLAUDE_PLUGIN_ROOT}/scripts/install-all-dependencies.py"
```

## Environment Detection Matrix

| Scenario | Detection Result | Command Used |
|----------|-----------------|--------------|
| uv installed | ✅ Use uv | `uv run python` |
| .venv exists | ✅ Use venv | `.venv/bin/python3` |
| Neither | ✅ Use system | `python3` |

## Testing

Verify which Python is being used:

```bash
# Check wrapper's Python
./scripts/run-in-env.sh -c "import sys; print(sys.executable)"

# Expected with uv:
# /path/to/project/.venv/bin/python3

# Check install script's detection
./scripts/run-in-env.sh scripts/install-all-dependencies.py --verbose

# Expected:
# ✨ Using uv for faster installation (if uv available)
# 📦 Using pip for installation (if uv not available)
```

## Benefits

1. **Consistent Environment**: Scripts always run in the same environment where packages are installed
2. **Auto-Detection**: No manual configuration needed
3. **Graceful Fallback**: Works with uv, pip, or system Python
4. **Fast by Default**: Prefers uv for speed when available
5. **Universal Compatibility**: Works on macOS, Linux, and Windows (with bash)

## Troubleshooting

### "ModuleNotFoundError" After Installation

This means the script ran in a different Python environment than where packages were installed.

**Fix:** Use the wrapper:
```bash
./scripts/run-in-env.sh scripts/your-script.py
```

### "Permission Denied" Running Wrapper

Make the wrapper executable:
```bash
chmod +x scripts/run-in-env.sh
```

### Wrapper Not Found

Ensure you're in the project root:
```bash
cd /path/to/claude-project-planner
./scripts/run-in-env.sh scripts/test-providers.py
```

## Implementation Details

### Why Not Just Change Shebang?

We considered changing scripts to use:
```python
#!/usr/bin/env python
```

But this doesn't solve the problem because:
- `#!/usr/bin/env python` still uses system Python
- Doesn't detect uv vs pip automatically
- No fallback logic

The wrapper provides:
- ✅ Environment detection
- ✅ Tool detection (uv vs pip)
- ✅ Graceful fallbacks
- ✅ Consistent behavior

### Why Bash Script?

- Fast (no Python startup overhead)
- Universal (works everywhere bash exists)
- Simple (easy to audit and understand)
- Portable (no dependencies)

## Related Files

- `scripts/run-in-env.sh` - Smart Python executor
- `scripts/install-all-dependencies.py` - Dependency installer (has uv/pip detection)
- `scripts/test-providers.py` - API key validator
- `commands/setup.md` - Setup command (uses wrapper)
- `requirements-full-plan.txt` - Package list
- `pyproject.toml` - Project configuration (compatible with both pip and uv)
