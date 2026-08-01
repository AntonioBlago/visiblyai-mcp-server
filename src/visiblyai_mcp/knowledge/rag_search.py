"""RAG knowledge-base search through the shared visibly-app API client."""

from __future__ import annotations

from typing import Optional


def search_rag(
    client,
    query: str,
    top_k: int = 5,
    category: Optional[str] = None,
    document_type: Optional[str] = None,
    include_external: bool = True,
) -> dict:
    """
    Search the SEO knowledge base (blogs, docs, Google guidelines).

    Returns dict with keys:
        results: list of {text, title, url, source, document_type, category, created_at, similarity}
        credits_used: int
        credits_remaining: int
        error: str (only on failure)
    """
    try:
        data = client.rag_search(
            query=query,
            top_k=top_k,
            category=category,
            document_type=document_type,
            include_external=include_external,
        )
        return {
            "results": data.get("data", []),
            "credits_used": data.get("credits_used", 2),
            "credits_remaining": data.get("credits_remaining"),
        }
    except Exception as e:
        return {"results": [], "error": str(e)}
