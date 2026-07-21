---
name: learn
description: Update project AGENTS.md with strategic knowledge discovered during this session, or Codex Local Memories when the discovery is personal or machine-specific. Defers to project guidance instead of overriding it. Use when user says "learn", "save knowledge", "update agents.md", "capture learnings", or at end of significant work sessions. Also used by commit skill for pre-commit knowledge capture.
allowed-tools: Read, Edit, AskUserQuestion
---

# Learn

Review the current conversation history and identify strategic, reusable knowledge. Route team-shared repository knowledge to the applicable project `AGENTS.md`; route genuinely personal or environment-specific discoveries to the native Codex Local Memories surface.

## Analysis Process

1. **Review Session History**
   - Examine all files read and modified during this session
   - Identify patterns discovered while working on tasks
   - Note architectural insights gained from exploring the codebase

2. **Extract Strategic Knowledge**
   - Filter out tactical details (bug fixes, specific implementations)
   - Focus on reusable patterns and project structure
   - Identify conventions and architectural decisions

3. **Categorize Findings**
   - Project architecture and structure
   - Data flow patterns
   - External service integrations
   - Project-specific conventions
   - Key dependencies and their purposes
   - Configuration patterns
   - Testing strategies
   - Build and deployment processes
   - Operational knowledge (debugging, DevOps)

## Destinations

This skill writes to one of two Codex knowledge surfaces:

- **`AGENTS.md`** (project memory, committed, team-shared) — the default destination. Use for architecture, conventions, integration patterns, and any other knowledge useful to the whole team.
- **Codex Local Memories** (native personal memory) — used when the discovery describes per-developer / per-checkout state: a tool-loading workaround that depends on this developer's runtime setup, a personal alias, or a per-checkout environment override.

  **Counter-example:** *"We keep credentials in `~/.aws/credentials`"* mentions a user-home path but describes a team-wide convention — the path is illustrative, not per-developer state. Such notes belong in project AGENTS.md. When in doubt about whether a discovery is genuinely personal, default to project AGENTS.md.

Never emulate Local Memories with a repository file, dotfile, or hardcoded filesystem path. If the current Codex surface does not expose memory saving, show the proposed memory and report that it was not persisted.

**Default for ambiguous cases: project AGENTS.md.** Leaking personal config into a committed file is a loud error that reviewers catch quickly; hiding project-wide knowledge in a gitignored personal file is a silent error that rots over time.

## What Qualifies

**INCLUDE** - Strategic discoveries from this session:
- Architectural patterns uncovered while working
- Project structure insights gained from navigation
- Conventions noticed across multiple files
- Integration patterns discovered
- Configuration approaches identified
- Testing strategies observed
- Build/deployment processes encountered
- Performance optimizations found
- Security implementations discovered
- Operational knowledge:
  - Database locations and connection details per environment
  - Useful queries discovered during debugging
  - Testing procedures and verification steps
  - Deployment workflows and commands
  - Log locations and monitoring endpoints
  - Environment-specific quirks and gotchas

**EXCLUDE** - Session-specific tactical work:
- The specific bug we fixed
- The particular feature we implemented
- Temporary workarounds we used
- One-off code changes
- TODO items we encountered
- Historical context about changes

## Decision Criteria

Ask yourself for each discovery:
- "Will this help understand the project in 6 months?"
- "Is this a pattern that appears multiple times?"
- "Does this represent a project-wide convention?"
- "Would knowing this speed up future development?"
- "Would this save debugging time in the future?" (for operational knowledge)

## Workflow

### 1. Check for Existing Memory-Placement Guidance
Before applying the routing rules below, scan the effective project instruction chain (applicable `AGENTS.md` and `AGENTS.override.md` files), `${CODEX_HOME:-$HOME/.codex}/AGENTS.md`, and accessible Local Memories for documented memory-placement guidance. If guidance exists, follow it instead of using this skill's defaults.

### 2. Check Existing Memory Content
Read the effective project instruction chain, `${CODEX_HOME:-$HOME/.codex}/AGENTS.md`, and accessible Local Memories to avoid duplication, including cross-project entries already captured in user memory.

### 3. Early Exit if Nothing Found
If no new strategic knowledge was discovered during this session:
- Report "no new strategic knowledge to capture"
- Do NOT ask for confirmation
- End the skill execution

### 4. Classify Each Discovery
For each discovery, determine its destination per the [Destinations](#destinations) rules: default to project `AGENTS.md`, and route only genuinely personal or machine-specific content to Codex Local Memories.

### 5. New Knowledge to Add
Present discovered knowledge formatted for the chosen destination, tagging each block with its inferred file:
```markdown
## [Section Name] → project AGENTS.md
- Discovery 1
- Discovery 2
```

### 6. User Confirmation with Codex interactive input

**CRITICAL**: Use Codex interactive input when available for granular selection of what to save. If it is unavailable, present the same granular choices in chat and wait for the user's answer.

Build options dynamically based on discoveries:
- First option: "All knowledge" - save everything to its inferred destination
- Last option before custom: "None" - skip saving entirely
- Middle options: Individual knowledge items (up to 2-3 most significant), each labelled with its inferred destination
- User can always type custom selection via "Other"

Example with 3 discoveries (2 project, 1 personal):
```yaml
question: "Which knowledge should I save?"
options:
  - label: "All (3 items)"
    description: "Save all discovered patterns to their inferred destinations"
  - label: "Service discovery pattern → project AGENTS.md"
    description: "Project-wide convention for how modules find each other"
  - label: "Local toolchain variant → Codex Local Memories"
    description: "Per-checkout build runner override (only relevant on this machine)"
  - label: "None"
    description: "Skip saving, nothing worth keeping"
```

Example with 1 discovery:
```yaml
question: "Save this knowledge?"
options:
  - label: "Yes → project AGENTS.md"
    description: "Save: [brief description of the discovery]"
  - label: "No"
    description: "Skip saving"
```

After user selection:
- "All" -> save everything to its inferred destination
- "None" -> end without saving
- Specific item -> save only that item, to the inferred destination shown in the label
- "Other" -> user types custom selection of **which discoveries** to save (comma-separated item names). Destinations follow the labels shown — `"Other"` does NOT redirect a destination to an arbitrary path. To override a routing decision, the user should decline the auto-classification, edit the destination file manually, or re-invoke the skill with explicit instructions.

## Important Guidelines
- Only capture genuinely new discoveries from this session
- Don't duplicate existing project AGENTS.md, `Codex Local Memories`, or user AGENTS.md content
- Focus on patterns observed, not specific code written
- Keep descriptions concise and actionable
- MUST obtain confirmation through Codex interactive input when available; otherwise use the same explicit choices in chat and wait for the user's answer
- If no knowledge found, exit early without asking
- **Defer to project- or user-level memory-placement guidance discovered in step 1** — do not override existing conventions with this skill's defaults
