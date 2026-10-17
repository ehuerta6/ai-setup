---
name: to-issues
description: Break an approved spec or large feature into focused, connected GitHub Issues that can be implemented independently by fresh agents.
---

# To issues

Turn an approved specification into a dependency graph of implementation-ready GitHub Issues.

The goal is not to create a checklist of technical layers.

The goal is to create small, meaningful units of product behavior that can be implemented and verified independently.

## Process

### 1. Gather context

Read:

- the complete approved spec;
- the parent GitHub Issue when one exists;
- relevant project instructions;
- enough of the existing codebase to understand integration points and current conventions.

Do not reopen product decisions already settled by the spec.

### 2. Identify implementation slices

Prefer vertical slices.

A good issue delivers a narrow but complete behavior across whichever layers are required.

Prefer:

- create a session end-to-end;
- edit an officer end-to-end;
- reveal a solution end-to-end.

Avoid horizontal decomposition such as:

- build database;
- build backend;
- build frontend.

A completed issue should produce something independently testable, demonstrable, or structurally necessary for later work.

### 3. Size issues for agents

Each issue should:

- fit comfortably in one fresh agent context;
- have one clear responsibility;
- avoid unrelated cleanup;
- contain enough context to execute without guessing;
- have observable acceptance criteria and, where behavior changes, a concrete before/after or failure/success scenario another agent can verify;

Split an issue when it contains multiple independently useful behaviors.

Merge issues when separating them would create artificial coordination without useful isolation.

### 4. Determine dependencies

For every issue identify genuine blockers.

Do not create a linear chain unless the work truly requires one.

Independent issues should remain independent so they may be implemented concurrently.

Think of the result as a dependency graph:

Parent spec
├── Issue A
├── Issue B
│   └── Issue D
└── Issue C
    └── Issue E

An issue is ready when all of its blockers are complete.

### 5. Handle broad refactors carefully

Vertical slices are the default.

Use an expand-migrate-contract sequence only for a cross-cutting migration whose mechanical coupling makes independently green vertical slices unsafe or impractical, such as changing a shared schema, type, or contract with many consumers:

1. **Expand:** introduce the new form while keeping the old form compatible; verify both can coexist.
2. **Migrate:** move consumers in bounded batches. Add dependency edges only where a stage or batch is blocked by earlier work, and give each batch a realistic check against the mixed state.
3. **Contract:** remove the old form after all consumers have moved; verify no old use remains and the new form works on its own.

Keep the repository working between stages whenever practical. If even bounded batches cannot remain independently green, say why and define the integration branch and verification gate that will validate the combined migration. Do not promise independent green tickets in that case. Do not use this sequence for ordinary features or local refactors that can be delivered as vertical slices.

### 6. Present the proposed breakdown

Before creating GitHub Issues, show:

1. issue title;
2. what it delivers;
3. acceptance criteria;
4. blockers;
5. relationship to the parent spec.

Ask for approval when the user has not already explicitly authorized creating the issues.

### 7. Create GitHub Issues

Create blockers before dependent issues so dependency references can use real issue numbers.

Use this structure:

## Parent

Reference the parent spec or parent GitHub Issue.

## What to build

Describe the behavior delivered by this issue from the project's perspective.

## Acceptance criteria

- [ ] Observable criterion
- [ ] Observable criterion

## Blocked by

Reference blocking issues.

Use `None` when the issue can start immediately.

## Notes

Include only implementation constraints or decisions needed to preserve the spec.

Omit this section when unnecessary.

### 8. Connect the graph

When GitHub supports the required relationship, use native sub-issue or dependency relationships.

Otherwise reference related issue numbers explicitly in the issue body.

The parent should make it easy to discover the complete implementation set.

## Rules

- The approved spec is the contract.
- Do not silently expand scope.
- Do not invent requirements.
- Prefer vertical slices.
- Do not create one issue per technical layer.
- Do not include exact file paths unless they are a required constraint.
- Do not prescribe implementation details the spec does not require.
- Preserve project terminology.
- Acceptance criteria describe behavior, not implementation steps.
- Dependencies must represent real blockers, not preferred ordering.
- Do not close or modify the parent issue unless explicitly requested.

## Completion

The breakdown is complete when:

- every requirement in the spec is covered;
- every issue has a clear outcome;
- every issue has verifiable acceptance criteria;
- dependencies are explicit;
- no issue requires unresolved product decisions;
- each issue can be understood by a fresh implementation agent.

The resulting issues are ready for `implement-issue`.
