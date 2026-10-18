# AI Setup

This repository is the canonical source for reusable AI-assisted software engineering configuration, with selected workflows for research, writing, learning, and long-running AI workspaces.

## Context

Project-specific instructions always override reusable configuration from this repository.

Before acting:

1. Read the project's own instructions and sources of truth.
2. Use `rules/context.md` when source precedence or missing context matters.
3. Load only the rules and skills relevant to the current task.
4. Do not invent missing requirements.

## Rules

Load applicable stable rules from `rules/`:

- `context.md` — source precedence and context handling
- `engineering.md` — implementation behavior
- `github.md` — Git and GitHub conventions
- `writing.md` — technical writing
- `security.md` — secrets and trust boundaries
- `ui.md` — UI and accessibility
- `definition-of-done.md` — completion criteria

When durable project context is relevant, consult [knowledge/README.md](knowledge/README.md) and load the `project-knowledge` skill. Search only for notes relevant to the current task.

## Skills

Use `README.md` as the catalog for available configuration and `WORKFLOWS.md` to choose the appropriate workflow, including research and AI workspace setup.

Load only the configuration relevant to the current task.

## Skills-first delivery

Maintain `ai-setup` as the canonical vault for rules, agents, templates, project instructions and skills. When a reusable improvement belongs to an existing repeatable workflow, prioritize updating its installable skill. Make the relevant skill self-contained enough to work after selective global installation without access to the rest of this repository. Embed only a concise task-relevant subset of canonical rules and boundaries; do not duplicate entire artifacts or erase their original ownership. Preserve the separate roles of agents, rules, templates and project instructions.

The `npx skills` CLI distributes skill copies, not arbitrary rules, Codex agent definitions or Project Instructions. Never claim otherwise.

## Agents

Use specialized agents from `agents/` when isolation improves review quality, context management, or teaching.

Do straightforward work directly.

## Adoption

Skills and workflows in this repository may be experimental.

Do not treat catalog presence as evidence that a workflow is accepted or adopted. Prefer demonstrated use and explicit decisions.

## This repository

`ai-setup` is a personal configuration repository and currently permits direct work on `main`.

Do not apply that exception to other repositories unless they explicitly say so.
