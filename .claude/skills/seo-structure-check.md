---
description: "Audit a website's SEO structure: URL routing, canonical URLs, sitemap, robots.txt, and hreflang consistency"
---

# /seo-structure-check

Audit a website's technical SEO structure — URL canonicalization, sitemap health, robots.txt, and hreflang implementation.

## Arguments

The user provides a domain or URL (e.g., `https://www.antonioblago.com`).
Optionally: the site's primary language (`de`, `en`, or `bilingual`).

## What This Checks

### 1. URL Routing & Canonical Structure

The canonical URL is the one Google should index. All other variants must redirect (301) to it.

**Correct pattern for bilingual sites:**
- German pages: `/de/<slug>` is canonical → bare `/slug` redirects 301 to `/de/<slug>`
- English pages: `/slug` (no locale prefix) is canonical
- Capital-letter variants (`/Impressum`) → redirect to lowercase canonical

**Check for:**
- [ ] Bare routes (without `/de/`) redirect to canonical with 301
- [ ] No duplicate content served at both `/slug` AND `/de/slug`
- [ ] Consistent lowercase URLs (no `/de/Impressum`, only `/de/impressum`)
- [ ] Legal pages have their own canonical URLs (not redirected to external domains)

### 2. Sitemap Audit

**Rules:**
- Only include **indexable** canonical URLs — never include `noindex` pages
- Both EN and DE versions of bilingual pages must appear
- Every bilingual URL pair must have `xhtml:link` hreflang annotations inside the `<url>` block
- `x-default` should point to the English (default) version

**Check for:**
- [ ] No `noindex` pages in sitemap (legal pages, account pages, etc.)
- [ ] No redirect URLs in sitemap (only canonical 200-status URLs)
- [ ] All bilingual page pairs present (EN + DE)
- [ ] Every bilingual `<url>` has hreflang `xhtml:link` for `en`, `de`, and `x-default`
- [ ] `<loc>` uses `www.` consistently (not bare domain)
- [ ] Missing tool/feature pages added

**Correct hreflang format in sitemap:**
```xml
<url>
    <loc>https://www.example.com/seo-tools</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://www.example.com/seo-tools"/>
    <xhtml:link rel="alternate" hreflang="de" href="https://www.example.com/de/seo-tools"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="https://www.example.com/seo-tools"/>
</url>
```

### 3. robots.txt Audit

**Rules:**
- `Allow` all indexable canonical URLs explicitly
- `Disallow` all app/login/account/internal routes
- Legal pages: `Allow` them for crawling (Google can crawl them even if noindex)
- Sitemap directive at the bottom: `Sitemap: https://www.domain.com/sitemap.xml`

**Check for:**
- [ ] All canonical indexable pages are explicitly Allowed
- [ ] Both EN and DE variants Allowed for bilingual pages
- [ ] `/de/` prefix correct (lowercase, matches actual routes)
- [ ] No old/redirect URLs listed (e.g., `/agb` if it now redirects to `/de/agb`)
- [ ] App routes Disallowed: `/admin/`, `/account/`, `/api/`, `/login`, `/register`, etc.
- [ ] Sitemap URL is correct and uses `www.`

### 4. Hreflang in `<head>`

For dynamically rendered sites, hreflang tags in `<head>` must match sitemap annotations.

**Correct pattern:**
```html
<link rel="alternate" hreflang="en" href="https://www.example.com/seo-tools">
<link rel="alternate" hreflang="de" href="https://www.example.com/de/seo-tools">
<link rel="alternate" hreflang="x-default" href="https://www.example.com/seo-tools">
<link rel="canonical" href="https://www.example.com/seo-tools">  <!-- or /de/seo-tools on DE page -->
```

**Check for:**
- [ ] Hreflang present on all bilingual pages
- [ ] Canonical tag matches the URL being rendered (not the other language version)
- [ ] `x-default` points to the EN version
- [ ] Legal pages override hreflang block with static URLs (not dynamically generated)

### 5. Legal Pages Structure

Legal pages (Impressum, Datenschutz, AGB, Privacy, etc.) have special rules:
- Must have `noindex, nofollow` meta robots
- Must NOT appear in sitemap
- Must be crawlable in robots.txt (crawling ≠ indexing)
- Must have correct hreflang pointing to EN/DE counterpart
- Each legal page should render its own content — never redirect to an external domain

**Canonical legal URL pairs (German sites):**
| German | English |
|--------|---------|
| `/de/impressum` | `/imprint` |
| `/de/datenschutz` | `/privacy` |
| `/de/agb` | `/terms-conditions` |
| `/de/nutzungsbedingungen` | `/terms-of-service` |
| `/de/subprozessoren` | `/sub-processors` |
| `/de/verschluesselung` | `/encryption` |
| `/de/ki-disclaimer` | `/ai-disclaimer` |

## Steps

1. **Fetch sitemap** — Call `analyze_url_structure` on `domain/sitemap.xml`. Check for noindex pages, redirect URLs, missing hreflang pairs.

2. **Check key routes** — Call `check_links` on the homepage. Verify all footer legal links resolve to 200 (not 404 or redirect loop).

3. **Crawl sample pages** — Call `crawl_website` with `max_pages=10`. For each bilingual page found:
   - Verify canonical tag matches the URL
   - Verify hreflang tags are present and correct
   - Verify no `noindex` on pages that should be indexed

4. **Compile checklist** — Present a pass/fail table:

| Area | Check | Status | Fix |
|------|-------|--------|-----|
| Sitemap | No noindex pages | ✓/✗ | Remove legal pages from sitemap |
| Sitemap | All bilingual pairs present | ✓/✗ | Add missing DE/EN versions |
| Sitemap | hreflang xhtml:link on all pairs | ✓/✗ | Add xhtml:link annotations |
| robots.txt | Canonical URLs Allowed | ✓/✗ | Add /de/ variants |
| robots.txt | No redirect URLs listed | ✓/✗ | Remove /agb if it redirects |
| Routing | Bare routes redirect 301 | ✓/✗ | Add redirect to /de/ canonical |
| Routing | No duplicate content | ✓/✗ | Remove dual-rendering routes |
| Head | hreflang on bilingual pages | ✓/✗ | Add via URL_MAP + template |
| Head | canonical matches rendered URL | ✓/✗ | Fix canonical tag |
| Legal | noindex on all legal pages | ✓/✗ | Add meta robots noindex |
| Legal | legal pages render own content | ✓/✗ | Remove external redirects |

## Testing

After making any structural fixes, run these tests to verify correctness:

### 1. HTTP Status Tests

For each canonical URL, verify it returns 200:
```bash
curl -o /dev/null -s -w "%{http_code}" https://www.example.com/de/impressum
curl -o /dev/null -s -w "%{http_code}" https://www.example.com/imprint
```

For each redirect URL, verify it returns 301 and the correct `Location` header:
```bash
curl -I https://www.example.com/impressum
# Expected: HTTP/2 301 + Location: https://www.example.com/de/impressum
curl -I https://www.example.com/en/pricing
# Expected: HTTP/2 301 + Location: https://www.example.com/pricing
```

### 2. Hreflang Consistency Test

Both pages in a bilingual pair must reference each other symmetrically. Fetch both:
```bash
curl -s https://www.example.com/seo-tools | grep hreflang
curl -s https://www.example.com/de/seo-tools | grep hreflang
```
**Pass:** EN page has `hreflang="de"` pointing to DE URL, and vice versa.
**Fail:** One page references a URL that redirects or returns 404.

### 3. Sitemap Validation

Fetch the sitemap and verify every `<loc>` returns 200:
```python
import requests
from xml.etree import ElementTree as ET

r = requests.get("https://www.example.com/sitemap.xml")
tree = ET.fromstring(r.content)
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
for url in tree.findall("s:url/s:loc", ns):
    status = requests.head(url.text, allow_redirects=False).status_code
    print(f"{status} {url.text}")
    assert status == 200, f"Sitemap URL not 200: {url.text}"
```

### 4. noindex Pages NOT in Sitemap

Verify legal pages are absent from sitemap:
```python
sitemap_content = requests.get("https://www.example.com/sitemap.xml").text
noindex_paths = ["/de/impressum", "/imprint", "/de/datenschutz", "/privacy", "/de/agb"]
for path in noindex_paths:
    assert path not in sitemap_content, f"noindex page found in sitemap: {path}"
```

### 5. robots.txt Sanity Check

Verify key paths are not accidentally blocked:
```python
from urllib.robotparser import RobotFileParser
rp = RobotFileParser()
rp.set_url("https://www.example.com/robots.txt")
rp.read()
indexable = ["/", "/de/", "/seo-tools", "/de/seo-tools", "/pricing", "/de/preise"]
for path in indexable:
    assert rp.can_fetch("*", f"https://www.example.com{path}"), f"Blocked: {path}"
```

### 6. Canonical Tag Test

Crawl each page and verify canonical matches its own URL (not the other language version):
```python
import requests
from bs4 import BeautifulSoup

def check_canonical(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    canonical = soup.find("link", rel="canonical")["href"]
    assert canonical == url, f"Wrong canonical on {url}: got {canonical}"

check_canonical("https://www.example.com/de/seo-tools")
check_canonical("https://www.example.com/seo-tools")
```

### For Flask/Python Projects (Bikefitting_Project)

Run the existing test suite after routing changes:
```bash
pytest scripts/Testing/ \
  --ignore=scripts/Testing/quick_test.py \
  --ignore=scripts/Testing/test_blog_access.py \
  --ignore=scripts/Testing/test_eeat_classifier_integration.py \
  --ignore=scripts/Testing/test_eeat_page_embeddings.py \
  -v -k "route or sitemap or redirect or legal"
```

Write dedicated route tests in `scripts/Testing/test_seo_structure.py`:
```python
def test_legal_redirects(client):
    """Bare legal routes must 301 to /de/ canonical."""
    for path, expected in [
        ("/impressum", "/de/impressum"),
        ("/agb", "/de/agb"),
        ("/datenschutz", "/de/datenschutz"),
    ]:
        r = client.get(path)
        assert r.status_code == 301
        assert r.headers["Location"].endswith(expected)

def test_legal_canonicals_200(client):
    """Canonical legal pages must return 200."""
    for path in ["/de/impressum", "/de/datenschutz", "/de/agb", "/imprint", "/privacy"]:
        r = client.get(path)
        assert r.status_code == 200

def test_sitemap_no_noindex_pages(client):
    """sitemap.xml must not contain noindex legal pages."""
    r = client.get("/sitemap.xml")
    content = r.data.decode()
    for blocked in ["/impressum", "/datenschutz", "/agb", "/imprint", "/privacy"]:
        assert blocked not in content, f"noindex page in sitemap: {blocked}"

def test_hreflang_symmetry(client):
    """Each bilingual page pair must reference each other."""
    pairs = [("/seo-tools", "/de/seo-tools"), ("/pricing", "/de/preise")]
    for en_url, de_url in pairs:
        en_soup = BeautifulSoup(client.get(en_url).data, "html.parser")
        de_soup = BeautifulSoup(client.get(de_url).data, "html.parser")
        en_hreflang_de = en_soup.find("link", hreflang="de")["href"]
        de_hreflang_en = de_soup.find("link", hreflang="en")["href"]
        assert de_url in en_hreflang_de
        assert en_url in de_hreflang_en
```

## Quality Gates

- Credit cost: ~30–50 credits (crawl + link check + URL analysis).
- Flag any legal page that redirects to an external domain — this hides content from users.
- Flag any page in sitemap that returns non-200 status.
- Flag any bilingual page missing from sitemap.

## Implementation Reference

Applied on `antonioblago.com` (2026-03-12):
- `/impressum`, `/agb`, `/datenschutz` → now 301 redirect to `/de/` canonical
- `/de/Impressum` → renamed to `/de/impressum` (lowercase)
- `URL_MAP` in `run.py` extended with all legal page pairs for automatic hreflang
- Sitemap: removed all `noindex` legal pages, added missing tool pages
- robots.txt: corrected canonical paths, added all bilingual variants
