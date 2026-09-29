# Visibly AI for Claude Code

Version 1.0.2. Includes the Visibly MCP connection and the content-nss-optimize skill.

[What the NSS measures](https://www.visibly-ai.com/nss-score) ·
[NSS auf Deutsch erklärt](https://www.visibly-ai.com/de/nss-score)

Methodological foundation: Antonio Blago's [Neuro-SEO-System®](https://www.antonioblago.com/de/neuro-seo-system/) (German overview).

[Installation, API-key setup, costs and usage](https://github.com/AntonioBlago/visiblyai-mcp-server/blob/master/PLUGINS.md)

On Windows, macOS and Linux, load `VISIBLYAI_API_KEY` before starting `claude`
from the same terminal. For an editor extension, fully quit the editor and
relaunch it from the prepared terminal; setting the key in its integrated terminal
does not update the parent editor. Persistent setup differs by OS:
[macOS/Linux](https://github.com/AntonioBlago/visiblyai-mcp-server/blob/master/PLUGINS.md#macos-and-linux),
[Windows](https://github.com/AntonioBlago/visiblyai-mcp-server/blob/master/PLUGINS.md#windows-saved-key-versus-running-client).
Check `/mcp`, then ask the agent to call `list_projects` to verify authenticated
access. This plugin targets Claude Code, not Claude Desktop.

The agent writes and revises the article using its own model. Visibly supplies context, NSS feedback and draft storage. A target score is not guaranteed.
