# Spec: SetupSmith MVP

**Status:** Draft for user approval (product decisions consolidated; no implementation yet)  
**Date:** 2026-10-10  
**Canonical repository:** [ehuerta6/setup-smith](https://github.com/ehuerta6/setup-smith) (formerly `ehuerta6/ai-setup`)  
**Initial validation projects:** [CappyCode](https://github.com/ehuerta6/cappy-code) and [CappyHub](https://github.com/ehuerta6/cappy-hub)

## Problem

The existing catalog contains reusable skills, agents, rules, templates, and Project Instructions, but using it in other repositories requires manual inspection and copying. Once adopted, a project has no reliable portable record of which canonical revision it uses, whether its copy has been customized, or which upstream changes it can safely adopt. Existing projects also have their own conventions that generic instructions must not overwrite.

SetupSmith adds **guided adoption and deterministic lifecycle management** to the existing catalog. It does not replace the catalog or become a separate repository.

**Primary workflow:** Analyze → Recommend → Install → Sync.

## Goals

1. Let someone begin with only the `setup-ai` skill in a supported coding assistant.
2. Analyze an existing or new codebase and recommend relevant catalog artifacts, preserving project-specific configuration.
3. Let the user choose exactly which recommendations to adopt and review changes before writes.
4. Install supported artifacts for Codex and Claude Code and track their canonical identity and revisions in a portable per-project manifest.
5. Detect upstream updates, local modifications, missing installations, and conflicts; show diffs; and safely apply selected updates.
6. Keep all core file/version operations deterministic and usable through a CLI without requiring an LLM.
7. Support the current SetupSmith repository as the first canonical source without hard-coding its individual skill names into the core manager.

## Non-goals

- AI conversation memory, automatic project-context extraction, cross-project document sharing, or agent-to-agent context transfer.
- A web dashboard, hosted accounts, remote state service, background sync, or automatic update application.
- MCP integration in the MVP, including write-capable MCP tools.
- Semantic matching of existing configuration, embeddings, or vector search.
- Automatic conflict resolution, three-way content merging, or LLM rewriting of instructions.
- Arbitrary assistant-format conversion or native installation of every catalog artifact type.
- Multi-source dependency graphs, user profiles/workspaces, or managing ChatGPT/Claude Desktop Project Instructions.
- Mandatory workflows, installation of the entire catalog, or changing project architecture to accommodate the tool.

## Concepts

- **Source:** A configured Git repository with canonical reusable artifacts; initially `ehuerta6/setup-smith`.
- **Artifact:** A uniquely identified catalog item (skill, agent, rule, or template). A skill includes its full directory and supporting files, not just `SKILL.md`.
- **Project:** A Git working tree adopting an explicit subset of source artifacts.
- **Installation:** One managed copy or supported link at an assistant-specific destination. One artifact may have multiple installations.
- **Manifest:** A committed, portable record of the source, adopted artifact identities and revisions, verified baselines, and managed destinations.
- **Baseline:** Canonical content known to have been adopted. An existing installation with no verified baseline is explicitly marked unknown.
- **Global bootstrap:** An initial `setup-ai` skill installed for the user using an existing compatible skill installer, separately from project-managed artifacts.

## User-visible behavior

### 1. Bootstrap and analyze

1. A user installs **only** `setup-ai` with a supported skills distribution mechanism and invokes `/setup-ai` in Codex or Claude Code.
2. The skill inspects existing project instructions (`AGENTS.md`, `CLAUDE.md` and related configuration), technology and repository metadata, relevant architecture/product docs, Git conventions, and the SetupSmith catalog. It reads selectively, not by indiscriminately loading the whole codebase.
3. For an empty repository, it recommends only minimal immediately useful configuration. For an existing repository, it prioritizes understanding and preserving what is already there.
4. The skill reuses `ai-config-builder` (bootstrap/adopt) and `project-audit` rather than duplicating those workflows.
5. It does not require changing the canonical catalog's directory structure or credentials in the project.

### 2. Recommend and select

Each relevant recommendation is classified as **ADD / KEEP EXISTING / REPLACE / SKIP**, with concise evidence, existing overlap, installation eligibility, and a proposed destination. Unsupported or uncertain installations must be identified; they are not silently considered installed. The user selects individual items or an eligible set; selecting recommendations is not approval to write.

The catalog may recommend skills, rules, agents, and templates, but **the MVP installs and synchronizes only skills with verified Codex/Claude Code support**. Rules, agents, and templates are recommendations/reference items in this release, not promised native installations. Templates used to create project documents are never automatically synchronized back to the template.

### 3. Preview and install

The manager identifies existing installations, exact canonical matches, unmapped local configurations, and occupied destinations. It offers explicit adoption of a known existing artifact without replacing it. Ambiguous matches require a user-provided mapping; name/path heuristics alone do not establish a verified baseline. An imported unknown-baseline copy is recorded as observed/customized and protected from automated replacement; it is not represented as fully reproducible from the canonical source.

Before any change, show the selected items, destinations, expected additions/replacements, diffs and conflicts. Obtain **one explicit final confirmation per proposed batch**. Never overwrite unmanaged files or project-owned instructions (including `AGENTS.md` and `CLAUDE.md`) through ordinary installation; changes to those files require their own reviewed proposal.

Use assistant-native discovery locations, checking actual client support. Existing `.codex/` or `.ai/skills/` layouts may be imported without pretending they are automatically discoverable by every client. If one requested target is unsupported, report it before approval and require the user to adjust the selection; never claim a partially supported target set is fully installed. Installation does not execute scripts bundled with an artifact.

### 4. Check and sync

On demand, refresh or use an explicitly labeled cached source revision, and compare the canonical artifact, recorded baseline, and actual local installations. Report at minimum:

- current;
- upstream update available;
- locally modified / diverged;
- upstream removed;
- installation missing;
- unknown baseline;
- unsupported / conflicting destination.

An artifact may have different conditions across assistant targets. The report identifies the actual affected paths and whether source data is fresh or cached.

Allow per-artifact selection, **Select All Safe**, and **Select None**. Select All Safe excludes local modifications, unknown baselines, unmanaged collisions, and unsupported destinations. Show diffs and obtain one final confirmation for the approved batch. Do not change unselected items.

Validate the planned source and destination state immediately before applying it; reject stale approvals if relevant content changed since preview. Upstream removal never silently deletes an installation. Explicit removal of **managed** installations is previewed and confirmed separately.

### 5. Recover and reconstruct

An update of one artifact across multiple assistant installations is **one logical operation**. If any installation in that operation fails, attempt to restore its previous state; report incomplete recovery and never claim the artifact is fully updated while its targets disagree. Successfully completed independent artifacts may remain updated.

The manifest records the state actually achieved, not merely the requested plan. Another machine with access to the source Git history can reconstruct **verified-baseline** managed installations from the committed manifest, or report precisely why a required revision or destination is unavailable. Imported unknown-baseline customizations remain in project files and must be committed separately if users want to carry them to another clone; they cannot be reconstructed from the canonical source alone. Do not rely on absolute machine paths or secrets in the manifest.

## Functional requirements

**FR-01 — Git source and discovery.** Configure one canonical Git source; discover the current catalog without restructuring it. Discover skills from directories containing `SKILL.md`, and discover rules, agents, and templates from the corresponding source directories. Paths and file contents identify artifacts; `registry.yaml` supplies adoption/status metadata when present but is **not an exhaustive index** (it currently omits rules and templates). Report invalid/unsupported items individually, and capture immutable source revisions for comparisons. A compatible alternative source may provide explicit directory mappings.

**FR-02 — Guided analysis.** `setup-ai` inspects only relevant project evidence; explains recommendations and delegates established analysis procedures to `ai-config-builder` and `project-audit`.

**FR-03 — User choice.** Classify ADD/KEEP EXISTING/REPLACE/SKIP. Preserve project-specific behavior. User chooses exact artifacts and assistant targets.

**FR-04 — Managed installations.** Install verified native skills, including any supporting resources, for Codex and Claude Code. Explicitly distinguish unsupported/legacy layout from native discovery.

**FR-05 — Safe existing adoption.** Identify exact matches using content and source evidence where possible. Permit manual mapping of existing or locally modified artifacts without overwriting; an unverified historical baseline remains unknown. Distinguish an observed imported file from a verified, reconstructable installation.

**FR-06 — Portable manifest.** Record source locator, canonical artifact identity, adopted immutable revision/content digest or unknown baseline, and each relative managed target. Separate source catalog status (`registry.yaml`) from project adoption state.

**FR-07 — Deterministic comparison.** Compare source, recorded baseline, and on-disk content; detect updates and local edits without relying on model judgment. Offline results must disclose cache freshness.

**FR-08 — Selective safe writes.** Preview concrete diffs; confirm the batch; protect unmanaged and changed files; apply only selected updates and perform a freshness/precondition check before mutation.

**FR-09 — Consistency and failure reporting.** Maintain artifact-level consistency across multiple installations where possible; restore failed changes when possible; report partial results truthfully and reconcile the manifest to actual state.

**FR-10 — Portable reconstruction.** Rehydrate verified-baseline managed configuration using immutable source revisions and portable destinations, without silent substitution if pinned revisions are inaccessible. Report explicitly when an imported unknown-baseline customization cannot be reconstructed solely from the manifest and canonical source.

**FR-11 — Interfaces.** Provide a standalone CLI for registration/initialization, listing, adding/adopting, checking, diffing, selectively updating, restoring, and explicitly removing managed items. Exact command names are a technical/design choice. `setup-ai` is a guided agent entry point to these capabilities, not a second implementation of file operations.

**FR-12 — Approval boundary.** Read-only discovery needs no write approval. Every write affecting project files or manifests requires approval of the exact proposed change; an agent selecting items is not itself authorization. Installing a missing CLI/tool dependency also requires user approval.

## Constraints and invariants

- **Single repository:** Keep SetupSmith's source catalog and installer code in `ehuerta6/setup-smith`; preserve existing catalog entries and responsibilities.
- **Canonical precedence:** New explicit decisions and target-project sources outrank reusable defaults. One authoritative home per reusable behavior.
- **Local-first and lightweight:** Use Git and local files/state, with no required cloud service or LLM for deterministic operations.
- **Portability:** No absolute paths or credentials in committed manifests. Local cache may be machine-specific and uncommitted.
- **Safety:** Avoid executing bundled scripts during installation; treat downloaded instructions as untrusted content; reject path traversal and symlinks that escape managed destinations; preserve applicable licenses/third-party notices.
- **Compatibility:** Do not assume arbitrary Markdown placed in a vendor folder is natively consumed. Support initially verified Codex and Claude Code skill layouts.
- **Truthful status:** No claimed installation, update, test pass, or recovery without evidence.

## Edge cases

| Case | Required behavior |
| --- | --- |
| User invokes setup on an already configured project | Inspect existing manifest and files; recommend updates/changes without duplicating managed files. |
| Existing file resembles a source skill but revision is unknown | Show possible match; allow explicit mapping; preserve content and unknown baseline. |
| Global bootstrap skill also exists locally | Recognize possible duplicate and avoid installing the same item without purpose. |
| Source has an update; local file was edited | Mark divergence and exclude from safe bulk update. |
| A managed installation is missing | Report missing; do not assume deleted intentionally or current. |
| Upstream artifact was deleted or renamed | Preserve local copy; explicit removal/mapping only. |
| Destination belongs to unmanaged content | Block ordinary installation and request a separate review. |
| Two selected artifacts target the same path | Block colliding operations before writes. |
| GitHub/source unavailable | Use local cache only if available; disclose revision and stale status. |
| Changes occur between preview and apply | Reject stale proposal and request another review. |
| Multi-target write partially fails | Restore where possible; disclose inconsistent targets and accurate manifest. |
| Same update runs twice without changes | No-op; do not rewrite files or report a new update. |
| Source commit referenced in manifest cannot be obtained | Explain unavailable revision; never replace it silently with latest. |
| Imported artifact has an unknown baseline in a fresh clone | Preserve any project-committed custom files; otherwise report that exact reconstruction is unavailable. |
| Target client cannot discover artifact | Report unsupported; do not claim success. |

## Implementation decisions and boundaries

- `setup-ai` is a **skill**, not a new orchestration agent or an MCP server.
- Reuse `ai-config-builder` and `project-audit`; do not duplicate their adoption/audit procedures in the skill.
- The CLI owns deterministic file changes and manifest state, while the agent owns contextual analysis/recommendations.
- The initial bootstrap should reuse an existing verified skill installer (e.g. Vercel Skills or an official client plugin) rather than requiring our own bootstrap executable. Do not claim an example installation command works until `setup-ai` exists and is tested.
- Evaluate `gh skill`, `npx skills`, and native client mechanisms for reusable internals/behaviors before implementing an installer. Third-party behavior may not satisfy our diff/approval guarantees; our manager remains responsible for them.
- Global bootstrap is supported, but complicated shared global/project profiles and system-wide update orchestration are outside MVP.
- Technical details (language, manifest encoding, cache format, command spelling, adapter layout, reuse of existing installers) remain implementation choices, provided all requirements above are met.

## Data and interface changes

The MVP introduces **one versioned, portable per-project manifest** with these logical fields:

- manifest schema version;
- source Git locator and configured branch/ref;
- canonical artifact ID and immutable adopted source revision;
- baseline content identity, or an explicit unknown-baseline marker;
- relative installation destinations and assistant targets.

It must be possible to distinguish source drift from local drift. The committed manifest is authoritative for *management identity*; actual filesystem content is authoritative for *what is installed*. Cache and temporary recovery data are not part of the committed contract.

A CLI is required; its exact spelling is not fixed by this specification. The `/setup-ai` skill provides the conversational path.

## Acceptance criteria

- [ ] Installing only `setup-ai` allows an agent to begin guided setup in an existing Git project without installing the whole catalog.
- [ ] Analysis of CappyCode identifies existing AI configuration and recommends only relevant catalog items with ADD/KEEP EXISTING/REPLACE/SKIP rationale.
- [ ] CappyHub can be analyzed independently and use a different adopted selection or revision.
- [ ] An existing locally customized skill can be explicitly adopted without content loss or fabricated baseline.
- [ ] Selected supported skills are discoverable by Codex and Claude Code at their actual native locations.
- [ ] Approved installation produces a portable manifest with accurate canonical revisions and destinations.
- [ ] A real changed upstream skill is detected and a concrete diff is shown.
- [ ] Select All Safe omits locally modified, unknown-baseline, unmanaged-conflict, and unsupported items.
- [ ] One batch approval changes exactly the selected managed installations; no approval means no write.
- [ ] Changes made after preview cause apply to refuse the stale proposal.
- [ ] An upstream deletion does not remove the managed copy automatically.
- [ ] Offline checks show exactly which cached revision was used and its freshness limit.
- [ ] A simulated partial failure reports actual state and cannot falsely report every assistant target current.
- [ ] A separate clone can reconstruct verified managed installations from source revisions, or fail explicitly for unavailable revisions and unknown-baseline customizations.
- [ ] Core compare/install/update behavior works from the CLI without an LLM or MCP.

## Verification

1. Exercise fresh and already-configured setups in CappyCode and CappyHub without modifying their product-specific instructions during discovery.
2. Demonstrate one real canonical skill revision change and independent opt-in updates in both projects.
3. Modify one installed skill locally and verify safe-update exclusion, diff correctness, and preserved content.
4. Simulate occupied unmanaged paths, missing files, upstream deletion, stale proposals, network failure, and a failure halfway through a two-assistant update.
5. Recreate verified configuration from the manifest in a fresh clone and verify target assistant discovery, contents, and source revisions; report unknown-baseline imports distinctly.
6. Run repository validation and any implementation tests actually present, reporting explicit pass/fail/untested results.

## Open questions

**No unresolved product decisions known to block this MVP.** Before implementation, perform a short technical evaluation of reuse options (`gh skill`, Vercel Skills, native integrations), choose manifest encoding and packaging, and verify current Codex/Claude locations and behavior experimentally. Do not treat untested external command examples as completed capabilities.

## Deferred roadmap

After real usage validates the MVP: broader native rule/agent support, optional global selection profiles, optional MCP read integration, richer update review, per-project workspaces, curated cross-project context, and retro-derived improvement suggestions. None is needed to ship the MVP.
