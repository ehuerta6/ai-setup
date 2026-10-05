---
name: github-flow
description: Apply the shared Git and GitHub conventions for commits, issues, pull requests, merging, and repository hygiene.
metadata:
  adapted_from:
    - cappycode git conventions
    - cappy-hub development workflow
---

# GitHub flow

Use the repository's own documented Git conventions when they exist.

These rules provide the default when the project does not specify otherwise.

## Scope

This skill covers:

- Git branches;
- commits;
- GitHub Issues;
- pull requests;
- merge preparation;
- repository hygiene.

## Repository-specific overrides

Project instructions may intentionally override these defaults.

For example, a personal configuration repository may explicitly allow direct work on `main`.

Honor the project's explicit workflow instead of forcing this skill's defaults.

## Branches

For normal collaborative project development:

- do not work directly on `main`;
- start from the latest `main`;
- use short-lived branches;
- keep each branch focused on one logical change.

Recommended prefixes:

- `feat/`
- `fix/`
- `docs/`
- `refactor/`
- `chore/`
- `ci/`

Use short descriptive names.

## Commits

Use Conventional Commit-style messages.

Examples:

- `feat: add session reveal controls`
- `fix: prevent duplicate live sessions`
- `docs: clarify local database workflow`
- `refactor: simplify session state handling`
- `chore: update development tooling`

A commit should represent one coherent change.

Do not mix unrelated edits into the same commit.

## Issues

Read the complete issue before implementation.

Treat acceptance criteria and explicit scope as constraints.

Do not silently expand scope.

When implementation reveals additional work, surface it separately instead of smuggling it into the current issue.

## Pull requests

Keep one logical change per PR.

A PR should explain:

## Summary

What problem the change addresses and what changed.

## Verification

What was actually run or manually verified.

## Decisions

Only include material implementation decisions or limitations that reviewers need to know.

Do not repeat the entire issue.

When implementing an issue, link it with:

`Closes #<issue-number>`

Use a Conventional Commit-style PR title.

## Before opening a PR

- update from the latest target branch;
- inspect the complete diff;
- remove debug code and accidental files;
- run relevant configured checks;
- verify acceptance criteria;
- confirm no secrets are included.

Never claim a check passed unless it was actually run.

## Merge

Default collaborative workflow:

- prefer Squash and Merge;
- use the PR title as the squash commit message;
- delete the feature branch after merge.

Do not merge unless the user explicitly requests it or the project's workflow explicitly grants that authority.

## Repository hygiene

Do not commit:

- secrets;
- API keys;
- passwords;
- private keys;
- local environment files;
- accidental generated artifacts;
- unrelated editor files.

Respect the repository's `.gitignore`.

## Rules

- Explicit project Git rules override these defaults.
- Keep changes focused.
- Preserve traceability from issue to implementation to PR.
- Do not hide failing checks.
- Do not rewrite shared history unless explicitly required and safe.
