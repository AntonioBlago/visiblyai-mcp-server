Hier ist eine anonymisierte und bereinigte Version mit neutralen Platzhaltern, neuen Farbpaletten-Beispielen und ohne personen- oder markenbezogene Details:

````md
---
description: "Setup guide for brand identity, fonts, logos, colors, report preferences — plus Python and Playwright installation"
---

# /brand-setup-guide

Complete setup guide for generating brand-compliant reports and tools: brand identity reference, font setup, logo paths, color constants, report preferences, Python environment, and Playwright installation.

## Brand Identity — <brand_name>

> **Path setup:** Place your font, logo, and image assets in a folder and set `ASSETS_DIR` once.  
> Recommended location: `~/.config/assets/`  
> On Windows: `C:\Users\<user>\.config\assets\`  
> On Mac/Linux: `~/.config/assets/`

### Colors

```python
# RGB tuples — use for PDF (fpdf2), matplotlib charts
PRIMARY = (34, 102, 170)          # #2266AA — primary brand color
SECONDARY = (98, 163, 217)        # #62A3D9 — secondary brand color
HIGHLIGHT = (242, 153, 74)        # #F2994A — accent
DARK = (24, 32, 44)               # #18202C — headings / dark elements
DEEPEST_DARK = (15, 18, 24)       # #0F1218 — cover backgrounds
NEAR_BLACK = (28, 28, 28)         # #1C1C1C — body text
SUCCESS = (39, 174, 96)           # #27AE60 — positive
WARNING = (230, 126, 34)          # #E67E22 — warning
DANGER = (192, 57, 43)            # #C0392B — critical
LIGHT_BG = (247, 249, 252)        # #F7F9FC — alternating rows / panels
WHITE = (255, 255, 255)

# Hex strings — use for Excel (openpyxl), HTML
PRIMARY_HEX = '2266AA'
SECONDARY_HEX = '62A3D9'
HIGHLIGHT_HEX = 'F2994A'
DARK_HEX = '18202C'
SUCCESS_HEX = '27AE60'
WARNING_HEX = 'E67E22'
DANGER_HEX = 'C0392B'
LIGHT_BG_HEX = 'F7F9FC'
````

### Fonts

**Paths:**

```python
import os

# Set ASSETS_DIR to wherever you stored the assets folder.
ASSETS_DIR = os.environ.get("REPORT_ASSETS_DIR", os.path.expanduser("~/.config/assets"))

# Subfolders:
FONT_DIR   = os.path.join(ASSETS_DIR, "fonts")
IMAGE_DIR  = os.path.join(ASSETS_DIR, "images")
LOGO_PATH  = os.path.join(IMAGE_DIR, "logo.png")
PHOTO_PATH = os.path.join(IMAGE_DIR, "profile-photo.jpg")
```

**Available font files (place in `FONT_DIR`):**

* `Heading-Regular.ttf`
* `Heading-SemiBold.ttf`
* `Heading-Bold.ttf`
* `Heading-Italic.ttf`
* `Body-Regular.ttf`
* `Body-SemiBold.ttf`
* `Body-Bold.ttf`
* `Body-Italic.ttf`

**fpdf2 registration:**

```python
from fpdf import FPDF

pdf.add_font('Heading', '',   os.path.join(FONT_DIR, 'Heading-Regular.ttf'), uni=True)
pdf.add_font('Heading', 'B',  os.path.join(FONT_DIR, 'Heading-Bold.ttf'),    uni=True)
pdf.add_font('Heading', 'I',  os.path.join(FONT_DIR, 'Heading-Italic.ttf'),  uni=True)
pdf.add_font('Body',    '',   os.path.join(FONT_DIR, 'Body-Regular.ttf'),    uni=True)
pdf.add_font('Body',    'B',  os.path.join(FONT_DIR, 'Body-Bold.ttf'),       uni=True)
pdf.add_font('Body',    'I',  os.path.join(FONT_DIR, 'Body-Italic.ttf'),     uni=True)
```

### Logos & Images

Place all brand assets in `IMAGE_DIR`:

```text
<ASSETS_DIR>/images/
├── logo.png
├── profile-photo.jpg
└── client-logos/
    └── example-client-logo.png
```

**Usage in PDF:**

```python
if os.path.exists(LOGO_PATH):
    pdf.image(LOGO_PATH, x=10, y=10, w=40)
```

## Report Standards

### PDF Layout (A4)

```text
Page 1:  Cover (dark background, accent bar, logo, title, client, date, contact)
Page 2:  Executive Summary or Table of Contents
Pages 3+: Content sections
Last:    Summary table + next steps + footer
```

**Design Rules:**

* Cover background: `DEEPEST_DARK`
* Content pages: `WHITE`
* Section titles: accent bar (3mm) + Heading Bold 14pt
* Table header: primary color background, white text
* Table rows: alternating `WHITE` and `LIGHT_BG`
* KPI boxes: success / warning / danger colors
* Info boxes: colored left bar + soft tinted background
* Body text: Body 9–10pt, `NEAR_BLACK`
* Captions: Body 8pt, muted gray

**Page break safety:**

```python
def ensure_space(self, needed_mm):
    if self.get_y() + needed_mm > 275:
        self.add_page()
        self._redraw_table_header()
```

### Excel Layout

```python
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

HEADER_FILL = PatternFill("solid", fgColor="2266AA")
HEADER_FONT = Font(color="FFFFFF", bold=True, name="Heading", size=10)
ALT_FILL = PatternFill("solid", fgColor="F7F9FC")
SUCCESS_FILL = PatternFill("solid", fgColor="27AE60")
DANGER_FILL = PatternFill("solid", fgColor="C0392B")
```

## Alternative Color Palettes

If a client has their own CI, define a palette class and swap it in.

```python
# Slate + Sky (clean corporate / tech consulting)
class SlateSkyPalette:
    PRIMARY    = (31, 41, 55)        # #1F2937
    ACCENT     = (59, 130, 246)      # #3B82F6
    SUCCESS    = (22, 163, 74)       # #16A34A
    DANGER     = (220, 38, 38)       # #DC2626
    ALT_BG     = (248, 250, 252)     # #F8FAFC
    TEXT       = (17, 24, 39)        # #111827
    TEXT_MUTED = (107, 114, 128)     # #6B7280

# Sand + Terracotta (editorial / premium / lifestyle)
class SandTerracottaPalette:
    PRIMARY    = (87, 58, 46)        # #573A2E
    ACCENT     = (201, 103, 72)      # #C96748
    SUCCESS    = (93, 138, 96)       # muted green
    DANGER     = (168, 58, 58)       # earthy red
    ALT_BG     = (250, 245, 239)     # warm sand
    TEXT       = (44, 34, 29)
    TEXT_MUTED = (124, 106, 96)

# Pine + Mint (health / sustainability / wellness)
class PineMintPalette:
    PRIMARY    = (26, 71, 66)        # #1A4742
    ACCENT     = (96, 176, 160)      # #60B0A0
    SUCCESS    = (72, 146, 84)       # green
    DANGER     = (176, 72, 72)       # muted red
    ALT_BG     = (242, 248, 246)     # fresh light bg
    TEXT       = (24, 39, 37)
    TEXT_MUTED = (102, 122, 118)

# Plum + Rose Gold (creative / boutique / modern luxury)
class PlumRosePalette:
    PRIMARY    = (74, 44, 82)        # deep plum
    ACCENT     = (196, 143, 133)     # rose gold
    SUCCESS    = (112, 153, 117)
    DANGER     = (170, 70, 76)
    ALT_BG     = (250, 246, 248)
    TEXT       = (38, 28, 40)
    TEXT_MUTED = (125, 108, 122)
```

**Hex equivalents for Excel:**

| Palette           | Style                   | Primary  | Accent   | Success  | Danger   |
| ----------------- | ----------------------- | -------- | -------- | -------- | -------- |
| Slate + Sky       | Corporate / tech        | `1F2937` | `3B82F6` | `16A34A` | `DC2626` |
| Sand + Terracotta | Editorial / premium     | `573A2E` | `C96748` | `5D8A60` | `A83A3A` |
| Pine + Mint       | Health / sustainability | `1A4742` | `60B0A0` | `489254` | `B04848` |
| Plum + Rose       | Creative / boutique     | `4A2C52` | `C48F85` | `709975` | `AA464C` |

## Alternative Fonts

Replace the `FONT_DIR` fonts with the client's brand fonts. The naming convention can stay consistent.

```python
# Example: Inter
pdf.add_font('Inter', '',  os.path.join(FONT_DIR, 'Inter-Regular.ttf'), uni=True)
pdf.add_font('Inter', 'B', os.path.join(FONT_DIR, 'Inter-Bold.ttf'),    uni=True)

# Example: Merriweather + Source Sans
pdf.add_font('Merriweather', '',  os.path.join(FONT_DIR, 'Merriweather-Regular.ttf'), uni=True)
pdf.add_font('Merriweather', 'B', os.path.join(FONT_DIR, 'Merriweather-Bold.ttf'),    uni=True)
pdf.add_font('SourceSans',   '',  os.path.join(FONT_DIR, 'SourceSans-Regular.ttf'),   uni=True)
pdf.add_font('SourceSans',   'B', os.path.join(FONT_DIR, 'SourceSans-Bold.ttf'),      uni=True)
```

**Font pairings by report type:**

| Report Style | Heading Font | Body Font   | Use For                |
| ------------ | ------------ | ----------- | ---------------------- |
| Default      | Heading      | Body        | General client reports |
| Corporate    | Montserrat   | Inter       | B2B / consulting       |
| Editorial    | Merriweather | Source Sans | Agency / strategy      |
| Technical    | Roboto       | Roboto Mono | Product / engineering  |
| Minimal      | Inter        | Inter       | SaaS / startup         |

### Contact Information (Footer Placeholder)

```text
<company_name>
<street_address>
<postal_code> <city>
Tel: <phone_number>
E-Mail: <email_address>
Web: <website_url>
```

### Language Rules

* Use one consistent tone throughout the report
* Use proper UTF-8 characters: ä, ö, ü, ß
* Use the report language required by the client
* Keep UI labels, headings, and tables linguistically consistent

## Project Folder Structure

```text
<PROJECTS_DIR>/<client-name>/
├── Keywords/
├── Data/
├── Reports/
├── Scripts/
├── Images/
└── Archive/
```

**Create on new project:**

```python
import os

PROJECTS_DIR = os.environ.get(
    "PROJECTS_DIR",
    os.path.expanduser("~/projects")
)

client = "client-name"
base = os.path.join(PROJECTS_DIR, client)
for folder in ["Keywords", "Data", "Reports", "Scripts", "Images", "Archive"]:
    os.makedirs(os.path.join(base, folder), exist_ok=True)
```

## Python Environment Setup

### Required for Report Generation

```bash
python --version
# Requires: Python 3.10+

pip install fpdf2 Pillow openpyxl pandas matplotlib requests
pip install sshtunnel pymysql
pip install numpy scipy

python -c "from fpdf import FPDF; from PIL import Image; import openpyxl; import pandas; print('OK')"
```

### Chart Generation

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

output_path = os.path.join(PROJECTS_DIR, "<client-name>", "Images", "chart.png")
plt.savefig(output_path, dpi=600, bbox_inches='tight', transparent=True)
```

## Playwright Setup

### Installation

```bash
node --version  # Requires: 18+
npm --version

npm install -g @playwright/mcp
npx playwright install chromium
npx playwright --version
```

### Configuration

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

### Available Playwright Tools

| Tool                       | Use Case            |
| -------------------------- | ------------------- |
| `browser_navigate`         | Open a URL          |
| `browser_snapshot`         | Read page structure |
| `browser_take_screenshot`  | Capture screenshot  |
| `browser_click`            | Click element       |
| `browser_fill_form`        | Fill fields         |
| `browser_type`             | Type text           |
| `browser_select_option`    | Select dropdown     |
| `browser_evaluate`         | Run JavaScript      |
| `browser_network_requests` | Inspect requests    |

## Initial Setup Workflow

On a new project, gather the basic inputs first:

```text
Step 1: Create project folder
Step 2: Add fonts, logos, and placeholder assets
Step 3: Prepare baseline data sources
Step 4: Generate first charts / exports
Step 5: Build summary report
```

## Quick Reference Checklist

Before starting any report:

* [ ] Python environment is active
* [ ] `ASSETS_DIR` is set
* [ ] Font files exist
* [ ] Client folder structure exists
* [ ] Logo file is available
* [ ] `matplotlib` uses `Agg`
* [ ] Output paths use `os.makedirs(..., exist_ok=True)`

## Python Report Scripts

The report scripts run locally inside each client project folder.

### Where They Live

```text
<PROJECTS_DIR>/<client-name>/Scripts/
├── generate_pdf.py
├── generate_pdf_anon.py
├── generate_charts.py
├── analyze_data.py
└── generate_excel.py
```

### Starting a New Script from Scratch

```text
"Write a PDF report script for [client-name],
use the patterns from /brand-setup-guide."
```

### Reference Docs

* `project_docs/best_practices.md`
* `project_docs/report_framework.md`

