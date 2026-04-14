"""CLI commands for visiblyai-mcp-server.

Usage:
    visiblyai-mcp-server sync-skills [path]   Push local skills to platform API
    visiblyai-mcp-server build-fallback [path] Compress skills into offline fallback

Skill source:  ``seo_skills/skills/*/SKILL.md`` (gitagent-style directories)
               or ``*.md`` flat files (legacy).
"""

import base64
import hashlib
import json
import re
import sys
import zlib
from pathlib import Path

import httpx

from .config import BASE_URL, get_api_key


# ---------------------------------------------------------------------------
# Frontmatter parsing (no pyyaml dependency)
# ---------------------------------------------------------------------------

def _parse_frontmatter(content: str) -> dict[str, object]:
    """Extract metadata from YAML frontmatter (simple line-by-line parser).

    Returns a dict with string values and a ``triggers`` list.
    """
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    result: dict[str, object] = {}
    current_list_key: str | None = None
    current_list: list[str] = []

    for line in parts[1].strip().splitlines():
        stripped = line.strip()

        # List item (indented "- value")
        if stripped.startswith("- ") and current_list_key:
            val = stripped[2:].strip().strip('"').strip("'")
            if val != "[]":
                current_list.append(val)
            continue

        # Close previous list
        if current_list_key:
            result[current_list_key] = current_list
            current_list_key = None
            current_list = []

        if ":" not in stripped:
            continue

        key, _, raw_val = stripped.partition(":")
        key = key.strip()
        raw_val = raw_val.strip()

        # Value on same line
        if raw_val and raw_val != "[]":
            # Remove surrounding quotes
            if (raw_val.startswith('"') and raw_val.endswith('"')) or \
               (raw_val.startswith("'") and raw_val.endswith("'")):
                raw_val = raw_val[1:-1]
            # Boolean
            if raw_val.lower() == "true":
                result[key] = True
            elif raw_val.lower() == "false":
                result[key] = False
            # Integer
            elif raw_val.isdigit():
                result[key] = int(raw_val)
            else:
                result[key] = raw_val
        elif raw_val == "[]":
            result[key] = []
        else:
            # Start of a list on following lines
            current_list_key = key
            current_list = []

    # Close final list
    if current_list_key:
        result[current_list_key] = current_list

    return result


# ---------------------------------------------------------------------------
# Skill discovery
# ---------------------------------------------------------------------------

def _find_skills_dir(skills_dir: str | None = None) -> Path:
    """Locate the skills directory."""
    if skills_dir:
        p = Path(skills_dir)
        if p.exists():
            return p
        print(f"Error: Skills directory not found: {p}")
        sys.exit(1)

    # Prefer seo_skills/skills/ (gitagent-style directories)
    p = Path.cwd() / "seo_skills" / "skills"
    if p.exists():
        return p

    # Legacy: .claude/skills/ flat files
    p = Path.cwd() / ".claude" / "skills"
    if p.exists():
        return p

    # Try relative to package location
    for sub in ("seo_skills/skills", ".claude/skills"):
        p = Path(__file__).parent.parent.parent.parent / sub
        if p.exists():
            return p

    print("Error: Skills directory not found. Provide path as argument.")
    sys.exit(1)


def _load_skills(skills_path: Path) -> list[dict]:
    """Read and parse all skill files (directory or flat layout).

    Supports:
    - ``seo_skills/skills/*/SKILL.md``  (gitagent directories)
    - ``*.md``                           (legacy flat files)
    """
    # Try directory layout first (flat or nested by category)
    dir_skills = sorted(skills_path.glob("**/SKILL.md"))
    if dir_skills:
        md_files = dir_skills
    else:
        md_files = sorted(skills_path.glob("*.md"))

    if not md_files:
        print(f"No skill files found in {skills_path}")
        sys.exit(1)

    skills = []
    for f in md_files:
        content = f.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        name = fm.get("name", f.parent.name if f.name == "SKILL.md" else f.stem)

        skill = {
            "name": name,
            "description": fm.get("description", ""),
            "content": content,
            "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            # Extended metadata from frontmatter
            "label_de": fm.get("label_de", ""),
            "label_en": fm.get("label_en", ""),
            "category": fm.get("category", "seo-analysis"),
            "credits_estimate": int(fm.get("credits_estimate", 0)),
            "orchestrable": bool(fm.get("orchestrable", False)),
            "triggers": fm.get("triggers", []),
            "related_agent_workflows": fm.get("related_agent_workflows", []),
        }
        skills.append(skill)
    return skills


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def sync_skills(skills_dir: str | None = None):
    """Push local skills to the platform API with full metadata."""
    api_key = get_api_key()
    if not api_key:
        print("Error: VISIBLYAI_API_KEY not set")
        sys.exit(1)

    skills_path = _find_skills_dir(skills_dir)
    skills = _load_skills(skills_path)

    print(f"Syncing {len(skills)} skills from {skills_path}...")

    try:
        resp = httpx.post(
            BASE_URL + "/tools/skills/sync",
            json={"skills": skills},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )
    except Exception as e:
        print(f"Error: Could not reach API: {e}")
        sys.exit(1)

    if resp.status_code != 200:
        print(f"Error: API returned {resp.status_code}: {resp.text}")
        sys.exit(1)

    data = resp.json()
    if not data.get("success"):
        print(f"Error: {data.get('error', 'Unknown')}")
        sys.exit(1)

    print(f"Done: {data.get('synced', 0)} updated, {data.get('unchanged', 0)} unchanged")
    for detail in data.get("details", []):
        status = detail.get("status", "?")
        print(f"  {detail['name']}: {status}")


def build_fallback(skills_dir: str | None = None):
    """Compress local skills into the _FALLBACK_DATA blob for offline use."""
    skills_path = _find_skills_dir(skills_dir)
    skills = _load_skills(skills_path)

    skills_data = {}
    for s in skills:
        skills_data[s["name"]] = {
            "description": s["description"],
            "content": s["content"],
        }

    raw = json.dumps(skills_data, ensure_ascii=False).encode("utf-8")
    compressed = base64.b64encode(zlib.compress(raw, 9)).decode("ascii")

    target = Path(__file__).parent / "knowledge" / "skills.py"
    if not target.exists():
        print(f"Error: Target file not found: {target}")
        sys.exit(1)

    source = target.read_text(encoding="utf-8")
    new_source = re.sub(
        r'_FALLBACK_DATA = "[^"]*"',
        f'_FALLBACK_DATA = "{compressed}"',
        source,
    )
    target.write_text(new_source, encoding="utf-8")
    print(f"Updated fallback in {target} ({len(compressed)} chars, {len(skills)} skills)")
