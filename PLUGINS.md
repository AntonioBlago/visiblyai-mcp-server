# Visibly AI plugins

Write an article with Claude Code, Codex or GitHub Copilot CLI, measure its real
Visibly NSS score, improve it, and save the finished draft to the Visibly editor.
The agent uses its own model for writing. Visibly provides context, scoring and storage.

[NSS explained: what the Neuro-SEO Score measures](https://www.visibly-ai.com/nss-score)
([Deutsch](https://www.visibly-ai.com/de/nss-score)) describes the assessment areas,
transparent feedback and limits without publishing the scoring implementation.
Its methodological foundation is Antonio Blago's
[Neuro-SEO System®](https://www.antonioblago.com/de/neuro-seo-system/) (German overview).

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
Choose [macOS/Linux](#macos-and-linux) or [Windows](#windows-saved-key-versus-running-client)
for persistent setup. For a quick connection, set it in a standalone terminal
and start your installed client (`codex` or `claude`) from that **same terminal**:

```bash
export VISIBLYAI_API_KEY='YOUR_VISIBLY_API_KEY'
codex
```

PowerShell:

```powershell
$env:VISIBLYAI_API_KEY = 'YOUR_VISIBLY_API_KEY'
codex
```

These examples start Codex CLI; use `claude` for Claude Code. Copilot CLI also
needs its [separate MCP connection](#github-copilot-cli). Install the appropriate
plugin using the client section below, then run the [connection check](#verify-the-connection).

On **every OS**, the key must reach the process running MCP. A new chat does not
refresh a running application's environment. Setting a variable in an integrated
terminal does not update its parent editor. The plugins do not automatically load
project `.env` files. Keep the key out of plugin files, Git and chat messages.

### macOS and Linux

The following commands work in **zsh and bash**. If you normally use fish, start
`bash` for these steps and launch the client from that shell.

For persistence, use your secret manager or create a private environment file
outside your projects. Create the file, restrict access, then open it in an editor:

```bash
mkdir -p "$HOME/.config/visibly"
chmod 700 "$HOME/.config/visibly"
touch "$HOME/.config/visibly/env"
chmod 600 "$HOME/.config/visibly/env"
nano "$HOME/.config/visibly/env"
```

Use your preferred editor if `nano` is unavailable. Add this line with your own
key, then save and close the editor (this also keeps the key out of shell history):

```bash
export VISIBLYAI_API_KEY='YOUR_VISIBLY_API_KEY'
```

Load that file explicitly in the terminal from which you will start the client:

```bash
. "$HOME/.config/visibly/env"
```

For future interactive terminals, add the following line once to `~/.zshrc`
(zsh, normally macOS) or `~/.bashrc` (interactive non-login bash, common on Linux):

```bash
[ ! -f "$HOME/.config/visibly/env" ] || . "$HOME/.config/visibly/env"
```

Bash login shells read a login profile instead; put the same line in the profile
your setup uses (usually `~/.bash_profile` or `~/.profile`), or load the private
file explicitly. Do not replace an existing profile. Shell startup files do not
guarantee that desktop apps started through Finder, Dock or a Linux app menu receive
the key. The explicit load-and-launch path above avoids that dependency.

Check whether a child process receives the exported key, without printing it:

```bash
if sh -c 'test -n "${VISIBLYAI_API_KEY:-}"'; then
    printf '%s\n' 'Visibly key available to child processes'
else
    printf '%s\n' 'Visibly key missing: load the private environment file first'
fi
```

- **Terminal clients:** run `codex` or `claude` from that same terminal after
  loading the key. Start a new session if the client was already running.
- **VS Code on macOS:** save your work and quit VS Code with **Cmd+Q**; closing a
  window alone may leave the application running. Load the key in Terminal, then
  run `code .` from your project directory. If `code` is unavailable, use VS Code's
  Command Palette → **Shell Command: Install 'code' command in PATH** first.
- **VS Code on Linux:** save your work and fully exit all VS Code instances.
  Load the key in a standalone terminal, then run `code .` from your project.
- **Other desktop apps:** use the app's supported launcher that inherits the
  prepared shell environment, or its documented credential setup. Reopening an
  app from the Dock or app menu alone does not establish environment inheritance.

After relaunching the editor, start a new agent chat and verify the connection.
For WSL, SSH or containers, configure the key in the environment where the MCP
client actually runs; a host environment variable is not automatically available there.

References: [Apple's shell environment guidance](https://support.apple.com/guide/terminal/apd382cc5fa-4f58-4449-b20a-41c53c006f8f/mac),
[Bash startup files](https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html),
[VS Code process environment](https://code.visualstudio.com/docs/terminal/advanced#_process-environment).

### Windows: saved key versus running client

Windows stores user environment variables separately from the environment of each
running process. A client inherits its environment when it starts. Saving a key
in Windows does not update an already running VS Code or Codex process. Likewise,
setting `$env:VISIBLYAI_API_KEY` in VS Code's integrated terminal affects that
terminal and its children, not the parent editor or its Codex extension.

For persistent setup, open **Edit environment variables for your account** in
Windows and add `VISIBLYAI_API_KEY` under **User variables** with your Visibly key.
The plugin reads this variable; it does not automatically load a project's `.env`
file or copy the saved Windows value into a running client.

Check presence without printing the key:

```powershell
[pscustomobject]@{
    SavedForUser = [bool][Environment]::GetEnvironmentVariable('VISIBLYAI_API_KEY', 'User')
    CurrentProcess = [bool]$env:VISIBLYAI_API_KEY
}
```

`SavedForUser = True` with `CurrentProcess = False` means the key is stored but this
PowerShell process has not loaded it. This checks the shell, not the environment
of a separately running Codex process. To load the saved key into this shell:

```powershell
$env:VISIBLYAI_API_KEY = [Environment]::GetEnvironmentVariable('VISIBLYAI_API_KEY', 'User')
if (-not $env:VISIBLYAI_API_KEY) { throw 'Save VISIBLYAI_API_KEY in Windows User variables first.' }
```

Then start the intended client from that same shell:

- **Codex CLI:** run `codex` and start a new session.
- **Codex in VS Code:** save your work and fully exit **all** VS Code windows first.
  Use a standalone PowerShell window, load the saved key as above, then run
  `code .` from your project directory. Start a new Codex chat in the reopened editor.
  A new chat, **Reload Window**, or an additional VS Code window can reuse the old
  process environment and is not a substitute for fully restarting the editor.
- **Other desktop clients:** fully quit the application and relaunch it with the
  key available in its launch environment, then start a new session.

Background: [Microsoft's environment-variable scopes and inheritance](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables).

### Verify the connection

After installing the plugin and starting the client with the key, ask:

> Call Visibly's list_projects through MCP and show the projects I can access.
> Report any connection or permission error. Do not start an analysis or modify content.

This authenticated read costs 0 Visibly credits. A successful empty list means the
connection works but no projects are visible to this key. Seeing the installed
skill or a tool list alone does not establish authenticated project access.

| Result | Next step |
| --- | --- |
| Visibly tools missing or environment variable missing | Check the key in the actual client's launch environment, verify the plugin is enabled, then fully restart the client and open a new chat. |
| Authentication rejected (401) | Check whether the configured key is current; replace a revoked key in the private store and reload/restart the client. |
| Permission rejected (403) or expected project absent | Check the key's scopes, allowed projects and your project membership in Visibly. |
| Network/TLS/timeout error | Check connectivity to `https://mcp.visibly-ai.com/mcp` and the client's proxy settings. |

Presence checks verify availability, not whether a key is valid. Report errors
without including the key. For Copilot's saved Authorization header, update its
MCP configuration after rotating a key; changing the shell variable alone does
not replace the header already stored by Copilot.

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

Start Codex with the key available, then open a new session. If VS Code or the
desktop client was already running when you saved the key, fully restart that
application first; a new chat alone does not refresh its environment. Follow the
[macOS/Linux setup](#macos-and-linux) or
[Windows setup](#windows-saved-key-versus-running-client), then
[verify the connection](#verify-the-connection).
Ask Codex to use `content-nss-optimize`.
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
