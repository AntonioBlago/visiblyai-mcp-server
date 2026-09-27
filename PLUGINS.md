# Visibly AI plugins

Write an article with Claude Code, Codex or GitHub Copilot CLI, measure its real
Visibly NSS score, improve it, and save the finished draft to the Visibly editor.
The agent uses its own model for writing. Visibly provides context, scoring and storage.

## Downloads

Plugin release **1.0.1** works with the current remote MCP server (**0.13.0**, 84 tools).
An API key and the appropriate project permissions are required for account data and writing drafts.

| Client | Plugin ZIP | Connection setup |
| --- | --- | --- |
| Claude Code | [visibly-claude-1.0.1.zip](https://github.com/AntonioBlago/visiblyai-mcp-server/releases/download/plugins-v1.0.1/visibly-claude-1.0.1.zip) | Bundled remote MCP configuration; environment variable |
| OpenAI Codex | [visibly-codex-1.0.1.zip](https://github.com/AntonioBlago/visiblyai-mcp-server/releases/download/plugins-v1.0.1/visibly-codex-1.0.1.zip) | Bundled remote MCP configuration; environment variable |
| GitHub Copilot CLI | [visibly-copilot-1.0.1.zip](https://github.com/AntonioBlago/visiblyai-mcp-server/releases/download/plugins-v1.0.1/visibly-copilot-1.0.1.zip) | Install skill plugin, then add the MCP connection below |

[Release notes and SHA-256 checksums](https://github.com/AntonioBlago/visiblyai-mcp-server/releases/tag/plugins-v1.0.1).
Each ZIP contains a plugin root: extract it into a folder named after the plugin.
The marketplace installation below downloads the files for you.

## API key

Create your own Visibly API key in [Visibly settings](https://app.visibly-ai.com/settings).
Make it available as `VISIBLYAI_API_KEY` in the environment of the client process.
For example, set it for the current terminal before starting the client:

```bash
export VISIBLYAI_API_KEY='YOUR_VISIBLY_API_KEY'
```

PowerShell:

```powershell
$env:VISIBLYAI_API_KEY = 'YOUR_VISIBLY_API_KEY'
```

Use your secret manager or a private local environment file for persistent setup;
never commit the real key. A GUI client must inherit the variable too; a value set
in a terminal does not change the environment of an already running application.

## Claude Code

```bash
claude plugin marketplace add AntonioBlago/visiblyai-mcp-server
claude plugin install visibly-claude@visibly
```

Start a new Claude Code session from the terminal containing the key. Check `/mcp`
and invoke `/visibly-claude:content-nss-optimize`, or ask for the workflow in plain language.
For a downloaded ZIP, extract it and use `claude --plugin-dir ./visibly-claude`.
This is a Claude Code plugin; it is not a Claude Desktop extension or claude.ai store listing.

## OpenAI Codex

```bash
codex plugin marketplace add AntonioBlago/visiblyai-mcp-server
codex plugin add visibly-codex@visibly
```

Start a new session with the key available. Ask Codex to use `content-nss-optimize`.
The Codex marketplace lives at `.agents/plugins/marketplace.json`; Claude's catalog
uses its own format in `.claude-plugin/marketplace.json`.
For an offline/local installation, clone the repository and pass the clone's root
to `codex plugin marketplace add`, then run the same `plugin add` command.

The Codex ZIP is also a plugin bundle for OpenAI agent environments that accept
`.codex-plugin/plugin.json`; configure `VISIBLYAI_API_KEY` in that environment.
See the [OpenAI Agents plugin documentation](https://developers.openai.com/api/docs/guides/agents-api/tools/plugins).

## GitHub Copilot CLI

```bash
copilot plugin marketplace add AntonioBlago/visiblyai-mcp-server
copilot plugin install visibly-copilot@visibly
```

Connect the MCP once using Copilot's supported local authentication setup:

```bash
copilot mcp add --transport http --header "Authorization: Bearer $VISIBLYAI_API_KEY" visiblyai https://mcp.visibly-ai.com/mcp
```

PowerShell uses `$env:VISIBLYAI_API_KEY` instead:

```powershell
copilot mcp add --transport http --header "Authorization: Bearer $env:VISIBLYAI_API_KEY" visiblyai https://mcp.visibly-ai.com/mcp
```

Alternatively, use `/mcp add` inside Copilot, choose HTTP, enter the same URL and
an `Authorization` header with `Bearer ` followed by your key. Copilot stores this
in your private user configuration. The shared plugin contains the skill only,
so credentials never need to be inserted into the plugin or its marketplace cache.
Restart Copilot and ask it to use `content-nss-optimize`.

For the downloaded ZIP, extract it and run `copilot --plugin-dir ./visibly-copilot`;
the separate MCP setup is still required.
This package targets Copilot CLI. VS Code uses its own MCP configuration:
run **MCP: Add Server**, select HTTP, and add `https://mcp.visibly-ai.com/mcp`
with your authentication header. Copy the canonical
[`skills/content-nss-optimize`](skills/content-nss-optimize) directory into your
workspace's `.github/skills/` directory if you also want the workflow in VS Code.

## First article

> Use content-nss-optimize for my selected Visibly project and ready content query.
> Write the article with your own model, optimize it toward NSS 80, save it as a draft,
> and give me the editor link. Do not use paid Visibly text generation.

- Reuses the actual briefing, brand context, terms, headings and available links.
- Calls `score_text` after each revision and reads the actual NSS.
- Stops at the requested target (70 or 80), five revisions, or two rounds without
  improvement. It retains the best draft and reports the measured result; a score
  target is not guaranteed.
- Saves a draft, reads and scores the stored text again, and returns an editor link.
  Opening a browser tab depends on the client and the user's request.
- Existing context, NSS scoring and draft saving use **0 Visibly credits**.
  Agent tokens/subscriptions still cost money. New analysis is separately paid and
  requires authorization. This workflow does not invoke Visibly's paid text generator
  or publish an article as a side effect.

## Marketplace availability

This repository is a **public, self-hosted plugin marketplace**. Anyone can add it
using the commands above or download a release. No Python installation is needed
for the remote connection. The [PyPI package](https://pypi.org/project/visiblyai-mcp-server/)
remains available for local stdio clients and has its own version/release cycle.

These packages are not listed in the providers' curated stores. Official directory
publication requires a separate submission/review. In particular, an authenticated
ChatGPT integration needs an OAuth-compatible login; these API-key packages do not
implement that login. See [OpenAI authentication](https://developers.openai.com/plugins/build/auth)
and [submission requirements](https://developers.openai.com/plugins/deploy/submission).

Client references: [Claude plugins](https://code.claude.com/docs/en/plugins-reference),
[Copilot plugins](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference),
[Copilot MCP setup](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers).

## Maintaining the bundles

Maintainers and agents: read [AGENTS.md](AGENTS.md) and the
[cross-repository handoff](docs/PLUGIN_MCP_HANDOFF.md) for current ownership,
release order, CMS handoff semantics, verified status and marketing updates.

Edit the canonical skill under `skills/content-nss-optimize/`, then run:

```bash
python scripts/build_plugins.py --sync-skills
```

Without `--sync-skills`, the build fails if a bundled skill differs from the canonical
source. ZIPs use an explicit file allowlist, fixed timestamps and SHA-256 checksums.
Plugin releases use `plugins-v*` tags, independently of Python package tags.
