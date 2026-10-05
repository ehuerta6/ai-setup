# AI Setup

Canonical reusable configuration for AI-assisted software engineering.

This repository contains reusable skills, agents, engineering rules, and templates that can be selectively copied into individual projects.

Project-specific requirements, architecture, product behavior, and technical decisions stay inside each project repository.

## How to use this repository

When applying this setup to another project:

1. Inspect that project's existing AI instructions, architecture, stack, Git workflow, and conventions.
2. Read this README as the catalog of available reusable configuration.
3. Select only the skills, agents, rules, and templates that actually apply.
4. Prefer existing project-specific instructions when they contain intentional product or architecture behavior.
5. Copy the exact canonical files from this repository instead of recreating them from the descriptions below.
6. Do not copy everything by default.
7. Keep project-specific context inside the project.

Before modifying the target project, present the proposed files to add, keep, replace, or skip.

## Typical development flow

Idea
→ `grill-me`
→ `to-spec`
→ `to-issues`
→ `implement-issue`
→ `verify-change`
→ `review-pr`

For batches of related issues:

Issues
→ `issue-batch-orchestrator`
→ `batch-orchestrator`
→ implementation agents
→ independent review
→ merge gates

Supporting skills are used only when relevant.

# Skills

## Planning

### `grill-me`

Path: `skills/grill-me/SKILL.md`

Use when a feature, product decision, or implementation plan still contains ambiguity.

Stress-tests decisions before implementation so agents do not have to guess.

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

### `github-flow`

Path: `skills/github-flow/SKILL.md`

Execute the repository's Git and GitHub workflow for branches, commits, issues, PRs, and merging.

Project-specific Git rules override its defaults.

### `issue-batch-orchestrator`

Path: `skills/issue-batch-orchestrator/SKILL.md`

Analyze multiple GitHub Issues and build safe parallel or sequential execution waves.

Optimizes for maximum safe parallelism and explicit merge gates.

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

### `writing-for-agents`

Path: `skills/writing-for-agents/SKILL.md`

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

## `mentor`

Path: `agents/mentor.md`

Explains engineering concepts and implementation decisions while helping with a task.

Use only when learning or explanation is desired.

## `supabase-database-reviewer`

Path: `agents/supabase-database-reviewer.md`

Review Supabase and PostgreSQL schema changes, migrations, RLS, authorization, and database security.

Only use for projects where Supabase or PostgreSQL database review is relevant.

## `batch-orchestrator`

Path: `agents/batch-orchestrator.md`

Execute an approved multi-issue execution plan.

Coordinates implementation agents, independent reviewers, merge gates, and dependent waves.

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

# Project instructions

Reusable presets for long-running ChatGPT Projects or other AI workspaces with multiple chats.

Project instructions define how an entire project behaves. Individual chats may have different purposes and should use only the relevant parts.

## `resume-reviews`

Path: `project-instructions/resume-reviews.md`

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

# Registry

`registry.yaml` tracks adoption status and provenance.

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
- `registry.yaml` — adoption status and provenance
- `AGENTS.md` — instructions for agents working inside this repository

# Principles

- Keep global behavior separate from project-specific context.
- Keep one canonical source for shared instructions.
- Load only the context needed for the current task.
- Prefer the smallest correct implementation.
- Never invent requirements, facts, metrics, test results, or technical decisions.
- Prefer project-specific instructions over reusable defaults.
- Testing something does not automatically make it adopted.
