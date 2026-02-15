# OpenRouter Web Grounding & Search Capabilities Research

**Date:** 2026-01-21
**Research Focus:** OpenRouter web search capabilities, Perplexity Sonar model access, pricing comparison
**Researcher:** Jesper Vang

---

## Executive Summary

OpenRouter provides comprehensive web grounding capabilities through:

1. **Universal Web Search Plugin** - Available for 400+ models via `:online` suffix or plugin configuration
2. **Dual Search Engines** - Native provider search (OpenAI, Anthropic, Perplexity, xAI) or Exa-powered search
3. **Perplexity Sonar Family** - Full access to all Sonar variants including exclusive Sonar Pro Search
4. **Transparent Pricing** - No markup on token costs, clear search fees, 5.5% platform fee on credit purchases

**Key Finding:** OpenRouter offers identical token pricing to direct Perplexity API but adds a 5.5% platform fee. Exclusive access to Sonar Pro Search makes OpenRouter the only option for advanced agentic research.

---

## 1. Web Search Architecture

### 1.1 Universal Plugin System

OpenRouter's web search works across **all 400+ models** through two integration methods:

**Method 1: Simple `:online` Suffix**
```json
{
  "model": "openai/gpt-5.2:online"
}
```

**Method 2: Explicit Plugin Configuration**
```json
{
  "model": "openai/gpt-5.2",
  "plugins": {
    "web": {
      "max_results": 5,
      "engine": "native",
      "search_prompt": "custom system message"
    }
  }
}
```

### 1.2 Dual-Engine Search System

| Engine Type | Providers | When Used | Cost |
|------------|-----------|-----------|------|
| **Native Search** | OpenAI, Anthropic, Perplexity, xAI | Auto-selected for supported providers | Provider-specific pricing |
| **Exa Search** | All other 400+ models | Fallback for non-native models | $4 per 1,000 search results |

**How It Works:**
- Native search: OpenRouter routes directly to provider's built-in search (lower latency, provider-optimized)
- Exa search: Hybrid keyword + embeddings-based search using LLM technology
- Automatic routing based on model selection
- Manual override available via `"engine": "native"` or `"engine": "exa"`

### 1.3 Search Results Integration

- Default: 5 search results per query (configurable via `max_results`)
- Results injected as system message before user prompt
- Automatic citation formatting with markdown links
- Search occurs on user query date by default

---

## 2. Perplexity Sonar Model Availability

### 2.1 Complete Sonar Family Access

OpenRouter hosts **13 Perplexity models** including all Sonar variants:

| Model | Context | Input | Output | Request Fee | Use Case |
|-------|---------|-------|--------|-------------|----------|
| **Sonar** | 127K | $1/M | $1/M | $5-12/1K (by context size) | Fast Q&A, speed-optimized |
| **Llama 3.1 Sonar** | 127K | $1/M | $1/M | $5-12/1K | Improved efficiency, latest variant |
| **Sonar Pro** | 200K | $3/M | $15/M | $6-14/1K | Advanced search, 2x citations |
| **Sonar Reasoning Pro** | 200K | $2/M | $8/M | $5-14/1K | Chain-of-thought reasoning + search |
| **Sonar Deep Research** | N/A | $2/M | $8/M | Special pricing* | Multi-step exhaustive research |
| **Sonar Pro Search** | 200K | $3/M | $15/M | $18/1K | **EXCLUSIVE** - Agentic multi-step |

*Deep Research pricing: $2/M input, $8/M output, $2/M citation tokens, $5/1K searches, $3/M reasoning tokens

### 2.2 Exclusive Model: Sonar Pro Search

**Only available through OpenRouter** - cannot be accessed via direct Perplexity API.

**Features:**
- Autonomous multi-step reasoning
- Plans and executes entire research workflows
- Uses tools to iteratively refine search strategy
- Most advanced agentic search system from Perplexity

**Pricing:**
- Token costs: $3/M input, $15/M output (same as Sonar Pro)
- Additional: $18 per 1,000 requests (reflects autonomous research complexity)

**Implication:** Organizations requiring Sonar Pro Search **must** use OpenRouter - no alternative exists.

---

## 3. Search Context Size Pricing

Perplexity models charge request fees based on search depth:

### 3.1 Standard Sonar & Sonar Reasoning

| Context Size | Sonar | Sonar Pro / Reasoning Pro | Data Retrieved |
|--------------|-------|---------------------------|----------------|
| **Low** | $5/1K | $6/1K | Minimal search info |
| **Medium** | $8/1K | $10/1K | Moderate search data |
| **High** | $12/1K | $14/1K | Extensive search info |

### 3.2 Cost Impact Example

**1 million queries at high context:**
- Sonar: $12,000 in request fees alone
- Sonar Pro: $14,000 in request fees alone
- Plus token costs

**Optimization:** Selecting "low" vs "high" context can reduce request fees by ~57% if quality permits.

---

## 4. Pricing Comparison: Direct Perplexity vs OpenRouter

### 4.1 Token Pricing (IDENTICAL)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| Sonar | $1 (both) | $1 (both) |
| Sonar Pro | $3 (both) | $15 (both) |
| Sonar Reasoning Pro | $2 (both) | $8 (both) |
| Sonar Deep Research | $2 (both) | $8 (both) |

**✅ Zero markup** - OpenRouter passes through provider pricing exactly.

### 4.2 Request Fees (IDENTICAL)

Search context fees are **identical** between direct and OpenRouter access.

Example: Sonar Pro at low context = $6/1K requests (both pathways)

### 4.3 Platform Fees (OpenRouter Only)

| Purchase Method | Fee | Minimum |
|-----------------|-----|---------|
| **Credit Card** | 5.5% | $0.80 |
| **Cryptocurrency** | 5% | None |

**Cost Impact:**
- $100 credit purchase → $5.50 platform fee
- $1,000 credit purchase → $55.00 platform fee
- $5,000 credit purchase → $275.00 platform fee

**Direct Perplexity:** No equivalent platform fee exists.

### 4.4 Total Cost Comparison Example

**Scenario:** 1 million Sonar Pro queries (low context)
- Token costs (500 input + 200 output per query): ~$600
- Request fees: $600
- **Total via Direct Perplexity:** $1,200
- **Total via OpenRouter:** $1,200 + 5.5% platform fee on credits ≈ $1,266

**The 5.5% platform fee is the only cost differential.**

### 4.5 Bring-Your-Own-Key (BYOK) Option

OpenRouter offers BYOK mode:
- First 1M requests/month: Free
- After 1M requests: 5% fee of equivalent OpenRouter usage cost
- Billing goes directly to Perplexity account

**When BYOK Makes Sense:**
- High-volume users (>1M requests/month)
- Organizations with existing Perplexity contracts
- Variable usage patterns where 5% post-1M may be less than 5.5% credit purchase fee

---

## 5. Non-Perplexity Web Search Options

### 5.1 Exa-Powered Search

**Available for:** All 400+ models on OpenRouter (when native not supported)

**Pricing:**
- $4 per 1,000 search results
- Default: 5 results per request = $0.02 per search
- Configurable: 3 results = $0.012 per search
- Configurable: 10 results = $0.04 per search

**How It Works:**
- Hybrid keyword + embeddings-based search
- LLM-powered semantic understanding
- Surfaces relevant results beyond exact keyword matches

**Use Cases:**
- Cost-optimized web search with smaller models
- Models without native search capabilities
- Experimentation across model families

### 5.2 OpenAI Native Search

**Models:** GPT-5, GPT-5.2, GPT-4o, GPT-4.1 variants

**Pricing:**
- $10 per 1,000 tool calls (standard web search)
- Search content tokens: Billed at model's input token rate
- For reasoning models: $10/1K calls + search tokens at model rates
- For non-reasoning models: Search content tokens are **free**

**Example:** GPT-5.2
- Token pricing: $0.60/M input, $2.40/M output
- Web search enabled: `gpt-5.2:online`
- Native search via OpenAI infrastructure

### 5.3 Anthropic Native Search

**Models:** Claude Opus 4.6, Claude Sonnet variants

**Pricing:**
- Context-size-based pricing (low/medium/high)
- Specific per-query costs not publicly disclosed
- Test billing required to understand exact costs

**Example:** Claude Opus 4.6
- Token pricing: $5/M input, $25/M output
- Web search: $10 per 1,000 calls
- Native search via Anthropic infrastructure

### 5.4 xAI Grok Models

**Special Feature:** X (Twitter) search integration alongside traditional web search

**Models:** Grok 4.1 Fast and variants

**Use Cases:**
- Real-time social media insights
- Breaking news from social platforms
- Customer support requiring social sentiment
- Deep research combining traditional web + social

---

## 6. Cost Optimization Strategies

### 6.1 When to Choose Direct Perplexity API

✅ **Direct API is better when:**
- Monthly API spend >$1,000 (5.5% platform fee becomes material)
- Production scale operations (thousands of requests/day)
- Single-provider focus (no need for multi-model switching)
- Data privacy requires zero intermediaries
- Team already managing multiple direct provider integrations

**Savings Example:**
- $5,000/month spend → Save $275/month in platform fees
- Annual savings: $3,300

### 6.2 When to Choose OpenRouter

✅ **OpenRouter is better when:**
- Experimentation phase (<$100/month spend, $5.50 platform fee negligible)
- Need access to multiple AI providers (OpenAI, Anthropic, Google, etc.)
- Require Sonar Pro Search (exclusive to OpenRouter)
- Unified API management preferred over multiple provider accounts
- Rapid model switching without code changes
- Prototyping and A/B testing across model families

**Convenience Value:**
- Single API key for 400+ models across 60+ providers
- OpenAI-compatible endpoints (minimal code changes)
- Consolidated billing dashboard
- Automatic failover and routing

### 6.3 Search Context Optimization

**Strategy:** Tune search context size based on quality requirements

| Context | Cost Savings | Quality Tradeoff |
|---------|--------------|------------------|
| Low → Medium | -33% request fees | Moderate data loss |
| Medium → High | -43% request fees | Significant data increase |
| Low → High | -57% request fees | Maximum data vs minimum |

**When to use Low Context:**
- Simple factual queries
- Cost-sensitive applications
- High-volume operations where quality permits

**When to use High Context:**
- Comprehensive research
- Complex market analysis
- Applications where search depth directly impacts output quality

### 6.4 Model Selection Within Sonar Family

| Model | Best For | Cost Profile |
|-------|----------|--------------|
| **Sonar** | Fast Q&A, high-volume simple queries | Lowest ($1/$1 tokens) |
| **Llama 3.1 Sonar** | Updated Sonar with efficiency improvements | Lowest ($1/$1 tokens) |
| **Sonar Pro** | Complex queries, 2x citations needed | 15x higher output costs |
| **Sonar Reasoning Pro** | Chain-of-thought reasoning required | Moderate ($2/$8 tokens) |
| **Sonar Deep Research** | Exhaustive multi-step projects | Higher but autonomous |
| **Sonar Pro Search** | Advanced agentic workflows | Highest ($18/1K requests) |

**Cost-Conscious Choice:** Start with base Sonar, upgrade only when quality demands it.

**Research-Intensive Choice:** Deep Research or Pro Search may reduce total query count through autonomous multi-search methodology.

---

## 7. Caching and Optimization Features

### 7.1 OpenRouter Prompt Caching

OpenRouter supports prompt caching for compatible models:
- Reduces redundant processing
- Lowers token costs for repeated context
- Automatic for supported models
- No additional configuration required

**Documentation:** https://openrouter.ai/docs/guides/features/prompt-caching

### 7.2 Exa Search Caching

Exa-powered searches include:
- 15-minute self-cleaning cache
- Faster responses for repeated queries
- Automatic cache management
- No developer action required

---

## 8. Data Privacy Considerations

### 8.1 OpenRouter Privacy Posture

**Default Settings:**
- Zero Data Retention (ZDR) by default
- Basic request metadata logged (timestamps, models, token counts)
- Prompt/completion logging disabled unless opted in
- Provider-level ZDR filtering available

**Enterprise Features:**
- SOC 2 and GDPR compliance (verify current status with sales)
- Data residency controls
- Account-level plugin defaults and admin controls
- Unified billing without sharing prompts with OpenRouter

### 8.2 Data Flow Comparison

| Access Method | Data Flow | Intermediaries |
|---------------|-----------|----------------|
| **Direct Perplexity** | User → Perplexity | 0 |
| **OpenRouter** | User → OpenRouter → Perplexity | 1 |
| **OpenRouter BYOK** | User → OpenRouter (routing only) → Perplexity | 1 (minimal) |

**Regulatory Impact:**
- HIPAA/PHI environments: May require direct access (no intermediary)
- Financial services: Evaluate OpenRouter's compliance documentation
- General commercial: OpenRouter's ZDR typically sufficient

---

## 9. Integration Methods

### 9.1 OpenAI SDK Compatibility

OpenRouter maintains OpenAI SDK compatibility:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_KEY"
)

# Enable web search with :online suffix
response = client.chat.completions.create(
    model="perplexity/sonar-pro:online",
    messages=[{"role": "user", "content": "What are the latest AI developments?"}]
)
```

### 9.2 Advanced Plugin Configuration

```python
response = client.chat.completions.create(
    model="perplexity/sonar-pro",
    messages=[{"role": "user", "content": "Research climate tech startups"}],
    extra_body={
        "plugins": {
            "web": {
                "max_results": 10,
                "engine": "native",
                "search_prompt": "Focus on peer-reviewed academic sources"
            }
        }
    }
)
```

### 9.3 Account-Level Plugin Defaults

**Via Dashboard:** Settings > Plugins
- Enable web search plugin globally
- Configure default parameters
- Prevent per-request overrides
- Enforce organizational policies

**Use Cases:**
- Ensure all queries use web search
- Standardize citation behavior
- Cost controls across teams
- Compliance requirements

---

## 10. Reasoning + Web Search Integration

### 10.1 Supported Models

Models with `reasoning` parameter support:
- Claude Opus 4.6
- OpenAI reasoning models
- Sonar Reasoning Pro
- Sonar Pro Search

### 10.2 How It Works

**Step-by-step:**
1. Model uses chain-of-thought reasoning to plan search strategy
2. Executes targeted web searches based on reasoning
3. Evaluates search result quality
4. Determines if additional searches needed
5. Synthesizes findings with reasoning exposed

**API Response:**
- `reasoning_details` array contains internal chain-of-thought
- Final `content` contains synthesized answer
- Citations included in markdown format

**Value:** Transparency and auditability of search strategy + reasoning process.

---

## 11. Enterprise Considerations

### 11.1 Enterprise Plan Features

**OpenRouter Enterprise:**
- Volume discounts and bulk credits
- 5M free BYOK requests/month (vs 1M on standard)
- Managed policy enforcement
- Provider data explorers for audit
- SSO/SAML authentication
- Contractual SLAs
- Dedicated rate limits
- Support SLA with shared Slack channel
- Invoicing options

**Pricing:** Custom based on volume, prepayment, annual commits

**Contact:** OpenRouter sales team for quotes

### 11.2 Perplexity Enterprise

**Direct Perplexity Enterprise:**
- Custom pricing for high-volume usage
- Guaranteed SLA commitments
- Priority support
- Custom agreements

**Comparison:**
- OpenRouter Enterprise: Access to 60+ providers + Perplexity
- Perplexity Enterprise: Single-provider focus, optimized for Sonar

---

## 12. Competitive Landscape

### 12.1 Perplexity Native Features (Direct API Only)

Features **not available** through OpenRouter:
- Perplexity's standard web interface
- Mobile apps
- Pro plan benefits (API credits, enhanced UI)

Features **available** through OpenRouter:
- All Sonar API models
- Same token/request pricing
- Exclusive Sonar Pro Search

### 12.2 Alternative Search-Enabled Providers

| Provider | Models | Search Method | Key Difference |
|----------|--------|---------------|----------------|
| **OpenAI** | GPT-5, GPT-4o | Native web search | Free search tokens for non-reasoning |
| **Anthropic** | Claude Opus 4.6 | Native web search | Context-size-based pricing |
| **xAI** | Grok 4.1 Fast | Native + X search | Social media integration |
| **Perplexity** | Sonar family | Purpose-built | Specialized for search synthesis |
| **OpenRouter + Exa** | All 400+ models | Exa-powered | Universal search layer |

### 12.3 RAG vs Native Search

**Custom RAG System:**
- Requires separate vector database
- Separate search infrastructure
- Index maintenance overhead
- Full control over sources and retrieval

**OpenRouter Native Search:**
- No infrastructure management
- Automatic search execution
- Provider-optimized retrieval
- Limited control over sources

**When to build RAG:** Proprietary data, specific domain knowledge, compliance requirements
**When to use native search:** Real-time web info, current events, general knowledge

---

## 13. Practical Recommendations

### 13.1 By Use Case

| Use Case | Recommended Approach | Model | Reasoning |
|----------|---------------------|-------|-----------|
| **Prototype/MVP** | OpenRouter | Sonar or Sonar Pro | Low platform fee, easy switching |
| **Production (<$1K/mo)** | OpenRouter | Sonar Pro | Convenience outweighs 5.5% fee |
| **Production (>$1K/mo)** | Direct Perplexity | Sonar Pro | Eliminate $55+/mo platform fees |
| **Multi-model app** | OpenRouter | Various | Unified API critical |
| **Advanced research** | OpenRouter (required) | Sonar Pro Search | Exclusive access |
| **Cost-optimized** | OpenRouter + Exa | Smaller models | $4/1K results vs native search |
| **Regulated industry** | Direct Perplexity | Any Sonar | Zero intermediaries |
| **Experimentation** | OpenRouter | Free tier first | Test before committing |

### 13.2 Migration Path

**Phase 1: Exploration (Week 1-2)**
- Start with OpenRouter free tier
- Test Sonar vs Sonar Pro vs base models + Exa search
- Measure latency, quality, cost per use case
- Platform fee negligible at this stage

**Phase 2: Production Trial (Month 1-3)**
- Move to OpenRouter paid tier
- Monitor monthly spend
- Optimize search context size
- Evaluate model selection

**Phase 3: Scale Decision (Month 3+)**
- If spend >$1K/month → Consider direct Perplexity integration
- If multi-provider → Stay on OpenRouter
- If Sonar Pro Search required → Stay on OpenRouter (exclusive)
- Calculate annual platform fee savings vs integration overhead

### 13.3 Cost Monitoring

**Track These Metrics:**
1. Token consumption (input/output split)
2. Request count per search context size
3. Platform fees as % of total spend
4. Model distribution (which Sonar variant used most)
5. Search results per query average

**Alert Thresholds:**
- Monthly spend approaching $1K (evaluate direct API)
- High-context request ratio >50% (consider optimization)
- Platform fees >$100/month (ROI check)

---

## 14. Key Takeaways

### ✅ What We Know

1. **Web Search Availability:** OpenRouter provides universal web search across 400+ models via Exa or native provider search
2. **Perplexity Access:** Full Sonar family available with identical token/request pricing to direct API
3. **Exclusive Model:** Sonar Pro Search only available through OpenRouter
4. **Platform Fee:** 5.5% on credit purchases (credit card) is the only cost differential
5. **BYOK Option:** 1M free requests/month, then 5% fee provides alternative for high-volume users
6. **Integration:** OpenAI-compatible SDK makes switching trivial

### 💡 Strategic Insights

1. **Break-even point:** ~$1,000/month spend where direct API saves $55/month in platform fees
2. **Convenience tax:** 5.5% platform fee is the price for unified multi-provider access
3. **Exclusive features:** Sonar Pro Search creates vendor lock-in to OpenRouter (no alternative)
4. **Search context tuning:** Can reduce request fees by 57% (low vs high context)
5. **Model selection:** 15x cost difference between Sonar and Sonar Pro output tokens

### ⚠️ Watch Out For

1. **Platform fees compound:** $5K/month spend = $275/month or $3,300/year in fees
2. **BYOK complexity:** 1M request threshold before savings materialize
3. **Privacy trade-off:** OpenRouter intermediation may not suit regulated industries
4. **Search context creep:** Default medium/high context increases costs quickly
5. **Model drift:** As spend grows, cost-optimal model selection changes

### 📊 When OpenRouter Wins

- Experimentation phase (low absolute cost)
- Multi-provider applications (unified API critical)
- Need for Sonar Pro Search (exclusive access)
- Rapid model A/B testing
- Teams avoiding multiple vendor relationships

### 📊 When Direct Perplexity Wins

- Production at scale (>$1K/month)
- Single-provider focus (Sonar family only)
- Regulated environments (no intermediary)
- Cost optimization priority
- Existing direct integration infrastructure

---

## 15. Additional Resources

### Official Documentation

- **OpenRouter Web Search:** https://openrouter.ai/docs/guides/features/plugins/web-search
- **OpenRouter Pricing:** https://openrouter.ai/pricing
- **OpenRouter Models Catalog:** https://openrouter.ai/models
- **Perplexity Pricing:** https://docs.perplexity.ai/getting-started/pricing
- **Perplexity Models:** https://docs.perplexity.ai/getting-started/models
- **OpenRouter FAQ:** https://openrouter.ai/docs/faq

### Integration Guides

- **OpenRouter Quickstart:** https://openrouter.ai/docs/quickstart
- **OpenRouter API Reference:** https://openrouter.ai/docs/api/reference
- **Web Search API (Responses Beta):** https://openrouter.ai/docs/api/reference/responses/web-search

### Comparison Tools

- **OpenRouter Model Comparison:** https://compare-openrouter-models.pages.dev
- **OpenRouter Pricing Calculator:** https://invertedstone.com/calculators/openrouter-pricing

---

## Appendix A: Pricing Tables

### A.1 Complete Perplexity Sonar Pricing Matrix

| Model | Context | Input (/M) | Output (/M) | Low Ctx | Med Ctx | High Ctx | Special Fees |
|-------|---------|-----------|-------------|---------|---------|----------|--------------|
| Sonar | 127K | $1 | $1 | $5/1K | $8/1K | $12/1K | - |
| Llama 3.1 Sonar | 127K | $1 | $1 | $5/1K | $8/1K | $12/1K | - |
| Sonar Pro | 200K | $3 | $15 | $6/1K | $10/1K | $14/1K | - |
| Sonar Reasoning Pro | 200K | $2 | $8 | $5/1K | $10/1K | $14/1K | - |
| Sonar Deep Research | - | $2 | $8 | - | - | - | $5/1K searches, $3/M reasoning, $2/M citation |
| Sonar Pro Search | 200K | $3 | $15 | - | - | - | $18/1K requests |

### A.2 OpenRouter Platform Fees

| Purchase Type | Fee | Minimum | Notes |
|---------------|-----|---------|-------|
| Credit Card | 5.5% | $0.80 | Standard |
| Cryptocurrency | 5% | None | Lower fee, no minimum |
| BYOK (first 1M/mo) | 0% | - | Free requests |
| BYOK (after 1M/mo) | 5% of usage | - | Applied to overage |
| Enterprise BYOK (first 5M/mo) | 0% | - | Higher free tier |

### A.3 Exa Search Pricing

| Results per Query | Cost per Request | Cost per 1K Requests |
|-------------------|------------------|----------------------|
| 1 result | $0.004 | $4.00 |
| 3 results | $0.012 | $12.00 |
| 5 results (default) | $0.020 | $20.00 |
| 10 results | $0.040 | $40.00 |

Formula: `cost = (results × $4) / 1000`

---

## Appendix B: Sample API Requests

### B.1 Basic Web Search (OpenRouter)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_KEY"
)

response = client.chat.completions.create(
    model="perplexity/sonar:online",
    messages=[
        {"role": "user", "content": "What are the latest AI breakthroughs in 2026?"}
    ]
)

print(response.choices[0].message.content)
```

### B.2 Advanced Plugin Configuration

```python
response = client.chat.completions.create(
    model="perplexity/sonar-pro",
    messages=[
        {"role": "user", "content": "Comprehensive market analysis of quantum computing startups"}
    ],
    extra_body={
        "plugins": {
            "web": {
                "max_results": 10,
                "engine": "native",
                "search_prompt": "Prioritize recent (2025-2026) news and financial reports"
            }
        }
    }
)
```

### B.3 Sonar Deep Research Example

```python
# Note: Deep Research may take 30-60 minutes for complex queries
response = client.chat.completions.create(
    model="perplexity/sonar-deep-research",
    messages=[
        {"role": "user", "content": "Analyze the competitive landscape of climate tech carbon capture solutions"}
    ]
)

# Response will include extensive citations and reasoning tokens
```

### B.4 Exa-Powered Search with Small Model

```python
# Use any model (even free ones) with web search
response = client.chat.completions.create(
    model="meta-llama/llama-3-8b:online",  # Small, cost-effective model
    messages=[
        {"role": "user", "content": "Latest news on fusion energy"}
    ]
)
```

---

## Appendix C: Cost Calculation Examples

### C.1 Example 1: Simple Q&A Application

**Specs:**
- 10,000 queries/day
- Average: 500 input tokens, 200 output tokens per query
- Model: Sonar (base)
- Search context: Low

**Monthly Cost:**
- Queries/month: 300,000
- Input tokens: 150M → $150
- Output tokens: 60M → $60
- Request fees (low context): 300 × $5 = $1,500
- **Total Direct Perplexity:** $1,710
- **Total OpenRouter:** $1,710 + 5.5% = ~$1,804
- **Platform fee cost:** $94/month or $1,128/year

**Recommendation:** At this scale, direct Perplexity API saves ~$1,128 annually.

### C.2 Example 2: Research Assistant

**Specs:**
- 1,000 queries/day
- Average: 2,000 input tokens, 1,500 output tokens per query
- Model: Sonar Pro
- Search context: High

**Monthly Cost:**
- Queries/month: 30,000
- Input tokens: 60M → $180
- Output tokens: 45M → $675
- Request fees (high context): 30 × $14 = $420
- **Total Direct Perplexity:** $1,275
- **Total OpenRouter:** $1,275 + 5.5% = ~$1,345
- **Platform fee cost:** $70/month or $840/year

**Recommendation:** At this scale, direct API saves ~$840 annually. However, if using Sonar Pro Search (exclusive), OpenRouter is required.

### C.3 Example 3: Prototype Application

**Specs:**
- 100 queries/day (testing phase)
- Average: 300 input tokens, 150 output tokens per query
- Model: Sonar
- Search context: Medium

**Monthly Cost:**
- Queries/month: 3,000
- Input tokens: 0.9M → $0.90
- Output tokens: 0.45M → $0.45
- Request fees (medium context): 3 × $8 = $24
- **Total Direct Perplexity:** $25.35
- **Total OpenRouter:** $25.35 + 5.5% = ~$26.74
- **Platform fee cost:** $1.39/month or $16.68/year

**Recommendation:** At this scale, platform fee is negligible. OpenRouter's convenience (unified API, easy model switching) easily justifies $1.39/month overhead.

---

**End of Research Document**
