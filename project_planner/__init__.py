"""
Project Planner - AI-powered project research and planning assistant.

A powerful Python package for generating comprehensive project specifications,
architecture designs, sprint plans, cost analysis, and implementation roadmaps.

Example:
    Generate a project plan programmatically::

        import asyncio
        from project_planner import generate_project

        async def main():
            async for update in generate_project("Plan a B2B SaaS for inventory management"):
                if update["type"] == "text":
                    # Live streaming of Project Planner's responses
                    print(update["content"], end="", flush=True)
                elif update["type"] == "progress":
                    # Structured progress updates
                    print(f"\\n[{update['stage']}] {update['message']}")
                elif update["type"] == "result":
                    print(f"\\nProject created: {update['project_directory']}")
                    print(f"Components: {update['component_count']}")

        asyncio.run(main())

    Use the CLI::

        $ project-planner
        > Plan a real-time chat application with microservices architecture
"""

from .api import generate_project
from .models import ProgressUpdate, TextUpdate, ProjectResult, ProjectMetadata, ProjectFiles, TokenUsage

__version__ = "1.0.0"
__author__ = "flight505"
__license__ = "MIT"

__all__ = [
    "generate_project",
    "ProgressUpdate",
    "TextUpdate",
    "ProjectResult",
    "ProjectMetadata",
    "ProjectFiles",
    "TokenUsage",
]
