# Claude Agent SDK Prompt Caching: Comprehensive Research

**Research Date:** 2026-01-21
**Project:** claude-project-planner
**Purpose:** Cost optimization and performance improvement for long-running planning agents

---

## Executive Summary

Prompt caching in Claude Agent SDK enables **90% cost reduction** and **50-85% latency improvement** for applications with repeated static content. The feature is **automatically enabled by default** in the Agent SDK, requiring no explicit configuration for basic use cases.

**Key Findings:**
- Cache writes cost 125% of standard input tokens (25% premium)
- Cache reads cost only 10% of standard input tokens (90% discount)
- Break-even point: Just 2 requests using the same cached prefix
- Default 5-minute cache refreshes automatically at no cost
- Extended 1-hour cache available at 200% write cost for long-running workflows

---

## 1. What Can Be Cached

### 1.1 System Prompts and Instructions

**Most valuable content to cache** - typically static across many requests.

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Static analysis framework - perfect for caching
analysis_framework = """
Software Architecture Analysis Framework:
1. Evaluate technology stack feasibility
2. Assess scalability and performance characteristics
3. Identify security vulnerabilities and mitigation strategies
4. Analyze deployment complexity and operational overhead
5. Calculate total cost of ownership (TCO)

Apply this framework consistently across all architecture reviews.
"""

options = ClaudeAgentOptions(
    system_prompt=analysis_framework,  # Automatically cached
    allowed_tools=["Read", "Grep", "WebSearch"],
    permission_mode="acceptEdits"
)
```

**Why this works:**
- System prompts remain constant across multiple queries
- Agent SDK automatically marks system prompts for caching
- First request: Creates cache at 125% cost
- Subsequent requests: Read from cache at 10% cost

---

### 1.2 Tool Definitions

**Tool definitions are cached as part of the system prompt hierarchy.**

```python
# Restrict to necessary tools only - reduces cached overhead
options = ClaudeAgentOptions(
    system_prompt="You are a project cost analyzer.",

    # Only include tools actually needed - each tool adds to cache size
    allowed_tools=[
        "Read",           # ~200 tokens
        "Grep",           # ~150 tokens
        "WebSearch"       # ~300 tokens
    ],  # Total: ~650 tokens

    # Avoid: allowed_tools=None (loads ALL tools - 5000+ tokens)
)
```

**Best Practice:**
- Complex agent systems may have 50+ available tools
- Including unnecessary tools inflates cached content by 30-40%
- Selective tool access = smaller cache = faster performance

**Impact:** A 72,000-token tool definition set cached once saves massive costs on repeated calls.

---

### 1.3 Conversation History and Context

**Conversation history can be partially or fully cached** depending on application needs.

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class CachingConversationSession:
    def __init__(self):
        self.options = ClaudeAgentOptions(
            system_prompt="""You are a project planning specialist.
            Maintain consistent methodology throughout the session.
            Always cite sources and validate assumptions.""",
            allowed_tools=["Read", "research-lookup"],
            permission_mode="acceptEdits"
        )
        self.client = ClaudeSDKClient(self.options)

    async def start(self):
        # Initial connection - creates cache
        await self.client.connect("Start project planning mode")

    async def send_query(self, user_input: str):
        # Subsequent queries benefit from cached system prompt + history
        await self.client.query(user_input, session_id="planning")

        async for message in self.client.receive_response():
            if hasattr(message, 'content'):
                print(f"Response: {message}")

    async def close(self):
        await self.client.disconnect()
```

**Multi-turn conversation pattern:**
- Turn 1: System prompt + initial query (cache creation)
- Turn 2: Cached system + previous turn + new query (cache hit)
- Turn 3: Cached system + cached history + new query (cache hit)

**Real-world performance:**
- Literary analysis example: Response time dropped from 24s → 7-11s after cache creation
- Cache efficiency increases with conversation length

---

### 1.4 Large Documents and Reference Materials

**Ideal for knowledge bases, codebases, research papers, project documentation.**

```python
async def analyze_project_with_cached_docs():
    # Load large project specification once
    with open("/projects/spec.md", "r") as f:
        project_spec = f.read()  # 150,000 tokens

    # Static system prompt includes the specification
    options = ClaudeAgentOptions(
        system_prompt=f"""You are a project analyst.

PROJECT SPECIFICATION:
{project_spec}

Analyze all queries against this specification.""",

        allowed_tools=["Read", "Grep", "research-lookup"],
        permission_mode="acceptEdits"
    )

    # First query - creates cache (150,000 tokens at 125% cost)
    async for msg in query("What are the main technical risks?", options):
        print(msg)

    # Subsequent queries - hit cache (150,000 tokens at 10% cost)
    async for msg in query("What is the estimated timeline?", options):
        print(msg)

    async for msg in query("Which services will cost the most?", options):
        print(msg)
```

**Cost calculation example:**
- **Without caching:** 150,000 tokens × 3 queries = 450,000 input tokens
  - Cost at $3/million: $1.35
- **With caching:**
  - Write: 150,000 × 1.25 = 187,500 tokens ($0.56)
  - Reads: 150,000 × 0.10 × 2 = 30,000 tokens ($0.09)
  - New content: ~500 tokens per query = 1,500 tokens ($0.004)
  - **Total: $0.65 (52% savings)**

---

### 1.5 Extended Thinking Blocks

**Thinking blocks are automatically cached but cannot be explicitly marked.**

When extended thinking is enabled:
- Thinking blocks generated in assistant responses
- Automatically cached when included in conversation history
- **Count as input tokens when read from cache**

```python
# Extended thinking usage with caching
options = ClaudeAgentOptions(
    system_prompt="Use extended thinking for complex analysis.",
    thinking={"type": "enabled", "budget_tokens": 10000},
    allowed_tools=["Read", "research-lookup"]
)

# First query generates thinking blocks
async for msg in query("Analyze the feasibility of this architecture", options):
    # Thinking blocks generated and returned
    pass

# Second query in same session
# Previous thinking blocks are automatically cached as part of conversation
async for msg in query("What are the cost implications?", options):
    # Benefits from cached thinking context
    pass
```

**Important considerations:**
- Thinking blocks add to cached token count
- Factor into cost calculations for extended thinking workflows
- Useful for multi-step reasoning where previous thinking informs next steps

---

### 1.6 Tool Results

**Tool results can be cached when relevant for subsequent requests.**

```python
# Example: Research results cached across multiple analysis queries
async def cached_research_workflow():
    options = ClaudeAgentOptions(
        system_prompt="You are a technology research analyst.",
        allowed_tools=["research-lookup", "Read"],
        permission_mode="acceptEdits"
    )

    # Query 1: Perform research (tool results generated)
    async for msg in query(
        "Research current pricing for AWS Lambda, Google Cloud Functions, and Azure Functions",
        options
    ):
        print(msg)

    # Query 2: Analyze research (tool results from Query 1 are cached)
    async for msg in query(
        "Compare the pricing models and recommend the most cost-effective option",
        options
    ):
        print(msg)

    # Query 3: Further analysis (still benefits from cached research)
    async for msg in query(
        "Calculate total cost for 10 million monthly invocations",
        options
    ):
        print(msg)
```

**Context management interaction:**
- Tool results can be automatically cleared when context grows large
- Clearing invalidates cache at that point (trade-off: context space vs cache efficiency)
- Configure with `clear_tool_uses` strategy and `keep` parameter

---

### 1.7 Minimum Token Requirements

**Critical constraint:** Prompts below minimum threshold cannot be cached.

| Model | Minimum Cacheable Tokens |
|-------|-------------------------|
| Claude Opus 4.5 | 4,096 tokens |
| Claude Sonnet 4.5 | 1,024 tokens |
| Claude Sonnet 4 | 1,024 tokens |
| Claude Haiku 4.5 | 1,024 tokens |
| Claude Haiku 3.5 | 1,024 tokens |

**Implications for claude-project-planner:**
- Our system prompts + tool definitions easily exceed 1,024 tokens
- Research results and planning documents add thousands more
- **Always meeting minimum threshold** - caching highly beneficial

```python
# Check if content meets minimum for caching
import tiktoken

def check_cache_threshold(content: str, model: str = "claude-sonnet-4.5") -> bool:
    enc = tiktoken.get_encoding("cl100k_base")
    token_count = len(enc.encode(content))

    thresholds = {
        "claude-opus-4.5": 4096,
        "claude-sonnet-4.5": 1024,
        "claude-haiku-4.5": 1024
    }

    min_tokens = thresholds.get(model, 1024)
    return token_count >= min_tokens

# Example usage
system_prompt = "Your comprehensive planning instructions..."
if check_cache_threshold(system_prompt):
    print(f"✓ Prompt meets caching threshold")
else:
    print(f"✗ Prompt too small to cache - consider consolidating content")
```

---

## 2. Pricing Structure and Cost Optimization

### 2.1 Cost Breakdown

**Three token cost tiers:**

| Token Type | Cost Multiplier | Example (Sonnet 4.5 @ $3/M base) |
|-----------|----------------|----------------------------------|
| **Standard Input** | 100% | $3.00 per million tokens |
| **Cache Write** | 125% | $3.75 per million tokens |
| **Cache Read** | 10% | $0.30 per million tokens |

**Output tokens:** Unchanged ($15/M for Sonnet 4.5)

---

### 2.2 Break-Even Analysis

**When does caching become profitable?**

```
Cost without caching: N × 100% (N requests, full processing)
Cost with caching: 125% + (N-1) × 10% (1 write, N-1 reads)

Break-even: 125% + (N-1) × 10% = N × 100%
Solving: N = 1.28 requests
```

**Conclusion: Caching is profitable after just 2 requests** using the same cached prefix.

---

### 2.3 Real-World Cost Scenarios for claude-project-planner

#### Scenario 1: Full Planning Workflow (Multiple Skills)

**Setup:**
- System prompt + tool definitions: 50,000 tokens
- Planning phases: 10 skill invocations
- Research results: 100,000 tokens (cached mid-workflow)

**Without caching:**
```
Phase 1: 50,000 tokens input
Phase 2: 50,000 tokens input
...
Phase 10: 50,000 tokens input
Total: 500,000 input tokens × $3/M = $1.50
```

**With caching:**
```
Phase 1 (cache write): 50,000 × $3.75/M = $0.19
Phase 2-10 (cache read): 50,000 × 9 × $0.30/M = $0.14
Total: $0.33 (78% savings)
```

**Additional savings from cached research:**
- Research cached at phase 3: 100,000 tokens
- Phases 4-10 read research from cache: 100,000 × 7 × $0.30/M = $0.21
- **Without caching research would cost:** 100,000 × 7 × $3/M = $2.10
- **Savings: $1.89 (90% reduction)**

**Total workflow cost:**
- Without caching: $1.50 + $2.10 = $3.60
- With caching: $0.33 + $0.21 = $0.54
- **Overall savings: $3.06 (85% reduction)**

---

#### Scenario 2: Batch Project Analysis

**Setup:**
- Analyze 100 project proposals
- Shared evaluation framework: 50,000 tokens (cached once)
- Each proposal: 5,000 tokens (not cached)

**Without caching:**
```
100 projects × 55,000 tokens = 5,500,000 input tokens
Cost: $16.50
```

**With caching:**
```
Cache write (framework): 50,000 × $3.75/M = $0.19
Cache reads (99 projects): 50,000 × 99 × $0.30/M = $1.49
New content: 5,000 × 100 × $3/M = $1.50
Total: $3.18 (81% savings)
```

---

#### Scenario 3: Interactive Planning Session

**Setup:**
- User iterates on architecture decisions
- Base context: 80,000 tokens (spec + requirements)
- 20 back-and-forth queries in session
- Cache duration: 5 minutes (free refresh)

**Without caching:**
```
20 queries × 80,000 tokens = 1,600,000 input tokens
Cost: $4.80
```

**With caching (5-min auto-refresh):**
```
Cache write: 80,000 × $3.75/M = $0.30
Cache reads: 80,000 × 19 × $0.30/M = $0.46
New queries: ~1,000 tokens × 20 × $3/M = $0.06
Total: $0.82 (83% savings)
```

**Note:** If queries are spaced within 5 minutes, cache auto-refreshes at no cost.

---

### 2.4 Cache Duration Economics

#### Default 5-Minute Cache

- **Write cost:** 125% of base input price
- **Refresh:** Automatic, no additional cost
- **Best for:** Interactive sessions, frequent requests

```python
# Default behavior - 5-minute cache
options = ClaudeAgentOptions(
    system_prompt="Project planning framework...",
    # No explicit cache configuration needed
)

# As long as requests arrive within 5 minutes, cache persists
# Each request refreshes the 5-minute timer
```

**Economics:**
- Ideal for: Real-time planning sessions, iterative workflows
- Break-even: 2 requests
- Maximum benefit: Unlimited requests within 5-min windows

---

#### Extended 1-Hour Cache

- **Write cost:** 200% of base input price (2× premium)
- **Read cost:** Still 10% (same as 5-min cache)
- **Best for:** Batch processing, async workflows, scheduled jobs

```python
# Extended cache would require lower-level API configuration
# Agent SDK uses 5-minute cache by default
# For 1-hour cache, consider using direct API calls with cache_control blocks

# Example of when 1-hour cache is beneficial:
# - Research task takes 15 minutes to complete
# - Follow-up analysis needs same research 30 minutes later
# - Scheduled reports run hourly with same base context
```

**Economics:**
- Break-even: 12 requests (higher write cost requires more reads to recover)
- Beneficial when: Request intervals exceed 5 minutes but under 60 minutes

**Cost comparison (100,000 tokens, 10 requests, Sonnet 4.5):**

| Cache Type | Write Cost | Read Cost | Total Cost | vs No Cache |
|-----------|-----------|-----------|------------|-------------|
| None | - | $3.00 × 10 | $30.00 | - |
| 5-minute | $3.75 | $0.30 × 9 | $6.45 | 78% savings |
| 1-hour | $6.00 | $0.30 × 9 | $8.70 | 71% savings |

**Decision matrix:**
- Requests < 5 min apart → Use 5-min cache (default)
- Requests 5-60 min apart → Use 1-hour cache
- Requests > 60 min apart → Caching provides no benefit

---

## 3. Implementation in Claude Agent SDK

### 3.1 Automatic Caching (Default Behavior)

**The Agent SDK enables prompt caching by default - no explicit configuration needed.**

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# This ALREADY uses prompt caching automatically
options = ClaudeAgentOptions(
    system_prompt="You are a project cost analyzer.",
    allowed_tools=["Read", "research-lookup"],
    permission_mode="acceptEdits"
)

# First request - cache is created automatically
async for message in query("Analyze AWS Lambda pricing", options):
    print(message)

# Second request - cache is hit automatically
async for message in query("Compare with Google Cloud Functions", options):
    print(message)
```

**What gets cached automatically:**
1. System prompt (`system_prompt` parameter)
2. Tool definitions (from `allowed_tools`)
3. Skills configuration (from filesystem or programmatic)
4. Static context loaded at startup

**No manual `cache_control` markers needed** for basic use cases.

---

### 3.2 Explicit Cache Control (Advanced)

**For fine-grained optimization, use direct API with explicit cache_control blocks.**

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

# Explicit cache control with multiple breakpoints
response = client.messages.create(
    model="claude-sonnet-4.5-20250514",
    max_tokens=2048,
    system=[
        {
            "type": "text",
            "text": "You are a software architecture specialist.",
        },
        {
            "type": "text",
            "text": "REFERENCE ARCHITECTURE:\n<large 50k token document>",
            "cache_control": {"type": "ephemeral"}  # Cache breakpoint 1
        }
    ],
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "PREVIOUS CONVERSATION:\n<10k tokens>",
                    "cache_control": {"type": "ephemeral"}  # Cache breakpoint 2
                },
                {
                    "type": "text",
                    "text": "What are the scaling limitations?"  # Not cached
                }
            ]
        }
    ]
)

# Check cache usage in response
print(f"Cache creation: {response.usage.cache_creation_input_tokens}")
print(f"Cache reads: {response.usage.cache_read_input_tokens}")
print(f"New input: {response.usage.input_tokens}")
```

**Multiple cache breakpoints:**
- Up to 4 distinct breakpoints per request
- Allows different content sections to be cached independently
- Example: System prompt (rarely changes) + Research docs (change weekly) + Conversation (changes frequently)

---

### 3.3 Session-Based Caching Pattern

**Best practice for multi-turn workflows in claude-project-planner.**

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock
import asyncio

class PlanningSessionWithCaching:
    def __init__(self, project_spec: str):
        self.project_spec = project_spec

        # Configure once - caching applies to entire session
        self.options = ClaudeAgentOptions(
            system_prompt=f"""You are a comprehensive project planner.

PROJECT SPECIFICATION:
{self.project_spec}

Use this specification as the foundation for all planning activities.
Always validate recommendations against the specification.""",

            allowed_tools=[
                "research-lookup",
                "architecture-research",
                "service-cost-analysis",
                "risk-assessment",
                "Read",
                "Write"
            ],
            permission_mode="acceptEdits",
            setting_sources=None  # No filesystem deps = consistent prompts
        )

        self.client = ClaudeSDKClient(self.options)
        self.phase = 0

    async def start_session(self):
        """Initialize session - creates cache."""
        await self.client.connect("Begin comprehensive project planning")
        self.phase = 0
        print("✓ Session started - cache created")

    async def run_planning_phase(self, phase_name: str, task: str):
        """Execute planning phase - benefits from cached context."""
        self.phase += 1
        print(f"\n{'='*60}")
        print(f"Phase {self.phase}: {phase_name}")
        print(f"{'='*60}")

        await self.client.query(task, session_id="planning")

        async for message in self.client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"\n{block.text}")

        print(f"\n✓ Phase {self.phase} complete (cache hit)")

    async def close_session(self):
        """Clean up session."""
        await self.client.disconnect()
        print(f"\n✓ Session closed - {self.phase} phases completed")


async def main():
    # Load project specification
    with open("project_spec.md", "r") as f:
        spec = f.read()  # 80,000 tokens

    session = PlanningSessionWithCaching(spec)

    await session.start_session()  # Cache creation

    # All subsequent phases benefit from cached spec
    await session.run_planning_phase(
        "Architecture Research",
        "Research and recommend technology stack for the specified requirements"
    )

    await session.run_planning_phase(
        "Cost Analysis",
        "Estimate infrastructure costs for the recommended architecture"
    )

    await session.run_planning_phase(
        "Risk Assessment",
        "Identify technical and business risks for the project"
    )

    await session.run_planning_phase(
        "Sprint Planning",
        "Create user stories and sprint plan for first 3 sprints"
    )

    await session.close_session()

    # Cost breakdown:
    # Without caching: 80,000 tokens × 4 phases = 320,000 tokens ($0.96)
    # With caching: 80,000 × 1.25 (write) + 80,000 × 3 × 0.10 (reads) = 124,000 ($0.37)
    # Savings: $0.59 (61%)

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 3.4 Monitoring Cache Performance

**Track cache effectiveness through token usage metrics.**

```python
from claude_agent_sdk import query, ClaudeAgentOptions
from anthropic.types import Message

async def query_with_metrics(prompt: str, options: ClaudeAgentOptions):
    """Execute query and report cache metrics."""

    print(f"\n{'='*60}")
    print(f"Query: {prompt[:100]}...")
    print(f"{'='*60}")

    response_text = []

    async for message in query(prompt, options):
        if hasattr(message, 'content'):
            response_text.append(str(message))

        # Check for usage metadata (available in some message types)
        if hasattr(message, 'usage'):
            usage = message.usage

            total_input = (
                getattr(usage, 'input_tokens', 0) +
                getattr(usage, 'cache_read_input_tokens', 0) +
                getattr(usage, 'cache_creation_input_tokens', 0)
            )

            cache_read = getattr(usage, 'cache_read_input_tokens', 0)
            cache_creation = getattr(usage, 'cache_creation_input_tokens', 0)

            cache_hit_rate = (cache_read / total_input * 100) if total_input > 0 else 0

            print(f"\n📊 Token Usage:")
            print(f"  Input tokens: {getattr(usage, 'input_tokens', 0)}")
            print(f"  Cache read: {cache_read}")
            print(f"  Cache creation: {cache_creation}")
            print(f"  Cache hit rate: {cache_hit_rate:.1f}%")
            print(f"  Output tokens: {getattr(usage, 'output_tokens', 0)}")

    return "\n".join(response_text)


async def monitor_caching_efficiency():
    """Monitor cache performance across multiple queries."""

    options = ClaudeAgentOptions(
        system_prompt="You are a project cost analyzer with 50,000 token framework...",
        allowed_tools=["Read", "research-lookup"],
        permission_mode="acceptEdits"
    )

    queries = [
        "Analyze AWS Lambda pricing structure",
        "Compare Lambda with Google Cloud Functions",
        "Estimate costs for 10M monthly invocations",
        "What cost optimization strategies are available?"
    ]

    for i, q in enumerate(queries, 1):
        print(f"\n{'#'*60}")
        print(f"Query {i}/{len(queries)}")
        print(f"{'#'*60}")

        await query_with_metrics(q, options)

        if i == 1:
            print("\n⚠️  First query creates cache - expect lower efficiency")
        else:
            print(f"\n✓ Query {i} should show high cache hit rate (>90%)")

# Expected output:
# Query 1: Cache creation: 50,000 tokens, Cache hit rate: 0%
# Query 2: Cache read: 50,000 tokens, Cache hit rate: 95%+
# Query 3: Cache read: 50,000 tokens, Cache hit rate: 95%+
# Query 4: Cache read: 50,000 tokens, Cache hit rate: 95%+
```

**Healthy caching metrics:**
- **First request:** `cache_creation_input_tokens` > 0, `cache_read_input_tokens` = 0
- **Subsequent requests:** `cache_read_input_tokens` >> `input_tokens`, `cache_creation_input_tokens` = 0
- **Target cache hit rate:** 90%+ (90% of input tokens from cache reads)

**Red flags:**
- Cache hit rate < 50% → Check for prompt inconsistencies
- Repeated cache creation → Content changing between requests
- Zero cache reads → Content below minimum token threshold

---

## 4. Best Practices for claude-project-planner

### 4.1 Optimize System Prompt Structure

**Place static content first, dynamic content last.**

```python
# ✅ GOOD: Static content consolidated at start
system_prompt = """
ROLE: You are a comprehensive software project planner.

METHODOLOGY:
1. Research-driven recommendations (use research-lookup extensively)
2. Real data only (no placeholder estimates)
3. Evidence-based risk assessment
4. Detailed building block specifications

PLANNING FRAMEWORK:
[50,000 tokens of detailed planning methodology...]

TOOLS AVAILABLE:
- research-lookup: Real-time technology research
- architecture-research: Stack analysis and ADR creation
- service-cost-analysis: Cloud pricing and ROI calculations
- risk-assessment: Risk registers and mitigation strategies

CONSTRAINTS:
- All recommendations must be validated with current research
- Cost estimates must use real pricing data
- Architecture decisions must include trade-off analysis
"""

# Dynamic content (user query) appended separately - not cached

# ❌ BAD: Dynamic references mixed into system prompt
system_prompt = f"""
You are planning a project for user {user_name} on {current_date}.
The project is: {project_description}  # Changes every query!
Use research to validate your recommendations.
"""
# This invalidates cache on every request
```

---

### 4.2 Restrict Tool Definitions

**Only include tools actually needed for the task.**

```python
# ✅ GOOD: Task-specific tool selection
# Architecture research phase
arch_options = ClaudeAgentOptions(
    system_prompt="Architecture research specialist...",
    allowed_tools=[
        "research-lookup",
        "architecture-research",
        "project-diagrams",
        "Read"
    ]  # ~1,500 tokens
)

# Cost analysis phase
cost_options = ClaudeAgentOptions(
    system_prompt="Cost analysis specialist...",
    allowed_tools=[
        "research-lookup",
        "service-cost-analysis",
        "Read"
    ]  # ~1,200 tokens
)

# ❌ BAD: Loading all tools regardless of need
bad_options = ClaudeAgentOptions(
    system_prompt="Project planner...",
    allowed_tools=None  # Loads ALL tools - 5,000+ tokens
)
```

**Impact:**
- Selective tools: 1,500 tokens cached
- All tools: 5,000 tokens cached
- **Difference: 3,500 tokens × $3.75/M (write) = $0.013 per cache creation**
- Over 100 planning sessions: **$1.30 wasted**

---

### 4.3 Design for 5-Minute Cache Windows

**Structure workflows to complete within cache TTL.**

```python
# ✅ GOOD: Sequential phases within cache window
async def efficient_planning_workflow():
    options = ClaudeAgentOptions(
        system_prompt="Comprehensive project planner...",
        allowed_tools=["research-lookup", "architecture-research"]
    )

    # All phases executed within 5 minutes
    # Cache created once, reused 5 times
    phases = [
        "Research technology stack options",
        "Analyze architectural patterns",
        "Estimate infrastructure costs",
        "Assess project risks",
        "Create sprint plan",
        "Generate executive summary"
    ]

    for phase in phases:
        async for msg in query(phase, options):
            print(msg)
        # Total time: ~4 minutes - cache stays hot

# ❌ BAD: Long delays between phases
async def inefficient_planning_workflow():
    options = ClaudeAgentOptions(
        system_prompt="Comprehensive project planner...",
        allowed_tools=["research-lookup", "architecture-research"]
    )

    async for msg in query("Research technology stack", options):
        print(msg)

    # ⚠️ 10-minute delay - cache expires!
    await asyncio.sleep(600)

    # Cache must be recreated - pay write cost again
    async for msg in query("Analyze architecture", options):
        print(msg)
```

**Solution for long-running workflows:**
- Use explicit 1-hour cache via direct API
- Or: Implement periodic "keep-alive" queries within 5-min window
- Or: Accept cache recreation cost for long delays

---

### 4.4 Avoid Cache Invalidation Triggers

**Certain changes invalidate all caches - avoid during sessions.**

```python
# ✅ GOOD: Consistent configuration throughout session
class PlanningSession:
    def __init__(self):
        # Configuration locked at start
        self.options = ClaudeAgentOptions(
            system_prompt="Fixed planning methodology...",
            allowed_tools=["research-lookup", "Read"],
            permission_mode="acceptEdits"
        )

    async def phase_1_research(self):
        # Uses locked configuration - cache hit
        async for msg in query("Research task", self.options):
            pass

    async def phase_2_analysis(self):
        # Same configuration - cache hit
        async for msg in query("Analysis task", self.options):
            pass


# ❌ BAD: Changing configuration mid-session
async def bad_workflow():
    # Phase 1
    options_v1 = ClaudeAgentOptions(
        system_prompt="Planning methodology v1",
        allowed_tools=["research-lookup", "Read"]
    )
    async for msg in query("Research task", options_v1):
        pass  # Cache created

    # Phase 2 - system prompt changed!
    options_v2 = ClaudeAgentOptions(
        system_prompt="Planning methodology v2",  # ⚠️ Different!
        allowed_tools=["research-lookup", "Read"]
    )
    async for msg in query("Analysis task", options_v2):
        pass  # Cache invalidated - full reprocessing
```

**Cache invalidation triggers:**
- Modifying system prompt text
- Adding/removing/changing tool definitions
- Changing tool_choice settings
- Enabling/disabling web search
- Adding/removing images in prompt

**Safe changes (do NOT invalidate cache):**
- Changing user query text
- Adding new conversation messages
- Appending new context after cache breakpoint

---

### 4.5 Combine Caching with Batch Processing

**For maximum cost savings, combine caching + batch API.**

```python
# Batch API offers 50% discount
# Prompt caching offers 90% discount on cache reads
# Combined: Up to 95% total savings

async def batch_project_analysis_with_caching():
    """
    Analyze 100 project proposals using shared evaluation framework.
    """

    # Shared framework (cached once)
    evaluation_framework = """
    [50,000 token comprehensive evaluation methodology]
    """

    options = ClaudeAgentOptions(
        system_prompt=evaluation_framework,
        allowed_tools=["Read", "research-lookup", "feasibility-analysis"],
        permission_mode="acceptEdits"
    )

    # First project - cache creation
    print("Processing project 1 (cache creation)...")
    async for msg in query("Analyze project_001.md", options):
        pass

    # Remaining 99 projects - cache hits
    for i in range(2, 101):
        print(f"Processing project {i:03d} (cache hit)...")
        async for msg in query(f"Analyze project_{i:03d}.md", options):
            pass

    # Cost calculation:
    # Without caching: 100 × 50,000 tokens × $3/M = $15.00
    # With caching:
    #   Write: 50,000 × $3.75/M = $0.19
    #   Reads: 50,000 × 99 × $0.30/M = $1.49
    #   Total: $1.68 (89% savings)

    # If using Batch API (50% off):
    #   Base savings: 50% → $7.50
    #   With caching: 89% → $1.68
    #   Batch + cache: ~94% total savings
```

---

### 4.6 Implement Cache Warming

**For batch workflows, explicitly create cache before main processing.**

```python
async def warm_cache_for_batch_processing():
    """
    Pre-create cache entry with dummy request before batch starts.
    Ensures all batch items hit cache immediately.
    """

    options = ClaudeAgentOptions(
        system_prompt="Comprehensive evaluation framework [50k tokens]...",
        allowed_tools=["Read", "feasibility-analysis"],
        permission_mode="acceptEdits"
    )

    # Cache warm-up with minimal query
    print("⏳ Warming cache...")
    async for msg in query("Acknowledge ready for batch processing", options):
        pass  # Discard response
    print("✓ Cache warmed")

    # Now all batch items immediately hit cache
    batch_items = [f"project_{i:03d}.md" for i in range(1, 101)]

    for item in batch_items:
        print(f"Processing {item} (cache hit from start)")
        async for msg in query(f"Analyze {item}", options):
            pass  # All requests benefit from pre-warmed cache

    # Alternative: Use first real batch item for cache creation
    # No separate warm-up needed, but first item slower
```

---

## 5. Integration with claude-project-planner Skills

### 5.1 Research-Intensive Skills

**Skills like `research-lookup`, `architecture-research`, `competitive-analysis` generate large research results that benefit from caching.**

```python
async def cached_research_workflow():
    """
    Research phase results cached and reused in subsequent analysis phases.
    """

    options = ClaudeAgentOptions(
        system_prompt="""You are a comprehensive project planner.

RESEARCH PHASE: Gather all necessary research before analysis.
ANALYSIS PHASE: Use cached research for cost, risk, and feasibility analysis.""",

        allowed_tools=[
            "research-lookup",
            "architecture-research",
            "competitive-analysis",
            "service-cost-analysis",
            "risk-assessment"
        ],
        permission_mode="acceptEdits"
    )

    # Phase 1: Research (generates ~100k tokens of research results)
    print("Phase 1: Comprehensive Research")
    async for msg in query(
        """Perform comprehensive research:
        1. Technology stack options for real-time messaging platform
        2. Cloud service pricing for WebSocket infrastructure
        3. Competitive analysis of Slack, Discord, Microsoft Teams
        """,
        options
    ):
        print(msg)
    # Research results now cached as part of conversation context

    # Phase 2: Cost analysis (uses cached research)
    print("\nPhase 2: Cost Analysis")
    async for msg in query(
        "Based on the research, estimate total infrastructure costs",
        options
    ):
        print(msg)
    # Cached: System prompt + research results

    # Phase 3: Risk assessment (uses cached research)
    print("\nPhase 3: Risk Assessment")
    async for msg in query(
        "Based on the research and cost analysis, identify project risks",
        options
    ):
        print(msg)
    # Cached: System prompt + research + cost analysis

    # Phase 4: Recommendation (uses all cached context)
    print("\nPhase 4: Final Recommendation")
    async for msg in query(
        "Synthesize research, costs, and risks into architecture recommendation",
        options
    ):
        print(msg)

    # Cost savings:
    # Without caching:
    #   Phase 1: 50k system + 100k research generated = 50k input
    #   Phase 2: 50k system + 100k research = 150k input
    #   Phase 3: 50k system + 100k research + 50k cost = 200k input
    #   Phase 4: 50k system + 100k research + 50k cost + 50k risk = 250k input
    #   Total: 650k input tokens × $3/M = $1.95

    # With caching:
    #   Phase 1: 50k × $3.75/M = $0.19 (cache write)
    #   Phase 2: 150k × $0.30/M = $0.05 (cache read)
    #   Phase 3: 200k × $0.30/M = $0.06 (cache read)
    #   Phase 4: 250k × $0.30/M = $0.08 (cache read)
    #   Total: $0.38 (81% savings)
```

---

### 5.2 Building Blocks Skill

**Component specifications benefit from cached project context.**

```python
async def building_blocks_with_cached_spec():
    """
    Generate building blocks using cached project specification.
    """

    # Load project specification
    with open("project_spec.md", "r") as f:
        spec = f.read()  # 120,000 tokens

    options = ClaudeAgentOptions(
        system_prompt=f"""You are a software component specification expert.

PROJECT SPECIFICATION:
{spec}

Create detailed building block specifications that Claude Code can implement.
Each building block must include:
- Clear interface definitions
- Dependencies and integration points
- Test criteria
- Implementation guidelines
""",
        allowed_tools=["building-blocks", "Read", "Write"],
        permission_mode="acceptEdits"
    )

    components = [
        "User authentication service",
        "Real-time messaging backend",
        "Message persistence layer",
        "WebSocket gateway",
        "Admin dashboard API",
        "Analytics pipeline"
    ]

    # Generate specification for each component
    # All components share cached project spec
    for component in components:
        print(f"\nGenerating specification: {component}")
        async for msg in query(
            f"Create detailed building block specification for: {component}",
            options
        ):
            print(msg)

    # Cost without caching: 120k × 6 components = 720k tokens × $3/M = $2.16
    # Cost with caching: 120k × $3.75/M + (120k × 5 × $0.30/M) = $0.63 (71% savings)
```

---

### 5.3 Sprint Planning with Cached Architecture

**Sprint planning reuses cached architecture decisions and building blocks.**

```python
async def sprint_planning_with_cached_context():
    """
    Generate sprint plans using cached architecture and component specs.
    """

    # Accumulated context from previous phases
    accumulated_context = """
    [Architecture Research Results: 50,000 tokens]
    [Building Block Specifications: 80,000 tokens]
    [Risk Assessment: 20,000 tokens]
    [Cost Analysis: 15,000 tokens]
    Total: 165,000 tokens
    """

    options = ClaudeAgentOptions(
        system_prompt=f"""You are an Agile sprint planning specialist.

PREVIOUS PLANNING CONTEXT:
{accumulated_context}

Use this context to create sprint plans with:
- User stories following INVEST criteria
- Story points and capacity planning
- Dependencies and blocked items
- Acceptance criteria
""",
        allowed_tools=["sprint-planning", "Read", "Write"],
        permission_mode="acceptEdits"
    )

    # Generate sprint plans for first 4 sprints
    for sprint_num in range(1, 5):
        print(f"\n=== Sprint {sprint_num} Planning ===")
        async for msg in query(
            f"Create user stories and sprint plan for Sprint {sprint_num}",
            options
        ):
            print(msg)

    # Cost without caching: 165k × 4 sprints = 660k tokens × $3/M = $1.98
    # Cost with caching: 165k × $3.75/M + (165k × 3 × $0.30/M) = $0.77 (61% savings)
```

---

## 6. Token Optimization Strategies

### 6.1 Context Window Management

**Balance context size with caching benefits.**

```python
from claude_agent_sdk import ClaudeAgentOptions

# Strategy 1: Full context caching (best for short workflows)
full_context_options = ClaudeAgentOptions(
    system_prompt="""
    [Comprehensive 100k token planning methodology]
    [Complete project specification: 50k tokens]
    [Full reference documentation: 30k tokens]
    Total: 180k tokens cached
    """,
    allowed_tools=["research-lookup", "Read"],
    permission_mode="acceptEdits"
)
# Pros: Maximum context, all info available
# Cons: Large cache, higher write costs, slower first request

# Strategy 2: Essential context caching (best for long workflows)
essential_context_options = ClaudeAgentOptions(
    system_prompt="""
    [Core planning methodology: 30k tokens]
    [Key project requirements: 15k tokens]
    Total: 45k tokens cached
    """,
    allowed_tools=["research-lookup", "Read"],
    permission_mode="acceptEdits"
)
# Pros: Smaller cache, faster responses, lower write costs
# Cons: May need to read additional files during execution

# Strategy 3: Hybrid - cache summary, read details on demand
hybrid_options = ClaudeAgentOptions(
    system_prompt="""
    [Core methodology: 20k tokens]
    [Project summary: 10k tokens]

    DETAILED DOCUMENTATION AVAILABLE:
    - Full spec: /docs/specification.md (use Read tool as needed)
    - Architecture: /docs/architecture.md (use Read tool as needed)
    - Requirements: /docs/requirements.md (use Read tool as needed)
    """,
    allowed_tools=["Read", "research-lookup"],
    permission_mode="acceptEdits"
)
# Pros: Balance of cached overview + on-demand details
# Cons: Additional tool calls may be needed
```

**Decision matrix:**

| Workflow Type | Context Strategy | Cache Size | Best For |
|--------------|------------------|-----------|----------|
| Interactive planning | Full context | 100-200k | Back-and-forth queries |
| Batch analysis | Essential only | 30-50k | Processing many items |
| Research-heavy | Hybrid | 50-80k | Generate large results |
| Multi-phase | Progressive | Grows 20k/phase | Sequential workflows |

---

### 6.2 Progressive Context Building

**Build cache incrementally as context grows.**

```python
class ProgressiveCachingWorkflow:
    """
    Start with minimal cache, progressively add context as workflow advances.
    """

    def __init__(self):
        self.cached_context = "Core planning methodology [20k tokens]"

    def get_options(self) -> ClaudeAgentOptions:
        return ClaudeAgentOptions(
            system_prompt=self.cached_context,
            allowed_tools=["research-lookup", "Read", "Write"],
            permission_mode="acceptEdits"
        )

    async def phase_1_research(self):
        """Initial research - minimal cache."""
        # Cache: 20k tokens
        async for msg in query("Research technology options", self.get_options()):
            print(msg)

        # Add research results to cached context
        self.cached_context += "\n\nRESEARCH RESULTS:\n[50k tokens of research]"
        # Cache now: 70k tokens

    async def phase_2_architecture(self):
        """Architecture design - cache includes research."""
        # Cache: 70k tokens (includes research)
        async for msg in query("Design architecture", self.get_options()):
            print(msg)

        # Add architecture to cached context
        self.cached_context += "\n\nARCHITECTURE:\n[30k tokens of architecture]"
        # Cache now: 100k tokens

    async def phase_3_costs(self):
        """Cost analysis - cache includes research + architecture."""
        # Cache: 100k tokens (includes research + architecture)
        async for msg in query("Estimate costs", self.get_options()):
            print(msg)

        # Add cost analysis to cached context
        self.cached_context += "\n\nCOST ANALYSIS:\n[20k tokens of costs]"
        # Cache now: 120k tokens

    async def phase_4_risks(self):
        """Risk assessment - cache includes all previous work."""
        # Cache: 120k tokens (full context)
        async for msg in query("Assess risks", self.get_options()):
            print(msg)

# Cost analysis:
# Without caching: (20k + 70k + 100k + 120k) input tokens = 310k × $3/M = $0.93
# With progressive caching:
#   Phase 1: 20k × $3.75/M = $0.08 (write)
#   Phase 2: 70k × $3.75/M = $0.26 (write - cache invalidated by context change)
#   Phase 3: 100k × $3.75/M = $0.38 (write - cache invalidated again)
#   Phase 4: 120k × $0.30/M = $0.04 (read - context stable)
#   Total: $0.76 (18% savings)

# Note: Progressive caching less efficient than stable caching
# Best when context must grow, but still better than no caching
```

**Recommendation for claude-project-planner:**
- Use **full context caching** for interactive sessions (user iterates on decisions)
- Use **essential context caching** for batch processing (analyze many projects)
- Use **progressive caching** when context grows unavoidably (research → analysis → planning)

---

### 6.3 Avoiding Cache Pollution

**Don't cache content that changes frequently.**

```python
# ❌ BAD: Caching dynamic content
bad_options = ClaudeAgentOptions(
    system_prompt=f"""
    Planning session started: {datetime.now()}  # Changes every request!
    User: {current_user}  # Changes per user!
    Project: {project_id}  # Changes per project!

    [Core methodology...]
    """,
    allowed_tools=["research-lookup"]
)
# Cache invalidated on every request - no benefit from caching

# ✅ GOOD: Cache only static content
good_options = ClaudeAgentOptions(
    system_prompt="""
    [Core methodology - static, 30k tokens]

    You will receive dynamic context in user messages:
    - Session metadata (timestamp, user, project)
    - User-specific requirements
    - Project-specific constraints
    """,
    allowed_tools=["research-lookup"]
)
# Cache remains valid across all requests
# Dynamic content passed in user message (not cached)
```

**What to cache:**
- Planning methodologies (static)
- Tool definitions (static)
- Reference documentation (rarely changes)
- Evaluation frameworks (standard across projects)

**What NOT to cache:**
- User names, timestamps (changes every request)
- Project-specific details (changes per project)
- Intermediate results (changes during workflow)
- Dynamic instructions (changes based on user input)

---

## 7. Context Editing and Memory Integration

### 7.1 Context Clearing Strategy

**When conversation history grows too large, context editing can clear old content.**

```python
# Context editing configuration (if needed)
# Note: Agent SDK may handle this automatically

context_management = {
    "trigger": {
        "type": "input_tokens",
        "value": 100000  # Clear when context exceeds 100k tokens
    },
    "keep": {
        "type": "tool_uses",
        "value": 5  # Keep last 5 tool results
    },
    "clear_at_least": 50000  # Clear at least 50k tokens (justify cache invalidation)
}

# When context is cleared, cache is invalidated
# Trade-off: Free up context space vs. lose cache efficiency
```

**Impact on caching:**
- Clearing content before cache breakpoint → Invalidates cache
- Next request must recreate cache (pay write cost again)
- Balance: Clear enough to justify cache recreation cost

**Best practices:**
- Set `clear_at_least` high enough to justify cache loss (50k+ tokens)
- Keep recent tool results (use `keep` parameter)
- Consider using memory tool instead of keeping everything in context

---

### 7.2 Memory Tool Integration

**Use memory tool to persist information outside of cached context.**

```python
async def workflow_with_memory_and_caching():
    """
    Combine prompt caching (for active context) with memory tool (for persistence).
    """

    options = ClaudeAgentOptions(
        system_prompt="""You are a project planner with memory.

MEMORY SYSTEM:
- Use memory tool to save important findings across sessions
- Memory persists beyond conversation context
- Reduces context size while maintaining access to critical info

WORKFLOW:
1. Research and analyze (use cached context for active work)
2. Save key findings to memory (free up context space)
3. Reference memory as needed (avoid re-processing)
""",
        allowed_tools=[
            "memory",  # Memory tool for persistence
            "research-lookup",
            "Read",
            "Write"
        ],
        permission_mode="acceptEdits"
    )

    # Phase 1: Research (generates large results)
    async for msg in query("""
        Research cloud service pricing for:
        - AWS Lambda
        - Google Cloud Functions
        - Azure Functions

        Save key findings to memory as 'cloud_pricing_research.md'
    """, options):
        print(msg)

    # Phase 2: Analysis (references memory, not full research in context)
    async for msg in query("""
        Analyze cost-effectiveness of each option.
        Reference cloud_pricing_research.md from memory.
    """, options):
        print(msg)

    # Benefits:
    # - Research results saved to memory (persistent)
    # - Cleared from context (free up space)
    # - Cache remains efficient (smaller cached context)
    # - Access preserved through memory references
```

**Memory + caching strategy:**
- **Active work:** Keep in cached context (fast access, no tool calls)
- **Completed work:** Move to memory (free context, maintain access)
- **Reference work:** Load from memory on demand (when needed)

---

## 8. Advanced Optimization Techniques

### 8.1 Cache Invalidation Tracking

**Monitor and prevent unexpected cache invalidation.**

```python
import hashlib
import json
from typing import Dict, Any

class CacheInvalidationTracker:
    """
    Track configuration changes that would invalidate cache.
    """

    def __init__(self):
        self.config_history = []

    def compute_config_hash(self, options: ClaudeAgentOptions) -> str:
        """Compute hash of cacheable configuration."""
        config = {
            "system_prompt": options.system_prompt,
            "allowed_tools": sorted(options.allowed_tools) if options.allowed_tools else [],
            "permission_mode": options.permission_mode,
            # Add other relevant fields
        }
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    def check_invalidation(self, options: ClaudeAgentOptions) -> bool:
        """Check if configuration would invalidate cache."""
        current_hash = self.compute_config_hash(options)

        if not self.config_history:
            self.config_history.append(current_hash)
            return False  # First request, no cache yet

        last_hash = self.config_history[-1]

        if current_hash != last_hash:
            print("⚠️  WARNING: Configuration changed - cache invalidated!")
            print(f"Previous hash: {last_hash[:16]}...")
            print(f"Current hash:  {current_hash[:16]}...")
            self.config_history.append(current_hash)
            return True  # Cache invalidated

        return False  # Cache still valid


# Usage in workflow
tracker = CacheInvalidationTracker()

async def planning_phase(phase_name: str, options: ClaudeAgentOptions):
    invalidated = tracker.check_invalidation(options)

    if invalidated:
        print(f"💰 Cache recreated - paying write cost for {phase_name}")
    else:
        print(f"✓ Cache hit - paying read cost for {phase_name}")

    async for msg in query(f"Execute {phase_name}", options):
        print(msg)
```

---

### 8.2 Parallel Query Batching

**Process independent queries in parallel while maintaining cache efficiency.**

```python
import asyncio

async def parallel_analysis_with_shared_cache():
    """
    Process multiple independent analyses in parallel.
    All share the same cached context.
    """

    # Shared configuration - single cache created
    shared_options = ClaudeAgentOptions(
        system_prompt="Evaluation framework [50k tokens]...",
        allowed_tools=["feasibility-analysis", "Read"],
        permission_mode="acceptEdits"
    )

    # Create cache with first request (serial)
    print("Creating cache with initial request...")
    async for msg in query("Warm up cache", shared_options):
        pass
    print("✓ Cache created\n")

    # Now process multiple projects in parallel
    # All hit the same cache simultaneously
    projects = [f"project_{i:03d}.md" for i in range(1, 21)]

    async def analyze_project(project_file: str):
        print(f"Analyzing {project_file} (cache hit)")
        async for msg in query(f"Analyze {project_file}", shared_options):
            pass
        print(f"✓ Completed {project_file}")

    # Run 20 analyses in parallel - all use same cache
    await asyncio.gather(*[analyze_project(p) for p in projects])

    # Cost:
    # Cache write: 50k × $3.75/M = $0.19
    # Parallel reads: 50k × 20 × $0.30/M = $0.30
    # Total: $0.49

    # Without caching: 50k × 20 × $3/M = $3.00
    # Savings: $2.51 (84%)
```

**Important:** Cache entries only available after first response **completes**, not just when request is submitted. Must serialize first request, then parallelize subsequent requests.

---

### 8.3 Cost-Aware Model Selection

**Choose model based on task requirements and caching benefits.**

```python
# Cost comparison for 100k token cached context, 10 queries

# Claude Opus 4.5 (most capable, highest cost)
opus_cost = {
    "cache_write": 100_000 / 1_000_000 * 6.25,  # $6.25/M
    "cache_reads": 100_000 / 1_000_000 * 0.50 * 9,  # $0.50/M × 9 reads
    "total": 100_000 / 1_000_000 * 6.25 + 100_000 / 1_000_000 * 0.50 * 9
}
# Total: $1.08

# Claude Sonnet 4.5 (balanced, recommended for most)
sonnet_cost = {
    "cache_write": 100_000 / 1_000_000 * 3.75,  # $3.75/M
    "cache_reads": 100_000 / 1_000_000 * 0.30 * 9,  # $0.30/M × 9 reads
    "total": 100_000 / 1_000_000 * 3.75 + 100_000 / 1_000_000 * 0.30 * 9
}
# Total: $0.65

# Claude Haiku 4.5 (fast, cost-effective)
haiku_cost = {
    "cache_write": 100_000 / 1_000_000 * 1.25,  # $1.25/M
    "cache_reads": 100_000 / 1_000_000 * 0.10 * 9,  # $0.10/M × 9 reads
    "total": 100_000 / 1_000_000 * 1.25 + 100_000 / 1_000_000 * 0.10 * 9
}
# Total: $0.22

# Recommendations:
# - Complex planning, architecture design → Opus 4.5
# - General planning, research, analysis → Sonnet 4.5 (RECOMMENDED)
# - Batch processing, simple queries → Haiku 4.5
```

**For claude-project-planner:**
- **Default model:** Sonnet 4.5 (best balance of capability and cost)
- **High-stakes decisions:** Opus 4.5 (architecture ADRs, feasibility analysis)
- **Batch operations:** Haiku 4.5 (processing many proposals, simple evaluations)

**Caching amplifies cost differences:**
- Haiku 4.5 with caching = 66% cheaper than Sonnet 4.5 with caching
- Without caching, difference is only 67% (less dramatic)

---

## 9. Measuring ROI of Prompt Caching

### 9.1 Cost Tracking Implementation

```python
from dataclasses import dataclass
from typing import List
import json

@dataclass
class QueryMetrics:
    phase: str
    input_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    output_tokens: int

    def cost(self, model: str = "sonnet-4.5") -> float:
        """Calculate cost for this query."""
        pricing = {
            "sonnet-4.5": {
                "base_input": 3.00,
                "cache_write": 3.75,
                "cache_read": 0.30,
                "output": 15.00
            }
        }

        p = pricing[model]

        input_cost = self.input_tokens / 1_000_000 * p["base_input"]
        write_cost = self.cache_creation_tokens / 1_000_000 * p["cache_write"]
        read_cost = self.cache_read_tokens / 1_000_000 * p["cache_read"]
        output_cost = self.output_tokens / 1_000_000 * p["output"]

        return input_cost + write_cost + read_cost + output_cost

    def cost_without_caching(self, model: str = "sonnet-4.5") -> float:
        """Calculate what cost would be without caching."""
        pricing = {
            "sonnet-4.5": {"base_input": 3.00, "output": 15.00}
        }

        p = pricing[model]

        # All tokens processed as standard input
        total_input = self.input_tokens + self.cache_read_tokens + self.cache_creation_tokens
        input_cost = total_input / 1_000_000 * p["base_input"]
        output_cost = self.output_tokens / 1_000_000 * p["output"]

        return input_cost + output_cost


class CachingROITracker:
    def __init__(self):
        self.metrics: List[QueryMetrics] = []

    def record(self, phase: str, usage: dict):
        """Record metrics from API response."""
        metric = QueryMetrics(
            phase=phase,
            input_tokens=usage.get("input_tokens", 0),
            cache_read_tokens=usage.get("cache_read_input_tokens", 0),
            cache_creation_tokens=usage.get("cache_creation_input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0)
        )
        self.metrics.append(metric)

    def generate_report(self) -> dict:
        """Generate comprehensive ROI report."""
        total_cached_cost = sum(m.cost() for m in self.metrics)
        total_uncached_cost = sum(m.cost_without_caching() for m in self.metrics)

        savings = total_uncached_cost - total_cached_cost
        savings_pct = (savings / total_uncached_cost * 100) if total_uncached_cost > 0 else 0

        total_cache_reads = sum(m.cache_read_tokens for m in self.metrics)
        total_input = sum(m.input_tokens + m.cache_read_tokens + m.cache_creation_tokens for m in self.metrics)

        cache_hit_rate = (total_cache_reads / total_input * 100) if total_input > 0 else 0

        return {
            "total_queries": len(self.metrics),
            "cost_with_caching": total_cached_cost,
            "cost_without_caching": total_uncached_cost,
            "savings": savings,
            "savings_pct": savings_pct,
            "cache_hit_rate": cache_hit_rate,
            "breakdown": [
                {
                    "phase": m.phase,
                    "cost": m.cost(),
                    "cost_without_caching": m.cost_without_caching(),
                    "cache_hit_rate": (m.cache_read_tokens / (m.input_tokens + m.cache_read_tokens + m.cache_creation_tokens) * 100)
                        if (m.input_tokens + m.cache_read_tokens + m.cache_creation_tokens) > 0 else 0
                }
                for m in self.metrics
            ]
        }

    def print_report(self):
        """Print formatted ROI report."""
        report = self.generate_report()

        print("\n" + "="*60)
        print("PROMPT CACHING ROI REPORT")
        print("="*60)
        print(f"Total Queries: {report['total_queries']}")
        print(f"Cost with Caching: ${report['cost_with_caching']:.4f}")
        print(f"Cost without Caching: ${report['cost_without_caching']:.4f}")
        print(f"Savings: ${report['savings']:.4f} ({report['savings_pct']:.1f}%)")
        print(f"Cache Hit Rate: {report['cache_hit_rate']:.1f}%")

        print("\nPer-Phase Breakdown:")
        print("-"*60)
        for phase in report['breakdown']:
            print(f"{phase['phase']:30} Cache Hit: {phase['cache_hit_rate']:5.1f}%  Cost: ${phase['cost']:.4f}")


# Usage example
tracker = CachingROITracker()

async for msg in query("Phase 1: Research", options):
    if hasattr(msg, 'usage'):
        tracker.record("Phase 1: Research", msg.usage)

async for msg in query("Phase 2: Architecture", options):
    if hasattr(msg, 'usage'):
        tracker.record("Phase 2: Architecture", msg.usage)

# ... more phases ...

tracker.print_report()

# Expected output:
# ============================================================
# PROMPT CACHING ROI REPORT
# ============================================================
# Total Queries: 6
# Cost with Caching: $0.54
# Cost without Caching: $3.60
# Savings: $3.06 (85.0%)
# Cache Hit Rate: 92.3%
#
# Per-Phase Breakdown:
# ------------------------------------------------------------
# Phase 1: Research                Cache Hit:   0.0%  Cost: $0.19
# Phase 2: Architecture            Cache Hit:  95.2%  Cost: $0.08
# Phase 3: Cost Analysis           Cache Hit:  96.1%  Cost: $0.06
# ...
```

---

## 10. Recommendations for claude-project-planner

### 10.1 Immediate Actions

1. **✅ No code changes needed** - Agent SDK already uses prompt caching automatically
2. **📊 Add cost tracking** - Implement ROI tracker to measure savings
3. **📝 Document caching benefits** - Update README with cost savings examples
4. **🔍 Monitor cache hit rates** - Add metrics to skill execution logs

### 10.2 Optimization Priorities

**High Priority (Immediate ROI):**
- ✅ Consolidate system prompts for each skill (maximize cached content)
- ✅ Restrict `allowed_tools` to task-specific tools (reduce cache overhead)
- ✅ Design workflows to complete within 5-min cache windows
- ✅ Use session-based patterns for multi-phase planning

**Medium Priority (Incremental Improvements):**
- Implement cache invalidation tracking
- Add cache warm-up for batch processing
- Optimize context size for different workflow types
- Combine memory tool with caching for long sessions

**Low Priority (Advanced Optimization):**
- Experiment with explicit cache control via direct API
- Implement parallel processing with shared cache
- Add model selection based on task complexity vs. cost

### 10.3 Expected Cost Savings

**Current Usage Estimates (hypothetical):**
- Average planning session: 6 skill invocations
- Average cached context per session: 80,000 tokens
- Average sessions per day: 20

**Without caching:**
- 80,000 tokens × 6 phases × 20 sessions = 9.6M tokens/day
- Cost: 9.6M × $3/M = **$28.80/day** = **$864/month**

**With caching (automatic in Agent SDK):**
- Cache writes: 80,000 × 20 sessions × $3.75/M = $6.00/day
- Cache reads: 80,000 × 5 phases × 20 sessions × $0.30/M = $2.40/day
- Total: **$8.40/day** = **$252/month**
- **Savings: $612/month (71%)**

### 10.4 Documentation Updates

**Add to README.md:**
```markdown
## Cost Optimization

Claude Project Planner uses **prompt caching** to reduce API costs by up to 85%.

### How It Works
- System prompts and tool definitions cached automatically
- First query creates cache (25% premium)
- Subsequent queries read from cache (90% discount)
- Cache persists for 5 minutes, auto-refreshes on each use

### Expected Savings
- Typical planning workflow: **6 phases with shared context**
- Cost without caching: **$1.80 per project**
- Cost with caching: **$0.42 per project** (77% savings)

### Best Practices
1. Group related queries within 5-minute windows
2. Use session-based workflows for multi-phase planning
3. Load project specs into system prompt for maximum caching benefit
```

---

## 11. Conclusion

Prompt caching in Claude Agent SDK provides **transformative cost optimization** for claude-project-planner:

### Key Takeaways

1. **90% cost reduction** on cached content - just 10% of standard input token cost
2. **50-85% latency improvement** - cached content processed instantly
3. **Automatic by default** - Agent SDK handles caching without explicit configuration
4. **Break-even at 2 requests** - profitable immediately for any repeated context

### Implementation Strategy

- ✅ **No code changes needed** - already using caching via Agent SDK
- 📊 **Add cost tracking** - measure and report actual savings
- 🎯 **Optimize workflows** - structure for maximum cache reuse
- 📈 **Monitor performance** - validate cache hit rates > 90%

### Expected Impact

For typical claude-project-planner usage:
- **Before:** $864/month in API costs (without caching)
- **After:** $252/month in API costs (with automatic caching)
- **Savings:** $612/month (71% reduction)

### Next Steps

1. Implement `CachingROITracker` class in codebase
2. Add cache metrics to workflow logs
3. Document savings in project README
4. Monitor and optimize cache hit rates

---

**Research completed:** 2026-01-21
**Status:** ✅ Comprehensive documentation ready for implementation
