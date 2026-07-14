#!/usr/bin/env python3
"""Reject legacy runtime contracts outside explicitly historical material."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
targets = [ROOT / ".agents", ROOT / "plugins", ROOT / "tests", ROOT / "README.md", ROOT / "AGENTS.md"]
parts = [
    "." + "claude",
    "CLAUDE" + "_",
    "CLAUDE" + ".md",
    "AskUser" + "Question",
    "EnterPlan" + "Mode",
    "EnterWork" + "tree",
    "Task" + "Create",
    "Skill" + "()",
    "codex" + " exec",
]
skip = {Path(__file__).resolve()}
failures: list[str] = []

files: list[Path] = []
for target in targets:
    files.extend(target.rglob("*") if target.is_dir() else [target])

for path in files:
    if not path.is_file() or path in skip or ".git" in path.parts:
        continue
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        continue
    for token in parts:
        if token in text:
            line = text[: text.index(token)].count("\n") + 1
            failures.append(f"{path.relative_to(ROOT)}:{line}: forbidden token {token!r}")

if failures:
    print("\n".join(failures))
    raise SystemExit(1)
print("No legacy runtime contracts found")
