#!/usr/bin/env python3
"""
Check if all required dependencies for /full-plan are installed.

This script validates that all Python modules needed for the full planning
workflow are available. It returns a list of missing dependencies that need
to be installed.

Usage:
    python scripts/check-dependencies.py [--mode full|minimal|gemini]

Exit codes:
    0 - All dependencies satisfied
    1 - Missing required dependencies
    2 - Missing optional dependencies (warning only)
"""

import argparse
import importlib.util
import json
import sys
from typing import List, Tuple


# Required dependencies for core functionality
CORE_DEPENDENCIES = [
    ("dotenv", "python-dotenv", "Environment variable management"),
    ("requests", "requests", "HTTP requests for API calls"),
    ("yaml", "pyyaml", "YAML parsing for building blocks"),
    ("jinja2", "jinja2", "Template rendering"),
]

# Required for research and AI integration
RESEARCH_DEPENDENCIES = [
    ("openai", "openai", "OpenRouter API client"),
]

# Required for document processing
DOCUMENT_DEPENDENCIES = [
    ("markitdown", "markitdown", "Document conversion"),
    ("PIL", "pillow", "Image processing"),
    ("pptx", "python-pptx", "PowerPoint file handling"),
]

# Optional Google Gemini integration
GEMINI_DEPENDENCIES = [
    ("google.genai", "google-genai", "Google Generative AI SDK"),
]

# Optional performance enhancements
OPTIONAL_DEPENDENCIES = [
    ("aiofiles", "aiofiles", "Async file I/O"),
    ("httpx", "httpx", "Async HTTP client"),
]


def check_module(module_name: str) -> bool:
    """Check if a Python module is installed and importable."""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def check_dependencies(
    include_research: bool = True,
    include_documents: bool = True,
    include_gemini: bool = False,
    include_optional: bool = False,
) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    """
    Check all dependencies based on mode.

    Returns:
        Tuple of (missing_required, missing_optional)
    """
    required_deps = CORE_DEPENDENCIES.copy()

    if include_research:
        required_deps.extend(RESEARCH_DEPENDENCIES)

    if include_documents:
        required_deps.extend(DOCUMENT_DEPENDENCIES)

    optional_deps = []
    if include_gemini:
        optional_deps.extend(GEMINI_DEPENDENCIES)

    if include_optional:
        optional_deps.extend(OPTIONAL_DEPENDENCIES)

    # Check required dependencies
    missing_required = []
    for module_name, package_name, description in required_deps:
        if not check_module(module_name):
            missing_required.append((module_name, package_name, description))

    # Check optional dependencies
    missing_optional = []
    for module_name, package_name, description in optional_deps:
        if not check_module(module_name):
            missing_optional.append((module_name, package_name, description))

    return missing_required, missing_optional


def format_dependency_list(deps: List[Tuple[str, str, str]]) -> str:
    """Format dependency list for display."""
    if not deps:
        return "None"

    lines = []
    for _, package_name, description in deps:
        lines.append(f"  - {package_name:20s} ({description})")
    return "\n".join(lines)


def get_install_command(deps: List[Tuple[str, str, str]], use_uv: bool = False) -> str:
    """Generate installation command for missing dependencies."""
    if not deps:
        return ""

    packages = [package_name for _, package_name, _ in deps]

    if use_uv:
        return f"uv pip install {' '.join(packages)}"
    else:
        return f"pip install {' '.join(packages)}"


def main():
    parser = argparse.ArgumentParser(
        description="Check dependencies for claude-project-planner"
    )
    parser.add_argument(
        "--mode",
        choices=["minimal", "full", "gemini"],
        default="full",
        help="Dependency check mode (default: full)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--suggest-uv",
        action="store_true",
        help="Suggest uv commands instead of pip",
    )

    args = parser.parse_args()

    # Determine what to check based on mode
    include_research = args.mode in ["full", "gemini"]
    include_documents = args.mode in ["full"]
    include_gemini = args.mode == "gemini"
    include_optional = args.mode == "full"

    # Check dependencies
    missing_required, missing_optional = check_dependencies(
        include_research=include_research,
        include_documents=include_documents,
        include_gemini=include_gemini,
        include_optional=include_optional,
    )

    # Output results
    if args.json:
        result = {
            "status": "ok" if not missing_required else "missing_required",
            "missing_required": [
                {"module": m, "package": p, "description": d}
                for m, p, d in missing_required
            ],
            "missing_optional": [
                {"module": m, "package": p, "description": d}
                for m, p, d in missing_optional
            ],
            "install_command_pip": get_install_command(missing_required, use_uv=False),
            "install_command_uv": get_install_command(missing_required, use_uv=True),
        }
        print(json.dumps(result, indent=2))
    else:
        print("=" * 70)
        print("Claude Project Planner - Dependency Check")
        print("=" * 70)
        print(f"Mode: {args.mode}")
        print()

        if not missing_required and not missing_optional:
            print("✓ All dependencies satisfied!")
            return 0

        if missing_required:
            print("✗ Missing REQUIRED dependencies:")
            print(format_dependency_list(missing_required))
            print()
            print("To install missing dependencies:")
            if args.suggest_uv:
                print(f"  {get_install_command(missing_required, use_uv=True)}")
            else:
                print(f"  {get_install_command(missing_required, use_uv=False)}")
                print()
                print("Or using uv:")
                print(f"  {get_install_command(missing_required, use_uv=True)}")
            print()

        if missing_optional:
            print("⚠ Missing OPTIONAL dependencies:")
            print(format_dependency_list(missing_optional))
            print()
            print("To install optional dependencies:")
            if args.suggest_uv:
                print(f"  {get_install_command(missing_optional, use_uv=True)}")
            else:
                print(f"  {get_install_command(missing_optional, use_uv=False)}")
            print()

    # Exit with appropriate code
    if missing_required:
        return 1
    elif missing_optional:
        return 2
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
