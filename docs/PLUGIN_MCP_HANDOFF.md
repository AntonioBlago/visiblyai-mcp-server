# Visibly Plugins und MCP: Übergabe für Agents

Stand: 2026-09-27. Diese Datei verbindet die Zuständigkeiten der Repositories.
Sie beschreibt den zu diesem Datum verifizierten Release, keine automatische
Live-Abfrage. Vor einem neuen Release Versionen und Deployment erneut prüfen.

## Aktueller Stand

| Bestandteil | Verifizierter Stand | Maßgebliche Quelle |
| --- | --- | --- |
| Python-Paket / MCP | 0.13.0, 84 registrierte Tools | `src/visiblyai_mcp/__init__.py`, Runtime-Tool-Manager |
| Plugin-Bundles | 1.0.1 für Codex, Claude Code und Copilot CLI | Manifeste unter `plugins/`, GitHub-Release `plugins-v1.0.1` |
| Remote-Verbindung | `https://mcp.visibly-ai.com/mcp` | Bikefitting-Kompatibilitätstransport mit Paket-Pin 0.13.0 |
| Native REST-API | `https://app.visibly-ai.com/api/v1/mcp` | visibly-app, FastAPI-Router und gemeinsame Services |
| Marketing | DE/EN-Downloadseiten live, Commit `2f30c55` | Repository `AntonioBlago/visiblyai`, `main`, Vercel |

Releases: [PyPI](https://pypi.org/project/visiblyai-mcp-server/0.13.0/),
[Plugin-ZIPs und Prüfsummen](https://github.com/AntonioBlago/visiblyai-mcp-server/releases/tag/plugins-v1.0.1).
Installationsbefehle, API-Key-Einrichtung und Beispielauftrag stehen in
[PLUGINS.md](../PLUGINS.md). Diese Befehle nicht als zweite Anleitung duplizieren.

## Welches Repository ist zuständig?

| Repository / Branch | Verantwortung | Einstieg |
| --- | --- | --- |
| `AntonioBlago/visibly-app` / `master` | Auth, Rechte, Abrechnung, Content, NSS, Editor, CMS-Status | `docs/PLUGIN_MCP_HANDOFF.md`, `docs/MCP_TOOLS_API.md` |
| `AntonioBlago/visiblyai-mcp-server` / `master` | MCP-Paket, Tool-Schemas, kanonischer Skill, Plugin-Manifeste und ZIPs | diese Datei, `PLUGINS.md`, `scripts/build_plugins.py` |
| `AntonioBlago/Bikefitting_Project` / `master` | Remote-JSON-RPC und historische REST-Kompatibilität | `docs/internal/MCP_SYNC_GUIDE.md` |
| `AntonioBlago/visiblyai` / `main` | Öffentliche Marketing-, Download- und Entwicklerseiten | `docs/PLUGIN_INTEGRATIONS.md`, `docs/DEPLOYMENT_VERCEL.md` |
| `AntonioBlago/AntonioBlago` / `main` | GitHub-Profil mit Links zu Paket und Plugins | `README.md` |

Die Marketing-Domain ist kein API-Host. Marketing läuft auf Vercel; Backend und
Remote-MCP laufen auf Railway. Ein lokales `railway status` kann auf ein anderes
Projekt zeigen: Zielservice vor einem Deployment anhand Domain und Repository prüfen.

## Unterstützte Clients und Grenzen

- **OpenAI Codex:** Plugin `visibly-codex`, Remote-MCP-Konfiguration enthalten.
- **Claude Code:** Plugin `visibly-claude`, Remote-MCP-Konfiguration enthalten.
- **GitHub Copilot CLI:** Plugin `visibly-copilot` enthält den Skill; MCP muss
  einmal separat eingerichtet werden. VS Code hat eine eigene Einrichtung.
- Claude Desktop kann als MCP-Client angebunden werden; der Claude-Code-Download
  ist keine Desktop-Erweiterung. Die Bundles implementieren keine direkte
  ChatGPT-Integration mit OAuth-Anmeldung.
- Der öffentliche GitHub-Marketplace ist verfügbar. Eine Listung in kuratierten
  Anbieter-Stores wurde nicht veröffentlicht und darf nicht behauptet werden.
- `VISIBLYAI_API_KEY` kommt aus der Client-Umgebung. Ein neu gesetzter Key erreicht
  bereits laufende GUI-Prozesse nicht automatisch; neue Sitzung starten.

Marktplatz-Kataloge: `.agents/plugins/marketplace.json` (Codex),
`.claude-plugin/marketplace.json` (Claude), `.github/plugin/marketplace.json`
(Copilot). Ihre Formate sind verschieden; nicht gegeneinander austauschen.

## Skills, Schreiben, Scoring und Kosten

Der mitgelieferte `content-nss-optimize` nutzt vorhandene Projektdaten und ein
fertiges Briefing. Der externe Agent schreibt und überarbeitet mit seinem Modell.
Visibly liefert Kontext, deterministisches `score_text` und Entwurfsspeicherung.
Diese drei Visibly-Operationen kosten 0 Credits; Modell-Tokens oder Abonnements
des Assistenten bleiben separat kostenpflichtig. Neue Analysen sind eigene,
gegebenenfalls kostenpflichtige Vorgänge. Die Optimierung ruft nicht beiläufig
die bezahlte Visibly-Textgenerierung auf.

Der Skill misst nach jeder Überarbeitung, behält den besten Entwurf und beendet
die Optimierung beim gewünschten NSS-Ziel, spätestens nach fünf Überarbeitungen
oder zwei Runden ohne Verbesserung. NSS 70/80 ist ein Ziel, keine Garantie.
Nach dem Speichern gespeicherten Text erneut lesen/scoren und den Editor-Link
zurückgeben. Ob ein Browser-Tab geöffnet wird, hängt vom Client ab.

Weitere Methodiken werden über `get_skill(name='list')` entdeckt und einzeln
abgerufen. Authentifizierte Aufrufe verwenden den aktuellen Visibly-Katalog;
anonyme Aufrufe können das Paket-Fallback nutzen. Am 2026-09-27 wurden remote
39 Skills authentifiziert gesehen. Die Kataloggröße ist dynamisch, keine feste
Plugin-Version und keine Zusage, dass jedes Tool mit jedem Key ausführbar ist.
Rechte, Feature-Schalter, Projektzugriff und Abrechnung entscheidet das Backend.

## Artikelidentität, Übernahme und 95-%-Toleranz

1. Vor einer bestehenden Website-Aktualisierung `get_article_workflow` lesen.
   Eine gleiche `published_url` beweist nicht, dass der gewählte Entwurf den
   CMS-Beitrag besitzt. Bei `binding_state='conflict'` den empfohlenen angebundenen
   Artikel öffnen und dessen Revision prüfen; keine zweite Verknüpfung erfinden.
2. **Entwurf speichern:** ändert Visibly. **Website-Version übernehmen:** importiert
   ins Editor-Dokument. **Website aktualisieren/veröffentlichen:** ist ein eigener
   CMS-Schreibvorgang mit eigenen Rechten und Status.
3. Eine Webhook-Annahme oder „zurückgespielt“ beweist keine fertige Veröffentlichung.
   Lieferstatus und aktuellen Live-Inhalt getrennt prüfen. Keine feste Wartezeit
   von beispielsweise 30 Minuten versprechen, wenn der Connector keine ETA liefert.
4. `get_article_workflow(compare_live=True)` liefert den Inhaltsvergleich. Die
   95-%-Grenze betrifft **Wort-Textähnlichkeit** zwischen gespeichertem und live
   abgerufenem Inhalt. Links, Bilder und Dokumentstruktur müssen weiterhin gleich
   sein. Titel und Meta-Description werden separat verglichen; fehlende Werte sind
   unbekannt und dürfen nicht als Übereinstimmung gelten.
5. `content_matches` bleibt der exakte Vergleich; `content_within_tolerance` ist
   das tolerante Ergebnis. Die 95-%-Grenze ist weder NSS-Toleranz noch statistische
   Genauigkeit, und sie bestätigt keinen asynchronen CMS-Job.

Bei NSS-Abweichungen denselben gespeicherten Text, dasselbe Format und dasselbe
Projekt-/Query-Briefing vergleichen. Score, Textvergleich und Lieferstatus sind
drei unterschiedliche Aussagen.

## Was wurde zuletzt geändert und geprüft?

- App bis `456ea603`: gemeinsamer Artikel-Workflow für UI/MCP, Erkennung konkurrierender
  Entwürfe, eindeutige Import-/Update-Aktionen, 95-%-Texttoleranz. App-CI und
  Produktion wurden für diesen Stand erfolgreich geprüft.
- Paket-Release `2f0adde`, Dokumentation `6f6e523`: MCP 0.13.0, `get_article_workflow`,
  Plugins 1.0.1; saubere PyPI-Installation mit 84 Tools geprüft.
- Remote-Transport `a546f87f` / `e873c3bb`: Paket-Pin 0.13.0 und authentifizierter
  Skill-Katalog aus Visibly; 81 gezielte MCP-Tests und Live-Tool-Liste geprüft.
  Das ist kein pauschaler Nachweis für spätere Commits oder die gesamte Legacy-CI.
  Die anschließend korrigierte Legacy-CI für `86d664b3` ist erfolgreich
  (GitHub-Actions-Lauf `36339842026`, am 2026-09-27 geprüft).
- Marketing `2f30c55`: drei Downloadkarten, Installationsanleitungen, NSS-/Kostenhinweise,
  Links in Startseite, Navigation und Footer; älteres SEO-Starter-Plugin separat.
  70 Tests bestanden; Browserprüfungen bei 390/1280/1440 px in DE/EN;
  alle drei veröffentlichten ZIPs gegen `SHA256SUMS.txt` geprüft;
  Vercel erfolgreich und beide Downloadseiten/Startseiten live mit HTTP 200 geprüft.

## Pflege und nächste Releases

1. Backend-Verträge zuerst ändern und prüfen; generierte API-Referenz mit
   `backend/scripts/gen_mcp_api_doc.py` aktualisieren. Auth/Billing nicht im Plugin
   oder Remote-Adapter nachimplementieren.
2. Paket-Schemas und `CONTENT_WORKFLOW_PATHS` synchron halten. Die Tool-Zahl aus
   `mcp._tool_manager._tools` bestimmen; dynamisch registrierte Tools mitzählen.
   Python-Version kommt aus `src/visiblyai_mcp/__init__.py` über Hatch.
3. Bei Skill-Änderungen die kanonische Datei bearbeiten und
   `python scripts/build_plugins.py --sync-skills` ausführen. Ohne Sync-Modus
   muss der Build identische Skill-Kopien, Manifeste, Kataloge und ZIPs validieren.
4. Nur passende Artefakte veröffentlichen: Python auf PyPI; Plugin-ZIPs und
   Prüfsummen unter einem neuen `plugins-vX.Y.Z`-Tag. Bereits veröffentlichte
   Release-ZIPs nicht still ersetzen. Ein Git-Push führt keinen PyPI-Upload aus;
   der Plugin-CI-Workflow validiert ZIPs, veröffentlicht sie aber nicht automatisch.
5. Remote-Transport bei Paketänderungen pinnen/deployen; anschließend authentifizierte
   und anonyme MCP-Aufrufe prüfen. Lokale Client-Updates sind ein weiterer Schritt.
6. Erst nach verfügbaren Downloads Marketing-Konstanten, DE/EN-Seiten und ggf.
   GitHub-Profil aktualisieren. Ein Marketing-Push auf `main` löst Vercel aus.
7. Diese Übergabe, lokale Agent-Einstiege und Changelogs mit Datum/Belegen pflegen.
   Dokumentationsänderungen allein benötigen keinen neuen PyPI-/Plugin-Release.

## Dokumentationsnachtrag vom 2026-09-27

Agent-Einstiege in Paket, App, Remote-Adapter, Marketing und GitHub-Profil ergänzt;
veraltete aktuelle Tool-/Versionsangaben korrigiert und historische Inventare
gekennzeichnet. Marketing-Konstanten und gemeinsame Partials kommentiert.
Marketing-Tests erneut 70/70 erfolgreich, lokale Dokumentationslinks geprüft und
alle drei Plugin-Bundles erneut validiert. Python-AST und sichtbare Templates der
Marketingseite sind gegenüber `2f30c55` unverändert. Dieser Nachtrag ändert keine
Produktversion und veröffentlicht keine neuen Paket- oder Plugin-Artefakte.
