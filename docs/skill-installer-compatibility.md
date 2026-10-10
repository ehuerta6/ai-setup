# Skill installer and assistant compatibility research

**Issue:** [#8](https://github.com/ehuerta6/setupsmith/issues/8)
**Evidence accessed:** 2026-10-10
**Recommendation:** Offer GitHub CLI `gh skill` as an optional, one-time bootstrap path for the future `setup-ai` skill. Do not use an installer as SetupSmith's managed install or sync engine.

## Executive summary

The common Agent Skills folder format is a practical fit for basic Codex and Claude Code skills: `SKILL.md` plus supporting files. Current native project destinations are Codex `.agents/skills/<name>/` and Claude Code `.claude/skills/<name>/`; user destinations are `~/.agents/skills/<name>/` and `~/.claude/skills/<name>/`.

GitHub CLI 2.101.0 includes `gh skill` (available since 2.90.0). It can install a selected skill from GitHub or a local source, target Codex or Claude Code, use project/user scope, and pin a tag or commit. It is still marked preview. Controlled local installs succeeded for both project destinations and temporary user-scope Codex. Supporting resources were copied. Codex's `debug prompt-input` included the fixture skill in the model-visible discovery list. Claude Code was unavailable, so its actual recognition/invocation remains untested.

The installer refuses an occupied destination without `--force`, preserving a modified file in the experiment. It also rewrites frontmatter to add source metadata; local-source metadata included an absolute path. Installer metadata is therefore not a portable SetupSmith manifest or verified content baseline.

Vercel Skills (`npx skills`) documents broader source and assistant support, project/global installs, copy/symlink modes, and update/remove commands. Its official repository released v1.7.1 on 2026-10-06. The command could not run because the npm package was not cached and network access to npm was unavailable.

Current Codex documentation says to invoke a skill with `$<skill-name>` (or select it from `/skills`); the specification's `/setup-ai` spelling is not documented for Codex. Revisit that invocation assumption before #10 implementation is treated as ready. Use immutable Git commit IDs for adopted source revisions and a separate content digest. Keep diffing, approval, path safety, collision handling, and recovery in SetupSmith. This research does not support a language, manifest encoding, or cache decision.

## Claim labels and scope

**Documented** = official docs/source; **Observed** = executed in the isolated environment; **Inference** = conclusion from evidence; **Untested** = not run. No CLI or `setup-ai` was implemented. No user installation or unrelated repository was changed.

## Comparison and decisions

| Option | Findings | License/maintenance | Decision |
| --- | --- | --- | --- |
| GitHub CLI `gh skill` | Selected skill/path; GitHub or local source; Codex/Claude targets; project/user/custom directory; tag/SHA pins; source metadata; preview/list/update. `--force` overwrites. It provides no SetupSmith manifest, reviewed diff, batch approval, verified baseline, or recovery. | GitHub CLI is MIT licensed and actively released. Skill commands are explicitly preview and may change. Requires gh >=2.90; tested 2.101.0. Skill contents retain their own authors' licensing. | **ADOPT for optional bootstrap only**, with version check, preview, review, and explicit approval. |
| Vercel Skills `npx skills` | Docs support GitHub shorthand/URLs/paths, GitLab, Azure Repos, arbitrary Git URLs, and local paths; select skills/agents; project/global scope; copy/symlink; update/remove. Ref retention and collision semantics were not established here. | MIT-licensed CLI; v1.7.1 released 2026-10-06. Requires Node/npm and package availability. README reports anonymous telemetry with opt-out variables. | **TEST** as an alternate bootstrap; don't add as a required dependency until pin, collision, symlink, and local-edit tests pass. |
| Native Codex | Docs specify repository `.agents/skills` and user `~/.agents/skills`; skills support references, scripts, assets. Codex CLI prompt-input diagnostic verified fixture discovery. | No separate installer dependency. Codex CLI observed at 0.160.0. Skill content license remains author-specific. | **ADOPT** native destinations; validate with actual target client. |
| Native Claude Code | Docs specify project `.claude/skills` and user `~/.claude/skills`; supporting files and name invocation are documented. Filesystem placement succeeded, runtime discovery did not run. | Claude Code is a separately installed proprietary product. npm install route requires Node 18+; a native installer is also documented. Skill licenses remain author-specific. | **ADOPT** documented destinations; **TEST** runtime invocation before claiming compatibility. |

Catalog inspection: the source has 21 skill folders, each with `SKILL.md`; no bundled supporting resource files were present in those folders. Agents, rules, templates, and Project Instructions remain in their separate catalog directories. `registry.yaml` is not a complete artifact index (in particular, it omits rules and most templates).

Official evidence: [gh skill install](https://cli.github.com/manual/gh_skill_install), [gh skill preview](https://cli.github.com/manual/gh_skill_preview), [GitHub CLI releases](https://github.com/cli/cli/releases), [GitHub CLI license](https://github.com/cli/cli/blob/trunk/LICENSE), [Vercel Skills README](https://github.com/vercel-labs/skills/blob/main/README.md), [Vercel Skills v1.7.1 release](https://github.com/vercel-labs/skills/releases/tag/v1.7.1), [Vercel Skills license](https://github.com/vercel-labs/skills/blob/main/LICENSE), [Codex skills docs](https://developers.openai.com/codex/skills), [Claude Code skills docs](https://code.claude.com/docs/en/skills), and [Agent Skills specification](https://agentskills.io/specification). Accessed 2026-10-10.

## Experimental environment

macOS 26.6.2; Git 2.55.0; Python 3.14.7; Node 26.8.2; npm/npx 11.19.1; GitHub CLI 2.101.0 (2026-09-15); Codex CLI 0.160.0. `command -v claude` returned no path. Each fixture used a disposable Git source/project and temporary HOME under `/private/tmp`; the directories were removed after each experiment.

The following recipe recreates the Codex and Claude destination checks, Codex prompt-input discovery check, and occupied/local-edit check. It uses only temporary directories and removes them on exit. It was rerun successfully on 2026-10-10.

```sh
set -eu
root=$(mktemp -d /private/tmp/setupsmith-issue8-repro-XXXXXX)
trap 'rm -rf "$root"' EXIT
mkdir -p "$root/source/skills/fixture-skill/references" \
  "$root/home" "$root/codex-home" "$root/codex-project" "$root/claude-project"
cat > "$root/source/skills/fixture-skill/SKILL.md" <<'EOF'
---
name: fixture-skill
description: Reports the fixture resource marker.
---
Read references/marker.txt and report its exact marker.
EOF
printf 'SETUPSMITH-FIXTURE-RESOURCE-83D2\n' > "$root/source/skills/fixture-skill/references/marker.txt"
(cd "$root/source" && git init -q && git config user.name Test \
  && git config user.email test@example.invalid && git add . \
  && git commit -qm fixture && git tag v1.0.0)
(cd "$root/codex-project" && git init -q)
(cd "$root/claude-project" && git init -q)
HOME="$root/home" gh skill install "$root/source" fixture-skill \
  --from-local --agent codex --scope project \
  --dir "$root/codex-project/.agents/skills"
HOME="$root/home" gh skill install "$root/source" fixture-skill \
  --from-local --agent claude-code --scope project \
  --dir "$root/claude-project/.claude/skills"
(cd "$root/codex-project" && CODEX_HOME="$root/codex-home" \
  HOME="$root/codex-home" codex debug prompt-input \
  'Report available skill names.' > "$root/prompt.json")
python3 -c "import json,sys; s=str(json.load(open(sys.argv[1]))); \
assert 'fixture-skill' in s; print('Codex discovery: PASS')" "$root/prompt.json"
test "$(cat "$root/codex-project/.agents/skills/fixture-skill/references/marker.txt")" \
  = 'SETUPSMITH-FIXTURE-RESOURCE-83D2'
test "$(cat "$root/claude-project/.claude/skills/fixture-skill/references/marker.txt")" \
  = 'SETUPSMITH-FIXTURE-RESOURCE-83D2'
printf 'local edit\n' > \
  "$root/codex-project/.agents/skills/fixture-skill/references/marker.txt"
set +e
HOME="$root/home" gh skill install "$root/source" fixture-skill \
  --from-local --agent codex --scope project \
  --dir "$root/codex-project/.agents/skills"
rc=$?
set -e
test "$rc" -eq 1
test "$(cat "$root/codex-project/.agents/skills/fixture-skill/references/marker.txt")" \
  = 'local edit'
printf 'Collision protection/local edit: PASS\n'
HOME="$root/home" gh skill install "$root/source" fixture-skill \
  --from-local --agent codex --scope user
test -f "$root/home/.agents/skills/fixture-skill/SKILL.md"
```

## Experiments and observations

### A. Codex native discovery

**PASS.** `gh skill` copied the fixture to project `.agents/skills/fixture-skill/`, including the reference file. Running `codex debug prompt-input 'Report available skill names.'` from the fixture Git project included `fixture-skill` and its `SKILL.md` path in the prompt's skill list. The exact resource marker remained `SETUPSMITH-FIXTURE-RESOURCE-83D2`. This proves CLI metadata discovery, not model invocation; the reference is available at its relative path but was not listed in prompt metadata.

The source Git repository includes a commit and `v1.0.0` tag, but installs use `--from-local` without a pin.

### B. Claude Code native discovery

**PASS (filesystem only).** The corresponding `gh skill install ... --agent claude-code --scope project --dir "$root/claude-project/.claude/skills"` placed `SKILL.md` and `references/marker.txt` at the documented path, retaining the marker.

**BLOCKED / UNAVAILABLE (runtime).** Claude Code was not installed; no prompt discovery or invocation was tested. Directory existence is not proof of client recognition.

### C. Minimal one-skill bootstrap

**PASS (fixture scope).** The project received just the representative fixture skill (aside from assistant-bundled skills); Codex's discovery list included it and its supporting resource remained accessible. No SetupSmith CLI was needed.

**Not tested:** `setup-ai` does not exist yet. To load canonical `ai-config-builder` and `audit-ai-config` procedures when they are not installed, the future skill must retrieve them from an accessible canonical checkout/source revision. The fixture demonstrates resource packaging and discovery only, not the complete SetupSmith bootstrap.

### D. Source and revision

**Observed:** A disposable Git source had a commit and tag `v1.0.0`; the local install was unpinned and inserted `metadata.local-path` with the absolute source path.

**Documented:** `gh skill` resolves unversioned installs to the latest repository release tag, then default-branch HEAD; tag and commit pins are supported, and source metadata supports `gh skill update`. Remote revision resolution/update was not run. Vercel README documents source URL forms and update commands; v1.7.1 release notes mention a skill lock for local-path installs. Its stored revision/schema was not executed or verified.

**Decision:** Preserve source locator and configured ref separately from resolved commit SHA. Record a content digest over relative paths and bytes. Never store the installer's absolute local-path metadata as portable identity or treat source metadata as baseline proof.

### E. Collision and file safety

**PASS (occupied path/local edit).** A duplicate install returned exit 1 with `skills already installed: fixture-skill (use --force to overwrite)`. After changing installed `marker.txt` to `local edit`, another install without `--force` returned the same error and preserved that edit. A separate user-scope Codex install went to temporary `$HOME/.agents/skills/bootstrap-fixture/`.

**Documented:** `--force` overwrites. Vercel docs describe symlink or copy installs, but collision/update semantics were not run. Symlink escape handling, interrupted installs, rollback, and remote authentication were not tested.

SetupSmith must independently reject unmanaged occupied destinations, validate symlinks and path traversal, produce concrete diffs, require approval, and recheck preconditions immediately before writing. Do not use `--force` or a prompt-skipping option as a safety policy.

## Recommendations for the MVP

1. **Bootstrap:** Once `setup-ai` exists, offer an explicitly approved `gh skill install <repo> <skill> --agent <codex|claude-code> --scope user` path. Require gh >=2.90, show a preview, and identify preview status. Don't make gh a runtime dependency. Keep Vercel as a tested alternative, not a mandatory second tool.
2. **Native destinations:** Use Codex `.agents/skills/<name>/`, Claude Code `.claude/skills/<name>/`, and documented user equivalents. Avoid older `.codex/skills` examples when current Codex docs identify `.agents/skills`.
3. **Source identity:** Pin reads to an immutable commit and retain configured branch/ref separately. Hash full skill trees, including supporting files.
4. **Responsibility:** Installer reuse ends at bootstrap. SetupSmith owns manifest, source resolution, preview, exact approval, path/symlink safety, local-change detection, selective updates, no-op behavior, and failure reconciliation. Never execute bundled scripts during install.
5. **Packaging:** No supported evidence chooses language, manifest encoding, or cache format. Before deciding, test minimal CLI packaging on the target OS and manifest round-trips for nested files and symlinks.

## Implications for Issues #9 and #10

- **#9 catalog discovery:** Implemented as a read-only CLI command. It discovers skills by `SKILL.md` directories and does not treat `registry.yaml` as exhaustive. It uses immutable revision reads and retains supporting files.
- **#10 guided analysis / `setup-ai`:** Implemented as a read-only skill that preserves one-skill startup and loads `ai-config-builder` and `audit-ai-config` from a retrievable pinned source on demand. Codex guidance is `$setup-ai` or selecting through `/skills`; Claude Code uses `/setup-ai`. A real Claude Code fixture/invocation test remains unavailable, so cross-assistant runtime compatibility is unverified.
- **Batch 2 readiness:** #9 discovery and #10 guided analysis are implemented. Managed installation and synchronization remain unimplemented. Claude Code runtime acceptance remains open pending native invocation tests.

## Remaining uncertainties

- Claude Code recognition/invocation unavailable (no executable).
- `npx --offline --yes skills --help` failed with npm `ENOTCACHED`; package not cached and registry unavailable. Vercel runtime not tested.
- Remote Git source/tag/commit resolution was documented but not executed in the fixture tests.
- No SetupSmith managed bootstrap, manifest, sync, source-freshness, installer rollback, or managed installation testing was possible because these features do not yet exist. Windows/Linux portability and broader security testing were outside the controlled experiment. Codex skill invocation syntax is documented in the MVP spec; Claude Code native invocation remains untested.

## Verification record

| Check | Result |
| --- | --- |
| `python3 scripts/validate_catalog.py` | PASS after the report edit (21 skills, 6 agents, 7 Project Instructions). |
| Codex native discovery | PASS: prompt-input listed fixture metadata from project `.agents/skills`. |
| Codex support resource | PASS: marker preserved after install. |
| Claude placement/resource | PASS (filesystem only); native runtime test blocked/unavailable. |
| One-skill pattern | PASS (fixture only); not a `setup-ai` test. |
| Occupied path/local modification | PASS: status 1 without `--force`; edit preserved. |
| Vercel Skills execution | SKIPPED: offline npm cache miss (`ENOTCACHED`). |
| Remote pin/update and symlinks | SKIPPED: documented only or not exercised. |
| `git diff --cached --check` | PASS on the staged report. |
| Markdown references/links | PASS: repository path references checked by catalog validator; every cited official URL opened successfully on 2026-10-10. |

## Independent review

The review found that the original check record named `git diff --check` after staging, which does not inspect the staged patch, and that the experiment steps were not fully reproducible. The record now names `git diff --cached --check`; a self-contained temporary-fixture recipe was added and rerun successfully. No further actionable findings remained.

## Sources

All accessed 2026-10-10: [gh skill install](https://cli.github.com/manual/gh_skill_install); [gh skill preview](https://cli.github.com/manual/gh_skill_preview); [GitHub CLI releases](https://github.com/cli/cli/releases); [GitHub CLI license](https://github.com/cli/cli/blob/trunk/LICENSE); [Vercel Skills README](https://github.com/vercel-labs/skills/blob/main/README.md); [Vercel Skills v1.7.1 release](https://github.com/vercel-labs/skills/releases/tag/v1.7.1); [Vercel Skills license](https://github.com/vercel-labs/skills/blob/main/LICENSE); [Codex skills](https://developers.openai.com/codex/skills); [Claude Code skills](https://code.claude.com/docs/en/skills); [Agent Skills format](https://agentskills.io/specification).
