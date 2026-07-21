#!/usr/bin/env python3
"""Validate the repository marketplace and all plugin manifests."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents/plugins/marketplace.json"
EXPECTED = {
    "brainstorm": "1.0.0",
    "review": "1.0.0",
    "planning": "1.0.0",
    "release-tools": "1.0.0",
    "thinking-tools": "1.0.0",
    "skill-eval": "1.0.0",
    "workflow": "1.0.0",
}
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
errors: list[str] = []


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}


market = load(MARKETPLACE)
if market.get("name") != "1kovalevskiy-cdx-thingz":
    errors.append("marketplace name must be 1kovalevskiy-cdx-thingz")
if market.get("interface", {}).get("displayName") != "cdx-thingz":
    errors.append("marketplace displayName must be cdx-thingz")

entries = market.get("plugins", [])
if [item.get("name") for item in entries] != list(EXPECTED):
    errors.append("marketplace plugin order or membership is incorrect")

for entry in entries:
    name = entry.get("name", "")
    source = entry.get("source", {})
    expected_path = f"./plugins/{name}"
    if source != {"source": "local", "path": expected_path}:
        errors.append(f"{name}: source must be local path {expected_path}")
    policy = entry.get("policy", {})
    if policy.get("installation") != "AVAILABLE" or policy.get("authentication") != "ON_INSTALL":
        errors.append(f"{name}: marketplace policy is incomplete")
    if entry.get("category") != "Developer Tools":
        errors.append(f"{name}: category must be Developer Tools")

    plugin_dir = ROOT / "plugins" / name
    manifest_path = plugin_dir / ".codex-plugin/plugin.json"
    manifest = load(manifest_path)
    if manifest.get("name") != name or plugin_dir.name != name:
        errors.append(f"{name}: folder, marketplace, and manifest names differ")
    version = manifest.get("version", "")
    if not SEMVER.fullmatch(version) or version != EXPECTED.get(name):
        errors.append(f"{name}: unexpected semver {version!r}")
    if manifest.get("author", {}).get("name") != "1kovalevskiy":
        errors.append(f"{name}: author must be 1kovalevskiy")
    interface = manifest.get("interface", {})
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category", "defaultPrompt"):
        if not interface.get(key):
            errors.append(f"{name}: interface.{key} is required")
    if name != "skill-eval" and manifest.get("skills") != "./skills/":
        errors.append(f"{name}: skills must be ./skills/")
    if "userConfig" in manifest:
        errors.append(f"{name}: userConfig is not allowed")
    for field in ("mcpServers", "apps", "assets"):
        if field in manifest:
            errors.append(f"{name}: {field} is not used by this repository")
    if manifest.get("skills") and not (plugin_dir / manifest["skills"]).is_dir():
        errors.append(f"{name}: skills path does not exist")
    hooks = plugin_dir / "hooks/hooks.json"
    if hooks.exists():
        load(hooks)

if errors:
    print("Plugin validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"Validated marketplace and {len(entries)} plugins")
