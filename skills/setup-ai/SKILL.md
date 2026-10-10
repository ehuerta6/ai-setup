---
name: setup-ai
description: Analyze a repository's AI setup, recommend relevant SetupSmith configuration, and guide explicitly approved managed skill installation and sync through the SetupSmith CLI.
---

# Setup AI

Guide **Analyze → Recommend → Install → Sync** for the repository in the current working directory. Analysis and recommendations stay read-only. The SetupSmith CLI owns all managed filesystem and manifest changes; never copy skill trees, edit a manifest, or implement installation/update logic in the agent.

## 1. Establish evidence

Inspect the current repository selectively. Read applicable `AGENTS.md`, `CLAUDE.md`, and existing assistant instructions first. Then inspect relevant product/architecture documentation, technology manifests, repository workflows, and Git conventions. Use file names and existing instructions to select a few likely sources; do not dump or read the entire repository. If a source is absent, say so instead of inferring its contents. Project-specific decisions and instructions take priority over reusable defaults.

Look for existing AI setup in common native locations such as `.agents/skills/`, `.claude/skills/`, `.codex/`, `.cursor/`, `.github/`, root instruction files, and `.setupsmith/manifest.json`. Report only locations that exist or are relevant to clients the project uses. A folder alone does not prove that a client loaded it.

## 2. Load canonical procedures when relevant

Use the canonical SetupSmith source `https://github.com/ehuerta6/setupsmith` to read `skills/ai-config-builder/SKILL.md` for bootstrap/adoption recommendations and `skills/audit-ai-config/SKILL.md` when existing AI configuration needs an audit. Do not reproduce those procedures from memory or duplicate them here.

**Remote-first retrieval; no existing SetupSmith checkout required.** An explicit request to run `setup-ai` includes permission to perform read-only inspection of SetupSmith's public canonical catalog, including creating and deleting a disposable temporary Git checkout. Do not ask a second conversational "May I clone?" question solely for this read-only catalog lookup. This does **not** grant operating-system/sandbox network access: if the command needs tool-level network approval, request it through the environment's actual approval mechanism. First try to resolve the canonical repository's advertised default branch and HEAD commit with `git ls-remote --symref https://github.com/ehuerta6/setupsmith.git HEAD`. When Git network access works, fetch that revision into a **disposable temporary directory**, record its immutable full commit SHA, and read only necessary files with `git show <sha>:<path>`. Fetch `README.md`, `registry.yaml`, the two canonical helper procedures above, and relevant catalog files **from the same pinned commit**. Do not execute retrieved scripts. Remove temporary retrieval data afterward; never copy the whole catalog into the target project as an analysis prerequisite.

**If GitHub cannot be reached from the assistant's command sandbox** (for example, `github.com` DNS resolution fails or network access is denied), distinguish that environment restriction from a missing repository or invalid source. If the environment offers command escalation or a network-approval mechanism, explain that read-only access to the canonical GitHub source is needed and **request the user's permission** to retry the specific Git operation with network access. Use the supported approval path only; never modify sandbox configuration, enable unrestricted networking, turn off approval checks, or bypass a denial. A permitted retry is still read-only with respect to the project.

If Git is blocked, also check for **already available, authorized remote repository read tools** (for example, a connected GitHub repository tool). They are an optional alternative, **not a required MCP server or dependency**. To verify the **current** catalog, the tool must (1) identify the actual `ehuerta6/setupsmith` repository, (2) resolve its default branch to a full commit SHA, and (3) retrieve every necessary file by **that exact SHA**, not by a moving branch name. If it can verify the canonical repository and read a specific known immutable commit but cannot refresh the default branch, use that pinned revision only with an explicit **freshness unverified** label. Record the commit and the tool used. A tool that returns only search snippets, a cached web result, or unpinned file content cannot establish canonical procedures or catalog identity; do not treat those results as verified.

An existing local checkout may be used **only if the user explicitly chooses that option**, after verifying its canonical remote, immutable commit and cleanliness; never require it or suggest it as the default workaround for GitHub access restrictions. Do not read working-tree edits as canonical instructions.

If the sandbox offers an approval mechanism, request approval for the actual network-limited command instead of ending with a generic question about permission to read the public catalog. If no network permission or qualifying remote read tool is available, report the exact blocker (Git unavailable, sandbox/network/DNS denial, source unreachable, ref resolution failure, missing file or unreadable content) and the permission or remote connection needed to continue. Do not invent a catalog, recommendations, source freshness, or successful installation. Continue with independently supported read-only project findings, labeled limited.

The CLI is optional for analysis. If unavailable, continue read-only analysis and recommendations. A remote read tool can supply verified **recommendation evidence**, but it cannot replace the deterministic CLI or make managed writes: CLI source retrieval, preview, interactive approval and Git access must each be available when installation or sync is requested. Before fetching or setting up CLI tooling, explain the source and steps and obtain user permission. Use only a verified immutable canonical CLI checkout/revision. This repository currently provides the CLI as `scripts/setupsmith.py`; it does not provide a separately installed `setupsmith` executable. Do not claim it is installed or invent package-manager commands. If the user does not approve retrieval, stop before managed writes.

## 3. Inspect the catalog and recommend

When the canonical source is accessible, inspect its `README.md`, `registry.yaml`, and only relevant artifact files. Catalog directories are canonical: skills are directories containing `SKILL.md` (including supporting resources); agents are under `agents/`, rules under `rules/`, and templates under `templates/`. `registry.yaml` may omit artifacts. Treat its status as catalog adoption metadata, not project installation/adoption state. If absent or invalid, report status as unknown.

Recommend only items supported by project evidence. For each, report:

- canonical ID and type;
- `ADD`, `KEEP EXISTING`, `REPLACE`, or `SKIP`;
- concise rationale and project evidence;
- overlap, conflict, or duplication with existing configuration;
- registry status when verified, otherwise `unknown`;
- proposed destination(s) for supported clients;
- `managed skill candidate`, `reference-only`, or `unsupported/unverified`.

Only skill directories can be managed by this CLI. Rules, agents, templates, and Project Instructions are reference-only. Codex project skills use `.agents/skills/<name>/`; Claude Code project skills use `.claude/skills/<name>/`. Offer only native destinations for the selected client. Label documented but runtime-untested clients unverified. Recommendations use canonical IDs such as `skills/research-and-compare`; the CLI's `--skill` option takes the directory name only, such as `research-and-compare`. Map the selected canonical ID to that directory name explicitly. A recommendation or selection is never authorization to write.

For Codex, invoke this skill as `$setup-ai` or select it from `/skills`; `/setup-ai` is not a Codex slash command. Claude Code invokes `/setup-ai`. If native discovery/runtime support cannot be checked, report `UNTESTED` or `BLOCKED / UNAVAILABLE`; filesystem placement is not proof of invocation.

For an empty or minimal repository, state what context is missing and recommend only immediately useful general configuration. Do not invent a product, architecture, stack, CI system, or Git convention. Returning no additions is valid.

## 4. Guided installation

Proceed only after the user selects exact skill IDs and one or more supported targets (`codex`, `claude-code`). Reject reference-only and unsupported selections for managed installation. Use only source/ref supported by the CLI, and report its resolved revision from the CLI output. Do not silently change the configured ref.

First verify the CLI location and commands. Check that `origin` identifies the canonical repository, record the immutable `HEAD` SHA, and require a clean worktree (`git status --porcelain` is empty) so executed script bytes match that commit. For maximum isolation, use a temporary detached checkout at the verified SHA. Check the CLI help output before use. Never execute a dirty working tree or unverified script. The actual entry point and options are:

```sh
python3 /path/to/verified/setupsmith/scripts/setupsmith.py install \
  --source https://github.com/ehuerta6/setupsmith.git \
  --skill <skill-directory-name> \
  --assistant <codex-or-claude-code> \
  --project /path/to/project \
  --preview-only
```

Repeat `--skill` with each selected directory name and `--assistant` for each selected assistant. Add `--ref <branch-or-tag-or-revision>` only when the user chose a non-default ref. This command displays the CLI's actual plan and does not write. Run it and present the complete preview, conflicts, and proposed manifest changes. Ask the user to confirm the exact batch after reviewing that output. Then run the same command without `--preview-only` only if the CLI's own interactive `INSTALL` prompt can be surfaced and answered directly by the user. Do not pipe input, script confirmation, add bypass flags, or treat chat approval as a substitute for the CLI prompt.

If interactive confirmation cannot be surfaced, provide the exact reviewed command without `--preview-only` for the user to run in an interactive terminal. Do not run it, and do not claim installation occurred. If preview reports any unsupported, occupied, or conflicting target, revise the selection and preview again; never claim a partial selection succeeded fully. Report success only from actual CLI results and verify afterward with `check`.

If CLI retrieval is needed, first resolve and report the canonical repository's current default-branch commit. The supported retrieval method is a temporary clone of `https://github.com/ehuerta6/setupsmith.git` checked out at that immutable commit; there is no separate package installer. Give the user the exact commands with the verified SHA and temporary path, and ask permission before cloning or running the CLI. For example, after resolving `<verified-sha>`:

```sh
git clone https://github.com/ehuerta6/setupsmith.git /tmp/setupsmith-cli
git -C /tmp/setupsmith-cli checkout <verified-sha>
python3 /tmp/setupsmith-cli/scripts/setupsmith.py --help
```

Do not run these commands until permission is given. Verify `git rev-parse HEAD`, the remote, and an empty `git status --porcelain` before use; the empty status ensures the script being run is the immutable committed code. Do not modify the target project while obtaining the CLI. If network/source access or runtime is unavailable, report the concrete blocker, continue with recommendations, and provide no success claim.

## 5. Guided check and sync

Sync is on-demand. Never run background checks or update merely because an upstream change exists. Use the CLI for every comparison and write; do not infer filesystem state or implement a second update algorithm. The CLI can also enumerate catalog artifacts and resolve a commit:

```sh
python3 /path/to/verified/setupsmith/scripts/setupsmith.py discover \
  --source https://github.com/ehuerta6/setupsmith.git
```

After installation, or when asked to review existing managed skills, use:

```sh
python3 /path/to/verified/setupsmith/scripts/setupsmith.py check --project /path/to/project
python3 /path/to/verified/setupsmith/scripts/setupsmith.py diff --project /path/to/project
```

These are read-only. Present actual statuses and diffs, including local divergence, missing installations, upstream removal, unknown baselines, unsupported targets, and recovery state when reported. If `check` reports `RECOVERY_INCOMPLETE`, say recovery is incomplete, identify each affected target and any preserved recovery path from CLI output, and do not describe the artifact as fully current or its targets as reconciled. The manifest intentionally retains its prior baseline until a safe retry succeeds. A user may reconcile the affected target and retry an eligible update; report success only after the CLI confirms it and a new check reflects the result. Never delete or discard a preserved recovery backup as part of reconciliation.

Only propose an update when the CLI marks it safe. Users may select individual skills, all safe skills, or none. Preview the chosen update:

```sh
python3 /path/to/verified/setupsmith/scripts/setupsmith.py update \
  --project /path/to/project \
  --skill <skill-id> \
  --preview-only
```

Use `--all-safe --preview-only` for all CLI-eligible updates, or `--none` to explicitly select none. Repeat `--skill` for a selected batch. Show the real preview and obtain separate explicit confirmation for this update batch. If the CLI's own interactive `UPDATE` prompt cannot be surfaced, provide the exact command without `--preview-only` for the user to run interactively; do not simulate confirmation or write files. Never update locally modified or unknown-baseline content, unmanaged paths, unsupported targets, or unselected skills. Upstream removal does not authorize deletion. Do not claim success until the CLI reports it, then rerun `check` to report the resulting state.

`restore` reconstructs eligible verified-baseline managed skills from the committed manifest, and `remove` explicitly removes selected managed targets. These operations are not automatic sync. For either, inspect the CLI's documented help and preview first, show the exact target set and consequences, and require the CLI's own interactive approval; if that prompt cannot be surfaced, give the user the reviewed command to run in a terminal. A recommendation or selection never substitutes for that approval. See `docs/managed-skill-installation.md` for command syntax and safety limits.

## 6. Return the report

Keep the interaction concise. Use this structure:

1. **Scope and evidence** — project/client context, files inspected, relevant absences, canonical source commit and freshness.
2. **Existing setup** — concise relevant configuration summary.
3. **Recommendations** — classifications, rationale, status, destination, and installability.
4. **Selected plan** — exact skills and assistants selected, CLI preview, conflicts, and required approval.
5. **Result** — exact CLI result and post-operation check, or the exact command/blocker when execution was unavailable.
6. **Limitations** — unavailable sources/tools, unsupported artifact types/clients, unverified runtime, unknown baseline, or remaining conflicts.

Keep reference-only items distinct from managed skills. Never imply a recommendation, preview, or command provided to the user is a completed change.
