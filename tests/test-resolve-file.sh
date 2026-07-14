#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/plugins/planning/skills/exec/scripts/resolve-file.sh"
WORK="$(mktemp -d)"
HOME_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK" "$HOME_DIR"' EXIT
PATH_NAME="prompts/task.md"

run() { (cd "$WORK" && CODEX_HOME="$HOME_DIR" bash "$SCRIPT" "$PATH_NAME"); }
fail() { echo "FAIL: $1" >&2; exit 1; }

run | grep -q "Task prompt for subagent" || fail "bundled fallback not loaded"
mkdir -p "$HOME_DIR/exec-plan/prompts"
printf 'user override\n' >"$HOME_DIR/exec-plan/$PATH_NAME"
[ "$(run)" = "user override" ] || fail "user override not loaded"
mkdir -p "$WORK/.codex/exec-plan/prompts"
printf 'project override\n' >"$WORK/.codex/exec-plan/$PATH_NAME"
[ "$(run)" = "project override" ] || fail "project override should win"
: >"$WORK/.codex/exec-plan/$PATH_NAME"
[ -z "$(run)" ] || fail "empty project override should suppress fallback"
if (cd "$WORK" && CODEX_HOME="$HOME_DIR" bash "$SCRIPT" missing.txt >/dev/null 2>&1); then
    fail "missing path should fail"
fi

echo "resolve-file: PASS"
