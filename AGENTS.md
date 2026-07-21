# AGENTS.md

Guidance for Codex when working in this repository.

## Purpose

`cdx-thingz` is a Codex-only marketplace of independent plugins containing skills, hooks, scripts, and references. It is an MIT-licensed Codex port of Umputun's `cc-thingz`; preserve that attribution.

## Repository rules

- Keep `README.md` current whenever a component, script, configuration surface, or usage flow changes.
- Keep all shipped content generic. Never hardcode personal paths, editor preferences, credentials, or machine-specific settings; use documented environment variables.
- Documentation must be self-contained and refer only to capabilities shipped by this repository or public Codex surfaces.
- Resolve bundled skill files relative to the calling `SKILL.md`. Use `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` only in hook commands where Codex supplies them.
- Use `$plugin:skill` for explicit skill examples while preserving natural-language activation.
- Do not add MCP servers, apps, or visual assets unless a feature actually requires them.

## Packaging and versions

- Marketplace catalog: `.agents/plugins/marketplace.json`.
- Plugin manifest: `plugins/<name>/.codex-plugin/plugin.json`.
- Standard plugin content lives in `skills/`, `hooks/`, `scripts/`, and `references/` as needed.
- Each plugin versions independently with semver. Any change to bundled consumer content requires that plugin's version bump.
- Every plugin keeps its own semantic version in `.codex-plugin/plugin.json`; bump it whenever bundled plugin content changes.
- Cross-plugin skill references use `$plugin:skill`.

## Current plugins

- `brainstorm` — collaborative design.
- `review` — PR, local diff, and writing-style review.
- `planning` — plan creation, explicit editor review, sequential execution, and a `SessionStart` bootstrap for editable prompt/reviewer overrides.
- `release-tools` — release preparation and last-tag summaries.
- `thinking-tools` — dialectic and root-cause analysis.
- `skill-eval` — skill-selection reminder hook.
- `workflow` — knowledge capture, clarification, course correction, and clipboard helpers.

## Planning constraints

- The main task owns orchestration. Run only one implementation agent at a time.
- Independent read-only reviewers may run in parallel from the main task.
- Never add nested agent orchestration to a leaf-agent prompt.
- Never invoke another Codex process for an independent second opinion.
- Use the existing Codex Worktree. Do not create hidden nested worktrees.
- Git and Mercurial execution remain supported; Git-only finalization is skipped on Mercurial.

## Custom rules

- Project rules: `.codex/brainstorm-rules.md` and `.codex/planning-rules.md`.
- User rules: `${CODEX_HOME:-$HOME/.codex}/brainstorm-rules.md` and `planning-rules.md`.
- Exec overrides: `.codex/exec-plan/`, then `${CODEX_HOME:-$HOME/.codex}/exec-plan/`, then bundled defaults.
- Resolution uses the first non-empty rules file and never merges layers.

## Testing

Run all repository checks before handoff:

```bash
bash tests/run-all.sh
```

Python helpers also expose embedded tests, including:

```bash
python3 plugins/planning/scripts/plan-annotate.py --test
python3 plugins/review/skills/git-review/scripts/git-review.py --test
```
