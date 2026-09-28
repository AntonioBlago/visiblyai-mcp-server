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
| `AntonioBlago/visibly-ai-cms-connector` / `master` | Python-SDK auf der CMS-Seite, zuvor GitHub `ai-content-autopilot` | `README.md`, `docs/INTEGRATION_DE.md` |
| `AntonioBlago/anycms` / `main` | Konkrete CMS-Anwendungsfälle für WordPress, Astro, Next.js und Flask | `README.md`, `docs/CONTRACT.md` |
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
  bereits laufende GUI-Prozesse nicht automatisch. Die gesamte Anwendung mit
  verfügbarer Variable neu starten, danach einen neuen Chat öffnen. Ein neuer
  Chat oder ein integriertes Terminal allein aktualisiert den Elternprozess nicht.
  Einrichtung für Windows, macOS und Linux sowie Verbindungsprüfung stehen in
  `PLUGINS.md`. Shell-Profile und Desktop-Startumgebungen getrennt behandeln.

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

### Verbindliche Update-Checkliste pro Änderung

Diese Liste vor jedem NSS-, API-, MCP- oder Plugin-Update durchgehen. Für jeden
Bestandteil im datierten Übergabestand **geändert und geprüft**, **nicht nötig
mit Grund** oder **offen** festhalten. Ein Git-Push ist kein Paket-Release und
kein Nachweis eines erfolgreichen Deployments oder Client-Updates.

| Bestandteil | Wann aktualisieren? | Abschlussnachweis |
| --- | --- | --- |
| App, NSS und Editor | Berechnung, Ergebnisfelder oder Anzeige geändert | Scorer-Version bei Berechnungsänderung; gemeinsame Engine wiederverwenden; lokale Kern-/Bereichstests, Lint/Build und betroffene Browserrouten; CI und produktiven Commit gesondert prüfen |
| REST-API und generierte Referenz | Tool-Vertrag oder Beschreibung geändert | Pydantic/OpenAPI und Generator pflegen; `gen_mcp_api_doc --check`; Rechte, Kosten, Persistenz und Editor-/MCP-Parität prüfen |
| Python-MCP-Paket / PyPI | Paketcode, Tool-Schemas, Mapping, Abhängigkeiten oder gebündelte Daten geändert | Paketversion erhöhen, Tests/Build, neuer Tag/Release und PyPI-Upload; saubere Installation der veröffentlichten Version, Toolzahl und Aufruf prüfen. Reine serverseitige NSS-Änderung braucht bei kompatiblem Vertrag keinen PyPI-Release |
| Remote-MCP | Paket-Pin, Transport, Toolvertrag oder Auth geändert | Bikefitting-Adapter/Pins synchronisieren; richtigen Railway-Service deployen; authentifizierte/anonyme Aufrufe und weitergereichte Ergebnisfelder prüfen |
| Plugin-Bundles | Mitgelieferter Skill, README, Manifest oder MCP-Konfiguration geändert | Kanonischen Skill synchronisieren; Versionen/Marktplatz-Kataloge prüfen; drei Bundles bauen; neuer `plugins-vX.Y.Z`-Release mit SHA256SUMS; ZIPs herunterladen und prüfen. Veröffentlichte ZIPs niemals unter gleichem Tag ersetzen |
| Marketing / Webseite | Verhalten, Erklärung, Version oder Downloads geändert | DE/EN gemeinsam pflegen; zentrale NSS-Seite und Neuro-SEO-Grundlage verlinken; Versionskonstanten/Downloads erst auf vorhandene Artefakte umstellen; Tests, Mobil/Desktop und echte Live-Inhalte prüfen |
| CMS-SDK und `anycms` | Artikel-, Revisions-, Import- oder CMS-Vertrag betroffen | Verträge, Beispiele und ggf. SDK-Version/Release synchronisieren; bei reiner NSS-Anzeige ausdrücklich als unverändert dokumentieren |
| Öffentliche READMEs / Profil | Einrichtung, Produktnamen, Versionen oder Linkziele betroffen | MCP, CMS-Connector, `anycms` und GitHub-Profil prüfen; NSS-Erklärung zentral verlinken, keine zweite Formel veröffentlichen |
| Installierte Clients / Caches | Nutzer soll einen neuen Plugin-/Paketstand tatsächlich verwenden | Installation aktualisieren, bei Bedarf Cache neu installieren; vollständiger Client-Neustart mit vorhandener Key-Umgebung auf Windows/macOS/Linux; neuen Chat und MCP-Verbindung prüfen. Git/PyPI allein aktualisiert keinen laufenden Client |
| Übergaben / Changelog | Bei jedem Update | Datum, Repositories, Commit-/Paket-/Plugin-/Scorer-Versionen, Tests, Deployment- und Release-Links sowie verbleibende Schritte festhalten; keine Zugangsdaten |

Für NSS immer zusätzlich prüfen: Der SEO-/GEO-Anteil enthält weiterhin Terme,
Entitäten, Query-Fan-outs und Belegsignale; Sprache/Zielgruppenmotive und
Artikel-E-E-A-T verständlich erklären. Keine vorhandene Komponente doppelt
einrechnen. Website-E-E-A-T bleibt separater Kontext. Vergleich nur bei gleichem
Text, Briefing, Persona, Scorer-Version und Bewertungsmodus.

**Einordnung des Updates vom 28.09.2026:** App v6, API-Erklärung, Marketing und
Plugin-Skill wurden geändert. PyPI 0.13.0 und Remote-Pin bleiben kompatibel,
weil weder Tool-Argumente noch Paket-Mapping geändert wurden. CMS-SDK/`anycms`
benötigen für diese NSS-Erweiterung keine neue Version; bestehende öffentliche
NSS-Links bleiben gültig. Ein regulärer Plugin-Release bleibt **offen**, damit
die geänderten gebündelten Anleitungen/Skills auch über die ZIP-Downloads
ausgeliefert werden. Bisher wurden diese Änderungen nur in Git veröffentlicht;
veröffentlichte Bundles 1.0.1 und installierte Caches bleiben auf ihrem Release-Stand.

### Reihenfolge der Veröffentlichung

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
   Reine Repository-Dokumentation benötigt keinen PyPI-Release. Geänderte Inhalte,
   die in Plugin-ZIPs mitgeliefert werden, benötigen für deren Auslieferung einen
   neuen Plugin-Release gemäß der Checkliste oben.

## Dokumentationsnachtrag vom 2026-09-27

Agent-Einstiege in Paket, App, Remote-Adapter, Marketing und GitHub-Profil ergänzt;
veraltete aktuelle Tool-/Versionsangaben korrigiert und historische Inventare
gekennzeichnet. Marketing-Konstanten und gemeinsame Partials kommentiert.
Marketing-Tests erneut 70/70 erfolgreich, lokale Dokumentationslinks geprüft und
alle drei Plugin-Bundles erneut validiert. Python-AST und sichtbare Templates der
Marketingseite sind gegenüber `2f30c55` unverändert. Dieser Nachtrag ändert keine
Produktversion und veröffentlicht keine neuen Paket- oder Plugin-Artefakte.

## CMS-Connector benannt und eingeordnet (2026-09-27)

Das separate GitHub-Repository `ai-content-autopilot` heißt jetzt
`visibly-ai-cms-connector` (**Visibly AI CMS Connector**). Der PyPI-Name
`ai-content-autopilot` und Python-Import `ai_content_autopilot` bleiben bestehen.
Dieses MCP-/Plugin-Repository behält seinen Namen. `anycms` bleibt das
Use-Case-Repository; es wird weder umbenannt noch mit dem SDK zusammengelegt.
Die [gemeinsame Erklärung](https://github.com/AntonioBlago/visibly-ai-cms-connector/blob/master/docs/INTEGRATION_DE.md)
führt vom externen Assistenten über Visibly zum CMS und zur Publikationsbestätigung.

## Windows-Prozessumgebung: Anleitung präzisiert (2026-09-28)

- Betroffen: `visiblyai-mcp-server` (`PLUGINS.md`, Codex-Bundle-README und diese
  Übergabe); Querverweis in `visibly-app/docs/PLUGIN_MCP_HANDOFF.md`.
- Beobachtung in der lokalen Codex-Sitzung: Plugin aktiviert, Windows-User-Variable
  vorhanden, Prozessvariable nicht vorhanden. Der vorhandene Schlüssel erlaubte
  einen direkten MCP-Handshake mit Server 0.13.0, die Liste von 84 Tools und einen
  erfolgreichen authentifizierten `list_projects`-Aufruf. Das beweist den Zugang,
  nicht das nachträgliche Laden nativer Werkzeuge in den laufenden Codex-Chat.
- Anleitung unterscheidet jetzt gespeicherte User-Variable, aktuelle Shell und
  Elternprozess. Vollständiger Anwendungsneustart, Start aus einer Shell mit
  geladenem Schlüssel und neuer Chat sind ausdrücklich beschrieben; ein neues
  Chatfenster oder integriertes Terminal allein genügt nicht.
- Lokal geprüft: vier PowerShell-Blöcke syntaktisch gültig; Schlüssel aus dem
  User-Scope in eine Test-Shell geladen und Vererbung an einen Kindprozess bestätigt,
  ohne den Wert auszugeben. Alle drei Bundles mit `scripts/build_plugins.py` in
  einem separaten temporären Verzeichnis validiert/gebaut; `git diff --check` sauber.
- Versionen unverändert: MCP 0.13.0, öffentliche Plugin-Manifeste 1.0.1. Nur
  Dokumentationsänderungen; kein Laufzeit-, Skill- oder API-Vertrag geändert.
  Nicht gepusht oder veröffentlicht; Release-ZIPs, installierter Plugin-Cache und
  Marketingseite unverändert. Die gebauten ZIPs sind lokale Prüfartefakte und dürfen
  veröffentlichte 1.0.1-Downloads nicht ersetzen. Für die aktualisierte gebündelte
  README bleibt ein späterer regulärer Plugin-Release offen.

## Plattformübergreifende Einrichtung (2026-09-28)

- `PLUGINS.md` und alle drei Bundle-READMEs behandeln jetzt Windows, macOS und
  Linux. zsh/bash: private Datei außerhalb des Projekts, Dateirechte, explizites
  Laden, optionale Shell-Profile und ein Kindprozess-Check ohne Schlüsselausgabe.
  macOS: Cmd+Q und `code`-Launcher; Linux: alle Editor-Instanzen beenden. Dock,
  App-Menü, WSL/SSH/Container und laufende Elternprozesse sind separat erklärt.
- Gemeinsamer Abschluss: authentifiziertes `list_projects`, leere Erfolgsliste
  von fehlenden Rechten unterscheiden, Hinweise zu 401/403/Netzwerk und zu
  Copilots gespeichertem Header nach einem Schlüsselwechsel.
- Marketing-Repository `visiblyai`: DE/EN-Plugin-Seiten mit aufklappbaren
  Betriebssystem-Anleitungen und Verbindungscheck. Der Guide-Link zeigt auf die
  aktuelle `master/PLUGINS.md`; versionierte Downloads bleiben auf Release 1.0.1.
  Dokumentationskorrekturen sollen nicht durch einen eingefrorenen Guide-Link
  unsichtbar bleiben. MCP-Dokumentation vor Marketing veröffentlichen.
- Geprüft: 11 Bash-Blöcke mit Git Bash syntaktisch validiert; fehlender und aus
  privater Datei geladener Dummy-Key samt Kindprozess-Vererbung geprüft. Vier
  PowerShell-Blöcke geparst; alle drei Plugin-Bundles temporär gebaut/validiert.
  Marketing: 70 bestehende Tests bestanden; Chromium-Prüfung in DE/EN bei
  390/1440 px, OS-Details geöffnet, Links/Verbindungscheck und Seitenbreite geprüft.
- Grenzen: kein nativer macOS-/Linux-Clientlauf und kein zsh-Lauf auf diesem
  Windows-Rechner; die Bash-Prüfung ersetzt diese nicht. Keine neuen Runtime-
  Features oder Versionsänderungen. Alles lokal und unveröffentlicht; bestehende
  Release-ZIPs und installierte Caches unverändert. Neue Bundle-READMEs erst mit
  regulärem künftigem Plugin-Release ausliefern.

## Öffentliche NSS-Referenz (2026-09-28, lokal)

Nachtrag Grundlage: README, PLUGINS, drei Bundle-READMEs und kanonischer Skill
verlinken Antonio Blagos Neuro-SEO System® unter
`https://www.antonioblago.com/de/neuro-seo-system/` (HTTP 200 und Canonical geprüft).
Die Marketingseite nennt die Grundlage auf DE/EN; entsprechende Verweise auch
im CMS-Connector, GitHub-Profil und interner NSS-Referenz der App ergänzt.
Skill-Kopien synchronisiert, Validator und drei temporäre Plugin-Builds erfolgreich;
Marketing erneut 73 Tests sowie vier Browseransichten (DE/EN, 390/1440 px) geprüft.
Weiterhin lokal, ohne Push/Deployment/Release. MCP 0.13.0, Plugins 1.0.1;
veröffentlichte ZIPs und installierte Caches unverändert.

Die zentrale Erklärung liegt künftig unter
[Deutsch](https://www.visibly-ai.com/de/nss-score) und
[English](https://www.visibly-ai.com/nss-score). Sie erklärt Bewertungsbereiche,
nachvollziehbares Feedback, Vergleichsbedingungen und Grenzen ohne Formel oder
Gewichte. Keine Zusage „unkopierbar“, Rankings oder KI-Zitationen daraus ableiten.

Links ergänzt: dieses Repository (README, PLUGINS, drei Bundle-READMEs,
kanonischer `content-nss-optimize`), `visibly-ai-cms-connector` (README und deutsche
Integration), GitHub-Profil `AntonioBlago`. `visibly-app` ersetzt die detaillierte
In-App-Formelerklärung durch eine Kurzreferenz mit Link. Scorer unverändert;
E-E-A-T wurde nicht in NSS integriert. Eine gesonderte Gewichtung ist bisher
nur ein Vorschlag und keine implementierte Produkteigenschaft.

Skill mit `quick_validate.py` validiert, Kopien per `build_plugins.py --sync-skills`
synchronisiert und drei Bundles in temporärem Verzeichnis geprüft. Marketing:
73 Tests, sechs Browseransichten DE/EN bei 390/768/1440 px und sechs eingehende
Linkwege. App-Build und gezielter Lint erfolgreich, globaler Lint mit bestehenden
31 Fehlern/6 Warnungen in anderen Dateien nicht grün. App-Route lokal mit
Auth-/Projekt-Fixtures geprüft; Details in App-Übergabe.

Veröffentlichung offen: erst Marketing-URLs ausliefern und live prüfen, danach
öffentliche Repository-Verweise; Setup-Dokumentation aus vorherigem Nachtrag vor
dem Marketing-Guide-Link bereitstellen. Kein Push, Deployment oder neuer
Plugin-/PyPI-Release erfolgt. Plugin-Version 1.0.1 und MCP 0.13.0 unverändert;
neue Skill-/README-Kopien für einen regulären nächsten Plugin-Release vormerken,
keine bestehenden Release-ZIPs ersetzen. Installierte Caches unverändert.

## Veröffentlichung der Dokumentation (2026-09-28)

Die vorherigen lokalen Statusangaben sind die Vorbereitungshistorie.
Setup-Anleitung `5d564e5` ist nach `master` gepusht. Marketing `visiblyai`:
Commit `c6f4d08` auf `main`, Vercel erfolgreich; die beiden NSS-Seiten live mit
HTTP 200 und Neuro-SEO-Grundlagenlink geprüft. Die NSS-Verweise in diesem Stand
zeigen damit auf vorhandene öffentliche Seiten. CMS-Connector und GitHub-Profil
werden im selben Veröffentlichungslauf aktualisiert.

Vor Veröffentlichung erneut drei Plugin-Bundles in einem temporären Verzeichnis
gebaut und kanonischen Skill validiert; Marketing 73 Tests erfolgreich.
MCP 0.13.0 / Plugins 1.0.1 unverändert. Kein PyPI-/Plugin-ZIP-Release und keine
Änderung installierter Caches; neue Bundle-Inhalte für nächsten Release vormerken.
App-Build und gezielter NSS-Lint erneut erfolgreich; globaler App-Lint weiterhin
31 Fehler/6 Warnungen in unveränderten Dateien. App-Status in deren Übergabe prüfen.
# NSS v6 und Artikel-E-E-A-T (2026-09-28)

Die App verwendet für den aktuellen Entwurf die vorhandenen Content-Prüfungen
der E-E-A-T-Engine; kein duplizierter E-E-A-T-Service. Website-E-E-A-T bleibt
separater Kontext. Das zusätzliche Ergebnis `data.nss.eeat` enthält Befunde und
Verfügbarkeit, `scores.nss_version`/`nss_mode` kennzeichnen die Vergleichsgrundlage.
Die Gewichtung bleibt in der internen App-Dokumentation, die öffentliche Erklärung
unter [Deutsch](https://www.visibly-ai.com/de/nss-score) bzw.
[English](https://www.visibly-ai.com/nss-score).

Kanonischer Skill ergänzt: Version/Modus festhalten, bei Wechsel Baseline neu
messen, fehlendes EEAT nicht als Null deuten, keine Autoren oder Belege erfinden.
Drei Bundle-Kopien über `build_plugins.py --sync-skills` synchronisiert; alle drei
Bundles temporär gebaut, `quick_validate.py` erfolgreich. API-Argumente unverändert,
Paket 0.13.0 / Plugins 1.0.1 weiter kompatibel. Kein PyPI-/ZIP-Release und kein
installierter Cache aktualisiert; Skill-Inhalte für nächsten regulären Release.
App lokal: 518 Tests, Build, Lint (0 Fehler/6 bestehende Warnungen) und
Editor-Browserprüfungen. Marketing lokal: 73 Tests und DE/EN-Browserprüfungen.
Veröffentlichung je Repository/Commit prüfen; lokale Nachweise sind kein Live-Test.
