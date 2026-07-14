#!/usr/bin/env python3
"""Validate the small YAML subset used by skill frontmatter."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
for path in ROOT.glob("plugins/*/skills/*/SKILL.md"):
    text = path.read_text()
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        errors.append(f"{path.relative_to(ROOT)}: missing frontmatter delimiters")
        continue
    front = text[4 : text.index("\n---\n", 4)]
    values = {}
    for line in front.splitlines():
        if not line.strip() or line.startswith((" ", "\t")) or ":" not in line:
            errors.append(f"{path.relative_to(ROOT)}: unsupported frontmatter line {line!r}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    if values.get("name") != path.parent.name:
        errors.append(f"{path.relative_to(ROOT)}: name must match skill directory")
    if not values.get("description"):
        errors.append(f"{path.relative_to(ROOT)}: description is required")

if errors:
    print("\n".join(errors))
    raise SystemExit(1)
print("Skill frontmatter is valid")
