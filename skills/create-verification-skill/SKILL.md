---
name: create-verification-skill
description: Create an executable project-local skill for verifying real user-facing application behavior and preserving observable evidence.
---

# Create verification skill

Use when a project has no repeatable agent-readable way to exercise its real app. Generate a **project-local** skill, not generic test advice. Reuse an established harness or verification skill where one already exists.

Adapted from [PStack's create-verification-skill](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md) for host-independent workflows and Codex. The project's requirements, policies, and architecture always take precedence.

## Inspect the project

Discover from source and instructions before asking the user:

- **Surface:** web, desktop, CLI/TUI, API, mobile, or library; identify primary user journeys.
- **Launch:** real setup, dependencies, migrations, seeded accounts, test environment, ports, and usable readiness indicator.
- **Drive:** prefer existing E2E and browser automation, PTY helpers, or HTTP contracts. Use stable selectors and commands, not screen coordinates where avoidable.
- **Observe:** action, visible state, exit code, response, DB or file side effect, audit log, and other meaningful assertions.
- **Isolate:** own test ports, user accounts, data directories, services, and processes so parallel agents do not corrupt one another's work.

Avoid production systems, sensitive production data, live payments, and destructive actions unless the user explicitly authorized the particular operation. Prefer synthetic or appropriately sanitized fixtures. Do not call a broken or inaccessible development environment ready.

## Generate a portable project skill

Write to the project's supported local skill directory, normally `.agents/skills/verify-<app>/` for Codex, or another directory required by its agent host. Use a short app-specific slug. Supply valid `SKILL.md` frontmatter with `name` and a precise `description`.

The generated skill must stand alone when another agent reads it cold:

1. **Launch:** exact prerequisites and commands, migrations/seed procedure if required, *usable* readiness signal, and teardown. A responding health endpoint alone may not prove readiness.
2. **Doctor:** quick read-only checks of the specific process, port ownership, build, authentication, and backing dependencies. Run before driving and again after unexpected failures.
3. **Drive:** actual user-path steps with concrete selectors, API requests, prompt strings or commands from this app and observable assertions.
4. **Evidence:** evidence location and formats (screenshots, recordings, CLI transcripts, logs, responses, persisted effects). Capture the initiating action **and** outcome, not only an attractive final screen; associate evidence with revision/environment and redact secrets.
5. **Cleanup:** stop only owned processes and remove owned scratch state while retaining evidence. Never kill by broad process name or trust an unverified dry-run not to mutate state.
6. **Helpers:** include executable scripts only where necessary, with runnable instructions; prefer the project's installed tools to new dependencies.

## Seed a useful feature map

Create `features/README.md` and a small number of separate feature documents (start with 3–5 genuinely important journeys). Each records what users do, entry path, required role/data, exact drive procedure, expected outcomes including relevant failure states, externally observable side effects, and known caveats.

Use requirements and source as the authority; do not fabricate selectors, seed users, or scenarios. Cover critical auth, persistence, and integrity paths where relevant. One happy path does not establish complete system correctness.

## Prove what you wrote

Execute launch → doctor → drive **one mapped feature** → capture evidence → cleanup on the target environment. Confirm evidence remains after teardown. Clean up failed attempts. If the run is blocked, keep the output clearly marked *unverified* and report prerequisites and failures; never claim a proven skill based on instructions alone.

Hand off the new skill's location and trigger to the project's workflow. Use `maintain-verification-skill` when its map or harness becomes stale. Do not run every mapped feature on every small PR.
