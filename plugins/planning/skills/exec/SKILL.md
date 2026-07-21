---
name: exec
description: "Execute plan tasks sequentially using subagents. Use when user says 'exec', 'execute plan', 'run plan', or wants to implement a plan file task by task with isolated subagents."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(bash:*), Agent, AskUserQuestion, TaskCreate, TaskUpdate, EnterWorktree
---

# exec

Bundled links in this file are relative to this `SKILL.md`. Resolve linked scripts, prompts, and agent files to absolute paths before invoking or embedding them, while keeping the project directory as the command working directory. Subagents receive only fully rendered prompts with absolute script paths and never depend on plugin environment variables.

Execute plan file tasks sequentially, each in an isolated subagent.

## Arguments

- `$ARGUMENTS` — path to plan file (optional; if omitted, ask user to pick from `PLANNING_PLANS_DIR`, default: `docs/plans/`)

## Configuration

Before resolving the plan or starting any work, read the planning configuration from the environment via Bash and retain the resolved values for the entire run:

```bash
printf 'plans_dir=%s\ntask_retries=%s\nreview_iterations=%s\nfinalize_enabled=%s\n' \
  "${PLANNING_PLANS_DIR:-docs/plans}" \
  "${PLANNING_TASK_RETRIES:-1}" \
  "${PLANNING_REVIEW_ITERATIONS:-5}" \
  "${PLANNING_FINALIZE_ENABLED:-1}"
```

`task_retries` and `review_iterations` must be non-negative integers. `finalize_enabled` must be `0` or `1`. If a value is invalid, stop before modifying the repository and report the invalid variable. Use `plans_dir`, `task_retries`, `review_iterations`, and `finalize_enabled` below instead of re-reading the environment or relying on implicit substitution.

## File Resolution

ALWAYS use [resolve-file.sh](scripts/resolve-file.sh) to read prompt and agent files. NEVER construct the override chain manually. Run the resolved script via Bash with one relative path argument, for example `prompts/task.md` or `agents/quality.txt`.
The script checks `.codex/exec-plan/`, then `${CODEX_HOME:-$HOME/.codex}/exec-plan/`, then bundled defaults automatically.

### Placeholder Substitution

After reading a prompt file, replace ALL placeholders with actual values before passing to a subagent. Subagents run in fresh contexts without plugin env vars.

Always substitute: `PLAN_FILE_PATH`, `PROGRESS_FILE_PATH`, `DEFAULT_BRANCH`, `RESOLVE_SCRIPT` (absolute path to [resolve-file.sh](scripts/resolve-file.sh)), `APPEND_PROGRESS_SCRIPT` (absolute path to [append-progress.sh](scripts/append-progress.sh)), `STAGE_AND_COMMIT_SCRIPT` (absolute path to [stage-and-commit.sh](scripts/stage-and-commit.sh)), `USER_RULES` (resolved custom rules content from the rules loading step, or empty string if no rules found), and phase-specific values (`FINDINGS_LIST`, `REVIEW_PHASE`). No unresolved placeholder may be passed to a subagent.

## Custom Rules Loading

Before starting execution, run [resolve-rules.sh](../../scripts/resolve-rules.sh) via Bash with `planning-rules.md` as its argument to check for user-provided custom rules.

If the output is non-empty, store it as the resolved custom rules content. When substituting `USER_RULES` in task prompts, wrap the content with a label so the subagent understands it: use "ADDITIONAL CUSTOM RULES:\n<content>" as the substitution. If the output is empty, substitute an empty string for `USER_RULES`. See [custom rules](../../references/custom-rules.md) for full documentation on the rules mechanism.

## Process

### Step 1. Resolve plan file

If `$ARGUMENTS` contains a file path, use it. Otherwise, list `.md` files in the resolved `plans_dir`, excluding `completed/`. If exactly one plan found, use it automatically. If multiple found, ask the user to pick one using Codex interactive input when available, with a concise text fallback.

Read the plan file. Count total Task sections (`### Task N:` or `### Iteration N:`) to know the scope.

Determine the default branch by running [detect-branch.sh](scripts/detect-branch.sh) via Bash with no arguments.

Note: in `hg` repos, detect-branch.sh returns `remote/<name>` when an upstream ref is available and otherwise falls back to `default`. Git-only finalize is skipped on hg; execution and commits remain in-place.

### Step 2. Choose the execution checkout

Detect VCS by running [detect-vcs.sh](scripts/detect-vcs.sh) via Bash with no arguments and capturing stdout as `vcs`.

**Mercurial:** continue in the current checkout. Codex Worktrees are Git-only; users who want hg isolation must enter an hg share before invoking the skill.

**Git:** use the environment already selected for this Codex task.

- If the task is already in a linked Codex Worktree on a branch, use it as-is. Never create a nested worktree.
- If it is a detached Codex Worktree, execute and commit there, but skip branch rename, rebase, squash, push, and PR operations. At completion suggest `codex/<plan-stem>` and the Codex **Create branch** action.
- In Local mode on the default branch, preserve the original isolation choice: ask whether to proceed in place or stop so the user can restart the task in Worktree mode. If proceeding in place, Step 4 creates `codex/<plan-stem>`.
- In Local mode on an existing feature branch, ask whether to continue on that branch or stop and restart in Worktree mode.

Use Codex interactive input when available, with a concise text fallback. Do not create a hidden worktree or move an existing branch behind the user's back.

### Step 3. Create task list

ALWAYS call `update_plan` before starting work. Create one plan item per `### Task N:` section, followed by comprehensive review, code-smell review, critical-only review, finalize, and stats summary. Include the task title and checkbox items in each implementation step. Keep at most one item `in_progress`; mark it `completed` immediately when its outcome is known and move the next item to `in_progress`.

### Step 4. Create branch

**Skip this step** in an existing linked Codex Worktree, a detached Codex Worktree, an hg checkout, or when already continuing on a Git feature branch. Carry the current branch/bookmark state forward to Step 5.

Otherwise (in-place mode), **MANDATORY**: run the script below. Do NOT create the branch manually — the script strips the date prefix from the plan filename and applies the Codex branch convention (e.g., `20260329-feature-name.md` → branch `codex/feature-name`).

Run [create-branch.sh](scripts/create-branch.sh) via Bash with the absolute plan-file path as its only argument.

The script creates a feature branch if currently on main/master, or stays on the current branch if already on a feature branch. Capture and use the branch name it outputs.

### Step 5. Initialize progress file

Initialize the progress file by running [init-progress.sh](scripts/init-progress.sh) via Bash with three arguments: the absolute `/tmp/progress-<plan-name>.txt` path, the absolute plan-file path, and the branch name (derive `<plan-name>` from the plan file stem, e.g., `fix-issues.md` → `progress-fix-issues`). The script creates the file with a header. Report the full progress file path to the user.

IMPORTANT: Always use [append-progress.sh](scripts/append-progress.sh) to write to the progress file after initialization. Never write directly.

### Step 6. Task loop

Repeat until no `[ ]` checkboxes remain in any Task section:

1. **Re-read the plan file** (subagent modifies it each iteration)
2. **Find the first Task section** (`### Task N:` or `### Iteration N:`) that still has `[ ]` checkboxes
3. **If none found** — all tasks complete, go to step 7
4. **Announce the task to the user** — before spawning the subagent, output a visible summary:
   - Task number and title (from the `### Task N:` header)
   - List all `[ ]` checkbox items in that task section
   - Example output:
     ```
     --- Task 1: Fix error handling ---
     - [ ] Handle the error from os.ReadFile
     - [ ] Either log and exit or handle gracefully
     ```
5. **Spawn a subagent** with `spawn_agent` using the task prompt from `prompts/task.md`, with all placeholders substituted as described above (including `USER_RULES`). Start exactly one implementation agent, then collect it with `wait_agent`. It inherits the current sandbox and approval profile.
6. **After subagent returns**, re-read the plan file and check if that task's checkboxes are now `[x]`
   - If yes — task succeeded, continue loop
   - If no — **retry** with a fresh subagent for the same task up to the resolved `task_retries` count. If all retries fail, stop and report failure to user
7. **Report to user**: "Task N completed" (one line). The task subagent logs details to the progress file.

CRITICAL: Spawn exactly ONE task subagent per iteration and WAIT for it to return before starting the next. NEVER batch-spawn multiple task subagents in a single message. Plan tasks are ordered and interdependent — later tasks build on the files earlier tasks create, and every task subagent edits the same plan-file checkboxes and overlapping source files, so running them in parallel corrupts the plan and the working tree. Parallel execution applies ONLY to the independent review agents in steps 7 and 9, never to this task loop.

CRITICAL: Do NOT stop the loop based on subagent return text. The ONLY condition to stop is: no `[ ]` checkboxes remain in any Task section (`### Task N:` or `### Iteration N:`). Always re-read the plan file to check.

CRITICAL: You are the ORCHESTRATOR. Never read code, debug errors, investigate diagnostics, or fix issues yourself. If a subagent leaves problems (compiler errors, test failures, lint issues), retry with a fresh subagent — pass the error details in the prompt so it can fix them. All code work happens inside subagents, not in the orchestrator.

Maximum iterations safety limit: 50. If reached, stop and report to user.

### Step 7. Review phase 1 — comprehensive then critical re-check

After all tasks complete, run a comprehensive code review on iteration 1, then narrow to critical-only re-checks on subsequent iterations to verify the fixer's work without re-running the full heavy sweep.

Report to user: "--- Review phase 1: comprehensive ---"

Loop up to the resolved `review_iterations` count. Track the current iteration number:

1. **Read review.md as a playbook (NOT as a subagent prompt)** — resolve `prompts/review.md` through the override chain and read it from this main session. It tells YOU (the orchestrator) which specialist agents to fan out for the current `REVIEW_PHASE`. Substitute `DEFAULT_BRANCH`, `PLAN_FILE_PATH`, `PROGRESS_FILE_PATH`, `RESOLVE_SCRIPT`, and `REVIEW_PHASE` in the resolved content. Then follow the playbook FROM THIS SESSION: call `spawn_agent` for every specified reviewer before waiting, then collect them with `wait_agent`. The fanout MUST be initiated from the main orchestrator.
   - **Iteration 1**: set `REVIEW_PHASE` to `comprehensive`. Per the playbook, launch 5 parallel review agents (quality, implementation, testing, simplification, documentation).
   - **Iteration 2 and later**: set `REVIEW_PHASE` to `critical`. Per the playbook, launch 2 parallel review agents (quality, implementation) focused on critical/major issues only. Before this iteration, report to user: "--- Review phase 1: critical re-check (iteration N) ---"

2. **Collect findings** — collect findings from ALL launched review agents. Pass the COMPLETE output (not a summary) to the fixer. Do NOT summarize, filter, or dismiss any findings. ALL findings are actionable. Report to user with a short list of findings. Log to progress file:
   Run [append-progress.sh](scripts/append-progress.sh) with the progress-file path and `review phase 1: findings`, then pipe the complete findings to the same script with the progress-file path as its only argument.

3. **If ALL agents reported zero issues** → report "Review phase 1: clean" and proceed to the next phase.

4. **Spawn a fixer agent** — resolve `prompts/fixer.md` through the override chain. Launch one fixer with `spawn_agent` and collect it with `wait_agent`; it inherits the current sandbox and approval profile. Pass the FULL unedited review output as FINDINGS_LIST — the fixer decides what's real, not you.

5. **After fixer returns** → show the "FIXES:" section to the user. Report "Review phase 1: iteration N fixes applied". Loop back to step 1.

If `review_iterations` is reached with issues still found, report "Review phase 1: max iterations reached, moving on" and continue.

### Step 8. Review phase 2 — code smells

Report to user: "--- Review phase 2: code smells analysis ---"

Run once (no loop):

1. **Spawn a smells agent** — resolve `agents/smells.txt` through the override chain. Launch one smells reviewer with `spawn_agent`, using the resolved prompt, and collect it with `wait_agent`.

2. **Collect findings** — after the agent returns, report to user with a compact list of findings (one line per finding). Log findings to progress file:
   Run [append-progress.sh](scripts/append-progress.sh) with the progress-file path and `review phase 2: findings`, then pipe the complete findings to the same script with the progress-file path as its only argument.

3. **If no issues found** → report "Smells analysis: clean" and proceed to the next phase.

4. **Spawn a fixer agent** — resolve `prompts/fixer.md` through the override chain. Launch one fixer with `spawn_agent` and collect it with `wait_agent`; it inherits the current sandbox and approval profile. Pass the FULL smells output as FINDINGS_LIST.

5. **After fixer returns** → report fixes to user. Proceed to the next phase.

### Step 9. Review phase 3 — critical only

Report to user: "--- Review phase 3: critical/major only (single pass) ---"

Same structure as step 7 but with `REVIEW_PHASE` set to `critical`. Resolve `prompts/review.md` and follow its playbook FROM THIS MAIN SESSION — launch 2 parallel review agents (quality, implementation) with `spawn_agent` before waiting, focusing on critical/major issues only. The fanout MUST be initiated from the main orchestrator. Same fixer flow — pass findings to fixer, show FIXES to user.

### Step 10. Finalize

Detect VCS with [detect-vcs.sh](scripts/detect-vcs.sh). If the resolved `finalize_enabled` value is not `1`, Git is detached, or VCS is hg, skip this Git-only step and report the reason.

After all reviews pass, rebase and clean up commits.

Report to user: "--- Finalize: rebase and clean up commits ---"

Spawn one finalizer with `spawn_agent`, collect it with `wait_agent`, and use the prompt from `prompts/finalizer.md`. The agent inherits the current sandbox and approval profile. Replace `DEFAULT_BRANCH`, `PLAN_FILE_PATH`, and `PROGRESS_FILE_PATH`.

This is best-effort — if rebase fails, report the issue but don't block completion.

### Step 11. Stats summary

After finalize (or after it was skipped), log completion by running [append-progress.sh](scripts/append-progress.sh) with the progress-file path and `completed`. This gives the stats agent the final run state and completion timestamp.

Then spawn one read-only summary agent with `spawn_agent`, collect it with `wait_agent`, and use `prompts/stats.md`. Replace `DEFAULT_BRANCH`, `PLAN_FILE_PATH`, and `PROGRESS_FILE_PATH` in the resolved content.

The stats agent reads only the progress file, plan, elapsed timestamps, and stable Git or Mercurial commands. It reports tasks, commits, diff stat, review/fixer iterations, validation, and elapsed time. It never parses internal Codex transcripts or caches.

Show the stats agent's full markdown output to the user verbatim. Do NOT summarize it further — the agent already produces a tight summary.

This step is best-effort — if stable progress or VCS data cannot be resolved, report the failure but do not block completion.

### Step 12. Completion

When stats summary is done (or skipped on failure):
- **Report autonomous decisions and deviations to the user.** The run had no human to answer questions, so subagents decided judgment calls themselves and logged them. Collect every such entry from the progress file — `grep -E '^\[(decision|deviation)\]' <progress-file>` — and present them in a dedicated section titled **"Decisions made autonomously / Deviations from the plan"**, one bullet per entry with its stated reason, so the user learns every question the run answered on its own and why. If there are none, state "no autonomous decisions or deviations were logged." Do this regardless of whether finalize ran — finalize is skipped on hg or when disabled, so this is the guaranteed place the user always gets the report.
- Move the finished plan into its `completed/` subdirectory and commit it (best-effort) by running [move-plan.sh](scripts/move-plan.sh) with the absolute plan-file path. The script is a no-op when the plan is already under `completed/` or missing, derives the target as a `completed/` sibling of the plan's directory (so it respects a custom `plans_dir` and worktrees), and commits the move VCS-aware (git/hg). Do NOT push. If the script exits non-zero, report the failure but do not block completion.
- Report the final line "All N tasks completed, reviews passed". Append ", branch finalized" only when finalize actually ran successfully. Append ", plan moved to completed/" only when move-plan.sh actually moved the file (it printed `moved plan to ...`); omit either suffix when that action was skipped, a no-op, or failed.

## Key rules

- Each subagent gets a fresh context — no accumulated state from previous tasks
- Parent session only tracks: task number, success/failure, retry count
- Plan file is the single source of truth for progress — always re-read it
- No signals — just checkboxes in the plan for task progress
- Maintain progress file (`/tmp/progress-<plan-name>.txt`) — see `prompts/progress-file.md` for format and when to write
- Do not modify the plan file yourself during the task, review, and finalize phases — only subagents modify it. The sole exception is the terminal move in step 12 (after all phases finish), which the orchestrator performs via `move-plan.sh`
- Do not implement or fix code yourself — only subagents implement and fix
- If a subagent fails or leaves broken code, re-run the loop — do NOT investigate or fix it yourself
- NEVER dismiss findings as "pre-existing", "not from changes", or "architectural" — ALL findings are actionable
- NEVER summarize or filter agent findings — pass the full output to the fixer agent verbatim
- All prompt and agent files MUST be resolved through the three-layer override chain before use
- One implementation agent runs at a time. Parallelism is only for independent read-only review agents launched by the main task.
- After reading a prompt file, substitute all placeholders before passing to subagent (see Placeholder Substitution)
- Subagents run with NO human available — they must NEVER ask the user a question (no Codex interactive input, no pausing for input). They decide judgment calls the plan does not settle from the project's lint rules, AGENTS.md, and code conventions, and log each as a `[decision]`/`[deviation]` line for the completion report
- In a Codex Worktree, never create a nested worktree or mutate the main checkout; all operations stay in the checkout already selected for this task, and Step 4's create-branch.sh is skipped
