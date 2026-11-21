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
nächsten Aufruf abgelehnt; Verzögerung 0 s. Einzige Lücke im Paket ist Hygiene: der
`httpx.Client` mit festem `Authorization`-Header wird nie geschlossen und bleibt bis zur
Garbage Collection im Speicher (L1, kein Widerrufsproblem).

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
| `classifier.py:566`, `:581-583`, `:595-620` TTL-Cache `_cache` | lokale Klassifikationsergebnisse | MD5 aus `keyword.lower()` und Markenname | 3600 s, höchstens 10 000 Einträge (`CACHE_MAX_SIZE`, Z. 21) | nein (kein Token, keine App-Antwort; Eingaben des Nutzers) | nein |
| `classifier.py:795-805` Singleton `_classifier_instance` (`global` Z. 801) | eine `KeywordClassifier`-Instanz | Modulvariable | Prozess | nein | nein |
| `cli.py:188-193` `sync_skills` | einmaliger `httpx.post` mit `Authorization: Bearer`, keine Speicherung | – | ein CLI-Lauf | ja | nein |
| `cli.py:239` `build_fallback` | schreibt nur komprimierte Skill-Inhalte nach `knowledge/skills.py` (`write_text`), keinen Schlüssel | Datei im Paket | dauerhaft (Entwicklerbefehl) | nein | nein |
| `content_workflow_tools.py:156-158` `create_contentpilot_key` (Pfad `api_client.py:29`) | Backend liefert den Klartext-`cp_`-Schlüssel; `_format_result` reicht `data` ungefiltert in die Werkzeugantwort und damit ins Transkript des MCP-Clients | Werkzeugantwort | im Paket ein Aufruf; im Transkript des MCP-Clients unbegrenzt (außerhalb des Pakets) | ja | ja (nach Widerruf per `revoke_contentpilot_key` steht der alte Klartext weiter im Transkript; gewolltes Verhalten, Einstufung durch data-security) |
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

## Lücken (K3)

Paket-Lücken, je mit einem strikten xfail-Test:

- **L1** `httpx.Client` wird nach dem Werkzeugaufruf nicht geschlossen (`api_client.py:68-82`, Aufrufer in den
  fünf Werkzeugmodulen). Der Bearer-Header mit dem Klartext-Schlüssel bleibt bis zur Garbage Collection im
  Speicher, Verbindungen im Pool bleiben offen. Kein Widerrufsproblem (jeder Aufruf baut einen neuen Client,
  die App prüft jeden Request). Test: `test_k1_5_client_closed_after_call`,
  `xfail(strict=True, reason="Befund 606-L1, Fix offen: …")`. Fix-Idee für eine Folgekarte: Werkzeug-Wrapper
  schließen den Client in `finally` oder nutzen `with VisiblyAIClient(...)`.

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

`pytest tests/test_revocation_606.py -rxXs`:

```
(wird nach dem Commit eingetragen)
```

`git diff --name-only f27edbd...HEAD -- . ':!docs/contracts'`:

```
(wird nach dem Commit eingetragen)
```

`grep -nE '_(TOKEN|KEY|SECRET) = "(lc|vat|vrt|cp)_' tests/test_revocation_606.py`:

```
(wird nach dem Commit eingetragen)
```

Urteil: Paket hält Prüfergebnisse über einen Aufruf hinaus: nein
