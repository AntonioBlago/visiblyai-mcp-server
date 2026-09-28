# Visibly AI for Codex

Version 1.0.1. Includes the Visibly MCP connection and the content-nss-optimize skill.

[What the NSS measures](https://www.visibly-ai.com/nss-score) ·
[NSS auf Deutsch erklärt](https://www.visibly-ai.com/de/nss-score)

Methodological foundation: Antonio Blago's [Neuro-SEO-System®](https://www.antonioblago.com/de/neuro-seo-system/) (German overview).

[Installation, API-key setup, costs and usage](https://github.com/AntonioBlago/visiblyai-mcp-server/blob/master/PLUGINS.md)

The MCP connection requires `VISIBLYAI_API_KEY` in the environment of the **Codex
process** on Windows, macOS and Linux. Saving a key or exporting it in a terminal
does not update an already running VS Code or Codex application. Fully exit the application and relaunch it
with the key loaded, then start a new chat. Setting the key only in VS Code's
integrated terminal does not update the extension's environment.

Follow the [macOS/Linux setup](https://github.com/AntonioBlago/visiblyai-mcp-server/blob/master/PLUGINS.md#macos-and-linux)
or [Windows setup](https://github.com/AntonioBlago/visiblyai-mcp-server/blob/master/PLUGINS.md#windows-saved-key-versus-running-client).
On macOS quit VS Code with Cmd+Q. On every OS, start it with `code .` from the
prepared terminal after fully exiting existing instances; a Dock or app-menu
launch does not guarantee the same environment.
Verify access by asking the agent to call `list_projects`; seeing this skill alone
does not establish an authenticated MCP connection.

The agent writes and revises the article using its own model. Visibly supplies context, NSS feedback and draft storage. A target score is not guaranteed.
