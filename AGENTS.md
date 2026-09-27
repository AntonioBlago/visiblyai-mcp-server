# Hinweise für Agents

- Lies [CLAUDE.md](CLAUDE.md) für Projektstruktur und bestehende Arbeitsregeln.
- Vor Änderungen an Plugins, Skills, MCP-Transport, Releases oder öffentlicher
  Darstellung: [Plugin-/MCP-Übergabe](docs/PLUGIN_MCP_HANDOFF.md) lesen.
- [PLUGINS.md](PLUGINS.md) ist die Installationsanleitung für Nutzer;
  `skills/content-nss-optimize/SKILL.md` ist die kanonische Workflow-Quelle.
  Die Kopien unter `plugins/` über `scripts/build_plugins.py --sync-skills`
  aktualisieren, nicht unabhängig bearbeiten.
- Python-Paket, Plugin-ZIPs, Remote-MCP und Marketingseite haben getrennte
  Veröffentlichungen. Ein Commit allein aktualisiert diese nicht alle.
- Nach Änderungen den Übergabestand mit Datum, betroffenen Repositories,
  Versionsquellen, Tests und tatsächlichem Veröffentlichungsstatus ergänzen.
  Geprüfte Beobachtungen von offenen Punkten unterscheiden; keine Keys oder
  privaten Artikelinhalte in die öffentliche Dokumentation schreiben.
