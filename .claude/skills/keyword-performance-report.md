---
description: "Generate a keyword performance report: ranking distribution, intent analysis, quick wins, cluster breakdown, and CTR benchmarking"
---

# /keyword-performance-report

Deep-dive keyword performance analysis — ranking distribution, intent/funnel mapping, CTR benchmarking against 2026 study data, cluster breakdown, and a prioritized action table.

## Arguments

The user provides:
- Domain or Visibly AI project (e.g., `example.com`)
- Optionally: keyword file (Excel/CSV with target keywords + SV + current positions)
- Optionally: country filter (e.g., `DE`, `AT`, `US`)
- Optionally: comparison period (default: last 28 days)

## Methodology

### Data Sources Priority

1. **GSC via `query_search_console`** — ground truth for clicks, impressions, CTR, position
2. **Tracked keywords via `get_keywords`** — positions from rank tracker
3. **Keyword file** (if provided) — target keyword list with SV from DataForSEO/Ahrefs
4. Cross-reference all three: map every keyword's search volume + position + GSC performance

### Keyword Segmentation

Classify every keyword into:

**By Type:**
- Brand (exact brand name / variants)
- Non-Brand Generic (category/problem keywords)
- Competitor (competitor brand names)
- Long-tail (3+ words, specific intent)

**By Ranking Bucket:**
| Bucket | Position Range | Description |
|--------|----------------|-------------|
| Top 3 | 1-3 | High visibility, max CTR |
| Page 1 | 4-10 | Visible, below fold |
| Page 2 | 11-20 | Near miss — push candidates |
| Weak | 21-100 | Low visibility |
| Not Ranking | >100 | No SERP presence |

**By Search Intent (via `classify_keywords`):**
- Informational: research / how-to / definition
- Commercial: comparison / best / review
- Transactional: buy / price / order / download
- Navigational: brand name / specific URL

**By Funnel Stage (AIDA):**
- Awareness (Informational)
- Interest (Commercial)
- Decision (Commercial, high intent)
- Action (Transactional)

### CTR Benchmarking

Compare actual GSC CTR against Keyword Study 2026 benchmarks:

| Pos | Overall | Transactional | Commercial | Informational | Navigational |
|-----|---------|---------------|------------|---------------|--------------|
| 1 | 5.59% | 3.68% | 4.10% | 3.24% | 8.91% |
| 2 | 3.15% | 2.38% | 3.44% | 2.44% | 5.30% |
| 3 | 2.37% | 2.45% | 2.23% | 1.87% | 3.98% |
| 4 | 2.07% | 2.75% | 1.75% | 1.33% | 2.55% |
| 5 | 1.51% | 2.06% | 1.37% | 0.83% | 1.60% |
| 6-10 | 0.52-1.11% | — | — | — | — |
| 11-20 | ~0.45% | — | — | — | — |

Source: [Keyword Study 2026](https://antonioblago.com/keyword-study-2026-organic-search-ctr) — 1.3M keywords, 94 domains

**Flag as underperforming** if: actual CTR < (benchmark CTR × 0.7) → title/meta optimization needed
**Flag as overperforming** if: actual CTR > (benchmark CTR × 1.3) → protect this page, expand its reach

### Cluster Analysis

Group keywords by topic cluster (manually or via keyword themes):
- Calculate aggregate SV, clicks, impressions, avg CTR per cluster
- Sort by delta potential (SV × avg target CTR - current clicks)
- Identify which clusters are strong vs. underdeveloped

### Cannibalization Detection

Flag keyword pairs where:
- 2+ different URLs rank for the same keyword
- The ranking URLs differ between GSC and rank tracker
- CTR is split between multiple pages (sum > expected for that position)

### Quick Wins Framework

Prioritize actions by impact × effort:

**Tier 1 — Title/Meta Fix (Effort: Low, Impact: High)**
- Position 5-15, Impressions > 200/28d, CTR < benchmark × 0.7
- Action: rewrite `<title>` + meta description + H1

**Tier 2 — Content Expansion (Effort: Medium, Impact: High)**
- Position 4-10, but only 1-2 related keywords ranking
- Competitors rank for 10+ related terms on same page
- Action: expand content with semantic keywords, add FAQ section

**Tier 3 — Internal Linking Boost (Effort: Low, Impact: Medium)**
- Position 11-20, page exists but few internal links
- Action: add 3-5 internal links from high-traffic pages

**Tier 4 — New Content Needed (Effort: High, Impact: High)**
- Not ranking (>100), SV > 500, no existing page addressing the topic
- Action: create dedicated landing page or blog post

## Steps

1. **Get live GSC data**
   ```
   query_search_console(dimension="query", limit=500, country="deu")
   query_search_console(dimension="page", limit=100)
   ```

2. **Get tracked keywords**
   ```
   get_keywords(domain=domain, limit=500)
   ```

3. **Classify all keywords**
   ```
   classify_keywords(keywords=[list of all unique keywords])
   ```

4. **Cross-reference with keyword file** (if provided):
   - Map file keywords → GSC data (clicks, impressions, CTR, avg_position)
   - Flag keywords in file but with 0 GSC impressions (not indexed or completely invisible)

5. **Calculate performance metrics per keyword:**
   - Performance score = (actual CTR / benchmark CTR for position) × 100
   - Gap = benchmark clicks - actual clicks (missed traffic per keyword)
   - Opportunity score = SV × max(0, benchmark_ctr_p5 - actual_ctr) × 0.5

6. **Cluster aggregation** — group by theme, sort by opportunity score

7. **Generate report** (see Output Format)

## Output Format

```markdown
# Keyword Performance Report — [domain] — [date]

## Executive Summary
- Total keywords analyzed: X (GSC) + Y (tracked) + Z (from file)
- Total organic clicks (28d): X
- Brand vs. Non-Brand split: X% / X%
- Avg. position (non-brand): X
- Quick wins identified: X

## 1. Ranking Distribution
| Bucket | Keywords | % of Total | Total SV | Current Clicks |
|--------|----------|------------|----------|----------------|
| Top 3 | | | | |
| Page 1 | | | | |
| Page 2 | | | | |
| Weak (21-100) | | | | |
| Not Ranking | | | | |

**Interpretation:** [auto-generated based on data — flag if >80% not ranking]

## 2. Intent Distribution
| Intent | Keywords | % | Clicks | Avg CTR |
|--------|----------|---|--------|---------|
| Informational | | | | |
| Commercial | | | | |
| Transactional | | | | |
| Navigational | | | | |

**Funnel gaps:** [which AIDA stages are missing coverage]

## 3. Top 20 Keywords by Clicks
| Keyword | Type | Clicks | Impressions | CTR | Pos | Benchmark CTR | Status |
|---------|------|--------|-------------|-----|-----|---------------|--------|

## 4. Cluster Breakdown (Top 10 by Opportunity)
| Cluster | KWs | Total SV | Current Clicks | Target Clicks | Delta |
|---------|-----|----------|----------------|---------------|-------|

## 5. Quick Wins Table
| Tier | Keyword | SV | Impr | CTR | Pos | Action |
|------|---------|----|----|-----|-----|--------|

## 6. Cannibalization Alerts
[List of keyword pairs with multiple ranking URLs]

## 7. Prioritized Action Plan
| Priority | Action | Keyword(s) | Expected Impact | Effort |
|----------|--------|------------|-----------------|--------|
| 1 | Title/Meta fix | ... | +X clicks/Mo | Low |
| 2 | Content expand | ... | +X clicks/Mo | Med |
```

## Excel Deliverable (Optional)

If user asks for Excel output:

**Sheet 1: All Keywords**
- Columns: Keyword, Type, Intent, Funnel, Position, SV, Clicks, Impressions, CTR, Benchmark CTR, Performance %, Gap, Opportunity Score
- Filter by bucket (frozen header, auto-filter)
- Conditional formatting: green (outperforming), orange (needs work), red (critical)

**Sheet 2: Cluster Summary**
- Aggregated view with charts

**Sheet 3: Quick Wins**
- Filtered action list sorted by priority

**Sheet 4: Methodology**
- Data sources, date ranges, CTR benchmark source

Reference Excel output: `<SEO_PROJECTS_DIR>/<client>/Reports/` — see `/ci-setup-guide` for path setup

## Quality Gates

- Never report potential without comparing against live GSC data
- Brand keywords must be separated before any CTR analysis (brand CTR is naturally higher)
- If GSC not connected: stop and instruct user to connect at visibly-ai.com
- Flag if avg position for tracked keywords differs > 5 positions from GSC avg position (data gap)
- Minimum: 100 keywords to make distribution analysis meaningful
- Credit estimate: ~20-30 credits (classify_keywords + get_keywords + GSC queries)
