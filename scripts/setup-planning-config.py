#!/usr/bin/env python3
"""
Interactive Planning Configuration Setup

Presents comprehensive UI for all planning options, eliminating need to remember flags.
Users discover all capabilities through guided setup flow.

Dynamically filters options based on available API keys.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


def check_api_keys() -> Dict[str, bool]:
    """
    Check which API keys are available in environment.

    Returns:
        Dict mapping provider name to availability
    """
    return {
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
        "perplexity": bool(os.getenv("PERPLEXITY_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "claude_max": bool(os.getenv("CLAUDE_CODE_OAUTH_TOKEN")),
    }


def generate_setup_questions(filter_unavailable: bool = True) -> List[Dict[str, Any]]:
    """
    Generate comprehensive setup questions for planning configuration.

    Dynamically filters options based on available API keys.

    Args:
        filter_unavailable: If True, mark unavailable options with warnings

    Returns:
        List of question configurations for AskUserQuestion
    """
    # Check which providers are available
    available = check_api_keys()
    has_research = available["gemini"] or available["openrouter"] or available["perplexity"]
    has_deep_research = available["gemini"]

    questions = [
        # Question 1: AI Provider Selection
        {
            "question": "Which AI provider should handle research and analysis tasks?",
            "header": "AI Provider",
            "multiSelect": False,
            "options": _filter_ai_provider_options(available, filter_unavailable)
        },

        # Question 2: Research Depth (NEW!)
        {
            "question": "How comprehensive should research be?",
            "header": "Research",
            "multiSelect": False,
            "options": _filter_research_depth_options(available, filter_unavailable)
        },

        # Question 3: Performance - Parallelization
        {
            "question": "Enable smart parallelization for faster execution?",
            "header": "Performance",
            "multiSelect": False,
            "options": [
                {
                    "label": "Yes - Full parallelization (Recommended)",
                    "description": "Run independent tasks concurrently. ~14% overall time savings, up to 60% in Phase 3 (feasibility analysis)"
                },
                {
                    "label": "No - Sequential execution",
                    "description": "Run all tasks in order. Simpler logs, more predictable. Use for first-time planning or learning workflow"
                }
            ]
        },

        # Question 4: Interactive Approval Gates
        {
            "question": "Review and approve each phase before continuing?",
            "header": "Workflow",
            "multiSelect": False,
            "options": [
                {
                    "label": "Yes - Interactive approval mode (Recommended)",
                    "description": "Pause after each phase for review. Ability to revise if direction needs adjustment. Best for critical projects"
                },
                {
                    "label": "No - Fully autonomous",
                    "description": "Run all 6 phases without pausing. Fastest approach. Review outputs at the end"
                }
            ]
        },

        # Question 5: Phase Selection
        {
            "question": "Which phases should be included in this plan?",
            "header": "Scope",
            "multiSelect": True,  # Allow selecting multiple phases
            "options": [
                {
                    "label": "Phase 1: Market Research (Required)",
                    "description": "Competitive analysis, market sizing, target audience research. Always recommended"
                },
                {
                    "label": "Phase 2: Architecture & Design (Required)",
                    "description": "Technical architecture, building blocks, system design. Cannot be skipped"
                },
                {
                    "label": "Phase 3: Feasibility & Costs (Recommended)",
                    "description": "Risk assessment, cost analysis, technical feasibility. Helps avoid expensive mistakes"
                },
                {
                    "label": "Phase 4: Implementation Planning (Required)",
                    "description": "Sprint planning, user stories, development roadmap. Cannot be skipped"
                },
                {
                    "label": "Phase 5: Go-to-Market Strategy",
                    "description": "Marketing campaign, launch strategy, content calendar. Skip for internal tools or APIs"
                },
                {
                    "label": "Phase 6: Plan Review (Recommended)",
                    "description": "Final validation, gap analysis, recommendations. Always recommended"
                }
            ]
        },

        # Question 6: Quality Assurance
        {
            "question": "Enable additional quality checks?",
            "header": "Quality",
            "multiSelect": True,  # Can enable multiple checks
            "options": [
                {
                    "label": "Multi-model architecture validation",
                    "description": "Validate architecture with 3 AI models (Gemini, GPT-4o, Claude) for consensus. Adds ~10 min, increases confidence"
                },
                {
                    "label": "Generate comprehensive diagrams",
                    "description": "Create C4, sequence, ERD, deployment diagrams for each phase. Visual documentation for all stakeholders"
                },
                {
                    "label": "Real-time research verification",
                    "description": "Cross-reference all technology recommendations with latest docs. Ensures current best practices"
                },
                {
                    "label": "None - Standard quality only",
                    "description": "Skip additional checks. Faster execution, still produces high-quality plans"
                }
            ]
        },

        # Question 7: Output Format
        {
            "question": "What output formats do you need?",
            "header": "Outputs",
            "multiSelect": True,
            "options": [
                {
                    "label": "Markdown files (Always included)",
                    "description": "All outputs in .md format. Always generated, works with Claude Code"
                },
                {
                    "label": "Generate final PDF report",
                    "description": "Compile all phases into professional PDF with table of contents, IEEE citations, cover page"
                },
                {
                    "label": "Generate PowerPoint presentation",
                    "description": "Executive summary slides for stakeholder presentation"
                },
                {
                    "label": "YAML building blocks",
                    "description": "Structured component specifications for automated code generation (Always included)"
                }
            ]
        }
    ]

    return questions


def _filter_ai_provider_options(available: Dict[str, bool], filter_unavailable: bool) -> List[Dict[str, str]]:
    """Filter AI provider options based on available keys."""
    options = []

    # Gemini Deep Research
    if available["gemini"]:
        options.append({
            "label": "Google Gemini Deep Research",
            "description": "✅ Available. 60-min comprehensive research, 1M token context. Best for Phase 1 competitive analysis"
        })
    elif filter_unavailable:
        options.append({
            "label": "Google Gemini Deep Research (Unavailable)",
            "description": "❌ Requires GEMINI_API_KEY. Run /project-planner:setup for setup guidance"
        })

    # Perplexity via OpenRouter
    if available["openrouter"]:
        options.append({
            "label": "Perplexity via OpenRouter (Recommended)",
            "description": "✅ Available. Fast 30-sec research. Good for most use cases"
        })
    elif filter_unavailable:
        options.append({
            "label": "Perplexity via OpenRouter (Unavailable)",
            "description": "❌ Requires OPENROUTER_API_KEY. Run /project-planner:setup for setup guidance"
        })

    # Perplexity Direct
    if available["perplexity"]:
        options.append({
            "label": "Perplexity Direct",
            "description": "✅ Available. Direct Perplexity access (skip OpenRouter 5.5% fee)"
        })

    # Auto-detect (always available if any research provider exists)
    if available["gemini"] or available["openrouter"] or available["perplexity"]:
        options.append({
            "label": "Auto-detect from available keys",
            "description": "Automatically use best available provider based on your API keys"
        })
    else:
        options.append({
            "label": "Auto-detect (No research providers configured)",
            "description": "❌ No research API keys found. Run /project-planner:setup to configure"
        })

    return options


def _filter_research_depth_options(available: Dict[str, bool], filter_unavailable: bool) -> List[Dict[str, str]]:
    """Filter research depth options based on available keys."""
    options = []
    has_deep_research = available["gemini"]
    has_fast_research = available["openrouter"] or available["perplexity"]

    # Balanced mode (requires Gemini for Deep Research)
    if has_deep_research:
        options.append({
            "label": "Balanced - Smart selection (Recommended)",
            "description": "✅ Deep Research for Phase 1 competitive analysis, Perplexity for quick lookups. Best quality/time tradeoff (~120 min total)"
        })
    elif filter_unavailable:
        options.append({
            "label": "Balanced (Requires Gemini)",
            "description": "❌ Needs GEMINI_API_KEY for Deep Research capability. Add key and re-run /project-planner:setup"
        })

    # Quick mode (only needs Perplexity)
    if has_fast_research:
        options.append({
            "label": "Quick - Perplexity only",
            "description": "✅ Fast 30-sec lookups for all research. Total time: ~30 min. Good for well-known tech stacks"
        })
    elif filter_unavailable:
        options.append({
            "label": "Quick - Perplexity only (Unavailable)",
            "description": "❌ Requires OPENROUTER_API_KEY or PERPLEXITY_API_KEY"
        })

    # Comprehensive mode (requires Gemini)
    if has_deep_research:
        options.append({
            "label": "Comprehensive - Deep Research for all",
            "description": "✅ 60-min Deep Research for every decision. Total time: ~4 hours. Best for novel/uncertain domains"
        })
    elif filter_unavailable:
        options.append({
            "label": "Comprehensive (Requires Gemini)",
            "description": "❌ Needs GEMINI_API_KEY. Add key and re-run /project-planner:setup"
        })

    # Auto mode (adapts to what's available)
    if has_deep_research and has_fast_research:
        options.append({
            "label": "Auto - Context-aware",
            "description": "✅ Intelligently choose based on query complexity. Uses Deep Research for competitive analysis"
        })
    elif has_fast_research:
        options.append({
            "label": "Auto - Context-aware (Perplexity only)",
            "description": "✅ Will use Perplexity for all research (Gemini not configured)"
        })
    elif has_deep_research:
        options.append({
            "label": "Auto - Context-aware (Gemini only)",
            "description": "✅ Will use Gemini Deep Research for all research (Perplexity not configured)"
        })
    else:
        options.append({
            "label": "Auto (No providers configured)",
            "description": "❌ No research providers available. Run /project-planner:setup"
        })

    return options


def parse_user_selections(answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Parse user answers into configuration object.

    Args:
        answers: Raw answers from AskUserQuestion

    Returns:
        Structured configuration for planning execution
    """
    config = {
        "ai_provider": "auto",
        "research_mode": "balanced",  # NEW
        "enable_parallelization": False,
        "interactive_mode": False,
        "phases": {
            "market_research": True,
            "architecture": True,
            "feasibility": True,
            "implementation": True,
            "marketing": False,
            "review": True
        },
        "quality_checks": {
            "multi_model_validation": False,
            "comprehensive_diagrams": False,
            "research_verification": False
        },
        "output_formats": {
            "markdown": True,  # Always
            "pdf": False,
            "pptx": False,
            "yaml": True  # Always
        }
    }

    # Parse AI Provider (Question 0)
    provider = answers.get("question_0", "")
    if "Gemini" in provider:
        config["ai_provider"] = "gemini"
    elif "Perplexity" in provider:
        config["ai_provider"] = "openrouter"
    else:
        config["ai_provider"] = "auto"

    # Parse Research Mode (Question 1) - NEW
    research_depth = answers.get("question_1", "")
    if "Balanced" in research_depth:
        config["research_mode"] = "balanced"
    elif "Quick" in research_depth:
        config["research_mode"] = "perplexity"
    elif "Comprehensive" in research_depth:
        config["research_mode"] = "deep_research"
    else:  # Auto
        config["research_mode"] = "auto"

    # Parse Parallelization (Question 2)
    parallel = answers.get("question_2", "")
    config["enable_parallelization"] = "Yes" in parallel

    # Parse Interactive Mode (Question 3)
    interactive = answers.get("question_3", "")
    config["interactive_mode"] = "Yes" in interactive

    # Parse Phase Selection (Question 4) - multiSelect
    phases = answers.get("question_4", "")
    config["phases"]["marketing"] = "Phase 5" in phases
    config["phases"]["feasibility"] = "Phase 3" in phases
    config["phases"]["review"] = "Phase 6" in phases
    # Phases 1, 2, 4 are always required

    # Parse Quality Checks (Question 5) - multiSelect
    quality = answers.get("question_5", "")
    config["quality_checks"]["multi_model_validation"] = "Multi-model" in quality
    config["quality_checks"]["comprehensive_diagrams"] = "comprehensive diagrams" in quality
    config["quality_checks"]["research_verification"] = "Real-time research" in quality

    # Parse Output Formats (Question 6) - multiSelect
    outputs = answers.get("question_6", "")
    config["output_formats"]["pdf"] = "PDF report" in outputs
    config["output_formats"]["pptx"] = "PowerPoint" in outputs

    return config


def save_config(config: Dict[str, Any], project_name: str) -> Path:
    """Save configuration to temp file for planning execution."""
    config_file = Path(f".{project_name}-config.json")
    with open(config_file, "w") as f:
        json.dump(config, indent=2, fp=f)
    return config_file


def display_config_summary(config: Dict[str, Any]) -> str:
    """Generate human-readable configuration summary."""
    research_mode_display = {
        "balanced": "BALANCED (Deep Research for Phase 1, Perplexity for others)",
        "perplexity": "QUICK (Perplexity only)",
        "deep_research": "COMPREHENSIVE (Deep Research for all)",
        "auto": "AUTO (Context-aware selection)"
    }

    lines = [
        "=" * 70,
        "Planning Configuration Summary",
        "=" * 70,
        "",
        f"AI Provider: {config['ai_provider'].upper()}",
        f"Research Mode: {research_mode_display.get(config['research_mode'], config['research_mode'].upper())}",
        f"Parallelization: {'ENABLED' if config['enable_parallelization'] else 'DISABLED'}",
        f"Interactive Mode: {'ENABLED' if config['interactive_mode'] else 'DISABLED'}",
        "",
        "Phases:",
    ]

    phase_names = {
        "market_research": "  ✓ Phase 1: Market Research",
        "architecture": "  ✓ Phase 2: Architecture & Design",
        "feasibility": "  {} Phase 3: Feasibility & Costs",
        "implementation": "  ✓ Phase 4: Implementation Planning",
        "marketing": "  {} Phase 5: Go-to-Market Strategy",
        "review": "  {} Phase 6: Plan Review"
    }

    for key, name in phase_names.items():
        if config["phases"][key]:
            lines.append(name.format("✓"))
        else:
            lines.append(name.format("✗").replace("✓", "✗"))

    lines.append("")
    lines.append("Quality Checks:")

    checks = config["quality_checks"]
    if checks["multi_model_validation"]:
        lines.append("  ✓ Multi-model validation")
    if checks["comprehensive_diagrams"]:
        lines.append("  ✓ Comprehensive diagrams")
    if checks["research_verification"]:
        lines.append("  ✓ Real-time research verification")
    if not any(checks.values()):
        lines.append("  ✗ None (standard quality only)")

    lines.append("")
    lines.append("Output Formats:")
    lines.append("  ✓ Markdown (always)")
    lines.append("  ✓ YAML building blocks (always)")
    if config["output_formats"]["pdf"]:
        lines.append("  ✓ PDF report")
    if config["output_formats"]["pptx"]:
        lines.append("  ✓ PowerPoint presentation")

    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Generate setup questions JSON for AskUserQuestion."""
    questions = generate_setup_questions()

    # Output JSON for use in command
    print(json.dumps({"questions": questions}, indent=2))


if __name__ == "__main__":
    main()
