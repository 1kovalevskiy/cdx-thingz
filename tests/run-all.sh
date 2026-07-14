#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 tests/validate-codex-plugins.py
python3 tests/validate-frontmatter.py
python3 tests/test-no-claude-runtime.py
python3 tests/test-port-fidelity.py

if command -v shellcheck >/dev/null 2>&1; then
    find plugins tests -name '*.sh' -print0 | xargs -0 shellcheck
else
    echo "shellcheck not installed; skipping local ShellCheck"
fi

for test_file in tests/test-*.sh; do
    bash "$test_file"
done

python3 plugins/planning/scripts/plan-annotate.py --test
python3 plugins/review/skills/git-review/scripts/git-review.py --test
