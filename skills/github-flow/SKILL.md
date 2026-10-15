---
name: github-flow
description: Execute Git and GitHub operations using the repository's documented conventions for commits, issues, pull requests, and merging.
---

# GitHub flow

Use this skill when performing Git or GitHub workflow operations.

Start with the target repository's `AGENTS.md`, Git documentation, and observed
configuration/history. Project-specific instructions and conventions take
precedence. Load the canonical `rules/github.md` or a project-adopted copy when
accessible; an individual skill installation may not include that separate
file.

When no repository convention can be established, use only the minimal safe
guidance below: keep changes focused, use a short-lived branch and
Conventional Commit message for collaborative work, verify the diff and
acceptance criteria before opening a PR, and never merge without explicit
authorization. State unknown required checks or merge preferences instead of
inventing them.

## Process

### 1. Inspect repository conventions

Before acting, determine:

- target branch;
- whether direct work on the target branch is allowed;
- branch naming requirements;
- commit conventions;
- required checks;
- PR requirements;
- merge strategy.

Do not assume every repository uses the same flow.

### 2. Prepare the change

Follow the repository's configured workflow.

Keep the change focused on one logical unit.

Inspect `git status` before switching branches or preparing a worktree. If the
checkout is stale, update from the intended base using repository conventions.
Preserve uncommitted and untracked changes; use an isolated worktree when
switching or cleaning could put them at risk. Never use destructive reset/clean
commands without authorization.

When using a branch, start from the latest intended base. For independent
parallel work, prefer separate branches and worktrees when supported and useful;
assign distinct issue and file ownership, and serialize work that shares a
working directory or has risky overlap. Use the target repository's own
integration conventions after dependencies merge.

### 3. Commit

Use the repository's commit convention.

When none exists, use the minimal safe guidance above and report any unknown
repository requirements.

Before committing:

- inspect staged changes;
- remove accidental files;
- confirm no secrets are included.

### 4. Prepare the PR

When a PR is part of the repository workflow:

- inspect the complete diff;
- confirm the PR's current head SHA, effective changed-file diff, and target
  branch; distinguish the PR's recorded base SHA from the current target tip;
- verify acceptance criteria;
- run relevant checks;
- use `templates/PULL_REQUEST.md` when applicable;
- link the implementation issue.

Report checks only for the exact revision they evaluated. Do not reuse earlier
results after the head changes; refresh the verification summary and PR
description when needed. `skills/verify-change/SKILL.md` defines the evidence
to record, including skipped or unavailable checks.

### 5. Merge

Use the repository's configured merge strategy.

Do not merge unless the user or repository workflow grants that authority.

Clean up temporary branches when appropriate.

## Completion

GitHub workflow work is complete when:

- the change is in the correct place;
- commit history follows project conventions;
- verification claims are accurate;
- issue and PR relationships are preserved;
- no unintended files or secrets were included.
