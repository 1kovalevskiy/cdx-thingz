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

The `skill-eval` plugin contains a `UserPromptSubmit` hook. The `planning` plugin contains a `SessionStart` hook that seeds editable prompt and reviewer overrides without overwriting existing files. Codex asks you to trust plugin hooks separately after installation; review them before enabling them. Start a new task after installing or updating plugins.

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

### review

Pull-request review, interactive Git diff annotation review, and writing-style guidance. Install the three skills together because `pr` applies `writing-style` when drafting comments.

| Component | Trigger | Description |
|---|---|---|
| skill | `$review:pr <number>` | PR review with architecture analysis, scope-creep detection, and merge workflow |
| skill | `$review:git-review [ref]` | Interactive Git diff annotation review through an editor overlay |
| skill | `$review:writing-style` | Direct technical communication with brevity and no filler |

`$review:pr` distinguishes pull requests from issues. Issues use a comment-only flow. Pull requests offer a full review or a quick diff-only review:

- Full review gathers metadata, discussion, checks, and inline suggestions; uses the current clean Codex checkout at the exact PR commit; and launches one analysis subagent to read changed files, run validation, inspect architecture, and identify unrelated changes. The main task then resolves open questions, drafts the review, asks before posting, and restores the original checkout state.
- Quick review uses metadata and `gh pr diff` without switching revisions, launching a subagent, or running tests and linters.

The skill uses `gh` for GitHub operations. Posting comments, submitting reviews, and merging always require explicit confirmation.

`$review:git-review` generates a cleaned diff and opens it in `$EDITOR` through agterm, tmux, kitty, or wezterm. User annotations come back as a diff; Codex presents a fix plan, applies approved changes, and repeats until the editor closes without changes. Run its embedded tests with `python3 plugins/review/skills/git-review/scripts/git-review.py --test`.

`$review:writing-style` applies to tickets, pull requests, code reviews, and commit messages. It favors brevity, honest feedback, problem-solution structure, technical precision, and anti-AI-speak. It does not apply to README files, public documentation, or blog posts.

### planning

Structured implementation planning with interactive annotation review and autonomous plan execution.

| Component | Trigger | Description |
|---|---|---|
| skill | `$planning:make <desc>` | Structured implementation plan with an interactive review loop |
| skill | `$planning:exec [plan-file]` | Autonomous plan executor: task loop, multi-phase review, and optional finalize |
| helper | explicit CLI use | Plan annotation in `$EDITOR` with a diff-based feedback loop |
| prompt | launched by `make` | Automated plan quality review for completeness, over-engineering, and testing |

#### make skill

`$planning:make` creates a plan in `docs/plans/yyyymmdd-<task-name>.md` through interactive context gathering:

1. Parses intent and quickly explores the relevant code.
2. Asks focused questions one at a time: goal, scope, constraints, testing approach, and title.
3. Proposes two or three implementation approaches when the direction is not obvious.
4. Creates a plan with task sections, explicit file lists, test requirements, validation commands, and progress tracking.
5. Offers interactive review, automated plan review, implementation, or completion.

#### Interactive plan review

When `revdiff` is installed, `make` uses `plugins/planning/scripts/launch-plan-review.sh` to open a syntax-highlighted TUI with line annotations. The launcher supports agterm, tmux, zellij, herdr, kitty, wezterm/kaku, cmux, ghostty, iTerm2, and emacs vterm where those terminals expose a suitable overlay interface.

Without `revdiff`, `plan-annotate.py <plan-file>` opens a temporary copy in `$EDITOR` through agterm, tmux, kitty, or wezterm and prints a unified diff. The skill applies the annotations and repeats until the editor closes without changes. `$EDITOR` defaults to `vi` and may contain arguments.

Codex has no `ExitPlanMode` equivalent, so this port intentionally does not install the original automatic plan-exit hook. In the Codex app, cloud, or IDE contexts without a visible terminal overlay, the skill links the plan and collects the same feedback in chat. Set `PLANNING_DISABLE_REVDIFF` to any non-empty value to force the chat flow.

Popup dimensions are configurable:

| Variable | Default | Description |
|---|---:|---|
| `REVDIFF_POPUP_WIDTH` | `90%` | tmux/zellij popup width |
| `REVDIFF_POPUP_HEIGHT` | `90%` | tmux/zellij popup height or wezterm split percentage |

Run the embedded fallback tests with `python3 plugins/planning/scripts/plan-annotate.py --test`.

#### Plan-review prompt

The automated reviewer checks problem definition, solution correctness, scope creep, over-engineering, testing requirements, task granularity, and adherence to `AGENTS.md` and custom rules. It returns severity-rated findings and an `APPROVE` or `NEEDS REVISION` verdict. `make` renders bundled paths to absolute paths and launches the prompt in one read-only subagent.

#### exec skill

`$planning:exec` takes a plan from `$planning:make` and executes it task by task:

1. **Task loop** — one implementation subagent per task section, commits after each task, retries on failure.
2. **Comprehensive review** — five parallel read-only reviewers: quality, implementation, testing, simplification, and documentation; confirmed findings go to a fixer.
3. **Code smells** — one reviewer checks conventions, `AGENTS.md`, and style; confirmed findings go to a fixer.
4. **Critical-only review** — quality and implementation reviewers perform a final critical/major pass.
5. **Finalize** — rebase, squash, and validate on an attached Git feature branch when enabled.
6. **Stats summary** — reports progress-file, elapsed-time, commit, validation, and Git/Mercurial diff statistics from stable artifacts.
7. **Completion** — reports autonomous decisions and deviations, moves the plan to its sibling `completed/` directory, and commits the move without pushing.

Review agents only report. Fixer agents verify every finding against the code, repair confirmed issues, reject false positives, validate, and commit. The run is autonomous by design: leaf subagents never wait for user input and record non-obvious decisions or plan deviations in the progress file.

#### Worktrees and VCS

The skill uses the environment already selected for the Codex task and never creates a nested hidden worktree. In a detached Codex-managed worktree it commits on detached HEAD, skips branch mutation and finalization, and points the user to the Codex **Create branch** action. In Local mode it asks before creating a `codex/<plan-name>` branch.

Git and Mercurial execution are supported. Mercurial runs in place and skips Git-only finalization.

#### Planning configuration

| Variable | Default |
|---|---:|
| `PLANNING_PLANS_DIR` | `docs/plans` |
| `PLANNING_TASK_RETRIES` | `1` |
| `PLANNING_REVIEW_ITERATIONS` | `5` |
| `PLANNING_FINALIZE_ENABLED` | `1` |
| `PLANNING_DISABLE_REVDIFF` | unset; set to any non-empty value to skip local editor overlays |

`exec` resolves and validates its execution settings once at startup. `make` follows the upstream layout and always creates plans under `docs/plans/`.

Planning rules resolve from `.codex/planning-rules.md`, then `${CODEX_HOME:-$HOME/.codex}/planning-rules.md`. Brainstorm rules use the analogous `brainstorm-rules.md` paths.

Exec prompts and reviewer definitions use a three-layer override chain:

1. Project: `.codex/exec-plan/prompts/` and `.codex/exec-plan/agents/`.
2. User: `${CODEX_HOME:-$HOME/.codex}/exec-plan/prompts/` and `${CODEX_HOME:-$HOME/.codex}/exec-plan/agents/`.
3. Bundled defaults.

The planning `SessionStart` hook copies missing bundled defaults to the user layer without overwriting existing files. Edit those copies for all projects, or create only the project-level files that need repository-specific behavior. If the hook is not trusted, the bundled fallback still works.

Bundled prompts are `task.md`, `fixer.md`, `review.md`, `finalizer.md`, `stats.md`, and `progress-file.md`. Bundled reviewers are `quality.txt`, `implementation.txt`, `testing.txt`, `simplification.txt`, `documentation.txt`, and `smells.txt`.

`review.md` is a main-task playbook because the review phase fans out several independent subagents. Task, fixer, finalizer, stats, and smells prompts are leaf work and never add nested orchestration.

### thinking-tools

Evidence-driven tools for dialectic analysis and systematic root-cause investigation.

| Component | Trigger | Description |
|---|---|---|
| skill | `$thinking-tools:dialectic <statement>` | Prove and counter-prove a claim with parallel agents, then verify the synthesis |
| skill | `$thinking-tools:root-cause-investigator` | Investigate errors and unexpected behavior with the 5-Why methodology |

`$thinking-tools:dialectic` launches thesis and antithesis agents in parallel. Both must cite concrete evidence; the main task weighs their reports and verifies every cited file, line, and implementation claim before presenting the conclusion.

`$thinking-tools:root-cause-investigator` progresses from the immediate symptom through process, system, and design causes to the fundamental root cause. Its bundled references cover common failure patterns and practical investigation techniques.

### workflow

Session helpers for knowledge capture, confusion handling, course correction, and clipboard operations.

| Component | Trigger | Description |
|---|---|---|
| skill | `$workflow:learn` | Capture strategic knowledge in project `AGENTS.md` or Codex Local Memories |
| skill | `$workflow:clarify` | Investigate confusion and determine whether a real issue exists |
| skill | `$workflow:wrong` | Reset and re-evaluate an unsuccessful approach |
| skill | `$workflow:md-copy` | Format the final answer as Markdown and copy it to the clipboard |
| skill | `$workflow:txt-copy` | Copy generated text to the clipboard |

`$workflow:learn` reviews the session for reusable architecture, conventions, integrations, testing practices, and operational knowledge. Team-wide repository guidance goes to the applicable project `AGENTS.md`; genuinely personal or machine-specific context goes to Codex Local Memories. It follows existing memory-placement guidance, asks the user which discoveries to save, and never substitutes repository dotfiles for Local Memories.

`$workflow:clarify` investigates the code, configuration, and documentation before deciding whether confusion comes from a misunderstanding, outdated context, configuration, documentation, or a real defect. For a real issue it assesses scope, presents alternatives when needed, and offers `$planning:make` or a separate Plan task instead of immediately changing code.

`$workflow:wrong` discards the unsuccessful direction, restates the core problem, identifies missing context, proposes two or three fresh approaches with trade-offs, and recommends the best path.

`$workflow:md-copy` reformats the final response as clean Markdown before copying it. `$workflow:txt-copy` copies generated text without reformatting. Both use a timestamped temporary file and support macOS `pbcopy` plus Linux `xclip` or `xsel`.

### skill-eval

| Component | Trigger | Description |
|---|---|---|
| hook | `UserPromptSubmit` | Forces skill evaluation before every response |

The hook injects a model-visible instruction before each turn. Codex must identify every relevant skill, read each selected `SKILL.md` completely, announce the selected skills, and follow their instructions before proceeding. If no skill is relevant, processing continues normally.

The bundled command returns the structured `UserPromptSubmit` `additionalContext` expected by Codex. As with other non-managed plugin hooks, it runs only after the installed hook definition has been reviewed and trusted.

### Editor overlays

Planning review can use `revdiff` and the backends supported by its bundled launchers; its `$EDITOR` fallback supports agterm, tmux, kitty, and wezterm. Local-diff review supports agterm, tmux, kitty, and wezterm. Overlays are available only in suitable local terminal environments. Planning falls back to chat when no visible overlay is available; local-diff review reports that a supported overlay is required. No automatic plan-exit hook is installed.

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

Without marketplace installation, self-contained skill directories can be copied into `~/.agents/skills/`. Keep each `SKILL.md` together with its `scripts/` and `references/` siblings so relative resolution continues to work.

The planning skills intentionally share plugin-level scripts and references, so copying only `skills/make/` or `skills/exec/` breaks their relative links. Install planning from the marketplace, or preserve the complete `plugins/planning/` tree in a stable location and update the copied skills' bundled links to that absolute location.

For `skill-eval`, copy the hook script to a stable location and merge its `UserPromptSubmit` entry from `plugins/skill-eval/hooks/hooks.json` into `~/.codex/hooks.json`, replacing `${PLUGIN_ROOT}` with that installed location. Planning works without its optional seeding hook; create `${CODEX_HOME:-$HOME/.codex}/exec-plan/` overrides manually when using the manual fallback. Review and trust hooks before enabling them.

## Tests

```bash
bash tests/run-all.sh
```

The suite runs marketplace/plugin validation, forbidden compatibility scans, ShellCheck when available, YAML frontmatter checks, shell tests, and embedded Python tests.

## License

MIT. See [LICENSE](LICENSE).
