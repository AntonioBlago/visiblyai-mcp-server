---
description: "Setup guide for CI brand identity, fonts, logos, colors, report preferences — plus Python and MCP Playwright installation"
---

# /ci-setup-guide

Complete setup guide for generating CI-compliant reports and tools: brand identity reference, font setup, logo paths, color constants, report preferences, Python environment, and MCP Playwright installation.

## Brand Identity — Antonio Blago

> **Path setup:** Place your font, logo, and image assets in a folder and set `ASSETS_DIR` once.
> The recommended location is `~/.claude/assets/` (works on all platforms).
> On Windows: `C:\Users\<username>\.claude\assets\`
> On Mac/Linux: `~/.claude/assets/`

### Colors

```python
# RGB tuples — use for PDF (fpdf2), matplotlib charts
ACCENT_ORANGE = (246, 87, 30)     # #f6571e — primary brand color
SECONDARY_ORANGE = (255, 145, 44) # #ff912c — secondary orange
BLUE = (47, 138, 229)             # #2f8ae5 — secondary
LIGHT_BLUE = (57, 163, 209)       # #39a3d1
DARK_NAVY = (4, 57, 89)           # #043959
DEEPEST_DARK = (12, 17, 21)       # #0c1115 — backgrounds
NEAR_BLACK = (23, 23, 22)         # #171716
TEAL = (26, 188, 156)             # #1abc9c — success
DANGER = (207, 46, 46)            # #cf2e2e — error/critical
LIGHT_BG = (248, 248, 248)        # #f8f8f8 — table alternating
WHITE = (255, 255, 255)

# Hex strings — use for Excel (openpyxl), HTML
ORANGE_HEX = 'F6571E'
DARK_HEX = '0C1115'
TEAL_HEX = '1ABC9C'
DANGER_HEX = 'CF2E2E'
NAVY_HEX = '043959'
LIGHT_BG_HEX = 'F8F8F8'
```

### Fonts

**Paths:**
```python
import os

# Set ASSETS_DIR to wherever you stored the assets folder.
# Default: ~/.claude/assets/ — works on Windows, Mac, Linux
ASSETS_DIR = os.environ.get("REPORT_ASSETS_DIR", os.path.expanduser("~/.claude/assets"))

# Subfolders:
FONT_DIR   = os.path.join(ASSETS_DIR, "fonts")    # Montserrat + Mulish TTF files
IMAGE_DIR  = os.path.join(ASSETS_DIR, "images")   # logos, photos, charts
LOGO_PATH  = os.path.join(IMAGE_DIR, "logo.png")
PHOTO_PATH = os.path.join(IMAGE_DIR, "photo.jpg")
```

**Available font files (place in `FONT_DIR`):**
- `Montserrat-Regular.ttf` — headings, buttons, section titles
- `Montserrat-SemiBold.ttf`
- `Montserrat-Bold.ttf`
- `Montserrat-ExtraBold.ttf`
- `Montserrat-Italic.ttf`
- `Montserrat-BoldItalic.ttf`
- `Mulish-Regular.ttf` — body text, tables
- `Mulish-SemiBold.ttf`
- `Mulish-Bold.ttf`
- `Mulish-Italic.ttf`

**fpdf2 registration (always include `uni=True` for German umlauts):**
```python
from fpdf import FPDF

pdf.add_font('Montserrat', '',   os.path.join(FONT_DIR, 'Montserrat-Regular.ttf'),   uni=True)
pdf.add_font('Montserrat', 'B',  os.path.join(FONT_DIR, 'Montserrat-Bold.ttf'),      uni=True)
pdf.add_font('Montserrat', 'I',  os.path.join(FONT_DIR, 'Montserrat-Italic.ttf'),    uni=True)
pdf.add_font('Montserrat', 'BI', os.path.join(FONT_DIR, 'Montserrat-BoldItalic.ttf'),uni=True)
pdf.add_font('Mulish',     '',   os.path.join(FONT_DIR, 'Mulish-Regular.ttf'),       uni=True)
pdf.add_font('Mulish',     'B',  os.path.join(FONT_DIR, 'Mulish-Bold.ttf'),          uni=True)
pdf.add_font('Mulish',     'I',  os.path.join(FONT_DIR, 'Mulish-Italic.ttf'),        uni=True)
```

### Logos & Images

Place all brand assets in `IMAGE_DIR`:

```
<ASSETS_DIR>/images/
├── logo.png          ← brand logo
├── photo.jpg         ← author/consultant photo
└── logos/            ← client logos (e.g. client-name-logo.png)
```

**Usage in PDF:**
```python
# Check before embedding to avoid FileNotFoundError:
if os.path.exists(LOGO_PATH):
    pdf.image(LOGO_PATH, x=10, y=10, w=40)
```

## Report Standards

### PDF Layout (A4)

```
Page 1:  Cover (dark bg #0c1115, orange accent bar, logo, title, client, date, contact)
Page 2:  Executive Summary or Table of Contents
Pages 3+: Content sections
Last:    Investment table + ROI + Next Steps + Contact footer
```

**CI Design Rules:**
- Background: DEEPEST_DARK on cover, WHITE on content pages
- Section titles: orange accent bar (3mm) left of text + Montserrat Bold 14pt
- Table header: orange bg, white text, Montserrat Bold 9pt
- Table rows: alternating WHITE and LIGHT_BG (#f8f8f8)
- KPI boxes: teal=good, orange=warning, red=critical
- Info boxes: colored left bar (3mm) + tinted background (10% opacity of bar color)
- Body text: Mulish 9-10pt, NEAR_BLACK
- Captions: Mulish 8pt, gray (140, 140, 140)

**Page break safety (always include):**
```python
def ensure_space(self, needed_mm):
    if self.get_y() + needed_mm > 275:
        self.add_page()
        self._redraw_table_header()  # if inside a table
```

### Excel Layout

```python
# Sheet structure:
# Sheet 1: Data Matrix (frozen panes, auto-filter, dropdowns)
# Sheet 2: Summary Dashboard (KPIs + charts)
# Sheet 3: Methodology (data sources, date ranges, limitations)

# Style constants (openpyxl):
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

HEADER_FILL = PatternFill("solid", fgColor="F6571E")
HEADER_FONT = Font(color="FFFFFF", bold=True, name="Montserrat", size=10)
ALT_FILL = PatternFill("solid", fgColor="F8F8F8")
TEAL_FILL = PatternFill("solid", fgColor="1ABC9C")
DANGER_FILL = PatternFill("solid", fgColor="CF2E2E")
```

## Alternative Color Palettes (Other Clients)

If the client has their own CI, define a palette class and swap it in.
Inspired by [2026 design system trends](https://inkbotdesign.com/stunning-colour-palettes/) — warm neutrals, blue-greens, and heritage tones:

```python
# Corporate deep blue (B2B / enterprise, authority + trust)
class BluePalette:
    PRIMARY    = (13, 27, 62)        # deep navy #0D1B3E
    ACCENT     = (30, 76, 161)       # cobalt blue #1E4CA1
    SUCCESS    = (39, 174, 96)       # green #27AE60
    DANGER     = (192, 57, 43)       # red #C0392B
    ALT_BG     = (245, 248, 252)     # off-white
    TEXT       = (20, 20, 20)
    TEXT_MUTED = (100, 110, 120)

# Warm neutral + coral (SaaS / startup / 2026 trend)
class CoralPalette:
    PRIMARY    = (255, 255, 255)     # white background
    ACCENT     = (255, 99, 71)       # coral red #FF6347
    SUCCESS    = (16, 185, 129)      # emerald #10B981
    DANGER     = (239, 68, 68)       # red-500 #EF4444
    ALT_BG     = (255, 250, 245)     # warm off-white
    TEXT       = (30, 20, 15)        # warm near-black
    TEXT_MUTED = (130, 115, 105)     # warm gray

# Smoky jade / teal (sustainability, health, blue-green trend 2026)
class JadePalette:
    PRIMARY    = (28, 42, 40)        # dark jade #1C2A28
    ACCENT     = (74, 99, 93)        # smoky jade #4A635D
    SUCCESS    = (60, 140, 100)      # forest green
    DANGER     = (180, 70, 55)       # terracotta
    ALT_BG     = (245, 248, 246)     # cool off-white
    TEXT       = (20, 32, 28)
    TEXT_MUTED = (100, 120, 112)

# Luxury chocolate + gold (premium, heritage, editorial)
class LuxuryPalette:
    PRIMARY    = (78, 52, 46)        # chocolate brown #4E342E
    ACCENT     = (212, 175, 55)      # gold #D4AF37
    SUCCESS    = (165, 132, 40)      # warm olive gold
    DANGER     = (180, 50, 50)
    ALT_BG     = (255, 253, 245)     # warm cream
    TEXT       = (40, 25, 20)
    TEXT_MUTED = (140, 115, 100)
```

**Hex equivalents for Excel:**
| Palette | Style | Primary | Accent | Success | Danger |
|---------|-------|---------|--------|---------|--------|
| Corporate Blue | B2B / enterprise | `0D1B3E` | `1E4CA1` | `27AE60` | `C0392B` |
| Coral Warm | SaaS / startup | `FFFFFF` | `FF6347` | `10B981` | `EF4444` |
| Smoky Jade | Sustainability / health | `1C2A28` | `4A635D` | `3C8C64` | `B44637` |
| Luxury Gold | Premium / editorial | `4E342E` | `D4AF37` | `A58428` | `B43232` |

## Alternative Fonts (Client-Specific)

Replace the `FONT_DIR` fonts with the client's brand fonts. Naming convention stays the same:

```python
# For a client using Inter (modern SaaS look):
# Download Inter from fonts.google.com/specimen/Inter
# Place in FONT_DIR as:
# Inter-Regular.ttf, Inter-Bold.ttf, Inter-Italic.ttf

pdf.add_font('Inter', '',  os.path.join(FONT_DIR, 'Inter-Regular.ttf'), uni=True)
pdf.add_font('Inter', 'B', os.path.join(FONT_DIR, 'Inter-Bold.ttf'),   uni=True)

# For a client using Playfair Display + Lato (editorial/luxury):
pdf.add_font('Playfair', '',  os.path.join(FONT_DIR, 'PlayfairDisplay-Regular.ttf'), uni=True)
pdf.add_font('Playfair', 'B', os.path.join(FONT_DIR, 'PlayfairDisplay-Bold.ttf'),    uni=True)
pdf.add_font('Lato',     '',  os.path.join(FONT_DIR, 'Lato-Regular.ttf'),            uni=True)
pdf.add_font('Lato',     'B', os.path.join(FONT_DIR, 'Lato-Bold.ttf'),              uni=True)
```

**Font pairings by report type:**
| Report Style | Heading Font | Body Font | Use For |
|-------------|-------------|-----------|---------|
| Default (brand) | Montserrat | Mulish / Aptos | Antonio Blago reports |
| Corporate | Montserrat | Inter | B2B enterprise clients |
| Editorial | Playfair Display | Lato | Creative/agency clients |
| Technical | Roboto | Roboto Mono | Developer / SaaS |
| Minimal | Inter | Inter | Startup / SaaS |

### Contact Information (Always in Footer)

```
Antonio Blago | Neuro-SEO System®
Hohenzollernstraße 143, 56058 Koblenz
Tel: +49 163 698 0955
E-Mail: info@antonioblago.com
Web: www.antonioblago.com
```

### Language Rules (German Reports)

- Always use **"du"** form (informal) — never "Sie"
- Always use UTF-8 umlauts: ä, ö, ü, ß — never ae, oe, ue, ss
- Management reports for international clients: English
- Team/operational documents: German

## Project Folder Structure

```
<SEO_PROJECTS_DIR>/<client-domain>/
├── Keywords/       # Excel/CSV keyword data, SV, positions
├── Data/           # GSC JSON, GA4 exports, crawl data
├── Reports/        # Generated PDFs, Excel deliverables
├── Scripts/        # Python analysis & generation scripts
├── Images/         # Charts, screenshots, logos
└── Archive/        # Previous proposals, old versions
```

**Create on new project:**
```python
import os

# Set SEO_PROJECTS_DIR via env var or use default:
SEO_PROJECTS_DIR = os.environ.get(
    "SEO_PROJECTS_DIR",
    os.path.expanduser("~/.claude/seo-projects")
)

client = "example.com"
base = os.path.join(SEO_PROJECTS_DIR, client)
for folder in ["Keywords", "Data", "Reports", "Scripts", "Images", "Archive"]:
    os.makedirs(os.path.join(base, folder), exist_ok=True)
```

## Python Environment Setup

### Required for Report Generation

```bash
# 1. Verify Python is installed
python --version
# Requires: Python 3.10+

# 2. Install core dependencies
pip install fpdf2 Pillow openpyxl pandas matplotlib requests

# For SSH tunneling (production DB access from local):
pip install sshtunnel pymysql

# For SEO data processing:
pip install numpy scipy

# Check installation:
python -c "from fpdf import FPDF; from PIL import Image; import openpyxl; import pandas; print('OK')"
```

### Chart Generation

```python
import matplotlib
matplotlib.use('Agg')  # CRITICAL: headless mode for server/script use
import matplotlib.pyplot as plt

# Always save at 600 DPI for print-quality PDFs:
output_path = os.path.join(SEO_PROJECTS_DIR, "<client>", "Images", "chart.png")
plt.savefig(output_path, dpi=600, bbox_inches='tight', transparent=True)
```

## MCP Playwright Setup

### Installation

```bash
# 1. Verify Node.js is installed
node --version  # Requires: 18+
npm --version

# 2. Install Playwright MCP server
npm install -g @playwright/mcp

# 3. Install browser binaries
npx playwright install chromium
# Or install all browsers:
npx playwright install

# 4. Verify:
npx playwright --version
```

### Claude Code Configuration

Add to Claude Code settings (`~/.claude/settings.json` or via `/mcp` command):

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp", "--headless"],
      "env": {}
    }
  }
}
```

**Headless mode** (default, no browser window):
```json
"args": ["@playwright/mcp", "--headless"]
```

**Headed mode** (see browser, useful for debugging):
```json
"args": ["@playwright/mcp"]
```

### Available Playwright MCP Tools

| Tool | Use Case |
|------|----------|
| `browser_navigate` | Go to URL |
| `browser_snapshot` | Get accessibility tree (default for reading) |
| `browser_take_screenshot` | Capture visual screenshot |
| `browser_click` | Click element |
| `browser_fill_form` | Fill form fields |
| `browser_type` | Type text at cursor |
| `browser_select_option` | Select dropdown value |
| `browser_evaluate` | Run JavaScript |
| `browser_network_requests` | Inspect network traffic |

### Visibly AI MCP Server

```bash
# Install from PyPI:
pip install visiblyai-mcp-server

# Or run locally from source:
cd <path-to-visiblyai-mcp-server>
pip install -e .
python -m visiblyai_mcp.server

# Configure in Claude Code:
# Add to MCP settings with API key from visibly-ai.com/account
```

**Three-system architecture:**
- `www.antonioblago.com` — Main web app (Flask, PythonAnywhere)
- `visibly-ai.com` — Landing page + auth
- `mcp.visibly-ai.com` — MCP server (FastAPI, PythonAnywhere)

## Initial Setup: Crawl Your Own Domain

On a new project, crawl the client's domain first to populate baseline data in Visibly AI:

```
# Step 1: Find the project
list_projects

# Step 2: Check what's connected
get_google_connections

# Step 3: Crawl the domain (collects on-page data, internal links, meta tags)
crawl_website(domain="example.com", max_pages=20)

# Step 4: Get current keyword rankings
get_keywords(domain="example.com", limit=200)

# Step 5: Get traffic snapshot
get_traffic_snapshot(domain="example.com")

# Step 6: Get competitor landscape
get_competitors(domain="example.com", limit=5)
```

This gives you the baseline needed before running `/seo-potential-report` or `/keyword-performance-report`.

**Cost estimate:** ~50-80 credits for a full baseline crawl + keyword + traffic + competitors.

## Quick Reference Checklist

Before starting any report:

- [ ] Python env active with fpdf2, Pillow, openpyxl, pandas, matplotlib
- [ ] `ASSETS_DIR` set and font files exist (check with `os.path.exists(FONT_DIR)`)
- [ ] Client folder created with standard structure
- [ ] Logo file exists for client (or use default `logo.png`)
- [ ] GSC connected in Visibly AI project
- [ ] matplotlib using `Agg` backend
- [ ] Output path uses `os.makedirs(path, exist_ok=True)`

## Python Report Scripts

The report scripts are **not bundled in the MCP server** — they run locally on your machine inside each client project folder.

### Where They Live

```
<SEO_PROJECTS_DIR>/<client>/Scripts/
├── generate_pdf.py              # CI-compliant A4 PDF (fpdf2 FPDF subclass)
├── generate_pdf_anon.py         # Anonymized version (no client name in PDF)
├── generate_charts.py           # matplotlib charts (600 DPI PNG, Agg backend)
├── analyze_potential.py         # CTR model + keyword potential table
└── generate_decision_matrix.py  # Multi-sheet Excel with openpyxl
```

### Starting a New Script from Scratch

When generating a report for a new client, just ask Claude Code:

```
"Write a potential analysis PDF script for [client domain],
use the CI patterns from /ci-setup-guide."
```

Claude will use the color constants, font registration, and layout rules from this guide to generate a ready-to-run `generate_pdf.py` — no boilerplate needed.

### Reference Docs

- `SEO projects/best_practices.md` — CI colors, page break safety, image compression patterns
- `SEO projects/seo_framework.md` — data pipeline, CTR model, deliverable types
