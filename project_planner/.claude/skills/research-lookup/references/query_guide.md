# Research Lookup - Query Guide & Quality Standards

## Core Capabilities

### 1. Academic Research Queries

**Search Academic Literature**: Query for recent papers, studies, and reviews in specific domains:

```
Query Examples:
- "Recent advances in CRISPR gene editing 2024"
- "Latest clinical trials for Alzheimer's disease treatment"
- "Machine learning applications in drug discovery systematic review"
- "Climate change impacts on biodiversity meta-analysis"
```

**Expected Response Format**:
- Summary of key findings from recent literature
- Citation of 3-5 most relevant papers with authors, titles, journals, and years
- Key statistics or findings highlighted
- Identification of research gaps or controversies
- Links to full papers when available

### 2. Technical and Methodological Information

**Protocol and Method Lookups**: Find detailed procedures, specifications, and methodologies:

```
Query Examples:
- "Western blot protocol for protein detection"
- "RNA sequencing library preparation methods"
- "Statistical power analysis for clinical trials"
- "Machine learning model evaluation metrics"
```

**Expected Response Format**:
- Step-by-step procedures or protocols
- Required materials and equipment
- Critical parameters and considerations
- Troubleshooting common issues
- References to standard protocols or seminal papers

### 3. Statistical and Data Information

**Research Statistics**: Look up current statistics, survey results, and research data:

```
Query Examples:
- "Prevalence of diabetes in US population 2024"
- "Global renewable energy adoption statistics"
- "COVID-19 vaccination rates by country"
- "AI adoption in healthcare industry survey"
```

**Expected Response Format**:
- Current statistics with dates and sources
- Methodology of data collection
- Confidence intervals or margins of error when available
- Comparison with previous years or benchmarks
- Citations to original surveys or studies

### 4. Citation and Reference Assistance

**Citation Finding**: Locate the most influential, highly-cited papers from reputable authors and prestigious venues:

```
Query Examples:
- "Foundational papers on transformer architecture" (expect: Vaswani et al. 2017 in NeurIPS, 90,000+ citations)
- "Seminal works in quantum computing" (expect: papers from Nature, Science by leading researchers)
- "Key studies on climate change mitigation" (expect: IPCC-cited papers, Nature Climate Change)
- "Landmark trials in cancer immunotherapy" (expect: NEJM, Lancet trials with 1000+ citations)
```

**Expected Response Format**:
- 5-10 most influential papers, **ranked by impact and relevance**
- Complete citation information (authors, title, journal, year, DOI)
- **Citation count** for each paper (approximate if exact unavailable)
- **Venue tier** indication (Nature, Science, Cell = Tier 1, etc.)
- Brief description of each paper's contribution
- **Author credentials** when notable (e.g., "from the Hinton lab", "Nobel laureate")
- Journal impact factors when relevant

**Quality Criteria for Citation Selection**:
- Prefer papers with **100+ citations** (for papers 3+ years old)
- Prioritize **Tier-1 journals** (Nature, Science, Cell, NEJM, Lancet)
- Include work from **recognized leaders** in the field
- Balance **foundational papers** (high citations, older) with **recent advances** (emerging, high-impact venues)

---

## Paper Quality and Popularity Prioritization

**CRITICAL**: When searching for papers, ALWAYS prioritize high-quality, influential papers over obscure or low-impact publications. Quality matters more than quantity.

### Citation-Based Ranking

Prioritize papers based on citation count relative to their age:

| Paper Age | Citation Threshold | Classification |
|-----------|-------------------|----------------|
| 0-3 years | 20+ citations | Noteworthy |
| 0-3 years | 100+ citations | Highly Influential |
| 3-7 years | 100+ citations | Significant |
| 3-7 years | 500+ citations | Landmark Paper |
| 7+ years | 500+ citations | Seminal Work |
| 7+ years | 1000+ citations | Foundational |

**When reporting citations**: Always indicate approximate citation count when known (e.g., "cited 500+ times" or "highly cited").

### Venue Quality Tiers

Prioritize papers from higher-tier venues:

**Tier 1 - Premier Venues** (Always prefer):
- **General Science**: Nature, Science, Cell, PNAS
- **Medicine**: NEJM, Lancet, JAMA, BMJ
- **Field-Specific Flagships**: Nature Medicine, Nature Biotechnology, Nature Methods, Nature Genetics, Cell Stem Cell, Immunity
- **Top CS/AI**: NeurIPS, ICML, ICLR, ACL, CVPR (for ML/AI topics)

**Tier 2 - High-Impact Specialized** (Strong preference):
- Journals with Impact Factor > 10
- Top conferences in subfields (e.g., EMNLP, NAACL, ECCV, MICCAI)
- Society flagship journals (e.g., Blood, Circulation, Gastroenterology)

**Tier 3 - Respected Specialized** (Include when relevant):
- Journals with Impact Factor 5-10
- Established conferences in the field
- Well-indexed specialized journals

**Tier 4 - Other Peer-Reviewed** (Use sparingly):
- Lower-impact journals, only if directly relevant and no better source exists

### Author Reputation Indicators

Prefer papers from established, reputable researchers:

- **Senior authors with high h-index** (>40 in established fields)
- **Multiple publications in Tier-1 venues**
- **Leadership positions** at recognized research institutions
- **Recognized expertise**: Awards, editorial positions, society fellows
- **First/last author on landmark papers** in the field

### Direct Relevance Scoring

Always prioritize papers that directly address the research question:

1. **Primary Priority**: Papers directly addressing the exact research question
2. **Secondary Priority**: Papers with applicable methods, data, or conceptual frameworks
3. **Tertiary Priority**: Tangentially related papers (include ONLY if from Tier-1 venues or highly cited)

### Practical Application

When conducting research lookups:

1. **Start with the most influential papers** - Look for highly-cited, foundational work first
2. **Prioritize Tier-1 venues** - Nature, Science, Cell family journals, NEJM, Lancet for medical topics
3. **Check author credentials** - Prefer work from established research groups
4. **Balance recency with impact** - Recent highly-cited papers > older obscure papers > recent uncited papers
5. **Report quality indicators** - Include citation counts, journal names, and author affiliations in responses

**Example Quality-Focused Query Response**:
```
Key findings from high-impact literature:

1. Smith et al. (2023), Nature Medicine (IF: 82.9, cited 450+ times)
   - Senior author: Prof. John Smith, Harvard Medical School
   - Key finding: [finding]

2. Johnson & Lee (2024), Cell (IF: 64.5, cited 120+ times)
   - From the renowned Lee Lab at Stanford
   - Key finding: [finding]

3. Chen et al. (2022), NEJM (IF: 158.5, cited 890+ times)
   - Landmark clinical trial (N=5,000)
   - Key finding: [finding]
```

---

## Usage Examples

### Example 1: Simple Literature Search (Sonar Pro Search)

**Query**: "Recent advances in transformer attention mechanisms 2024"

**Model Selected**: Sonar Pro Search (straightforward lookup)

**Response Includes**:
- Summary of 5 key papers from 2024
- Complete citations with DOIs
- Key innovations and improvements
- Performance benchmarks
- Future research directions

### Example 2: Comparative Analysis (Sonar Reasoning Pro)

**Query**: "Compare and contrast the advantages and limitations of transformer-based models versus traditional RNNs for sequence modeling"

**Model Selected**: Sonar Reasoning Pro (complex analysis required)

**Response Includes**:
- Detailed comparison across multiple dimensions
- Analysis of architectural differences
- Trade-offs in computational efficiency vs performance
- Use case recommendations
- Synthesis of evidence from multiple studies
- Discussion of ongoing debates in the field

### Example 3: Method Verification (Sonar Pro Search)

**Query**: "Standard protocols for flow cytometry analysis"

**Model Selected**: Sonar Pro Search (protocol lookup)

**Response Includes**:
- Step-by-step protocol from recent review
- Required controls and calibrations
- Common pitfalls and troubleshooting
- Reference to definitive methodology paper
- Alternative approaches with pros/cons

### Example 4: Mechanism Explanation (Sonar Reasoning Pro)

**Query**: "Explain the underlying mechanism of how mRNA vaccines trigger immune responses and why they differ from traditional vaccines"

**Model Selected**: Sonar Reasoning Pro (requires causal reasoning)

**Response Includes**:
- Detailed mechanistic explanation
- Step-by-step biological processes
- Comparative analysis with traditional vaccines
- Molecular-level interactions
- Integration of immunology and pharmacology concepts
- Evidence from recent research

### Example 5: Statistical Data (Sonar Pro Search)

**Query**: "Global AI adoption in healthcare statistics 2024"

**Model Selected**: Sonar Pro Search (data lookup)

**Response Includes**:
- Current adoption rates by region
- Market size and growth projections
- Survey methodology and sample size
- Comparison with previous years
- Citations to market research reports
