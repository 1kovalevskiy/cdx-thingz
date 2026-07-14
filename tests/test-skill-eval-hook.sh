#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS="$ROOT/plugins/skill-eval/hooks/hooks.json"
SCRIPT="$ROOT/plugins/skill-eval/hooks/skill-forced-eval-hook.sh"

python3 - "$HOOKS" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
command = data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
assert command == 'sh "${PLUGIN_ROOT}/hooks/skill-forced-eval-hook.sh"'
PY

output="$(sh "$SCRIPT")"
grep -q "Read every relevant skill's SKILL.md completely" <<<"$output"
grep -q "Announce that you are using each selected skill" <<<"$output"
grep -q "Follow all selected skill instructions" <<<"$output"
echo "skill-eval hook: PASS"
