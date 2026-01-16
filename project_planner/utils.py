"""Utility functions for project planner."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import re


def find_existing_projects(output_folder: Path) -> List[Dict[str, Any]]:
    """
    Get all existing project directories with their metadata.

    Args:
        output_folder: Path to the project outputs folder.

    Returns:
        List of dicts with path, name, and timestamp info.
    """
    projects = []
    if not output_folder.exists():
        return projects

    for project_dir in output_folder.iterdir():
        if project_dir.is_dir():
            projects.append({
                'path': project_dir,
                'name': project_dir.name,
                'mtime': project_dir.stat().st_mtime
            })

    # Sort by modification time (most recent first)
    projects.sort(key=lambda x: x['mtime'], reverse=True)
    return projects


def detect_project_reference(user_input: str, existing_projects: List[Dict[str, Any]]) -> Optional[Path]:
    """
    Try to detect if the user is referring to an existing project.

    Args:
        user_input: User's input text.
        existing_projects: List of existing project dictionaries.

    Returns:
        The project path if found, None otherwise.
    """
    if not existing_projects:
        return None

    user_input_lower = user_input.lower()

    # Keywords that suggest continuing with existing work
    continuation_keywords = [
        "continue", "update", "edit", "revise", "modify", "change",
        "add to", "fix", "improve", "review", "the project", "this project",
        "my project", "current project", "previous project", "last project",
        "the plan", "this plan", "my plan", "current plan",
        "architecture", "the architecture", "sprint", "the sprint",
        "building blocks", "components", "cost analysis", "risk assessment",
        "add component", "add sprint", "update timeline"
    ]

    # Keywords that suggest searching for/looking up an existing project
    search_keywords = [
        "look for", "find", "search for", "where is", "which project",
        "show me", "open", "locate", "get"
    ]

    # Keywords that explicitly indicate a new project
    new_project_keywords = [
        "new project", "start fresh", "start afresh", "create new",
        "different project", "another project", "plan a new",
        "new plan", "fresh start", "from scratch"
    ]

    # If user explicitly wants a new project, return None
    if any(keyword in user_input_lower for keyword in new_project_keywords):
        return None

    # Check if user mentions continuation or search keywords
    has_continuation_keyword = any(keyword in user_input_lower for keyword in continuation_keywords)
    has_search_keyword = any(keyword in user_input_lower for keyword in search_keywords)

    # Try to find project by name/topic keywords
    best_match = None
    best_match_score = 0

    for project in existing_projects:
        project_name = project['name'].lower()
        # Extract topic from directory name (format: YYYYMMDD_HHMMSS_topic)
        parts = project_name.split('_', 2)
        if len(parts) >= 3:
            topic = parts[2].replace('_', ' ')
            # Check if topic words appear in user input
            topic_words = topic.split()
            matches = sum(1 for word in topic_words if len(word) > 3 and word in user_input_lower)

            # Keep track of best match
            if matches > best_match_score:
                best_match_score = matches
                best_match = project['path']

            # If we have a strong match (2+ topic words), return it
            # This is especially important for search keywords
            if matches >= 2 and (has_search_keyword or has_continuation_keyword):
                return project['path']

    # If we found any match with search keywords, return the best one
    if has_search_keyword and best_match_score > 0:
        return best_match

    # If user used continuation keywords but no specific match, use most recent project
    if has_continuation_keyword and existing_projects:
        return existing_projects[0]['path']

    return None


def scan_project_directory(project_dir: Path) -> Dict[str, Any]:
    """
    Scan a project directory and collect all file information.

    Args:
        project_dir: Path to the project directory.

    Returns:
        Dictionary with comprehensive file information.
    """
    result = {
        # Specifications
        'project_spec': None,
        'technical_spec': None,
        'api_spec': None,
        'data_model': None,

        # Research outputs
        'market_research': None,
        'competitive_analysis': None,
        'technology_research': None,

        # Analysis outputs
        'feasibility_analysis': None,
        'cost_analysis': None,
        'risk_assessment': None,
        'roi_projections': None,

        # Planning outputs
        'sprint_plan': None,
        'timeline': None,
        'building_blocks': None,
        'component_breakdown': None,  # Alias for building_blocks (api.py compatibility)

        # Components
        'components': [],  # List of component directories

        # Diagrams
        'diagrams': [],

        # Meta files
        'progress_log': None,
        'summary': None,
        'plan_review': None,

        # Data and sources
        'data': [],
        'sources': [],

        # Legacy support (for backwards compatibility)
        'pdf_final': None,
        'tex_final': None,
        'pdf_drafts': [],
        'tex_drafts': [],
        'bibliography': None,
        'figures': [],
    }

    if not project_dir.exists():
        return result

    # Scan specifications/ directory
    specs_dir = project_dir / "specifications"
    if specs_dir.exists():
        for file in specs_dir.iterdir():
            if file.is_file():
                name_lower = file.name.lower()
                if 'project' in name_lower and 'spec' in name_lower:
                    result['project_spec'] = str(file)
                elif 'technical' in name_lower or 'tech' in name_lower:
                    result['technical_spec'] = str(file)
                elif 'api' in name_lower:
                    result['api_spec'] = str(file)
                elif 'data' in name_lower and 'model' in name_lower:
                    result['data_model'] = str(file)

    # Scan research/ directory
    research_dir = project_dir / "research"
    if research_dir.exists():
        for file in research_dir.iterdir():
            if file.is_file():
                name_lower = file.name.lower()
                if 'market' in name_lower:
                    result['market_research'] = str(file)
                elif 'competitive' in name_lower or 'competitor' in name_lower:
                    result['competitive_analysis'] = str(file)
                elif 'technology' in name_lower or 'tech' in name_lower:
                    result['technology_research'] = str(file)

    # Scan analysis/ directory
    analysis_dir = project_dir / "analysis"
    if analysis_dir.exists():
        for file in analysis_dir.iterdir():
            if file.is_file():
                name_lower = file.name.lower()
                if 'feasibility' in name_lower:
                    result['feasibility_analysis'] = str(file)
                elif 'cost' in name_lower:
                    result['cost_analysis'] = str(file)
                elif 'risk' in name_lower:
                    result['risk_assessment'] = str(file)
                elif 'roi' in name_lower:
                    result['roi_projections'] = str(file)

    # Scan planning/ directory
    planning_dir = project_dir / "planning"
    if planning_dir.exists():
        for file in planning_dir.iterdir():
            if file.is_file():
                name_lower = file.name.lower()
                if 'sprint' in name_lower:
                    result['sprint_plan'] = str(file)
                elif 'timeline' in name_lower:
                    result['timeline'] = str(file)

    # Scan components/ directory
    components_dir = project_dir / "components"
    if components_dir.exists():
        # Look for building_blocks file
        blocks_file = components_dir / "building_blocks.yaml"
        if blocks_file.exists():
            result['building_blocks'] = str(blocks_file)
            result['component_breakdown'] = str(blocks_file)  # Alias for api.py compatibility
        else:
            blocks_file = components_dir / "building_blocks.md"
            if blocks_file.exists():
                result['building_blocks'] = str(blocks_file)
                result['component_breakdown'] = str(blocks_file)  # Alias for api.py compatibility

        # Scan for component subdirectories and component_breakdown file
        for item in components_dir.iterdir():
            if item.is_dir():
                result['components'].append(str(item))
            elif item.is_file() and 'component_breakdown' in item.name.lower():
                result['component_breakdown'] = str(item)

    # Scan diagrams/ directory
    diagrams_dir = project_dir / "diagrams"
    if diagrams_dir.exists():
        for file in sorted(diagrams_dir.iterdir()):
            if file.is_file():
                result['diagrams'].append(str(file))

    # Scan data/ directory
    data_dir = project_dir / "data"
    if data_dir.exists():
        for file in sorted(data_dir.iterdir()):
            if file.is_file():
                result['data'].append(str(file))

    # Scan sources/ directory
    sources_dir = project_dir / "sources"
    if sources_dir.exists():
        for file in sorted(sources_dir.iterdir()):
            if file.is_file():
                result['sources'].append(str(file))

    # Check for progress.md and SUMMARY.md
    progress_file = project_dir / "progress.md"
    if progress_file.exists():
        result['progress_log'] = str(progress_file)

    summary_file = project_dir / "SUMMARY.md"
    if summary_file.exists():
        result['summary'] = str(summary_file)

    plan_review_file = project_dir / "PLAN_REVIEW.md"
    if plan_review_file.exists():
        result['plan_review'] = str(plan_review_file)

    # Legacy support: Scan final/ directory
    final_dir = project_dir / "final"
    if final_dir.exists():
        for file in final_dir.iterdir():
            if file.is_file():
                if file.suffix == '.pdf':
                    result['pdf_final'] = str(file)
                elif file.suffix == '.tex':
                    result['tex_final'] = str(file)

    # Legacy support: Scan drafts/ directory
    drafts_dir = project_dir / "drafts"
    if drafts_dir.exists():
        for file in sorted(drafts_dir.iterdir()):
            if file.is_file():
                if file.suffix == '.pdf':
                    result['pdf_drafts'].append(str(file))
                elif file.suffix == '.tex':
                    result['tex_drafts'].append(str(file))

    # Legacy support: Scan references/ directory
    references_dir = project_dir / "references"
    if references_dir.exists():
        bib_file = references_dir / "references.bib"
        if bib_file.exists():
            result['bibliography'] = str(bib_file)

    # Legacy support: Scan figures/ directory
    figures_dir = project_dir / "figures"
    if figures_dir.exists():
        for file in sorted(figures_dir.iterdir()):
            if file.is_file():
                result['figures'].append(str(file))

    return result


def count_building_blocks(blocks_file: Optional[str]) -> int:
    """
    Count the number of building blocks in a YAML or Markdown file.

    Args:
        blocks_file: Path to the building blocks file.

    Returns:
        Number of building blocks found.
    """
    if not blocks_file or not Path(blocks_file).exists():
        return 0

    try:
        with open(blocks_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # For YAML files, count '- name:' entries
            if blocks_file.endswith('.yaml') or blocks_file.endswith('.yml'):
                matches = re.findall(r'^\s*-\s*name:', content, re.MULTILINE)
                return len(matches)

            # For Markdown files, count ## Component or ### Block headers
            matches = re.findall(r'^#{2,3}\s+(Component|Block|Building Block):', content, re.MULTILINE | re.IGNORECASE)
            return len(matches)
    except (FileNotFoundError, OSError, UnicodeDecodeError, ValueError):
        # File not found, permission denied, encoding error, or parsing error
        return 0


def count_sprints(sprint_file: Optional[str]) -> int:
    """
    Count the number of sprints in a sprint plan file.

    Args:
        sprint_file: Path to the sprint plan file.

    Returns:
        Number of sprints found.
    """
    if not sprint_file or not Path(sprint_file).exists():
        return 0

    try:
        with open(sprint_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # For YAML files, count 'sprint_number:' entries
            if sprint_file.endswith('.yaml') or sprint_file.endswith('.yml'):
                matches = re.findall(r'sprint_number:', content)
                return len(matches)

            # For Markdown files, count ## Sprint headers
            matches = re.findall(r'^#{2,3}\s*Sprint\s*\d+', content, re.MULTILINE | re.IGNORECASE)
            return len(matches)
    except (FileNotFoundError, OSError, UnicodeDecodeError, ValueError):
        # File not found, permission denied, encoding error, or parsing error
        return 0


def extract_project_name(project_dir: Path) -> Optional[str]:
    """
    Extract project name from directory or spec file.

    Args:
        project_dir: Path to the project directory.

    Returns:
        Project name string, or None if not found.
    """
    # First try to extract from directory name
    dir_name = project_dir.name
    parts = dir_name.split('_', 2)
    if len(parts) >= 3:
        return parts[2].replace('_', ' ').title()

    # Try to find in project spec
    spec_file = project_dir / "specifications" / "project_spec.md"
    if spec_file.exists():
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for # Project Name or name: in YAML frontmatter
                match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
                if match:
                    return match.group(1).strip()
        except (FileNotFoundError, OSError, UnicodeDecodeError):
            # File not found, permission denied, or encoding error
            pass

    return None


# Backwards compatibility aliases
find_existing_papers = find_existing_projects
detect_paper_reference = detect_project_reference
scan_paper_directory = scan_project_directory


def count_citations_in_bib(bib_file: Optional[str]) -> int:
    """
    Count the number of citations in a BibTeX file.

    Args:
        bib_file: Path to the .bib file.

    Returns:
        Number of citations found.
    """
    if not bib_file or not Path(bib_file).exists():
        return 0

    try:
        with open(bib_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Count @article, @book, @inproceedings, etc.
            matches = re.findall(r'@\w+\s*{', content)
            return len(matches)
    except (FileNotFoundError, OSError, UnicodeDecodeError, ValueError):
        # File not found, permission denied, encoding error, or parsing error
        return 0


def extract_citation_style(bib_file: Optional[str]) -> str:
    """
    Try to extract citation style from BibTeX file or paper metadata.

    Args:
        bib_file: Path to the .bib file.

    Returns:
        Citation style name (default: "BibTeX").
    """
    return "BibTeX"


def count_words_in_tex(tex_file: Optional[str]) -> Optional[int]:
    """
    Estimate word count in a LaTeX file.

    Args:
        tex_file: Path to the .tex file.

    Returns:
        Estimated word count, or None if file doesn't exist.
    """
    if not tex_file or not Path(tex_file).exists():
        return None

    try:
        with open(tex_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # Remove LaTeX commands
            content = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', '', content)
            # Remove comments
            content = re.sub(r'%.*', '', content)
            # Remove special characters
            content = re.sub(r'[{}$\\]', '', content)

            # Count words
            words = content.split()
            return len(words)
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        # File not found, permission denied, or encoding error
        return None


def extract_title_from_tex(tex_file: Optional[str]) -> Optional[str]:
    """
    Extract title from a LaTeX file.

    Args:
        tex_file: Path to the .tex file.

    Returns:
        Title string, or None if not found.
    """
    if not tex_file or not Path(tex_file).exists():
        return None

    try:
        with open(tex_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # Look for \title{...}
            match = re.search(r'\\title\s*\{([^}]+)\}', content)
            if match:
                title = match.group(1)
                # Clean up LaTeX commands in title
                title = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', '', title)
                return title.strip()
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        # File not found, permission denied, or encoding error
        pass

    return None
