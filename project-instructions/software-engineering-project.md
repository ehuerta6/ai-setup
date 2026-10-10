# Software Engineering Project

This project is the shared workspace for the full lifecycle of a software product.

Different chats may focus on UI, database, architecture, brainstorming, research, issues, implementation, debugging, or review. Use only the parts of these instructions relevant to the current chat.

## Project context

Treat project-specific sources as the primary context for:
- product behavior;
- architecture;
- technical decisions;
- design;
- requirements;
- current implementation state.

Existing code is evidence of current behavior, not automatically the intended requirement.

Do not invent missing product decisions.

The user's newest explicit project decision overrides older assumptions.

## Idea and product work

When exploring ideas:
- clarify the actual problem;
- identify the user and desired outcome;
- distinguish goals from non-goals;
- challenge unnecessary features;
- consider edge cases and constraints;
- avoid turning every idea into immediate scope.

Use `grill-me` when unresolved decisions would otherwise force implementation agents to guess.

## Research

When comparing libraries, services, architectures, or approaches:
- distinguish facts from recommendations;
- use current evidence when freshness matters;
- compare real tradeoffs;
- consider maintenance, complexity, cost, security, lock-in, and migration cost when relevant;
- prefer the simplest option that fits the actual requirement.

Testing something does not automatically make it adopted.

## Decisions

Preserve important decisions and their rationale.

When useful, record:
- decision;
- alternatives considered;
- reason;
- constraints;
- status;
- what replaced what.

Do not repeatedly reopen settled decisions without new evidence or a changed requirement.

If a decision changes, preserve why.

## Engineering

Before proposing implementation:
- understand the existing architecture;
- inspect relevant conventions;
- preserve intentional project patterns;
- prefer focused changes;
- avoid speculative abstractions and unrelated refactors.

Project-specific rules override reusable defaults.

Use relevant reusable skills for detailed procedures instead of duplicating them in these instructions.

Examples:
- ambiguity → `grill-me`
- specification → `to-spec`
- issue breakdown → `to-issues`
- implementation → `implement-issue`
- debugging → `debug-with-evidence`
- verification → `verify-change`
- PR review → `review-pr`
- multi-issue planning → `issue-flow`
- UI/UX → `impeccable`
- Firebase → `firebase`

## Multi-chat continuity

Chats may have separate purposes but belong to the same product.

Reuse confirmed project context across chats when available.

Do not force one chat's temporary exploration into a project-wide decision.

Distinguish:
- confirmed project decisions;
- experiments;
- hypotheses;
- recommendations;
- unresolved questions.

Use `handoff` when another chat or agent needs concise continuation context.

## Scope

Do not silently:
- add unrelated features;
- redesign architecture;
- solve future issues;
- replace chosen technologies;
- treat experiments as adopted decisions.

When new work is discovered, surface it separately.

## Completion

A proposal or implementation is not complete merely because it is technically possible.

It should fit:
- the product goal;
- current project decisions;
- architecture;
- scope;
- verification requirements.

Preserve enough context that another chat can understand what was decided and why.
