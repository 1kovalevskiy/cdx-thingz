#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/plugins/planning/hooks/seed-overrides.sh"
CODEX_TEST_HOME="$(mktemp -d)"
trap 'rm -rf "$CODEX_TEST_HOME"' EXIT

sh "$SCRIPT" "$ROOT/plugins/planning" "$CODEX_TEST_HOME"

test -f "$CODEX_TEST_HOME/exec-plan/prompts/task.md"
test -f "$CODEX_TEST_HOME/exec-plan/prompts/review.md"
test -f "$CODEX_TEST_HOME/exec-plan/agents/quality.txt"
test -f "$CODEX_TEST_HOME/exec-plan/agents/smells.txt"

printf 'custom task prompt\n' >"$CODEX_TEST_HOME/exec-plan/prompts/task.md"
sh "$SCRIPT" "$ROOT/plugins/planning" "$CODEX_TEST_HOME"
[ "$(cat "$CODEX_TEST_HOME/exec-plan/prompts/task.md")" = "custom task prompt" ]

echo "planning seed overrides: PASS"
