# Handover: FalkorDB + GraphRAG für die SEO-Wissensmigration

> Stand: 2026-06-05. Quelle der Muster: das Projekt **SkillMind**
> (`C:\Users\anton\PycharmProjects\skillmind`, public auf PyPI als `skillmind`,
> Backend produktiv auf Railway-FalkorDB). Dieses Dokument überträgt die dort
> erprobten und live verifizierten Bausteine auf die Migration der
> SEO-Wissensbasis der visibly-app.

---

## 1. Ausgangslage und Ziel

**Heute** (`src/visiblyai_mcp/knowledge/rag_search.py`):
Das MCP-Tool `rag_search` / `query_knowledge_base` ruft `POST /tools/rag-search`
auf dem visibly-app-Backend (FastAPI auf Railway) auf. Das Backend macht reine
**Vektor-Suche** über eine SEO-Wissensbasis (Blogs, Docs, Google-Guidelines).
Antwortformat pro Treffer:

```json
{ "text", "title", "url", "source", "document_type", "category", "created_at", "similarity" }
```

Die Wissensbasis ist heute eine flache Liste von Chunks. Es gibt keine
Beziehungen zwischen Dokumenten, keine Themencluster, keine Reihenfolge in
mehrstufigen Guides.

**Ziel:**
Die SEO-Wissensbasis auf einen **graph- und vektorfähigen Store (FalkorDB)**
migrieren und **GraphRAG** aktivieren, sodass die Suche nicht nur die k
ähnlichsten Chunks liefert, sondern auch über den Wissensgraphen verbundene
Inhalte (gleiches Thema, verlinkte Dokumente, nächster Schritt eines Guides).
Der MCP-Vertrag (`/tools/rag-search`, gleiches Antwortformat) bleibt unverändert,
nur das Backend dahinter wird ausgetauscht. Seit Version 0.7.0 nutzt RAG wie alle
API-Tools den globalen Backend-Pfad aus `VISIBLYAI_API_URL` in `config.py`.

**Warum GraphRAG gerade für SEO-Wissen lohnt:**
- SEO-Wissen ist stark **vernetzt** (ein Canonical-Thema berührt hreflang,
  Indexierung, interne Verlinkung). Reine Vektor-Suche verfehlt verbundene, aber
  anders formulierte Inhalte.
- Guides sind **sequenziell** (Audit-Schritt 1..n). Eine `:NEXT`-Kette erlaubt
  "zeig mir den nächsten Schritt".
- Inhalte clustern um **Entities** (Keyword, Domain, Google-Update). Diese werden
  zu Graph-Knoten und verbinden Dokumente, die kein gemeinsames Vokabular teilen.

---

## 2. Die erprobte Architektur (aus SkillMind)

Referenzdateien im SkillMind-Repo:

| Datei | Inhalt |
|---|---|
| `src/skillmind/store/falkordb_store.py` | Kompletter FalkorDB-Store: Vektor-Index, GraphRAG-Retrieval, `link_sequence`, `build_graph` |
| `src/skillmind/store/base.py` | `MemoryStore`-ABC (der Vertrag, den jeder Backend erfüllt) |
| `src/skillmind/models.py` | `Memory`, `QueryFilter`, `QueryResult` (Pydantic) |
| `src/skillmind/config.py` | `StoreConfig.falkordb_*`, `resolve_env()` |
| `src/skillmind/embeddings.py` | `EmbeddingEngine` (sentence-transformers, `all-MiniLM-L6-v2`, dim 384) |
| `src/skillmind/video/youtube_learner.py` | Ingestion at scale: Streaming, Batching, Parallel, Checkpoint/Resume |

### 2.1 Warum FalkorDB

FalkorDB ist eine Redis-basierte Graphdatenbank **mit eingebautem Vektor-Index**.
Das ist der entscheidende Punkt: ein einziger Store kombiniert Vektor-KNN
(klassisches RAG) und Graph-Traversierung (GraphRAG), ohne zwei Systeme
synchron halten zu müssen. Verifiziert gegen `falkordb/falkordb` (Graph-Modul
v41809, SDK `falkordb==1.6.1`).

**Wichtige verifizierte Eigenschaft:** Der Vektor-Index-`score` ist eine
**COSINE DISTANCE** (identische Vektoren -> ~0). Der Store exponiert daher
`similarity = 1 - distance`, damit "höher = relevanter" gilt. Diese eine Zeile
ist eine häufige Fehlerquelle, wenn man den Index neu aufsetzt.

### 2.2 Graph-Schema

Jedes Wissensstück ist ein `:Memory`-Knoten. Skalar-Properties (Embedding
bewusst ausgeschlossen, damit Reads nicht den ganzen Vektor übertragen):

```
id, type, topic, title, content, tags,
source, confidence, created_at, updated_at, expires_at, metadata_json,
embedding (vecf32, nur intern)
```

Deterministische Kanten, die beim Schreiben automatisch entstehen
(`_upsert` in `falkordb_store.py`):

```
(:Memory)-[:HAS_TOPIC]->(:Topic {name})     // ein primäres Thema je Memory
(:Memory)-[:HAS_TAG]->(:Tag {name})          // n Tags je Memory
```

Kanten, die per Pipeline materialisiert werden:

```
(:Memory)-[:RELATES_TO {kind}]->(:Memory)    // build_graph(): aus [[wikilinks]] + Vektor-Nähe
(:Memory)-[:NEXT {group_key}]->(:Memory)     // link_sequence(): feste Reihenfolge (Guide-Schritte)
```

`group_key` (z. B. die Guide-ID) wird auf jede `:NEXT`-Kante gestempelt, damit
sich beliebig viele Sequenzen denselben Graphen teilen, ohne dass die Ketten
sich verheddern.

### 2.3 Vektor-Index anlegen (idempotent)

```python
# dimension MUSS zur EmbeddingEngine passen (all-MiniLM-L6-v2 -> 384)
graph.query(
    "CREATE VECTOR INDEX FOR (m:Memory) ON (m.embedding) "
    "OPTIONS {dimension: 384, similarityFunction: 'cosine'}"
)
# CREATE wirft, wenn der Index existiert -> Exception fangen und auf
# "already"/"exist" prüfen (siehe _create_vector_index).
```

Hinweis aus `clear()`: Nach einem bulk `MATCH (n) DETACH DELETE n` re-indexiert
ein **persistierter** Vektor-Index die danach eingefügten Knoten nicht
zuverlässig. Beim vollständigen Neuaufbau daher Index **droppen und neu anlegen**.

---

## 3. Datenmodell-Mapping: SEO-Doc -> Memory

Der bestehende RAG-Treffer mappt fast 1:1 auf das `Memory`-Modell. Für die
Migration der SEO-Wissensbasis:

| RAG-Feld (heute) | Memory-Feld | Anmerkung |
|---|---|---|
| `text` | `content` | der eigentliche Chunk |
| `title` | `title` | |
| `category` | `topic` | primäres Thema -> wird `:Topic`-Knoten |
| `document_type` | `tags` (+ metadata) | z. B. `blog`, `google-guideline`, `doc` |
| `url` | `metadata.url` | im `metadata_json` |
| `source` | `source` | `import` für die Migration |
| `created_at` | `created_at` | |
| `similarity` | `QueryResult.score` | wird vom Store berechnet, nicht gespeichert |

**SEO-spezifische Erweiterung des Graphen** (über die SkillMind-Basis hinaus,
gleiches Muster wie `HAS_TOPIC`): zusätzliche Entity-Knoten, die Dokumente ohne
gemeinsames Vokabular verbinden. Empfohlen:

```
(:Memory)-[:ABOUT_KEYWORD]->(:Keyword {term})   // Ziel-Keyword des Dokuments
(:Memory)-[:ABOUT_DOMAIN]->(:Domain {host})     // behandelte Domain (Client/Wettbewerber)
(:Memory)-[:CITES]->(:Source {url})             // externe Quelle (Google-Doc, Studie)
```

Diese Knoten erweitern die Inverse-Degree-Logik (siehe 4.2) automatisch: ein
seltenes Keyword verbindet stark, ein Hub-Tag wie `seo` fast gar nicht.

---

## 4. GraphRAG-Retrieval (der Kern)

Implementiert in `_graphrag_query` / `_expand` / `_rerank` in
`falkordb_store.py`. Drei Stufen:

### 4.1 Seed -> Expand -> Re-rank

```
1. Seed:   Vektor-KNN über einen großzügigen Pool (= solide RAG-Baseline).
2. Expand: Von den Top-`seed_k` Seeds entlang gemeinsamer Topics/Tags und
           :RELATES_TO-Ketten (bis `hops`) verbundene Memories einsammeln.
3. Re-rank: Vektor-Ähnlichkeit + Graph-Nähe + Confidence kombinieren.
           Graph-only-Kandidaten bekommen aus ihrem gespeicherten Embedding
           einen fairen Vektor-Score, damit sie mitkonkurrieren.
```

Schlüssel-Cypher fürs Seeding (Vektor-KNN):

```cypher
CALL db.idx.vector.queryNodes('Memory','embedding',$k, vecf32($v))
YIELD node, score
RETURN node.id, node.title, node.content, ..., score
ORDER BY score ASC        -- score = COSINE DISTANCE, klein = ähnlich
LIMIT $limit
```

### 4.2 Das Hub-Problem (wichtigste Lektion)

Naiv verbindet jeder gemeinsame Tag zwei Dokumente gleich stark. Dann
verbindet ein Hub-Tag (z. B. `seo` auf hunderten Docs) **jeden** Seed mit
**jedem** Dokument, und der Graph-Boost ertränkt die Vektor-Ähnlichkeit.

Lösung in `_expand`: gemeinsame Topic/Tag-Kanten werden mit der **inversen
Degree** des geteilten Knotens gewichtet.

```cypher
-- Degree jedes erreichbaren Attributs (wie viele Memories teilen es)
MATCH (s:Memory) WHERE s.id IN $ids
MATCH (s)-[:HAS_TOPIC|HAS_TAG]->(a)
WITH DISTINCT a
MATCH (a)<-[:HAS_TOPIC|HAS_TAG]-(m:Memory)
RETURN id(a), count(m)
```

```python
inv = 1.0 / degree.get(aid, 1)        # seltener Tag = starkes Signal
boost[cand] += seed_sim * _ATTR_WEIGHT * inv
```

Weitere Stabilisatoren (alle in `falkordb_store.py` als Konstanten):
- `_GRAPH_WEIGHT = 0.25` — Graph-Boost ist nur Zusatz auf die Vektor-Sim.
- `_BOOST_CAP = 1.0` — gedeckelt, damit er einen starken Vektor-Treffer nie begräbt.
- Normalisierung durch die **Seed-Anzahl** -> Boost ist ein Mittel pro Seed,
  wächst nicht mit der Anzahl zufällig verbundener Seeds.
- `_HOP_DISCOUNT = 0.5` pro zusätzlichem `:RELATES_TO`-Hop.

### 4.3 Re-rank-Formel (rein, offline testbar)

```python
base  = vec_sim + GRAPH_WEIGHT * min(graph_boost, BOOST_CAP)
score = base * (0.5 + 0.5 * confidence)   # Confidence gewichtet sanft
```

`confidence` lässt sich für SEO sinnvoll belegen: Google-Guideline = 1.0,
eigener Blog = 0.8, externe Drittquelle = 0.6. Damit ranken offizielle Quellen
bei Gleichstand vor.

### 4.4 Tuning-Knöpfe (Env / Config)

```
falkordb_graphrag = true     # GraphRAG an (sonst reiner Vektor-Pfad)
falkordb_seed_k   = 5        # wie viele Vektor-Seeds vor der Graph-Expansion
falkordb_hops     = 2        # max. Traversierungstiefe (1..3)
```

Empfehlung Start: `seed_k=5`, `hops=2`. Erst Vektor-Baseline gegen GraphRAG auf
echten SEO-Queries vergleichen, dann `seed_k`/`hops` justieren.

---

## 5. Ingestion at Scale (die Migration selbst)

Die SEO-Wissensbasis ist groß. Die teuren Lektionen aus dem SkillMind-YouTube-
Learner (`youtube_learner.py`) sind 1:1 auf den Migrations-Batch übertragbar.
Diese vier Muster sind der Unterschied zwischen "läuft durch" und "hängt nach
10 Minuten und speichert nichts".

### 5.1 Streaming aller Anthropic-Calls (gegen Read-Timeouts)

Lange LLM-Calls (Zusammenfassen/Strukturieren eines Doks) laufen ohne Streaming
in HTTP-Read-Timeouts. Muster (aus der Bikefitting-App übernommen,
`eeat_claude_analyzer.py`):

```python
def _stream_text(client, prompt, model, max_tokens):
    parts = []
    with client.messages.stream(
        model=model, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            parts.append(text)
    return "".join(parts)
```

Der `anthropic.Anthropic`-Client ist **thread-safe** -> ermöglicht Parallelität
(5.3). Default-Modell für Bulk-Extraktion: Haiku 4.5
(`claude-haiku-4-5-20251001`), env-überschreibbar.

### 5.2 Batching auf ~100k Kontext-Fenster

Eingaben in Fenster von ca. 100k Token schneiden (`max_window_chars`, in
SkillMind 300_000 Zeichen ~ 100k Token), Output-Tokens moderat (4096). Nicht das
1M-Fenster nutzen — es verbrennt Cache-Budget ohne Mehrwert.

### 5.3 Parallelisierung mit ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=concurrency) as pool:   # default 6
    futs = {pool.submit(_work, item): item for item in todo}
    for fut in as_completed(futs):
        idx, result = fut.result()
        results[idx] = result
# Reihenfolge am Ende per Index wiederherstellen: [results[i] for i in sorted(results)]
```

Bei einem Shop/Backend mit Rate-Limits (vgl. die X-BIONIC-Crawl-Lektion)
`concurrency` konservativ wählen (4..6), sonst 429/403.

### 5.4 Checkpoint / Resume (kritisch bei großen Läufen)

Pro Einheit (Dokument/Kapitel) atomar auf Platte checkpointen, damit ein
Abbruch nicht alles verliert. Muster aus `youtube_learner.py`:

```python
# .skillmind/yt_progress/<job_id>.json  -> {"chapters": {idx: result}}
def _save_checkpoint(job_id, index, result):
    with self._ckpt_lock:                      # threading.Lock, da parallel
        data = self._load_checkpoint(job_id)
        data["items"][str(index)] = result
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data))
        tmp.replace(path)                       # atomar
```

Beim Start: Checkpoint laden, bereits erledigte Einheiten überspringen, nur den
Rest verarbeiten. Nach **vollständiger** Speicherung in FalkorDB den Checkpoint
löschen. Für die SEO-Migration `job_id` = Migrations-Batch-ID (z. B. Datum +
Quelle).

### 5.5 Reihenfolge-Graph nach dem Speichern

Nach dem Schreiben aller Memories eines Guides die `:NEXT`-Kette ziehen:

```python
store.link_sequence(ordered_memory_ids, rel="NEXT", group_key=guide_id)
# 24 Schritte -> 23 :NEXT-Kanten, idempotent (MERGE)
```

Verifiziert im Live-Lauf: 24 Memories -> 23 `:NEXT`-Kanten mit
`group_key=<id>`, sauber traversierbar vor-/rückwärts.

---

## 6. MCP-Integration

### 6.1 Vertrag unverändert lassen

`rag_search.py` ruft `POST {RAG_BASE_URL}/tools/rag-search` mit
`{query, top_k, category, document_type, include_external}` und erwartet
`{data: [...], credits_used, credits_remaining}`. **Dieser Vertrag bleibt.**
Im visibly-app-Backend wird nur die Implementierung hinter `/tools/rag-search`
von Vektor-Suche auf den FalkorDB-`query()` umgestellt:

```python
results = store.query(text=query, limit=top_k, filter=QueryFilter(
    topics=[category] if category else None,
    tags=[document_type] if document_type else None,
))
data = [{
    "text": r.memory.content,
    "title": r.memory.title,
    "url": r.memory.metadata.get("url", ""),
    "source": r.memory.source.value,
    "document_type": ...,            # aus tags/metadata
    "category": r.memory.topic,
    "created_at": r.memory.created_at.isoformat(),
    "similarity": r.score,           # GraphRAG-Score statt reiner Cosine-Sim
} for r in results]
```

Der Produktionsdefault zeigt bereits auf visibly-app. `VISIBLYAI_API_URL` muss
nur für Staging oder lokale Entwicklung überschrieben werden.

### 6.2 FastMCP-3.x-Stolperstein (aus SkillMind-Fix)

SkillMind hatte einen Startup-Crash auf FastMCP 3.x wegen einer
**Forward-Reference auf `Context`** in einer Tool-Signatur. Der visibly-MCP-
Server nutzt ebenfalls FastMCP. Falls beim Anbinden neuer Tools ein Startup-
Crash auftritt: Typannotation `Context` (statt `"Context"`-String) importieren
und direkt referenzieren, nicht als String-Forward-Ref. (Commit `827baf6` im
SkillMind-Repo als Referenz.)

---

## 7. Konkreter Migrationsplan

**Phase 0 — Infra**
- FalkorDB auf Railway bereitstellen (existiert bereits für SkillMind als
  Vorlage). Zugang ausschließlich über Env (`FALKORDB_URL` inkl. Passwort im
  Redis-URL, oder `FALKORDB_PASSWORD` separat). **Kein Secret ins Repo, kein
  Echo in Logs.**
- Vektor-Index mit `dimension` = Embedding-Dim der gewählten Engine anlegen.

**Phase 1 — Store-Layer portieren**
- `FalkorDBStore` + `MemoryStore`-ABC + `models.py` aus SkillMind in das
  Backend (Bikefitting `scripts/`-FastAPI bzw. visibly-app) übernehmen. Der Code
  ist backend-agnostisch geschrieben und hängt nur an `EmbeddingEngine`.
- Embedding-Engine festlegen: `all-MiniLM-L6-v2` (384, lokal, kostenlos) oder
  OpenAI-Embeddings (höhere Qualität, Kosten/Latenz). Dimension muss zum Index
  passen.

**Phase 2 — Bestandsdaten migrieren**
- Heutige RAG-Chunks -> `Memory`-Objekte (Mapping aus Abschnitt 3).
- Ingestion-Runner mit den vier Mustern aus Abschnitt 5 (Streaming/Batch/
  Parallel/Checkpoint). Bei reinen Bestands-Chunks ohne LLM-Schritt entfällt
  Streaming; Checkpoint/Parallel bleiben relevant.
- `build_graph()` einmal laufen lassen (Wikilinks + Vektor-Nähe ->
  `:RELATES_TO`). Guides per `link_sequence()` verketten.

**Phase 3 — GraphRAG aktivieren und vergleichen**
- `falkordb_graphrag=true`. Gegen einen Satz echter SEO-Queries
  Vektor-Baseline vs. GraphRAG vergleichen (Trefferqualität, nicht nur Latenz).
- `seed_k`/`hops`/`confidence`-Belegung justieren.

**Phase 4 — Cutover**
- `VISIBLYAI_API_URL` bei Bedarf für Staging setzen. MCP-Vertrag unverändert.
- Verifikation (siehe 8).

---

## 8. Betrieb, Verifikation, Fallstricke

**Verifikations-Queries** (nach der Migration, ohne Secrets auszugeben):

```cypher
MATCH (m:Memory) RETURN count(m)                                   -- Gesamtzahl
MATCH (m:Memory) WHERE m.metadata_json CONTAINS $guide RETURN count(m)
MATCH (:Memory)-[r:NEXT {group_key:$guide}]->(:Memory) RETURN count(r)
MATCH (m:Memory)-[:HAS_TOPIC]->(t:Topic) RETURN t.name, count(m) ORDER BY count(m) DESC
```

**Fallstricke aus dem SkillMind-Live-Lauf:**
1. **Cosine-DISTANCE vs. -Similarity**: `score` aus dem Vektor-Index ist eine
   Distanz. `similarity = 1 - distance`. Sonst rankt die Suche invers.
2. **Windows-Konsole / cp1252**: `print()` mit Unicode (z. B. `->` als U+2192)
   crasht auf cp1252. Reports encoding-sicher ausgeben
   (`errors="replace"`), sonst stirbt ein erfolgreicher Lauf am letzten print.
3. **Doppelte Normalisierung**: Chapter-/Chunk-Daten nur **einmal** in das
   interne Format normalisieren. Zweimal -> alle Startzeiten/Offsets kollabieren
   auf 0 (kostete in SkillMind eine Fehldiagnose).
4. **PyPI-JSON-Cache**: Nach Upload ist das JSON-API ein paar Minuten gecacht;
   gegen `/simple/<pkg>/` prüfen, nicht gegen `/pypi/<pkg>/json`.
5. **Index nach bulk delete**: persistierter Vektor-Index re-indexiert nach
   `DETACH DELETE` nicht zuverlässig -> beim Vollaufbau Index droppen + neu.
6. **Rate-Limits**: bei Quellen mit Limits `concurrency` klein halten (4..6).

**Secrets**: FalkorDB-/Redis-Passwort und API-Keys ausschließlich über Env. Das
skillmind- und das visibly-Repo sind public. Beim Verifizieren nur Zähler
ausgeben, nie URL/Passwort.

---

## 9. Was direkt portierbar ist

Aus `C:\Users\anton\PycharmProjects\skillmind\src\skillmind\`:

- `store/falkordb_store.py` — komplett (Store, GraphRAG, `link_sequence`,
  `build_graph`). Einzige Abhängigkeit: `EmbeddingEngine` + `models.py`.
- `store/base.py`, `models.py`, `config.py` (nur die `falkordb_*`-Felder +
  `resolve_env`) — direkt übernehmbar.
- Ingestion-Muster aus `video/youtube_learner.py` (`_stream_text`,
  `_save_checkpoint`/`_load_checkpoint`, ThreadPoolExecutor-Block) — als Vorlage
  für den Migrations-Runner.

Empfehlung: nicht das ganze SkillMind-Paket als Dependency ziehen, sondern den
Store-Layer als eigenes kleines Modul ins visibly-Backend kopieren (er ist
bewusst dependency-arm gehalten: `pydantic`, `falkordb`, eine Embedding-Engine).

---

*Fragen / Kontext: Antonio Blago. Live-Referenz für alle Muster ist der
SkillMind-Live-Lauf vom 2026-06-05 (Video `7xTGNNLPyMI`: 24 Kapitel-Memories +
23 `:NEXT`-Kanten in FalkorDB, GraphRAG aktiv).*
