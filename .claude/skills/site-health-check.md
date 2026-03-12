---
description: "Quick technical SEO health check for a website"
---

# /site-health-check

Run a quick technical health check combining crawl, link check, on-page analysis, and URL structure review.

## Arguments

The user provides a URL (e.g., `https://example.com`).

## Methodology

Based on Antonio Blago's first-steps SEO audit approach — what an SEO expert checks first on any new project:

### Priority Check Areas (in order)
1. **Performance data** — Traffic trends (sideways = not alarming but investigate, declining = action needed). Always look at clicks, impressions, CTR, and position in relation, not isolation.
2. **Indexing status** — The ratio of indexed to non-indexed pages is critical. Many grey (not indexed) pages vs few green (indexed) = alarming. Without indexing, pages cannot appear in search results at all.
3. **Core Web Vitals** — Green = fast enough, Yellow = needs improvement, Red = immediate action (Google may not crawl properly, users bounce).

### Content Quality Checklist (per page)
- Internal links: minimum 5 other pages/articles linked
- CTAs to offers/contact page
- External links: follow for reputable sources (scientific, authoritative), nofollow for affiliate/commercial
- Table of contents for longer articles
- Author bio/about section
- Images with keyword-rich alt tags
- Paragraphs: max 2-3 sentences, not too nested
- Lists (numbered/bullet) preferred over dense text
- Engaging title with primary keyword
- Meta description optimized
- URL: short, descriptive keywords, no dates or "blog-1" patterns
- Use keyword synonyms and alternative formulations

## Steps

1. **Crawl** — Call `crawl_website` with `max_pages=5`. Check title tags, meta descriptions, headings, word count across pages.

2. **Link check** — Call `check_links` on the homepage. Report broken links and redirect chains.

3. **On-page analysis** — Call `onpage_analysis` on the homepage with the main keyword from the title/H1. Report the 24-point score.

4. **URL structure** — Call `analyze_url_structure` on 3-5 sample URLs from the crawl. Check for:
   - SEO-friendly URLs (lowercase, hyphens, descriptive keywords)
   - No date patterns, IDs, or parameter strings
   - Reasonable depth (not too many subdirectories)

5. **Compile checklist** — Present a pass/fail checklist:

   **Indexing & Crawlability**
   - [ ] Relevant pages are indexed (check ratio)
   - [ ] Sitemap is submitted and readable
   - [ ] No critical pages blocked by robots.txt

   **On-Page SEO**
   - [ ] Title tags present, within length limits, contain primary keyword
   - [ ] Meta descriptions present and engaging
   - [ ] H1 tags present (exactly 1 per page)
   - [ ] Content score >= 70 (on-page analysis)
   - [ ] Word count adequate (>300 per page)
   - [ ] Internal links (>=5 per page)
   - [ ] Images have keyword-rich alt text

   **Technical Health**
   - [ ] No broken links (404s)
   - [ ] No redirect chains
   - [ ] URLs are SEO-friendly (lowercase, hyphens, no params)
   - [ ] Core Web Vitals: green status (if available)

   **Content Quality**
   - [ ] Paragraphs are short (2-3 sentences max)
   - [ ] Lists used where appropriate
   - [ ] CTAs present linking to offers/contact
   - [ ] External links use proper follow/nofollow

## Quality Gates

- This is a quick check — keep it under 5 tool calls.
- Present results as a clear pass/fail table with severity (critical/warning/info).
- For each failed check, provide a one-sentence fix recommendation.
- Credits: ~50-70.

## Video References

Methodology based on Antonio Blago's SEO training:
- [Die 3 wichtigsten Checks in Google Search Console](https://www.youtube.com/watch?v=QmSkrS5rytE)
- [Aufbau des optimalen Blogartikels](https://www.youtube.com/watch?v=JIzm5OumLEI)
- [Google Search Console - Performance und Indexierung](https://www.youtube.com/watch?v=o5HGyXgGlhA)
