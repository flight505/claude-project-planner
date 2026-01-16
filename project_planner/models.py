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
        stage: Current workflow stage (see PROGRESS_STAGES in api.py)
        details: Optional dictionary with additional context (tool name, files created, etc.)
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
    """Live text output from Project Planner during generation.

    Streams the AI's actual text responses in real-time, allowing API consumers
    to display reasoning and explanations as they happen.

    Attributes:
        type: Always "text" to distinguish from progress and result messages
        content: The text content from the AI's response
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
    description: str = ""
    project_type: str = ""  # "saas", "mobile_app", "api", "fullstack", "cli", "library"
    architecture_type: Optional[str] = None  # "monolith", "microservices", "serverless", "hybrid"
    estimated_complexity: str = "medium"  # "small", "medium", "large", "enterprise"
    estimated_timeline: Optional[str] = None
    estimated_cost: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ProjectFiles:
    """File paths for all generated project artifacts."""
    # Specifications
    project_spec: Optional[str] = None
    technical_spec: Optional[str] = None
    api_spec: Optional[str] = None
    data_model: Optional[str] = None

    # Research outputs
    market_research: Optional[str] = None
    competitive_analysis: Optional[str] = None
    technology_research: Optional[str] = None

    # Analysis outputs
    feasibility_analysis: Optional[str] = None
    cost_analysis: Optional[str] = None
    risk_assessment: Optional[str] = None
    roi_projections: Optional[str] = None

    # Planning outputs
    sprint_plan: Optional[str] = None
    timeline: Optional[str] = None
    component_breakdown: Optional[str] = None

    # Diagrams
    diagrams: List[str] = field(default_factory=list)

    # Meta files
    progress_log: Optional[str] = None
    summary: Optional[str] = None
    plan_review: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class BuildingBlock:
    """A component specification for Claude Code to build.

    Represents a discrete, buildable unit of the project that can be
    handed off to Claude Code for implementation.
    """
    name: str = ""
    type: str = ""  # "frontend", "backend", "infrastructure", "integration", "shared"
    description: str = ""
    responsibilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    interfaces: Dict[str, Any] = field(default_factory=dict)
    complexity: str = "M"  # "S", "M", "L", "XL"
    estimated_hours: Optional[int] = None
    implementation_notes: Optional[str] = None
    test_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ServiceCostEstimate:
    """Cost estimate for a cloud service or API."""
    service_name: str = ""
    provider: str = ""  # "aws", "gcp", "azure", "vercel", "stripe", etc.
    category: str = ""  # "compute", "storage", "database", "api", "auth", etc.
    monthly_cost_low: float = 0.0
    monthly_cost_mid: float = 0.0
    monthly_cost_high: float = 0.0
    assumptions: str = ""
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class SprintDefinition:
    """Definition of a sprint in the project plan."""
    sprint_number: int = 0
    name: str = ""
    duration_weeks: int = 2
    goals: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    stories: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class RiskItem:
    """A risk item in the risk assessment."""
    id: str = ""
    category: str = ""  # "technical", "business", "resource", "external", "security"
    description: str = ""
    likelihood: str = "medium"  # "low", "medium", "high"
    impact: str = "medium"  # "low", "medium", "high"
    risk_score: int = 0  # 1-9 based on likelihood * impact
    mitigation: str = ""
    contingency: Optional[str] = None
    owner: Optional[str] = None
    status: str = "open"  # "open", "mitigating", "closed", "accepted"

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
    status: str = "success"  # success|partial|failed
    project_directory: str = ""
    project_name: str = ""
    metadata: ProjectMetadata = field(default_factory=ProjectMetadata)
    files: ProjectFiles = field(default_factory=ProjectFiles)

    # Component information
    components: List[BuildingBlock] = field(default_factory=list)
    component_count: int = 0

    # Cost information
    cost_estimates: List[ServiceCostEstimate] = field(default_factory=list)
    total_monthly_cost_estimate: Optional[str] = None

    # Sprint information
    sprints: List[SprintDefinition] = field(default_factory=list)
    sprint_count: int = 0
    total_estimated_hours: Optional[int] = None

    # Risk information
    risks: List[RiskItem] = field(default_factory=list)
    high_risks_count: int = 0

    # Research sources
    research_sources_count: int = 0

    # Diagrams
    diagrams_count: int = 0

    # Status
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
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
        result['components'] = [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.components]
        result['cost_estimates'] = [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.cost_estimates]
        result['sprints'] = [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.sprints]
        result['risks'] = [r.to_dict() if hasattr(r, 'to_dict') else r for r in self.risks]

        return result

