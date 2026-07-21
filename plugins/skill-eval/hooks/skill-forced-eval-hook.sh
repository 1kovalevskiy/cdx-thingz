#!/bin/sh
# skill-forced-eval-hook.sh - UserPromptSubmit hook for Codex.
#
# forces Codex to evaluate and use relevant skills before implementation.

printf '%s' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"'
awk 'BEGIN { first = 1 } {
    gsub(/\\/, "\\\\")
    gsub(/"/, "\\\"")
    if (!first) printf "\\n"
    printf "%s", $0
    first = 0
}' <<'EOF'
INSTRUCTION: MANDATORY SKILL ACTIVATION

Check available skills for relevance before proceeding.

IF any skills are relevant:
  1. State which skills are relevant and why (there can be multiple)
  2. Read every relevant skill's SKILL.md completely
  3. Announce that you are using each selected skill
  4. Follow all selected skill instructions, then proceed with the task

IF no skills are relevant:
  - Proceed directly

Example with multiple bundled skills:
  User asks "brainstorm this feature, then turn the approved design into an implementation plan"
  → Select: brainstorm (for collaborative design), planning make (for the implementation plan)
  → Read and follow both skills in workflow order

CRITICAL: Read and follow ALL relevant skills before implementation.
Multiple skills can and should be used when applicable.
Mentioning a skill without reading and following it is worthless.
EOF
printf '%s\n' '"}}'
