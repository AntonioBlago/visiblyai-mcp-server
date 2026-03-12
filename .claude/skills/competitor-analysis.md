---
description: "Compare a domain against its SEO competitors"
---

# /competitor-analysis

Identify and compare competitors based on keyword overlap, traffic, and backlink authority.

## Arguments

The user provides a target domain (e.g., `example.com`) and optionally a location/language.

## Methodology

Follow Antonio Blago's competitor analysis workflow:

1. **Start from the target keyword** — Search the primary keyword the client wants to rank for. Identify who ranks in the top 3-5 positions. These are your real SEO competitors (not necessarily business competitors).
2. **Analyze each competitor's profile** — Check traffic, keyword count, traffic trend (ascending/descending), and traffic cost (SEA equivalent).
3. **Export and merge keyword lists** — Pull competitor keywords and merge with your own keyword research for a complete picture.
4. **Check ranking distribution** — Evaluate how keywords are distributed across positions:
   - Top 1-5: aim for at least 5% of all keywords here
   - Top 6-10: also aim for >5%
   - Positions 11-50: the majority will be here, that's normal
   - Positions 51-100: minimize these over time
5. **Backlink comparison** — Check referring domains and backlinks. Note the SEA equivalent (traffic cost) to show the financial power behind organic rankings.

### Key Insight
"Just because you produce more content and keywords doesn't automatically increase traffic proportionally. Focus on quality positions, not just volume." — Antonio Blago

## Steps

1. **Find competitors** — Call `get_competitors` with `limit=10`. Identify the top 5 by keyword overlap.

2. **Traffic comparison** — For the target domain and top 3 competitors, call `get_traffic_snapshot`. Build a comparison table including:
   - Organic traffic (monthly clicks)
   - Total ranked keywords
   - Traffic trend (ascending/descending/sideways)
   - Traffic cost (SEA equivalent — "to generate this traffic via Google Ads, you'd need X/month")

3. **Keyword comparison** — For the target and top 3 competitors, call `get_keywords` with `limit=100`. Cross-reference to find:
   - Shared keywords (both rank)
   - Keyword gaps (competitor ranks, target does not) — these are content opportunities
   - Unique strengths (target ranks, competitor does not)

4. **Authority comparison** — For the target and top 3 competitors, call `get_backlinks`. Compare Domain Rating, referring domains, total backlinks.

5. **Ranking distribution** — For each domain, analyze position distribution:
   - Top 1-5 positions: X% (benchmark: >=5%)
   - Top 6-10 positions: X% (benchmark: >=5%)
   - Positions 11-20: X%
   - Positions 21-50: X%
   - Positions 51-100: X%

6. **Keyword classification** — Call `classify_keywords` on all unique keywords found. Analyze which intents each competitor dominates (informational, transactional, commercial, navigational).

7. **Compile report** — Present:
   - Competitor overview table (domain, traffic, DR, keyword overlap, traffic cost/SEA equivalent)
   - Ranking distribution comparison (position buckets per domain)
   - Top 10 keyword gaps with search volume — prioritized by difficulty/volume ratio
   - Intent distribution comparison
   - Authority comparison chart
   - Strategic recommendations:
     - Which competitor's keyword strategy to emulate
     - Quick-win keywords (gaps with low difficulty, decent volume)
     - Content types competitors use that the target is missing
     - Backlink gap assessment

## CTR Model (Keyword Study 2026)

Use intent-specific CTR when calculating traffic potential for keyword gaps:

| Pos | Overall | Transactional | Commercial | Informational | Navigational |
|-----|---------|---------------|------------|---------------|--------------|
| 1 | 5.59% | 3.68% | 4.10% | 3.24% | 8.91% |
| 2 | 3.15% | 2.38% | 3.44% | 2.44% | 5.30% |
| 3 | 2.37% | 2.45% | 2.23% | 1.87% | 3.98% |
| 4 | 2.07% | 2.75% | 1.75% | 1.33% | 2.55% |
| 5 | 1.51% | 2.06% | 1.37% | 0.83% | 1.60% |
| 6-10 | 0.52-1.11% | 0.65-1.45% | 0.51-1.07% | 0.20-0.59% | 0.52-1.09% |
| 11-20 | ~0.45% | ~0.45% | ~0.46% | ~0.50% | ~0.48% |
| 20+ | <0.40% | | | | |

Source: [Keyword Study 2026](https://antonioblago.com/keyword-study-2026-organic-search-ctr) — 1.3M keywords, 94 domains

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

- Limit to top 3 competitors for detailed comparison (to manage credits).
- If a competitor's data fails, skip it and note in the report.
- Show total credits consumed.
- Always include the SEA equivalent to demonstrate the value of organic rankings.

## Video References

Methodology based on Antonio Blago's SEO training:
- [Wettbewerbsanalyse fuer Keywords](https://www.youtube.com/watch?v=OzJdYOxVGuw)
- [Neuro SEO System](https://www.youtube.com/watch?v=5rTDSvpH98s)
