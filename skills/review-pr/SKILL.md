---
name: review-pr
description: Review a pull request or completed diff separately against its requirements and against the repository's engineering standards.
---

# Review PR

Review completed work along two independent axes:

1. requirements;
2. engineering quality.

A change can succeed on one axis and fail on the other.

Do not let good code excuse incorrect product behavior, or correct behavior excuse unsafe code.

## Process

### 1. Gather context

Read:

- the complete diff;
- linked issue;
- acceptance criteria;
- approved spec when available;
- relevant project instructions;
- surrounding implementation where needed.

When repository knowledge is relevant to the diff, inspect only the related notes and load `project-knowledge` when available. Check that notes distinguish approved intent from current behavior. Suggest an on-demand Knowledge Review if the diff reveals material possible staleness or contradiction; do not start a full review unless requested.

Review the whole change, not isolated snippets.

### 2. Review requirements

Check whether the implementation:

- satisfies every acceptance criterion;
- matches the approved spec;
- preserves explicitly required behavior;
- omits requested behavior;
- adds behavior that was not requested;
- handles required states and edge cases.

Report requirement mismatches separately from code-quality findings.

### 3. Review engineering quality

Check for:

- correctness bugs;
- regressions;
- unsafe assumptions;
- unnecessary complexity;
- speculative abstractions;
- unnecessary dependencies;
- duplicate logic where an established project pattern already exists;
- missing validation;
- missing tests;
- error handling that hides failures;
- security or authorization mistakes;
- data integrity problems;
- accessibility regressions when UI changed.

Respect documented project standards over generic preferences.

Do not report stylistic preferences that tooling already enforces.

### 4. Review structural simplicity when warranted

For nontrivial changes, consider whether the same behavior could be achieved with fewer concepts, branches, mutable flags, wrappers, or layers. Look for meaningful maintainability problems, not a mandated refactor:

- special-case conditionals scattered into unrelated paths instead of one clear domain boundary;
- abstraction, pass-through helpers, or configuration modes that create indirection without reducing complexity;
- logic placed in the wrong ownership layer, duplicated canonical helpers, or coupled components;
- loosely typed boundary data, unnecessary casts or optionality that hides actual invariants;
- related writes that can leave partial state rather than an appropriate atomic update;
- unnecessarily serialized independent work when this materially complicates orchestration;
- modules whose growth, especially crossing around 1,000 lines, **signals** a cohesion problem; size alone is never a failure.

Propose a simpler structure only with a concrete failure mode or material readability/maintenance benefit. Preserve the existing architecture unless the requested change warrants altering it; do not recommend sweeping refactors or abstractions merely to shorten code. The review remains read-only unless the user authorizes edits.

### 5. Evaluate verification

Check whether the evidence actually demonstrates the changed behavior.

Look for:

- missing tests;
- tests that only verify implementation details;
- acceptance criteria with no verification;
- checks claimed as passing without evidence;
- missing real user-path proof for a change that affects application behavior;
- evidence that omits persistent side effects, permission boundaries, or failure states relevant to the change.

Calibrate depth to blast radius, criticality, integration boundaries, reversibility, persistence and data-integrity impact, security and authorization implications, plausible regressions, and available verification evidence. For high-consequence changes, examine critical assumptions and likely regression paths beyond the diff, verify the most consequential against real code or tests when feasible, and report gaps. Keep this focused; isolated, reversible changes do not need an exhaustive audit.

### 6. Report findings

Order findings by severity.

For each finding include:

- severity;
- file or relevant location;
- what is wrong;
- concrete failure scenario or impact;
- requirement or standard involved when applicable.

Do not manufacture findings to make the review look thorough. Multiple model approvals are not a substitute for independent evidence and checks.

If no actionable findings exist, say so.

### 7. Report residual risk

After findings, note meaningful verification gaps or areas not exercised.

Give a clear recommendation:

- ready;
- changes required.

## Review axes

Keep these mentally separate:

### Requirements

Did we build the right thing?

### Engineering

Did we build it safely and maintainably?

## Rules

- Findings first.
- Evidence over preference.
- Do not nitpick for volume.
- Do not silently broaden the issue scope.
- Do not treat generic best practices as project requirements.
- Do not rewrite the implementation during review unless explicitly asked.
- Do not invent defects without a plausible failure mode.

## Completion

A review is complete when:

- the full diff has been inspected;
- requirements have been checked;
- engineering quality has been checked;
- verification gaps are identified;
- actionable findings include evidence;
- the final recommendation is clear.
