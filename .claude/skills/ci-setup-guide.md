---
description: "Setup guide for CI brand identity, fonts, logos, colors, report preferences — plus Python and MCP Playwright installation"
---

# /ci-setup-guide

Complete setup guide for generating CI-compliant reports and tools: brand identity reference, font setup, logo paths, color constants, report preferences, Python environment, and MCP Playwright installation.

## Brand Identity — Antonio Blago

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
FONT_DIR = r'C:\Users\anton\OneDrive\Mabya\Dokumente\Claude\fonts'
# Also available at:
# r'C:\Users\anton\Downloads\Antonio Blago\Antonio Blago\fonts'
```

**Available files:**
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

pdf.add_font('Montserrat', '',   f'{FONT_DIR}/Montserrat-Regular.ttf',   uni=True)
pdf.add_font('Montserrat', 'B',  f'{FONT_DIR}/Montserrat-Bold.ttf',      uni=True)
pdf.add_font('Montserrat', 'I',  f'{FONT_DIR}/Montserrat-Italic.ttf',    uni=True)
pdf.add_font('Montserrat', 'BI', f'{FONT_DIR}/Montserrat-BoldItalic.ttf',uni=True)
pdf.add_font('Mulish',     '',   f'{FONT_DIR}/Mulish-Regular.ttf',       uni=True)
pdf.add_font('Mulish',     'B',  f'{FONT_DIR}/Mulish-Bold.ttf',          uni=True)
pdf.add_font('Mulish',     'I',  f'{FONT_DIR}/Mulish-Italic.ttf',        uni=True)
```

### Logos & Images

**Profile photo:**
```
C:\Users\anton\OneDrive\Mabya\Dokumente\Claude\images\photo.jpg
C:\Users\anton\OneDrive\Mabya\Dokumente\Claude\images\photo.png
```

**Brand logo:**
```
C:\Users\anton\OneDrive\Mabya\Dokumente\Claude\images\logo.png
```

**Client logos:**
```
C:\Users\anton\OneDrive\Mabya\Dokumente\Claude\images\logos\
├── Titus-Logo.png
├── Purelei-Logo.png
├── GFU-Cyrus-Logo.png
├── Lotto-Niedersachsen-Logo.png
├── Merzbschwanen-Logo.png
├── pelveasy-logo.png
└── rabea-kiess-logo.png
```

**Charts (reference outputs):**
```
C:\Users\anton\OneDrive\Mabya\Dokumente\Claude\images\
├── chart_gsc_monthly.png
├── chart_competitor_traffic.png
├── chart_ranking_dist.png
├── chart_traffic_comparison.png
└── chart_international.png
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
C:\Users\anton\OneDrive\Mabya\Dokumente\Claude\SEO projects\[client-domain]\
├── Keywords\       # Excel/CSV keyword data, SV, positions
├── Data\           # GSC JSON, GA4 exports, crawl data
├── Reports\        # Generated PDFs, Excel deliverables
├── Scripts\        # Python analysis & generation scripts
├── Images\         # Charts, screenshots, logos
└── Archive\        # Previous proposals, old versions
```

**Create on new project:**
```python
import os
client = "example.com"
base = rf"C:\Users\anton\OneDrive\Mabya\Dokumente\Claude\SEO projects\{client}"
for folder in ["Keywords", "Data", "Reports", "Scripts", "Images", "Archive"]:
    os.makedirs(f"{base}\\{folder}", exist_ok=True)
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

### Bikefitting Project (Flask App)

```bash
# Use project virtualenv:
C:\Users\anton\PycharmProjects\Bikefitting_Project\webapp312\Scripts\python.exe

# Run tests:
C:\Users\anton\PycharmProjects\Bikefitting_Project\webapp312\Scripts\pytest.exe scripts/Testing/ \
  --ignore=scripts/Testing/quick_test.py \
  --ignore=scripts/Testing/test_blog_access.py \
  --ignore=scripts/Testing/test_eeat_classifier_integration.py \
  --ignore=scripts/Testing/test_eeat_page_embeddings.py
```

### Chart Generation

```python
import matplotlib
matplotlib.use('Agg')  # CRITICAL: headless mode for server/script use
import matplotlib.pyplot as plt

# Always save at 600 DPI for print-quality PDFs:
plt.savefig('chart.png', dpi=600, bbox_inches='tight', transparent=True)
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

### Visibly AI MCP Server (mcp.visibly-ai.com)

The Visibly AI MCP server is deployed separately. For development:

```bash
# Install from PyPI:
pip install visiblyai-mcp-server

# Or run locally from source:
cd C:\Users\anton\PycharmProjects\visiblyai-mcp-server
pip install -e .
python -m visiblyai_mcp.server

# Configure in Claude Code:
# Add to MCP settings with API key from visibly-ai.com/account
```

**Three-system architecture:**
- `www.antonioblago.com` — Main web app (Flask, PythonAnywhere)
- `visibly-ai.com` — Landing page + auth (separate Visibly app)
- `mcp.visibly-ai.com` — MCP server (FastAPI, PythonAnywhere)

## Quick Reference Checklist

Before starting any report:

- [ ] Python env active with fpdf2, Pillow, openpyxl, pandas, matplotlib
- [ ] Font files exist at `FONT_DIR` path (check with `os.path.exists`)
- [ ] Client folder created with standard structure
- [ ] Logo file exists for client (or use default `logo.png`)
- [ ] GSC connected in Visibly AI project
- [ ] matplotlib using `Agg` backend
- [ ] Output path uses `os.makedirs(path, exist_ok=True)`

## Implementation References

- PDF generation: `paroc.com/generate_pdf.py`, `paroc.com/generate_pdf_anon.py`
- Chart generation: `paroc.com/generate_charts.py`
- Potential analysis: `paroc.com/analyze_potential.py`
- Excel decision matrix: `x-bonic.com/generate_xbionic_decision_full.py`
- Best practices: `SEO projects/best_practices.md`
- Framework overview: `SEO projects/seo_framework.md`
