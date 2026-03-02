"""
SEO Checklists - fetched from VisiblyAI platform API.

Content is served from the platform to keep it up-to-date and not expose
plain text in the distributed package.
"""

from typing import Dict, List

import httpx

from ..config import BASE_URL

# Available types (for validation only, content comes from API)
CHECKLIST_TYPES = ["general", "blog", "ecommerce", "discover", "backlink"]


def get_checklist(checklist_type: str, language: str = "en") -> str:
    """Get a specific checklist by type and language from the platform API.

    Args:
        checklist_type: One of 'general', 'blog', 'ecommerce', 'discover', 'backlink', or 'all'
        language: 'de' or 'en' (default: 'en')

    Returns:
        Markdown formatted checklist
    """
    try:
        resp = httpx.get(
            BASE_URL + "/tools/checklist",
            params={"checklist_type": checklist_type, "language": language},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return data.get("data", "")
        return f"Failed to fetch checklist (HTTP {resp.status_code}). Check your internet connection."
    except Exception as e:
        return f"Could not fetch checklist: {e}. Ensure you have internet access."


def list_checklists() -> List[Dict[str, str]]:
    """List all available checklists with descriptions."""
    descriptions = {
        "general": "General SEO checklist covering technical foundation, indexing, OnPage, content quality, and monitoring",
        "blog": "Blog article SEO checklist for research, structure, content quality, SEO elements, and engagement",
        "ecommerce": "E-commerce SEO checklist for KPIs, keyword mapping, product pages, category pages, and link building",
        "discover": "Google Discover checklist for technical setup, content quality, visuals, and distribution",
        "backlink": "Backlink checklist for analysis, quality assessment, link building strategies, and monitoring",
    }
    return [
        {"type": ct, "description": descriptions.get(ct, "")}
        for ct in CHECKLIST_TYPES
    ]