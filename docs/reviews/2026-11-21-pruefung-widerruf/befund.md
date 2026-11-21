# Befund Karte 606: Tokens, Prüfergebnisse und Widerruf im MCP-Paket

- Geprüfter Commit: `680ca448eb1a73d6bd4683630ef0769f44121c6e` (Branch `board/606-pruefkarte-speichert-der-mcp-s`; `src/` ist identisch mit dem Abzweigpunkt `f27edbd`)
- Datum: 2026-11-21
- Umfang: stdio-Paket `visiblyai-mcp-server` (`src/visiblyai_mcp/`). Nicht im Umfang: Remote-Adapter `mcp.visibly-ai.com` (siehe L-Remote), App `visibly-app`.
- Vertrag: `docs/contracts/karte-606_v001.md`
- Tests: `tests/test_revocation_606.py`

## Kurzfassung

Das Paket hat keinen Token-, Antwort- oder Prüfergebnis-Cache. Jeder Werkzeugaufruf liest
`VISIBLYAI_API_KEY` neu aus `os.environ`, baut einen neuen `VisiblyAIClient` mit neuem
`httpx.Client` und schickt den Schlüssel an die App, die ihn je Anfrage prüft. Ein 401 wird
nicht wiederholt. Ein in der App widerrufenes `lc_`- oder `vat_`-Token wird deshalb beim
nächsten Aufruf abgelehnt; Verzögerung 0 s. Lücken im Paket (keine davon ein Widerrufsproblem):
L1 Hygiene, der `httpx.Client` mit festem `Authorization`-Header wird nie geschlossen und bleibt
bis zur Garbage Collection im Speicher; L2 (Fund des data-security-Reviews) ein Schlüssel mit
Whitespace am Ende landet vollständig in der Fehlermeldung `HTTP error: Illegal header value …`
und damit in der Werkzeugausgabe.

## Inventar (K1)

Zeilennummern am geprüften Commit.

| Datei:Zeile | Was wird gehalten | Schlüssel | Lebensdauer | Token-/Nutzerbezug ja/nein | Widerrufsrelevant ja/nein |
|---|---|---|---|---|---|
| `config.py:13-15` `get_api_key` | nichts; liest `VISIBLYAI_API_KEY` bei jedem Aufruf aus `os.environ` | Umgebungsvariable `VISIBLYAI_API_KEY` | je Aufruf gelesen; die Umgebung selbst ist ab Prozessstart fest (vom MCP-Client gesetzt) | ja | nein (Widerruf prüft die App; ein neuer Schlüssel wirkt erst nach Neustart des MCP-Clients) |
| `config.py:5-7` `BASE_URL` | Backend-URL aus `VISIBLYAI_API_URL` oder Standard | Modulkonstante | Prozess (Importzeit) | nein | nein |
| `api_client.py:12` `_TIMEOUT` | `httpx.Timeout(60.0, connect=10.0)`: 60 s je Lesevorgang, 10 s Verbindungsaufbau | Modulkonstante | Prozess (Importzeit) | nein | ja (begrenzt nur einen Lesevorgang einer laufenden Anfrage, siehe K2) |
| `api_client.py:65-66` `self.api_key` / `self._client` | Schlüssel im Klartext und `httpx.Client` der Instanz | Instanzattribut | Lebensdauer der `VisiblyAIClient`-Instanz = ein Werkzeugaufruf, danach bis GC | ja | nein (Instanz wird je Aufruf neu gebaut) |
| `api_client.py:68-78` `_ensure_client` | `httpx.Client` mit festem Header `Authorization: Bearer <Schlüssel>` (Z. 72-73); `close()` (Z. 80-82) wird von keinem Werkzeug aufgerufen | Instanzattribut `_client` | bis GC der Instanz (nie explizit geschlossen) | ja | nein (Hygiene, Lücke L1) |
| `api_client.py:439-444` `_handle_response` | nichts; 401 wird sofort als `APIError(status_code=401)` geworfen, ohne Retry; `_post` (Z. 422-429) und `_get` (Z. 431-437) senden genau einen Request | – | – | ja | ja (belegt sofortige Ablehnung) |
| `paid_tools.py:14-23` `_require_key` | neue `VisiblyAIClient(api_key)`-Instanz je Werkzeugaufruf | lokale Variable | ein Aufruf | ja | nein |
| `project_tools.py:21-26` `_require_key` (genutzt von `_call`, Z. 39-53) | neue Instanz je Aufruf | lokale Variable | ein Aufruf | ja | nein |
| `content_write_tools.py:67-71` `_require_key` (genutzt von `_call`, Z. 78-80) | neue Instanz je Aufruf | lokale Variable | ein Aufruf | ja | nein |
| `content_workflow_tools.py:14-23` `_call` (Instanz Z. 21) | neue Instanz je Aufruf | lokale Variable | ein Aufruf | ja | nein |
| `free_tools.py:269-271` `get_account_info` → `verify` | neue Instanz je Aufruf, `POST /auth/verify` | lokale Variable | ein Aufruf | ja | nein |
| `classifier.py:406`, `:410-432` `_compiled_cache` | kompilierte Regex-Muster der Klassifikator-Klasse | Klassenattribut | Prozess | nein (kein Token, keine App-Antwort) | nein |
| `classifier.py:582` TTL-Cache `_cache` (Parameter `cache_ttl_seconds` Z. 566, Aufbau Z. 581-583, Zugriff Z. 595-620) | lokale Klassifikationsergebnisse | MD5 aus `keyword.lower()` und Markenname | 3600 s, höchstens 10 000 Einträge (`CACHE_MAX_SIZE`, Z. 21) | nein (kein Token, keine App-Antwort; Eingaben des Nutzers) | nein |
| `classifier.py:795-805` Singleton `_classifier_instance` (`global` Z. 801) | eine `KeywordClassifier`-Instanz | Modulvariable | Prozess | nein | nein |
| `cli.py:188-193` `sync_skills` | einmaliger `httpx.post` mit `Authorization: Bearer`, keine Speicherung | – | ein CLI-Lauf | ja | nein |
| `cli.py:239` `build_fallback` | schreibt nur komprimierte Skill-Inhalte nach `knowledge/skills.py` (`write_text`), keinen Schlüssel | Datei im Paket | dauerhaft (Entwicklerbefehl) | nein | nein |
| `content_workflow_tools.py:156-158` `create_contentpilot_key` (Pfad `api_client.py:29`) | Backend liefert den Klartext-`cp_`-Schlüssel; `_format_result` reicht `data` ungefiltert in die Werkzeugantwort und damit ins Transkript des MCP-Clients | Werkzeugantwort | im Paket ein Aufruf; im Transkript des MCP-Clients unbegrenzt (außerhalb des Pakets) | ja | ja (der Aufruf rotiert, der alte `cp_`-Schlüssel ist danach inaktiv; Annotation destruktiv, `tools/annotations.py:224`. Nach Widerruf per `revoke_contentpilot_key` steht der alte Klartext weiter im Transkript; gewolltes Verhalten, Einstufung durch data-security) |
| `api_client.py:428-429` (`_post`), `:436-437` (`_get`) `APIError(f"HTTP error: {e}")`; ausgegeben über `paid_tools.py:36-47` `_handle_error`, `free_tools.py:279-283` `get_account_info` (`str(e)`), `knowledge/rag_search.py:38-39` (`str(e)`, Aufruf `paid_tools.py:694-695`), `cli.py:194-195` (Terminal) | Ausnahmetext von httpx/h11; bei Schlüssel mit `\n`, `\r` oder Leerzeichen am Ende lautet er `Illegal header value b'Bearer <Schlüssel>\n'` | Werkzeugantwort | im Paket ein Aufruf; im Transkript des MCP-Clients unbegrenzt | ja | nein (Leck des Schlüssels, kein Widerrufsproblem; Lücke L2) |
| `PLUGINS.md:31-44`, `:77`, `:241-247`; `README.md:38`, `:49`, `:58`; `plugins/visibly-claude/.mcp.json:7`; `plugins/visibly-codex/.mcp.json:6`; `server.py:10` | Schlüssel im Client-Setup außerhalb des Pakets: Umgebungsvariable `VISIBLYAI_API_KEY`, Shell-Profil, Windows-Benutzervariable bzw. Bearer-Header der Remote-Konfiguration | Umgebung/Konfiguration des MCP-Clients | bis der Nutzer ihn ändert | ja | ja (nach Passwortwechsel muss der Nutzer einen neuen Schlüssel eintragen und den Client neu starten; der alte wird von der App abgelehnt) |

Weitere geprüfte Stellen ohne Token-Bezug: `knowledge/checklists.py:117`, `knowledge/google_guidelines.py:78`/`:125`,
`knowledge/seo_guidance.py:90`/`:129`, `knowledge/skills.py:47`/`:83` rufen öffentliche Endpunkte per `httpx.get` ohne
`Authorization` auf und halten keine Antworten. `server.py` registriert nur Werkzeuge (kein Lifespan, kein
Sitzungszustand). `api_client.py:431` `_get` ruft `_require_key` nicht auf; betrifft nur `get_locations`
(ohne Auth), keine Lücke im Sinn dieser Karte. Kein `lru_cache`, `functools.cache`, `cached_property`,
`shelve`, `pickle`, `redis` oder `diskcache` im Paket; kein Client auf Modulebene (statisch geprüft durch
`test_k1_2_no_hidden_cache`, Erlaubnisliste = die Zeilen `classifier.py` `_classifier_instance`/`_compiled_cache`
und `cli.py` `write_text` oben).

## Widerruf je Token-Art (K2)

| Token | Beleg | Ergebnis | Maximale Verzögerung |
|---|---|---|---|
| `lc_` | `test_k1_3_lc_revoked_rejected_next_call` über `paid_tools.get_traffic_snapshot`, `project_tools.get_site_health`, `content_write_tools.get_mcp_operation`, `content_workflow_tools.list_articles`, `free_tools.get_account_info`; Mock 200, dann 401 | 2. Aufruf direkt danach liefert `"status_code": 401` bzw. `"authenticated": false`; genau 2 Requests, beide mit `Authorization: Bearer <Schlüssel>` | 0 s |
| `vat_` | `test_k1_4_vat_revoked_rejected_next_call` über `free_tools.get_account_info` (`/auth/verify`) und `paid_tools.get_traffic_snapshot` | wie `lc_`; das Paket unterscheidet keine Präfixe und schickt `vat_` je Aufruf an die App | 0 s |

Maximale Verzögerung: 0 s für jeden Aufruf, der nach dem Widerruf beginnt. Eine Anfrage, die die App vor dem
Widerruf angenommen hat, läuft zu Ende; das Paket begrenzt sie nur über `_TIMEOUT` (Lese-Timeout 60 s je
Lesevorgang, Verbindungsaufbau 10 s); die Gesamtdauer einer Anfrage ist im Paket nicht begrenzt
(`test_k1_4_max_delay_bound`).

`test_k1_3_key_change_takes_effect` belegt, dass ein Schlüsselwechsel in der Umgebung beim nächsten Request
wirkt (kein prozessweiter Client). Das belegt nur den Code-Pfad: Im Betrieb erhält der Prozess seine Umgebung
beim Start; ein neuer Schlüssel nach Passwortwechsel wirkt erst nach Neustart des MCP-Clients. Das ist eine
Nutzerhürde, kein Widerrufsproblem, denn der alte Schlüssel wird ab dem Widerruf von der App abgelehnt.

Beobachtung (keine Änderung, eigene Karte nötig): Die 401-Meldung „Invalid or missing API key. Get one at …“
(`api_client.py:442`) nennt keinen Widerruf; ein Nutzer nach Passwortwechsel erkennt daraus nicht, dass er
einen neuen Schlüssel braucht.

Reichweite von `test_k1_7_401_output_has_no_key`: belegt nur den Fall „401 mit sauberem Schlüssel“ (5 Pfade × `lc_`/`vat_`),
nicht Transport- oder Protokollfehler; dafür steht L2.

## Lücken (K3)

Paket-Lücken, je mit einem strikten xfail-Test:

- **L1** `httpx.Client` wird nach dem Werkzeugaufruf nicht geschlossen (`api_client.py:68-82`, Aufrufer in den
  fünf Werkzeugmodulen). Der Bearer-Header mit dem Klartext-Schlüssel bleibt bis zur Garbage Collection im
  Speicher, Verbindungen im Pool bleiben offen. Kein Widerrufsproblem (jeder Aufruf baut einen neuen Client,
  die App prüft jeden Request). Test: `test_k1_5_client_closed_after_call`,
  `xfail(strict=True, reason="Befund 606-L1, Fix offen: …")`. Fix-Idee für eine Folgekarte: Werkzeug-Wrapper
  schließen den Client in `finally` oder nutzen `with VisiblyAIClient(...)`.

- **L2** Schlüssel mit Whitespace am Ende erscheint in der Werkzeugausgabe (`api_client.py:428-429`/`:436-437`,
  ausgegeben über `paid_tools.py:36-47`, `free_tools.py:279-283`, `knowledge/rag_search.py:38-39`). Enthält
  `VISIBLYAI_API_KEY` am Ende `\n`, `\r` oder ein Leerzeichen (Kopierfehler, `.env` mit CRLF, Windows-Variable),
  lehnt h11 den Header ab und setzt den vollständigen Wert in die Ausnahme; das Paket reicht ihn als
  `"error": "HTTP error: Illegal header value b'Bearer <Schlüssel>\n'"` mit `"status_code": 0` an den MCP-Client
  und damit ins Transkript weiter. Der Schlüssel ohne das Whitespace ist meist gültig. Nachgestellt mit
  httpx 0.28.1, httpcore 1.0.9, h11 0.16.0. Test: `test_k1_5_key_not_in_transport_error`,
  `xfail(strict=True, reason="Befund 606-L2, Fix offen: …")`; ein Gegentest mit vorübergehendem `strip()` in
  `VisiblyAIClient.__init__` macht ihn zum XPASS (strict rot), danach zurückgenommen. Fix-Idee für eine
  Folgekarte: Schlüssel beim Einlesen mit `strip()` bereinigen und keine rohen Ausnahmetexte in `APIError`
  übernehmen.

Außerhalb des Pakets, ohne Test:

- **L-Remote: nicht geprüft.** Der Remote-Adapter hinter `https://mcp.visibly-ai.com/mcp` liegt im Repo
  `Bikefitting_Project` (lokaler Klon leer). Die Plugin-Konfigurationen (`plugins/visibly-claude/.mcp.json`,
  `plugins/visibly-codex/.mcp.json`) schicken den Schlüssel als Bearer-Header an diesen Adapter, nicht an das
  stdio-Paket. Folgekarten-Text:

  > **Titel:** Prüfkarte: Cacht der Remote-MCP-Adapter (mcp.visibly-ai.com) Token-Prüfungen, greift ein Widerruf sofort? (Folge visiblyai-mcp-server #606)
  >
  > Repo `Bikefitting_Project`, Fundort `docs/internal/MCP_SYNC_GUIDE.md` (Remote-JSON-RPC und REST-Kompatibilität).
  > Nur Prüfung, kein Fix ohne neue Karte. Fragen:
  > 1. Speichert der Adapter das Ergebnis der Token-Prüfung (`vat_`, `lc_`) zwischen (lru_cache, TTL-Cache, Redis, Session-Objekt)? Je Fundstelle Datei:Zeile, Schlüssel, Lebensdauer.
  > 2. Hält der Adapter je MCP-Verbindung oder `Mcp-Session-Id` eine Session mit Nutzer-Kontext oder Token, und wie lange lebt sie nach einem Widerruf weiter?
  > 3. Wie lange leben `vat_` und `vrt_` im Adapter (eigene Ablaufzeit, Refresh ohne Rückfrage an die App)?
  > 4. Beleg je Token-Art per Test mit nachgebildeter App-Antwort (erst 200, dann 401) und maximaler Verzögerung in Sekunden; Lücken als `xfail(strict=True)`.
  > 5. Review data-security.

## Prüfläufe

0 skipped, 0 XPASS, 2 xfailed = 2 Paket-Lücken (L1, L2). Gesamte Unit-Suite (`timeout 600 pytest tests/ --ignore=tests/integration --ignore=tests/e2e`): 242 passed, 2 xfailed; ohne die neue Datei 221 passed wie vor der Änderung.
Gegentest: `get_api_key` vorübergehend mit `functools.lru_cache` versehen → `test_k1_2_no_hidden_cache`, `test_k1_3_key_change_takes_effect` und beide `test_k1_4_vat_…` rot; danach zurückgenommen (`git checkout`).

`pytest tests/test_revocation_606.py -rxXs`:

```
=========================== short test summary info ============================
XFAIL tests/test_revocation_606.py::test_k1_5_client_closed_after_call - Befund 606-L1, Fix offen: httpx.Client mit Bearer-Header bleibt nach dem Aufruf offen bis GC
XFAIL tests/test_revocation_606.py::test_k1_5_key_not_in_transport_error - Befund 606-L2, Fix offen: Schlüssel mit Whitespace erscheint in 'HTTP error'-Meldung
======================== 21 passed, 2 xfailed in 0.23s =========================
```

`git diff --name-only f27edbd...HEAD -- . ':!docs/contracts'`:

```
docs/reviews/2026-11-21-pruefung-widerruf/befund.md
tests/test_revocation_606.py
```

`grep -nE '_(TOKEN|KEY|SECRET) = "(lc|vat|vrt|cp)_' tests/test_revocation_606.py`:

```
(leer, Exit 1)
```

## Review data-security

- Reviewer: Agent data-security (nicht der Befund-Autor)
- Datum: 2026-11-21
- Geprüfter Commit: `680ca448eb1a73d6bd4683630ef0769f44121c6e` (Code). `git diff 680ca44 HEAD -- src` ist leer, `src/` ist also am Test-Commit `6e0437a` gleich. Den Befund habe ich im Stand der Arbeitskopie gelesen, dort hat `befund.md` noch nicht committete Änderungen.
- Urteil: freigegeben mit Auflagen

### Einstufung der Lücken
- L1: niedrig – Der Klartext-Schlüssel steht im Prozess ohnehin die ganze Laufzeit in `os.environ`, und jeder Aufruf baut einen neuen Client. Der nicht geschlossene `httpx.Client` hält den Header nur bis zur Garbage Collection und lässt Verbindungen offen; das betrifft Hygiene und Ressourcen, ändert aber weder am Widerruf noch an der Angriffsfläche etwas.
- L-Remote: hoch – Beide Plugin-Konfigurationen (`plugins/visibly-claude/.mcp.json:5-7`, `plugins/visibly-codex/.mcp.json:5-6`) schicken den Schlüssel an `mcp.visibly-ai.com`, nicht an das stdio-Paket. Dort laufen auch `vat_` und `vrt_`. Ob der Adapter Prüfungen zwischenspeichert, ist also für die meisten Nutzer offen. Laut E2 gehört das nicht zu dieser Karte und blockiert sie nicht, die Folgekarte hat aber Vorrang.

### Stellen, an denen ein Schlüssel in Werkzeugausgabe oder Fehlermeldung landen kann
- `tools/content_workflow_tools.py:156-158` `create_contentpilot_key` → `_call` (Z. 21) → `paid_tools.py:26-33` `_format_result` gibt `data` ungefiltert aus – **mittel**. Das Backend schickt den Klartext-Schlüssel `cp_` einmalig als `data.result.api_key` mit `key_delivery: "one_time"` (Backend `mcp_cms_routes.py:146-160`, Agent-Worktree `199f275`). Damit steht er dauerhaft im Transkript des MCP-Clients und in den Protokollen des LLM-Anbieters, außerhalb des Pakets. Das ist laut E6 gewollt und keine Paket-Lücke. Abhilfe: Rotation über denselben Aufruf (alter Schlüssel wird `is_active = 0`) oder `revoke_contentpilot_key`; `get_contentpilot_key_status` zeigt nur die maskierte Form (`mask_key`).
- `api_client.py:428-429` (`_post`) und `:436-437` (`_get`) bauen die Meldung `HTTP error: {e}`. Über `paid_tools.py:39` bzw. `:47` `_handle_error` (genutzt von paid, project, content_write und content_workflow) sowie `free_tools.py:279-283` `get_account_info` mit `str(e)` landet sie in der Werkzeugausgabe – **mittel, im Befund nicht erfasst**. Enthält `VISIBLYAI_API_KEY` am Ende ein Leerzeichen, `\n` oder `\r` (Kopierfehler, `.env` mit CRLF, Windows-Variable), lehnt h11 den Header ab. Die Meldung lautet `Illegal header value b'Bearer <vollständiger Schlüssel>\n'`, httpcore und httpx reichen den Text unverändert durch. Das habe ich nachgestellt: über `get_traffic_snapshot`, `get_site_health`, `create_contentpilot_key` und `get_account_info` stand der volle Schlüssel (`lc_`, genauso bei `vat_`) in der JSON-Antwort, mit `status_code: 0`. Getestet mit h11 0.16.0, httpcore 1.0.9, httpx 0.28.1; das Netz war per `httpcore.MockBackend` nachgebildet. Der Schlüssel ohne das Leerzeichen am Ende ist meist der gültige, damit gelangt ein funktionierendes Zugangsdatum ins Transkript.
- `knowledge/rag_search.py:38-39` gibt `str(e)` aus, aufgerufen von `paid_tools.py:694-695` – **mittel**. Ist der Schlüssel fehlerhaft wie oben beschrieben, tritt dort derselbe Fehler auf.
- `cli.py:194-195` (`Could not reach API: {e}`) – **niedrig**. Gleicher h11-Weg, aber die Ausgabe geht ins Terminal bzw. CI-Log des Entwicklerbefehls `sync-skills`, nicht in eine Werkzeugantwort. `cli.py:199` gibt `resp.text` des Backends aus und enthält keinen Schlüssel aus dem Paket.
- `api_client.py:68-78` `_ensure_client` bei Nicht-ASCII-Zeichen im Schlüssel: Der `UnicodeEncodeError` nennt nur Zeichen und Position. **Kein Leck** (nachgestellt).
- `api_client.py:439-444` bei 401: feste Meldung ohne Schlüssel. **Kein Leck**, belegt durch `test_k1_7_401_output_has_no_key` für 5 Pfade × `lc_`/`vat_`, die Tests sind grün.
- `api_client.py:415-420` und die `_require_key`-Varianten in den Werkzeugmodulen: Meldungen nennen nur den Namen der Variablen. **Kein Leck**.
- `api_client.py:468-491` `_parse_error_body`: übernimmt nur `detail` bzw. `msg` oder die ersten 200 Zeichen von `resp.text` des Backends. Der Schlüssel steht nur im Header, nicht im Body, und Pydantic-`input` wird nicht übernommen. **Kein Leck aus dem Paket.** Nur wenn das Backend Header zurückspiegelt, wäre es eins; das ist hier nicht prüfbar.
- Logging: Im Paket schreibt kein `logger`-Aufruf Schlüssel oder Header. Die INFO-Zeile von httpx nennt nur Methode, URL und Status. **Kein Leck**.
- `cli.py:239` `write_text` schreibt nur Skill-Inhalte. **Kein Leck**.

### Weitere Befunde / Auflagen
1. Auflage: Den h11-Weg (`api_client.py:428-429`/`:436-437`, `free_tools.py:282`, `rag_search.py:39`) als Paket-Lücke **L2** in den Befund aufnehmen. Dazu gehört genau ein Test mit `xfail(strict=True, reason="Befund 606-L2, Fix offen: Schlüssel mit Whitespace erscheint in 'HTTP error'-Meldung")`: Schlüssel mit `"\n"` am Ende, echter `httpx.HTTPTransport` mit `httpcore.MockBackend`, Erwartung „Schlüssel nicht in der Ausgabe“. Danach `-rxXs` neu laufen lassen und die Zeile „0 skipped, 0 XPASS, 2 xfailed“ im Befund ändern, sonst ist K1.5 nicht erfüllt. Fix-Idee für die Folgekarte: `api_key.strip()` beim Einlesen und keine rohen Ausnahmetexte in `APIError`.
2. Im Befund fehlt ein Hinweis, dass `test_k1_7_401_output_has_no_key` nur den Fall „401 mit sauberem Schlüssel“ abdeckt, nicht Transport- oder Protokollfehler.
3. Die Zeile zu `create_contentpilot_key` um zwei Punkte ergänzen: Der Aufruf rotiert (der alte `cp_`-Schlüssel ist danach inaktiv), und die Annotation steht auf destruktiv (`tools/annotations.py:224`).
4. Zeilennummern am Prüf-Commit stichprobenartig geprüft (config, api_client, die fünf Werkzeugmodule, classifier, cli, server, PLUGINS, README, Plugin-`.mcp.json`): alle stimmen. Ungenau ist nur `classifier.py:566`, das zeigt auf den Parameter `cache_ttl_seconds`; das Wörterbuch `_cache` steht in Z. 582. Bitte ergänzen.
5. Prüflauf bestätigt: `pytest tests/test_revocation_606.py -rxXs` ergibt 21 passed, 1 xfailed, 0 skipped, 0 XPASS. Im Test gibt es keine Schlüssel-Literale, Platzhalter entstehen zur Laufzeit.
6. Aussagen zum Widerruf bestätigt: kein Cache für Tokens oder Prüfergebnisse, neuer Client je Aufruf, 401 ohne Wiederholung, Verzögerung 0 s für jeden Aufruf, der nach dem Widerruf beginnt.
7. Nicht geprüft: Remote-Adapter, Live-Backend, Speicherung der Transkripte beim MCP-Client oder LLM-Anbieter. Die Backend-Antwort von `create_contentpilot_key` stammt aus einem Agent-Worktree von visibly-app (`199f275`), weil der Hauptklon leer ist.
8. Vorschlag für `learnings/sicherheit.md`: „httpx/h11 setzt bei ungültigem Header-Wert den vollständigen Wert in die Fehlermeldung (`Illegal header value b'Bearer …'`). Deshalb Secrets vor dem Bau des Headers mit `strip()` bereinigen und nie `str(httpx.HTTPError)` ungefiltert an Nutzer, LLM-Werkzeugausgaben oder Logs weitergeben.“

## Umsetzung der Auflagen (Befund-Autor, nach dem Review)

- Auflage 1: L2 im Abschnitt „Lücken“ und als Inventarzeile aufgenommen; Test `test_k1_5_key_not_in_transport_error` mit `xfail(strict=True)`; Lauf jetzt 21 passed, 2 xfailed, 0 skipped, 0 XPASS (Abschnitt „Prüfläufe“).
- Auflage 2: Hinweis zur Reichweite von `test_k1_7_401_output_has_no_key` im Abschnitt „Widerruf je Token-Art“ ergänzt.
- Auflage 3: Zeile `create_contentpilot_key` um Rotation und destruktive Annotation ergänzt.
- Auflage 4: Inventarzeile des TTL-Caches zeigt jetzt auf `classifier.py:582`.
- Vorschlag 8 (Learnings) liegt außerhalb dieses Repos und bleibt offen.

Urteil: Paket hält Prüfergebnisse über einen Aufruf hinaus: nein
