# Context

Rules for deciding what information is authoritative and what context an agent should load.

## Sources of truth

Explicit user decisions have the highest authority.

After that, follow the project's own documented source-of-truth hierarchy.

When a project does not define one, prefer:

1. latest explicit user or project decision;
2. project-specific instructions;
3. approved specs, designs, and decision records;
4. the active GitHub Issue and its accepted clarifications;
5. global rules from SetupSmith;
6. applicable skills;
7. existing code patterns as implementation evidence.

Existing code shows current behavior. It does not automatically define product requirements.

## Conflicts

When sources disagree:

- prefer the most recent explicit decision;
- do not silently reconcile incompatible requirements;
- surface material conflicts before implementation;
- do not let a global convention override an intentional project-specific decision.

## Missing information

Do not invent requirements.

Before asking the user:

- inspect the repository;
- read available project documentation;
- inspect linked issues or specs;
- use available tools to discover factual information.

Ask only when the missing information is a decision the user must make or cannot be reliably discovered.

## Context loading

Load the minimum context needed for the task.

Prefer pointers to canonical sources over copying their contents into multiple files.

Separate:

- stable global rules;
- project-specific context;
- task-specific temporary notes.

## Memory and prior work

Do not assume an old decision is still current when newer project context contradicts it.

Distinguish:

- information read from current sources;
- previously known context;
- new decisions made during the current task.

## Experimental workflows

Testing a tool, skill, agent, or workflow does not make it a default.

Use these states when tracking adoption:

- `testing`
- `accepted`
- `rejected`
- `default`
- `replaced`

Only the user promotes a workflow into normal use.
