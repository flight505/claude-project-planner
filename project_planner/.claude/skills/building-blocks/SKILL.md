---
name: building-blocks
description: "Component specification toolkit for breaking software projects into discrete, buildable blocks. Create detailed specifications with interfaces, dependencies, test criteria, and effort estimates for Claude Code to build incrementally."
allowed-tools: [Read, Write, Edit, Bash]
---

# Building Blocks Specification

## Overview

Building blocks are discrete, independently buildable components that together form a complete software system. This skill helps you decompose projects into well-specified blocks that Claude Code can build incrementally, with clear interfaces, dependencies, and acceptance criteria.

## When to Use This Skill

This skill should be used when:
- Decomposing a system into buildable components
- Creating detailed component specifications
- Defining interfaces between components
- Specifying API contracts and events
- Estimating effort and complexity
- Planning incremental delivery

## Visual Enhancement with Project Diagrams

**When documenting building blocks, always include diagrams.**

Use the **project-diagrams** skill to generate:
- Component dependency diagrams
- Interface contract visualizations
- Data flow between components
- Build sequence diagrams

```bash
python .claude/skills/project-diagrams/scripts/generate_schematic.py "diagram description" -o diagrams/output.png
```

---

## Building Block Framework

### Block Types

| Type | Description | Examples |
|------|-------------|----------|
| **frontend** | User interface components | Dashboard, Forms, Navigation |
| **backend** | Server-side services | Auth Service, API Gateway, Business Logic |
| **infrastructure** | Platform and DevOps | CI/CD, Monitoring, Database Setup |
| **integration** | External system connectors | Payment Gateway, Email Service, Third-party APIs |
| **shared** | Cross-cutting components | Logging, Configuration, Utilities |

### Block Specification Schema

```yaml
building_block:
  # Identity
  name: "string - clear, descriptive name"
  id: "string - unique identifier (e.g., BB-001)"
  type: "frontend | backend | infrastructure | integration | shared"

  # Description
  description: "string - what this block does and why"
  responsibilities:
    - "string - specific responsibility 1"

  # Dependencies
  dependencies:
    internal:
      - block_id: "BB-XXX"
        type: "required | optional"
        interface: "interface name"
    external:
      - name: "PostgreSQL"
        version: ">=14.0"
        purpose: "Primary data storage"

  # Interfaces
  interfaces:
    api_endpoints:
      - method: "GET | POST | PUT | PATCH | DELETE"
        path: "/api/v1/resource"
        description: "What this endpoint does"
        request_schema: "schema reference or inline"
        response_schema: "schema reference or inline"
        auth_required: true | false
    events_published:
      - name: "event.name"
        description: "When this event is emitted"
        payload_schema: "schema reference"
    events_consumed:
      - name: "event.name"
        description: "How this block responds"
    data_contracts:
      - name: "Contract name"
        description: "Data structure shared"
        schema: "schema reference"

  # Estimation
  complexity: "S | M | L | XL"
  estimated_hours: number
  story_points: number

  # Quality
  test_criteria:
    - "string - acceptance criterion 1"

  # Metadata
  priority: "critical | high | medium | low"
  sprint_assignment: "Sprint N"
  owner: "string - responsible team/person"
```

### Complexity Guidelines

| Complexity | Hours | Story Points | Characteristics |
|------------|-------|--------------|-----------------|
| **S (Small)** | 4-8 | 1-2 | Single responsibility, minimal dependencies, straightforward |
| **M (Medium)** | 16-24 | 3-5 | Multiple responsibilities, some dependencies, standard patterns |
| **L (Large)** | 32-48 | 8-13 | Complex logic, multiple dependencies, custom implementations |
| **XL (Extra Large)** | 48-80 | 13-21 | Highly complex, many dependencies, novel solutions needed |

## Decomposition Process

### Step 1: Identify Domains

Start with domain-driven decomposition:
1. **List core domains** - What are the main business areas?
2. **Identify bounded contexts** - Where are the natural boundaries?
3. **Map domain interactions** - How do domains communicate?

### Step 2: Extract Components

For each domain, identify components by asking:
- What are the distinct responsibilities?
- What could be built and deployed independently?
- What has different scaling characteristics?
- What changes together vs. changes independently?

### Step 3: Define Interfaces

For each component, define: API contracts (REST, GraphQL), event contracts (messages published/consumed), data contracts (shared structures).

### Step 4: Map Dependencies

Create a dependency graph. Rules: no circular dependencies, minimize dependency chains, shared components at the bottom, infrastructure before business logic.

### Step 5: Estimate Effort

For each block: review similar past work, consider complexity factors, apply velocity adjustments, add 20-30% buffer.

For detailed specification examples (backend service, frontend component, infrastructure block), see `references/examples.md`.

## Output Format

### building_blocks.yaml

Primary output file listing all blocks:

```yaml
metadata:
  project: "[Project Name]"
  total_blocks: N
  total_estimated_hours: N
  version: "1.0.0"

building_blocks:
  - name: "Block 1"
    id: "BB-001"
    # ... full specification

dependency_graph:
  - from: "BB-002"
    to: "BB-001"
    type: "required"

build_order:
  - phase: 1
    blocks: ["BB-001", "BB-100"]
  - phase: 2
    blocks: ["BB-002", "BB-003"]
```

### Component Specifications Directory

For complex blocks, create detailed specs:

```
components/
├── building_blocks.yaml          # Master list
├── component_specs/
│   ├── BB-001_auth_service.md   # Detailed spec
│   ├── BB-002_user_service.md
│   └── BB-020_dashboard_ui.md
└── interfaces/
    ├── api_contracts.yaml        # OpenAPI specs
    └── event_contracts.yaml      # Event schemas
```

## Quality Checklist

- [ ] All system functionality covered by blocks
- [ ] No overlapping responsibilities between blocks
- [ ] Dependencies form DAG (no circular dependencies)
- [ ] All interfaces specified with schemas
- [ ] Complexity estimates are realistic
- [ ] Test criteria are specific and testable
- [ ] Build order respects dependencies
- [ ] Shared/infrastructure blocks identified
- [ ] Dependency diagram generated

## Best Practices

**Do's:** Keep blocks focused (single responsibility), make independently testable, define interfaces before implementation, include error handling in test criteria, version interface contracts, document why blocks are separated.

**Don'ts:** Create blocks too small (< 4 hours) or too large (> 80 hours), have hidden dependencies, specify implementation details in interfaces, skip test criteria, forget infrastructure blocks.
