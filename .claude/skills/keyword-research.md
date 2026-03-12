---
description: "Comprehensive keyword research for a domain or topic"
---

# /keyword-research

Research and classify keywords with search volumes, intent, and funnel mapping.

## Arguments

The user provides a domain and/or topic keywords. Optionally a location (default: Germany).

## Methodology

Follow Antonio Blago's keyword research process — a cyclical, not linear workflow:

### The Keyword Research Cycle
1. **Theme research** — Start with 5-10 broad topic blocks relevant to the business (e.g., "Personal Training", "Rueckenschmerzen", "Fitness")
2. **Keyword discovery** — For each topic, find all relevant keywords from multiple sources: SEO tools, competitor analysis, Google Search Console, related searches
3. **SERP overlap grouping** — Group keywords by search intent similarity. If two keywords show similar search results (SERP overlap), they belong in the SAME article. Putting similar-intent keywords in separate articles causes keyword cannibalization — Google won't know which to rank.
4. **Intent classification** — Classify each group by search intent (informational, transactional, commercial, navigational)
5. **Content mapping** — Map keyword groups to content pieces (Content = Themes + Keywords)

### Key Filtering Criteria
- **For new/young sites**: Start with difficulty <=10 AND search volume >=100. This drastically reduces the keyword set to achievable targets.
- **For established sites**: Adjust difficulty threshold upward based on Domain Rating.
- **Always check**: difficulty-to-volume ratio (good balance = low difficulty + decent volume), search intent relevance, and CPC (indicates commercial value).

### Common Mistakes to Avoid
- Treating keyword research as a linear, one-time process (it's a cycle that continuously optimizes)
- Ignoring SERP overlap — creating multiple articles for same intent — cannibalization
- Targeting only high-volume keywords without considering difficulty
- Not grouping keywords by topic and intent before creating content

## Steps

1. **Existing rankings** — Call `get_keywords` with `limit=500` for the domain.

2. **Search volume validation** — Call `validate_keywords` on the found keywords (batch if >200).

3. **Classification** — Call `classify_keywords` on all keywords. Get intent, funnel stage, brand type, conversion score. Group by:
   - **Intent**: transactional, commercial, informational, navigational
   - **Funnel stage**: Awareness > Interest > Decision > Action (AIDA)
   - **Brand type**: brand, generic, competitor

4. **GSC real data** (if available) — Call `get_google_connections` to check. If GSC connected, call `query_search_console` with `dimension=query`, `limit=200` for real click/impression data.

5. **Topic clustering** — Group keywords by primary topic (SERP overlap principle). For each cluster, show:
   - Cluster name
   - Total search volume
   - Average position
   - Dominant intent
   - Funnel stage distribution
   - Recommended content type (blog post, landing page, product page, FAQ)

6. **Difficulty/Volume analysis** — For each keyword, show:
   - Difficulty vs. volume ratio
   - CPC (commercial value indicator)
   - Current position (if ranking)
   - Estimated clicks at target position (use intent-specific CTR from the model below)

7. **Compile report** — Present:
   - Total keywords found and total search volume
   - Keyword table sorted by opportunity (favorable difficulty/volume ratio + weak current position)
   - Topic clusters with aggregated metrics
   - Quick wins: keywords on page 2 (positions 11-20) with high volume
   - Content gaps: high-volume topics with no current rankings
   - SERP overlap warnings: keywords that should be on the same page
   - Keyword set recommendations by site maturity:
     - New sites: focus on difficulty <=10, volume >=100
     - Growing sites: expand to difficulty <=30
     - Established sites: target competitive terms
   - Priority action list with content type recommendations

## CTR Model (Keyword Study 2026)

Based on 1.3M keywords across 94 domains (real GSC data, Aug 2025 – Feb 2026). Use intent-specific CTR for traffic potential calculations:

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

**Key insights for keyword prioritization:**
- **Transactional** keywords have the highest CTR at positions 3-5 (2.45-2.75%) — best ROI for content optimization
- **Commercial** keywords lead at position 2 (3.44%) — strong for comparison/review content
- **Navigational** keywords dominate position 1 (8.91%) but drop sharply — brand building matters
- **Informational** keywords have the lowest CTR overall — volume must compensate

When calculating traffic potential per keyword, always match the CTR to the keyword's classified intent type, not the overall average.

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

- Cap at 500 keywords for the initial pull.
- If GSC is not connected, skip that step and note it.
- Always flag potential cannibalization risks (same-intent keywords on different pages).
- Show credits consumed.

## Video References

Methodology based on Antonio Blago's SEO training:
- [Keyword Recherche Einfuehrung](https://www.youtube.com/watch?v=WUTTxtJQKf4)
- [Keyword Recherche - Ein komplexes Thema mit vielen Fehlern](https://www.youtube.com/watch?v=VC4D-aC8boE)
- [Einfuehrung in die verschiedenen Keyword Arten](https://www.youtube.com/watch?v=99EmvOlHGdk)
- [Wettbewerbsanalyse fuer Keywords](https://www.youtube.com/watch?v=OzJdYOxVGuw)
