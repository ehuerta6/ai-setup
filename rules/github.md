# GitHub

Stable Git and GitHub conventions.

Use the `github-flow` skill for the procedural workflow.

Project-specific Git rules may override these defaults.

## Changes

Keep each logical change focused.

Do not mix unrelated work into the same commit or pull request.

## Branches

For normal collaborative repositories, prefer short-lived branches from the latest `main`.

Common prefixes:

- `feat/`
- `fix/`
- `docs/`
- `refactor/`
- `chore/`
- `ci/`

A repository may explicitly choose direct work on `main`, especially for personal configuration or low-risk repositories.

Respect that project decision.

## Commits

Use Conventional Commit-style messages when the project does not specify otherwise.

Examples:

- `feat: add session controls`
- `fix: prevent duplicate events`
- `docs: clarify setup workflow`
- `refactor: simplify state handling`
- `chore: update tooling`

Commits should describe what changed, not narrate the development process.

## Issues

Read the full issue and relevant comments before implementation.

Treat accepted scope and acceptance criteria as constraints.

Do not silently expand the issue.

## Pull requests

A PR should make it easy to understand:

- the problem;
- the change;
- how it was verified;
- material decisions or limitations.

Link implementation issues with:

`Closes #<issue-number>`

Do not duplicate the entire issue body.

## Verification claims

Never state that a check passed unless it actually ran successfully.

Report checks that were:

- passed;
- failed;
- skipped;
- unavailable.

## Merge

For collaborative repositories, prefer Squash and Merge unless the project says otherwise.

Do not merge work unless the user or repository workflow grants that authority.

## Repository hygiene

Never intentionally commit:

- credentials;
- API keys;
- tokens;
- private keys;
- secrets;
- local environment files containing sensitive values;
- accidental editor or generated files.

Respect `.gitignore`.
