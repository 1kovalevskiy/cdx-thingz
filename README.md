# cdx-thingz

Opinionated plugins and skills for OpenAI Codex, packaged as a repository marketplace. This is the Codex port of [umputun/cc-thingz](https://github.com/umputun/cc-thingz); original authorship remains credited to Umputun and the project remains MIT-licensed.

## Install

Add the marketplace:

```bash
codex plugin marketplace add 1kovalevskiy/cdx-thingz
```

Install any plugin:

```bash
codex plugin add brainstorm@1kovalevskiy-cdx-thingz
codex plugin add review@1kovalevskiy-cdx-thingz
codex plugin add planning@1kovalevskiy-cdx-thingz
codex plugin add release-tools@1kovalevskiy-cdx-thingz
codex plugin add thinking-tools@1kovalevskiy-cdx-thingz
codex plugin add skill-eval@1kovalevskiy-cdx-thingz
codex plugin add workflow@1kovalevskiy-cdx-thingz
```

The `skill-eval` plugin contains a `UserPromptSubmit` hook. Codex asks you to trust plugin hooks separately after installation; review the hook before enabling it. Start a new task after installing or updating plugins.

## Plugins

| Plugin | Skills / behavior |
|---|---|
| `brainstorm` | `$brainstorm:brainstorm` — collaborative design and approach comparison |
| `review` | `$review:pr`, `$review:git-review`, `$review:writing-style` |
| `planning` | `$planning:make`, `$planning:exec` |
| `release-tools` | `$release-tools:new`, `$release-tools:last-tag` |
| `thinking-tools` | `$thinking-tools:dialectic`, `$thinking-tools:root-cause-investigator` |
| `skill-eval` | reminds Codex to evaluate and fully read relevant skills |
| `workflow` | `$workflow:learn`, `$workflow:clarify`, `$workflow:wrong`, `$workflow:md-copy`, `$workflow:txt-copy` |

Natural-language activation also works. The explicit form is `$plugin:skill`.

### Planning configuration

| Variable | Default |
|---|---:|
| `PLANNING_PLANS_DIR` | `docs/plans` |
| `PLANNING_TASK_RETRIES` | `1` |
| `PLANNING_REVIEW_ITERATIONS` | `5` |
| `PLANNING_FINALIZE_ENABLED` | `1` |
| `PLANNING_DISABLE_REVDIFF` | unset; set to any non-empty value to skip local editor overlays |

Planning rules resolve from `.codex/planning-rules.md`, then `${CODEX_HOME:-$HOME/.codex}/planning-rules.md`. Brainstorm rules use the analogous `brainstorm-rules.md` paths. Exec prompt overrides resolve from `.codex/exec-plan/`, then `${CODEX_HOME:-$HOME/.codex}/exec-plan/`, then bundled defaults.

`$planning:exec` runs one implementation agent at a time and uses parallelism only for independent read-only reviews. It uses the Worktree already selected for the Codex task and never creates a hidden nested worktree. Detached Codex worktrees skip rebase/squash and finish with a suggested branch/Create branch action. Mercurial execution is supported in place; Git-only finalization is skipped.

### Knowledge capture

`$workflow:learn` sends team-wide repository guidance to the applicable project `AGENTS.md`. Personal preferences and machine-specific context go to Codex Local Memories through the native Codex memory surface. It never substitutes repository dotfiles for Local Memories and never saves secrets or transient debugging state.

### Editor overlays

Planning and local-diff review can use `revdiff`, agterm, tmux, zellij, kitty, wezterm-compatible terminals, and other backends supported by the bundled launchers. Overlays are available only in suitable local terminal environments. In Codex app, cloud, or IDE tasks without a visible overlay, the skills show the plan or diff and collect feedback in chat. No automatic plan-exit hook is installed.

## Local development

Validate the repository, then add this checkout as a marketplace:

```bash
bash tests/run-all.sh
codex plugin marketplace add "$(pwd)"
```

After editing bundled plugin content, bump that plugin's version. Refresh a Git marketplace snapshot, then reinstall the changed plugin instead of editing cache directories:

```bash
codex plugin marketplace upgrade 1kovalevskiy-cdx-thingz
codex plugin remove planning@1kovalevskiy-cdx-thingz
codex plugin add planning@1kovalevskiy-cdx-thingz
codex plugin list
```

For a local-path marketplace, skip the upgrade command but still remove and add the plugin so its versioned cache is rebuilt. Verify behavior in a new task.

## Manual fallback

Without marketplace installation, copy individual skill directories into `~/.agents/skills/`. Keep each `SKILL.md` together with its `scripts/` and `references/` siblings so relative resolution continues to work.

For `skill-eval`, copy the hook script to a stable location and merge its `UserPromptSubmit` entry from `plugins/skill-eval/hooks/hooks.json` into `~/.codex/hooks.json`, replacing `${PLUGIN_ROOT}` with that installed location. Review and trust the hook before enabling it.

## Tests

```bash
bash tests/run-all.sh
```

The suite runs marketplace/plugin validation, forbidden compatibility scans, ShellCheck when available, YAML frontmatter checks, shell tests, and embedded Python tests.

## License

MIT. See [LICENSE](LICENSE).
