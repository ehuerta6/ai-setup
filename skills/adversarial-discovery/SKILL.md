---
name: adversarial-discovery
description: Orchestrate evidence-backed, independent analysis and review for consequential decisions with meaningful uncertainty or competing options.
---

# Adversarial discovery

Use this workflow when uncertainty, competing options, cross-cutting constraints, or decision impact make independent analysis useful. Route simple requirements and settled decisions through the ordinary workflow, including `grill-me` when clarification is still needed.

## Process

1. **Freeze the scope.** Clarify the decision and questions, confirmed constraints, source baseline, current draft-spec revision (or state that none exists), and time/token/agent budget. Use `grill-me` for unresolved questions; record the resulting question set before analysis.
2. **Choose a feasible analysis count.** Use about 1 analysis for modest uncertainty, 3 for meaningful uncertainty, or up to 5 for complex/high-impact work. These are heuristics, not quotas. Adapt to actual runtime, isolation, concurrency, and resource limits. Record the requested and actual counts and why they differ. Never claim an unavailable or unexecuted agent ran.
3. **Collect independent first passes.** Give each actual analyst the same frozen questions and source baseline. Assign complementary lenses only where useful. Keep initial outputs private from other analysts until submitted; if the runtime cannot provide that isolation, record the limitation.
4. **Synthesize from evidence.** For each question, compare options, evidence quality, agreements, dissent, counterevidence, tradeoffs, correlated assumptions or sources, and unresolved uncertainty. Agreement counts describe convergence; they do not establish correctness. Use `research-and-compare` when external evidence comparison is needed.
5. **Update one draft.** The coordinator is the sole writer to shared specs and decision indexes. Preserve the evaluated revision, link each proposed decision to evidence and affected requirements, distinguish findings from inference, and mark every unapproved decision **Proposed**. This workflow does not turn proposals into approved inputs for `to-spec`; use `to-spec` only after the user resolves the relevant decisions.
6. **Challenge the revised draft.** When available, use `spec-reviewer` in a fresh context to inspect the exact revision for contradictions, unsupported claims, missing requirements, security/data risks, and unverifiable acceptance criteria. Record its isolation limits and exact reviewed revision. Treat review findings as evidence to disposition, not automatic approval.
7. **Iterate selectively.** Address material findings with targeted analysis or edits, then review the resulting revision when needed. Stop when critical/high findings are resolved or explicitly dispositioned, further analysis has diminishing value, a user decision is required, or the budget is exhausted. Report what remains open; do not require a fixed number of rounds.
8. **Hold the human gate.** The user explicitly approves decisions and specifications before implementation, and authorizes implementation and merges separately. Never automatically approve requirements, architecture, implementation, issues, or merges.

## Portable record

Keep a compact Markdown record in the consuming project's repository, adapting paths and fields to local conventions. Include:

- **Baseline:** questions and stable IDs; options; constraints; source references/revisions; draft-spec revision or hash; budget; requested and actual analyst counts.
- **Analysis records:** one per execution that actually occurred, with analyst/lens, baseline revision, evidence and source revisions, findings, and isolation limits.
- **Synthesis:** evidence-backed agreements, dissent, correlated assumptions, counterevidence, tradeoffs, unresolved choices, and **Proposed** decisions.
- **Spec changes:** requirement links, changed revision/hash, single-writer identity, and explicit approval status.
- **Review:** reviewer context/isolation, exact revision/hash reviewed, findings with severity, disposition, and follow-up revision/review link.
- **Next step:** user choices, approval state, and the reason analysis stopped.

Preserve the trace `Question → Options → Evidence → Proposed Decision → Requirement → Review Result`. Link to source records rather than copying full analysis histories. Do not require a particular project directory layout.

## Completion

The record distinguishes actual executions from plans, traces claims to evidence and revisions, preserves meaningful disagreement and uncertainty, identifies proposed versus user-approved decisions, and states the review result and next approval gate. This workflow supports traceability; it does not by itself demonstrate better decision quality.
