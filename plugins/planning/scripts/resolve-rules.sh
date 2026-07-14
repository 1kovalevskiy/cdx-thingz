#!/bin/bash
# resolve custom rules file through the two-layer override chain
# usage: resolve-rules.sh <filename>
# e.g.: resolve-rules.sh planning-rules.md
#
# checks in order (first-found-wins, not merged):
#   1. .codex/<filename> (project override)
#   2. ${CODEX_HOME:-$HOME/.codex}/<filename> (user override)
#
# empty files are treated as absent and fall through to the next level
# outputs file content to stdout if found, empty output if not
# always exits 0

filename="${1:-}"
[ -n "$filename" ] || exit 0

codex_home="${CODEX_HOME:-$HOME/.codex}"

if [ -s ".codex/$filename" ]; then
    cat ".codex/$filename"
elif [ -s "$codex_home/$filename" ]; then
    cat "$codex_home/$filename"
fi
