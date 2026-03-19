---
description: "Quick sample-based SEO audit: 100-page sample, PageSpeed, core technical checks, and top quick wins (~80-120 credits)"
---

# /quick-seo-audit

Fast SEO health check based on a sample of up to 100 pages. Covers the most impactful checks without a full site crawl. Ideal for initial assessment, client pitches, or monthly monitoring.

## Arguments

The user provides:
- Domain (e.g., `example.com`)
- Optionally: target keyword, focus area (technical/content/rankings)

## Credit Estimate

~80-120 credits. Minimum balance: 120 credits.

## Steps

### 1. Verify Credits (0 credits)
Call `get_account_info`. Need ~120 credits minimum.

### 2. Sitemap Inventory (20 credits)
Call `audit_sitemap(domain)`:
- Total URL count, duplicates, broken URLs
- Quick site size assessment

### 3. Sample Crawl (60 credits)
Call `crawl_website(url, max_pages=10)` on the homepage:
- Crawls homepage + up to 9 linked pages
- Extracts: title, meta, H1, word count, internal links, images
- Identifies: missing titles, missing H1, thin content, missing alt text

### 4. PageSpeed Check (15 credits)
Call `check_pagespeed` on 3 pages:
- Homepage (mobile)
- 1 category/listing page (mobile)
- 1 content/product page (mobile)
- Get: Performance, Accessibility, SEO scores + Core Web Vitals

### 5. Structured Data Spot Check (10 credits)
Call `check_structured_data` on 2 pages:
- Homepage
- 1 product/article page
- Validate JSON-LD schemas

### 6. GSC Data (0 credits)
If connected, call `query_search_console(dimension="query", limit=100)`:
- Top queries, CTR benchmarking
- Quick wins: high impressions + low CTR

### 7. Quick Keyword Check (10-20 credits)
Call `get_keywords(domain, limit=100)`:
- Ranking distribution overview
- Top keywords by traffic

### 8. Compile Quick Report

## Output Format

```markdown
# Quick SEO Audit — [domain] — [date]

## Health Score: [X/100]

Calculated from: PageSpeed (25%), Content Health (25%), Technical (25%), Rankings (25%)

## Top 5 Issues (Priority Order)

| # | Issue | Impact | Effort | Action |
|---|-------|--------|--------|--------|
| 1 | [issue] | High | Low | [specific fix] |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

## PageSpeed Summary
| Page | Performance | Accessibility | SEO | LCP | CLS |
|------|------------|---------------|-----|-----|-----|
| Homepage | | | | | |
| Category | | | | | |
| Content | | | | | |

## Content Issues (from sample)
| Issue | Count (in sample) | Estimated total |
|-------|--------------------|-----------------|
| Missing title | [n] | ~[n * total/sample] |
| Missing meta | [n] | |
| Missing H1 | [n] | |
| Thin content | [n] | |

## Sitemap Health
- Total URLs: [n]
- Duplicates: [n]
- Broken (non-200): [n]

## Ranking Snapshot
- Total keywords: [n]
- Page 1: [n] | Page 2: [n] | Weak: [n]
- Brand vs. Generic: [%] / [%]

## Quick Wins (Top 5)
| Keyword | Impressions | CTR | Position | Action |
|---------|------------|-----|----------|--------|

## Recommended Next Step
Based on this quick audit, the top priority is: [recommendation].
For a complete analysis, run @full-seo-audit.

---
Credits used: ~[X] | Time: ~2-3 minutes
```

## Quality Gates

- Max 120 credits consumed
- If GSC not connected: skip step 6, note recommendation to connect
- Always extrapolate sample findings to estimated total (e.g., "3 of 10 pages missing H1 = ~30% of site")
- Quick audit should complete in under 3 minutes
- Always recommend @full-seo-audit for comprehensive analysis
- Health score formula: average of 4 sub-scores, each 0-100
  - PageSpeed: average Performance score across checked pages
  - Content: 100 - (issues_found / pages_checked * 100)
  - Technical: based on sitemap health + crawl errors
  - Rankings: based on % of keywords on Page 1
