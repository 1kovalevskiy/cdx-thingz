#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/plugins/brainstorm/scripts/resolve-rules.sh"
WORK="$(mktemp -d)"
HOME_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK" "$HOME_DIR"' EXIT
FILE="brainstorm-rules.md"

run() { (cd "$WORK" && CODEX_HOME="$HOME_DIR" bash "$SCRIPT" "$FILE"); }
fail() { echo "FAIL: $1" >&2; exit 1; }

[ -z "$(run)" ] || fail "missing files should be empty"
printf 'user\n' >"$HOME_DIR/$FILE"
[ "$(run)" = user ] || fail "user rules not loaded"
mkdir -p "$WORK/.codex"
printf 'project\n' >"$WORK/.codex/$FILE"
[ "$(run)" = project ] || fail "project rules should win"
: >"$WORK/.codex/$FILE"
[ "$(run)" = user ] || fail "empty project rules should use user fallback"
rm -f "$WORK/.codex/$FILE"
[ "$(run)" = user ] || fail "user fallback not restored"
[ -z "$(cd "$WORK" && CODEX_HOME="$HOME_DIR" bash "$SCRIPT")" ] || fail "missing filename should be empty"

echo "brainstorm resolve-rules: PASS"
