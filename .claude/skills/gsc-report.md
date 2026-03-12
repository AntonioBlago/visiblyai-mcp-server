---
description: "Google Search Console performance report with quick wins"
---

# /gsc-report

Generate a GSC performance report identifying top queries, pages, and quick-win opportunities.

## Arguments

The user provides a domain or GSC property. Optionally a time period (default: 28 days).

## Methodology

Based on Antonio Blago's GSC analysis approach — the first thing an SEO expert does on any new project:

### How to Read GSC Data Correctly
- **Always look at metrics in relation, never in isolation.** High impressions + low clicks = poor CTR (title/meta needs work). High clicks + low impressions = niche keyword doing well.
- **Average position context**: When you rank for very few keywords (10-20), avg position isn't meaningful yet. As you grow to 500-1000+ keywords, it naturally settles around 20-30 average — this is normal.
- **Impression vs Click**: An impression counts when your page appears in search results. A click only counts when the user stays on the page long enough with satisfactory engagement signals — it's not just a click-and-bounce.
- **Traffic trends**: Sideways traffic = not alarming but investigate. Declining = action needed. Rising but position dropping = you rank for more keywords now (dilution effect, often temporary).

### Indexing — The Invisible Killer
- Without indexing, pages CANNOT appear in search results. Period.
- Check the green (indexed) vs grey (not indexed) ratio.
- Many non-indexed pages with few indexed = alarming, immediate action needed.
- Common non-indexing reasons: redirects, canonical tags (Google may choose a different canonical), duplicates, noindex tags, robots.txt blocks.
- 404 errors should be monitored regularly but note Google sometimes reports false 404s.
- Sitemap must be submitted and successfully read.

### Core Web Vitals
- Green = acceptable, Yellow = needs improvement, Red = urgent (may impact crawling and cause user bounce).
- For e-commerce: also check product/merchant listings tab.

## Steps

1. **Verify connection** — Call `get_google_connections`. Confirm GSC is connected. If not, inform the user they need to connect GSC first at visibly-ai.com.

2. **Top queries** — Call `query_search_console` with `dimension=query`, `limit=200`. Get clicks, impressions, CTR, position.

3. **Top pages** — Call `query_search_console` with `dimension=page`, `limit=50`.

4. **Device breakdown** — Call `query_search_console` with `dimension=device`.

5. **Classify queries** — Call `classify_keywords` on the top 100 queries. Map intent and funnel distribution (AIDA: Awareness > Interest > Decision > Action).

6. **Quick wins analysis** — Identify keywords with:
   - **Title/Meta optimization**: High impressions (>100) but low CTR (<5%) — the page shows up but doesn't attract clicks. Rewrite title and meta description.
   - **Push to page 1**: Position 4-20 with decent volume — close to visibility, needs content improvement or backlinks.
   - **Content expansion**: High CTR but low impressions — the content converts well but targets too narrow a query. Expand content to capture related keywords.
   - **Cannibalization risk**: Multiple pages ranking for the same query — consolidate content.

7. **Compile report** — Present:
   - Summary: total clicks, impressions, avg CTR, avg position
   - Context note: explain what avg position means for this keyword count
   - Top 20 queries by clicks (with CTR and position)
   - Top 10 pages by clicks
   - Device split (desktop/mobile/tablet)
   - Intent distribution of ranking queries
   - Funnel mapping: which AIDA stages are covered, which are gaps
   - Quick-win keyword table sorted by potential impact:
     | Keyword | Impressions | Clicks | CTR | Position | Action |
   - Indexing health summary (if data available from other tools)
   - Action items prioritized by effort vs. impact

## CTR Benchmarks (Keyword Study 2026)

Compare user's actual CTR against these benchmarks from the Keyword Study 2026 (1.3M keywords, 94 domains):

| Pos | Overall | Transactional | Commercial | Informational | Navigational |
|-----|---------|---------------|------------|---------------|--------------|
| 1 | 5.59% | 3.68% | 4.10% | 3.24% | 8.91% |
| 2 | 3.15% | 2.38% | 3.44% | 2.44% | 5.30% |
| 3 | 2.37% | 2.45% | 2.23% | 1.87% | 3.98% |
| 4 | 2.07% | 2.75% | 1.75% | 1.33% | 2.55% |
| 5 | 1.51% | 2.06% | 1.37% | 0.83% | 1.60% |
| 6-10 | 0.52-1.11% | 0.65-1.45% | 0.51-1.07% | 0.20-0.59% | 0.52-1.09% |

If a keyword's actual CTR is **below** the benchmark for its position and intent, flag it as a quick win for title/meta optimization. If **above**, the content is performing well.

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

- If GSC is not connected, stop and instruct the user to connect at visibly-ai.com.
- Credits: 0 (GSC tools are free). classify_keywords is also free.
- This skill costs 0 credits since it only uses GSC + classify_keywords (free).
- Always explain WHY a metric matters, not just WHAT it shows.

## Video References

Methodology based on Antonio Blago's SEO training:
- [Die 3 wichtigsten Checks in Google Search Console](https://www.youtube.com/watch?v=QmSkrS5rytE)
- [Google Search Console - Performance und Indexierung](https://www.youtube.com/watch?v=o5HGyXgGlhA)
- [Vorstellung visibly AI](https://www.youtube.com/watch?v=LENq2hDKswg)
