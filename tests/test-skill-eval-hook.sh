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
python3 - "$output" <<'PY'
import json, sys

data = json.loads(sys.argv[1])
hook_output = data["hookSpecificOutput"]
assert hook_output["hookEventName"] == "UserPromptSubmit"
context = hook_output["additionalContext"]
assert "Read every relevant skill's SKILL.md completely" in context
assert "Announce that you are using each selected skill" in context
assert "Follow all selected skill instructions" in context
PY
echo "skill-eval hook: PASS"
