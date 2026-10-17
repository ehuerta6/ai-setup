---
name: verify-change
description: Verify a code change using the repository's actual configured checks and report concrete evidence without hiding failures.
---

# Verify change

Verify that a change works and is safe to deliver.

Do not assume every repository uses the same commands.

Discover the project's real validation workflow first.

## Process

### 1. Identify what changed

Determine:

- intended behavior;
- affected boundaries;
- relevant acceptance criteria;
- likely regression areas.

Use the issue, spec, and final diff as evidence.

### 2. Discover repository checks

Inspect the repository for configured validation such as:

- test scripts;
- type checking;
- linting;
- formatting;
- builds;
- integration tests;
- end-to-end tests;
- database validation;
- CI workflows.

Use project-provided commands instead of inventing replacements.

Before running checks in parallel, identify shared generated files. Sequence checks when one creates, regenerates, or removes files another consumes; parallelize independent checks when safe.

### 3. Run focused checks

During iteration, prefer the smallest check that exercises the changed behavior.

Examples:

- one test file;
- one package;
- one route;
- one affected subsystem.

Do not rerun the full suite after every minor edit.

### 4. Verify actual application behavior

For a change to a user-facing workflow, prefer the project's existing E2E/browser, desktop, CLI, or API harness. If a project-local `verify-*` skill exists, use its documented launch → doctor → drive → evidence → cleanup process for the affected journeys and meaningful regression paths.

Check the user action, observed result, and relevant persisted or external side effect—not merely a screenshot or direct internal state setter. Verify error paths, authorization, and data integrity where they are affected. For bug fixes, compare before/after reproduction when feasible. Keep test instances, accounts, ports, and data isolated; do not pull production data or invoke destructive external actions without authorization.

Do not drive the entire feature map for every PR; target changed behavior and plausible regressions. Use `create-verification-skill` to establish reusable project-local instructions only when a meaningful verification gap warrants it, and `maintain-verification-skill` when that skill or feature map drifts. If interactive verification is not available, clearly report the gap and use the best reliable signal available.

### 5. Run required completion checks

Before delivery, run the repository's relevant full checks.

Only run checks that actually apply to the project and change.

If a check cannot be run:

- say which check;
- explain why;
- identify the resulting verification gap.

### 6. Inspect the final diff

Verify that the diff contains:

- only intended changes;
- no debug output;
- no accidental generated files;
- no credentials or secrets;
- no unexplained dependency additions;
- tests when behavior changed.

For documentation changes, check behavior and deployment claims against current code and accepted decisions. Distinguish dated deployment observations from current state, and validate relevant internal links and anchors when practical.

### 7. Report evidence

For real-app verification, record the journey driven, environment, tested revision, observed behavior and side effects, and sanitized evidence artifacts. Screenshots or recordings supplement explicit assertions; do not treat visual appearance alone as proof of persistence or correctness.

Report each meaningful check and its actual result, identifying the exact
revision it evaluated. For PR verification, capture the current head SHA and
associate hosted checks with that SHA; keep local, CI, Preview, and manual
results distinct. After a rebase, new commit, or integration, refresh evidence
for the new head instead of carrying forward earlier results.

Confirm that required checks and relevant tests actually executed. A green
workflow does not cover tests or jobs marked skipped, pending, or
`action_required`. State those gaps and any fork or external authorization
needed; do not describe incomplete verification as complete.

Example:

- `npm test`: passed
- `npm run typecheck`: passed
- `npm run build`: failed because `<reason>`
- manual browser verification: not performed

Never convert an unrun check into a pass.

When claiming an experimental or validation procedure is reproducible, replay its described setup and commands from a clean starting state when feasible. State relevant prerequisites, source/ref/branch state, generated parent directories, and execution or lifecycle order needed to reproduce it. If only part was replayed or a full replay was unavailable, identify what was verified and the remaining gap; do not claim complete reproducibility. This does not require unrelated tests or expensive experiments when reproducibility is not being claimed.

## Rules

- Verification is evidence, not assumption.
- Prefer configured project commands.
- Do not bypass or disable failing checks to make the change appear complete.
- Do not hide failures.
- Automated checks passing does not prove the product requirement was implemented correctly.
- Verify both behavior and repository health.

## Completion

Verification is complete when:

- the changed behavior has a direct verification signal;
- relevant repository checks have been run;
- the final diff has been inspected;
- all results and remaining gaps are reported accurately.
