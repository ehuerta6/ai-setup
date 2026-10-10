---
name: setup-ai
description: Analyze a repository's existing AI setup and recommend relevant SetupSmith configuration without changing project files.
---

# Setup AI

Guide **Analyze → Recommend** for the repository in the current working directory. This skill is read-only. Never install configuration, create a manifest, write a plan file, or edit project instructions. A recommendation is not approval or proof of adoption.

## 1. Establish evidence

Inspect the current repository selectively. Read applicable `AGENTS.md`, `CLAUDE.md`, and existing assistant instructions first. Then inspect relevant product/architecture documentation, technology manifests, repository workflows, and Git conventions. Use file names and existing instructions to select a few likely sources; do not dump or read the entire repository. If a source is absent, say so instead of inferring its contents. Project-specific decisions and instructions take priority over reusable defaults.

Look for existing AI setup in common native locations such as `.agents/skills/`, `.claude/skills/`, `.codex/`, `.cursor/`, `.github/`, and root instruction files. Report only locations that exist or are relevant to the clients the project uses. Do not treat a file name or folder alone as proof that a client loaded it.

## 2. Load canonical procedures when relevant

Use the canonical SetupSmith source `https://github.com/ehuerta6/setupsmith` to read `skills/ai-config-builder/SKILL.md` for bootstrap/adoption recommendations and `skills/audit-ai-config/SKILL.md` when existing AI configuration needs an audit. Do not reproduce these procedures from memory or duplicate them here.

Use only files from an immutable commit, never directly from a checkout's working tree. For an accessible checkout, verify that its Git remote identifies `https://github.com/ehuerta6/setupsmith`, record `git rev-parse HEAD`, and read the helper files with `git show <sha>:<path>` so uncommitted edits cannot alter the instructions. When source access is available, resolve the default branch using `git ls-remote --symref`; if the checkout is behind, fetch and read from the newly resolved commit. If remote freshness cannot be checked, report the exact commit SHA and say that its freshness is unverified; do not call its procedures current. If neither a verifiable canonical checkout nor a successful immutable source retrieval is available, do not use copied or remembered procedures.

For retrieval, fetch the resolved branch into a temporary directory, record the resulting commit SHA, and read only the needed files from that commit with `git show <sha>:<path>`. Do not run scripts or other files from the source. Remove temporary retrieval data when finished.

If canonical source access fails and no readable immutable commit is available, state which file(s) could not be retrieved and whether the failure was Git unavailable, source unreachable, ref resolution failure, missing file, or unreadable content. Do not claim to have applied either procedure or make recommendations that depend on its unavailable guidance. Continue only with findings that can be supported independently, clearly marked as limited.

Do not require or assume the SetupSmith CLI is installed. If it is absent, analysis can continue. Do not invent CLI installation, managed-install, or sync commands.

## 3. Inspect the catalog selectively

When the canonical source is accessible, inspect its `README.md`, `registry.yaml`, and only the relevant artifact files. Catalog directories are canonical: skills are directories containing `SKILL.md` (including their supporting resources); agents are under `agents/`, rules under `rules/`, and templates under `templates/`. `registry.yaml` may omit artifacts. Treat its status as catalog adoption metadata, not project installation or adoption state. If status is absent or invalid, report it as unknown; do not infer a status.

Recommend only items supported by project evidence. For each item, report:

- canonical ID and type;
- `ADD`, `KEEP EXISTING`, `REPLACE`, or `SKIP`;
- concise rationale and the project evidence behind it;
- overlap, conflict, or duplication with current project configuration;
- registry status when verified, otherwise `unknown`;
- proposed destination(s) for the project's supported clients;
- `installable skill candidate` or `reference-only`.

Only skill directories can be considered for managed native skill installation. Rules, agents, templates, and Project Instructions are reference-only; never describe them as installed skills. In Codex, the project destination is `.agents/skills/<name>/` and the user destination is `~/.agents/skills/<name>/`. In Claude Code, the project destination is `.claude/skills/<name>/` and the user destination is `~/.claude/skills/<name>/`. Offer only destinations documented for the client's native skill mechanism. Label an artifact managed-install eligible only for clients whose skill discovery/invocation support has been verified; identify documented but runtime-untested clients as unverified. A skill recommendation is a candidate, not a completed installation. Do not provide an unverified installation command.

For client compatibility, distinguish verified runtime support from documented placement. Codex skill invocation is `$setup-ai` or selection from `/skills`; do not describe `/setup-ai` as a Codex slash command. Claude Code invokes `/setup-ai`. If a runtime or its native skill discovery cannot be checked, label it `UNTESTED` or `BLOCKED / UNAVAILABLE` and do not imply filesystem placement proves invocation works.

## 4. Make evidence-based recommendations

For an existing project, recommend `KEEP EXISTING` when its current configuration already covers the need and fits its conventions. Use `REPLACE` only when evidence shows an artifact is stale or conflicting and explain the specific conflict; never propose an unreviewed overwrite. Use `ADD` only for a useful gap. Use `SKIP` for irrelevant, duplicative, unsupported, or unverifiable items. Do not recommend the whole catalog.

For a minimal or empty repository, report missing context and recommend only immediately useful, general configuration. Do not invent a product, architecture, language, framework, CI system, or Git convention. It is valid to return no additions when the evidence does not support one.

## 5. Return the report

Use this compact structure:

1. **Scope and evidence** — repository/client context, files inspected, relevant absences, and canonical source commit if available.
2. **Existing setup** — concise summary of relevant configuration and conventions.
3. **Recommendations** — the four-way classifications, rationale, status, destination, and installability fields above.
4. **Limitations** — exact unavailable sources, unsupported clients/artifact types, missing evidence, CLI/runtime test state.
5. **Next step** — ask which recommendations the user wants to pursue. Do not modify files in response to the analysis alone.
