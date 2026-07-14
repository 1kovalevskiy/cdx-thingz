#!/usr/bin/env python3
"""Guard behavior-bearing text that must survive tool-specific ports."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

MIN_LINES = {
    "plugins/brainstorm/skills/brainstorm/SKILL.md": 118,
    "plugins/brainstorm/references/usage.md": 60,
    "plugins/brainstorm/references/custom-rules.md": 45,
    "plugins/planning/skills/make/SKILL.md": 390,
    "plugins/planning/skills/exec/SKILL.md": 200,
    "plugins/planning/references/usage.md": 100,
    "plugins/planning/references/custom-rules.md": 45,
    "plugins/planning/skills/make/references/plan-review.md": 175,
    "plugins/release-tools/skills/last-tag/SKILL.md": 95,
    "plugins/release-tools/skills/new/SKILL.md": 230,
    "plugins/review/skills/git-review/SKILL.md": 105,
    "plugins/review/skills/pr/SKILL.md": 570,
    "plugins/review/skills/writing-style/SKILL.md": 165,
    "plugins/thinking-tools/skills/dialectic/SKILL.md": 80,
    "plugins/thinking-tools/skills/root-cause-investigator/SKILL.md": 115,
    "plugins/workflow/skills/clarify/SKILL.md": 210,
    "plugins/workflow/skills/learn/SKILL.md": 150,
    "plugins/workflow/skills/md-copy/SKILL.md": 40,
    "plugins/workflow/skills/txt-copy/SKILL.md": 45,
    "plugins/workflow/skills/wrong/SKILL.md": 50,
    "plugins/skill-eval/hooks/skill-forced-eval-hook.sh": 25,
}

EXPECTED = {
    "plugins/brainstorm/references/usage.md": [
        "## Triggers",
        "## Workflow Phases",
        "### Phase 1: Understand",
        "### Phase 2: Explore Approaches",
        "### Phase 3: Present Design",
        "### Phase 4: Next Steps",
        "## Examples",
        "## Key Principles",
    ],
    "plugins/brainstorm/references/custom-rules.md": [
        "## File Locations",
        "## Resolution",
        "## Managing Rules",
        "## Example Content",
        "## How Rules Apply",
    ],
    "plugins/planning/references/usage.md": [
        "## Make — `$planning:make`",
        "## Exec — `$planning:exec`",
        "### Configuration",
        "### Customization",
        "### Subagent constraint",
        "## Plan-Review — prompt",
        "## Interactive Review",
    ],
    "plugins/planning/references/custom-rules.md": [
        "## File Locations",
        "## Resolution",
        "## Managing Rules",
        "## Example Content",
        "## How Rules Apply",
    ],
    "plugins/planning/skills/make/references/plan-review.md": [
        "## Custom Rules Loading",
        "## Plan Structure Reference",
        "## Review Workflow",
        "#### Problem Definition (Critical)",
        "#### Over-Engineering Detection (Critical)",
        "#### Testing Requirements (Critical)",
        "## Output Format",
        "### Testing Coverage Assessment",
        "## When NOT to Flag",
        "## Confidence Scoring",
    ],
    "plugins/skill-eval/hooks/skill-forced-eval-hook.sh": [
        "INSTRUCTION: MANDATORY SKILL ACTIVATION",
        "Read every relevant skill's SKILL.md completely",
        "Multiple skills can and should be used when applicable",
    ],
    "plugins/review/skills/pr/SKILL.md": [
        "git fetch origin +pull/<number>/head:refs/codex-review/pr-<number>",
        "verify `git rev-parse HEAD` equals",
        "restore `<review_restore_branch>`",
    ],
}

failures = []
for relative, minimum in MIN_LINES.items():
    count = len((ROOT / relative).read_text().splitlines())
    if count < minimum:
        failures.append(f"{relative}: unexpectedly shortened to {count} lines (minimum {minimum})")

for relative, anchors in EXPECTED.items():
    text = (ROOT / relative).read_text()
    for anchor in anchors:
        if anchor not in text:
            failures.append(f"{relative}: missing behavior anchor: {anchor}")

for path in (ROOT / "plugins").rglob("*"):
    if not path.is_file():
        continue
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        continue
    if "SKILL_DIR" in text:
        failures.append(f"{path.relative_to(ROOT)}: contains undefined SKILL_DIR pseudo-variable")
    if path.name == "SKILL.md" and "Codex interactive input" in text:
        for number, line in enumerate(text.splitlines(), 1):
            normalized = line.lower()
            if "codex interactive input" not in normalized:
                continue
            if not re.search(r"\b(?:use|using)\b.*codex interactive input", normalized):
                continue
            if "do not" in normalized or "no codex interactive input" in normalized:
                continue
            if not any(term in normalized for term in ("when available", "if it is unavailable", "text fallback")):
                failures.append(
                    f"{path.relative_to(ROOT)}:{number}: interactive input has no availability/fallback guidance"
                )
    for number, line in enumerate(text.splitlines(), 1):
        if re.search(r"\b(?:bash|sh|python3)\s+[A-Z][A-Z_]+_SCRIPT\b", line):
            failures.append(
                f"{path.relative_to(ROOT)}:{number}: rendered script placeholder is not quoted"
            )
    if path.suffix == ".md":
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("#", "http://", "https://")) or target == "url":
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                failures.append(
                    f"{path.relative_to(ROOT)}: broken bundled link: {target}"
                )

if failures:
    raise SystemExit("\n".join(failures))

print("Port fidelity anchors are present")
