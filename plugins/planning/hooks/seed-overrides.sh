#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
    echo "usage: seed-overrides.sh <plugin-root> <codex-home>" >&2
    exit 1
fi

plugin_root="$1"
codex_home="$2"
target_root="$codex_home/exec-plan"

mkdir -p "$target_root/prompts" "$target_root/agents"

for source in "$plugin_root"/skills/exec/references/prompts/*.md; do
    [ -f "$source" ] || continue
    target="$target_root/prompts/$(basename "$source")"
    [ -f "$target" ] || cp "$source" "$target"
done

for source in "$plugin_root"/skills/exec/references/agents/*.txt; do
    [ -f "$source" ] || continue
    target="$target_root/agents/$(basename "$source")"
    [ -f "$target" ] || cp "$source" "$target"
done
