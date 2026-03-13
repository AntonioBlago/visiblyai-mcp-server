# Visibly AI MCP — Installation Guide

**MCP Server:** `visiblyai-mcp-server`
**Support:** [antonioblago.com](https://www.antonioblago.com) · info@antonioblago.com

---

## What is an MCP?

MCP (Model Context Protocol) connects external tools directly into Claude. Once installed, you can ask Claude things like:

> "Check the SEO of example.com"
> "What keywords is my competitor ranking for?"
> "Run an OnPage audit on this page for the keyword 'seo tool'"

Claude calls the tools automatically — no copy-pasting, no switching tabs.

---

## Step 1 — Install Claude Code

Claude Code is the CLI for Claude. Open a terminal and run:

```bash
npm install -g @anthropic-ai/claude-code
```

> **Requires Node.js 18+.** Download from [nodejs.org](https://nodejs.org) if you don't have it.

Verify the install:

```bash
claude --version
```

---

## Step 2 — Install Python (if needed)

Some MCP options (local install) require Python 3.10 or higher.

**Download:** [python.org/downloads](https://www.python.org/downloads/)

During installation on Windows, check **"Add Python to PATH"**.

Verify:

```bash
python --version
# or
python3 --version
```

---

## Step 3 — Add the Visibly AI MCP

Choose one option. **Option A is recommended** — no Python or local install needed.

---

### Option A — Remote Server (zero install, recommended)

No Python needed. Claude connects directly to the Visibly AI server.

**With API key (all tools):**

```bash
claude mcp add --transport http \
  --header "Authorization: Bearer YOUR_API_KEY" \
  visiblyai https://mcp.visibly-ai.com/mcp
```

**Without API key (6 free tools only):**

```bash
claude mcp add --transport http visiblyai https://mcp.visibly-ai.com/mcp
```

---

### Option B — uvx (local, no install needed)

Requires Python 3.10+ with `uv` installed (`pip install uv`).

```bash
claude mcp add --transport stdio \
  --env VISIBLYAI_API_KEY=YOUR_API_KEY \
  visiblyai -- uvx visiblyai-mcp-server
```

---

### Option C — pip install (local)

```bash
pip install visiblyai-mcp-server

claude mcp add --transport stdio \
  --env VISIBLYAI_API_KEY=YOUR_API_KEY \
  visiblyai -- visiblyai-mcp-server
```

---

## Step 4 — Get an API Key

Free tools work without a key. Paid tools (traffic, keywords, backlinks, audits) require an API key with credits.

1. Register at [antonioblago.com/register](https://www.antonioblago.com/register)
2. Go to **Account → API Keys**
3. Create a key (starts with `lc_`)
4. Replace `YOUR_API_KEY` in the command above

---

## Step 5 — Restart Claude Code

After adding the MCP, restart Claude Code:

```bash
claude
```

Verify the MCP is connected:

```bash
/mcp
```

You should see `visiblyai` listed as connected.

---

## Step 6 — Optional: Add Playwright MCP

Playwright adds a browser automation tool so Claude can take screenshots, fill forms, and interact with web pages directly.

**Install:**

```bash
npm install -g @playwright/mcp
```

**Add to Claude:**

```bash
claude mcp add --transport stdio playwright -- npx @playwright/mcp
```

**Install browsers (first time only):**

```bash
npx playwright install chromium
```

**Verify:**

```bash
/mcp
# Should show both "visiblyai" and "playwright"
```

---

## Available Tools

### Free (no API key needed) — 8 tools

| Tool | What it does |
|------|-------------|
| `classify_keywords_simple` | Brand/generic/intent classification via local regex (DE+EN, offline) |
| `seo_checklist` | Blog, ecommerce, local, discover, backlink checklists |
| `seo_guidance` | Title tags, EEAT, Core Web Vitals, Schema best practices |
| `get_google_guidelines` | Official Google Search guidelines by category |
| `get_skill` | SEO workflow guides: audit, keyword research, competitor analysis |
| `analyze_url_structure` | URL SEO-friendliness check |
| `get_account_info` | Your credit balance and tier |
| `list_locations` | Available countries for paid tools |

### Paid (credits required) — 13 tools

| Tool | Credits | What it does |
|------|---------|-------------|
| `classify_keywords_advanced` | varies | Keyword classification with DataForSEO Search Intent API + regex |
| `get_traffic_snapshot` | varies | Organic + paid traffic for any domain |
| `get_historical_traffic` | varies | Traffic trends up to 5 years |
| `get_keywords` | varies | Top ranking keywords with volume + position |
| `get_competitors` | varies | Competitor domains by keyword overlap |
| `get_backlinks` | varies | Backlink profile with Domain Rating |
| `get_referring_domains` | varies | Referring domains with authority |
| `validate_keywords` | varies | Search volume, competition, CPC |
| `crawl_website` | 15–60 | Live crawl + optional OnPage audit |
| `onpage_analysis` | 15 | 24-point OnPage SEO audit |
| `check_links` | 20 | Broken link detection |
| `seo_agent` | varies | Specialized SEO agents: analyst, strategist, copywriter, consultant |
| `seo_workflow` | 150–200 | Full SEO audit + keyword performance report |
| `query_knowledge_base` | 2 | RAG search over SEO knowledge base and Google guidelines |

### Google & Projects (API key, 0 credits)

| Tool | What it does |
|------|-------------|
| `list_projects` | Your EEAT projects with scores |
| `get_project` | Project details + competitors + Google connections |
| `get_google_connections` | Connected GSC/GA4 properties |
| `query_search_console` | GSC: clicks, impressions, CTR, position |
| `query_analytics` | GA4: traffic overview, top pages, sources |

---

## Example Prompts

Once the MCP is active, ask Claude naturally:

```
Analyze the SEO of visibly-ai.com

What are the top keywords for example.com in Germany?

Run an OnPage audit on https://example.com/page for the keyword "seo tool"

Check for broken links on https://example.com

Classify these keywords: "seo agentur berlin", "was ist seo", "seo tool kaufen"

Show me my GSC data for the last 30 days for project ID 5

What are the backlinks for my competitor domain?

Run a full SEO performance audit for example.com (project_id: 12)

What does Google say about EEAT and helpful content?

Search the knowledge base for structured data best practices
```

---

## Troubleshooting

### MCP not showing in `/mcp`

1. Confirm the `claude mcp add` command ran without errors
2. Restart Claude Code completely
3. Run `/mcp` again

### "Tool not found" error

The MCP is connected but the tool name is wrong. Use `/mcp` to see available tools, or ask Claude: *"What MCP tools do you have?"*

### API key errors (401 / unauthorized)

- Check the key starts with `lc_`
- For remote (Option A): make sure the header is `Authorization: Bearer lc_yourkey`
- For local (Options B/C): make sure `VISIBLYAI_API_KEY=lc_yourkey` is set

### "Not enough credits"

Top up at [antonioblago.com/credits](https://www.antonioblago.com/credits/dashboard) or upgrade your plan.

### Python not found (Windows)

Re-install Python from [python.org](https://www.python.org/downloads/) and check **"Add Python to PATH"** during setup. Then restart your terminal.

### Playwright browsers not installed

```bash
npx playwright install chromium
```

---

## Configuration File Location

Claude Code stores MCP settings in:

| OS | Path |
|----|------|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

You can also edit the config manually. Example with both MCPs:

```json
{
  "mcpServers": {
    "visiblyai": {
      "type": "http",
      "url": "https://mcp.visibly-ai.com/mcp",
      "headers": {
        "Authorization": "Bearer lc_your_key"
      }
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["@playwright/mcp"]
    }
  }
}
```

---

## Subscription Plans

| Plan | Credits/month | Projects | Price |
|------|---------------|----------|-------|
| Free | 0 | 1 | Free |
| Standard | 2,500 | 3 | €39/mo |
| Pro | 10,000 | 10 | €119/mo |
| Agency | 50,000 | 50 | €399/mo |

> Introductory prices — limited time.

Manage your subscription at [antonioblago.com/credits](https://www.antonioblago.com/credits/dashboard)

---

## Help & Support

| Channel | Link |
|---------|------|
| Support | [antonioblago.com](https://www.antonioblago.com) |
| Email | info@antonioblago.com |
| Register | [antonioblago.com/register](https://www.antonioblago.com/register) |
| Credits | [antonioblago.com/credits](https://www.antonioblago.com/credits/dashboard) |
| API Keys | Account → API Keys after login |

---

*Visibly AI — Neuro-SEO System® · Antonio Blago · Koblenz, Germany*
