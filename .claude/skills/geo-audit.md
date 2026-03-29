---
description: "GEO (Generative Engine Optimization) audit: AI visibility, citation worthiness, brand mentions, sentiment, grounding pages, and AI-traffic measurement"
---

# /geo-audit

Run a Generative Engine Optimization audit to assess and improve AI visibility — how the brand appears in ChatGPT, Google AI Overviews, Perplexity, Gemini, and other AI search systems.

## Arguments

The user provides:
- Domain (e.g., `example.com`)
- Brand name (e.g., "PURELEI", "Visibly AI")
- Optionally: 2-3 competitors for comparison
- Optionally: business type (B2B / eCommerce / SaaS / D2C / Local)

## Credit Estimate

~50-120 credits depending on depth. Minimum balance: 80 credits.

## Background: GEO vs SEO

**SEO** = Sichtbarkeit in Suchergebnislisten (Google rankings)
**GEO** = Sichtbarkeit innerhalb der KI-Antwort selbst (ChatGPT, AI Overviews, Perplexity)

AI Overviews reduce organic CTR by ~34.5% (Ahrefs 2025 study, 300k keywords). Position #1 informational CTR dropped 44.6%. GEO is no longer optional.

### The 4 Levels of AI Visibility

1. **SEO Foundation** — Who doesn't rank, won't get cited. AI Overviews feed from organic rankings.
2. **Citation Worthiness** — AI extracts individual paragraphs, not whole pages. Each paragraph must answer a clear question standalone.
3. **Brand Visibility** — 80% of brand mentions in AI answers come from third-party domains. Mentions beat backlinks for AI visibility.
4. **Sentiment** — AI evaluates tonality. Positive mentions = more prominent placement.

## Steps

### Phase 1: SEO Foundation Check (20 credits)

1. **Verify credits** — Call `get_account_info`. Need ~80 credits minimum.

2. **Organic baseline** — Call `get_traffic_snapshot(domain)`. Record:
   - Organic traffic, DR, keyword count
   - This is the SEO foundation that GEO builds on

3. **Keyword inventory** — Call `get_keywords(domain, limit=200)`. Then `classify_keywords` on top 50.
   - Focus on informational keywords (most affected by AI Overviews)
   - Flag keywords with high impressions but falling CTR = likely AI Overview impact

### Phase 2: Citation Worthiness Analysis (30-60 credits)

4. **Crawl key pages** — Call `crawl_website` on 5 representative pages:
   - Homepage, 1 category, 1 product, 1 blog article, 1 about/FAQ page
   - For each page evaluate citation worthiness:

   **Citation Worthiness Checklist:**
   - [ ] Clear H1 → H2 → H3 heading hierarchy
   - [ ] One thought per paragraph (standalone readable)
   - [ ] Direct question-answer format present
   - [ ] Factual claims with sources cited
   - [ ] Schema.org structured data (Organization, Product, FAQ, HowTo)
   - [ ] Author attribution with expertise signals (E-E-A-T)
   - [ ] Lead definition format: "[Name] ist ein/eine [Kategorie], die [Funktion]."
   - [ ] No marketing fluff in H1 (just entity name, no adjectives)

5. **Structured data check** — Call `check_structured_data` on 3 key pages:
   - Check for: Organization, Person, Product, FAQPage, HowTo, BreadcrumbList
   - JSON-LD must mirror HTML content exactly (no hidden keywords)
   - Validate that critical entity data is machine-readable

6. **On-page analysis** — Call `onpage_analysis` on the homepage:
   - Evaluate content structure quality for AI extraction
   - Flag thin content (<300 words) — AI can't cite what isn't there

### Phase 3: Brand Visibility & Deep GEO Analysis (0-5 credits)

7. **Deep GEO analysis via backend agent** — Call `seo_agent` for AI-visibility-aware analysis:
   ```
   task: "Vollständiger GEO-Check für [brand] auf [domain]: Brand Visibility (externe Erwähnungen, Vergleichs-Content Präsenz, Fachportal-Sichtbarkeit), Citation Worthiness Score, Grounding Page Status, und AI-Crawler robots.txt Analyse. Gib konkrete Empfehlungen für die 4 Stufen der AI-Sichtbarkeit."
   agent: "consultant"
   domain: "[domain]"
   ```
   The backend agent system has the full GEO knowledge base (4 Stufen, Citation Worthiness, Brand Visibility, Sentiment, Grounding Pages, AI Crawlers) and will generate comprehensive recommendations.

8. **Grounding Page assessment** — From sitemap/crawl data:
   - Look for URLs like `/facts/[brand-name]/` or `/ai/[brand-name]/`
   - If missing: recommend creation following Grounding Page Standard v1.4

### Phase 4: AI Crawler Access Check (0 credits)

9. **robots.txt analysis** — From crawl data, check:
   - Is `OAI-SearchBot` allowed? (ChatGPT search visibility)
   - Is `GPTBot` allowed? (AI model training — separate decision)
   - Is `Google-Extended` allowed? (Gemini, AI training)
   - Is `PerplexityBot` allowed?

   **Recommendation matrix:**
   | Bot | Recommendation | Reason |
   |-----|---------------|--------|
   | OAI-SearchBot | Allow | Needed for ChatGPT search visibility |
   | GPTBot | Decision by client | Training data vs. content protection |
   | Google-Extended | Allow | Needed for Gemini and AI Overviews |
   | PerplexityBot | Allow | Growing search channel |

### Phase 5: AI Traffic Measurement Setup (0 credits)

10. **GA4 LLM channel check** — Recommend setup:
    - Custom Channel Group "LLM" in GA4
    - Regex for AI referrers: `chatgpt.com|perplexity.ai|claude.ai|gemini.google.com|copilot.microsoft.com|grok.com|meta.ai|you.com`
    - Full regex available at: https://gist.github.com/AntonioBlago/3e093b622c91625b18e879ef25d5c81a

### Phase 6: Report Compilation

## Output Format

```markdown
# GEO Audit — [domain] — [date]

## Executive Summary
- 5 bullet points: current AI visibility assessment
- Overall GEO readiness: Not Started / Basic / Intermediate / Advanced
- Biggest quick win for AI visibility

## 1. SEO Foundation (Level 1)
| Metric | Value | Status |
|--------|-------|--------|
| Domain Rating | [0-100] | [ok/warning] |
| Organic Traffic | [monthly] | [ok/warning] |
| Informational Keywords | [count] | [ok/warning] |
| CTR Trend (info keywords) | [rising/stable/falling] | [ok/warning/critical] |

**AI Overview Impact:**
- Keywords likely affected by AI Overviews: [count/list]
- Estimated CTR loss: [percentage if data available]

## 2. Citation Worthiness (Level 2)
| Page | Heading Structure | Standalone Paragraphs | Schema | E-E-A-T Signals | Score |
|------|------------------|----------------------|--------|-----------------|-------|
| Homepage | [ok/fix] | [ok/fix] | [types found] | [ok/missing] | /10 |
| ... | | | | | |

**Top 3 Citation Fixes:**
1. [Specific fix with page URL]
2. [Specific fix]
3. [Specific fix]

## 3. Brand Visibility (Level 3)
| Signal | Status | Action Needed |
|--------|--------|---------------|
| About/Facts Page | [exists/missing] | [action] |
| Organization Schema | [valid/missing/errors] | [action] |
| External Mentions | [assessment] | [action] |
| Grounding Page | [exists/missing] | [action] |
| Comparison/Listicle Presence | [assessment] | [action] |

**Key Insight:** 80% of brand mentions in AI answers come from third-party domains.
Recommendation: Digital PR + Fachportal-Erwaehnungen parallel to SEO.

## 4. Sentiment (Level 4)
- Brand perception assessment based on available data
- Review/rating presence check
- Recommendation for sentiment monitoring

## 5. AI Crawler Access
| Bot | Current Status | Recommendation |
|-----|---------------|----------------|
| OAI-SearchBot | [allowed/blocked/not set] | [action] |
| GPTBot | [allowed/blocked/not set] | [action] |
| Google-Extended | [allowed/blocked/not set] | [action] |
| PerplexityBot | [allowed/blocked/not set] | [action] |

## 6. AI Traffic Measurement
- GA4 LLM Channel: [configured/not configured]
- Setup instructions provided: [yes/no]
- Current LLM traffic (if measurable): [data]

## 7. Grounding Page Template
If missing, provide a template:
- Recommended URL: /facts/[brand-slug]/
- H1: [Brand Name]
- Lead Definition: "[Brand] ist [definition]."
- Key fact grid elements to include
- JSON-LD schema type recommendation

## 8. Priority Action Plan

**P1 — Sofort (Week 1-2)**
- [Specific GEO quick wins: robots.txt, schema fixes, heading structure]

**P2 — Kurzfristig (Month 1)**
- [Grounding page creation, citation-worthy content rewrites]

**P3 — Laufend (Ongoing)**
- [Digital PR for brand mentions, sentiment monitoring, AI traffic tracking]

## 9. GEO KPI Framework

**KPQ 1:** "Werden wir in KI-Antworten zitiert?"
- KPI: AI Citation Rate (Peec.ai, SE Ranking AI tracking)
- KPI: LLM Referral Sessions in GA4

**KPQ 2:** "Ist unser Content zitierfaehig?"
- KPI: Citation Worthiness Score per page
- KPI: Structured data coverage (% pages with valid schema)

**KPQ 3:** "Wie wird unsere Marke in KI wahrgenommen?"
- KPI: Brand Sentiment Score (positive/neutral/negative)
- KPI: Brand mention frequency in AI responses

## Tools for Ongoing GEO Monitoring
- Peec.ai — Prompt tracking, tagging, visibility analysis
- SE Ranking — AI Overviews + ChatGPT prompt tracking
- SISTRIX — SEO + AI extension, sentiment analysis
- Rankscale — Transparent model tracking
- GA4 LLM Channel Group — Traffic from AI referrers
```

## Key Studies Referenced

- Ahrefs 2025: AI Overviews reduce CTR by 34.5% (300k keywords analyzed)
- AirOps 2025: 80%+ brand mentions in AI from third-party domains (177M citations)
- Semrush & Profound 2025: 90% of third-party mentions from comparison/listicle content
- Semrush & Claneo 2025: Mentions beat backlinks for AI visibility
- SimilarWeb: 95.3% of ChatGPT users also use Google; 14.3% of Google users also use ChatGPT

## Quality Gates

- If domain has <100 organic keywords: note "SEO foundation needs building first before GEO"
- If no GSC connected: note limitation in CTR trend analysis
- Always distinguish between what you CAN measure (via tools) and what requires manual monitoring (brand mentions in AI)
- Grounding Page recommendations must follow Standard v1.4 (groundingpage.com/spec/)
- Label all AI traffic projections as estimates
