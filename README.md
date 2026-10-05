# AI Setup

My version-controlled environment for AI-assisted software engineering.

This repository stores reusable skills, agents, engineering rules, templates, and setup configuration that can be shared across projects.

Project-specific product requirements, architecture, and technical decisions stay inside each project's repository.

## Structure

| Directory | Purpose |
| --- | --- |
| `skills/` | Reusable workflows and capabilities for AI agents |
| `agents/` | Specialized agent roles and responsibilities |
| `rules/` | Stable engineering and collaboration rules |
| `templates/` | Reusable specs, plans, issues, PRs, and other artifacts |
| `setup/` | Configuration for AI development tools |
| `scripts/` | Installation, synchronization, and validation utilities |

## Development workflow

```text
grill-me
→ to-spec
→ to-issues
→ implement-issue
→ verify-change
→ review-pr
```

Supporting skills are used when applicable.

## Principles

- Keep global behavior separate from project-specific context.
- Keep one canonical source for shared instructions.
- Load detailed context only when relevant.
- Prefer the smallest correct implementation.
- Never invent requirements, facts, test results, or technical decisions.
- Adapt third-party skills instead of blindly copying them.
- Testing a workflow does not automatically make it a default.

## Status

This repository and its workflows are currently being built and evaluated.
