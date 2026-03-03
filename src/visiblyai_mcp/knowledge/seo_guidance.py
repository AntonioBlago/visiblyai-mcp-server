"""
SEO Guidance Knowledge Base - fetched from VisiblyAI platform API with offline fallback.

Content is served from the platform to keep it up-to-date. If the API is
unreachable, a compressed offline copy is used as fallback.
"""

import base64
import json
import zlib
from typing import List

import httpx

from ..config import BASE_URL

# Compressed fallback (zlib + base64) — keeps content out of plain text
_FALLBACK_DATA = (
    "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"
)


def _load_fallback():
    """Decompress embedded fallback data."""
    raw = zlib.decompress(base64.b64decode(_FALLBACK_DATA))
    return json.loads(raw.decode("utf-8"))


def get_guidance(topic: str) -> str:
    """Get SEO guidance for a specific topic.

    Tries the platform API first; falls back to embedded offline data.

    Args:
        topic: Topic key (e.g., 'title_tags', 'eeat', 'keyword_research')

    Returns:
        Markdown formatted guidance
    """
    # Try API first
    try:
        resp = httpx.get(
            BASE_URL + "/tools/guidance",
            params={"topic": topic},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return data.get("data", "")
    except Exception:
        pass

    # Fallback to embedded data
    try:
        topics = _load_fallback()
        if topic in topics:
            return topics[topic]["content"]

        # Fuzzy match
        topic_lower = topic.lower().replace(" ", "_").replace("-", "_")
        for key, data in topics.items():
            if topic_lower in key or key in topic_lower:
                return data["content"]
            if topic_lower in data["title"].lower().replace(" ", "_"):
                return data["content"]

        available = ", ".join(topics.keys())
        return f"Topic '{topic}' not found. Available topics: {available}"
    except Exception as e:
        return f"Could not load guidance: {e}"


def list_topics() -> List[dict]:
    """List all available SEO guidance topics.

    Tries API first, falls back to embedded data.
    """
    # Try API first
    try:
        resp = httpx.get(
            BASE_URL + "/tools/guidance",
            params={"topic": "list"},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return data.get("data", [])
    except Exception:
        pass

    # Fallback
    try:
        topics = _load_fallback()
        return [
            {"topic": key, "title": data["title"]}
            for key, data in topics.items()
        ]
    except Exception:
        return []


def search_guidance(query: str) -> str:
    """Search across all topics for relevant guidance.

    Note: Since content is server-side, this fetches the most relevant topic.
    Falls back to embedded data if API is unreachable.
    """
    topics = list_topics()
    if not topics:
        return "Could not fetch topics. Check your internet connection."

    # Try to find matching topic by name
    query_lower = query.lower().replace(" ", "_").replace("-", "_")
    for t in topics:
        topic_key = t.get("topic", "")
        if query_lower in topic_key or topic_key in query_lower:
            return get_guidance(topic_key)

    # Return first match or suggest listing topics
    available = ", ".join(t.get("topic", "") for t in topics)
    return f"No exact match for '{query}'. Available topics: {available}"
