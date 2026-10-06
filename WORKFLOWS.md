# Workflows

Scenario-based guide for using `ai-setup`.

These are recommended routes, not mandatory pipelines.

Use only the steps that provide value for the current task.

## Router

Only have an idea?
→ Idea discovery

Know what to build but have not started?
→ New project

Already have a project?
→ Existing project adoption

Project already uses ai-setup?
→ Project audit

Working on one feature?
→ Feature workflow

Working on several issues?
→ Batch workflow

Found a bug?
→ Debug workflow

Need better tests?
→ Testing workflow

Need new AI configuration?
→ AI config workflow

## Only an idea

Use when the idea is still abstract and product or technical decisions are unresolved.

Example:

"Build an e-commerce site."

Flow:

project-base
→ ai-config-builder bootstrap
→ grill-me
→ clarify product and constraints
→ to-spec
→ make technical decisions
→ ai-config-builder adopt

Do not select stack-specific configuration before decisions justify it.

Avoid choosing databases, frameworks, deployment platforms, or specialized agents merely because they may become useful later.

## Product defined, project not started

Use when the desired product is clear but implementation has not begun.

Flow:

project-base or a specialized Project Instruction
→ grill-me for remaining ambiguity
→ to-spec
→ spec-reviewer
→ technical direction
→ ai-config-builder adopt
→ to-issues
→ implementation

## Existing project adoption

Use for repositories such as CappyCode or CappyHub.

Give the AI:

- the project;
- `README.md`;
- this file;
- existing project instructions.

Ask it to inspect the project and classify reusable configuration as:

- ADD;
- KEEP EXISTING;
- REPLACE;
- SKIP.

Do not copy everything.

Project-specific product behavior and architecture take priority.

Copy canonical files rather than recreating them from README descriptions.

## Existing project maintenance

Use:

`project-audit`

Review current configuration for:

- drift;
- duplication;
- stale instructions;
- missing configuration;
- project behavior that should remain local;
- reusable improvements that should move to ai-setup.

Approve changes before applying them.

## New ChatGPT or Claude Project

If a matching preset exists, start from it.

Available presets include:

- resume-reviews;
- learning-coach;
- interview-prep;
- software-engineering-project;
- course-companion.

If no preset fits:

start from `project-base`.

Customize the preset using actual project context.

Do not blindly append it to existing instructions.

Merge and remove duplication.

For ChatGPT Project Instructions, keep the final customized instructions under the platform limit.

## Feature is still unclear

Flow:

grill-me
→ to-spec
→ spec-reviewer
→ to-issues

Skip steps when the requirement is already sufficiently defined.

## Feature already has an approved spec

Flow:

spec-reviewer
→ to-issues
→ implement-issue
→ test-engineer when useful
→ verify-change
→ review-pr

## One approved issue

Flow:

implement-issue
→ test-engineer when behavior needs protection
→ verify-change
→ review-pr

## Several related issues

Flow:

issue-batch-orchestrator
→ execution waves
→ batch-orchestrator
→ implementers
→ test-engineer where valuable
→ independent review
→ merge gates

Optimize for maximum safe parallelism.

Dependent work starts after prerequisites merge.

## Bug

Flow:

debug-with-evidence
→ identify root cause
→ add a regression test when valuable
→ smallest correct fix
→ verify-change

Do not change several unrelated things until the bug disappears.

## Testing

Use `test-engineer` when test quality or missing protection is the problem.

Prioritize:

- business rules;
- invariants;
- critical flows;
- security boundaries;
- data integrity;
- important regressions.

Use coverage as diagnostic evidence, not a goal.

Use property-based testing when meaningful invariants exist.

Use mutation testing selectively when it helps evaluate whether important tests actually detect faults.

Then use `verify-change` for final execution and reporting.

## Need new AI configuration

Use:

`ai-config-builder`

Flow:

inspect existing catalog
→ CREATE / EXTEND EXISTING / DON'T CREATE
→ choose artifact type
→ define responsibility and boundaries
→ create compact configuration
→ registry status: testing
→ test on a real task

Artifact types:

- skill;
- agent;
- rule;
- template;
- Project Instruction.

## Workflow improvement

After meaningful use:

retro
→ identify what worked or failed
→ project-specific lesson?
   → keep it in the project
→ reusable lesson?
   → consider improving ai-setup

Testing a workflow does not make it accepted or default.

## Durable decision

When a technical or product decision should remain understandable later, use:

`templates/DECISION.md`

Do not create decision records for trivial choices.

## Core principle

Start from the project's actual state.

Do not install configuration merely because it exists.

Use the minimum reusable configuration that materially improves the workflow.
