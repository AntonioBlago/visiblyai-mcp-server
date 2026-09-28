# Visibly AI for GitHub Copilot CLI

Version 1.0.1. Includes the content-nss-optimize skill. Add the Visibly MCP connection once using the setup instructions below; authentication is stored in Copilot's private user configuration.

[What the NSS measures](https://www.visibly-ai.com/nss-score) ·
[NSS auf Deutsch erklärt](https://www.visibly-ai.com/de/nss-score)

Methodological foundation: Antonio Blago's [Neuro-SEO-System®](https://www.antonioblago.com/de/neuro-seo-system/) (German overview).

[Installation, API-key setup, costs and usage](https://github.com/AntonioBlago/visiblyai-mcp-server/blob/master/PLUGINS.md)

The guide covers Windows, macOS and Linux. After installation, use Copilot's
`/mcp add` to configure the HTTP connection and your Authorization header, then
restart Copilot and ask it to call `list_projects` to verify authenticated access.
If you use the environment-variable command instead, load the key in the same
terminal before running it. After rotating the key, update Copilot's saved MCP
header as well. Copilot in VS Code has its own setup, described in the guide.

The agent writes and revises the article using its own model. Visibly supplies context, NSS feedback and draft storage. A target score is not guaranteed.
