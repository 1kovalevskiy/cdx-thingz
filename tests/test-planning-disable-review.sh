#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAUNCHER="$ROOT/plugins/planning/scripts/launch-plan-review.sh"
ANNOTATE="$ROOT/plugins/planning/scripts/plan-annotate.py"

launcher_output="$(PLANNING_DISABLE_REVDIFF=1 bash "$LAUNCHER" /tmp/nonexistent-disabled-plan.md)"
[ -z "$launcher_output" ] || { echo "FAIL: disabled launcher produced output" >&2; exit 1; }

annotate_output="$(PLANNING_DISABLE_REVDIFF=1 python3 "$ANNOTATE" /tmp/nonexistent-disabled-plan.md)"
[ -z "$annotate_output" ] || { echo "FAIL: disabled file mode produced output" >&2; exit 1; }

echo "planning disable review: PASS"
