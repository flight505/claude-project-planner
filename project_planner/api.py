"""Async API for programmatic project planning and architecture generation."""

import asyncio
import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncGenerator, Union, Literal
from datetime import datetime
from dotenv import load_dotenv

from claude_agent_sdk import query as claude_query, ClaudeAgentOptions
from claude_agent_sdk.types import HookMatcher, StopHookInput, HookContext

from .core import (
    get_api_key,
    load_system_instructions,
    ensure_output_folder,
    get_data_files,
    process_data_files,
    create_data_context_message,
    setup_claude_skills,
)
from .models import ProgressUpdate, TextUpdate, ProjectResult, ProjectMetadata, ProjectFiles, TokenUsage
from .utils import scan_project_directory


# Model mapping for effort levels
EFFORT_LEVEL_MODELS = {
    "low": "claude-haiku-4-5",
    "medium": "claude-sonnet-4-5",
    "high": "claude-opus-4-5",
}

# Progress stages for project planning workflow
PROGRESS_STAGES = [
    "initialization",      # Setting up project structure
    "requirements",        # Gathering and analyzing requirements
    "research",            # Architecture research and patterns lookup
    "architecture",        # Designing system architecture
    "components",          # Defining building blocks and components
    "cost_analysis",       # Service cost estimation
    "sprint_planning",     # Creating sprint plans and timelines
    "risk_assessment",     # Risk analysis and mitigation
    "documentation",       # Writing final documentation
    "complete",            # All done
]


def create_completion_check_stop_hook(auto_continue: bool = True):
    """
    Create a stop hook that optionally forces continuation.

    Args:
        auto_continue: If True, always continue (never stop on agent's own).
                      If False, allow normal stopping behavior.
    """
    async def completion_check_stop_hook(
        hook_input: StopHookInput,
        matcher: str | None,
        context: HookContext,
    ) -> dict:
        """
        Stop hook that checks if the task is complete before allowing stop.

        When auto_continue is True, this returns continue_=True to force
        the agent to continue working instead of stopping.
        """
        if auto_continue:
            return {"continue_": True}
        return {"continue_": False}

    return completion_check_stop_hook


async def generate_project(
    query: str,
    output_dir: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    effort_level: Literal["low", "medium", "high"] = "medium",
    project_type: Literal["full", "architecture", "sprint", "cost", "risk"] = "full",
    data_files: Optional[List[str]] = None,
    cwd: Optional[str] = None,
    track_token_usage: bool = False,
    auto_continue: bool = True,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Generate a comprehensive project plan asynchronously with progress updates.

    This is a stateless async generator that yields progress updates during
    execution and a final comprehensive result with all project details.
    Supports full project plans, architecture designs, sprint plans, cost analysis, and risk assessments.

    Args:
        query: The project planning request (e.g., "Plan a B2B SaaS for inventory management",
               "Design architecture for a real-time chat system", "Create sprint plan for auth module")
        output_dir: Optional custom output directory (defaults to cwd/planning_outputs)
        api_key: Optional Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        model: Optional explicit Claude model to use. If provided, overrides effort_level.
        effort_level: Effort level that determines the model to use (default: "medium"):
            - "low": Uses Claude Haiku 4.5 (fastest, most economical)
            - "medium": Uses Claude Sonnet 4.5 (balanced) [default]
            - "high": Uses Claude Opus 4.5 (most capable)
        project_type: Type of output to generate (default: "full"):
            - "full": Complete project plan with all components
            - "architecture": Focus on technical architecture only
            - "sprint": Focus on sprint planning only
            - "cost": Focus on cost analysis only
            - "risk": Focus on risk assessment only
        data_files: Optional list of data file paths to include (specs, mockups, etc.)
        cwd: Optional working directory (defaults to current directory)
        track_token_usage: If True, track and return token usage in the final result
        auto_continue: If True (default), the agent will not stop on its own

    Yields:
        Progress updates (dict with type="progress") during execution
        Final result (dict with type="result") containing all project information

    Example:
        ```python
        async for update in generate_project("Plan a B2B SaaS for inventory management"):
            if update["type"] == "progress":
                print(f"[{update['stage']}] {update['message']}")
            elif update["type"] == "result":
                print(f"Project created: {update['project_directory']}")
                print(f"Components: {update['component_count']}")
        ```
    """
    start_time = time.time()

    # Resolve model
    if model is None:
        model = EFFORT_LEVEL_MODELS[effort_level]

    # Determine working directory
    if cwd:
        work_dir = Path(cwd).resolve()
    else:
        work_dir = Path.cwd().resolve()

    # Load .env from working directory
    env_file = work_dir / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)

    # Get API key
    try:
        api_key_value = get_api_key(api_key)
    except ValueError as e:
        yield _create_error_result(str(e))
        return

    # Get package directory for copying skills
    package_dir = Path(__file__).parent.absolute()

    # Set up Claude skills in the working directory
    setup_claude_skills(package_dir, work_dir)

    # Ensure output folder exists
    output_folder = ensure_output_folder(work_dir, output_dir)

    # Initial progress update
    yield ProgressUpdate(
        message="Initializing project planning",
        stage="initialization",
    ).to_dict()

    # Load system instructions
    system_instructions = load_system_instructions(work_dir)

    # Add project-specific instructions
    project_type_instructions = _get_project_type_instructions(project_type)

    system_instructions += "\n\n" + f"""
IMPORTANT - WORKING DIRECTORY:
- Your working directory is: {work_dir}
- ALWAYS create planning_outputs folder in this directory: {work_dir}/planning_outputs/
- NEVER write to /tmp/ or any other temporary directory
- All project outputs MUST go to: {work_dir}/planning_outputs/<timestamp>_<description>/

IMPORTANT - PROJECT TYPE:
{project_type_instructions}

IMPORTANT - OUTPUT STRUCTURE:
Create the following folder structure for project outputs:
- planning_outputs/<timestamp>_<project_name>/
  - research/          (market_research.md, competitive_analysis.md, technology_research.md)
  - analysis/          (feasibility_analysis.md, cost_analysis.md, risk_assessment.md, roi_projections.md)
  - specifications/    (project_spec.md, technical_spec.md, api_spec.md, data_model.md)
  - components/        (component_breakdown.md, individual component specs)
  - planning/          (sprint_plan.md, timeline.md, milestones.md)
  - diagrams/          (architecture.png, component_diagram.png, data_flow.png)
  - progress.md        (real-time progress log)
  - SUMMARY.md         (executive summary)
"""

    # Process data files if provided
    if data_files:
        data_file_paths = get_data_files(work_dir, data_files)
        if data_file_paths:
            yield ProgressUpdate(
                message=f"Found {len(data_file_paths)} data file(s) to process",
                stage="initialization",
            ).to_dict()

    # Check auto-continue setting
    env_auto_continue = os.environ.get("PROJECT_PLANNER_AUTO_CONTINUE", "").lower()
    if env_auto_continue in ("false", "0", "no"):
        auto_continue = False

    # Configure Claude agent options
    options = ClaudeAgentOptions(
        system_prompt=system_instructions,
        model=model,
        allowed_tools=["Read", "Write", "Edit", "Bash", "WebSearch", "research-lookup"],
        permission_mode="bypassPermissions",
        setting_sources=["project"],
        cwd=str(work_dir),
        max_turns=500,
        hooks={
            "Stop": [
                HookMatcher(
                    matcher=None,
                    hooks=[create_completion_check_stop_hook(auto_continue=auto_continue)],
                )
            ]
        },
    )

    # Track progress
    current_stage = "initialization"
    output_directory = None
    last_message = ""
    tool_call_count = 0
    files_written = []

    # Token usage tracking
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_creation_tokens = 0
    total_cache_read_tokens = 0

    yield ProgressUpdate(
        message="Starting project planning",
        stage="initialization",
        details={"query_length": len(query), "project_type": project_type},
    ).to_dict()

    # Execute query
    try:
        accumulated_text = ""
        async for message in claude_query(prompt=query, options=options):
            # Track token usage
            if track_token_usage and hasattr(message, "usage") and message.usage:
                usage = message.usage
                total_input_tokens += getattr(usage, "input_tokens", 0)
                total_output_tokens += getattr(usage, "output_tokens", 0)
                total_cache_creation_tokens += getattr(usage, "cache_creation_input_tokens", 0)
                total_cache_read_tokens += getattr(usage, "cache_read_input_tokens", 0)

            if hasattr(message, "content") and message.content:
                for block in message.content:
                    # Handle text blocks
                    if hasattr(block, "text"):
                        text = block.text
                        accumulated_text += text

                        # Yield live text update
                        yield TextUpdate(content=text).to_dict()

                        # Analyze for progress
                        stage, msg = _analyze_progress(accumulated_text, current_stage)
                        if stage != current_stage and msg and msg != last_message:
                            current_stage = stage
                            last_message = msg
                            yield ProgressUpdate(message=msg, stage=stage).to_dict()

                    # Handle tool use blocks
                    elif hasattr(block, "type") and block.type == "tool_use":
                        tool_call_count += 1
                        tool_name = getattr(block, "name", "unknown")
                        tool_input = getattr(block, "input", {})

                        if tool_name.lower() == "write":
                            file_path = tool_input.get("file_path", tool_input.get("path", ""))
                            if file_path:
                                files_written.append(file_path)

                        tool_progress = _analyze_tool_use(tool_name, tool_input, current_stage)
                        if tool_progress:
                            stage, msg = tool_progress
                            if msg != last_message:
                                current_stage = stage
                                last_message = msg
                                yield ProgressUpdate(
                                    message=msg,
                                    stage=stage,
                                    details={
                                        "tool": tool_name,
                                        "tool_calls": tool_call_count,
                                        "files_created": len(files_written),
                                    },
                                ).to_dict()

        # Project planning complete
        yield ProgressUpdate(
            message="Scanning output directory",
            stage="complete",
        ).to_dict()

        # Find the output directory
        output_directory = _find_most_recent_output(output_folder, start_time)

        if not output_directory:
            error_result = _create_error_result("Output directory not found after generation")
            if track_token_usage:
                error_result['token_usage'] = TokenUsage(
                    input_tokens=total_input_tokens,
                    output_tokens=total_output_tokens,
                    cache_creation_input_tokens=total_cache_creation_tokens,
                    cache_read_input_tokens=total_cache_read_tokens,
                ).to_dict()
            yield error_result
            return

        # Process data files
        if data_files:
            data_file_paths = get_data_files(work_dir, data_files)
            if data_file_paths:
                processed_info = process_data_files(
                    work_dir,
                    data_file_paths,
                    str(output_directory),
                    delete_originals=False
                )
                if processed_info:
                    yield ProgressUpdate(
                        message=f"Processed {len(processed_info['all_files'])} file(s)",
                        stage="complete",
                    ).to_dict()

        # Scan output directory
        file_info = scan_project_directory(output_directory)

        # Build result
        result = _build_project_result(output_directory, file_info)

        # Add token usage
        if track_token_usage:
            result.token_usage = TokenUsage(
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                cache_creation_input_tokens=total_cache_creation_tokens,
                cache_read_input_tokens=total_cache_read_tokens,
            )

        yield ProgressUpdate(
            message="Project planning complete",
            stage="complete",
        ).to_dict()

        yield result.to_dict()

    except Exception as e:
        error_result = _create_error_result(f"Error during project planning: {str(e)}")
        if track_token_usage:
            error_result['token_usage'] = TokenUsage(
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens,
                cache_creation_input_tokens=total_cache_creation_tokens,
                cache_read_input_tokens=total_cache_read_tokens,
            ).to_dict()
        yield error_result


def _get_project_type_instructions(project_type: str) -> str:
    """Get specific instructions based on project type."""
    instructions = {
        "full": """Generate a COMPLETE project plan including:
- Market and competitive research
- Technical architecture design with ADRs
- Building blocks breakdown for Claude Code
- Service cost analysis
- Sprint planning with INVEST stories
- Risk assessment with mitigations""",

        "architecture": """Focus on TECHNICAL ARCHITECTURE:
- Technology stack research and comparison
- Architecture Decision Records (ADRs)
- C4 model diagrams (Context, Container, Component)
- API design and data models
- Infrastructure recommendations""",

        "sprint": """Focus on SPRINT PLANNING:
- Epic breakdown into user stories
- INVEST criteria validation
- Story point estimation
- Dependency mapping
- Sprint timeline and milestones""",

        "cost": """Focus on COST ANALYSIS:
- Cloud service comparison (AWS, GCP, Azure)
- API and third-party service costs
- TCO calculations
- ROI projections (3-year)
- Cost optimization recommendations""",

        "risk": """Focus on RISK ASSESSMENT:
- Technical risk identification
- Business risk analysis
- Security considerations
- Mitigation strategies
- Go/no-go decision framework""",
    }
    return instructions.get(project_type, instructions["full"])


def _analyze_progress(text: str, current_stage: str) -> tuple:
    """Analyze text for progress stage transitions."""
    text_lower = text.lower()

    stage_order = PROGRESS_STAGES
    current_idx = stage_order.index(current_stage) if current_stage in stage_order else 0

    # Detect stage transitions
    if current_idx < stage_order.index("research"):
        if "researching" in text_lower or "searching" in text_lower or "analyzing market" in text_lower:
            return "research", "Conducting research"

    if current_idx < stage_order.index("architecture"):
        if "architecture" in text_lower or "designing" in text_lower or "tech stack" in text_lower:
            return "architecture", "Designing architecture"

    if current_idx < stage_order.index("components"):
        if "component" in text_lower or "building block" in text_lower or "module" in text_lower:
            return "components", "Defining components"

    if current_idx < stage_order.index("cost_analysis"):
        if "cost" in text_lower or "pricing" in text_lower or "tco" in text_lower:
            return "cost_analysis", "Analyzing costs"

    if current_idx < stage_order.index("sprint_planning"):
        if "sprint" in text_lower or "story" in text_lower or "backlog" in text_lower:
            return "sprint_planning", "Planning sprints"

    if current_idx < stage_order.index("risk_assessment"):
        if "risk" in text_lower or "mitigation" in text_lower:
            return "risk_assessment", "Assessing risks"

    if current_idx < stage_order.index("complete"):
        if "complete" in text_lower or "finished" in text_lower or "done" in text_lower:
            return "complete", "Finalizing"

    return current_stage, None


def _analyze_tool_use(tool_name: str, tool_input: Dict[str, Any], current_stage: str) -> tuple:
    """Analyze tool usage for progress updates."""
    file_path = tool_input.get("file_path", tool_input.get("path", ""))
    command = tool_input.get("command", "")
    filename = Path(file_path).name if file_path else ""

    # Write tool
    if tool_name.lower() == "write":
        if "market_research" in file_path:
            return ("research", "Writing market research")
        elif "competitive" in file_path:
            return ("research", "Writing competitive analysis")
        elif "technology_research" in file_path or "tech_stack" in file_path:
            return ("research", "Writing technology research")
        elif "architecture" in file_path or "technical_spec" in file_path:
            return ("architecture", f"Writing {filename}")
        elif "component" in file_path or "building_block" in file_path:
            return ("components", f"Defining component: {filename}")
        elif "cost" in file_path or "roi" in file_path:
            return ("cost_analysis", f"Writing {filename}")
        elif "sprint" in file_path or "timeline" in file_path:
            return ("sprint_planning", f"Writing {filename}")
        elif "risk" in file_path:
            return ("risk_assessment", f"Writing {filename}")
        elif "SUMMARY" in file_path or "progress" in file_path:
            return ("documentation", f"Writing {filename}")
        elif file_path:
            return (current_stage, f"Creating {filename}")
        return None

    # Read tool
    elif tool_name.lower() == "read":
        if file_path:
            return (current_stage, f"Reading {filename}")
        return None

    # Bash tool
    elif tool_name.lower() == "bash":
        if "mkdir" in command:
            if "planning_outputs" in command:
                return ("initialization", "Creating output directory")
            return ("initialization", "Setting up directories")
        elif "mermaid" in command.lower():
            return ("architecture", "Generating diagram")
        return None

    # Research/lookup tools
    elif "research" in tool_name.lower() or "lookup" in tool_name.lower():
        query_text = tool_input.get("query", "")
        if query_text:
            truncated = query_text[:50] + "..." if len(query_text) > 50 else query_text
            return ("research", f"Researching: {truncated}")
        return ("research", "Searching databases")

    # Web search
    elif "search" in tool_name.lower() or "web" in tool_name.lower():
        query_text = tool_input.get("query", "")
        if query_text:
            truncated = query_text[:40] + "..." if len(query_text) > 40 else query_text
            return ("research", f"Web search: {truncated}")
        return ("research", "Searching online")

    return None


def _find_most_recent_output(output_folder: Path, start_time: float) -> Optional[Path]:
    """Find the most recently created output directory."""
    try:
        output_dirs = [d for d in output_folder.iterdir() if d.is_dir()]
        if not output_dirs:
            return None

        recent_dirs = [
            d for d in output_dirs
            if d.stat().st_mtime >= start_time - 5
        ]

        if not recent_dirs:
            recent_dirs = output_dirs

        return max(recent_dirs, key=lambda d: d.stat().st_mtime)
    except (FileNotFoundError, PermissionError, OSError, ValueError):
        # Directory not found, permission denied, or no directories to compare
        return None


# scan_project_directory is now imported from utils.py (see line 23)
# Removed duplicate implementation - using consolidated version from utils.py


def _build_project_result(project_dir: Path, file_info: Dict[str, Any]) -> ProjectResult:
    """Build a ProjectResult from scanned files."""
    # Extract project name from directory
    project_name = ""
    parts = project_dir.name.split('_', 2)
    if len(parts) >= 3:
        project_name = parts[2].replace('_', ' ')

    metadata = ProjectMetadata(
        name=project_name,
        created_at=datetime.fromtimestamp(project_dir.stat().st_ctime).isoformat() + "Z",
        description=project_name,
    )

    files = ProjectFiles(
        project_spec=file_info.get('project_spec'),
        technical_spec=file_info.get('technical_spec'),
        api_spec=file_info.get('api_spec'),
        data_model=file_info.get('data_model'),
        market_research=file_info.get('market_research'),
        competitive_analysis=file_info.get('competitive_analysis'),
        technology_research=file_info.get('technology_research'),
        feasibility_analysis=file_info.get('feasibility_analysis'),
        cost_analysis=file_info.get('cost_analysis'),
        risk_assessment=file_info.get('risk_assessment'),
        roi_projections=file_info.get('roi_projections'),
        sprint_plan=file_info.get('sprint_plan'),
        timeline=file_info.get('timeline'),
        component_breakdown=file_info.get('component_breakdown'),
        diagrams=file_info.get('diagrams', []),
        progress_log=file_info.get('progress_log'),
        summary=file_info.get('summary'),
        plan_review=file_info.get('plan_review'),
    )

    # Determine status
    has_specs = file_info.get('project_spec') or file_info.get('technical_spec')
    has_components = bool(file_info.get('components'))
    status = "success" if has_specs else ("partial" if has_components else "failed")

    result = ProjectResult(
        status=status,
        project_directory=str(project_dir),
        project_name=project_dir.name,
        metadata=metadata,
        files=files,
        component_count=len(file_info.get('components', [])),
        diagrams_count=len(file_info.get('diagrams', [])),
        errors=[],
    )

    return result


def _create_error_result(error_message: str) -> Dict[str, Any]:
    """Create an error result dictionary."""
    result = ProjectResult(
        status="failed",
        project_directory="",
        project_name="",
        errors=[error_message],
    )
    return result.to_dict()


# Backwards compatibility alias
generate_paper = generate_project
