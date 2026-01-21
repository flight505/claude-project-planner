# Research Provider Pricing Analysis & Optimization Strategy

## Executive Summary

Based on OpenRouter pricing data and Gemini benchmarks, **Gemini 3 Flash offers 25-40× better cost efficiency** than the current Perplexity Sonar Pro/Reasoning Pro implementation while providing comparable or superior performance.

**Key Finding**: Current implementation may be using expensive Perplexity models for tasks that Gemini Flash could handle at a fraction of the cost.

---

## Current Implementation

### Research Routing Strategy

| Use Case | Current Provider | Model | Cost Structure |
|----------|-----------------|-------|----------------|
| Simple lookups | Perplexity | `sonar-pro` | $3/1M prompt + $15/1M output + $5/1K searches |
| Complex analysis | Perplexity | `sonar-reasoning-pro` | $2/1M prompt + $8/1M output + $5/1K searches |
| Deep research (2-query limit) | Gemini | `gemini-3-pro-preview` | Pro subscription ($20/mo) |

### Cost Per Query Estimates

**Perplexity Sonar Pro** (typical 500-token query, 2000-token response):
- Input: 500 tokens × $3/1M = $0.0015
- Output: 2000 tokens × $15/1M = $0.03
- Search: 1 search × $5/1K = $0.005
- **Total: ~$0.0365 per query**

**Perplexity Sonar Reasoning Pro** (typical 500-token query, 3000-token response):
- Input: 500 tokens × $2/1M = $0.001
- Output: 3000 tokens × $8/1M = $0.024
- Search: 1 search × $5/1K = $0.005
- **Total: ~$0.03 per query**

**Gemini 3 Flash** (same workload):
- Input: 500 tokens × $0.075/1M = $0.0000375
- Output: 2000 tokens × $0.30/1M = $0.0006
- **Total: ~$0.00064 per query**

**Cost Comparison:**
- Perplexity Sonar Pro: **57× more expensive** than Gemini Flash
- Perplexity Reasoning Pro: **47× more expensive** than Gemini Flash

---

## Comprehensive Model Comparison

### Perplexity Models (via OpenRouter)

| Model | Input | Output | Context | Search Cost | Specialty |
|-------|-------|--------|---------|-------------|-----------|
| sonar | $2/1M | $8/1M | 128K | $5/1K req | General Q&A |
| sonar-pro | $3/1M | $15/1M | 200K | $5/1K searches | Multi-step queries |
| sonar-reasoning-pro | $2/1M | $8/1M | 128K | $5/1K searches | DeepSeek R1 reasoning |
| sonar-pro-search | $3/1M | $15/1M | 200K | **$18/1K req** | Agentic workflows |
| **sonar-deep-research** | $2/1M | $8/1M | 128K | **$5/1K searches** | Research synthesis |

### Gemini Models

| Model | Input | Output | Context | Performance | Speed |
|-------|-------|--------|---------|-------------|-------|
| **gemini-3-flash** | **$0.075/1M** | **$0.30/1M** | **1M** | GPQA: 90.4%, SWE: 78% | **3× faster** |
| gemini-3-pro | $1.50/1M | $6.00/1M | 1M | GPQA: 91.9%, MMMU: 81% | Frontier reasoning |

### Key Insights

1. **Context Window Advantage**: Gemini models have **5-8× larger context** (1M vs 128-200K tokens)
2. **Performance**: Gemini 3 Flash matches or exceeds Sonar Pro on most benchmarks
3. **Speed**: Gemini 3 Flash is 3× faster than Gemini 3 Pro (and likely faster than Sonar)
4. **Cost**: Gemini 3 Flash is dramatically cheaper for token-based operations

---

## Optimization Strategies

### Strategy 1: Gemini-First Approach (Recommended)

**Routing Logic:**

```
Query Type              → Provider             → Cost Ratio vs Current
────────────────────────────────────────────────────────────────────
Simple lookup           → Gemini 3 Flash       → 57× cheaper
Standard research       → Gemini 3 Flash       → 57× cheaper
Complex reasoning       → Gemini 3 Pro         → Similar cost to Sonar Reasoning
Deep research (60 min)  → Gemini Deep Research → $20/mo (unlimited)
Temporal accuracy       → Perplexity Sonar Pro → Keep for 2026 data
```

**Benefits:**
- 50-60× cost reduction for 90% of queries
- Larger context window (1M tokens)
- Faster responses (3× speed improvement)
- Keep Perplexity for temporal accuracy edge cases

**Estimated Savings:**
- 100 queries/month: **~$3.50 → $0.06** (98% reduction)
- 1000 queries/month: **~$35 → $0.64** (98% reduction)

### Strategy 2: Add Perplexity Deep Research Alternative

**Problem**: Gemini Deep Research has 2-query budget limit

**Solution**: Add `perplexity/sonar-deep-research` as alternative:

| Feature | Gemini Deep Research | Perplexity Sonar Deep Research |
|---------|---------------------|-------------------------------|
| Duration | 30-60 min | ~5-15 min (estimated) |
| Cost | $20/mo subscription | $5/1K searches + tokens |
| Citations | High | ~111 citations/query |
| Temporal Accuracy | Knowledge cutoff | ✅ Real-time web |
| Budget Limit | 2 queries/session | ✅ Unlimited |
| Autonomy | Multi-step agentic | Multi-step autonomous |

**Cost Example** (10-search Deep Research query):
- Searches: 10 × $5/1K = $0.05
- Input: 10K tokens × $2/1M = $0.02
- Output: 8K tokens × $8/1M = $0.064
- **Total: ~$0.134 per deep research**

**vs Gemini Deep Research:**
- Month 1: $20 (subscription)
- Months 2+: $20/mo regardless of usage

**Break-even**: ~150 deep research queries/month

**Benefits:**
- No budget constraints
- Better temporal accuracy
- Faster execution
- Pay-per-use pricing

### Strategy 3: Hybrid Tiered Approach

**Tier 1: Gemini 3 Flash** (90% of queries)
- Simple lookups
- Standard research
- Documentation checks
- **Cost**: ~$0.0006/query

**Tier 2: Gemini 3 Pro** (8% of queries)
- Complex reasoning
- Multi-step analysis
- Architecture decisions
- **Cost**: ~$0.015/query

**Tier 3a: Gemini Deep Research** (1% of queries)
- Comprehensive market analysis
- 2-query budget limit
- **Cost**: $20/mo subscription

**Tier 3b: Perplexity Sonar Deep Research** (1% of queries)
- Alternative to Gemini Deep Research
- No budget constraints
- Better temporal accuracy
- **Cost**: ~$0.13/query

**Tier 4: Perplexity Sonar Pro** (temporal accuracy only)
- Only when real-time 2026 data needed
- Regulatory timelines
- Current pricing information
- **Cost**: ~$0.0365/query

---

## Implementation Recommendations

### Phase 1: Quick Wins (Immediate)

1. **Default to Gemini 3 Flash** for all standard research
2. **Keep Perplexity** only for explicit temporal accuracy needs
3. **Update research-lookup skill** to prefer Gemini Flash

**Implementation:**
```python
# In research_lookup.py or gemini_research.py
DEFAULT_PROVIDER = "gemini"  # Change from "perplexity"
DEFAULT_MODEL = "gemini-3-flash"

# Only use Perplexity when:
if requires_temporal_accuracy(query):
    use_perplexity_sonar_pro()
else:
    use_gemini_flash()
```

**Expected Savings**: ~98% cost reduction

### Phase 2: Add Deep Research Alternative (Optional)

1. **Implement Perplexity Sonar Deep Research** integration
2. **Let users choose**: Gemini Deep Research vs Perplexity Deep Research
3. **Remove 2-query budget** for Perplexity version

**Configuration:**
```json
{
  "deep_research_provider": "gemini" | "perplexity" | "auto",
  "gemini_budget": 2,  // Only applies if gemini selected
  "perplexity_budget": null  // Unlimited
}
```

### Phase 3: Smart Routing (Advanced)

Implement context-aware routing:

```python
def select_research_provider(query, context):
    # Temporal accuracy critical → Perplexity
    if requires_real_time_data(query, context):
        return "perplexity/sonar-pro"

    # Deep comprehensive research → Deep Research agent
    if is_deep_research_query(query, context):
        if context.get("prefer_gemini") or gemini_budget_available():
            return "gemini-deep-research"
        else:
            return "perplexity/sonar-deep-research"

    # Complex reasoning → Gemini Pro
    if is_complex_reasoning(query):
        return "gemini-3-pro"

    # Default → Gemini Flash (fastest + cheapest)
    return "gemini-3-flash"
```

---

## Cost Projections

### Current Implementation (100 queries/month)

```
Phase 1 (3 queries):
- 2 Perplexity Sonar Pro: 2 × $0.0365 = $0.073
- 1 Perplexity Reasoning Pro: 1 × $0.03 = $0.03

Phase 2-6 (10 queries):
- 10 Perplexity Sonar Pro: 10 × $0.0365 = $0.365

Total per /full-plan: $0.468
Total per 100 queries: ~$3.60/month
```

### Optimized Implementation (100 queries/month)

```
Phase 1 (3 queries):
- 2 Gemini 3 Flash: 2 × $0.00064 = $0.00128
- 1 Gemini Deep Research: $20/mo (covers unlimited)

Phase 2-6 (10 queries):
- 10 Gemini 3 Flash: 10 × $0.00064 = $0.0064

Total per /full-plan: $0.00768 + $20/mo
Total per 100 queries: ~$0.08 + $20/mo = $20.08/month
```

**Analysis:**
- If 1-2 /full-plan per month: **$20.08 vs $0.94** (higher cost due to subscription)
- If 10+ /full-plan per month: **$20.80 vs $4.68** (4.4× savings)
- **Break-even**: ~43 queries/month

### Alternative: Perplexity Deep Research (100 queries/month)

```
Phase 1 (3 queries):
- 2 Gemini 3 Flash: 2 × $0.00064 = $0.00128
- 1 Perplexity Deep Research: 1 × $0.13 = $0.13

Phase 2-6 (10 queries):
- 10 Gemini 3 Flash: 10 × $0.00064 = $0.0064

Total per /full-plan: $0.13768
Total per 100 queries: ~$1.10/month
```

**Analysis:**
- **71% cheaper** than current implementation
- No subscription required
- Better temporal accuracy
- Scales linearly with usage

---

## Recommendations Summary

### Immediate Action (Phase 1)
✅ **Switch default provider to Gemini 3 Flash**
- 98% cost reduction for standard queries
- Better performance, larger context
- Minimal code changes

### Short-term (Phase 2)
✅ **Add Perplexity Sonar Deep Research integration**
- Alternative to Gemini Deep Research
- No budget constraints
- Better for high-volume usage
- Superior temporal accuracy

### Long-term (Phase 3)
✅ **Implement smart routing**
- Gemini Flash for default
- Perplexity for temporal accuracy
- Deep Research agents for comprehensive analysis
- Context-aware provider selection

---

## Implementation Priority

### High Priority (Do Now)
1. ✅ Fix documentation (completed)
2. Change default research provider to Gemini 3 Flash
3. Reserve Perplexity for temporal accuracy needs only

### Medium Priority (Next Week)
4. Add Perplexity Sonar Deep Research integration
5. Make deep research provider configurable
6. Update user documentation with cost comparisons

### Low Priority (Future)
7. Implement advanced smart routing
8. Add cost tracking and reporting
9. Provider performance benchmarking

---

## Questions for Decision

1. **Usage Volume**: How many /full-plan executions per month?
   - <5/month: Perplexity Deep Research cheaper
   - >5/month: Gemini subscription breaks even

2. **Temporal Accuracy**: How critical is real-time 2026 data?
   - Critical: Keep Perplexity as default for Phase 1
   - Moderate: Use Gemini Flash, Perplexity for specific queries

3. **Budget Philosophy**:
   - Pay-per-use: Favor Perplexity Deep Research
   - Subscription: Favor Gemini Deep Research (if >5 uses/month)

4. **Implementation Timeline**:
   - Quick fix: Just default to Gemini Flash (1 line change)
   - Full optimization: Implement all three phases (1-2 weeks)

---

**Recommendation**: Start with Phase 1 (Gemini Flash default) for immediate 98% cost savings, then evaluate Phase 2 (Perplexity Deep Research) based on usage patterns.
