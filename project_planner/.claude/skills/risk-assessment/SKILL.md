---
name: risk-assessment
description: "Project risk assessment toolkit. Identify technical, business, resource, and external risks, score likelihood and impact, define mitigation strategies and contingency plans for comprehensive risk management."
allowed-tools: [Read, Write, Edit, Bash]
---

# Risk Assessment

## Overview

Risk assessment is a systematic process for identifying, analyzing, and planning responses to project risks. Evaluate technical, business, resource, and external risks, score by likelihood and impact, and define mitigation strategies and contingency plans to manage project uncertainty.

## When to Use This Skill

This skill should be used when:
- Identifying risks in new project plans
- Assessing technical and architectural risks
- Evaluating business and market risks
- Planning risk mitigations and contingencies
- Creating risk registers for projects
- Monitoring and updating risk status

## Visual Enhancement with Project Diagrams

**When documenting risk assessments, include visualizations.**

Use the **project-diagrams** skill to generate:
- Risk heat maps (likelihood vs. impact matrix)
- Risk category breakdown charts
- Mitigation timeline diagrams
- Decision trees for contingency plans

```bash
python .claude/skills/project-diagrams/scripts/generate_schematic.py "diagram description" -o diagrams/output.png
```

---

## Risk Assessment Framework

### Risk Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **Technical** | Technology and implementation risks | Integration failures, scalability issues, technical debt |
| **Security** | Data and system security risks | Breaches, vulnerabilities, compliance failures |
| **Resource** | Team and capacity risks | Key person dependency, skill gaps, turnover |
| **External** | Third-party and environmental risks | API changes, vendor reliability, regulatory changes |
| **Business** | Market and financial risks | Competition, market changes, budget cuts |
| **Timeline** | Schedule and delivery risks | Scope creep, estimation errors, dependencies |
| **Operational** | Production and support risks | Downtime, incident response, maintenance |

### Risk Scoring Matrix

**Likelihood Scale:**

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Rare | < 10% probability, unlikely to occur |
| 2 | Unlikely | 10-30% probability, could occur |
| 3 | Possible | 30-50% probability, might occur |
| 4 | Likely | 50-80% probability, will probably occur |
| 5 | Almost Certain | > 80% probability, expected to occur |

**Impact Scale:**

| Score | Level | Description |
|-------|-------|-------------|
| 1 | Negligible | Minor inconvenience, easily absorbed |
| 2 | Minor | Some disruption, workaround available |
| 3 | Moderate | Significant impact, requires response |
| 4 | Major | Serious impact, threatens objectives |
| 5 | Critical | Catastrophic, project failure possible |

**Risk Score Calculation:**
```
Risk Score = Likelihood x Impact

1-4:   Low risk (green)
5-9:   Medium risk (yellow)
10-15: High risk (orange)
16-25: Critical risk (red)
```

### Response Strategies

| Strategy | When to Use | Example |
|----------|-------------|---------|
| **Avoid** | Eliminate the risk entirely | Change technology, remove feature |
| **Mitigate** | Reduce likelihood or impact | Add redundancy, implement safeguards |
| **Transfer** | Shift risk to third party | Insurance, outsourcing, SLAs |
| **Accept** | Acknowledge and monitor | Low-impact risks, cost-effective |

## Risk Specification Schema

```yaml
risk:
  id: "RISK-NNN"
  title: "Short descriptive title"
  category: "technical | security | resource | external | business | timeline | operational"
  description: "What is the risk? What could go wrong?"
  cause: "What could cause this risk to materialize?"
  effect: "What would be the impact if this risk materializes?"
  likelihood: 1-5
  likelihood_rationale: "Why this likelihood score"
  impact: 1-5
  impact_rationale: "Why this impact score"
  risk_score: N  # likelihood x impact
  risk_level: "low | medium | high | critical"
  response_strategy: "avoid | mitigate | transfer | accept"
  mitigation:
    actions:
      - "Specific action to reduce likelihood or impact"
    responsible: "Team or person"
    deadline: "YYYY-MM-DD"
    cost: "Estimated cost if applicable"
  contingency:
    trigger: "What indicates this risk has materialized"
    actions:
      - "Action to take if risk occurs"
    responsible: "Team or person"
  status: "identified | mitigating | monitoring | closed | materialized"
  owner: "Person responsible for tracking"
  identified_date: "YYYY-MM-DD"
  last_reviewed: "YYYY-MM-DD"
  related_risks: ["RISK-XXX"]
```

For detailed example risk entries across all categories (technical, security, resource, external, timeline), see `references/common_risks.md`.

## Risk Register Template

```yaml
risk_register:
  project: "[Project Name]"
  last_updated: "YYYY-MM-DD"
  summary:
    total_risks: N
    critical: N
    high: N
    medium: N
    low: N
  risks:
    - id: "RISK-001"
      title: "..."
      category: "..."
      # ... full specification
  review_schedule:
    frequency: "Every sprint"
    next_review: "YYYY-MM-DD"
    reviewer: "Project Manager"
```

## Risk Assessment Report Structure

```markdown
# Risk Assessment Report: [Project Name]

## Executive Summary
- Total risks identified: N
- Critical/High risks: N (requiring immediate attention)
- Primary risk areas: [Categories]
- Overall risk level: [Low/Medium/High]

## Risk Heat Map
[Visual representation of risks by likelihood/impact]

## Critical and High Risks
### RISK-001: [Title]
**Score:** [N] (Critical/High) | **Category:** [Category]
**Description:** [What could go wrong]
**Mitigation:** [Actions] | **Contingency:** [If risk materializes]
**Owner:** [Person responsible]

## Medium and Low Risks
| ID | Title | Category | Score | Status |
|----|-------|----------|-------|--------|

## Risk Monitoring Plan
| Risk ID | Metric to Monitor | Review Frequency | Trigger |
|---------|-------------------|------------------|---------|

## Recommendations
1. [Key action to reduce overall risk]
```

## Risk Assessment Process

### Phase 1: Risk Identification
**Techniques:** Brainstorming, checklist review, assumption analysis, expert interviews, historical review.

**Questions to Ask:** What could go wrong? What assumptions are we making? What dependencies do we have? What has failed in similar projects?

### Phase 2: Risk Analysis
For each identified risk: describe clearly, identify root causes, assess effects, score likelihood (1-5), score impact (1-5), calculate risk score, determine risk level.

### Phase 3: Risk Response Planning
For high and critical risks: choose response strategy, define mitigation actions, assign ownership, set deadlines, define contingency plans, identify triggers.

### Phase 4: Risk Monitoring
Ongoing: review risk register each sprint, update scores, track mitigation completion, monitor triggers, add new risks, close resolved risks.

## Quality Checklist

- [ ] All risk categories considered
- [ ] Risks clearly described with cause and effect
- [ ] Likelihood and impact scored with rationale
- [ ] High/Critical risks have mitigation plans
- [ ] Contingency plans defined with triggers
- [ ] Risk owners assigned
- [ ] Review schedule established
- [ ] Risk heat map generated
- [ ] Stakeholders aware of critical risks

## Best Practices

**Do's:** Involve the whole team, be specific about causes/effects, update regularly, track mitigation completion, learn from materialized risks, communicate transparently.

**Don'ts:** Ignore "unlikely" high-impact risks, set and forget, underestimate security risks, assume risks are someone else's problem, let risk assessment become a checkbox exercise.
