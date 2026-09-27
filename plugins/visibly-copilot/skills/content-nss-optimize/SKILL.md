---
name: content-nss-optimize
description: Write or revise an article with Claude or another external agent, iteratively measure and improve its Visibly NSS score, and hand the finished draft to the Visibly editor without paid Visibly text generation.
---

# Write, measure and improve with Visibly

Use the connected Visibly MCP tools. Tool prefixes differ between clients; discover the exact names in the connected server. The agent writes and revises the text using its own model. Visibly supplies project context, analysis, deterministic feedback and draft storage.

## Target and costs

- Use the requested NSS target, normally 70 or 80; default to **80** if none was specified. A target is not a guaranteed outcome.
- Existing context, `score_text` and draft saving cost **0 Visibly credits**. The external agent's own token or subscription costs still apply.
- A new SERP/content analysis via `create_content_query` is separately paid and requires `spending:execute`. Use an existing ready query when available. Only start a paid analysis within the user's authorized research scope and budget; otherwise explain the missing prerequisite.
- Do not call `generate_article_from_query`, `regenerate_content_article`, `optimize_content_draft`, `run_content_optimizer`, or queue an article for this workflow. The agent performs the revisions itself. Publishing is a separate user request.

## Establish the context

1. Resolve the project and article/query from the user's selection using `list_projects`, `get_project`, `list_content_queries`, `get_content_query`, `get_content_status` and `get_content_briefing` as needed. Reuse the selected editor query, language, country, keyword, persona, brand rules and revision. Read all relevant paginated draft/article content, not only the first page.
2. For an existing article, use `get_article(include_content=true)` and retain its article id and revision. Do not create a second article. If a ready analysis is missing, wait for an already running analysis or arrange the authorized analysis. A missing NSS (`nss_unavailable_reason`) is **unavailable**, not zero.
3. Read the actual briefing: search intent, required terms and their ranges, heading terms, entities, reader questions, length and structural targets. Use supplied brand facts, tone, persona and page-type requirements. If required brand/template context is unavailable through the tools, request it instead of inventing it.
4. Find relevant real internal targets using `list_pages` and `get_internal_links`. Use descriptive anchors, preserve existing useful links, and cite relevant external sources for factual claims. Do not invent URLs or claim link availability was checked when it was not. NSS is not a broken-link validator; check links separately with available browsing/URL tools.

## Bounded improvement loop

Write the first complete draft, or keep the current text as the baseline. Use one format consistently, preferably HTML so headings, paragraphs and links are explicit.

Call `score_text(project_id, query_id, content, format, persona_id)` with the **whole candidate text**. Read the actual NSS at `data.nss.scores.nss` (some clients unwrap `data`). Keep the query, persona and analysis unchanged between rounds so scores remain comparable. Do not substitute AI-visibility, heuristic SEO or brand scores for NSS.

For each revision:

1. Record the measured NSS and inspect the returned heading, term, entity, fan-out, structure, readability, style, brand and overoptimization feedback.
2. Choose the few changes most likely to help the reader and address measured gaps. Improve heading hierarchy and intent, answer missing questions, use entities naturally, clarify difficult passages, and add relevant verified links. Avoid keyword stuffing and unsupported facts even if they could increase a score.
3. Rewrite those passages with the agent's own model. Re-score the complete candidate with `score_text`.
4. Retain the best measured draft that still meets the factual and editorial requirements. Discard regressions. Track round, NSS and material changes.

Stop when the requested target is reached and the editorial/link checks pass, after **five revision rounds**, after **two consecutive rounds without improving the best NSS**, or when a required tool/context is unavailable. Respect a different explicit user limit. At a plateau, retain the best draft and report its actual score and remaining gaps. Never invent a score, silently lower the target, promise rankings, or start paid generation to reach it.

## Save, verify and open

- New article: call `submit_article_draft` with the existing query id, matching keyword/country/language/persona and current `expected_query_revision`. Pass `expected_article_revision` when the query already references an editable draft. Use a stable idempotency key for retries of identical content; a changed payload needs a new operation key.
- Existing article: use `update_article` for draft/rejected articles or `edit_content_article` for another supported editable status, with the current `expected_revision`. Saving is not publishing. On a revision conflict, read the current version and reconcile it with the user instead of overwriting newer work.
- Read the stored article back using `get_article(include_content=true)` including every page. Re-score the **stored, sanitized text** with the same query. Report that final measured score; do not report a pre-save score as the saved result if sanitization changed the text. Count any further revisions against the same limit.
- Show the returned `editor_url` as a clickable link. For an existing article update, use the connected Visibly app's article-editor route `/tools/content/creation/{project_id}/editor?article={article_id}`. Open it with a browser tool only when supported and requested. The editor loads the text and automatically scores it against the ready query; the MCP cannot force a browser tab to open in every client.
- Finish with the article link, initial and final NSS, number of revisions, main improvements, any remaining blockers, and actual separately incurred analysis credits. Do not publish or approve the article as a side effect of optimization.
