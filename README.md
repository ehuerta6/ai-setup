# SetupSmith

A reusable catalog of skills, agents, rules, templates, and Project Instructions, with guided setup and deterministic project-local skill installation for AI coding assistants.

**Available now:** the configuration catalog, manual adoption workflows, read-only CLI catalog discovery, explicitly approved selective skill installation and adoption of existing skills, read-only managed-skill checks/diffs, explicitly approved selective updates, manifest-based restoration of verified skills, and the standalone `setup-ai` Analyze → Recommend skill. Automatic synchronization and managed removal are not implemented. See the [MVP specification](docs/setupsmith-mvp.md) and [managed installation guide](docs/managed-skill-installation.md).

Browse this README to find configuration. Use [WORKFLOWS.md](WORKFLOWS.md) to choose a process for a specific task.

Projects can adopt only what they need. Keep product behavior, architecture, and other project-specific decisions in the project repository.

## Quick start

- **Choose a workflow:** start with the scenario router in [WORKFLOWS.md](WORKFLOWS.md), then load the relevant skills.
- **Adopt configuration into a project today:** inspect its AI instructions, architecture, stack, Git workflow, and conventions. Then follow the manual Project adoption route in [WORKFLOWS.md](WORKFLOWS.md) and copy only the selected canonical files. For example, add `skills/firebase/SKILL.md` only to a project that uses Firebase, and keep product-specific instructions there.
- **Set up a multi-chat workspace:** choose a Project Instructions preset below and tailor it with `skills/ai-config-builder/SKILL.md`.
- **Discover catalog artifacts:** run `python3 scripts/setupsmith.py discover --source https://github.com/ehuerta6/setupsmith.git`. It defaults to the Git source's advertised default branch; use `--ref <branch-or-tag-or-revision>` to select another ref. This command is read-only with respect to the target project and reports its resolved commit.
- **Analyze a project:** install only `skills/setup-ai/SKILL.md` using your assistant's supported skill mechanism, then invoke it as `$setup-ai` or select it from `/skills` in Codex, or as `/setup-ai` in Claude Code. The skill inspects and recommends only; it does not install or edit project files. Codex native discovery and invocation were checked for this skill; Claude Code runtime discovery is unavailable in the current environment.

The catalog below lists each artifact's canonical path and purpose.

## Choosing configuration

Use the smallest artifact that fits the job:

| Artifact | Use it for |
| --- | --- |
| Skill | A repeatable task workflow, such as [research-and-compare](skills/research-and-compare/SKILL.md). |
| Agent | A focused role that benefits from its own instructions or review context. |
| Rule | A stable constraint that should guide many kinds of work, such as [security](rules/security.md). |
| Template | A starting structure for a recurring document or decision. |
| Project Instruction | Shared context for a long-running, multi-chat workspace, such as [research-workspace](project-instructions/research-workspace.md). |

You do not need to adopt the whole catalog. In an existing repository, inspect its own instructions first, then copy only the relevant canonical files and keep product and architecture decisions in that repository. For example, a Firebase project might adopt `skills/firebase/SKILL.md` and `rules/security.md`, while leaving unrelated skills behind.

The catalog also supports nontechnical work. Use [research-and-compare](skills/research-and-compare/SKILL.md) for a focused comparison, [learning-coach](project-instructions/learning-coach.md) for a multi-chat learning workspace, or [general-workspace](project-instructions/general-workspace.md) when a workspace needs continuity across chats. Skills guide tasks; Project Instructions hold durable context. Keep personal details and decisions in the project workspace.

# Skills

## Configuration

### `setup-ai`

Path: `skills/setup-ai/SKILL.md`

Analyze project conventions and recommend catalog configuration without modifying project files.

### `ai-config-builder`

Path: `skills/ai-config-builder/SKILL.md`

Design or evolve skills, agents, rules, templates, and Project Instructions without unnecessary duplication.

### `audit-ai-config`

Path: `skills/audit-ai-config/SKILL.md`

Audit existing project AI configuration for drift, duplication, stale instructions, and missing reusable configuration.

### `research-and-compare`

Path: `skills/research-and-compare/SKILL.md`

Research a question and compare options using current, traceable evidence and explicit tradeoffs.

## Planning

### `grill-me`

Path: `skills/grill-me/SKILL.md`

Use when a feature, product decision, or implementation plan still contains ambiguity.

Stress-tests decisions before implementation so agents do not have to guess. Sharpens domain terminology, surfaces behavior conflicts, and identifies useful edge cases.

### `prototype`

Path: `skills/prototype/SKILL.md`

Optional disposable UI or logic experiments for answering concrete design questions before implementation. Use only when trying alternatives will resolve uncertainty better than discussion.

### `to-spec`

Path: `skills/to-spec/SKILL.md`

Turn resolved product and technical decisions into an implementation-ready specification.

Does not restart discovery or invent missing decisions.

### `to-issues`

Path: `skills/to-issues/SKILL.md`

Break an approved spec into focused GitHub Issues.

Prefers vertical slices, explicit dependencies, and issues that fit inside a fresh agent context.

## Implementation and review

### `implement-issue`

Path: `skills/implement-issue/SKILL.md`

Implement one approved GitHub Issue while respecting its acceptance criteria and project conventions.

### `verify-change`

Path: `skills/verify-change/SKILL.md`

Discover and run the repository's actual validation workflow.

Reports real evidence instead of assuming checks passed.

### `review-pr`

Path: `skills/review-pr/SKILL.md`

Review completed work independently against both requirements and engineering quality.

### `debug-with-evidence`

Path: `skills/debug-with-evidence/SKILL.md`

Debug using reproduction, evidence, explicit hypotheses, and focused tests instead of random edits.

### `git-flow`

Path: `skills/git-flow/SKILL.md`

Execute the repository's Git and GitHub workflow for branches, commits, issues, PRs, and merging.

Project-specific Git rules override its defaults.

### `plan-issue-batches`

Path: `skills/plan-issue-batches/SKILL.md`

Plan existing GitHub Issues into dependency-aware batches, generate a prompt for a selected batch, and update the plan as repository state changes.

Unlike `to-issues`, it does not create issues. Unlike the `issue-batch-orchestrator` agent, it prepares the plan and prompt rather than executing the batch.

## Stack-specific

### `firebase`

Path: `skills/firebase/SKILL.md`

Use for Firebase Auth, Firestore, Security Rules, Emulator Suite, Functions, Storage, seeds, and trusted server boundaries.

Only use in projects that actually use Firebase.

## Agent workflow

### `handoff`

Path: `skills/handoff/SKILL.md`

Create compact context for transferring unfinished work to another agent or session.

### `retro`

Path: `skills/retro/SKILL.md`

Evaluate completed AI-assisted work and identify improvements to skills, rules, tooling, or workflow.

### `write-agent-instructions`

Path: `skills/write-agent-instructions/SKILL.md`

Write and maintain compact instructions intended for AI agents.

Use this when creating or cleaning AGENTS files, skills, prompts, or similar agent context.

## Writing and design

### `humanizer`

Path: `skills/humanizer/SKILL.md`

Rewrite prose to sound natural while preserving facts, intent, and the writer's real voice.

### `unslop`

Path: `skills/unslop/SKILL.md`

Clean technical prose by removing vague, inflated, formulaic, or low-signal writing.

### `impeccable`

Path: `skills/impeccable/SKILL.md`

Design, critique, audit, polish, or improve frontend UI and UX.

## Career

### `resume-review`

Path: `skills/resume-review/SKILL.md`

Review, roast, rewrite, and tailor technical resumes for software engineering and related roles.

Personal resume history and Resume Bank content remain outside this repository.

# Agents

Agents are specialized roles used when isolating responsibility or context improves the result.

Straightforward work should be done directly.

## `pr-reviewer`

Path: `agents/pr-reviewer.md`

Independent reviewer for completed implementation work.

Use before merge when a separate review perspective is useful.

## `engineering-mentor`

Path: `agents/engineering-mentor.md`

Explains engineering concepts and implementation decisions while helping with a task.

Use only when learning or explanation is desired.

## `supabase-database-reviewer`

Path: `agents/supabase-database-reviewer.md`

Review Supabase and PostgreSQL schema changes, migrations, RLS, authorization, and database security.

Only use for projects where Supabase or PostgreSQL database review is relevant.

## `issue-batch-orchestrator`

Path: `agents/issue-batch-orchestrator.md`

Execute an approved multi-issue execution plan.

Coordinates implementation agents, independent reviewers, merge gates, and dependent waves.

## Additional agents

### `spec-reviewer`

Path: `agents/spec-reviewer.md`

Independently review a specification before implementation.

### `test-engineer`

Path: `agents/test-engineer.md`

Design high-value tests around meaningful behavior, regressions, invariants, and critical flows.

# Rules

Rules contain stable engineering constraints.

Procedural workflows belong in skills instead.

## `context`

Path: `rules/context.md`

Defines source precedence, conflict handling, context loading, and how to treat missing information.

## `engineering`

Path: `rules/engineering.md`

General implementation principles for scope, simplicity, architecture, errors, comments, and dependencies.

## `github`

Path: `rules/github.md`

Stable Git and GitHub conventions.

Project-specific Git rules may override these defaults.

## `writing`

Path: `rules/writing.md`

Technical writing rules for accuracy, clarity, signal density, terminology, and claims.

## `security`

Path: `rules/security.md`

General rules for secrets, trust boundaries, authorization, data, privileges, and destructive actions.

## `ui`

Path: `rules/ui.md`

General UI rules for hierarchy, real states, accessibility, responsive behavior, and consistency.

## `definition-of-done`

Path: `rules/definition-of-done.md`

Defines the minimum evidence required before considering engineering work complete.

# Templates

Templates provide lightweight structure for common engineering artifacts.

They are starting points, not mandatory formats.

## `SPEC`

Path: `templates/SPEC.md`

Implementation-ready product or technical specification.

## `PLAN`

Path: `templates/PLAN.md`

Implementation strategy derived from an approved spec.

## `ISSUE`

Path: `templates/ISSUE.md`

Focused GitHub Issue structure.

## `PULL_REQUEST`

Path: `templates/PULL_REQUEST.md`

Concise PR summary and verification structure.

## `HANDOFF`

Path: `templates/HANDOFF.md`

Transfer unfinished work between agents or sessions.

## `BATCH`

Path: `templates/BATCH.md`

Persist an issue orchestration graph, execution waves, gates, and orchestrator prompt.

## `AGENT_TASK`

Path: `templates/AGENT_TASK.md`

Shape a task for delegated work that may need tools, repository access, changes, or verification. Use it when the agent needs a defined outcome, scope, evidence, or delivery report.

## `CHAT_TASK`

Path: `templates/CHAT_TASK.md`

Shape a conversational request for research, writing, analysis, or similar work. Tools may still be used when useful.

Use neither when a direct request is already clear and needs no reusable structure. Keep only sections that affect the task; remove unused optional sections rather than filling them with guesses. In every project, follow its instructions and sources of truth over reusable prompts.

## `DECISION`

Path: `templates/DECISION.md`

Lightweight record for important durable decisions and their rationale.

# Project instructions

Reusable presets for long-running ChatGPT Projects or other AI workspaces with multiple chats.

Project instructions define how an entire project behaves. Individual chats may have different purposes and should use only the relevant parts.

## `resume-workspace`

Path: `project-instructions/resume-workspace.md`

For technical resume review, tailoring, Resume Bank usage, recruiter signal, and truthful positioning.

## `learning-coach`

Path: `project-instructions/learning-coach.md`

For roadmap-driven technical learning with interactive teaching, implementation, debugging, retrieval practice, and mastery checks.

## `interview-prep`

Path: `project-instructions/interview-prep.md`

For coding interviews, DSA, system design, behavioral preparation, mocks, and weakness tracking.

## `software-engineering-project`

Path: `project-instructions/software-engineering-project.md`

For multi-chat software projects covering product thinking, brainstorming, research, decisions, architecture, implementation, UI, database work, and review.

## `course-companion`

Path: `project-instructions/course-companion.md`

For academic courses where syllabus, slides, assignments, and professor-provided material define the primary learning context.

## `general-workspace`

Path: `project-instructions/general-workspace.md`

Universal starting point when no specialized Project Instruction preset fits.

## `research-workspace`

Path: `project-instructions/research-workspace.md`

For long-running, multi-chat research projects with shared sources, findings, decisions, and continuity notes.

# Registry

`registry.yaml` tracks artifact identity and adoption status.

Possible statuses:

- `testing`
- `accepted`
- `rejected`
- `default`
- `replaced`

A workflow being present in this repository does not automatically make it part of the default setup.

# Repository structure

- `skills/` — reusable workflows
- `agents/` — specialized roles
- `rules/` — stable engineering constraints
- `templates/` — reusable artifact structures
- `project-instructions/` — reusable multi-chat project behavior
- `registry.yaml` — artifact identity and adoption status
- `AGENTS.md` — instructions for agents working inside this repository
- `WORKFLOWS.md` — scenario-based guide for choosing workflows

# Principles

- Keep global behavior separate from project-specific context.
- Keep one canonical source for shared instructions.
- Load only the context needed for the current task.
- Prefer the smallest correct implementation.
- Never invent requirements, facts, metrics, test results, or technical decisions.
- Prefer project-specific instructions over reusable defaults.
- Testing something does not automatically make it adopted.
