"""CLI commands for visiblyai-mcp-server.

Usage:
    visiblyai-mcp-server sync-skills [path]   Push local skills to platform API
    visiblyai-mcp-server build-fallback [path] Compress skills into offline fallback
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


def _parse_frontmatter(content: str) -> str:
    """Extract description from YAML frontmatter."""
    if not content.startswith("---"):
        return ""
    parts = content.split("---", 2)
    if len(parts) < 3:
        return ""
    # Simple YAML parsing without pyyaml dependency
    for line in parts[1].strip().splitlines():
        line = line.strip()
        if line.startswith("description:"):
            desc = line[len("description:"):].strip()
            # Remove surrounding quotes
            if (desc.startswith('"') and desc.endswith('"')) or \
               (desc.startswith("'") and desc.endswith("'")):
                desc = desc[1:-1]
            return desc
    return ""


def _find_skills_dir(skills_dir: str | None = None) -> Path:
    """Locate the skills directory."""
    if skills_dir:
        p = Path(skills_dir)
        if p.exists():
            return p
        print(f"Error: Skills directory not found: {p}")
        sys.exit(1)

    # Default: .claude/skills/ relative to CWD
    p = Path.cwd() / ".claude" / "skills"
    if p.exists():
        return p

    # Try relative to package location
    p = Path(__file__).parent.parent.parent.parent / ".claude" / "skills"
    if p.exists():
        return p

    print("Error: Skills directory not found. Provide path as argument.")
    sys.exit(1)


def _load_skills(skills_path: Path) -> list[dict]:
    """Read and parse all skill markdown files."""
    md_files = sorted(skills_path.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {skills_path}")
        sys.exit(1)

    skills = []
    for f in md_files:
        content = f.read_text(encoding="utf-8")
        skills.append({
            "name": f.stem,
            "description": _parse_frontmatter(content),
            "content": content,
            "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        })
    return skills


def sync_skills(skills_dir: str | None = None):
    """Push local .claude/skills/*.md files to the platform API."""
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
