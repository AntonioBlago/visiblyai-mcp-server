---
description: "Analyze keyword optimization potential: SERP analysis, GSC real data, close variant grouping, and actionable strategy"
---

# /keyword-optimization

Analyze a keyword's full optimization potential — SERP landscape, close variant performance, GSC real data, and a prioritized strategy to rank higher.

## Arguments

The user provides:
- Target keyword (e.g., "Ehering aus Gold")
- Domain (e.g., `example.com`) — to check current ranking
- Optionally: location (default: Germany), language (default: German)

## When to Use

Trigger on phrases like:
- "Optimierungspotenziale fuer [keyword]"
- "Wie ranke ich fuer [keyword]"
- "Optimize for [keyword]"
- "Keyword optimieren"
- "SERP check fuer [keyword]"
- "Wer rankt fuer [keyword]"
- "Ranking verbessern fuer [keyword]"

## Methodology

### The Close Variant Reality

Google groups close variants (singular/plural, word order, inflections) into one SERP. Optimizing for ONE variant benefits ALL variants. The workflow must:
1. Identify the variant group (via `validate_keywords`)
2. Find which variants the user already ranks for (via GSC)
3. Analyze the SERP to understand what Google rewards
4. Build a strategy that covers the entire variant group

### Data Source Priority

| Priority | Source | What it gives | Cost |
|----------|--------|---------------|------|
| 1 | **GSC** (`query_search_console`) | Real impressions, clicks, CTR, position per variant | Free |
| 2 | **SERP Check** (`check_serp`) | Live top 10 results, content types, competitor analysis | 15 credits |
| 3 | **Validate Keywords** (`validate_keywords`) | SV (grouped), CPC, competition for all variants | ~10 credits |
| 4 | **Crawl/Sitemap** (`crawl_website`) | Existing page content, word count, headings, internal links | 15 credits |
| 5 | **URL Structure** (`analyze_url_structure`) | URL pattern, sitemap detection, thematic structure | Free |
| 6 | **OnPage Analysis** (`onpage_analysis`) | 24-point SEO check of the target page | 15 credits |
| 7 | **Classify Keywords** (`classify_keywords`) | Intent + funnel stage | Free |

## Steps

1. **Validate keyword + discover variants** — Call `validate_keywords` with the target keyword. This returns the Google Ads grouped SV and all close variants.

   Note in the output: "SV comes from Google Ads (grouped close variants). For exact per-variant data, see GSC section below."

2. **Classify intent** — Call `classify_keywords` on the target keyword + top 5 variants. Determine:
   - Search intent (transactional / commercial / informational)
   - Funnel stage (AIDA)
   - This determines CTR benchmark and content type

3. **Check live SERP** — Call `check_serp` for the target keyword. Analyze:
   - **Who ranks?** List top 10 with domain, title, URL
   - **Content type distribution**: How many are product pages vs. blog posts vs. category pages vs. glossary?
   - **Domain authority pattern**: Are top results big brands or niche sites?
   - **Content depth indicator**: Titles that suggest long-form vs. short-form content
   - **Your position**: Is the user's domain in the top 10/20? If not, note "Not in top {depth}"
   - **SERP intent signal**: What does Google think the user wants? (based on what types of pages rank)

4. **GSC real data** (if available) — Call `get_google_connections` first. If GSC connected:
   - `query_search_console(dimension="query", limit=500)` — filter results for the keyword and all close variants
   - For each variant found: show clicks, impressions, CTR, avg position
   - Calculate: total impressions across all variants = "real search demand"
   - Flag variants with high impressions but low CTR (title/meta optimization needed)
   - Flag variants on positions 4-15 (push-to-page-1 candidates)

5. **Find the right target page** — This is CRITICAL. Do NOT just crawl the homepage. Find the specific page that should rank for this keyword:

   **Method A: GSC page data (best)**
   - If GSC connected: `query_search_console(dimension="page", limit=100)` — filter for pages that already get impressions for the keyword variants
   - The URL with the most impressions for this keyword cluster = the current target page

   **Method B: Sitemap scan**
   - Call `audit_sitemap(domain)` — get all URLs from the sitemap
   - Search the URL list for pages containing the keyword in the URL path (e.g., `/eheringe-gold/`, `/gold-eheringe/`, `/eheringe/gold/`)
   - Also look for category pages or product listing pages that match the topic

   **Method C: Site search via crawl**
   - Call `crawl_website(f"https://{domain}/", keyword, max_pages=10)` — crawl the homepage and follow internal links
   - From the crawl results, find pages where the title, H1, or content mentions the keyword

   **Method D: Ask the user**
   - If none of the above methods find a relevant page, ASK the user:
     "Ich konnte keine spezifische Seite fuer '[keyword]' auf [domain] finden. Hast du bereits eine Seite dafuer? Wenn ja, welche URL? Wenn nein, empfehle ich eine neue Seite unter /[slug]/ zu erstellen."

   **IMPORTANT:** Never default to the homepage. The target page must be the most relevant page for the keyword. If no page exists, explicitly recommend creating one with a suggested URL structure.

6. **OnPage analysis of target page** — Run `onpage_analysis(target_url, keyword)` on the page found in step 5:
   - Get 24-point SEO score
   - Identify specific gaps (missing keyword in title/H1/meta, thin content, no internal links, etc.)
   - Compare word count and content depth against SERP top 3 competitors (from step 3)
   - If the page scores <50/100, highlight this as a P1 priority fix

7. **Compile strategy** — Based on all data, generate a prioritized action plan:

### Strategy Framework

**Tier 1 — Quick Wins (1-2 weeks, low effort)**
- Title tag optimization (include primary keyword variant + power words)
- Meta description rewrite (include CTA, match search intent)
- H1 alignment (must contain target keyword)
- Internal linking: add 3-5 links from high-traffic pages

**Tier 2 — Content Optimization (2-4 weeks, medium effort)**
- Content expansion: match or exceed top competitor word count
- Add FAQ section targeting long-tail variants
- Semantic keyword integration (related terms from SERP analysis)
- Add structured data (FAQ schema, Product schema, etc.)

**Tier 3 — Authority Building (1-3 months, high effort)**
- Create supporting content cluster (2-3 related articles linking to main page)
- Earn backlinks via content marketing or digital PR
- Build topical authority in the keyword's category

**Tier 4 — GEO Optimization (if informational keyword with falling CTR)**
- AI Overviews reduce informational CTR by up to 44.6% at position #1
- Optimize content for citation worthiness: clear headings, standalone paragraphs, direct Q&A format
- Add FAQ schema and structured data for AI extraction
- For brand keywords: ensure Grounding Page exists at /facts/[brand]/
- Note: the backend `seo_agent` (consultant) has built-in GEO knowledge — use it for deeper GEO analysis

## Output Format

```markdown
# Keyword Optimization Report — "[keyword]"

## 1. Keyword Overview
| Metric | Value |
|--------|-------|
| Target Keyword | [keyword] |
| Grouped SV (Google Ads) | [SV] |
| Close Variants | [count] variants in group |
| Search Intent | [intent] |
| Funnel Stage | [stage] |
| CPC | [cpc] EUR |
| Competition | [level] |

**Note:** SV is Google Ads grouped volume (all close variants combined).
For exact per-variant volumes, connect Google Search Console.

## 2. SERP Landscape — Top 10
| # | Domain | Title | Content Type |
|---|--------|-------|-------------|
| 1 | ... | ... | Product / Blog / Category |

**SERP Signals:**
- Dominant content type: [type]
- Domain authority pattern: [brands vs niche]
- Your position: [pos or "not ranking"]

## 3. Close Variant Performance (GSC)
| Variant | Impressions | Clicks | CTR | Position | Status |
|---------|------------|--------|-----|----------|--------|
| ehering gold | 5,200 | 120 | 2.3% | 8.2 | Push candidate |
| eheringe gold | 3,100 | 45 | 1.5% | 12.1 | Page 2 - needs push |
| ehering aus gold | 200 | 3 | 1.5% | 18.4 | Weak |

**Total real demand:** [sum impressions] impressions/month across all variants

## 4. Existing Page Analysis
| Metric | Value |
|--------|-------|
| Ranking URL | [url or "No page found"] |
| Word count | [count] |
| Title | [current title] |
| H1 | [current H1] |
| Internal links | [count] |
| Content gap vs. top 3 | [word count diff, missing topics] |

## 5. On-Page Score
- Overall: [score]/100
- [Top 3 gaps with specific fixes]

## 5. Strategy — Prioritized Actions
| Priority | Action | Expected Impact | Effort | Timeline |
|----------|--------|-----------------|--------|----------|
| 1 | Rewrite title: "[suggestion]" | +30-50% CTR | Low | 1 day |
| 2 | Expand content to [X] words | +2-5 positions | Medium | 1 week |
| 3 | Add [X] internal links | +1-3 positions | Low | 1 day |
| 4 | Create FAQ section | Long-tail coverage | Medium | 2 days |
| 5 | Build 2 supporting articles | Topical authority | High | 2-4 weeks |

## 6. Traffic Projection
| Timeframe | Est. Position | Est. CTR | Est. Monthly Clicks |
|-----------|--------------|----------|-------------------|
| Current | [pos] | [ctr]% | [clicks] |
| +3 months | [target] | [ctr]% | [clicks] |
| +6 months | [target] | [ctr]% | [clicks] |
| +12 months | [target] | [ctr]% | [clicks] |

Use intent-specific CTR from Keyword Study 2026.
```

## CTR Model (Keyword Study 2026)

| Pos | Overall | Transactional | Commercial | Informational | Navigational |
|-----|---------|---------------|------------|---------------|--------------|
| 1 | 5.59% | 3.68% | 4.10% | 3.24% | 8.91% |
| 2 | 3.15% | 2.38% | 3.44% | 2.44% | 5.30% |
| 3 | 2.37% | 2.45% | 2.23% | 1.87% | 3.98% |
| 4 | 2.07% | 2.75% | 1.75% | 1.33% | 2.55% |
| 5 | 1.51% | 2.06% | 1.37% | 0.83% | 1.60% |
| 6-10 | 0.52-1.11% | 0.65-1.45% | 0.51-1.07% | 0.20-0.59% | 0.52-1.09% |

Source: [Keyword Study 2026](https://antonioblago.com/keyword-study-2026-organic-search-ctr)

## Quality Gates

- Total credits: ~55-70 (validate: ~10, SERP: 15, crawl: 15, onpage: 15, classify: 0, GSC: 0, URL structure: 0)
- If GSC not connected: skip step 4, note "Connect GSC for real performance data"
- If onpage URL unknown: skip step 5
- Always show SV source disclaimer (Google Ads grouped vs GSC real)
- SERP results are a snapshot — note the date
- Traffic projections are estimates — label as conservative/realistic
