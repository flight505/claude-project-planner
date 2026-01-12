#!/usr/bin/env python3
"""
Parse project planning input template and extract structured data.

This script reads a filled-out plan-input template and extracts all
project information into a structured JSON format for use by the planner.

Usage:
    python scripts/parse-plan-input.py <input-file> [--output <output-file>] [--validate]

Exit codes:
    0 - Success
    1 - Parsing error
    2 - Validation error (missing required fields)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_markdown_field(content: str, field_name: str, multiline: bool = False) -> Optional[str]:
    """
    Extract a field value from markdown content.

    Args:
        content: Full markdown content
        field_name: Field name to extract (e.g., "Project Name")
        multiline: Whether field can span multiple lines

    Returns:
        Extracted value or None if not found
    """
    # Pattern for single-line fields: **Field Name**: value
    pattern = rf'\*\*{re.escape(field_name)}\*\*:\s*(.+?)(?:\n|$)'

    if multiline:
        # For multiline fields, capture until next ## or **Field**
        pattern = rf'\*\*{re.escape(field_name)}\*\*:\s*\n(.*?)(?=\n##|\n\*\*[A-Z]|$)'
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    else:
        match = re.search(pattern, content)

    if match:
        value = match.group(1).strip()
        # Remove placeholder markers
        if value.startswith('[') and value.endswith(']'):
            return None  # Still placeholder
        return value

    return None


def parse_list_items(content: str, section_title: str) -> List[str]:
    """
    Extract numbered or bulleted list items from a section.

    Args:
        content: Full markdown content
        section_title: Section title (e.g., "Success Metrics")

    Returns:
        List of extracted items
    """
    # Find the section
    section_pattern = rf'\*\*{re.escape(section_title)}\*\*:\s*\n(.*?)(?=\n##|\n\*\*[A-Z]|$)'
    section_match = re.search(section_pattern, content, re.DOTALL | re.MULTILINE)

    if not section_match:
        return []

    section_content = section_match.group(1)

    # Extract list items (numbered or bulleted)
    items = []
    for line in section_content.split('\n'):
        line = line.strip()
        # Match numbered lists: 1. Item or bulleted lists: - Item
        if re.match(r'^\d+\.\s+', line) or line.startswith('- '):
            item = re.sub(r'^\d+\.\s+|-\s+', '', line).strip()
            # Skip placeholders
            if not (item.startswith('[') and item.endswith(']')):
                items.append(item)

    return items


def extract_section_content(content: str, section_title: str) -> str:
    """
    Extract all content from a markdown section.

    Args:
        content: Full markdown content
        section_title: Section heading (e.g., "## Project Overview")

    Returns:
        Section content as string
    """
    # Pattern to match section header and capture content until next section
    pattern = rf'^##\s+{re.escape(section_title)}.*?\n(.*?)(?=^##\s+|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if match:
        return match.group(1).strip()

    return ""


def parse_plan_input(file_path: Path) -> Dict[str, Any]:
    """
    Parse the plan input file and extract all fields.

    Args:
        file_path: Path to input file

    Returns:
        Dictionary with extracted data
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract all fields
    data = {
        "project_name": parse_markdown_field(content, "Project Name"),
        "description": parse_markdown_field(content, "Description", multiline=True),

        "target_audience": {
            "primary_users": parse_markdown_field(content, "Primary Users"),
            "user_personas": parse_markdown_field(content, "User Personas", multiline=True),
            "geographic_focus": parse_markdown_field(content, "Geographic Focus"),
            "market_size": parse_markdown_field(content, "Market Size"),
        },

        "goals": {
            "primary_objective": parse_markdown_field(content, "Primary Objective", multiline=True),
            "success_metrics": parse_list_items(content, "Success Metrics"),
            "business_model": parse_markdown_field(content, "Business Model", multiline=True),
        },

        "technical_requirements": {
            "core_features": parse_list_items(content, "Core Features"),
            "integrations": parse_markdown_field(content, "Integrations Required", multiline=True),
            "data_requirements": parse_markdown_field(content, "Data Requirements", multiline=True),
            "compliance_security": parse_markdown_field(content, "Compliance/Security", multiline=True),
        },

        "constraints": {
            "timeline": parse_markdown_field(content, "Timeline", multiline=True),
            "budget": parse_markdown_field(content, "Budget", multiline=True),
            "technical_constraints": parse_markdown_field(content, "Technical Constraints", multiline=True),
            "team": parse_markdown_field(content, "Team", multiline=True),
            "scalability": parse_markdown_field(content, "Scalability", multiline=True),
        },

        "technology_preferences": {
            "preferred_stack": parse_markdown_field(content, "Preferred Technology Stack", multiline=True),
            "cloud_provider": parse_markdown_field(content, "Cloud Provider Preference"),
            "development_approach": parse_markdown_field(content, "Development Approach", multiline=True),
            "existing_infrastructure": parse_markdown_field(content, "Existing Infrastructure", multiline=True),
        },

        "go_to_market": {
            "launch_strategy": parse_markdown_field(content, "Launch Strategy", multiline=True),
            "marketing_channels": parse_markdown_field(content, "Marketing Channels", multiline=True),
            "competition": parse_markdown_field(content, "Competition", multiline=True),
            "pricing_strategy": parse_markdown_field(content, "Pricing Strategy", multiline=True),
        },

        "additional_context": {
            "problem_statement": parse_markdown_field(content, "Problem Statement", multiline=True),
            "unique_value_prop": parse_markdown_field(content, "Unique Value Proposition", multiline=True),
            "key_assumptions": parse_markdown_field(content, "Key Assumptions", multiline=True),
            "risks_concerns": parse_markdown_field(content, "Risks & Concerns", multiline=True),
        },
    }

    return data


def validate_required_fields(data: Dict[str, Any]) -> List[str]:
    """
    Validate that all required fields are present.

    Args:
        data: Parsed data dictionary

    Returns:
        List of missing required fields
    """
    missing = []

    # Check top-level required fields
    if not data.get("project_name"):
        missing.append("Project Name")
    if not data.get("description"):
        missing.append("Description")

    # Check nested required fields
    if not data.get("target_audience", {}).get("primary_users"):
        missing.append("Primary Users")

    if not data.get("goals", {}).get("primary_objective"):
        missing.append("Primary Objective")

    if not data.get("technical_requirements", {}).get("core_features"):
        missing.append("Core Features")

    return missing


def generate_context_summary(data: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary for context.

    Args:
        data: Parsed data dictionary

    Returns:
        Formatted summary string
    """
    lines = []

    lines.append(f"# {data.get('project_name', 'Untitled Project')}")
    lines.append("")

    if data.get("description"):
        lines.append("## Description")
        lines.append(data["description"])
        lines.append("")

    if data.get("target_audience", {}).get("primary_users"):
        lines.append(f"**Target Users**: {data['target_audience']['primary_users']}")
        lines.append("")

    if data.get("goals", {}).get("primary_objective"):
        lines.append(f"**Primary Goal**: {data['goals']['primary_objective']}")
        lines.append("")

    if data.get("technical_requirements", {}).get("core_features"):
        lines.append("**Core Features**:")
        for i, feature in enumerate(data["technical_requirements"]["core_features"], 1):
            lines.append(f"{i}. {feature}")
        lines.append("")

    if data.get("constraints", {}).get("budget"):
        lines.append(f"**Budget**: {data['constraints']['budget']}")

    if data.get("constraints", {}).get("timeline"):
        lines.append(f"**Timeline**: {data['constraints']['timeline']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Parse project planning input template"
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to filled-out plan input file"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output JSON file (default: print to stdout)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate required fields and exit with error if missing"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Output human-readable summary instead of JSON"
    )

    args = parser.parse_args()

    # Check input file exists
    if not args.input_file.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    # Parse input
    data = parse_plan_input(args.input_file)

    # Validate if requested
    if args.validate:
        missing = validate_required_fields(data)
        if missing:
            print("Error: Missing required fields:", file=sys.stderr)
            for field in missing:
                print(f"  - {field}", file=sys.stderr)
            sys.exit(2)

    # Output
    if args.summary:
        summary = generate_context_summary(data)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(summary)
        else:
            print(summary)
    else:
        # Output JSON
        output_json = json.dumps(data, indent=2, ensure_ascii=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_json)
            print(f"✓ Parsed data saved to: {args.output}")
        else:
            print(output_json)

    # Exit successfully
    sys.exit(0)


if __name__ == "__main__":
    main()
