---
description: "Run a full SEO audit on a domain using multiple VisiblyAI MCP tools"
---

# /seo-audit

Run a comprehensive SEO audit combining traffic, keywords, on-page, links, and backlinks into a structured report.

## Arguments

The user provides a domain (e.g., `example.com`) and optionally a target keyword.

## Methodology (Neuro-SEO System)

Follow Antonio Blago's 4-phase Neuro-SEO audit approach:

1. **Business understanding first** — Before diving into data, understand the business model, target audience, motives, and pain points. This prevents running in the wrong strategic direction.
2. **SEO audit + competitor analysis + keyword research** — Collect all data systematically.
3. **Strategy with sales psychology** — Map findings to the customer journey (AIDA: Awareness > Information > Evaluation > Purchase > Loyalty).
4. **Quick wins + monitoring** — Identify fast improvements, implement, and track results continuously.

### Key Principles
- Always look at metrics in relation to each other, not in isolation (e.g., high impressions + low CTR = title/meta optimization needed).
- SEO is pull marketing: users have active demand. Calculate potential using the CTR model from the Keyword Market Study (see below), with 2.5% avg conversion rate.
- Traffic cost = SEA equivalent. Show the monetary value of organic traffic (what it would cost as Google Ads).
- Content quality checklist: internal links (min 5), CTAs to offers, external links to authoritative sources (follow for reputable, nofollow for affiliate/commercial), table of contents, author bio, images with alt tags.

## Steps

1. **Verify credits** — Call `get_account_info` to check the balance is sufficient (~80 credits needed).

2. **Traffic baseline** — Call `get_traffic_snapshot` for the domain. Record organic traffic, paid traffic, keyword count. Calculate the SEA equivalent (traffic cost = what this organic traffic would cost as ads).

3. **Keyword inventory** — Call `get_keywords` with `limit=200`. Extract the top keyword by traffic share if user didn't specify one.

4. **Keyword classification** — Call `classify_keywords` on the found keywords. Summarize:
   - Intent distribution (transactional/commercial/informational/navigational)
   - Funnel stages mapped to AIDA (Awareness > Interest > Decision > Action)
   - Brand vs. generic keyword ratio

5. **On-page crawl** — Call `crawl_website` on the homepage with the top keyword. Check against the blog/page quality checklist:
   - Title tag with primary keyword, readable and engaging
   - Meta description optimized
   - Heading structure (H1-H3)
   - Internal linking (minimum 5 links to other pages)
   - External links with proper follow/nofollow attribution
   - Images with alt tags containing keywords
   - Paragraphs max 2-3 sentences, use lists where possible
   - Word count adequate (>300)

6. **On-page analysis** — Call `onpage_analysis` on the main landing page with the target keyword. Report overall score, passed/failed checks, recommendations. Note: content score should be higher than competitors.

7. **Link health** — Call `check_links` on the homepage. Report total links, broken links, redirects.

8. **Backlink profile** — Call `get_backlinks`. Report Domain Rating, total backlinks, referring domains.

9. **GEO readiness check** — Call `seo_agent` with:
   ```
   task: "GEO-Quick-Check for [domain]: Citation Worthiness, AI-Crawler-Zugang (robots.txt), Schema-Coverage für KI, CTR-Trend bei informational Keywords."
   agent: "consultant"
   domain: "[domain]"
   ```
   The backend has built-in GEO knowledge and will return AI-visibility-aware recommendations.

10. **Compile report** — Present a structured markdown report with:
   - Executive summary (1-2 sentences)
   - Traffic overview table with SEA equivalent value
   - Keyword distribution by intent AND funnel stage (AIDA mapping)
   - On-page score and top 5 recommendations (referencing the content quality checklist)
   - Link health status
   - Backlink authority summary
   - Traffic potential calculation: for top keywords, show estimated clicks at target position using the CTR model below
   - Priority action items (top 5), starting with quick wins

## CTR Model (Keyword Study 2026)

Based on 1.3M keywords across 94 domains from the Keyword Study 2026 (real GSC data, Aug 2025 – Feb 2026). Use the **overall CTR** for general calculations, or intent-specific CTR for more precise projections:

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

**Key insight**: Transactional keywords have higher CTR at positions 3-5 than other intents — prioritize these for quick-win position improvements. Navigational keywords dominate at position 1 (8.91%) but drop sharply.

Source: [Keyword Study 2026](https://antonioblago.com/keyword-study-2026-organic-search-ctr)

### Niche CTR Benchmarks (FirstPageSage 2026)

For niche-specific projections, apply these Position 1 / 2 / 3 CTR benchmarks. Values are adjusted from FirstPageSage 2026 data using the relative ratio between our Keyword Study 2026 and FirstPageSage overall averages (Pos 1: 14.1%, Pos 2: 17.1%, Pos 3: 23.5%):

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

**Note**: These values are derived from FirstPageSage 2026 niche benchmarks, adjusted downward by the ratio between our Keyword Study 2026 (real GSC data with AI Overviews, SERP features) and FirstPageSage's overall averages (measured on clean SERPs). Use for **niche comparisons** — the overall CTR model above is more precise for traffic projections.

## Quality Gates

- If any tool returns an error, note it in the report section and continue with remaining tools.
- Do NOT abort the entire audit if one tool fails.
- Always show credits consumed at the end of the report.
- Frame recommendations in terms of business impact, not just technical fixes.

## Video References

Methodology based on Antonio Blago's SEO training:
- [Neuro SEO System - SEO und Verkaufspsychologie](https://www.youtube.com/watch?v=5rTDSvpH98s)
- [Aufbau des optimalen Blogartikels](https://www.youtube.com/watch?v=JIzm5OumLEI)
- [Vorstellung visibly AI](https://www.youtube.com/watch?v=LENq2hDKswg)
