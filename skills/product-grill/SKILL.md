---
name: product-grill
description: Rigorously clarify product goals, users, scope, workflows, permissions, constraints, and observable behavior without asking the user to design technical internals.
---

# Product grill

Use when product intent or behavior needs rigorous discovery and the user should not have to choose implementation details. For a familiar design where the user wants to resolve product and technical decisions together, keep using `grill-me`.

The goal is a shared, challenging account of what the product should do and why. This skill discovers product requirements; it does not research or select an architecture.

## Process

1. Read the conversation and relevant project instructions, decisions, specs, issues, and code. Separate known facts from product choices; inspect facts that are already available instead of asking the user to repeat them.
2. Establish the problem, desired outcomes, target users, and important use cases. Then clarify observable features and behavior, workflows, scope and priorities, autonomy and permissions, constraints, and acceptable user-facing tradeoffs. Ask focused questions in manageable rounds, explaining the product decision each question resolves. Use concrete examples and recommend an option only when its product consequences support that recommendation.
3. Challenge the emerging requirements. Look for ambiguous terms, contradictions, unsupported assumptions, missing actors or states, and behavior that would force an implementer to guess. Walk through normal, edge, failure, recovery, and permission-sensitive scenarios that matter. Revisit earlier answers when a later decision changes their implications.
4. Keep technical ownership with engineering. Accept technical preferences or constraints the user volunteers, and ask about technical matters only to clarify an intentional preference or a real product constraint. When implementation choices have different user-visible effects, explain those effects in plain language and ask about the desired behavior. Record architecture, storage, protocol, algorithm, integration, or feasibility questions for later investigation; do not ask the user to pick among them or silently choose one.
5. Continue until important product behavior, priorities, and user-facing tradeoffs are clear enough to specify. Unresolved technical investigation does not by itself block product discovery. If broader research or design is needed, point to the existing appropriate workflow, such as `research-and-compare`, `adversarial-discovery`, or `adversarial-design`.

## Discovery handoff

Summarize the result for `to-spec`, keeping these categories distinct:

- **Confirmed product decisions** — choices explicitly made by the user.
- **Recommendations** — product options proposed but not approved.
- **Assumptions and hypotheses** — beliefs that need evidence or validation.
- **Open product questions** — user decisions still needed, and the behavior they affect.
- **Technical uncertainties for investigation** — questions for engineering or research, with relevant product constraints and expected user-visible consequences.

Include the problem, users and use cases, goals, scope and priorities, key workflows and observable behaviors, constraints, permissions, and relevant edge or failure cases. Do not present recommendations, assumptions, or technical guesses as confirmed decisions.

## Completion

The handoff makes clear what the product should do, for whom, and under what user-facing constraints; exposes consequential assumptions and unresolved product choices; and leaves technical investigation visible without turning it into a user architecture interview. It is ready to pass to `to-spec`, which can record unresolved questions without inventing answers.
