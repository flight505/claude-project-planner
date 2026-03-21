# Risk Assessment - Common Risk Examples by Category

Use these examples as templates when identifying project risks. Adapt the specifics to match your project context.

## Technical Risks

```yaml
risks:
  - id: "RISK-T001"
    title: "Integration Complexity"
    category: "technical"
    description: |
      Third-party API integrations prove more complex than estimated,
      requiring additional development time.
    cause: |
      - Poor API documentation
      - Undocumented edge cases
      - Version incompatibilities
    effect: |
      - Sprint delays
      - Increased development cost
      - Technical debt
    likelihood: 3
    impact: 3
    risk_score: 9
    risk_level: "medium"
    response_strategy: "mitigate"
    mitigation:
      actions:
        - "Prototype integrations in Sprint 1"
        - "Create abstraction layer for external dependencies"
        - "Document fallback approaches"
      responsible: "Tech Lead"
      deadline: "End of Sprint 1"
    contingency:
      trigger: "Integration spike takes >3 days"
      actions:
        - "Evaluate alternative providers"
        - "Adjust timeline and communicate to stakeholders"
    status: "identified"

  - id: "RISK-T002"
    title: "Scalability Issues"
    category: "technical"
    description: |
      System architecture cannot handle projected user growth,
      requiring significant rearchitecture.
    cause: |
      - Underestimated traffic growth
      - Inefficient database queries
      - Synchronous processing bottlenecks
    effect: |
      - Performance degradation
      - User experience impact
      - Costly emergency fixes
    likelihood: 2
    impact: 4
    risk_score: 8
    risk_level: "medium"
    response_strategy: "mitigate"
    mitigation:
      actions:
        - "Design for 10x expected load"
        - "Implement caching layer from start"
        - "Plan load testing in Sprint 3"
    contingency:
      trigger: "Response times exceed 2 seconds at 50% projected load"
      actions:
        - "Emergency scale-up infrastructure"
        - "Activate CDN for static assets"
        - "Implement request queuing"
    status: "identified"
```

## Security Risks

```yaml
risks:
  - id: "RISK-S001"
    title: "Data Breach"
    category: "security"
    description: |
      Unauthorized access to user data due to security vulnerability.
    cause: |
      - Unpatched vulnerabilities
      - Weak authentication
      - SQL injection or XSS
    effect: |
      - Regulatory fines (GDPR)
      - Reputation damage
      - Legal liability
    likelihood: 2
    impact: 5
    risk_score: 10
    risk_level: "high"
    response_strategy: "mitigate"
    mitigation:
      actions:
        - "Security audit before launch"
        - "Implement WAF and rate limiting"
        - "Enable encryption at rest and in transit"
        - "Conduct penetration testing"
      responsible: "Security Team"
      cost: "$5,000-10,000"
    contingency:
      trigger: "Detection of unauthorized access"
      actions:
        - "Activate incident response plan"
        - "Isolate affected systems"
        - "Notify affected users within 72 hours"
        - "Engage forensic investigation"
    status: "identified"
```

## Resource Risks

```yaml
risks:
  - id: "RISK-R001"
    title: "Key Person Dependency"
    category: "resource"
    description: |
      Critical project knowledge concentrated in one team member,
      creating single point of failure.
    cause: |
      - Complex domain expertise
      - Specialized technical skills
      - Insufficient documentation
    effect: |
      - Project delays if person unavailable
      - Knowledge loss if person leaves
      - Bottleneck in decision making
    likelihood: 3
    impact: 4
    risk_score: 12
    risk_level: "high"
    response_strategy: "mitigate"
    mitigation:
      actions:
        - "Document all architectural decisions (ADRs)"
        - "Pair programming on critical components"
        - "Cross-train at least 2 team members"
      responsible: "Engineering Manager"
    contingency:
      trigger: "Key person unavailable > 1 week"
      actions:
        - "Activate backup assignee"
        - "Prioritize documentation catch-up"
        - "Consider contractor for specialized skills"
    status: "identified"
```

## External Risks

```yaml
risks:
  - id: "RISK-E001"
    title: "Third-Party API Deprecation"
    category: "external"
    description: |
      Critical third-party API announces deprecation or breaking changes
      during project timeline.
    cause: |
      - Vendor business changes
      - Technology evolution
      - Acquisition or shutdown
    effect: |
      - Forced migration effort
      - Timeline delays
      - Potential feature loss
    likelihood: 2
    impact: 3
    risk_score: 6
    risk_level: "medium"
    response_strategy: "mitigate"
    mitigation:
      actions:
        - "Abstract all external dependencies"
        - "Identify alternative providers"
        - "Monitor vendor announcements"
      responsible: "Tech Lead"
    contingency:
      trigger: "Deprecation announcement or breaking change"
      actions:
        - "Assess migration timeline"
        - "Evaluate alternative providers"
        - "Adjust project timeline if needed"
    status: "identified"
```

## Timeline Risks

```yaml
risks:
  - id: "RISK-TL001"
    title: "Scope Creep"
    category: "timeline"
    description: |
      Requirements expand beyond original scope, consuming budget
      and extending timeline.
    cause: |
      - Unclear initial requirements
      - Stakeholder additions
      - "Just one more feature" syndrome
    effect: |
      - Budget overrun
      - Timeline extension
      - Team burnout
    likelihood: 4
    impact: 3
    risk_score: 12
    risk_level: "high"
    response_strategy: "mitigate"
    mitigation:
      actions:
        - "Document scope in detail before starting"
        - "Implement change request process"
        - "Regular scope reviews in sprint planning"
        - "Prioritize MVP features ruthlessly"
      responsible: "Product Owner"
    contingency:
      trigger: "Scope increases by >20% from baseline"
      actions:
        - "Formal change request required"
        - "Adjust timeline or budget"
        - "Deprioritize lower-value features"
    status: "identified"
```
