---
name: prototype
description: Build a disposable UI or logic prototype to answer a concrete design question before production implementation.
---

# Prototype

Use this optional workflow when a specific uncertainty is faster or clearer to explore by trying an isolated alternative than by discussing it. Every prototype must state the concrete question it is meant to answer. If no question can be stated, do not prototype.

Prototypes are temporary learning tools. Mark their files and UI clearly as disposable, and remove them from the main implementation when the experiment ends unless the user explicitly asks to keep a specific part. Do not merge prototype code into production by default.

## Choose a path

### UI prototype

Use when the question concerns layout, interaction, usability, or a screen's important states.

- Build a small set of meaningfully different alternatives that make the trade-offs easy to compare.
- Include the key states that could change the choice, such as empty, loading, error, disabled, and success states when relevant.
- Make switching alternatives straightforward and keep the comparison in one place when practical.
- Use the project's existing technology, components, and conventions where they help answer the question.
- Focus on structure and interaction. Skip production polish and unrelated features.
- Leave detailed UI/UX critique and refinement to `impeccable`.

### Logic prototype

Use when behavior, a state machine, transitions, or edge cases are difficult to reason about on paper.

- Represent the relevant states and allowed transitions explicitly.
- Show the current state and transition history after each action.
- Provide controls for important valid cases, edge cases, and invalid transitions.
- Keep the model small enough that a person can explore it directly.
- Use local fixtures or in-memory state. Keep it isolated from production data, services, and side effects.

## Constraints

- Prefer the project's existing stack and simplest runnable setup.
- Do not add infrastructure, dependencies, persistence, or abstractions unless the design question requires testing that specific concern.
- Never use real production data when a local fixture or isolated environment is sufficient.
- Add only enough error handling to run the experiment and see its result.
- Do not write production-level tests or harden the prototype as if it were production code.
- Keep the prototype easy to find and run, and make its temporary status unmistakable.

## Close the experiment

Summarize the question, alternatives tried, observations, limitations, and the decision or remaining uncertainty. Record a durable product or architecture decision with `templates/DECISION.md` only when it is important, non-obvious, and likely to matter later. Include relevant findings in the spec or implementation handoff.

A prototype can inform `to-spec`; it does not replace resolving decisions with `grill-me` or specify implementation by itself. Retain or merge prototype code only when the user explicitly requires it. Otherwise remove it from the main implementation.

## Example scenario

Illustrative only; this prototype has not been executed.

**Question:** Should a review request become actionable immediately after it is reopened, or only after its owner reassigns it?

A logic prototype could model `draft`, `open`, `reopened`, and `closed` states with controls for submit, close, reopen, and reassign. It would show the current owner and transition history, then let someone try reopening an unassigned request and attempting an invalid transition from `closed` directly to `reassigned`. Use local sample records only. The result should settle the intended state rules, not supply production code.
