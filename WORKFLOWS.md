# Workflows

Scenario-based guide for using `ai-setup`.

These routes are suggestions, not a required sequence. Use only the steps that help with the task. For a single reusable workflow, load its skill; for durable multi-chat context, start from a Project Instruction preset.

## Router

| If you're... | Go to |
| --- | --- |
| Starting with an idea | [Only an idea](#only-an-idea) |
| Planning a product that has not started | [Product defined, project not started](#product-defined-project-not-started) |
| Setting up AI in an empty repo | [Empty repo needs minimal AI setup](#empty-repo-needs-minimal-ai-setup) |
| Adopting configuration into an existing project | [Existing project adoption](#existing-project-adoption) |
| Reviewing configuration that's already in use | [Existing project maintenance](#existing-project-maintenance) |
| Creating a multi-chat workspace | [New ChatGPT or Claude Project](#new-chatgpt-or-claude-project) |
| Researching or comparing options | [Research and comparison](#research-and-comparison) |
| Clarifying a feature | [Feature is still unclear](#feature-is-still-unclear) |
| Working from an approved spec | [Feature already has an approved spec](#feature-already-has-an-approved-spec) |
| Implementing one issue | [One approved issue](#one-approved-issue) |
| Coordinating related issues | [Several related issues](#several-related-issues) |
| Debugging a bug | [Bug](#bug) |
| Improving tests | [Testing](#testing) |
| Getting an independent review | [Independent review](#independent-review) |
| Preparing a commit, PR, or merge | [Git and GitHub delivery](#git-and-github-delivery) |
| Handing work to another chat or agent | [Continue work elsewhere](#continue-work-elsewhere) |
| Creating reusable AI configuration | [Need new AI configuration](#need-new-ai-configuration) |
| Improving an existing workflow | [Workflow improvement](#workflow-improvement) |

## Only an idea

Use when the product or technical direction is still unclear.

Flow:

grill-me
→ optionally prototype for an unresolved concrete design question
→ to-spec
→ ai-config-builder adopt when the project is defined
→ to-issues when implementation is ready

Do not select stack-specific configuration before decisions justify it.


## Product defined, project not started

Use when the desired product is understood but implementation has not begun.

Flow:

grill-me when meaningful ambiguity remains
→ optionally prototype for an unresolved concrete design question
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

Before changing the project, present the proposed files and classify each as ADD, KEEP EXISTING, REPLACE, or SKIP.

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


## Research and comparison

Use `research-and-compare` when a decision depends on external evidence or a structured comparison. For a continuing multi-chat research effort, start with `project-instructions/research-workspace.md` and adapt it to the project's sources and question.


## Feature is still unclear

Use `grill-me` to resolve product and technical questions before writing a spec. If a concrete uncertainty is easier to test than discuss, use `prototype` to compare isolated UI or logic alternatives. Skip it when discussion resolves the question. Prototypes are temporary and do not automatically become production code.

Flow:

grill-me
→ optionally prototype for an unresolved concrete design question
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
