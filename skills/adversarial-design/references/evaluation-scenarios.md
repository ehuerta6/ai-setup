# Adversarial design evaluation scenarios

These hand-authored prompts are fixtures for future manual evaluation. They
have not been run. Check the observable behavior in an actual run; fixture
presence and catalog validation do not establish design quality or improved
decision quality.

## Complex product from an initial idea

**Prompt:** Design a local-first collaboration app from this short idea. Find
the missing requirements, compare existing solutions, model the important
flows and failure behavior, resolve consequential architecture questions,
and prepare a specification for approval.

**Look for:** project grounding; a dependency-ordered decision graph; relevant
research; explicit architecture tradeoffs; user journeys, states, permissions,
contracts, invariants, failures, and recovery; risk-based validation; spec
review; a fresh implementer readiness simulation when isolation is available;
and an honest approval and readiness state.

## Respect accepted architecture

**Prompt:** Design a major feature in an existing project with accepted
architecture and explicit source-of-truth instructions. A new technology is
popular but not required by the feature.

**Look for:** preservation of accepted decisions, no unnecessary technology
change, and any proposed exception tied to evidence and approval.

## Decision dependency ordering

**Prompt:** The design has unresolved identity, data ownership, offline merge,
and screen detail decisions. Some depend on others.

**Look for:** a dependency graph that resolves foundational choices before
downstream behavior and avoids premature design.

## Architecture tradeoff evaluation

**Prompt:** Compare two viable architectures against this product's real
consistency, deployment, security, maintenance, and cost scenarios.

**Look for:** scenario-based tradeoffs with evidence and explicit compromises,
not popularity or generic rankings.

## Critical flows, security, and data integrity

**Prompt:** Model account creation, shared-resource access, concurrent edits,
permission revocation, partial failure, backup, and recovery for a sensitive
data product.

**Look for:** actors, permissions, state transitions, invariants, data
contracts, trust boundaries, failure and recovery behavior, and unresolved
risks that block readiness.

## Disposable prototype

**Prompt:** Two interaction models may prevent destructive edits differently,
and repository evidence does not resolve the usability question. Run a
disposable comparison.

**Look for:** an explicit question, meaningful alternatives, isolation from
production data and services, limited observations, and correct removal or
retention only with explicit user direction.

## Implementation readiness failure

**Prompt:** Review this draft as a fresh implementer. One requirement does not
define behavior when a user's access is revoked during an edit.

**Look for:** a concrete blocking question tied to its requirement; the spec
stays DRAFT and is not called implementation-ready.

## User-dependent unresolved decision

**Prompt:** A product needs to choose between public-by-default sharing and
invite-only sharing. Evidence cannot establish the intended policy. Prepare
the design and wait for the product owner's decision.

**Look for:** the choice remains Unresolved or Proposed, the tradeoff is
explained, and no approval is inferred.

## Simple task bypass

**Prompt:** Add one clearly specified optional field using the project's
accepted architecture and existing validation behavior.

**Look for:** routing to ordinary `to-spec` or implementation workflow
without full design orchestration.

## Evaluation limits

Record scenarios attempted, runtime capabilities, and actual observations.
Do not claim the skill improves design quality without a comparable empirical
evaluation.
