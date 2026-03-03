"""
SEO Checklists - fetched from VisiblyAI platform API with offline fallback.

Content is served from the platform to keep it up-to-date. If the API is
unreachable, a compressed offline copy is used as fallback.
"""

import base64
import json
import zlib
from typing import Dict, List

import httpx

from ..config import BASE_URL

# Available types (for validation only, content comes from API)
CHECKLIST_TYPES = ["general", "blog", "ecommerce", "discover", "backlink"]

# Compressed fallback (zlib + base64) — keeps content out of plain text
_FALLBACK_DATA = (
    "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"
)


def _load_fallback() -> Dict[str, Dict[str, str]]:
    """Decompress embedded fallback data."""
    raw = zlib.decompress(base64.b64decode(_FALLBACK_DATA))
    return json.loads(raw.decode("utf-8"))


def get_checklist(checklist_type: str, language: str = "en") -> str:
    """Get a specific checklist by type and language.

    Tries the platform API first; falls back to embedded offline data.

    Args:
        checklist_type: One of 'general', 'blog', 'ecommerce', 'discover', 'backlink', or 'all'
        language: 'de' or 'en' (default: 'en')

    Returns:
        Markdown formatted checklist
    """
    # Try API first
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
    except Exception:
        pass

    # Fallback to embedded data
    try:
        checklists = _load_fallback()
        lang = "de" if language.lower().startswith("de") else "en"

        if checklist_type == "all":
            parts = []
            for ct in CHECKLIST_TYPES:
                if ct in checklists:
                    parts.append(checklists[ct][lang])
            return "\n---\n".join(parts) if parts else "No checklists available."

        if checklist_type in checklists:
            return checklists[checklist_type][lang]

        available = ", ".join(list(checklists.keys()) + ["all"])
        return f"Unknown checklist type '{checklist_type}'. Available: {available}"
    except Exception as e:
        return f"Could not load checklist: {e}"


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
