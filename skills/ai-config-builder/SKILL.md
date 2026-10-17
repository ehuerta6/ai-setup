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

Do not use Bootstrap to discover the product itself. Use `product-grill` for unresolved product requirements when the user should not have to choose technical internals; use `grill-me` when product and technical decisions are both in scope for a user who is comfortable resolving them.

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

### Create a ChatGPT or Claude Project

Use when setting up a long-running workspace with multiple related chats. This is a Project Instruction task, not a request to copy a whole preset unchanged.

1. Select the closest existing preset from `README.md` and `WORKFLOWS.md`; use `project-base` only when no specialized preset fits.
2. Identify the project's purpose, scope, audience, and sources of truth from supplied files and explicit decisions. Record missing context rather than filling gaps.
3. Separate durable workspace behavior from reference documents. Keep instructions focused on how chats should work; keep detailed facts, research, and evolving project material in referenced files.
4. Preserve decisions and rationale in a durable project source so they carry across chats. Distinguish decisions from findings, hypotheses, and open questions.
5. Remove generic preset instructions that do not apply. Avoid repeating context already present in project files or another authoritative instruction.
6. Add only project-specific customization needed to resolve actual requirements or constraints. Keep project-specific behavior authoritative over reusable defaults.
7. Return concise final Project Instructions, the chosen preset, the sources used, and any unresolved questions.

## Identify the artifact type

Choose:

- Skill — procedure for a specific task.
- Agent — specialized role or isolated responsibility.
- Rule — stable constraint.
- Template — reusable artifact structure.
- Project Instruction — long-lived behavior for a multi-chat project.

## Skills-first distribution

`ai-setup` remains the canonical vault for reusable skills, agents, rules, templates, and project instructions. Prefer updating a **relevant installable skill** when knowledge from another artifact should change how agents perform a task.

- Keep canonical rules, templates, and agents in their own files; do not delete or reclassify them for CLI convenience.
- Embed only the essential, task-relevant constraints, precedence, safety boundaries, and completion criteria into the corresponding skill so a globally installed copy can operate without a checkout of `ai-setup`.
- Treat a skill as standalone: test the instruction path when sibling skills, rules, agents, or templates are inaccessible; provide a fallback or state the dependency honestly.
- Preserve project-specific context in its own repository. Do not transfer secrets, credentials, or domain decisions into global skills.
- Prefer extending an existing skill to creating another skill with an overlapping trigger. Create a new skill only for a distinct repeatable workflow.
- Avoid copying complete rules or templates into every skill. The canonical file stays authoritative for maintenance, while a concise operational subset travels with the skill. Keep those subsets consistent when the canonical behavior changes.
- Agents remain isolated roles, not disguised skills; project instructions and templates retain their own purposes. `npx skills` distributes skills, not these other artifact types.

This is a packaging priority, not a requirement to expand the catalog or rewrite every artifact.

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

Default new configuration to experimental until usage supports promotion, **unless the user explicitly directs immediate adoption**. Record explicit acceptance separately from execution or test evidence: adoption does not prove the configuration works. Do not infer acceptance from catalog presence.

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
