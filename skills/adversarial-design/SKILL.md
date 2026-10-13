---
name: adversarial-design
description: Coordinate an adaptive end-to-end design phase for a product or major software feature, producing a traceable, approval-ready specification.
---

# Adversarial design

Use for a product idea or major feature whose implementation depends on
multiple unresolved product, behavior, or architecture decisions. Coordinate
existing project discovery and design capabilities into one coherent Design
Package. This is an experimental testing workflow, not a required step for
every project. For a simple bounded ambiguity, use `grill-me`; for settled
requirements, use `to-spec` or the project's ordinary implementation flow.

The objective is to reduce unresolved implementation decisions and late
redesign through evidence and explicit decisions. It cannot guarantee a
perfect design or eliminate user participation. Do not implement application
code as part of this workflow.

## Process

Adapt the phases to project scale and risk. Skip phases that add no value and
iterate only where a later finding exposes an upstream conflict.

1. **Ground in the project.** Read project instructions, current sources of
   truth, accepted specifications and decisions, and relevant architecture or
   code. Establish the problem, users, goals, constraints, non-goals, current
   system boundaries, and accepted decisions. Do not ask the user for facts
   available in those sources. Separate genuinely user-dependent choices from
   questions answerable by inspection or research.
2. **Order the open decisions.** Build a lightweight Decision Dependency
   Graph: list unresolved decisions, their dependencies, impact, reversibility,
   and evidence needed. Resolve foundational, high-impact, or blocking
   decisions before downstream details. Use `grill-me`'s decision-tree method
   for questions requiring the user's judgment; do not duplicate its interview
   procedure.
3. **Research and deliberate selectively.** Use `research-and-compare` for
   decisions that depend on current external evidence. Prefer primary sources,
   record provenance, and distinguish fact, inference, and recommendation.
   Use `adversarial-discovery` only when independent analysis and structured
   challenge can materially improve a consequential or contested decision.
   Record outcomes as proposals until approved. Keep ordinary decisions in
   their simplest adequate workflow.
4. **Evaluate architecture against real needs.** Compare viable architectures
   using the project's actual quality attributes and scenarios, such as
   persistence consistency, local-first behavior, security, deployment,
   performance, maintainability, interoperability, or cost when relevant.
   Record responsibilities, interfaces, constraints, evidence, compromises,
   and why rejected options did not fit. Preserve accepted architecture unless
   evidence or an explicit requirement warrants revisiting it. Keep consequential
   architecture decisions **Proposed** until approved.
5. **Model end-to-end behavior.** Describe the important actors and journeys,
   permissions, states and transitions, invariants, data flows and contracts,
   failure handling, recovery, concurrency, and edge cases that matter to the
   feature. Use a flow, table, or state model only where it clarifies behavior
   or exposes a decision. Derive security, privacy, and data-integrity analysis
   from the system's trust boundaries and data handling.
6. **Experiment when evidence needs it.** Invoke `prototype` for a concrete
   uncertainty better answered by a disposable UI or logic experiment than by
   research or discussion. State the question and alternatives; isolate it
   from production systems and data; report observations and limitations; and
   remove it when done unless the user explicitly asks to keep part. Do not use
   a prototype as production implementation.
7. **Validate by risk.** Check the design against relevant failure, trust,
   permission, privacy, migration, data-integrity, operational, and recovery
   risks. Prioritize scenarios whose failure would make the design unsafe,
   inconsistent, or impossible to implement correctly. Record evidence,
   assumptions, mitigations, and unresolved risks; do not apply an irrelevant
   universal checklist.
8. **Consolidate the Design Package.** The coordinator is the single writer of
   the evolving design. Assemble requirements and findings with source links,
   decision IDs, affected requirements, and revision traceability. Use
   `templates/DECISION.md` for durable non-obvious choices when useful. Use
   `to-spec` to structure only resolved and approved decisions; it does not
   conduct discovery or turn proposals into confirmed requirements. Adapt
   `templates/SPEC.md` to local conventions. Keep the package in one or more
   project-local documents according to its size; do not create a mandatory
   file tree or duplicate source material.
9. **Review and simulate implementation readiness.** When a specification
   exists, use `spec-reviewer` to find contradictions, missing behavior,
   unsupported claims, and untestable criteria. Then ask a fresh implementing
   perspective, if real isolation is available, to outline components,
   contracts, observable behavior, tests, edge and failure cases, and an
   implementation order without writing production code. Ask: **What would an
   implementer still have to guess?** Report exact blocking requirements or
   decision IDs. If isolation is unavailable, disclose that limitation and
   perform only an explicitly non-independent self-check.
10. **Offer a design playback when useful.** For broad products or when
    misunderstanding is plausible, explain the complete product in readable
    terms: scope and phases, capabilities, key flows, permissions or autonomy,
    data behavior, architecture, limitations, and exceptions. Capture user
    corrections as a new revision before approval.
11. **Present the approval gate.** Summarize the proposed design, evidence,
    rejected alternatives, risks, open user decisions, review findings, and
    readiness result. Ask the user to approve consequential product and
    architecture decisions. Implementation and PR merge require their own
    authorization. Never convert an autonomous recommendation or polished
    specification into user approval.

## Decision and readiness states

Track each material choice as one of:

- **Proposed** — evidence-backed recommendation that awaits user approval
  where approval is required.
- **User-approved** — explicitly approved by the user, with its scope and
  source recorded.
- **Unresolved** — evidence is insufficient or a user-dependent choice is
  still open.

Call the specification **implementation-ready** only when important product
and architecture decisions are resolved, required approvals are recorded,
behavior and acceptance criteria are testable, and readiness review finds no
blocking guesswork. Otherwise label it **DRAFT**, state the blockers and next
decision, and do not hand it off as ready. Reversible implementation details
may remain flexible when they do not change product behavior or architecture.

## Design Package

Produce only the artifacts useful for the actual design. Collectively, the
package should contain:

- a product specification with problem, goals, non-goals, scope, observable
  behavior, critical flows, acceptance criteria, and verification;
- architecture choices, responsibilities, important contracts, constraints,
  quality-attribute tradeoffs, and supporting evidence;
- a traceable decision record with options, evidence, rationale, rejected
  choices, dissent, open questions, and approval state;
- relevant risk and validation findings, prototype observations, reviewer
  dispositions, and readiness blockers.

Keep source-of-truth hierarchy and project-specific terminology intact. Link
to analyses and evidence instead of copying long records. Do not require a
particular document layout.

## Stopping conditions

Stop or return a clearly marked draft when critical blockers are resolved or
dispositioned and further analysis has diminishing value; when the remaining
choice belongs to the user; or when available time, evidence, or runtime
capability is exhausted. Declare practical resource limits when known. Report
which phases ran, what was skipped and why, what was actually reviewed or
tested, unresolved risks, and the next approval or discovery step. Do not
claim evaluation or decision-quality improvement without empirical evidence.

## Completion

The Design Package is coherent and traceable; proposed, user-approved, and
unresolved decisions are distinguishable; important flows, contracts, and
risks are documented; the spec has an honest readiness state; and the user
knows what remains before implementation.
