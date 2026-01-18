#!/usr/bin/env python3
"""
Project Planner CLI Tool
A command-line interface for AI-powered project planning.
"""

import os
import sys
import time
import asyncio
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import HookMatcher

from .core import (
    get_api_key,
    load_system_instructions,
    ensure_output_folder,
    get_data_files,
    process_data_files,
    create_data_context_message,
    setup_claude_skills,
    create_completion_check_stop_hook,
)
from .utils import find_existing_projects, detect_project_reference, scan_project_directory
from .models import TokenUsage


async def main(track_token_usage: bool = False) -> Optional[TokenUsage]:
    """
    Main CLI loop for the project planner.

    Args:
        track_token_usage: If True, track and return token usage statistics

    Returns:
        TokenUsage object if track_token_usage is True, None otherwise
    """
    # Explicitly load .env file from current working directory
    cwd_resolved = Path.cwd().resolve()
    env_file = cwd_resolved / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)

    # Get API key (verify it exists)
    try:
        get_api_key()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Get the current working directory and package directory
    cwd = Path.cwd().resolve()
    package_dir = Path(__file__).parent.absolute()

    # Set up Claude skills in the working directory
    setup_claude_skills(package_dir, cwd)

    # Ensure planning_outputs folder exists
    output_folder = ensure_output_folder(cwd)

    # Load system instructions from .claude/PLANNER.md
    system_instructions = load_system_instructions(cwd)

    # Add project planning specific instructions
    system_instructions += "\n\n" + f"""
IMPORTANT - WORKING DIRECTORY:
- Your working directory is: {cwd}
- ALWAYS create planning_outputs folder in this directory: {cwd}/planning_outputs/
- NEVER write to /tmp/ or any other temporary directory
- All project outputs MUST go to: {cwd}/planning_outputs/<timestamp>_<description>/

IMPORTANT - CONVERSATION CONTINUITY:
- The user will provide context if they want to continue working on an existing project
- If the prompt includes [CONTEXT: You are currently working on a project in: ...], continue that project
- If no such context is provided, this is a NEW project request - create a new project directory
- Do NOT assume there's an existing project unless explicitly told in the prompt context
- Each new chat session should start with a new project unless context says otherwise

PROJECT OUTPUT STRUCTURE:
- specifications/: PRD, technical specs, API specs, data models
- research/: market research, technology research, competitive analysis
- analysis/: feasibility, cost analysis, risk assessment, ROI projections
- components/: building blocks YAML, component specifications
- planning/: sprint plans, timeline, milestones
- diagrams/: architecture diagrams, flow charts, data models
- data/: input data files
- sources/: reference materials
"""

    # Check if auto-continue is enabled
    auto_continue = os.environ.get("PROJECT_PLANNER_AUTO_CONTINUE", "true").lower() in ("true", "1", "yes")

    # Configure agent options
    options = ClaudeAgentOptions(
        system_prompt=system_instructions,
        model="claude-sonnet-4-5",
        allowed_tools=["Read", "Write", "Edit", "Bash", "WebSearch", "research-lookup"],
        permission_mode="bypassPermissions",
        setting_sources=["project"],
        cwd=str(cwd),
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

    # Track conversation state
    current_project_path = None
    conversation_history = []

    # Token usage tracking
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_creation_tokens = 0
    total_cache_read_tokens = 0

    # Print welcome message
    print("=" * 70)
    print("Project Planner CLI")
    print("=" * 70)
    print("\nWelcome! I'm your AI-powered project planning assistant.")
    print("\nI can help you with:")
    print("  • 📊 Business case research and market analysis")
    print("  • 🏛️ Software architecture design (ADRs, C4 diagrams)")
    print("  • 🧱 Breaking projects into buildable components")
    print("  • 💰 Service cost analysis and ROI projections")
    print("  • 📋 Sprint planning and implementation timelines")
    print("  • ⚠️ Risk assessment and mitigation strategies")
    print("\n📋 Workflow:")
    print("  1. Describe your project idea or requirements")
    print("  2. I'll research, analyze, and create comprehensive plans")
    print("  3. All outputs saved to: planning_outputs/<timestamp_project>/")
    print("  4. Progress tracked in real-time in progress.md")
    print(f"\n📁 Working directory: {cwd}")
    print(f"📁 Output folder: {output_folder}")
    print(f"\n📦 Input Files:")
    print("  • Place spec files in 'data/' folder to include them")
    print("  • Requirements docs (.md, .docx) → copied to specifications/")
    print("  • Data files (csv, json, etc.) → copied to project's data/")
    print("  • Diagrams (png, svg) → copied to project's diagrams/")
    print("\n🤖 Intelligent Project Detection:")
    print("  • I detect when you're referring to a previous project")
    print("  • Continue: 'continue', 'update the plan', 'add component', etc.")
    print("  • Search: 'find the inventory project', 'show me the SaaS plan'")
    print("  • Say 'new project' to explicitly start fresh")
    print("\nType 'exit' or 'quit' to end the session.")
    print("Type 'help' for usage tips.")
    print("=" * 70)
    print()

    # Main loop
    while True:
        try:
            # Get user input
            user_input = input("\n> ").strip()

            # Handle special commands
            if user_input.lower() in ["exit", "quit"]:
                print("\nThank you for using Project Planner CLI. Goodbye!")
                if track_token_usage:
                    return TokenUsage(
                        input_tokens=total_input_tokens,
                        output_tokens=total_output_tokens,
                        cache_creation_input_tokens=total_cache_creation_tokens,
                        cache_read_input_tokens=total_cache_read_tokens,
                    )
                return None

            if user_input.lower() == "help":
                _print_help()
                continue

            if not user_input:
                continue

            # Get all existing projects
            existing_projects = find_existing_projects(output_folder)

            # Check if user wants to start a new project
            new_project_keywords = [
                "new project", "start fresh", "start afresh", "create new",
                "different project", "another project", "plan a new",
                "new plan", "fresh start", "from scratch"
            ]
            is_new_project_request = any(keyword in user_input.lower() for keyword in new_project_keywords)

            # Try to detect reference to existing project
            detected_project_path = None
            if not is_new_project_request:
                detected_project_path = detect_project_reference(user_input, existing_projects)

                if detected_project_path and str(detected_project_path) != current_project_path:
                    current_project_path = str(detected_project_path)
                    print(f"\n🔍 Detected reference to existing project: {detected_project_path.name}")
                    print(f"📂 Working on: {current_project_path}")

                    # Show what files exist
                    project_info = scan_project_directory(detected_project_path)
                    file_count = sum([
                        1 if project_info.get('project_spec') else 0,
                        1 if project_info.get('technical_spec') else 0,
                        1 if project_info.get('sprint_plan') else 0,
                        1 if project_info.get('building_blocks') else 0,
                        1 if project_info.get('cost_analysis') else 0,
                        1 if project_info.get('risk_assessment') else 0,
                        len(project_info.get('diagrams', [])),
                        len(project_info.get('data', [])),
                        len(project_info.get('sources', [])),
                        1 if project_info.get('progress_log') else 0,
                        1 if project_info.get('summary') else 0,
                    ])
                    print(f"📄 Found {file_count} artifact(s) in this project\n")

                elif detected_project_path and str(detected_project_path) == current_project_path:
                    print(f"📂 Continuing with: {Path(current_project_path).name}\n")

            # Handle data files
            data_context = ""
            data_files = get_data_files(cwd)

            # PHASE 1: New project with data files
            if data_files and not current_project_path and (is_new_project_request or not current_project_path):
                print(f"\n📦 Found {len(data_files)} file(s) in data folder.")
                print("📝 Starting a new project...")
                print("⏳ Step 1/2: Creating project directory...\n")

                directory_prompt = f"""Create a new project directory structure in planning_outputs/ following the standard format:
planning_outputs/YYYYMMDD_HHMMSS_<project_name>/

Create these folders:
- specifications/
- research/
- analysis/
- components/
- planning/
- diagrams/
- data/
- sources/

IMPORTANT:
1. Only create the directory structure and progress.md file
2. Do NOT start the planning yet
3. Report back the directory path you created
4. Wait for further instructions

Based on the user request: {user_input}"""

                async for message in query(prompt=directory_prompt, options=options):
                    if track_token_usage and hasattr(message, "usage") and message.usage:
                        usage = message.usage
                        total_input_tokens += getattr(usage, "input_tokens", 0)
                        total_output_tokens += getattr(usage, "output_tokens", 0)
                        total_cache_creation_tokens += getattr(usage, "cache_creation_input_tokens", 0)
                        total_cache_read_tokens += getattr(usage, "cache_read_input_tokens", 0)

                    if hasattr(message, "content") and message.content:
                        for block in message.content:
                            if hasattr(block, "text"):
                                print(block.text, end="", flush=True)

                print("\n")

                # Detect newly created directory
                time.sleep(1)
                try:
                    project_dirs = [d for d in output_folder.iterdir() if d.is_dir()]
                    if project_dirs:
                        most_recent = max(project_dirs, key=lambda d: d.stat().st_mtime)
                        time_since_modification = time.time() - most_recent.stat().st_mtime

                        if time_since_modification < 15:
                            current_project_path = str(most_recent)
                            print(f"✓ Directory created: {most_recent.name}\n")
                except Exception as e:
                    print(f"Warning: Could not detect project directory: {e}\n")

                # PHASE 2: Process data files
                if current_project_path:
                    print(f"⏳ Step 2/2: Processing and copying data files...")
                    processed_info = process_data_files(cwd, data_files, current_project_path)
                    if processed_info:
                        data_context = create_data_context_message(processed_info)
                        spec_count = len(processed_info.get('spec_files', []))
                        source_count = len(processed_info.get('source_files', []))
                        data_count = len(processed_info.get('data_files', []))
                        image_count = len(processed_info.get('image_files', []))
                        if spec_count > 0:
                            print(f"   ✓ Copied {spec_count} spec file(s) to specifications/")
                        if source_count > 0:
                            print(f"   ✓ Copied {source_count} source file(s) to sources/")
                        if data_count > 0:
                            print(f"   ✓ Copied {data_count} data file(s) to data/")
                        if image_count > 0:
                            print(f"   ✓ Copied {image_count} diagram(s) to diagrams/")
                        print("   ✓ Deleted original files from data folder\n")
                        print("✅ Files processed. Now starting project planning...\n")

                contextual_prompt = f"""[CONTEXT: You are working on a project in: {current_project_path}]
[FILES HAVE BEEN PROCESSED AND COPIED - see details below]
{data_context}

Now continue with the project planning for the user's request:
{user_input}"""

            elif data_files and current_project_path and not is_new_project_request:
                # Existing project with data files
                print(f"📦 Found {len(data_files)} file(s) in data folder. Processing...")
                processed_info = process_data_files(cwd, data_files, current_project_path)
                if processed_info:
                    data_context = create_data_context_message(processed_info)
                    spec_count = len(processed_info.get('spec_files', []))
                    source_count = len(processed_info.get('source_files', []))
                    data_count = len(processed_info.get('data_files', []))
                    image_count = len(processed_info.get('image_files', []))
                    if spec_count > 0:
                        print(f"   ✓ Copied {spec_count} spec file(s) to specifications/")
                    if source_count > 0:
                        print(f"   ✓ Copied {source_count} source file(s) to sources/")
                    if data_count > 0:
                        print(f"   ✓ Copied {data_count} data file(s) to data/")
                    if image_count > 0:
                        print(f"   ✓ Copied {image_count} diagram(s) to diagrams/")
                    print("   ✓ Deleted original files from data folder\n")

                contextual_prompt = f"""[CONTEXT: You are currently working on a project in: {current_project_path}]
[INSTRUCTION: Continue working on this existing project. Do NOT create a new project directory.]
{data_context}
User request: {user_input}"""

            elif is_new_project_request and not data_files:
                # New project without data files
                current_project_path = None
                print("📝 Starting a new project...\n")
                contextual_prompt = user_input

            elif current_project_path and not data_files:
                # Existing project without new data files
                project_info = scan_project_directory(Path(current_project_path))

                context_parts = [
                    f"[CONTEXT: You are currently working on a project in: {current_project_path}]",
                    "[INSTRUCTION: Continue working on this existing project. Do NOT create a new project directory.]",
                    "\n📁 Current project contents:"
                ]

                # Add information about existing artifacts
                if project_info.get('project_spec'):
                    context_parts.append(f"  • Project Spec: {Path(project_info['project_spec']).name}")
                if project_info.get('technical_spec'):
                    context_parts.append(f"  • Technical Spec: {Path(project_info['technical_spec']).name}")
                if project_info.get('building_blocks'):
                    context_parts.append(f"  • Building Blocks: {Path(project_info['building_blocks']).name}")
                if project_info.get('sprint_plan'):
                    context_parts.append(f"  • Sprint Plan: {Path(project_info['sprint_plan']).name}")
                if project_info.get('cost_analysis'):
                    context_parts.append(f"  • Cost Analysis: {Path(project_info['cost_analysis']).name}")
                if project_info.get('risk_assessment'):
                    context_parts.append(f"  • Risk Assessment: {Path(project_info['risk_assessment']).name}")
                if project_info.get('diagrams'):
                    context_parts.append(f"  • Diagrams: {len(project_info['diagrams'])} file(s)")
                if project_info.get('data'):
                    context_parts.append(f"  • Data files: {len(project_info['data'])} file(s)")
                if project_info.get('sources'):
                    context_parts.append(f"  • Source files: {len(project_info['sources'])} file(s)")
                if project_info.get('progress_log'):
                    context_parts.append(f"  • Progress log: progress.md")
                if project_info.get('summary'):
                    context_parts.append(f"  • Summary: SUMMARY.md")

                context_parts.append(f"\nUser request: {user_input}")
                contextual_prompt = "\n".join(context_parts)

            else:
                # No data files, no detected project
                contextual_prompt = user_input

            # Send query
            print()
            async for message in query(prompt=contextual_prompt, options=options):
                if track_token_usage and hasattr(message, "usage") and message.usage:
                    usage = message.usage
                    total_input_tokens += getattr(usage, "input_tokens", 0)
                    total_output_tokens += getattr(usage, "output_tokens", 0)
                    total_cache_creation_tokens += getattr(usage, "cache_creation_input_tokens", 0)
                    total_cache_read_tokens += getattr(usage, "cache_read_input_tokens", 0)

                if hasattr(message, "content") and message.content:
                    for block in message.content:
                        if hasattr(block, "text"):
                            print(block.text, end="", flush=True)

            print()

            # Detect if a new project directory was created
            if not current_project_path and not data_files:
                try:
                    project_dirs = [d for d in output_folder.iterdir() if d.is_dir()]
                    if project_dirs:
                        most_recent = max(project_dirs, key=lambda d: d.stat().st_mtime)
                        time_since_modification = time.time() - most_recent.stat().st_mtime

                        if time_since_modification < 10:
                            current_project_path = str(most_recent)
                            print(f"\n📂 Working on: {most_recent.name}")
                except (OSError, ValueError):
                    # Directory access error or no directories to compare
                    pass

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'exit' to quit or continue with a new prompt.")
            continue
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again or type 'exit' to quit.")

    if track_token_usage:
        return TokenUsage(
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            cache_creation_input_tokens=total_cache_creation_tokens,
            cache_read_input_tokens=total_cache_read_tokens,
        )
    return None


def _print_help():
    """Print help information."""
    print("\n" + "=" * 70)
    print("HELP - Project Planner CLI")
    print("=" * 70)
    print("\n📝 What I Can Do:")
    print("  • Research business cases and market opportunities")
    print("  • Design software architectures with ADRs and C4 diagrams")
    print("  • Break projects into buildable components for Claude Code")
    print("  • Analyze service costs (AWS, GCP, Azure, etc.)")
    print("  • Create sprint plans with INVEST user stories")
    print("  • Assess risks and create mitigation strategies")
    print("  • Generate comprehensive project documentation")
    print("\n🔄 Planning Workflow:")
    print("  1. You describe your project idea or requirements")
    print("  2. I research market, technology, and competitive landscape")
    print("  3. I design architecture and break into components")
    print("  4. I estimate costs and create sprint plans")
    print("  5. All files organized in planning_outputs/ folder")
    print("\n💡 Example Requests:")
    print("  'Plan a B2B SaaS inventory management system'")
    print("  'Design architecture for a real-time chat application'")
    print("  'Break down a mobile app for food delivery into components'")
    print("  'Research tech stack options for a fintech startup'")
    print("  'Create sprint plan for an e-commerce platform'")
    print("  'Analyze costs for deploying on AWS vs GCP'")
    print("\n📁 Output Structure:")
    print("  All work saved to: planning_outputs/<timestamp>_<project>/")
    print("  - specifications/ - PRD, technical specs, API specs")
    print("  - research/ - Market, technology, competitive analysis")
    print("  - analysis/ - Feasibility, costs, risks, ROI")
    print("  - components/ - Building blocks for Claude Code")
    print("  - planning/ - Sprint plans, timeline, milestones")
    print("  - diagrams/ - Architecture, flow, data model diagrams")
    print("  - progress.md - Real-time progress log")
    print("  - SUMMARY.md - Project summary")
    print("\n📦 Input Files:")
    print("  Place files in the 'data/' folder at project root:")
    print("  • Spec files (.md with 'spec' in name) → specifications/")
    print("  • Context files (.md, .docx, .pdf) → sources/")
    print("  • Data files (csv, json, etc.) → project's data/")
    print("  • Images (png, svg, etc.) → project's diagrams/")
    print("  • Original files automatically deleted after copying")
    print("\n🎯 Pro Tips:")
    print("  • Be specific about project type (SaaS, mobile, API, etc.)")
    print("  • Mention scale expectations (startup, enterprise)")
    print("  • Specify cloud preferences if any (AWS, GCP, Azure)")
    print("  • Check progress.md for detailed execution logs")
    print("\n🔄 Project Detection:")
    print("  • I detect when you're referring to a previous project")
    print("  • Continue: 'update the plan', 'add sprint', 'edit architecture'")
    print("  • Search: 'find the inventory project', 'show the SaaS plan'")
    print("  • Say 'new project' or 'start fresh' to begin a new one")
    print("=" * 70)


def cli_main():
    """Entry point for the CLI script."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)


if __name__ == "__main__":
    cli_main()
