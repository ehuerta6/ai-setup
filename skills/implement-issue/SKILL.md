---
name: implement-issue
description: Implement one approved GitHub Issue from scope discovery through a verified, review-ready change.
---

# Implement issue

Implement exactly one approved GitHub Issue.

The issue defines the scope. Project instructions, approved specs, and explicit user decisions define the requirements around it.

## Process

### 1. Read the work

Read the complete issue:

- title;
- body;
- acceptance criteria;
- comments;
- linked specs;
- linked issues;
- blockers.

Identify the behavior the issue must deliver.

If the issue depends on unresolved product decisions, stop implementation and surface them.

### 2. Inspect the repository

Before editing:

- read applicable project instructions;
- inspect surrounding implementation;
- inspect related tests;
- identify existing patterns and abstractions;
- identify configured validation commands;
- inspect relevant schema, API, state, or UI boundaries.

When `knowledge/README.md` exists and durable context could affect the issue, read its guide and retrieve only relevant notes. Load `project-knowledge` when available. Capture or update a note only when the work produces durable knowledge; a routine issue does not require one.

Use the existing architecture unless the issue requires changing it.

### 3. Define the minimum change

Determine:

- which behavior must change;
- which parts of the system are affected;
- which existing patterns should be reused;
- what explicitly remains outside scope.

Prefer the smallest **complete and readable** change. Apply the existing engineering rules even when only this skill is installed:

1. Omit behavior not required by the issue.
2. Reuse the project's existing implementation and domain patterns.
3. Use platform or standard-library capabilities before adding dependencies.
4. Reuse installed dependencies where appropriate.
5. Implement the smallest correct new code when none of the above meets the requirement.

Avoid speculative factories, generalized services, wrappers, future-facing flags, and parallel abstractions. Don't equate fewer lines with better code; preserve necessary validation, failures, access controls, and tests. Keep explanatory comments for invariants, constraints, and non-obvious tradeoffs rather than narrating obvious code.

When the approach depends on an unfamiliar or version-sensitive API or an external integration, check the project's installed versions and the relevant authoritative documentation before choosing an approach. Skip external research for routine internal changes.

Do not bundle cleanup or refactors that are not required.

### 4. Implement incrementally

Make focused edits.

When behavior changes:

- add or update appropriate tests;
- preserve existing behavior outside the issue;
- reuse existing dependencies and patterns when suitable;
- avoid speculative abstractions or future-facing architecture.

If a bug appears during implementation, use `debug-with-evidence`.

### 5. Verify acceptance criteria

Before considering implementation complete:

- check every acceptance criterion individually;
- verify the user-visible behavior through its actual interface, using a maintained project-local verification skill or existing harness when available;
- confirm no requirement was silently skipped;
- confirm no unrequested behavior was added.

Then use `verify-change` when installed. If it is unavailable, execute the repository's configured focused and required completion checks directly, inspect the final diff, and report precise results and gaps; never assume a sibling skill was installed.

### 6. Review the final diff

Inspect the complete diff.

Look for:

- unrelated edits;
- accidental files;
- debug code;
- stale comments;
- missing tests;
- unnecessary dependencies;
- requirement mismatches;
- scope creep;
- incidental branching and extra layers that could be removed without changing behavior.

### 7. Prepare delivery

Use `github-flow` for commit and PR conventions.

Report:

- what changed;
- what was verified;
- any relevant limitations or decisions;
- anything intentionally left out of scope.

Do not merge unless the user explicitly asks for the merge.

## Rules

- The issue is a scope boundary, not permission to redesign adjacent systems.
- Do not invent missing requirements.
- Read before editing.
- Prefer current project patterns over introducing new ones.
- Prefer simple, direct code.
- Do not hide failures with broad exception handling or arbitrary defaults.
- Do not claim checks passed unless they were actually run.
- Do not silently modify unrelated behavior.

## Completion

The issue is implementation-complete when:

- all acceptance criteria are satisfied;
- the implementation matches the approved requirements;
- relevant tests exist;
- validation succeeds or failures are reported accurately;
- the final diff contains only intentional changes;
- the change is ready for review.
