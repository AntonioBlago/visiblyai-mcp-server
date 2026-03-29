---
description: "Comprehensive full-site SEO audit: sitemap crawl, PageSpeed, structured data, hreflang, competitor analysis, keyword gaps, and prioritized roadmap"
---

# /full-seo-audit

Run a comprehensive SEO audit covering technical SEO, content, performance, structured data, internationalization, rankings, competitors, and backlinks. Full sitemap crawl with prioritized P1/P2/P3 action plan and 30-60-90 day roadmap.

## Arguments

The user provides:
- Domain (e.g., `example.com`)
- Optionally: target market (default: Germany), target keyword, business type (B2B/eCommerce/SaaS)

## Credit Estimate

~300-500 credits depending on site size. Minimum balance: 400 credits.

## Steps

### Phase 1: Setup & Inventory (20 credits)

1. **Verify credits** — Call `get_account_info`. Need ~400 credits minimum. Warn if insufficient.

2. **Sitemap audit** — Call `audit_sitemap(domain)`. Get:
   - Total URL count, duplicate entries, broken URLs, lastmod coverage
   - Site structure overview (page types, depth)
   - Flag: sites with >50% non-200 sitemap URLs = critical

### Phase 2: Technical Crawl (60-300 credits)

3. **Crawl representative pages** — Call `crawl_website` on key pages:
   - Homepage (1 call)
   - 3-5 category/collection pages
   - 3-5 product/article pages
   - Extract per page: title, meta description, H1, word count, internal links, images, alt texts
   - For sites <500 URLs: crawl up to 50 pages (5 calls x 10 pages)
   - For sites >500 URLs: crawl homepage + 9 representative pages (1 call)

4. **Orphan page detection** — Compare sitemap URLs against internal links found during crawl:
   - Pages in sitemap but never linked from any crawled page = potential orphans
   - Flag pages with 0 incoming internal links

### Phase 3: Performance & Accessibility (25 credits)

5. **PageSpeed / Core Web Vitals** — Call `check_pagespeed` on 5 representative pages:
   - Homepage (mobile + desktop)
   - 1 category page (mobile)
   - 1 product/article page (mobile)
   - 1 additional page (mobile)
   - Collect: Performance score, Accessibility score, SEO score, LCP, CLS, TBT, FCP
   - Benchmark: Performance >90 = good, 50-90 = needs work, <50 = critical
   - Flag accessibility issues (contrast, touch targets, zoom blocking)

### Phase 4: Structured Data & Internationalization (25-60 credits)

6. **Structured data validation** — Call `check_structured_data` on 5 pages:
   - Homepage, 1 category, 1 product, 1 article, 1 other
   - Validate JSON-LD schemas: required fields, correct types
   - Check for: Organization, WebSite, BreadcrumbList, Product, Article, FAQPage
   - Provide corrected JSON-LD snippets for errors

7. **Hreflang audit** (skip if monolingual) — Call `check_hreflang` on 5 pages:
   - Check x-default present, language codes valid, all targets resolve
   - Validate bidirectional linking
   - Flag missing or broken hreflang annotations

### Phase 5: Content Audit (from crawl data)

8. **On-page content analysis** — Call `onpage_analysis` on 3 key pages (15 credits each = 45 credits):
   - Homepage + 1 high-traffic page + 1 underperforming page
   - 24-point check: title, meta, H1, content length, internal links, images, alt text
   - Flag: missing H1, duplicate titles, meta too long/short, thin content

9. **Content issues from crawl** — Aggregate from all crawled pages:
   - Pages with missing/empty title tags
   - Pages with missing/empty meta descriptions
   - Pages with missing/empty H1
   - Pages with thin content (<300 words)
   - Pages with missing alt text on images
   - Pages with missing Open Graph tags
   - Pages with missing Twitter Card tags

### Phase 6: Rankings & Traffic (20-40 credits)

10. **Keyword inventory** — Call `get_keywords(domain, limit=500)`. Then `classify_keywords` on top 100.
    - Ranking distribution: Top 3 / Page 1 / Page 2 / Weak / Not Ranking
    - Intent distribution: informational / commercial / transactional / navigational
    - Brand vs. Generic split
    - Funnel mapping (AIDA)

11. **GSC real data** (free) — Call `query_search_console(dimension="query", limit=500)` + `query_search_console(dimension="page", limit=100)`:
    - Top queries by clicks/impressions
    - Brand vs. Generic performance
    - CTR benchmarking against Keyword Study 2026
    - Quick wins: high impressions + low CTR

12. **GA4 data** (free) — Call `query_analytics(report_type="overview")` + `query_analytics(report_type="traffic_sources")`:
    - Organic traffic trend
    - Traffic source distribution
    - Revenue attribution (if eCommerce)

### Phase 7: Competitive Landscape (60 credits)

13. **Competitors** — Call `get_competitors(domain, limit=10)`:
    - DR, organic traffic, organic keywords per competitor
    - Identify direct vs. adjacent competitors

14. **Backlink profile** — Call `get_backlinks(domain)` + `get_referring_domains(domain)`:
    - DR score (0-100), total backlinks, referring domains
    - Dofollow vs. nofollow ratio
    - Top referring domains

### Phase 8: GEO Readiness (0 additional credits — uses existing data)

15. **AI visibility quick-check** — Using data already collected, call `seo_agent` with:
    ```
    task: "GEO-Readiness-Check for [domain]: Bewerte Citation Worthiness (Heading-Struktur, Standalone-Absätze, Schema-Coverage), AI-Crawler-Zugang (robots.txt: OAI-SearchBot, Google-Extended, PerplexityBot), und Grounding Page Existenz. Nutze die bereits gecrawlten Daten."
    agent: "consultant"
    domain: "[domain]"
    ```
    The backend agent system has built-in GEO knowledge (4 Stufen der AI-Sichtbarkeit, Citation Worthiness, Brand Visibility, Sentiment) and will generate GEO-aware recommendations automatically.

    Add the GEO findings as **Section 9** in the report output.

### Phase 9: Report Compilation

16. **Generate structured report** with these sections:

## Output Format

```markdown
# Full SEO Audit — [domain] — [date]

## Executive Summary
- 5 bullet points with the biggest findings
- Overall health assessment: Critical / Needs Work / Good / Excellent

## 1. Technical Health
| Check | Status | Details |
|-------|--------|---------|
| Sitemap | [ok/warning/error] | [total URLs, duplicates, broken] |
| Crawlability | [ok/warning/error] | [blocked URLs, redirect chains] |
| Orphan Pages | [count] | [pages with 0 internal links] |
| HTTPS | [ok/warning] | [mixed content issues] |
| Canonical Tags | [ok/warning] | [missing/conflicting] |

## 2. PageSpeed & Core Web Vitals
| Page | Perf | Access | SEO | LCP | CLS | TBT |
|------|------|--------|-----|-----|-----|-----|
| Homepage (mobile) | | | | | | |
| Category (mobile) | | | | | | |
| Product (mobile) | | | | | | |
- Accessibility issues: [list]
- Top optimization opportunities: [list]

## 3. Structured Data
| Page | Schemas Found | Valid | Errors |
|------|--------------|-------|--------|
- Missing recommended schemas: [list]
- Corrected JSON-LD snippets: [code blocks]

## 4. Internationalization (Hreflang)
| Issue | Count | Priority |
|-------|-------|----------|
| Missing x-default | | |
| Broken hreflang targets | | |
| Non-reciprocal links | | |

## 5. Content Health
| Issue | Count | Priority |
|-------|-------|----------|
| Missing title | [n] | P1 |
| Missing meta description | [n] | P1 |
| Missing H1 | [n] | P1 |
| Thin content (<300 words) | [n] | P2 |
| Missing alt text | [n] | P2 |
| Missing OG tags | [n] | P3 |

## 6. Rankings & Keywords
- Total keywords: [n] | Total search volume: [n]
- Ranking distribution table
- Intent distribution table
- Brand vs. Generic split
- Top 10 keywords by traffic
- Quick wins: [table with keyword, impressions, CTR, position, action]

## 7. Backlink Profile
| Metric | Value |
|--------|-------|
| Domain Rating | [0-100] |
| Total Backlinks | [n] |
| Referring Domains | [n] |
| Dofollow Ratio | [%] |

## 8. Competitor Benchmark
| Domain | DR | Traffic | Keywords | Gap |
|--------|----|---------|---------|----|

## 9. GEO Readiness (AI Visibility)
| Check | Status | Action |
|-------|--------|--------|
| Citation Worthiness | [score/assessment] | [action] |
| AI Crawler Access | [allowed/blocked] | [action] |
| Structured Data for AI | [coverage %] | [action] |
| Grounding Page | [exists/missing] | [action] |
| Informational CTR Trend | [stable/falling] | [AI Overview impact?] |

## 10. Priority Action Plan (P1/P2/P3)

**P1 — Sofort (Critical, week 1-2)**
- [List of critical issues with specific fixes]

**P2 — Kurzfristig (Important, week 2-4)**
- [List of important improvements]

**P3 — Laufend (Ongoing optimization)**
- [List of continuous improvement items]

## 10. 30-60-90 Day Roadmap

| Day | Milestone | Actions | Expected Impact |
|-----|-----------|---------|-----------------|
| 30 | Quick Wins Done | P1 fixes, title/meta optimization | +20-50% CTR |
| 60 | Technical Clean | Indexing fixes, speed optimization | +50-100% crawl efficiency |
| 90 | Content + Authority | Content gaps filled, link building started | +100-200% organic traffic |

## 11. KPI Framework

**KPQ 1:** "Are we visible for non-brand search terms?"
- KPI: Non-brand organic clicks/month
- KPI: Non-brand keywords on Page 1

**KPQ 2:** "Is our technical foundation solid?"
- KPI: Core Web Vitals pass rate
- KPI: Indexation rate (indexed/total)

**KPQ 3:** "Are we converting organic traffic?"
- KPI: Organic conversion rate
- KPI: Revenue per organic session
```

## CTR Model (Keyword Study 2026)

| Pos | Overall | Transactional | Commercial | Informational | Navigational |
|-----|---------|---------------|------------|---------------|--------------|
| 1 | 5.59% | 3.68% | 4.10% | 3.24% | 8.91% |
| 2 | 3.15% | 2.38% | 3.44% | 2.44% | 5.30% |
| 3 | 2.37% | 2.45% | 2.23% | 1.87% | 3.98% |
| 4 | 2.07% | 2.75% | 1.75% | 1.33% | 2.55% |
| 5 | 1.51% | 2.06% | 1.37% | 0.83% | 1.60% |
| 6-10 | 0.52-1.11% | | | | |

Source: [Keyword Study 2026](https://antonioblago.com/keyword-study-2026-organic-search-ctr)

## Quality Gates

- Minimum credits: 400 before starting
- If GSC/GA4 not connected: skip those steps, note in report
- If site is monolingual: skip hreflang audit
- Always include credit consumption summary at the end
- P1 issues must have specific, actionable fixes (not just "fix it")
- Structured data errors must include corrected JSON-LD code
- Traffic projections labeled as estimates, not guarantees
