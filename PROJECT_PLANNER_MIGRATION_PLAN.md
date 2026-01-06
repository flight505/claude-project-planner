# Project Planner Plugin Migration Plan

This document provides detailed code modification plans for transforming `claude-scientific-writer` into a `project-planner` plugin.

---

## 1. Package Rename Plan

### Directory Rename
```
scientific_writer/  ->  project_planner/
```

### Files Requiring Rename

| Current Path | New Path |
|--------------|----------|
| `scientific_writer/__init__.py` | `project_planner/__init__.py` |
| `scientific_writer/api.py` | `project_planner/api.py` |
| `scientific_writer/cli.py` | `project_planner/cli.py` |
| `scientific_writer/core.py` | `project_planner/core.py` |
| `scientific_writer/models.py` | `project_planner/models.py` |
| `scientific_writer/utils.py` | `project_planner/utils.py` |
| `scientific_writer/.claude/` | `project_planner/.claude/` |

### Import Statement Changes

#### `__init__.py`
```python
# OLD
from .api import generate_paper
from .models import ProgressUpdate, TextUpdate, PaperResult, PaperMetadata, PaperFiles, TokenUsage

# NEW
from .api import generate_project
from .models import ProgressUpdate, TextUpdate, ProjectResult, ProjectMetadata, ProjectFiles, TokenUsage
```

#### `api.py`
```python
# OLD
from .core import (
    get_api_key,
    load_system_instructions,
    ensure_output_folder,
    get_data_files,
    process_data_files,
    create_data_context_message,
    setup_claude_skills,
)
from .models import ProgressUpdate, TextUpdate, PaperResult, PaperMetadata, PaperFiles, TokenUsage
from .utils import (
    scan_paper_directory,
    count_citations_in_bib,
    extract_citation_style,
    count_words_in_tex,
    extract_title_from_tex,
)

# NEW
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
from .utils import (
    scan_project_directory,
    count_components,
    extract_architecture_type,
    count_services,
    extract_project_name,
)
```

#### `cli.py`
```python
# OLD
from .core import (...)
from .utils import find_existing_papers, detect_paper_reference, scan_paper_directory

# NEW
from .core import (...)
from .utils import find_existing_projects, detect_project_reference, scan_project_directory
```

### pyproject.toml Updates

```toml
# OLD
[project]
name = "scientific-writer"
version = "2.10.2"
description = "Deep research and writing tool - combines AI-driven deep research with well-formatted written outputs. Generates publication-ready scientific documents with verified citations."

[project.scripts]
scientific-writer = "scientific_writer.cli:cli_main"

[tool.hatch.build.targets.wheel]
packages = ["scientific_writer"]

# NEW
[project]
name = "project-planner"
version = "1.0.0"
description = "AI-powered project planning tool - generates comprehensive software architecture documents, sprint plans, building blocks, service cost analysis, and implementation roadmaps."

[project.scripts]
project-planner = "project_planner.cli:cli_main"

[tool.hatch.build.targets.wheel]
packages = ["project_planner"]
```

### Dependencies Update (pyproject.toml)

```toml
# OLD
dependencies = [
    "claude-agent-sdk>=0.1.0",
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
    "pymupdf>=1.24.0",  # For PDF to image conversion
]

# NEW
dependencies = [
    "claude-agent-sdk>=0.1.0",
    "python-dotenv>=1.0.0",
    "requests>=2.31.0",
    "pyyaml>=6.0.0",      # For YAML config files
    "jinja2>=3.1.0",      # For template rendering
]
```

---

## 2. api.py Modifications

### New Function Signature

```python
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
from .utils import (
    scan_project_directory,
    count_components,
    extract_architecture_type,
    count_services,
    extract_project_name,
)


# Model mapping for effort levels
EFFORT_LEVEL_MODELS = {
    "low": "claude-haiku-4-5",
    "medium": "claude-sonnet-4-5",
    "high": "claude-opus-4-5",
}


# NEW: Progress stages for project planning workflow
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


async def generate_project(
    query: str,
    output_dir: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    effort_level: Literal["low", "medium", "high"] = "medium",
    data_files: Optional[List[str]] = None,
    cwd: Optional[str] = None,
    track_token_usage: bool = False,
    auto_continue: bool = True,
    project_type: Literal["full", "architecture", "sprint", "cost", "risk"] = "full",
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Generate a software project plan asynchronously with progress updates.

    This is a stateless async generator that yields progress updates during
    execution and a final comprehensive result with all project planning details.
    Supports full project plans, architecture docs, sprint plans, cost analysis, and risk assessments.

    Args:
        query: The project planning request (e.g., "Create architecture for a microservices e-commerce platform",
               "Generate sprint plan for mobile app MVP", "Analyze AWS costs for SaaS application")
        output_dir: Optional custom output directory (defaults to cwd/planning_outputs)
        api_key: Optional Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        model: Optional explicit Claude model to use. If provided, overrides effort_level.
        effort_level: Effort level that determines the model to use (default: "medium"):
            - "low": Uses Claude Haiku 4.5 (fastest, most economical)
            - "medium": Uses Claude Sonnet 4.5 (balanced) [default]
            - "high": Uses Claude Opus 4.5 (most capable)
        data_files: Optional list of data file paths to include (requirements docs, existing code, etc.)
        cwd: Optional working directory (defaults to package parent directory)
        track_token_usage: If True, track and return token usage in the final result
        auto_continue: If True (default), the agent will not stop on its own and will
            continue working until the task is complete. Set to False to allow
            normal stopping behavior.
        project_type: Type of project planning output to generate:
            - "full": Complete project plan with all components (default)
            - "architecture": Architecture document only
            - "sprint": Sprint planning only
            - "cost": Service cost analysis only
            - "risk": Risk assessment only

    Yields:
        Progress updates (dict with type="progress") during execution
        Final result (dict with type="result") containing all project planning information

    Example:
        ```python
        async for update in generate_project("Create architecture for a real-time chat application"):
            if update["type"] == "progress":
                print(f"[{update['stage']}] {update['message']}")
            else:
                print(f"Project plan created: {update['project_directory']}")
                print(f"Architecture: {update['files']['architecture_doc']}")

        # With token usage tracking:
        async for update in generate_project("Plan microservices migration", track_token_usage=True):
            if update["type"] == "result":
                print(f"Token usage: {update.get('token_usage')}")
        ```
    """
    # ... implementation follows similar pattern to generate_paper ...
```

### New `_analyze_progress` Function

```python
def _analyze_progress(text: str, current_stage: str) -> tuple:
    """
    Analyze text for project planning stage transitions.

    Returns:
        Tuple of (stage, message) - returns current stage if no transition detected
    """
    text_lower = text.lower()

    current_idx = PROGRESS_STAGES.index(current_stage) if current_stage in PROGRESS_STAGES else 0

    # Detect stage transitions based on keywords
    if current_idx < PROGRESS_STAGES.index("requirements"):
        if "requirement" in text_lower or "user stor" in text_lower or "acceptance criteria" in text_lower:
            return "requirements", "Analyzing requirements"

    if current_idx < PROGRESS_STAGES.index("research"):
        if "research" in text_lower or "pattern" in text_lower or "best practice" in text_lower:
            return "research", "Researching architecture patterns"

    if current_idx < PROGRESS_STAGES.index("architecture"):
        if "architecture" in text_lower or "system design" in text_lower or "component diagram" in text_lower:
            return "architecture", "Designing system architecture"

    if current_idx < PROGRESS_STAGES.index("components"):
        if "building block" in text_lower or "component" in text_lower or "module" in text_lower:
            return "components", "Defining building blocks"

    if current_idx < PROGRESS_STAGES.index("cost_analysis"):
        if "cost" in text_lower or "pricing" in text_lower or "budget" in text_lower:
            return "cost_analysis", "Analyzing service costs"

    if current_idx < PROGRESS_STAGES.index("sprint_planning"):
        if "sprint" in text_lower or "milestone" in text_lower or "timeline" in text_lower:
            return "sprint_planning", "Creating sprint plan"

    if current_idx < PROGRESS_STAGES.index("risk_assessment"):
        if "risk" in text_lower or "mitigation" in text_lower or "contingency" in text_lower:
            return "risk_assessment", "Assessing risks"

    if current_idx < PROGRESS_STAGES.index("documentation"):
        if "document" in text_lower or "readme" in text_lower or "summary" in text_lower:
            return "documentation", "Writing documentation"

    if current_idx < PROGRESS_STAGES.index("complete"):
        if "complete" in text_lower or "finished" in text_lower or "done" in text_lower:
            return "complete", "Finalizing output"

    return current_stage, None
```

### New `_analyze_tool_use` Function

```python
def _analyze_tool_use(tool_name: str, tool_input: Dict[str, Any], current_stage: str) -> tuple:
    """
    Analyze tool usage to provide dynamic, context-aware progress updates.
    """
    file_path = tool_input.get("file_path", tool_input.get("path", ""))
    command = tool_input.get("command", "")
    filename = Path(file_path).name if file_path else ""

    # Read tool - detect what's being read
    if tool_name.lower() == "read":
        if ".yaml" in file_path or ".yml" in file_path:
            return ("requirements", f"Reading configuration: {filename}")
        elif "requirements" in file_path.lower() or "spec" in file_path.lower():
            return ("requirements", f"Analyzing requirements: {filename}")
        elif "architecture" in file_path.lower():
            return ("architecture", f"Reading architecture: {filename}")
        elif ".json" in file_path:
            return ("research", f"Reading data: {filename}")
        return (current_stage, f"Reading {filename}")

    # Write tool - detect what's being written
    elif tool_name.lower() == "write":
        if "architecture" in filename.lower():
            return ("architecture", "Writing architecture document")
        elif "sprint" in filename.lower() or "plan" in filename.lower():
            return ("sprint_planning", "Creating sprint plan")
        elif "cost" in filename.lower() or "budget" in filename.lower():
            return ("cost_analysis", "Writing cost analysis")
        elif "risk" in filename.lower():
            return ("risk_assessment", "Documenting risks")
        elif "component" in filename.lower() or "building" in filename.lower():
            return ("components", "Defining components")
        elif "readme" in filename.lower() or "summary" in filename.lower():
            return ("documentation", "Creating documentation")
        elif ".md" in file_path:
            return ("documentation", f"Writing {filename}")
        return (current_stage, f"Creating {filename}")

    # Edit tool
    elif tool_name.lower() == "edit":
        return (current_stage, f"Updating {filename}")

    # Bash tool
    elif tool_name.lower() == "bash":
        if "mkdir" in command:
            return ("initialization", "Creating project structure")
        elif "tree" in command or "ls " in command:
            return (current_stage, "Inspecting structure")
        return (current_stage, f"Running command")

    # Research lookup tool
    elif "research" in tool_name.lower() or "lookup" in tool_name.lower():
        query_text = tool_input.get("query", "")
        if query_text:
            truncated = query_text[:50] + "..." if len(query_text) > 50 else query_text
            return ("research", f"Researching: {truncated}")
        return ("research", "Researching patterns and best practices")

    return None
```

### New `_build_project_result` Function

```python
def _build_project_result(project_dir: Path, file_info: Dict[str, Any]) -> ProjectResult:
    """
    Build a comprehensive ProjectResult from scanned files.

    Args:
        project_dir: Path to project directory
        file_info: Dictionary of file information from scan_project_directory

    Returns:
        ProjectResult object
    """
    # Extract metadata
    project_name = extract_project_name(project_dir)
    architecture_type = extract_architecture_type(file_info.get('architecture_doc'))

    metadata = ProjectMetadata(
        name=project_name,
        created_at=datetime.fromtimestamp(project_dir.stat().st_ctime).isoformat() + "Z",
        architecture_type=architecture_type,
        component_count=count_components(file_info.get('components_doc')),
        service_count=count_services(file_info.get('architecture_doc')),
        estimated_sprints=file_info.get('sprint_count', 0),
    )

    # Build files object
    files = ProjectFiles(
        architecture_doc=file_info.get('architecture_doc'),
        components_doc=file_info.get('components_doc'),
        sprint_plan=file_info.get('sprint_plan'),
        cost_analysis=file_info.get('cost_analysis'),
        risk_assessment=file_info.get('risk_assessment'),
        diagrams=file_info.get('diagrams', []),
        requirements=file_info.get('requirements'),
        progress_log=file_info.get('progress_log'),
        summary=file_info.get('summary'),
    )

    # Determine status
    status = "success"
    if not file_info.get('architecture_doc'):
        if file_info.get('requirements'):
            status = "partial"
        else:
            status = "failed"

    result = ProjectResult(
        status=status,
        project_directory=str(project_dir),
        project_name=project_dir.name,
        metadata=metadata,
        files=files,
        diagrams_count=len(file_info.get('diagrams', [])),
        services_identified=file_info.get('services', []),
        technologies_recommended=file_info.get('technologies', []),
        errors=[],
    )

    return result
```

---

## 3. models.py New Dataclasses

### Complete New models.py

```python
"""Data models for project planner API responses."""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class ProgressUpdate:
    """Progress update during project planning.

    Attributes:
        type: Always "progress" to distinguish from result messages
        timestamp: ISO 8601 timestamp of the update
        message: Human-readable progress message
        stage: Current workflow stage (initialization|requirements|research|architecture|components|cost_analysis|sprint_planning|risk_assessment|documentation|complete)
        details: Optional dictionary with additional context
    """
    type: str = "progress"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    message: str = ""
    stage: str = "initialization"
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        if result.get('details') is None:
            del result['details']
        return result


@dataclass
class TextUpdate:
    """Live text output from Project-Planner during generation.

    Streams Project-Planner's actual text responses in real-time.

    Attributes:
        type: Always "text" to distinguish from progress and result messages
        content: The text content from Project-Planner's response
    """
    type: str = "text"
    content: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ProjectMetadata:
    """Metadata about the generated project plan."""
    name: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    architecture_type: str = ""  # e.g., "microservices", "monolith", "serverless", "hybrid"
    component_count: int = 0
    service_count: int = 0
    estimated_sprints: int = 0
    estimated_duration_weeks: Optional[int] = None
    estimated_team_size: Optional[int] = None
    estimated_monthly_cost: Optional[float] = None
    technology_stack: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ProjectFiles:
    """File paths for all generated project planning artifacts."""
    # Core documents
    architecture_doc: Optional[str] = None          # Main architecture document
    components_doc: Optional[str] = None            # Building blocks documentation
    sprint_plan: Optional[str] = None               # Sprint planning document
    cost_analysis: Optional[str] = None             # Service cost analysis
    risk_assessment: Optional[str] = None           # Risk assessment document

    # Supporting files
    requirements: Optional[str] = None              # Requirements/user stories
    api_spec: Optional[str] = None                  # API specifications (OpenAPI/Swagger)
    data_model: Optional[str] = None                # Data model documentation
    infrastructure: Optional[str] = None            # Infrastructure as code references

    # Diagrams
    diagrams: List[str] = field(default_factory=list)

    # Meta files
    progress_log: Optional[str] = None
    summary: Optional[str] = None

    # Source/input files
    source_docs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ServiceCostEstimate:
    """Cost estimate for a single service/component."""
    service_name: str = ""
    provider: str = ""                    # e.g., "AWS", "GCP", "Azure", "Vercel"
    service_type: str = ""                # e.g., "compute", "database", "storage"
    monthly_cost_low: float = 0.0
    monthly_cost_mid: float = 0.0
    monthly_cost_high: float = 0.0
    scaling_notes: str = ""
    assumptions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class SprintDefinition:
    """Definition of a single sprint."""
    sprint_number: int = 0
    name: str = ""
    duration_weeks: int = 2
    goals: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    dependencies: List[int] = field(default_factory=list)  # Sprint numbers this depends on
    team_focus: List[str] = field(default_factory=list)    # e.g., ["backend", "frontend"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class RiskItem:
    """A single risk item with assessment and mitigation."""
    risk_id: str = ""
    category: str = ""              # e.g., "technical", "schedule", "resource", "external"
    description: str = ""
    likelihood: str = ""            # "low", "medium", "high"
    impact: str = ""                # "low", "medium", "high"
    risk_score: int = 0             # 1-9 (likelihood * impact)
    mitigation_strategy: str = ""
    contingency_plan: str = ""
    owner: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class BuildingBlock:
    """A building block / component in the architecture."""
    name: str = ""
    type: str = ""                  # e.g., "service", "database", "queue", "cache"
    description: str = ""
    technology: str = ""            # e.g., "Node.js", "PostgreSQL", "Redis"
    responsibilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    scaling_strategy: str = ""
    estimated_effort_days: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class TokenUsage:
    """Token usage statistics.

    Attributes:
        input_tokens: Total input tokens consumed
        output_tokens: Total output tokens consumed
        cache_creation_input_tokens: Tokens used for cache creation
        cache_read_input_tokens: Tokens read from cache
    """
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens (input + output)."""
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['total_tokens'] = self.total_tokens
        return result


@dataclass
class ProjectResult:
    """Final result containing all information about the generated project plan."""
    type: str = "result"
    status: str = "success"         # success|partial|failed
    project_directory: str = ""
    project_name: str = ""

    # Structured data
    metadata: ProjectMetadata = field(default_factory=ProjectMetadata)
    files: ProjectFiles = field(default_factory=ProjectFiles)

    # Summary data
    diagrams_count: int = 0
    services_identified: List[str] = field(default_factory=list)
    technologies_recommended: List[str] = field(default_factory=list)

    # Detailed planning data (optional, populated if available)
    building_blocks: List[BuildingBlock] = field(default_factory=list)
    sprints: List[SprintDefinition] = field(default_factory=list)
    cost_estimates: List[ServiceCostEstimate] = field(default_factory=list)
    risks: List[RiskItem] = field(default_factory=list)

    # Cost summary
    total_monthly_cost_estimate: Optional[Dict[str, float]] = None  # {"low": x, "mid": y, "high": z}

    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Token usage
    token_usage: Optional[TokenUsage] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)

        # Ensure nested objects are also dictionaries
        if isinstance(self.metadata, ProjectMetadata):
            result['metadata'] = self.metadata.to_dict()
        if isinstance(self.files, ProjectFiles):
            result['files'] = self.files.to_dict()
        if isinstance(self.token_usage, TokenUsage):
            result['token_usage'] = self.token_usage.to_dict()
        elif self.token_usage is None:
            del result['token_usage']

        # Convert lists of dataclasses
        result['building_blocks'] = [bb.to_dict() if isinstance(bb, BuildingBlock) else bb for bb in self.building_blocks]
        result['sprints'] = [s.to_dict() if isinstance(s, SprintDefinition) else s for s in self.sprints]
        result['cost_estimates'] = [c.to_dict() if isinstance(c, ServiceCostEstimate) else c for c in self.cost_estimates]
        result['risks'] = [r.to_dict() if isinstance(r, RiskItem) else r for r in self.risks]

        return result
```

---

## 4. New Skill SKILL.md Templates

### 4.1 architecture-research/SKILL.md

```markdown
---
name: architecture-research
description: "Research software architecture patterns, best practices, and technology recommendations. Search architectural decision records (ADRs), compare technology stacks, analyze scalability patterns, and gather industry benchmarks for informed technical decisions."
allowed-tools: [Read, Write, Edit, Bash]
---

# Architecture Research

## Overview

Architecture research is the systematic process of gathering, analyzing, and synthesizing information about software architecture patterns, technologies, and best practices. This skill enables informed architectural decisions by researching proven patterns, technology comparisons, scalability strategies, and industry benchmarks.

**Critical Principle: Architecture decisions should be data-driven and based on research into proven patterns, not assumptions or preferences.**

## When to Use This Skill

This skill should be used when:
- Evaluating architecture patterns (microservices vs monolith, event-driven, etc.)
- Comparing technology stacks for specific use cases
- Researching scalability and performance patterns
- Gathering industry benchmarks and case studies
- Creating Architectural Decision Records (ADRs)
- Analyzing trade-offs between different approaches
- Investigating infrastructure options (cloud providers, serverless, containers)
- Researching security patterns and compliance requirements

## Core Capabilities

### 1. Pattern Research
- Microservices architecture patterns
- Event-driven architecture
- Domain-Driven Design (DDD)
- CQRS and Event Sourcing
- API Gateway patterns
- Service mesh patterns

### 2. Technology Comparison
- Database selection (SQL vs NoSQL, specific products)
- Message queue comparison (Kafka, RabbitMQ, SQS)
- Container orchestration (Kubernetes, ECS, Docker Swarm)
- API frameworks and languages
- Frontend frameworks
- Cloud provider comparisons

### 3. Scalability Patterns
- Horizontal vs vertical scaling
- Caching strategies
- Load balancing approaches
- Database sharding
- CDN strategies
- Auto-scaling patterns

### 4. Security Research
- Authentication patterns (OAuth, JWT, SAML)
- Authorization frameworks
- API security best practices
- Data encryption approaches
- Compliance requirements (GDPR, HIPAA, SOC2)

## Research Workflow

### Phase 1: Define Research Questions
1. Identify specific architectural decisions needed
2. List key requirements and constraints
3. Define evaluation criteria
4. Prioritize research areas

### Phase 2: Gather Information
Use `research-lookup` skill:
```bash
python skills/research-lookup/scripts/research_lookup.py \
  "What are the best practices for [PATTERN] in [CONTEXT]?"
```

### Phase 3: Synthesize Findings
1. Compare options against criteria
2. Document trade-offs
3. Create recommendation matrix
4. Generate ADR (Architectural Decision Record)

### Phase 4: Document Decisions
Create ADR following template:
- Context
- Decision drivers
- Considered options
- Decision outcome
- Consequences

## Output Format

Research outputs should be structured as:

```markdown
# Architecture Research: [Topic]

## Research Question
[Clear statement of what we're researching]

## Evaluation Criteria
1. [Criterion 1]
2. [Criterion 2]
...

## Options Analyzed
### Option A: [Name]
- Pros: ...
- Cons: ...
- Best for: ...

### Option B: [Name]
- Pros: ...
- Cons: ...
- Best for: ...

## Comparison Matrix
| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| ...       | ...      | ...      | ...      |

## Recommendation
[Clear recommendation with rationale]

## Sources
- [Source 1]
- [Source 2]
```

## Integration with Other Skills

This skill works effectively with:
- **building-blocks**: Use research to inform component design
- **service-cost-analysis**: Research pricing and cost patterns
- **risk-assessment**: Identify technical risks from research
- **sprint-planning**: Inform effort estimates from research
- **scientific-schematics**: Generate architecture diagrams

## Resources

### Reference Files
- `references/architecture_patterns.md`: Common architecture patterns
- `references/technology_comparisons.md`: Technology comparison guides
- `references/adr_template.md`: ADR template

### Assets
- `assets/comparison_matrix_template.md`: Comparison matrix template
- `assets/adr_template.md`: Architectural Decision Record template
```

---

### 4.2 building-blocks/SKILL.md

```markdown
---
name: building-blocks
description: "Define and document software architecture building blocks, components, and services. Create component specifications, interface definitions, responsibility assignments, and dependency mappings for clear system decomposition."
allowed-tools: [Read, Write, Edit, Bash]
---

# Building Blocks

## Overview

Building blocks are the fundamental components, services, and modules that compose a software system. This skill helps define, document, and organize these architectural elements with clear responsibilities, interfaces, and dependencies.

**Critical Principle: Each building block should have a single, clear responsibility with well-defined interfaces and minimal coupling to other components.**

## When to Use This Skill

This skill should be used when:
- Decomposing a system into components/services
- Defining service boundaries and responsibilities
- Creating component specifications
- Documenting interfaces between components
- Mapping dependencies and data flows
- Planning component implementation order
- Creating system decomposition diagrams

## Building Block Structure

Each building block should be documented with:

### 1. Identity
- Name (clear, descriptive)
- Type (service, library, database, queue, cache, etc.)
- Owner (team or individual responsible)

### 2. Responsibilities
- Primary purpose
- Key functions/features
- What it owns (data, processes)
- What it does NOT do (explicit boundaries)

### 3. Interfaces
- API endpoints
- Event publications
- Event subscriptions
- Shared data structures

### 4. Dependencies
- Upstream dependencies (what it calls)
- Downstream dependencies (what calls it)
- External dependencies (third-party services)

### 5. Technology Stack
- Language/framework
- Database/storage
- Infrastructure requirements

### 6. Operational Characteristics
- Scalability requirements
- Availability requirements
- Performance requirements

## Output Format

```markdown
# Building Block: [Name]

## Overview
**Type**: [service | library | database | queue | cache | gateway]
**Owner**: [Team/Individual]
**Status**: [proposed | approved | implemented | deprecated]

## Description
[2-3 sentence description of the building block's purpose]

## Responsibilities
### Does:
- [Responsibility 1]
- [Responsibility 2]

### Does NOT:
- [Anti-responsibility 1]
- [Anti-responsibility 2]

## Interfaces

### REST API
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/v1/... | GET | ... |

### Events Published
| Event | Description | Payload Schema |
|-------|-------------|----------------|
| ... | ... | ... |

### Events Consumed
| Event | Source | Handler |
|-------|--------|---------|
| ... | ... | ... |

## Dependencies

### Upstream (calls these)
- [Service A] - for [purpose]
- [Database B] - for [purpose]

### Downstream (called by these)
- [Service C] - for [purpose]

### External
- [Third-party service] - for [purpose]

## Technology Stack
- **Language**: [e.g., Node.js, Python, Go]
- **Framework**: [e.g., Express, FastAPI, Gin]
- **Database**: [e.g., PostgreSQL, MongoDB]
- **Cache**: [e.g., Redis]

## Operational Requirements
- **Availability**: [e.g., 99.9%]
- **Latency**: [e.g., p99 < 100ms]
- **Throughput**: [e.g., 1000 req/s]
- **Scaling**: [horizontal | vertical | auto]

## Implementation Notes
[Any additional notes for implementers]

## Open Questions
- [ ] [Question 1]
- [ ] [Question 2]
```

## Visual Generation

Use `scientific-schematics` skill to generate:
- Component diagrams
- Dependency graphs
- Data flow diagrams
- Sequence diagrams

```bash
python skills/scientific-schematics/scripts/generate_schematic.py \
  "Component diagram showing [service name] with its dependencies and interfaces" \
  -o figures/component_[name].png
```

## Integration with Other Skills

This skill works effectively with:
- **architecture-research**: Research best practices for component design
- **service-cost-analysis**: Estimate costs per component
- **sprint-planning**: Plan implementation order
- **risk-assessment**: Identify component-level risks
- **scientific-schematics**: Generate component diagrams

## Resources

### Reference Files
- `references/component_patterns.md`: Common component patterns
- `references/interface_design.md`: Interface design best practices

### Assets
- `assets/building_block_template.md`: Building block template
- `assets/dependency_matrix_template.md`: Dependency matrix template
```

---

### 4.3 service-cost-analysis/SKILL.md

```markdown
---
name: service-cost-analysis
description: "Analyze and estimate cloud service costs for software projects. Compare pricing across AWS, GCP, Azure, and other providers. Generate detailed cost breakdowns, scaling projections, and budget recommendations with low/mid/high estimates."
allowed-tools: [Read, Write, Edit, Bash]
---

# Service Cost Analysis

## Overview

Service cost analysis provides detailed estimation of cloud infrastructure and service costs for software projects. This skill helps teams understand the financial implications of architectural decisions, compare provider options, and plan budgets with realistic projections.

**Critical Principle: Cost estimates should always include low/mid/high ranges to account for uncertainty, with clear documentation of assumptions.**

## When to Use This Skill

This skill should be used when:
- Planning infrastructure budgets for new projects
- Comparing costs between cloud providers
- Estimating scaling costs as usage grows
- Analyzing cost implications of architecture decisions
- Creating cost optimization recommendations
- Preparing budget proposals for stakeholders
- Evaluating build vs buy decisions

## Cost Analysis Framework

### 1. Service Categories

#### Compute
- Virtual machines (EC2, GCE, Azure VMs)
- Container services (ECS, GKE, AKS)
- Serverless (Lambda, Cloud Functions, Azure Functions)
- Kubernetes (EKS, GKE, AKS)

#### Database
- Relational (RDS, Cloud SQL, Azure SQL)
- NoSQL (DynamoDB, Firestore, CosmosDB)
- In-memory (ElastiCache, Memorystore)
- Data warehouses (Redshift, BigQuery, Synapse)

#### Storage
- Object storage (S3, GCS, Azure Blob)
- Block storage (EBS, Persistent Disk)
- File storage (EFS, Filestore)
- Archive storage (Glacier, Archive Storage)

#### Networking
- Load balancers
- CDN (CloudFront, Cloud CDN)
- DNS (Route53, Cloud DNS)
- VPN and Direct Connect
- Data transfer costs

#### Platform Services
- API gateways
- Message queues (SQS, Pub/Sub)
- Event streaming (Kinesis, Kafka)
- Search (Elasticsearch, Algolia)

#### Third-Party SaaS
- Auth (Auth0, Firebase Auth)
- Email (SendGrid, SES)
- Monitoring (Datadog, New Relic)
- Error tracking (Sentry)

### 2. Estimation Methodology

For each service, estimate:

1. **Low Estimate**: Minimal viable configuration
2. **Mid Estimate**: Expected typical usage (80th percentile)
3. **High Estimate**: Peak usage or growth scenario

### 3. Key Factors

- **Usage patterns**: Steady vs bursty
- **Data volumes**: Storage and transfer
- **User growth**: Scaling projections
- **Reserved vs on-demand**: Commitment discounts
- **Regional pricing**: Location-based differences

## Output Format

```markdown
# Service Cost Analysis: [Project Name]

## Executive Summary
- **Total Monthly Cost (Low)**: $X,XXX
- **Total Monthly Cost (Mid)**: $X,XXX
- **Total Monthly Cost (High)**: $X,XXX

## Assumptions
- Active users: [X - Y - Z] (low/mid/high)
- Data storage: [X - Y - Z] GB
- API requests: [X - Y - Z] per month
- Region: [primary region]

## Cost Breakdown by Category

### Compute
| Service | Provider | Low | Mid | High | Notes |
|---------|----------|-----|-----|------|-------|
| App servers | AWS EC2 | $XX | $XX | $XX | 2x t3.medium (low) to 4x c5.large (high) |
| ...     | ... | ... | ... | ... | ... |

**Subtotal**: $XX - $XX - $XX

### Database
| Service | Provider | Low | Mid | High | Notes |
|---------|----------|-----|-----|------|-------|
| PostgreSQL | AWS RDS | $XX | $XX | $XX | db.t3.medium (low) to db.r5.large (high) |
| ...     | ... | ... | ... | ... | ... |

**Subtotal**: $XX - $XX - $XX

[Continue for all categories...]

## Total Cost Summary

| Category | Low | Mid | High |
|----------|-----|-----|------|
| Compute | $XX | $XX | $XX |
| Database | $XX | $XX | $XX |
| Storage | $XX | $XX | $XX |
| Networking | $XX | $XX | $XX |
| Third-Party | $XX | $XX | $XX |
| **TOTAL** | **$XX** | **$XX** | **$XX** |

## Cost Optimization Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

## Scaling Projections

| Metric | Month 1 | Month 6 | Month 12 | Year 2 |
|--------|---------|---------|----------|--------|
| Users | XX | XX | XX | XX |
| Monthly Cost | $XX | $XX | $XX | $XX |

## Provider Comparison (if applicable)

| Service | AWS | GCP | Azure | Recommendation |
|---------|-----|-----|-------|----------------|
| Compute | $XX | $XX | $XX | [Provider] |
| Database | $XX | $XX | $XX | [Provider] |
| ... | ... | ... | ... | ... |

## Data Sources
- [Provider pricing pages with dates]
- [Calculator links]
```

## Research Integration

Use `research-lookup` to get current pricing:
```bash
python skills/research-lookup/scripts/research_lookup.py \
  "What is the current pricing for AWS [service] in [region]?"
```

## Integration with Other Skills

This skill works effectively with:
- **architecture-research**: Research cost-effective architecture patterns
- **building-blocks**: Estimate per-component costs
- **sprint-planning**: Include cost milestones
- **risk-assessment**: Identify cost-related risks

## Resources

### Reference Files
- `references/cloud_pricing_guide.md`: Cloud pricing overview
- `references/cost_optimization.md`: Cost optimization strategies

### Assets
- `assets/cost_analysis_template.md`: Cost analysis template
- `assets/provider_comparison_template.md`: Provider comparison template
```

---

### 4.4 sprint-planning/SKILL.md

```markdown
---
name: sprint-planning
description: "Create detailed sprint plans, project timelines, and implementation roadmaps. Define sprints with goals, deliverables, dependencies, and team assignments. Generate Gantt charts and milestone trackers for software project execution."
allowed-tools: [Read, Write, Edit, Bash]
---

# Sprint Planning

## Overview

Sprint planning organizes software development work into time-boxed iterations with clear goals, deliverables, and dependencies. This skill creates comprehensive sprint plans that balance ambition with achievability, ensuring teams have clear direction and stakeholders have realistic expectations.

**Critical Principle: Sprint plans should be realistic, account for dependencies, and include buffer time for unexpected challenges.**

## When to Use This Skill

This skill should be used when:
- Creating project implementation roadmaps
- Breaking down large initiatives into sprints
- Defining sprint goals and deliverables
- Identifying dependencies between work items
- Estimating effort and team capacity
- Creating timeline visualizations
- Planning releases and milestones
- Coordinating cross-team dependencies

## Sprint Planning Framework

### 1. Sprint Structure

Each sprint should define:
- **Sprint Number**: Sequential identifier
- **Name**: Descriptive theme (e.g., "Foundation Sprint", "Auth & Users")
- **Duration**: Typically 2 weeks (adjust as needed)
- **Goals**: 2-4 high-level objectives
- **Deliverables**: Specific outputs
- **Dependencies**: What must be complete before
- **Team Focus**: Which teams/skills involved
- **Definition of Done**: Completion criteria

### 2. Planning Phases

#### Phase 1: Scope Definition
- List all features/components to build
- Estimate effort for each (story points or days)
- Identify dependencies
- Prioritize by value and dependencies

#### Phase 2: Capacity Planning
- Determine team composition
- Calculate available capacity per sprint
- Account for meetings, support, PTO
- Apply velocity/buffer factors

#### Phase 3: Sprint Allocation
- Group related work items
- Respect dependencies
- Balance workload across sprints
- Include technical debt and testing

#### Phase 4: Risk Adjustment
- Add buffer sprints for unknowns
- Identify critical path
- Plan contingencies
- Set milestone checkpoints

## Output Format

```markdown
# Sprint Plan: [Project Name]

## Overview
- **Total Duration**: XX weeks (X sprints)
- **Team Size**: X developers, Y designers, Z QA
- **Sprint Duration**: 2 weeks
- **Start Date**: YYYY-MM-DD
- **Target Completion**: YYYY-MM-DD

## Sprint Summary

| Sprint | Name | Dates | Key Deliverables |
|--------|------|-------|------------------|
| 0 | Planning & Setup | MM/DD - MM/DD | Dev environment, architecture docs |
| 1 | [Name] | MM/DD - MM/DD | [Key deliverables] |
| ... | ... | ... | ... |

---

## Sprint 0: Planning & Setup

**Duration**: 1 week
**Dates**: MM/DD - MM/DD

### Goals
1. Finalize technical architecture
2. Set up development environment
3. Create project infrastructure

### Deliverables
- [ ] Architecture documentation approved
- [ ] CI/CD pipeline configured
- [ ] Development environment setup
- [ ] Initial backlog groomed

### Team Focus
- Backend: Environment setup
- Frontend: Design system setup
- DevOps: CI/CD, infrastructure

### Dependencies
- None (first sprint)

### Definition of Done
- All team members can build and run locally
- Architecture document reviewed and approved
- First sprint backlog refined

---

## Sprint 1: [Sprint Name]

**Duration**: 2 weeks
**Dates**: MM/DD - MM/DD

### Goals
1. [Goal 1]
2. [Goal 2]
3. [Goal 3]

### Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]

### User Stories / Tasks
| ID | Title | Estimate | Assignee |
|----|-------|----------|----------|
| US-001 | [Story title] | 5 pts | [Name] |
| US-002 | [Story title] | 3 pts | [Name] |
| ... | ... | ... | ... |

**Sprint Capacity**: XX points
**Planned Points**: XX points (XX% utilization)

### Team Focus
- Backend: [Focus area]
- Frontend: [Focus area]
- QA: [Focus area]

### Dependencies
- Blocked by: None
- Blocks: Sprint 2 (user authentication)

### Risks
- [Risk 1]: [Mitigation]

### Definition of Done
- All code reviewed and merged
- Unit tests passing (>80% coverage)
- Integration tests passing
- Documentation updated
- Demo ready

---

[Continue for all sprints...]

---

## Milestones

| Milestone | Date | Sprint | Criteria |
|-----------|------|--------|----------|
| MVP | MM/DD | Sprint 4 | Core features functional |
| Beta | MM/DD | Sprint 6 | All features, limited users |
| Launch | MM/DD | Sprint 8 | Production ready |

## Critical Path

```
Sprint 0 (Setup) → Sprint 1 (Auth) → Sprint 2 (Core) → Sprint 4 (MVP)
                                   ↘ Sprint 3 (UI) ↗
```

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk 1] | High | Medium | [Mitigation] |
| ... | ... | ... | ... |

## Assumptions
1. Team velocity: X points per sprint
2. No major scope changes after Sprint 2
3. Dependencies available as scheduled
```

## Visual Generation

Use `scientific-schematics` skill to generate:
- Gantt charts
- Milestone timelines
- Dependency diagrams
- Burndown projections

```bash
python skills/scientific-schematics/scripts/generate_schematic.py \
  "Gantt chart showing 8 sprints over 16 weeks with milestones at Sprint 4 (MVP), Sprint 6 (Beta), Sprint 8 (Launch)" \
  -o figures/sprint_timeline.png
```

## Integration with Other Skills

This skill works effectively with:
- **building-blocks**: Plan implementation of components
- **architecture-research**: Inform effort estimates
- **service-cost-analysis**: Align costs with timeline
- **risk-assessment**: Incorporate risks into planning
- **scientific-schematics**: Generate timeline visuals

## Resources

### Reference Files
- `references/agile_planning.md`: Agile planning best practices
- `references/estimation_techniques.md`: Estimation techniques

### Assets
- `assets/sprint_template.md`: Sprint template
- `assets/milestone_template.md`: Milestone template
```

---

### 4.5 risk-assessment/SKILL.md

```markdown
---
name: risk-assessment
description: "Identify, analyze, and plan mitigation for software project risks. Assess technical, schedule, resource, and external risks with likelihood/impact scoring. Create risk registers, mitigation strategies, and contingency plans."
allowed-tools: [Read, Write, Edit, Bash]
---

# Risk Assessment

## Overview

Risk assessment systematically identifies, analyzes, and plans responses to project risks. This skill helps teams proactively address potential problems before they impact project success, ensuring realistic planning and stakeholder awareness.

**Critical Principle: Risk assessment should be comprehensive yet prioritized - focus mitigation efforts on high-impact, high-likelihood risks first.**

## When to Use This Skill

This skill should be used when:
- Starting new software projects
- Evaluating architecture decisions
- Planning sprint milestones
- Preparing stakeholder communications
- Making build vs buy decisions
- Assessing third-party dependencies
- Planning for scale and growth
- Evaluating compliance requirements

## Risk Categories

### 1. Technical Risks
- Architecture complexity
- Technology maturity
- Integration challenges
- Performance uncertainties
- Security vulnerabilities
- Technical debt

### 2. Schedule Risks
- Unclear requirements
- Dependency delays
- Scope creep
- Resource availability
- Learning curves
- Testing bottlenecks

### 3. Resource Risks
- Team skill gaps
- Key person dependencies
- Budget constraints
- Tool/license availability
- Infrastructure limitations

### 4. External Risks
- Vendor/third-party reliability
- Regulatory changes
- Market changes
- Competitor actions
- Economic factors

### 5. Operational Risks
- Deployment complexity
- Monitoring gaps
- Incident response
- Data management
- Compliance maintenance

## Risk Assessment Framework

### Step 1: Risk Identification
- Brainstorm potential risks
- Review similar project histories
- Analyze dependencies
- Consider external factors
- Examine assumptions

### Step 2: Risk Analysis
For each risk, assess:

**Likelihood** (1-3):
- 1 = Low (unlikely, <25%)
- 2 = Medium (possible, 25-75%)
- 3 = High (likely, >75%)

**Impact** (1-3):
- 1 = Low (minor delay/cost)
- 2 = Medium (significant delay/cost)
- 3 = High (project failure/critical)

**Risk Score** = Likelihood x Impact (1-9)

### Step 3: Risk Prioritization
- Critical (7-9): Immediate action required
- Significant (4-6): Active monitoring and mitigation
- Minor (1-3): Accept or monitor

### Step 4: Response Planning
For each significant risk:
- **Mitigation**: Actions to reduce likelihood/impact
- **Contingency**: Plan if risk materializes
- **Trigger**: When to activate contingency
- **Owner**: Person responsible

## Output Format

```markdown
# Risk Assessment: [Project Name]

## Executive Summary

### Risk Profile
- **Total Risks Identified**: XX
- **Critical Risks**: X
- **Significant Risks**: X
- **Minor Risks**: X

### Top 5 Risks
1. [Risk name] - Score: X - Mitigation: [summary]
2. ...

---

## Risk Register

### Critical Risks (Score 7-9)

#### RISK-001: [Risk Name]

**Category**: [Technical | Schedule | Resource | External | Operational]

**Description**:
[Detailed description of the risk and its potential manifestation]

**Assessment**:
- Likelihood: [High/Medium/Low] (X)
- Impact: [High/Medium/Low] (X)
- Risk Score: X

**Root Causes**:
- [Cause 1]
- [Cause 2]

**Affected Areas**:
- [Area 1]
- [Area 2]

**Mitigation Strategy**:
1. [Action 1]
2. [Action 2]

**Contingency Plan**:
If this risk materializes:
1. [Response action 1]
2. [Response action 2]

**Trigger Conditions**:
- [Condition that indicates risk is materializing]

**Owner**: [Name/Role]
**Review Date**: [Date]

---

[Repeat for all critical and significant risks...]

---

## Risk Matrix

```
Impact →
    Low     Medium    High
L ┌─────────┬─────────┬─────────┐
i │ Monitor │ Monitor │ Mitigate│
k │ (1)     │ (2)     │ (3)     │
e ├─────────┼─────────┼─────────┤
l │ Monitor │ Mitigate│ Mitigate│
i │ (2)     │ (4)     │ (6)     │
h ├─────────┼─────────┼─────────┤
o │ Mitigate│ Mitigate│ Critical│
o │ (3)     │ (6)     │ (9)     │
d └─────────┴─────────┴─────────┘
  ↑
```

## Risk Summary by Category

| Category | Critical | Significant | Minor | Total |
|----------|----------|-------------|-------|-------|
| Technical | X | X | X | X |
| Schedule | X | X | X | X |
| Resource | X | X | X | X |
| External | X | X | X | X |
| Operational | X | X | X | X |
| **TOTAL** | **X** | **X** | **X** | **X** |

## Mitigation Cost Summary

| Risk ID | Mitigation Cost | Contingency Budget |
|---------|-----------------|-------------------|
| RISK-001 | $X,XXX | $X,XXX |
| RISK-002 | $X,XXX | $X,XXX |
| ... | ... | ... |
| **TOTAL** | **$X,XXX** | **$X,XXX** |

## Monitoring Plan

| Risk ID | Metric to Monitor | Threshold | Frequency |
|---------|-------------------|-----------|-----------|
| RISK-001 | [Metric] | [Value] | Weekly |
| ... | ... | ... | ... |

## Assumptions and Dependencies

### Key Assumptions
1. [Assumption 1]
2. [Assumption 2]

### Critical Dependencies
1. [Dependency 1] - Owner: [X] - Due: [Date]
2. [Dependency 2] - Owner: [X] - Due: [Date]

## Review Schedule
- Initial review: [Date]
- Ongoing reviews: [Frequency]
- Final review: [Date]
```

## Visual Generation

Use `scientific-schematics` skill to generate:
- Risk heatmaps
- Risk trend charts
- Category distribution charts

```bash
python skills/scientific-schematics/scripts/generate_schematic.py \
  "Risk heatmap matrix with X-axis Impact (Low, Medium, High) and Y-axis Likelihood (Low, Medium, High). Color gradient from green (low risk) to red (high risk). Show 10 risks plotted as labeled points" \
  -o figures/risk_heatmap.png
```

## Integration with Other Skills

This skill works effectively with:
- **architecture-research**: Identify technical risks from patterns
- **building-blocks**: Assess component-level risks
- **service-cost-analysis**: Identify cost-related risks
- **sprint-planning**: Incorporate risks into timeline
- **scientific-schematics**: Generate risk visualizations

## Resources

### Reference Files
- `references/risk_categories.md`: Risk category definitions
- `references/mitigation_patterns.md`: Common mitigation patterns

### Assets
- `assets/risk_register_template.md`: Risk register template
- `assets/risk_matrix_template.md`: Risk matrix template
```

---

## 5. marketplace.json Updates

```json
{
  "name": "claude-project-planner",
  "metadata": {
    "description": "Skills and setup for software project planning (architecture, sprints, cost analysis, risk assessment) using the project-planner toolkit.",
    "version": "1.0.0",
    "homepage": "https://github.com/flight505/claude-project-planner"
  },
  "owner": {
    "name": "flight505",
    "email": "contact@example.com"
  },
  "plugins": [
    {
      "name": "claude-project-planner",
      "description": "Collection of project planning skills",
      "source": "./",
      "strict": false,
      "skills": [
        "./skills/architecture-research",
        "./skills/building-blocks",
        "./skills/service-cost-analysis",
        "./skills/sprint-planning",
        "./skills/risk-assessment",
        "./skills/research-lookup",
        "./skills/scientific-schematics",
        "./skills/generate-image",
        "./skills/markitdown",
        "./skills/document-skills"
      ]
    }
  ]
}
```

---

## 6. Additional Files to Update

### core.py Updates

Rename functions and update paths:

```python
# OLD
def setup_claude_skills(package_dir: Path, work_dir: Path) -> None
def load_system_instructions(work_dir: Path) -> str  # Looks for WRITER.md
def ensure_output_folder(cwd: Path, custom_dir: Optional[str] = None) -> Path  # Creates writing_outputs

# NEW
def setup_claude_skills(package_dir: Path, work_dir: Path) -> None
def load_system_instructions(work_dir: Path) -> str  # Looks for PLANNER.md
def ensure_output_folder(cwd: Path, custom_dir: Optional[str] = None) -> Path  # Creates planning_outputs
```

### WRITER.md -> PLANNER.md

Create new `PLANNER.md` with project planning instructions instead of scientific writing instructions.

### utils.py Updates

```python
# Rename functions
def find_existing_papers -> find_existing_projects
def detect_paper_reference -> detect_project_reference
def scan_paper_directory -> scan_project_directory
def count_citations_in_bib -> count_components
def extract_citation_style -> extract_architecture_type
def count_words_in_tex -> count_services
def extract_title_from_tex -> extract_project_name
```

---

## Summary of Changes

| Category | Items Changed |
|----------|---------------|
| Package Rename | 6 Python files, pyproject.toml, directory name |
| Import Updates | ~20 import statement changes across files |
| API Functions | `generate_paper` -> `generate_project`, new progress stages |
| Models | 7 new dataclasses (ProjectMetadata, ProjectFiles, etc.) |
| New Skills | 5 SKILL.md files (~400 lines each) |
| Marketplace | Complete rewrite of marketplace.json |
| Supporting Files | WRITER.md -> PLANNER.md, core.py, utils.py updates |

This migration plan provides a complete roadmap for transforming the scientific-writer into a project-planner plugin while maintaining the same architectural patterns and quality standards.
