"""
SEO Guidance Knowledge Base - fetched from VisiblyAI platform API.

Content is served from the platform to keep it up-to-date and not expose
plain text in the distributed package.
"""

from typing import List

import httpx

from ..config import BASE_URL


def get_guidance(topic: str) -> str:
    """Get SEO guidance for a specific topic from the platform API.

    Args:
        topic: Topic key (e.g., 'title_tags', 'eeat', 'keyword_research')

    Returns:
        Markdown formatted guidance
    """
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
        return f"Failed to fetch guidance (HTTP {resp.status_code}). Check your internet connection."
    except Exception as e:
        return f"Could not fetch guidance: {e}. Ensure you have internet access."


def list_topics() -> List[dict]:
    """List all available SEO guidance topics from the platform API."""
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
        return []
    except Exception:
        return []


def search_guidance(query: str) -> str:
    """Search across all topics for relevant guidance.

    Note: Since content is server-side, this fetches the most relevant topic.
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