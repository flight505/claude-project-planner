"""
Enhanced Research Integration

Demonstrates how to integrate the new progress tracking and checkpoint
capabilities with the existing research_lookup.py system.

This provides a bridge between:
- ResearchLookup (existing research execution)
- ResumableResearchExecutor (new checkpoint/progress system)

Usage:
    from enhanced_research_integration import EnhancedResearchLookup

    research = EnhancedResearchLookup(
        project_folder=project_folder,
        phase_num=1,
        research_mode="balanced"
    )

    result = await research.research_with_progress(
        task_name="competitive-analysis",
        query="Analyze competitive landscape..."
    )
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "project_planner" / ".claude" / "skills" / "research-lookup" / "scripts"))

from resumable_research import ResumableResearchExecutor
from research_progress_tracker import ResearchProgressTracker
from research_error_handling import ErrorRecoveryStrategy

try:
    from research_lookup import ResearchLookup
    HAS_RESEARCH_LOOKUP = True
except ImportError:
    HAS_RESEARCH_LOOKUP = False
    print("Warning: research_lookup.py not available")


class EnhancedResearchLookup:
    """
    Enhanced research lookup with progress tracking and checkpoints.

    Wraps ResearchLookup to add:
    - Real-time progress tracking
    - Checkpoint creation and resume
    - Error recovery with retry
    - Graceful degradation
    """

    def __init__(
        self,
        project_folder: Path,
        phase_num: int,
        research_mode: str = "auto",
        force_model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize enhanced research lookup.

        Args:
            project_folder: Path to project output folder
            phase_num: Current phase number
            research_mode: Research mode (perplexity/deep_research/balanced/auto)
            force_model: Optional Perplexity model override
            context: Optional context for routing decisions
        """
        self.project_folder = Path(project_folder)
        self.phase_num = phase_num
        self.research_mode = research_mode
        self.force_model = force_model
        self.context = context or {}

        # Initialize base research lookup
        if HAS_RESEARCH_LOOKUP:
            self.research_lookup = ResearchLookup(
                research_mode=research_mode,
                force_model=force_model,
                context=context
            )
        else:
            self.research_lookup = None

        # Initialize resumable executor
        self.executor = ResumableResearchExecutor(
            project_folder=project_folder,
            phase_num=phase_num
        )

    async def research_with_progress(
        self,
        task_name: str,
        query: str,
        estimated_duration_sec: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute research with full progress tracking and checkpoint support.

        Args:
            task_name: Unique name for this research task
            query: Research query
            estimated_duration_sec: Estimated duration (auto-detected if not provided)

        Returns:
            Research results dictionary with progress metadata
        """
        if not self.research_lookup:
            raise ImportError("research_lookup.py not available")

        # Auto-detect estimated duration based on research mode
        if estimated_duration_sec is None:
            if self.research_mode == "deep_research":
                estimated_duration_sec = 3600  # 60 min
            elif self.research_mode == "balanced":
                # Check if this query would use deep research
                if self.research_lookup._should_use_deep_research(query):
                    estimated_duration_sec = 3600
                else:
                    estimated_duration_sec = 30
            else:
                estimated_duration_sec = 30  # Perplexity default

        # Determine provider
        use_deep_research = self.research_lookup._should_use_deep_research(query)
        provider = "gemini_deep_research" if use_deep_research else "perplexity_sonar"

        # Create research functions
        async def primary_research_func():
            """Primary research function using lookup_async."""
            return await self.research_lookup.lookup_async(query)

        async def fallback_research_func():
            """Fallback to Perplexity if Deep Research fails."""
            # Force Perplexity mode temporarily
            original_mode = self.research_lookup.research_mode
            self.research_lookup.research_mode = "perplexity"

            try:
                result = self.research_lookup.lookup(query)
                return result
            finally:
                self.research_lookup.research_mode = original_mode

        # Execute with full enhancement
        result = await self.executor.execute(
            task_name=task_name,
            query=query,
            provider=provider,
            estimated_duration_sec=estimated_duration_sec,
            research_func=primary_research_func,
            fallback_func=fallback_research_func if use_deep_research else None
        )

        # Add executor stats to result
        result["executor_stats"] = self.executor.get_stats()

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get research execution statistics."""
        return self.executor.get_stats()


# Example integration for full-plan Phase 1
async def example_phase1_research(project_folder: Path, project_name: str):
    """
    Example: Phase 1 research with enhanced capabilities.

    Demonstrates how to use EnhancedResearchLookup in a full-plan workflow.
    """
    print(f"\n{'='*70}")
    print(f"PHASE 1: MARKET RESEARCH - Enhanced with Progress Tracking")
    print("="*70)

    # Initialize enhanced research
    research = EnhancedResearchLookup(
        project_folder=project_folder,
        phase_num=1,
        research_mode="balanced",  # Use balanced mode (Deep Research for major tasks)
        context={"phase": 1, "task_type": "market_research"}
    )

    # Define Phase 1 research tasks
    tasks = [
        {
            "name": "market-overview",
            "query": f"Provide a market overview for {project_name} in 2025",
            "estimated_duration": 30  # Perplexity
        },
        {
            "name": "competitive-analysis",
            "query": f"Comprehensive competitive landscape analysis for {project_name}",
            "estimated_duration": 3600  # Deep Research
        },
        {
            "name": "market-sizing",
            "query": f"Market size and growth projections for {project_name}",
            "estimated_duration": 30  # Perplexity
        }
    ]

    # Execute each task with progress tracking
    results = {}
    task_statuses = {}

    for task in tasks:
        print(f"\n{'='*70}")
        print(f"🔹 Task: {task['name']}")
        print("="*70)

        try:
            result = await research.research_with_progress(
                task_name=task["name"],
                query=task["query"],
                estimated_duration_sec=task.get("estimated_duration")
            )

            results[task["name"]] = result
            task_statuses[task["name"]] = "completed"

            print(f"\n✅ Task completed: {task['name']}")
            print(f"   Provider: {result.get('provider', 'unknown')}")
            print(f"   Sources: {len(result.get('sources', []))}")

        except Exception as e:
            print(f"\n❌ Task failed: {task['name']}")
            print(f"   Error: {e}")
            task_statuses[task["name"]] = "failed"

    # Print statistics
    stats = research.get_stats()
    print(f"\n{'='*70}")
    print("PHASE 1 STATISTICS")
    print("="*70)
    print(f"Tasks executed: {stats['tasks_executed']}")
    print(f"Tasks resumed: {stats['tasks_resumed']}")
    print(f"Tasks completed: {stats['tasks_completed']}")
    print(f"Tasks failed: {stats['tasks_failed']}")
    print(f"Total time saved: ~{stats['total_time_saved_min']} minutes")
    print("="*70)

    # Save phase checkpoint with research task statuses
    import checkpoint_manager
    checkpoint_manager.save_checkpoint(
        project_folder=project_folder,
        phase_num=1,
        context_summary="Phase 1 market research completed with enhanced progress tracking",
        research_tasks=task_statuses
    )

    return results


# CLI integration example
async def main():
    """
    Example CLI usage of enhanced research.

    This demonstrates how to use the enhanced research system from the command line.
    """
    import tempfile

    # Create temporary project folder for demonstration
    with tempfile.TemporaryDirectory() as tmpdir:
        project_folder = Path(tmpdir) / "test_project"
        project_folder.mkdir()

        print("\n" + "="*70)
        print("ENHANCED RESEARCH INTEGRATION EXAMPLE")
        print("="*70)

        # Run example Phase 1 research
        results = await example_phase1_research(
            project_folder=project_folder,
            project_name="AI Agent Platform"
        )

        print(f"\n{'='*70}")
        print("RESULTS SUMMARY")
        print("="*70)
        for task_name, result in results.items():
            success = result.get("success", False)
            status = "✅" if success else "❌"
            print(f"{status} {task_name}")

        print("\n💡 Integration complete! The enhanced research system is ready to use.")


if __name__ == "__main__":
    if HAS_RESEARCH_LOOKUP:
        asyncio.run(main())
    else:
        print("Error: research_lookup.py not available. Install dependencies and try again.")
        sys.exit(1)
