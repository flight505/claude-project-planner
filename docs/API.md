# Claude Project Planner API

**Version:** 1.4.0-alpha

Complete reference for the Claude Project Planner programmatic API. This API enables you to generate comprehensive software project plans including architecture documents, sprint plans, cost analyses, and implementation roadmaps—all backed by real-time research.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core API](#core-api)
- [Progress Tracking API](#progress-tracking-api-v140-alpha)
- [Research Integration](#research-integration)
- [Data Models](#data-models)
- [Best Practices](#best-practices)

---

## Installation

```bash
# Install with uv (recommended)
uv sync

# Or install in your current environment
uv pip install -e .

# Install optional dependencies
uv pip install -e ".[all]"  # All features
uv pip install -e ".[gemini]"  # Gemini Deep Research
uv pip install -e ".[documents]"  # PDF/DOCX support
```

---

## Quick Start

### Basic Usage

```python
import asyncio
from pathlib import Path

# Import the main planning function
# (Note: Programmatic API is under development for v1.4.0)
# Current usage is primarily via CLI commands

# CLI Usage (recommended):
# /full-plan my-project
# /tech-plan my-project
```

### Using CLI Tools

```python
import subprocess

# Run full planning via CLI
result = subprocess.run(
    ["claude", "run", "/full-plan", "my-saas-project"],
    capture_output=True,
    text=True
)

# Monitor research progress
result = subprocess.run(
    ["python", "scripts/monitor-research-progress.py",
     "planning_outputs/20260115_my-project", "--list"],
    capture_output=True,
    text=True
)
print(result.stdout)
```

---

## Progress Tracking API (v1.4.0-alpha)

The progress tracking system provides comprehensive monitoring and checkpoint capabilities for long-running research operations.

### EnhancedResearchLookup

Integrates progress tracking with the research lookup system.

```python
import asyncio
from pathlib import Path
from scripts.enhanced_research_integration import EnhancedResearchLookup

async def main():
    # Initialize with progress tracking
    research = EnhancedResearchLookup(
        project_folder=Path("planning_outputs/20260115_my-project"),
        phase_num=1,
        research_mode="balanced"  # or "quick", "deep_research", "auto"
    )

    # Execute research with automatic progress tracking
    result = await research.research_with_progress(
        task_name="competitive-analysis",
        query="Comprehensive competitive landscape analysis for SaaS market",
        estimated_duration_sec=3600  # Optional, auto-detected if not provided
    )

    # Access results
    print(f"Success: {result['success']}")
    print(f"Provider: {result['provider']}")
    print(f"Sources: {len(result.get('sources', []))}")

    # View execution statistics
    stats = research.get_stats()
    print(f"Tasks completed: {stats['tasks_completed']}")
    print(f"Tasks resumed: {stats['tasks_resumed']}")
    print(f"Time saved: {stats['total_time_saved_min']} minutes")

asyncio.run(main())
```

**Key Features:**
- Automatic checkpoint creation at 15%, 30%, 50% milestones
- Graceful degradation (Deep Research → Perplexity fallback)
- Error recovery with exponential backoff
- External monitoring support via progress files
- Statistics tracking across all research operations

### ResumableResearchExecutor

Core executor for resumable research operations with full checkpoint support.

```python
import asyncio
from pathlib import Path
from scripts.resumable_research import ResumableResearchExecutor

async def main():
    # Initialize executor
    executor = ResumableResearchExecutor(
        project_folder=Path("planning_outputs/20260115_my-project"),
        phase_num=1,
        auto_resume=True  # Automatically resume from checkpoints if available
    )

    # Define research function
    async def my_research_func():
        # Your research logic here
        return {"findings": "...", "sources": [...]}

    # Execute with full progress tracking
    result = await executor.execute(
        task_name="market-research",
        query="Market size and growth projections",
        provider="perplexity_sonar",  # or "gemini_deep_research"
        estimated_duration_sec=30,
        research_func=my_research_func,
        fallback_func=None  # Optional fallback function
    )

    # Check execution results
    if result["success"]:
        print(f"Research completed: {result['result']}")
        print(f"Time saved: {result['metadata']['time_saved_min']} minutes")
    else:
        print(f"Research failed: {result['error']}")

    # Get statistics
    stats = executor.get_stats()
    print(f"Total tasks: {stats['tasks_executed']}")
    print(f"Resumed: {stats['tasks_resumed']}")
    print(f"Failed: {stats['tasks_failed']}")

asyncio.run(main())
```

### ResearchProgressTracker

Low-level progress tracking for custom integrations.

```python
import asyncio
from pathlib import Path
from scripts.research_progress_tracker import ResearchProgressTracker

async def main():
    # Initialize tracker
    tracker = ResearchProgressTracker(
        project_folder=Path("planning_outputs/20260115_my-project"),
        task_id="custom-research-001"
    )

    # Start tracking
    await tracker.start(
        query="Custom research query",
        provider="custom_provider",
        estimated_duration_sec=600
    )

    # Update progress
    await tracker.update(
        phase="analyzing",
        current_action="Processing data...",
        progress_pct=30.0
    )

    # Add checkpoint
    await tracker.checkpoint(
        phase="analyzing",
        progress_pct=30.0,
        partial_results={"findings": ["Finding 1", "Finding 2"]}
    )

    # Complete or fail
    await tracker.complete(results={"final": "results"})
    # OR
    # await tracker.fail(error="Error message", error_type="rate_limit")

    # Read progress (from another process)
    progress = tracker.read_progress()
    print(f"Status: {progress['status']}")
    print(f"Progress: {progress['progress_pct']}%")

asyncio.run(main())
```

### ResearchCheckpointManager

Manage research checkpoints for resume capability.

```python
from pathlib import Path
from scripts.research_checkpoint_manager import ResearchCheckpointManager

# Initialize manager
manager = ResearchCheckpointManager(
    project_folder=Path("planning_outputs/20260115_my-project"),
    phase_num=1
)

# Save checkpoint
manager.save_research_checkpoint(
    task_name="competitive-analysis",
    query="Original query",
    partial_results={"findings": [...]},
    sources_collected=[...],
    progress_pct=30.0,
    resumable=True
)

# Load checkpoint
checkpoint = manager.load_research_checkpoint("competitive-analysis")
if checkpoint:
    print(f"Progress: {checkpoint['progress_pct']}%")
    print(f"Resumable: {checkpoint['resumable']}")

# Build resume prompt
resume_prompt = manager.build_resume_prompt("competitive-analysis", checkpoint)
print(resume_prompt)  # Prompt for AI to continue research

# Get time estimates
estimate = manager.get_resume_estimate(checkpoint)
print(f"Time saved: {estimate['time_saved_min']} minutes")
print(f"Time remaining: {estimate['time_remaining_min']} minutes")

# Delete checkpoint after successful completion
manager.delete_checkpoint("competitive-analysis")
```

---

## Research Integration

### Using Research Lookup with Progress Tracking

```python
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from research_lookup import ResearchLookup

# Basic usage (without progress tracking)
lookup = ResearchLookup(
    research_mode="balanced",
    force_model=None,
    context={"phase": 1, "task_type": "competitive-analysis"}
)

# Sync research
result = lookup.lookup("Market trends for SaaS in 2026")

# Async research (for Deep Research)
result = await lookup.lookup_async("Comprehensive competitive landscape")

print(f"Provider: {result['provider']}")
print(f"Content: {result['content']}")
print(f"Sources: {result.get('sources', [])}")
```

---

## Data Models

### Progress Update

```python
{
    "task_id": str,
    "status": str,  # "running", "completed", "failed"
    "progress_pct": float,  # 0.0 to 100.0
    "phase": str,
    "current_action": str,
    "started_at": str,  # ISO timestamp
    "updated_at": str,  # ISO timestamp
    "estimated_completion_at": str,  # ISO timestamp
    "checkpoints": List[Dict],
    "metadata": Dict[str, Any]
}
```

### Research Checkpoint

```python
{
    "task_name": str,
    "query": str,
    "created_at": str,  # ISO timestamp
    "progress_pct": float,
    "resumable": bool,
    "partial_results": Dict[str, Any],
    "sources_collected": List[Dict],
    "metadata": {
        "phase": str,
        "estimated_total_duration_sec": int,
        "time_elapsed_sec": float,
        "source_count": int
    }
}
```

### Research Result

```python
{
    "success": bool,
    "provider": str,  # "perplexity_sonar", "gemini_deep_research"
    "content": str,
    "sources": List[Dict],
    "result": Any,  # Full result data
    "error": Optional[str],
    "metadata": {
        "resumed": bool,
        "checkpoint_used": Optional[str],
        "time_saved_min": float,
        "retries": int
    }
}
```

### Executor Statistics

```python
{
    "tasks_executed": int,
    "tasks_completed": int,
    "tasks_failed": int,
    "tasks_resumed": int,
    "total_time_saved_min": float
}
```

---

## Best Practices

### 1. Use Enhanced Research Integration

For new code, always use `EnhancedResearchLookup` instead of direct `ResearchLookup`:

```python
# ✅ Good - includes progress tracking and checkpoints
from scripts.enhanced_research_integration import EnhancedResearchLookup
research = EnhancedResearchLookup(...)

# ❌ Avoid - no progress tracking
from scripts.research_lookup import ResearchLookup
lookup = ResearchLookup(...)
```

### 2. Handle Async Properly

Research operations are async, always use proper async context:

```python
# ✅ Good
async def my_function():
    result = await research.research_with_progress(...)

asyncio.run(my_function())

# ❌ Bad - blocking async call
result = research.research_with_progress(...)  # Won't work
```

### 3. Monitor Long-Running Operations

For operations > 2 minutes, use external monitoring:

```python
# Start research in main process
result = await research.research_with_progress(task_name="analysis", ...)

# Monitor from separate terminal:
# python scripts/monitor-research-progress.py <project_folder> --list
```

### 4. Clean Up Checkpoints

Always clean up checkpoints after successful completion:

```python
# After successful research
if result["success"]:
    manager.delete_checkpoint(task_name)
```

### 5. Use Appropriate Research Modes

Choose research mode based on your needs:

```python
# Balanced mode (recommended) - Deep Research for Phase 1, Perplexity for others
research = EnhancedResearchLookup(research_mode="balanced", ...)

# Quick mode - Perplexity only, fast iteration
research = EnhancedResearchLookup(research_mode="perplexity", ...)

# Comprehensive mode - Deep Research for everything, high quality
research = EnhancedResearchLookup(research_mode="deep_research", ...)

# Auto mode - Smart selection based on keywords
research = EnhancedResearchLookup(research_mode="auto", ...)
```

### 6. Handle Errors Gracefully

Always implement error handling:

```python
try:
    result = await research.research_with_progress(...)
    if not result["success"]:
        print(f"Research failed: {result['error']}")
        # Implement fallback or retry logic
except Exception as e:
    print(f"Exception: {e}")
    # Handle unexpected errors
```

---

## CLI Tools

### Monitor Research Progress

```bash
# List all active operations
python scripts/monitor-research-progress.py <project_folder> --list

# Monitor specific operation
python scripts/monitor-research-progress.py <project_folder> <task_id>

# Follow mode (continuous updates)
python scripts/monitor-research-progress.py <project_folder> <task_id> --follow
```

### Resume Interrupted Research

```bash
# List resumable tasks
python scripts/resume-research.py <project_folder> <phase_num> --list

# Resume specific task
python scripts/resume-research.py <project_folder> <phase_num> --task <task_name>

# Force resume (ignore age warnings)
python scripts/resume-research.py <project_folder> <phase_num> --task <task_name> --force
```

---

## Environment Variables

### Required

```bash
export ANTHROPIC_API_KEY='your_key'  # Core planning and text generation
```

### Optional

```bash
export OPENROUTER_API_KEY='your_key'  # Perplexity research, image generation
export GEMINI_API_KEY='your_key'      # Google Gemini Deep Research (requires AI Pro subscription)
```

---

## Examples

### Complete Phase 1 Research with Progress Tracking

```python
import asyncio
from pathlib import Path
from scripts.enhanced_research_integration import EnhancedResearchLookup

async def phase1_research():
    project_folder = Path("planning_outputs/20260115_my-saas")

    research = EnhancedResearchLookup(
        project_folder=project_folder,
        phase_num=1,
        research_mode="balanced"
    )

    # Task 1: Quick market lookup (Perplexity, 30s)
    result1 = await research.research_with_progress(
        task_name="market-data",
        query="Latest SaaS pricing trends 2026"
    )

    # Task 2: Competitive analysis (Deep Research, 60 min)
    result2 = await research.research_with_progress(
        task_name="competitive-analysis",
        query="Comprehensive competitive landscape for task management SaaS"
    )

    # Task 3: Market research (Deep Research, 60 min)
    result3 = await research.research_with_progress(
        task_name="market-research",
        query="Market size and growth opportunities for SaaS"
    )

    # View statistics
    stats = research.get_stats()
    print(f"\nPhase 1 Complete:")
    print(f"  Tasks: {stats['tasks_completed']}/{stats['tasks_executed']}")
    print(f"  Resumed: {stats['tasks_resumed']}")
    print(f"  Time saved: {stats['total_time_saved_min']} minutes")

asyncio.run(phase1_research())
```

---

## See Also

- [WORKFLOWS.md](WORKFLOWS.md) - Complete workflow examples
- [CHANGELOG.md](../CHANGELOG.md) - Version history and features
- [README.md](../README.md) - User-facing documentation
- [CONTEXT_claude-project-planner.md](../CONTEXT_claude-project-planner.md) - Architecture deep dive

---

**Last Updated:** 2026-01-15
**Version:** 1.4.0-alpha
