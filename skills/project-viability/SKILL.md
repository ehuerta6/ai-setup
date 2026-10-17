---
name: project-viability
description: Decide whether a software project idea solves a worthwhile real problem or should be validated, simplified, or skipped before product discovery.
---

# Project viability

Use when someone has a software project idea but is uncertain whether building it is worthwhile. This applies to personal problems, friends, schools, clubs, communities, open source, internal tools, and businesses. Assess the value of solving the problem, **not** revenue potential unless revenue matters to the user.

This skill owns one decision: **build, validate first, or don't build**. It does not elicit complete requirements, select architecture, write specifications, or orchestrate agents. It is optional, not a mandatory gate for every project.

## Process

1. **Ground the idea.** State the problem, who experiences it, their current workaround, how often it occurs, the consequence of leaving it unsolved, and the desired improvement. Inspect supplied project context first. Mark missing information as unknown, not fact.
2. **Compare against not building.** Consider doing nothing, changing the process, using existing tools, configuring an integration, writing a small script, or extending existing software. Compare the likely benefit, setup cost, ongoing maintenance, and friction introduced. Prefer the smallest effective solution.
3. **Challenge through three lenses**, using the same factual baseline:
   - **Advocate:** strongest concrete case that solving the problem will help a real user.
   - **Skeptic:** reasons the pain may be overstated, adoption may fail, or the proposed software may be unnecessary.
   - **Pragmatist:** opportunity cost, effort, maintenance, alternatives, and the smallest useful scope.
   Do not assign these perspectives automatic authority. Synthesize their claims as a **judge**, weighing evidence rather than voting or requiring consensus.
4. **Separate evidence from assumptions.** Distinguish observed usage, firsthand reports, and verified alternatives from hypotheses. Identify the highest-impact unknown and, if necessary, the cheapest way to resolve it (for example, observe a real workflow or try a manual workaround). Do not fabricate interviews, user counts, savings, prices, or agent executions. Research existing solutions only when doing so would change the recommendation.
5. **Give one recommendation:**
   - **BUILD:** there is sufficient reason to proceed; state the smallest useful starting scope.
   - **VALIDATE FIRST:** a material unknown could overturn the decision; state a concrete check and what result would change the recommendation.
   - **DON'T BUILD:** the need is weak or a simpler alternative is sufficient; name that alternative.
   State material dissent and uncertainty. The user makes the final decision.

## Output

Keep the review proportional to the decision. Normally include:

- **Problem and users:** the observed pain and present workaround, distinguishing unknowns.
- **Strongest case for / against:** concise advocate, skeptic, and pragmatist findings.
- **Alternatives:** the best non-build or smaller-build option.
- **Verdict and next action:** BUILD, VALIDATE FIRST, or DON'T BUILD, with reasons and one concrete next step.

## Boundaries

- **Before discovery:** if building is worthwhile and the user agrees, hand off the problem and open product questions to `product-grill` or `grill-me`. Do not perform their requirement-discovery work here. Do not create a spec, issues, code, or a repository without a separate request.
- **Before complex debate:** when a high-impact decision genuinely warrants independent analysis, `adversarial-discovery` owns actual multi-agent execution and debate. These three lenses alone are not independent agents; never describe them as such without real isolation.
- **Against false economics:** evaluate practical usefulness, time and friction saved, reliability, and user goals. Financial return is only one possible criterion.
- **Against process overhead:** keep low-stakes ideas lightweight. Do not force this review onto already-approved or clearly scoped implementation tasks.

## Completion

The user can choose whether to build, cheaply validate a decisive unknown, or use a simpler solution, with evidence and uncertainty visible and without prematurely designing the product.
