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

## Skills

Use `README.md` as the catalog for available configuration and `WORKFLOWS.md` to choose the appropriate workflow, including research and AI workspace setup.

Load only the configuration relevant to the current task.

## Agents

Use specialized agents from `agents/` when isolation improves review quality, context management, or teaching.

Do straightforward work directly.

## Adoption

Skills and workflows in this repository may be experimental.

Check `registry.yaml` before treating something as an established default.

Testing does not imply adoption.

## This repository

`ai-setup` is a personal configuration repository and currently permits direct work on `main`.

Do not apply that exception to other repositories unless they explicitly say so.
