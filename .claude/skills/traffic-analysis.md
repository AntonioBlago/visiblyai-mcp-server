---
description: "Analyze traffic trends and growth projections for a domain"
---

# /traffic-analysis

Analyze current traffic, historical trends, and project future growth.

## Arguments

The user provides a domain (e.g., `example.com`). Optionally a time range.

## Methodology

Based on Antonio Blago's traffic analysis and Neuro-SEO approach:

### Traffic as Business Value
- **SEA equivalent** is the most powerful metric for stakeholder communication. Calculate: "To generate this organic traffic via Google Ads, you'd need X/month." This makes SEO ROI tangible.
- Traffic cost shows the financial power behind organic rankings — even if a site looks small, high traffic cost means the keywords are commercially valuable.

### Pull Marketing Principle
SEO is pull marketing — users have active demand. Traffic potential calculation:
- Search volume x CTR at target position x conversion rate = potential leads/sales
- Conservative conversion rate: 2.5% (adjust by industry)
- Example: "Bleaching Duesseldorf" with 480 searches/month at Pos 1 (5.59% overall CTR) = ~27 clicks, at 2.5% conversion = ~1 lead/month. With navigational intent (8.91% CTR) or brand recognition, results improve significantly.

### Trend Interpretation
- **Ascending traffic + ascending keywords** = healthy growth, content strategy working
- **Ascending keywords but flat traffic** = ranking for more terms but not in top positions yet (common early stage)
- **Descending traffic** = action needed, check for algorithm updates, competitor gains, or content decay
- **Traffic concentration risk** = if >50% traffic comes from top 10 keywords, the site is fragile

### Traffic Architecture (Neuro-SEO)
Build traffic through a hub-and-spoke model:
- **Brand/offer page** (hub) — main conversion target
- **Local landing pages** (spokes) — e.g., "Personal Training Frankfurt/Koeln/Darmstadt"
- **Product landing pages** (spokes) — optimized for specific commercial keywords
- **Blog** (authority builder) — adds expertise, captures informational keywords, supports the hub pages

## Steps

1. **Current snapshot** — Call `get_traffic_snapshot`. Record organic/paid traffic baseline. Calculate and highlight the SEA equivalent value.

2. **Historical trends** — Call `get_historical_traffic` for the last 12 months. Identify growth/decline trajectory and inflection points.

3. **Top keywords** — Call `get_keywords` with `limit=100`. Identify which keywords drive the most traffic. Calculate traffic concentration (% from top 10 keywords).

4. **GA4 real data** (if available) — Call `get_google_connections`. If GA4 connected, call `query_analytics` with `report_type=overview` for real session/user data. Also call with `report_type=traffic_sources` for channel breakdown.

5. **Trend analysis** — Calculate:
   - Month-over-month growth rate
   - Trend direction (growing/stable/declining) with context explanation
   - Seasonal patterns (if 12+ months of data)
   - Traffic concentration risk (% from top 10 keywords — flag if >50%)
   - Keyword count trend vs traffic trend (are they aligned?)

6. **Traffic potential** — For top 20 keywords, calculate:
   - Current estimated clicks (position x CTR model)
   - Potential clicks at target position
   - Delta (opportunity)
   - Monetary value (delta clicks x average CPC = SEA equivalent of growth)

7. **Compile report** — Present:
   - Current traffic summary with SEA equivalent
   - 12-month trend with direction indicator and context
   - Top 10 traffic-driving keywords
   - Traffic concentration risk assessment
   - Channel breakdown (if GA4 available)
   - Traffic potential table (current vs. projected at target positions)
   - Revenue projection: potential additional leads/sales using CTR model + conversion rate
   - 3-month projection based on trend
   - Recommendations for traffic growth:
     - Quick wins (position improvements for existing keywords)
     - Content gaps (topics competitors cover but target doesn't)
     - Traffic architecture suggestions (local pages, product pages, blog)

## CTR Model (Keyword Study 2026)

Based on 1.3M keywords across 94 domains (real GSC data, Aug 2025 – Feb 2026):

| Pos | Overall | Transactional | Commercial | Informational | Navigational |
|-----|---------|---------------|------------|---------------|--------------|
| 1 | 5.59% | 3.68% | 4.10% | 3.24% | 8.91% |
| 2 | 3.15% | 2.38% | 3.44% | 2.44% | 5.30% |
| 3 | 2.37% | 2.45% | 2.23% | 1.87% | 3.98% |
| 4 | 2.07% | 2.75% | 1.75% | 1.33% | 2.55% |
| 5 | 1.51% | 2.06% | 1.37% | 0.83% | 1.60% |
| 6 | 1.11% | 1.45% | 1.07% | 0.59% | 1.09% |
| 7 | 0.87% | 1.08% | 0.85% | 0.51% | 0.88% |
| 8 | 0.61% | 0.83% | 0.71% | 0.20% | 0.84% |
| 9 | 0.58% | 0.73% | 0.59% | 0.25% | 0.66% |
| 10 | 0.52% | 0.65% | 0.51% | 0.27% | 0.52% |
| 11-15 | ~0.47% | ~0.50% | ~0.46% | ~0.41% | ~0.48% |
| 16-20 | ~0.45% | ~0.41% | ~0.45% | ~0.54% | ~0.50% |
| 20+ | <0.40% | | | | |

Use intent-specific CTR for more precise traffic projections (e.g., transactional keywords have higher CTR at positions 3-5 than other intents).

Source: [Keyword Study 2026](https://antonioblago.com/keyword-study-2026-organic-search-ctr)

### Niche CTR Benchmarks (FirstPageSage 2026)

Adjusted from FirstPageSage using the ratio between Keyword Study 2026 and FirstPageSage overall CTR:

| Niche | Pos 1 | Pos 2 | Pos 3 |
|-------|-------|-------|-------|
| **Overall Average** | 5.59% | 3.15% | 2.37% |
| B2B SaaS | 5.62% | 3.25% | 2.65% |
| eCommerce | 5.00% | 2.60% | 2.06% |
| Financial Services | 5.56% | 2.81% | 2.14% |
| Legal Services | 5.19% | 3.30% | 2.44% |
| Real Estate | 5.41% | 3.17% | 2.28% |
| HVAC / Local Services | 5.11% | 3.29% | 2.25% |
| IT & Managed Services | 5.80% | 3.46% | 2.49% |
| Manufacturing | 5.70% | 3.15% | 2.16% |
| Medical / Biotech | 5.96% | 3.08% | 2.75% |
| Higher Education | 5.29% | 3.22% | 2.35% |
| Software Development | 5.63% | 3.24% | 2.35% |
| Solar / Energy | 5.31% | 2.89% | 2.11% |

**Note**: Adjusted from FirstPageSage 2026 (clean SERPs) using our Keyword Study 2026 ratio. Use for niche comparisons only.

## Quality Gates

- If GA4 is not connected, use DataForSEO estimates and note the data source.
- Always include SEA equivalent to quantify organic traffic value.
- Show credits consumed.
- Frame growth recommendations in terms of business impact (leads, revenue), not just traffic numbers.

## Video References

Methodology based on Antonio Blago's SEO training:
- [Neuro SEO System - SEO und Verkaufspsychologie](https://www.youtube.com/watch?v=5rTDSvpH98s)
- [Vorstellung visibly AI](https://www.youtube.com/watch?v=LENq2hDKswg)
- [Wettbewerbsanalyse fuer Keywords](https://www.youtube.com/watch?v=OzJdYOxVGuw)
