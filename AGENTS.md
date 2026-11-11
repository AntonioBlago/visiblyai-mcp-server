# Hinweise für Agents

- Markenname in gepflegten Texten immer **Neuro-SEO-System®** schreiben, auch
  auf Englisch. URLs, technische Kennungen und originale Quelldaten beibehalten.

- Lies [CLAUDE.md](CLAUDE.md) für Projektstruktur und bestehende Arbeitsregeln.
- Vor Änderungen an Plugins, Skills, MCP-Transport, Releases oder öffentlicher
  Darstellung: [Plugin-/MCP-Übergabe](docs/PLUGIN_MCP_HANDOFF.md) lesen.
- [PLUGINS.md](PLUGINS.md) ist die Installationsanleitung für Nutzer;
  `skills/content-nss-optimize/SKILL.md` ist die kanonische Workflow-Quelle.
  Die Kopien unter `plugins/` über `scripts/build_plugins.py --sync-skills`
  aktualisieren, nicht unabhängig bearbeiten.
- Python-Paket, Plugin-ZIPs, Remote-MCP und Marketingseite haben getrennte
  Veröffentlichungen. Ein Commit allein aktualisiert diese nicht alle.
- Der Paperclip-Konnektor (`AntonioBlago/paperclip-plugin-visibly-ai`) ruft
  dieselben REST-Pfade wie `src/visiblyai_mcp/api_client.py` auf, mit fester
  Werkzeugliste. Wird dort ein Pfad oder Parameter umbenannt, entfernt oder
  ein neues lesendes Werkzeug ergänzt, im Konnektor `npm run check:mcp`
  laufen lassen und `src/tools.ts` nachziehen.
- Nach Änderungen den Übergabestand mit Datum, betroffenen Repositories,
  Versionsquellen, Tests und tatsächlichem Veröffentlichungsstatus ergänzen.
  Geprüfte Beobachtungen von offenen Punkten unterscheiden; keine Keys oder
  privaten Artikelinhalte in die öffentliche Dokumentation schreiben.
