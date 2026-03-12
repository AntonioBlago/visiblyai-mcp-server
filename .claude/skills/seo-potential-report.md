---
description: "Generate a full SEO potential analysis + offer with roadmap, investment, and ROI calculation for a client domain"
---

# /seo-potential-report

Generate a data-driven SEO potential analysis with realistic traffic projections, lead calculation, SEA equivalence, and a phased offer with roadmap — ready for client presentation.

## Arguments

The user provides:
- Client domain (e.g., `client-domain.com`)
- Target market / country (e.g., `DE`, `AT`, `CH`)
- Optionally: keyword file path (Excel/CSV with target keywords + SV + current positions)
- Optionally: monthly SEA budget (EUR) for equivalence calculation
- Optionally: business type (B2B / eCommerce / SaaS / Local)

## Methodology

Based on the real Antonio Blago workflow validated across multiple B2B and eCommerce clients.

### Data Pipeline

```
Excel Keywords → analyze_potential (CTR modeling + GSC mapping)
GSC Live Data  → validate_keywords → cross-reference
Competitor data → get_competitors → benchmark gap
All data        → generate offer structure + PDF
```

### Phase 1: Status-Quo Analysis

Pull live GSC data to establish the current baseline:

1. **`get_google_connections`** — verify GSC/GA4 are connected for this project
2. **`query_search_console`** — dimension=query, limit=500, country filter (e.g., `deu`)
3. **`query_search_console`** — dimension=page, limit=100 — find underperforming URLs
4. If keyword file provided: cross-reference every target keyword against live GSC data (clicks, impressions, CTR, position)

**Keyword classification buckets:**
- Brand vs. Generic vs. Competitor
- Ranking status: Top 3 / Page 1 (4-10) / Page 2 (11-20) / Weak (21-100) / Not Ranking (>100)
- Brand-share of clicks (high brand-share = no discovery funnel = red flag)

### Phase 2: Potential Calculation

Apply CTR model per keyword based on target position:

```python
def estimated_ctr(position):
    """Keyword Study 2026 — 1.3M keywords, 94 domains"""
    if position <= 1: return 0.0559
    elif position <= 2: return 0.0315
    elif position <= 3: return 0.0237
    elif position <= 4: return 0.0207
    elif position <= 5: return 0.0151
    elif position <= 6: return 0.0111
    elif position <= 7: return 0.0087
    elif position <= 8: return 0.0068
    elif position <= 9: return 0.0057
    elif position <= 10: return 0.0052
    elif position <= 20: return 0.0045
    elif position <= 50: return 0.003
    else: return 0.001
```

**Target position logic (12-month horizon):**

```python
def target_position(current_pos, search_volume):
    if current_pos > 100:
        if search_volume > 10000: return 15
        elif search_volume > 5000: return 12
        elif search_volume > 1000: return 8
        else: return 5
    elif current_pos > 20:
        return max(5, current_pos - 10)
    elif current_pos > 10:
        return max(3, current_pos - 5)
    else:
        return max(1, current_pos - 2)
```

**Calculate per keyword:**
- Current clicks = SV × estimated_ctr(current_pos)
- Target clicks = SV × estimated_ctr(target_pos)
- Delta = Target clicks - Current clicks

**Aggregate by cluster/theme** — show top 10 clusters by delta.

### Phase 3: Lead & ROI Calculation

```
Lead calculation (B2B):
- Contact rate: 1.5% conservative / 2.0% realistic / 2.5% optimistic
- Close rate: 10-20%
- Average deal value: ask user or estimate from industry

SEA equivalence:
- Multiply additional clicks/month by avg CPC (from get_keywords or user-provided)
- Annual SEA value = add. clicks × 12 × avg CPC

ROI:
- Investment: phased offer total (see Phase 5)
- Return: annual SEA equivalent or lead value
```

### Phase 4: Quick Wins

Identify top 5 quick wins:
- From GSC: keywords with position 4-15 AND high impressions AND CTR < benchmark
- From keyword file: keywords currently not ranking (>100) but with existing page content
- Filter for: Impressions > 100, CTR < 5%, Position 5-20 = title/meta fix = fastest win

### Phase 5: Generate Offer Structure

Structure the offer in 4 phases matching client context:

| Phase | Name | Scope | Investment |
|-------|------|-------|------------|
| 0 | Setup & Datensichtung | Materials review, GSC/GA4 access, mapping | Inkl. in Phase 1 |
| 1 | Advanced SEO Audit | Technical, content, structure, competitor, quick wins | 2.000-3.500 EUR |
| 2 | Strategische Begleitung | 3-4 months, monthly retainer | 1.200-2.000 EUR/Mo |
| 3 | Optional: Neuro-SEO / Content Cluster | Advanced module after Phase 1 data | 3.000-5.000 EUR |

**Budget calibration rules:**
- Small business (< 500k ARR): Phase 1: 1.500 EUR, Phase 2: 800 EUR/Mo
- Mid-market (500k-5M ARR): Phase 1: 2.500 EUR, Phase 2: 1.500 EUR/Mo
- Enterprise (> 5M ARR): Phase 1: 3.500 EUR, Phase 2: 2.000 EUR/Mo

### Phase 6: Milestone Roadmap (High-Level)

| Quarter | Milestone | Expected Result |
|---------|-----------|-----------------|
| Q1 | Audit + Quick Wins | +50-100% org. traffic |
| Q2 | Content-Cluster + Tech-Fixes | +200-300% org. traffic |
| Q3 | Skalierung + Tracking | +400-500% org. traffic |
| Q4 | Optimierung + Scale | +700-1.000% org. traffic |

### Phase 7: KPQ / KPI Framework

Always propose 3 KPQs (Key Performance Questions) + KPIs:

**KPQ 1:** "Sind wir im relevanten Umfeld sichtbar ohne Brand-Traffic?"
- KPI: Non-Brand organic Clicks/Month
- KPI: Non-Brand Keywords Page 1

**KPQ 2:** "Steigern wir Markenbekanntheit digital?"
- KPI: Brand search volume trend (GSC)
- KPI: Direct traffic (GA4)

**KPQ 3:** "Generieren wir qualifizierte Kontakte über digitale Kanäle?"
- KPI: Contact form submissions / downloads / calls
- KPI: Lead-to-Sale conversion rate

## Steps

1. **Get live data** — `get_google_connections`, `query_search_console` (query + page dimensions)
2. **Get tracked keywords** — `get_keywords` if project exists in Visibly AI
3. **Get competitors** — `get_competitors` for benchmark (limit=5)
4. **Classify keywords** — `classify_keywords` on top 100 GSC queries
5. **Calculate potential** — Apply CTR model and target position logic to all keywords
6. **Find quick wins** — Filter GSC for high-impression / low-CTR opportunities
7. **Structure offer** — Match to business size, existing work, client context
8. **Generate report** — Present as structured document (see Output Format)

## Output Format

```
# SEO Potential Report — [Client Domain] / [Date]

## 1. Ausgangslage (Status-Quo)
- Tabelle: Kennzahlen (Traffic, Keywords, Brand-Anteil, etc.)
- Tabelle: Ranking-Verteilung (Top 3 / Page 1 / Page 2 / Weak / Not Ranking)

## 2. Cluster-Potenzial
- Tabelle: Top 10 Cluster nach Delta (SV, Ist-Clicks, Ziel-Clicks, Delta)

## 3. Wachstumsprognose (12 Monate)
- Traffic-Prognose Tabelle (3 / 6 / 12 Monate)
- Lead-Potenzial (konservativ / realistisch / optimistisch)
- SEA-Äquivalenz

## 4. Quick Wins (Top 5)
- Tabelle: Keyword, SV, Impressions, Clicks, CTR, Pos., Maßnahme

## 5. Angebot & Investition
- Phasen-Tabelle mit Leistungen + Investment
- Gesamt-Investment + ROI

## 6. Meilensteinplan (High-Level)
- Quartals-Tabelle

## 7. KPQ / KPI Framework
- 3 KPQs mit zugehörigen KPIs
```

## PDF Generation

If the user asks for a PDF deliverable:

1. **Setup fonts** from `FONT_DIR` (see `/ci-setup-guide` for path setup — Montserrat + Mulish with `uni=True`)
2. **Use CI colors:**
   ```python
   ACCENT = (246, 87, 30)      # Orange #f6571e
   DARK = (12, 17, 21)         # #0c1115
   SUCCESS = (26, 188, 156)    # Teal #1abc9c
   DANGER = (207, 46, 46)      # Red #cf2e2e
   LIGHT_BG = (248, 248, 248)  # #f8f8f8
   ```
3. **Structure:** Cover page → Table of Contents → Status-Quo → Potential → Quick Wins → Offer → ROI → Roadmap → KPIs
4. **Save to:** `<SEO_PROJECTS_DIR>/<client>/Reports/`
5. **Reference script:** see `/ci-setup-guide` → Implementation References → `generate_pdf.py`

## Quality Gates

- Always cross-reference keyword file data against live GSC — never report without GSC validation
- Flag if Brand clicks > 70% of total (no discovery funnel = critical problem)
- Flag if > 80% of target keywords not ranking at all (likely technical/authority issue)
- Quick wins must have > 100 impressions in last 28 days to be actionable
- Traffic projections: label as conservative/realistic/optimistic — never as guaranteed
- Include risk table with 3-5 realistic risks + countermeasures

## Implementation Reference

Validated across B2B client projects (manufacturing / industry sector, March 2026):
- 216 target keywords analyzed, 82% not ranking at all
- Brand-share: 91.5% of all clicks (no discovery funnel)
- 12-month potential: +7,757 additional organic clicks/month
- SEA equivalence: ~80,000 EUR/year vs. 8,500 EUR investment = 9.4x ROI
- Reference scripts: `<SEO_PROJECTS_DIR>/<client>/Scripts/analyze_potential.py`, `generate_pdf.py`
