# How to use AI Setup

This file is the operational guide for using `ai-setup`.

`README.md` tells you what exists.

`HOW_TO_USE.md` tells you how to apply it safely.

## Core principle

Do not start by copying configuration.

Start by giving the AI the catalog and asking what the target project actually needs.

Reusable configuration should be selected intentionally, not installed everywhere by default.

## What each part is for

| Type | Purpose |
| --- | --- |
| `project-instructions/` | Defines how an entire multi-chat AI Project should behave |
| `rules/` | Stable constraints that should consistently hold |
| `skills/` | Procedures for performing a specific task |
| `agents/` | Specialized roles for isolated or focused work |
| `templates/` | Reusable structure for common artifacts |
| `registry.yaml` | Tracks whether something is testing, accepted, rejected, default, or replaced |

Project-specific product behavior, architecture, and decisions should remain in the target project.

## Add AI configuration to a coding project

Give the AI:

- the target repository;
- `ai-setup/README.md`;
- the project's existing AI instructions.

Then ask:

> Inspect this repository and compare its current AI instructions and workflow against the available configuration in `ai-setup/README.md`.
>
> Recommend only the skills, agents, rules, templates, and project instructions that would materially help this project.
>
> For each recommendation, tell me:
> - why it applies;
> - where it should live;
> - whether it overlaps with something already present;
> - whether to keep, add, replace, or skip it.
>
> Prefer existing project-specific instructions when they contain intentional product or architecture behavior.
>
> Do not modify anything until I approve the proposed set.

After approval:

1. Copy the exact canonical files from `ai-setup`.
2. Do not recreate files from README descriptions.
3. Adapt only what genuinely needs a project-specific override.
4. Avoid copying configuration that the project will not use.

## Create instructions for a ChatGPT or Claude Project

Choose the closest preset from `project-instructions/`.

Available starting points include:

- `resume-reviews.md`
- `learning-coach.md`
- `interview-prep.md`
- `software-engineering-project.md`
- `course-companion.md`

Give the preset and the actual project context to the AI.

Then ask:

> Use this Project Instructions preset as a base.
>
> Inspect the existing project context, sources, and instructions.
>
> Customize the preset for this specific project.
>
> Preserve useful reusable behavior, but replace generic assumptions with the project's real goals, source-of-truth rules, constraints, terminology, and workflows.
>
> Do not blindly append the preset to existing instructions. Merge them and remove duplication.
>
> Keep the final Project Instructions under 8,000 characters.

The preset is a starting point, not a file that must be copied unchanged.

## Software engineering projects

For a software project, start with:

`project-instructions/software-engineering-project.md`

Then specialize it with the project's real:

- product model;
- users;
- goals and non-goals;
- source-of-truth rules;
- architecture;
- technical constraints;
- Git workflow;
- terminology.

Different chats inside the same Project may then focus on different concerns such as:

- UI/UX;
- product decisions;
- database;
- Firebase or Supabase;
- brainstorming;
- research;
- GitHub Issues;
- implementation;
- debugging;
- review.

Each chat should use only the parts of the Project Instructions relevant to its current purpose.

## Using skills

Use a skill when the current task matches its responsibility.

Examples:

- unresolved feature decisions → `grill-me`
- decisions ready for specification → `to-spec`
- approved spec needs issues → `to-issues`
- implement one issue → `implement-issue`
- bug investigation → `debug-with-evidence`
- verify completed work → `verify-change`
- review a PR → `review-pr`
- coordinate several issues → `issue-batch-orchestrator`
- Firebase work → `firebase`
- UI/UX work → `impeccable`
- resume work → `resume-review`
- cross-chat continuation → `handoff`

Do not force a skill into a task just because it exists.

## Using agents

Use an agent when separating responsibility or context improves the result.

Examples:

- independent implementation review → `pr-reviewer`
- multi-issue execution → `batch-orchestrator`
- teaching during technical work → `mentor`
- Supabase/PostgreSQL database review → `supabase-database-reviewer`

Straightforward work does not need a specialized agent.

An implementer should not be the only reviewer of its own work when independent review matters.

## Using rules

Copy global rules only when they provide value to the target project.

Before copying one, compare it with existing project instructions.

Project-specific rules should win when intentional.

Avoid maintaining the same rule in several places.

## Using templates

Templates provide structure, not mandatory ceremony.

Use them when creating:

- specs;
- plans;
- GitHub Issues;
- pull requests;
- handoffs;
- issue batch plans.

Adapt the structure when the project already has a better established format.

## Project Instructions vs skills

Use Project Instructions for long-lived project behavior.

Use skills for specific procedures.

Example:

`software-engineering-project.md`

defines how a software Project behaves across many chats.

`to-issues`

defines how to perform one specific task inside that Project.

Do not duplicate the full skill procedure inside Project Instructions.

## Promoting something into ai-setup

When a workflow works well inside a project:

1. review the result;
2. use `retro` when useful;
3. decide whether the lesson is project-specific or reusable.

If project-specific:

keep it in the project.

If reusable:

consider extracting it into `ai-setup`.

Do not promote one-off project behavior into global configuration without evidence that it generalizes.

## Updating existing projects

When `ai-setup` changes, do not automatically synchronize every project.

Instead:

1. review the new or changed item;
2. decide whether the project benefits from it;
3. update that project when relevant.

Projects do not need to remain perfect mirrors of `ai-setup`.

## Adoption status

Check `registry.yaml` before treating something as an established workflow.

Possible states:

- `testing`
- `accepted`
- `rejected`
- `default`
- `replaced`

Presence in the repository does not imply adoption.
