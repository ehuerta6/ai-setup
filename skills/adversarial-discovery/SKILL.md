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
4. **Select debate deliberately.** Compare the independent submissions for material disagreement, consequential tradeoffs, unsupported assumptions, and possibly correlated errors. Debate only when it could change a decision, expose a meaningful risk, or improve the evidence. Skip it when the answer is straightforward and adequately supported. Agreement alone is not a reason to debate or evidence that a claim is correct.
5. **Run a structured challenge and rebuttal.** After initial submissions are frozen, give participants concise summaries of the other positions and their supporting evidence. Ask each participant to identify specific objections, counterevidence, assumptions, and falsification conditions: what evidence or condition would change its position? Participants answer substantive challenges and may maintain, qualify, retract, or change their positions. Add at most one targeted follow-up exchange when new evidence or a consequential objection warrants it; stop earlier when exchanges add no useful information. Challenge claims and reasoning, not people.
6. **Synthesize from evidence.** The coordinator compares verified evidence, its quality and provenance, assumptions, feasibility, tradeoffs, counterarguments, correlated sources, position changes, dissent, and remaining uncertainty. Do not decide by vote, agent count, confidence rhetoric, or consensus. Preserve a well-supported minority objection even when most participants disagree. Use `research-and-compare` when external evidence comparison is needed.
7. **Update one draft.** The coordinator is the sole writer to shared specs and decision indexes. Preserve the evaluated revision and link each proposed decision to evidence and affected requirements. Distinguish findings from inference, include why material alternatives did not prevail, retain unresolved objections, and mark every unapproved decision **Proposed**. This workflow does not turn proposals into approved inputs for `to-spec`; use `to-spec` only after the user resolves the relevant decisions.
8. **Review when useful.** When a specification or requirement set is affected and review would add value, use `spec-reviewer` in a fresh context to inspect the exact revision for contradictions, unsupported claims, missing requirements, security/data risks, and unverifiable acceptance criteria. Record its isolation limits and exact reviewed revision. Treat review findings as evidence to disposition, not automatic approval.
9. **Stop within the declared budget.** Before analysis, set practical limits for participating analysts, debate exchanges, research, and time or tokens when the runtime exposes them. Adapt to actual runtime and report the limits and what ran. Stop when challenges are answered or no longer productive, additional work has diminishing value, a user decision is required, or the budget is reached. Report what remains open.
10. **Hold the human gate.** The user explicitly approves decisions and specifications before implementation, and authorizes implementation and merges separately. Never automatically approve requirements, architecture, implementation, issues, or merges.

## Portable record

Keep a compact Markdown record in the consuming project's repository, adapting paths and fields to local conventions. Include:

- **Baseline:** questions and stable IDs; options; constraints; source references/revisions; draft-spec revision or hash; budget; requested and actual analyst counts.
- **Analysis records:** one per execution that actually occurred, with analyst/lens, baseline revision, evidence and source revisions, findings, and isolation limits.
- **Debate:** for each material decision, initial options, concise challenge and rebuttal summaries, evidence and source revisions, falsification conditions, position changes, deciding reasons, rejected alternatives, minority objections, unresolved disagreement, and approval state. Link to the actual analysis records; do not reproduce full transcripts or private chain-of-thought.
- **Synthesis:** evidence-backed agreements, dissent, correlated assumptions, counterevidence, tradeoffs, unresolved choices, and **Proposed** decisions.
- **Spec changes:** requirement links, changed revision/hash, single-writer identity, and explicit approval status.
- **Review:** reviewer context/isolation, exact revision/hash reviewed, findings with severity, disposition, and follow-up revision/review link.
- **Next step:** user choices, approval state, and the reason analysis stopped.

Preserve the trace `Question → Initial Options → Evidence → Challenge → Rebuttal or Position Change → Proposed Decision → Requirement → Review Result → Human Approval`. Link to source records rather than copying full analysis histories. Do not require a particular project directory layout.

## Debate limits

- Do not fabricate agents, independent isolation, debates, research, or experimental outcomes. Use only capabilities the runtime actually provides. If genuine inter-agent exchange is unavailable, say so and synthesize the actual independent submissions without simulating a debate.
- Do not require debate, an agent count, parallel execution, or a fixed number of rounds. Resource heuristics in this skill guide planning; they are not quotas.
- Keep records to concise argument summaries and evidence. Do not request or store private chain-of-thought.
- Preserve the distinction between proposed and user-approved decisions even when every participant agrees.

## Completion

The record distinguishes actual executions from plans, traces claims and position changes to evidence and revisions, preserves meaningful disagreement and uncertainty, identifies proposed versus user-approved decisions, and states the review result and next approval gate. This workflow supports traceability; it does not by itself demonstrate better decision quality.
