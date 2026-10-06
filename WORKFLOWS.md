# Workflows

Scenario-based guide for using `ai-setup`.

These are recommended routes, not mandatory pipelines.

Use the smallest workflow that fits the current task.

## Router

Only have an idea?
→ Idea discovery

Know what to build but have not started?
→ New project

Have an empty repo that needs minimal AI configuration?
→ Bootstrap

Already have a defined or existing project?
→ Project adoption

Project already uses AI configuration?
→ Project audit

Working from a spec?
→ Spec workflow

Working from one issue?
→ Issue workflow

Working on several related issues?
→ Batch workflow

Found a bug?
→ Debug workflow

Need better tests?
→ Testing workflow

Need independent review?
→ Review workflow

Need Git or GitHub delivery?
→ GitHub workflow

Starting a ChatGPT or Claude Project?
→ AI workspace workflow

Moving work to another chat or agent?
→ Handoff

Need new reusable AI configuration?
→ AI config workflow

Want to improve the workflow itself?
→ Retro


## Only an idea

Use when the product or technical direction is still unclear.

Flow:

grill-me
→ to-spec
→ ai-config-builder adopt when the project is defined
→ to-issues when implementation is ready

Do not select stack-specific configuration before decisions justify it.


## Product defined, project not started

Use when the desired product is understood but implementation has not begun.

Flow:

grill-me when meaningful ambiguity remains
→ to-spec
→ spec-reviewer when useful
→ ai-config-builder adopt
→ to-issues


## Empty repo needs minimal AI setup

Use when the project or repository is new and needs only enough AI configuration to start working safely.

Flow:

ai-config-builder bootstrap

Bootstrap should recommend only the minimum useful starting configuration.

Do not use Bootstrap to discover what product should be built.


## Existing project adoption

Use when the project already has meaningful product, architecture, or code context.

Flow:

ai-config-builder adopt

Classify relevant reusable configuration as:

- ADD
- KEEP EXISTING
- REPLACE
- SKIP

Project-specific behavior and architecture take priority over reusable defaults.


## Existing project maintenance

Use when a project already has AI configuration and it may have drifted.

Flow:

project-audit

Audit for:

- stale configuration;
- duplication;
- conflicts;
- missing reusable configuration;
- reusable behavior that belongs in ai-setup.


## New ChatGPT or Claude Project

Use a specialized Project Instruction preset when one clearly fits.

Available presets include:

- resume-reviews;
- learning-coach;
- interview-prep;
- software-engineering-project;
- course-companion.

If no specialized preset fits, start from:

project-base

Then:

preset or project-base
→ tune using current sources, context, and handoff when available
→ remove irrelevant generic behavior
→ produce final Project Instructions

Do not blindly paste the reusable preset as the final instructions.


## Feature is still unclear

Flow:

grill-me
→ to-spec
→ spec-reviewer when useful
→ to-issues


## Feature already has an approved spec

Flow:

spec-reviewer when useful
→ to-issues
→ implement-issue


## One approved issue

Flow:

implement-issue
→ pr-reviewer when independent review is useful

`implement-issue` already handles implementation, appropriate tests, verification, and delivery preparation.


## Several related issues

Flow:

issue-batch-orchestrator
→ batch-orchestrator

The planning skill determines dependencies, waves, and gates.

The agent executes the approved plan and coordinates implementation and independent review.


## Bug

Flow:

debug-with-evidence
→ pr-reviewer when independent review is useful

`debug-with-evidence` owns reproduction, diagnosis, root-cause fixing, regression protection, and verification.


## Testing

Use when test quality or missing protection is the problem.

Flow:

test-engineer
→ verify-change

Prioritize meaningful fault detection over test count or arbitrary coverage targets.

Use property-based or mutation testing only when they provide useful signal.


## Independent review

Use when separating implementation and review context improves confidence.

Flow:

pr-reviewer

The PR reviewer uses `review-pr` to evaluate both:

- requirements;
- engineering quality.


## Git and GitHub delivery

Use when the main task is branch, commit, PR, or merge workflow.

Flow:

github-flow

Project-specific Git rules override reusable defaults.


## Continue work elsewhere

Use when transferring unfinished work to another chat, session, or agent.

Flow:

handoff

Prefer pointers to canonical artifacts instead of duplicating their full contents.


## Need new AI configuration

Use:

ai-config-builder build

Flow:

inspect existing configuration
→ CREATE / EXTEND EXISTING / DON'T CREATE
→ create compact configuration
→ registry status: testing
→ test on a real task

Possible artifact types:

- skill;
- agent;
- rule;
- template;
- Project Instruction.


## Workflow improvement

After meaningful real-world usage:

retro

Use evidence from actual work to decide whether something should:

- stay project-specific;
- change in ai-setup;
- become automated;
- remain unchanged.

Testing a workflow does not make it accepted or default.


## Durable decision

When a technical or product decision should remain understandable later, use:

templates/DECISION.md

Do not create decision records for trivial choices.


## Core principle

WORKFLOWS chooses the right tool.

Skills define procedures.

Agents isolate responsibilities.

Rules define stable constraints.

Project Instructions define long-running workspace behavior.

Templates define reusable artifact shapes.

Do not repeat a skill's internal procedure here.

Use the minimum reusable configuration that materially improves the work.
