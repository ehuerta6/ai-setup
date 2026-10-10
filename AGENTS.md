# SetupSmith

This repository is the canonical source for reusable AI-assisted software engineering configuration, with selected research, writing, learning, and multi-chat workflows. SetupSmith also plans guided per-project recommendation, installation, version tracking, and safe selective updates.

For product-development work, read [docs/setupsmith-mvp.md](docs/setupsmith-mvp.md). The CLI supports read-only catalog discovery and managed-skill checks/diffs, plus explicitly approved selective installation, adoption, updates, restoration, and removal; see [docs/managed-skill-installation.md](docs/managed-skill-installation.md) for commands and limits. The standalone `setup-ai` skill supports read-only Analyze → Recommend. Codex uses `$setup-ai` or `/skills`; Claude Code uses `/setup-ai`. Automatic synchronization is not implemented. Do not claim unavailable commands work. Catalog maintenance remains a separate, equally valid responsibility.

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

`ehuerta6/setupsmith` is a personal configuration repository and currently permits direct work on `main`.

Do not apply that exception to other repositories unless they explicitly say so.
