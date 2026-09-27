"""Validate and build the public plugin ZIPs using only the standard library."""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = {
    "claude": ".claude-plugin/plugin.json",
    "codex": ".codex-plugin/plugin.json",
    "copilot": "plugin.json",
}


def build(output: Path, sync_skills: bool = False) -> None:
    canonical = (ROOT / "skills/content-nss-optimize/SKILL.md").read_bytes()
    bundles = []
    for client, manifest_path in MANIFESTS.items():
        folder = ROOT / "plugins" / f"visibly-{client}"
        manifest = json.loads((folder / manifest_path).read_text(encoding="utf-8"))
        skill = folder / "skills/content-nss-optimize/SKILL.md"
        if sync_skills:
            skill.write_bytes(canonical)
        if skill.read_bytes() != canonical:
            raise ValueError(f"Stale skill in {folder.name}; run with --sync-skills")
        if manifest["name"] != folder.name or manifest["version"] != "1.0.0":
            raise ValueError(f"Unexpected plugin identity/version: {folder.name}")
        paths = [manifest_path, "README.md", "skills/content-nss-optimize/SKILL.md"]
        if "mcpServers" in manifest:
            config_path = manifest["mcpServers"]
            server = json.loads((folder / config_path).read_text(encoding="utf-8"))["mcpServers"]["visiblyai"]
            if server["url"] != "https://mcp.visibly-ai.com/mcp":
                raise ValueError(f"Unexpected MCP host: {folder.name}")
            if client == "codex":
                if server.get("bearer_token_env_var") != "VISIBLYAI_API_KEY":
                    raise ValueError("Codex must read the key from the environment")
            elif server.get("headers") != {"Authorization": "Bearer ${VISIBLYAI_API_KEY}"}:
                raise ValueError("Claude must read the key from the environment")
            paths.append(config_path.removeprefix("./"))
        bundles.append((folder, paths))

    for catalog in (".claude-plugin/marketplace.json", ".github/plugin/marketplace.json", ".agents/plugins/marketplace.json"):
        market = json.loads((ROOT / catalog).read_text(encoding="utf-8"))
        for plugin in market["plugins"]:
            source = plugin["source"]
            source = source["path"] if isinstance(source, dict) else source
            if source != f"./plugins/{plugin['name']}" or not (ROOT / source).is_dir():
                raise ValueError(f"Invalid marketplace source: {catalog}")

    output.mkdir(parents=True, exist_ok=True)
    checksums = []
    for folder, paths in bundles:
        archive = output / f"{folder.name}-1.0.0.zip"
        # Explicit allowlist: local credentials, caches and build output cannot enter ZIPs.
        with ZipFile(archive, "w", compression=ZIP_DEFLATED) as handle:
            for relative in sorted(paths):
                info = ZipInfo(relative, date_time=(2026, 9, 27, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                handle.writestr(info, (folder / relative).read_bytes())
        with ZipFile(archive) as handle:
            if handle.testzip() is not None or sorted(handle.namelist()) != sorted(paths):
                raise ValueError(f"Invalid archive: {archive.name}")
        checksums.append(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}")
        print(archive)
    (output / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist/plugins-1.0.0")
    parser.add_argument("--sync-skills", action="store_true", help="Refresh bundled skills from the canonical source")
    args = parser.parse_args()
    build(args.output, args.sync_skills)
