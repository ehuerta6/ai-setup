---
name: ai-config-builder
description: Design or evolve reusable AI configuration such as skills, agents, rules, templates, and project instructions without creating unnecessary duplication.
---

# AI config builder

Use this skill when creating or changing reusable AI configuration.

## Modes

Choose the mode that matches the project's current state.

### Bootstrap

Use when a new or empty project needs the minimum AI configuration required to begin working safely.

Select only immediately useful configuration.

Do not use Bootstrap to discover the product itself. Use `grill-me` when product or technical decisions are unresolved.

Do not recommend stack-specific or workflow-specific configuration before decisions justify it.

### Adopt

Use when the project is defined or already exists.

Inspect the actual project and classify relevant configuration as:

- ADD
- KEEP EXISTING
- REPLACE
- SKIP

Project-specific behavior takes priority over reusable defaults.

### Build

Use when creating or extending a skill, agent, rule, template, or Project Instruction.

Inspect:

- `README.md`;
- related existing configuration;
- the target project's context.

Then choose:

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

Match the output to the selected mode.

### Bootstrap

Provide:

- minimum starting configuration;
- why each item is needed now;
- decisions intentionally deferred until the project is clearer;
- next discovery step.

### Adopt

For each relevant item provide:

- ADD / KEEP EXISTING / REPLACE / SKIP;
- why it applies;
- overlap with existing project behavior;
- where it should live.

### Build

Provide:

- CREATE / EXTEND EXISTING / DON'T CREATE;
- artifact type and name;
- overlap with existing configuration;
- proposed file location;
- finished content when creation is approved;
- one realistic test scenario.
