---
name: ai-config-builder
description: Design or evolve reusable AI configuration such as skills, agents, rules, templates, and project instructions without creating unnecessary duplication.
---

# AI config builder

Use this skill when creating or changing reusable AI configuration.

## First decide what is needed

Inspect:
- `README.md`;
- related existing configuration;
- the target project's context.

Choose one:

- CREATE
- EXTEND EXISTING
- DON'T CREATE

Do not create a new artifact when an existing one already owns the responsibility.

## Identify the artifact type

Choose:

- Skill — procedure for a specific task.
- Agent — specialized role or isolated responsibility.
- Rule — stable constraint.
- Template — reusable artifact structure.
- Project Instruction — long-lived behavior for a multi-chat project.

## Discovery

Ask only the questions needed to define:

- purpose;
- trigger or use case;
- required context;
- expected behavior;
- boundaries;
- output;
- completion criteria;
- tools or related skills;
- how it will be tested.

For agents also determine:

- what responsibility is isolated;
- what the agent may modify;
- what requires approval;
- when it must stop;
- what it reports back.

## Writing

Keep configuration compact.

Prefer:
- clear responsibilities;
- behavior over explanation;
- references to canonical sources;
- progressive disclosure.

Avoid:
- duplicated rules;
- giant instruction files;
- speculative capabilities;
- implementation details that belong in project code;
- copying documentation into prompts.

Use `writing-for-agents` when useful.

## Adoption

New configuration starts as `testing`.

Do not mark it accepted or default without explicit user confirmation and real usage evidence.

## Return

Provide:

- recommendation: CREATE / EXTEND EXISTING / DON'T CREATE;
- artifact type and name;
- overlap with existing configuration;
- proposed file location;
- finished content when creation is approved;
- one realistic test scenario.
