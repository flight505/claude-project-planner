# Research Lookup - Provider Details & Technical Configuration

## OpenRouter API Configuration

This skill integrates with OpenRouter (openrouter.ai) to access Perplexity's Sonar models:

**Model Specifications**:
- **Models**:
  - `perplexity/sonar-pro` (fast lookup, 200K context)
  - `perplexity/sonar-reasoning-pro` (deep analysis with DeepSeek R1, 128K context)
- **Search Mode**: Academic/scholarly mode (prioritizes peer-reviewed sources)
- **Search Context**: Always uses `high` search context for deeper, more comprehensive research results
- **Context Window**: 128-200K tokens depending on model
- **Capabilities**: Academic paper search, citation generation, scholarly analysis
- **Output**: Rich responses with citations and source links from academic databases
- **Pricing**: $2-3/1M input + $8-15/1M output + $5/1K searches

**API Requirements**:
- OpenRouter API key (set as `OPENROUTER_API_KEY` environment variable)
- Account with sufficient credits for research queries
- Proper attribution and citation of sources

**Python Dependencies** (for CLI usage):
If using the `research_lookup.py` script directly, install dependencies:
```bash
pip install requests
# Or install all plugin dependencies:
pip install -r requirements.txt
```

**Academic Mode Configuration**:
- System message configured to prioritize scholarly sources
- Search focused on peer-reviewed journals and academic publications
- Enhanced citation extraction for academic references
- Preference for recent academic literature (2020-2024)
- Direct access to academic databases and repositories

### Response Quality and Reliability

**Source Verification**: The skill prioritizes:
- Peer-reviewed academic papers and journals
- Reputable institutional sources (universities, government agencies, NGOs)
- Recent publications (within last 2-3 years preferred)
- High-impact journals and conferences
- Primary research over secondary sources

**Citation Standards**: All responses include:
- Complete bibliographic information
- DOI or stable URLs when available
- Access dates for web sources
- Clear attribution of direct quotes or data

---

## Performance and Cost Considerations

### Response Times

**Sonar Pro Search**:
- Typical response time: 5-15 seconds
- Best for rapid information gathering
- Suitable for batch queries

**Sonar Reasoning Pro**:
- Typical response time: 15-45 seconds
- Worth the wait for complex analytical queries
- Provides more thorough reasoning and synthesis

### Cost Optimization

**Automatic Selection Benefits**:
- Saves costs by using Sonar Pro Search for straightforward queries
- Reserves Sonar Reasoning Pro for queries that truly benefit from deeper analysis
- Optimizes the balance between cost and quality

**Manual Override Use Cases**:
- Force Sonar Pro Search when budget is constrained and speed is priority
- Force Sonar Reasoning Pro when working on critical research requiring maximum depth
- Use for specific sections of papers (e.g., Pro Search for methods, Reasoning for discussion)

**Best Practices**:
1. Trust the automatic selection for most use cases
2. Review query results - if Sonar Pro Search doesn't provide sufficient depth, rephrase with reasoning keywords
3. Use batch queries strategically - combine simple lookups to minimize total query count
4. For literature reviews, start with Sonar Pro Search for breadth, then use Sonar Reasoning Pro for synthesis

---

## Security and Ethical Considerations

**Responsible Use**:
- Verify all information against primary sources when possible
- Clearly attribute all data and quotes to original sources
- Avoid presenting AI-generated summaries as original research
- Respect copyright and licensing restrictions
- Use for research assistance, not to bypass paywalls or subscriptions

**Academic Integrity**:
- Always cite original sources, not the AI tool
- Use as a starting point for literature searches
- Follow institutional guidelines for AI tool usage
- Maintain transparency about research methods

---

## Complementary Tools

In addition to research-lookup, the project planner has access to **WebSearch** for:

- **Quick metadata verification**: Look up DOIs, publication years, journal names, volume/page numbers
- **Non-academic sources**: News, blogs, technical documentation, current events
- **General information**: Company info, product details, current statistics
- **Cross-referencing**: Verify citation details found through research-lookup

**When to use which tool:**
| Task | Tool |
|------|------|
| Find academic papers | research-lookup |
| Literature search | research-lookup |
| Deep analysis/comparison | research-lookup (Sonar Reasoning Pro) |
| Look up DOI/metadata | WebSearch |
| Verify publication year | WebSearch |
| Find journal volume/pages | WebSearch |
| Current events/news | WebSearch |
| Non-scholarly sources | WebSearch |
