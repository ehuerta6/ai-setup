# SetupSmith MVP end-to-end validation

**Date:** 2026-10-10
**Issue:** [#19](https://github.com/ehuerta6/setupsmith/issues/19)
**SetupSmith base:** `1a09dd426cba92745a6eaa3a07e67aef2d20e657`

## Scope and environment

Validation used disposable Git clones. All project-local bootstraps, manifests, installs, edits, and removals stayed in temporary clones; no test changes were committed or pushed to CappyCode or CappyHub. No application test suites, database commands/migrations, production data, credentials, or deployments were used.

| Repository | Branch | Source commit |
| --- | --- | --- |
| SetupSmith | `main` at validation start | `1a09dd426cba92745a6eaa3a07e67aef2d20e657` |
| CappyCode | `main` | `1559f250ea0fc495f934030d312cb78eacf663e6` |
| CappyHub | `main` | `70b80c20f3d525251b2357071bd6c00bfc8d1366` |

Environment: macOS 26.6.2, Python 3.14.7, Git 2.55.0, Codex CLI 0.160.0. Claude Code was not installed. No standalone `setupsmith` command was available; commands ran through `python3 scripts/setupsmith.py` in a clean SetupSmith checkout at the base SHA.

The canonical source locator was `https://github.com/ehuerta6/setupsmith.git`, with `refs/heads/main`. A local Git mirror made source reads deterministic and independent of network access. It began at the actual SetupSmith base, then received unpublished commits:

| Revision | Commit | Controlled change |
| --- | --- | --- |
| A | `1a09dd426cba92745a6eaa3a07e67aef2d20e657` | Actual SetupSmith base |
| B | `5c0bbd7e04eac0c0e5ecce28652b11fa0d4fe1ff` | Edit `audit-ai-config/SKILL.md`; add Markdown support file and binary resource |
| C | `39bf2a5f6d44b04b1d05330742e3079bf2b8ec79` | Change audit text/resource/binary and separately change `setup-ai` |
| D | `ea2a38d0f493119826e0e63e9076b24b270e753a` | Remove `audit-ai-config` from controlled source |

The CLI received the canonical HTTPS URL; per-process Git URL rewriting sent its fetches to the local fixture. Thus CLI `fresh` status means fresh relative to that fixture, not a live GitHub check. One command without the rewrite confirmed an unreachable canonical source reports `SOURCE_UNAVAILABLE` and “no cached source was used.”

## Phase A: analyze and recommend

Only revision A’s `skills/setup-ai/SKILL.md` was bootstrapped into each clone at `.agents/skills/setup-ai/`. Its SHA-256 was `74f56fd22cfbccfd46dd902cefb93d6a1c7d535e4c06432704522de059efd5fd`. The bootstrap preceded analysis. Before and after analysis, both clones had no tracked changes; the only untracked item was that bootstrap. No manifest existed. The current assistant followed the canonical `setup-ai` process and loaded `ai-config-builder` and `audit-ai-config` from immutable revision A.

### CappyCode

| Canonical ID | Recommendation | Type / registry | Rationale and target |
| --- | --- | --- | --- |
| `skills/setup-ai` | ADD for validation bootstrap | Managed skill candidate / `testing` | Supports requested analysis; native Codex target `.agents/skills/setup-ai/`. |
| `skills/firebase` | KEEP EXISTING | Managed skill / `testing` | `.codex/skills/firebase/`, CappyCode’s Firebase documentation, Firestore rules, and project instructions already govern Firebase. Preserve; do not migrate. |
| `skills/verify-change` | KEEP EXISTING | Managed skill / `testing` | Existing `.codex/skills/verify-change/` and the project’s Git conventions document define workflow. |
| `skills/ai-config-builder` | KEEP EXISTING | Managed skill / `testing` | Existing `.codex/skills/ai-config-builder/` is customized; do not replace by name alone. |
| `skills/audit-ai-config` | SKIP | Managed skill / `testing` | Duplicates `.codex/skills/project-audit/` and CappyCode’s AI configuration document. |
| `skills/git-flow` | SKIP | Managed skill / `testing` | Duplicates project `github-flow` and its Git conventions document. |
| `rules/security` | KEEP EXISTING | Reference-only / status unknown | `.codex/rules/security.md` and Firestore rules are project-owned sources. |

### CappyHub

| Canonical ID | Recommendation | Type / registry | Rationale and target |
| --- | --- | --- | --- |
| `skills/setup-ai` | ADD for validation bootstrap | Managed skill / `testing` | Supports analysis; native Codex target `.agents/skills/setup-ai/`. |
| `skills/audit-ai-config` | ADD | Managed skill / `testing` | Complements its `.ai/skills/` collection with a reusable configuration audit; target `.agents/skills/audit-ai-config/`. |
| `.ai/skills/database-change` | KEEP EXISTING | Project-owned; no canonical match | Its Supabase migration, RLS, and generated-type procedure is project-specific. |
| `.ai/skills/local-database-workflow` | KEEP EXISTING | Project-owned; no canonical match | Governs CappyHub’s distinct local Supabase states. Preserve it. |
| `skills/verify-change` | KEEP EXISTING | Managed skill / `testing` | Existing `.ai/skills/verify-change/` is project-owned; avoid duplicate placement. |
| `skills/firebase` | SKIP | Managed skill / `testing` | CappyHub uses Supabase/PostgreSQL. |
| `rules/security` | KEEP EXISTING | Reference-only / status unknown | Project instructions and database policies govern authorization. |

SetupSmith skills in the registry are `testing`; status is catalog metadata, not project adoption. The registry does not list `rules/security`, so that status is unknown. CLI discovery marked `.codex/skills/` and `.ai/skills/` as legacy/non-native candidates, not native installations. A test-only mapping of `.codex/skills/project-audit` to `skills/audit-ai-config` below tests custom-name handling; it is not a recommendation to replace that skill.

**Analysis changed no files:** both clones had an empty `git diff HEAD`; only the one-file bootstrap was untracked.

## Phase B: selective installation and adoption

All CLI and subcommand help was inspected before use. `discover` at A returned `complete: true`, `refs/heads/main`, and revision A; both selected skills were registered with status `testing`.

| Clone | Actual CLI selection and result |
| --- | --- |
| CappyCode | `adopt` selected exact `.agents/skills/setup-ai → skills/setup-ai` and verified it at A. It also explicitly mapped customized `.codex/skills/ai-config-builder → skills/ai-config-builder` and `.codex/skills/project-audit → skills/audit-ai-config`; both became `baseline_state: unknown`, `revision: null`, with observed hashes and `codex-legacy` targets. Existing bytes were not rewritten; other skills remained unmanaged. |
| CappyHub | `adopt` selected exact `.agents/skills/setup-ai → skills/setup-ai` at A. `.ai/skills/` remained unmanaged. `install` selected only `skills/audit-ai-config`, Codex, `.agents/skills/audit-ai-config/`, ref `refs/heads/main`, revision A. Preview showed paths, hashes, and proposed manifest. A second target at `.claude/skills/audit-ai-config/` was later installed only to test sibling removal. |

Every write used the CLI TTY boundary. `INSTALL`, `UPDATE`, `RESTORE`, and `REMOVE` inputs were simulated only inside disposable clones/fixtures, as allowed by the request; these were not presented as human confirmations. Declined approval and noninteractive writes changed nothing. No real project configuration was touched.

Manifest inspection confirmed canonical source URLs, refs, immutable revisions, relative destinations, and per-file SHA-256 values. No credentials, machine-specific paths, or absolute target paths were present. Existing unmanaged project files were preserved.

## Phase C: checks, diffs, sync, and refusals

At A, `check` reported verified setup-ai/audit-ai-config as `CURRENT`. CappyCode’s explicit legacy mappings were `UNKNOWN_BASELINE` and `UNSUPPORTED_TARGET`; no historical revision was invented.

At B, CappyHub `check`/`diff` reported `UPSTREAM_UPDATE` for audit-ai-config, a concrete Markdown diff, an added supporting file, and a binary SHA-256 diff. The selected update preview showed proposed files and manifest changes. Declining at the TTY and a noninteractive attempt left revision A and all files unchanged. An approved simulated TTY update advanced only audit-ai-config to B. Repeating update at B selected no artifacts and wrote nothing.

At C, `--all-safe --preview-only` showed both changed skills; `--none --preview-only` selected none. An approved update selected only audit-ai-config, advancing B → C. setup-ai stayed pinned at A. Follow-up `check` reported audit-ai-config `CURRENT` and setup-ai `UPSTREAM_UPDATE`; `--all-safe` then selected only setup-ai. This verified that an unselected artifact and baseline were preserved.

For local-edit preservation, CappyCode’s verified setup-ai file was edited after adoption. `check` and `diff` showed `LOCAL_DIVERGENCE, UPSTREAM_UPDATE` and the exact local patch. `--all-safe` excluded it as different from baseline. The edited SHA-256 remained `f9d9af74178c268a290455d959e41c53d12fba123e62cdd471a4a086b99770ea`; its manifest revision/hash remained A. Unknown-baseline entries retained `revision: null`; `diff` stated that a historical text diff was unavailable and reported observed hashes.

At D, the CLI reported `UPSTREAM_REMOVED`; local files remained intact and `--all-safe` explicitly excluded the removed skill. A separate canonical-source outage reported `SOURCE_UNAVAILABLE` and no cached source. Automated tests cover occupied destinations, stale source/local/manifest previews, missing files, unsafe paths, unknown-baseline edits, and other refusals.

## Phase D: restore, removal, and native discovery

### Fresh-clone restore

A separate controlled fixture project was committed with the CLI-produced CappyHub manifest and freshly cloned. Seed commit: `3356ecd0598f522dc7f3dd6652f8b92825be034e`. The manifest pinned audit-ai-config to C and setup-ai to A. Restore preview listed exact destinations and file hashes; applying restore reconstructed both full trees from those pins, including binary bytes `666978747572652d62696e6172792d7265766973696f6e2d4300fe`.

Manifest SHA-256 remained `bc4d168ccdde65958952323a03f4faceb8413bc291e909f06753ff2a78663fa9`. Repeat restore said “Already restored and verified” and made no changes; file hashes, sizes, mtimes, and inodes matched. Automated tests separately cover unavailable pins, unknown-baseline customizations, unsupported targets, occupied paths, and stale restore plans. A CappyCode restore preview stopped on unknown/local content conflicts and wrote nothing.

### Managed removal

Removal preview selected only `skills/audit-ai-config=.agents/skills/audit-ai-config` and showed `.claude/skills/audit-ai-config` as the remaining target. A noninteractive attempt was refused with no changes. After simulated TTY approval, only the Codex target was removed. The Claude sibling and unrelated setup-ai entry remained. The final check continued to report the sibling as `UPSTREAM_REMOVED` at D. Automated tests cover modified-content refusal, recovery backups/state, stale content, and unrelated entries.

### Native assistant discovery

- **Codex:** `codex debug prompt-input '$setup-ai'` showed setup-ai loaded from `.agents/skills/` in both clone contexts (Codex CLI 0.160.0). This is native discovery evidence. A separate read-only `codex exec` was attempted: global state writes were denied by the sandbox; with a temporary Codex home, the runtime started but could not resolve/reach its model endpoint. Separate CLI invocation is therefore unverified; it is not claimed as passed.
- **Claude Code:** `claude --version` failed because the runtime was absent. It was not installed. `.claude/skills/` was used only for CLI file lifecycle testing; native discovery/invocation remains **BLOCKED / UNAVAILABLE**.

## Checks and acceptance matrix

The automated CLI suite, manual filesystem/hash assertions, agent-guided analysis, and native discovery diagnostic are separate evidence types. Local results: `python3 -m unittest discover -s tests -v` passed (99 tests); `python3 scripts/validate_catalog.py` passed after correcting project-doc references; `git diff --check` passed. The GitHub Actions workflow is `.github/workflows/validate-catalog.yml`; its PR result is reported separately from local checks.

| Issue #19 criterion | Status | Evidence type |
| --- | --- | --- |
| Analyze both projects from setup-ai-only bootstrap; distinct evidence-based recommendations; no analysis writes | PASS | Agent-guided read-only workflow; Codex prompt-input diagnostic; clone status/diff |
| Adopt/install in both projects and selectively apply real Git source changes | PASS | Actual CLI previews; disposable TTY simulations; revisions A–C; manifest/hash checks |
| Local edits, unknown baselines, conflicts/stale plans, upstream removal, missing files, offline/cache reporting | PASS | Manual project clone edit/outage/removal; automated CLI unittest fixtures |
| Multi-target recovery and fresh-clone restore, including pinned/unavailable revisions and unsupported targets | PASS | Automated recovery/restore fixtures; actual committed-manifest clone restore and no-op repeat |
| Actual Codex and Claude Code native discovery | BLOCKED / UNAVAILABLE | Codex discovery passed; Claude runtime unavailable. Directory placement was not counted as discovery. |
| Catalog validation and configured CLI checks with reproducible evidence | PASS | Local checks and CLI results; CI reported separately |

| GitHub Actions `validate-catalog` workflow for the PR | PENDING | Workflow is configured to run catalog validation and the unittest suite; check the PR check result before treating CI as passed. |

## Findings, limitations, and reproduction

- No blocking SetupSmith defect was observed in the exercised lifecycle commands. No product code or tests changed; this PR adds the report only.
- The local clone initially pointed at `53199317cbf42ae7a950b0a9c1f818a8aa5e7b5b`, whose README/WORKFLOWS were stale about update/removal. Refreshing to the requested base `1a09dd4…` brought those docs into alignment with the CLI and managed-installation guide. No documentation change was needed for that drift.
- Codex discovery is verified, but a separate CLI skill invocation could not reach its model endpoint. Claude Code discovery/invocation is unavailable. These gaps prevent declaring the complete native-runtime criterion validated.
- Controlled catalog commits B/C/D and the restore fixture were local and unpublished. Per-process URL rewriting preserved the canonical source identity while resolving those fixture commits.

To reproduce, clone the two project SHAs above into disposable directories, bootstrap only SetupSmith revision A’s `skills/setup-ai/SKILL.md` at `.agents/skills/setup-ai/`, then confirm `git diff HEAD` is empty after analysis. Inspect `python3 scripts/setupsmith.py --help` and each subcommand’s help. Run the recorded `adopt`/`install` previews before TTY-approved writes. Build a local source mirror at A, create real Git commits B/C/D with the changes in the table, and direct only the CLI process’s Git URL resolution to that mirror. Commit the CLI-produced manifest only in a separate controlled restore fixture; clone it and test `restore`. Do not commit or push project clone changes. The automated regression reproduction is the unittest command below; existing fixture tests cover detailed refusal and recovery cases.

### Reproducible CLI sequence

The following uses `$T` for a temporary parent directory and assumes the SetupSmith checkout is `$T/setupsmith`, the disposable projects are `$T/cappy-code` and `$T/cappy-hub`, and the catalog mirror is `$T/catalog-fixture`. Create those clones first. Create the catalog mirror and configure its local author before the first CLI call. Before CLI commands that read the catalog, scope Git URL rewriting to the shell:

```sh
export T=/private/tmp/setupsmith-repro
git clone --local "$T/setupsmith" "$T/catalog-fixture"
git -C "$T/catalog-fixture" switch -C main 1a09dd426cba92745a6eaa3a07e67aef2d20e657
git -C "$T/catalog-fixture" config user.name 'SetupSmith Validation Fixture'
git -C "$T/catalog-fixture" config user.email 'validation-fixture@example.invalid'
export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0="url.file://$T/catalog-fixture/.insteadOf"
export GIT_CONFIG_VALUE_0='https://github.com/ehuerta6/setupsmith.git'
cd "$T/setupsmith"
python3 scripts/setupsmith.py discover --source https://github.com/ehuerta6/setupsmith.git --ref refs/heads/main

python3 scripts/setupsmith.py adopt --source https://github.com/ehuerta6/setupsmith.git --ref refs/heads/main --project "$T/cappy-code" --map .agents/skills/setup-ai=skills/setup-ai --map .codex/skills/ai-config-builder=skills/ai-config-builder --map .codex/skills/project-audit=skills/audit-ai-config --preview-only
python3 scripts/setupsmith.py adopt --source https://github.com/ehuerta6/setupsmith.git --ref refs/heads/main --project "$T/cappy-code" --map .agents/skills/setup-ai=skills/setup-ai --map .codex/skills/ai-config-builder=skills/ai-config-builder --map .codex/skills/project-audit=skills/audit-ai-config
python3 scripts/setupsmith.py adopt --source https://github.com/ehuerta6/setupsmith.git --ref refs/heads/main --project "$T/cappy-hub" --map .agents/skills/setup-ai=skills/setup-ai --preview-only
python3 scripts/setupsmith.py adopt --source https://github.com/ehuerta6/setupsmith.git --ref refs/heads/main --project "$T/cappy-hub" --map .agents/skills/setup-ai=skills/setup-ai
python3 scripts/setupsmith.py install --source https://github.com/ehuerta6/setupsmith.git --ref refs/heads/main --skill audit-ai-config --assistant codex --project "$T/cappy-hub" --preview-only
python3 scripts/setupsmith.py install --source https://github.com/ehuerta6/setupsmith.git --ref refs/heads/main --skill audit-ai-config --assistant codex --project "$T/cappy-hub"
python3 scripts/setupsmith.py check --project "$T/cappy-hub"
python3 scripts/setupsmith.py diff --project "$T/cappy-hub" --skill audit-ai-config
```

The block above is the A-stage sequence only: it discovers, adopts, and installs at revision A, then checks and diffs. Commands requiring approval were run with simulated `INSTALL`, `UPDATE`, `RESTORE`, or `REMOVE` answers in a disposable TTY. A declined answer and a noninteractive write were also attempted and verified to leave the clone unchanged. A direct network-source attempt without the Git rewrite returned `SOURCE_UNAVAILABLE`.

The mirror history was constructed as real commits. Starting at A, B appended `Validation fixture revision B: include supporting-resource and binary-file checks.` to the audit skill, added a support Markdown file containing `Revision B supporting reference.`, and wrote bytes `b'fixture-binary-revision-B' + bytes([0, 255])` to its binary resource. C changed `revision B` to `revision C` in the skill, appended `Validation fixture revision C: selective sync must preserve unselected artifacts.`, changed the reference to `Revision C supporting reference changed.`, changed the binary final byte from 255 to 254, and appended `Validation fixture revision C: independent second managed artifact changed.` to the setup-ai skill. D deleted the audit skill directory with `git rm -r`. These changes test text, new and changed support files, binary content, independent selections, and upstream removal without publishing fixture history.

The B/C/D creation recipe was replayed in a fresh disposable clone at A. At A the audit skill contained only `SKILL.md`; after the recipe the `main` branch contained the B, C, and D commits in order and the fixture worktree was clean. The B step creates the previously absent `assets` directory before writing its binary resource.

To recreate the mirror history, run this after the A-stage install/adoption commands (the commands that modify `$T/cappy-hub`):

```sh
python3 - "$T/catalog-fixture" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
audit = root / 'skills/audit-ai-config'
skill = audit / 'SKILL.md'
skill.write_text(skill.read_text() + '\n\nValidation fixture revision B: include supporting-resource and binary-file checks.\n')
(audit / 'reference.md').write_text('Revision B supporting reference.\n')
(audit / 'assets').mkdir(parents=True, exist_ok=True)
(audit / 'assets/revision.bin').write_bytes(b'fixture-binary-revision-B' + bytes([0, 255]))
PY
git -C "$T/catalog-fixture" add skills/audit-ai-config
git -C "$T/catalog-fixture" commit -m 'test: create controlled catalog revision B'
```

At B, run:

```sh
python3 scripts/setupsmith.py check --project "$T/cappy-hub"
python3 scripts/setupsmith.py diff --project "$T/cappy-hub" --skill audit-ai-config
python3 scripts/setupsmith.py update --project "$T/cappy-hub" --all-safe --preview-only
python3 scripts/setupsmith.py update --project "$T/cappy-hub" --skill audit-ai-config
```

Then create C and run the C-stage checks and selective sync. `--all-safe --preview-only` is a preview showing setup-ai as the only remaining eligible update; leave it pinned at A for the restore fixture:

```sh
python3 - "$T/catalog-fixture" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
audit = root / 'skills/audit-ai-config'
skill = audit / 'SKILL.md'
skill.write_text(skill.read_text().replace('revision B', 'revision C') + 'Validation fixture revision C: selective sync must preserve unselected artifacts.\n')
(audit / 'reference.md').write_text('Revision C supporting reference changed.\n')
binary = audit / 'assets/revision.bin'
binary.write_bytes(b'fixture-binary-revision-C' + bytes([0, 254]))
setup = root / 'skills/setup-ai/SKILL.md'
setup.write_text(setup.read_text() + '\nValidation fixture revision C: independent second managed artifact changed.\n')
PY
git -C "$T/catalog-fixture" add skills/audit-ai-config skills/setup-ai
git -C "$T/catalog-fixture" commit -m 'test: create controlled catalog revision C'
```

```sh
python3 scripts/setupsmith.py check --project "$T/cappy-hub"
python3 scripts/setupsmith.py diff --project "$T/cappy-hub" --skill audit-ai-config
python3 scripts/setupsmith.py update --project "$T/cappy-hub" --skill audit-ai-config
python3 scripts/setupsmith.py check --project "$T/cappy-hub"
python3 scripts/setupsmith.py update --project "$T/cappy-hub" --all-safe --preview-only
python3 scripts/setupsmith.py update --project "$T/cappy-hub" --none --preview-only
```

Prepare a fresh project with the CLI-generated manifest at C, while audit-ai-config is pinned at C and setup-ai remains pinned at A:

```sh
mkdir -p "$T/restore-seed/.setupsmith"
cp "$T/cappy-hub/.setupsmith/manifest.json" "$T/restore-seed/.setupsmith/manifest.json"
git -C "$T/restore-seed" init -b main
git -C "$T/restore-seed" config user.name 'SetupSmith Validation Fixture'
git -C "$T/restore-seed" config user.email 'validation-fixture@example.invalid'
git -C "$T/restore-seed" add .setupsmith/manifest.json
git -C "$T/restore-seed" commit -m 'test: seed pinned manifest for restore'
git clone --local "$T/restore-seed" "$T/restore-clone"
```

Run restore against that fresh clone before adding another target to CappyHub:

```sh
python3 scripts/setupsmith.py restore --project "$T/restore-clone" --preview-only
python3 scripts/setupsmith.py restore --project "$T/restore-clone"
```

Then install the Claude Code file target at C solely for the managed-sibling removal check. Finally create D and run the D-stage check/update/remove commands:

```sh
python3 scripts/setupsmith.py install --source https://github.com/ehuerta6/setupsmith.git --ref refs/heads/main --skill audit-ai-config --assistant claude-code --project "$T/cappy-hub"
git -C "$T/catalog-fixture" rm -r skills/audit-ai-config
git -C "$T/catalog-fixture" commit -m 'test: remove managed skill in controlled revision D'
```

At D, run:

```sh
python3 scripts/setupsmith.py check --project "$T/cappy-hub"
python3 scripts/setupsmith.py diff --project "$T/cappy-hub" --skill audit-ai-config
python3 scripts/setupsmith.py update --project "$T/cappy-hub" --all-safe --preview-only
python3 scripts/setupsmith.py remove --project "$T/cappy-hub" --target skills/audit-ai-config=.agents/skills/audit-ai-config --preview-only
python3 scripts/setupsmith.py remove --project "$T/cappy-hub" --target skills/audit-ai-config=.agents/skills/audit-ai-config
```

This keeps all fixture commits local. The `discover`, install, update, restore, and remove CLI commands in the preceding sequence are run at the stated points in this order: A, B, C, restore snapshot at C, then D.

Representative observed output/status values were: discovery `complete: true` at A; audit check at B `UPSTREAM_UPDATE`; audit check at D `UPSTREAM_REMOVED`; adopted customized legacy directories `UNKNOWN_BASELINE` with `revision: null`; local edit `LOCAL_DIVERGENCE` plus `UPSTREAM_UPDATE`; Codex install target `.agents/skills/audit-ai-config/`; and successful restore `Already restored and verified` on repeat. Binary bytes restored at C were `666978747572652d62696e6172792d7265766973696f6e2d4300fe`. The report’s commit IDs and SHA-256 values identify the exact source and file states used.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_catalog.py
git diff --check
```


## Validation addendum — 2026-10-10

This addendum records later user-observed Codex evidence without changing the historical results above. The original validation used SetupSmith base `1a09dd426cba92745a6eaa3a07e67aef2d20e657` and Codex CLI `0.160.0`; PR #43 subsequently merged the remote-first retrieval changes at `af3a6466400fbacdacc4bbebd0ffbc439d97bc53`.

### Earlier Codex results

- The earlier Codex CLI `0.160.0` discovery diagnostic passed, but its separate model-backed invocation could not reach the model endpoint. This remains the historical result in Phase D.
- A later user-observed Codex CLI `0.160.0` invocation analyzed CappyHub but could not retrieve the catalog because GitHub DNS/network access was denied in that command sandbox. Recommendations that depended on the catalog were correctly withheld. The report in #43 was merged to address the remote-first retrieval guidance; this failure is not retroactively recorded as a pass.

### Later real Codex invocation

The user reports that on 2026-10-10, Codex CLI `0.162.1` successfully ran `$setup-ai` in CappyHub using the SetupSmith revision above. This is user-provided session evidence, not an independently reproduced run.

- Codex inspected the actual CappyHub project, retrieved SetupSmith remotely, and resolved `main` to the immutable commit `af3a6466400fbacdacc4bbebd0ffbc439d97bc53`.
- It used a disposable temporary checkout, read the README, registry, relevant procedures, and catalog entries at the pinned revision, then removed the checkout.
- It generated ADD / KEEP EXISTING / REPLACE / SKIP recommendations in a read-only analysis. CappyHub was not modified and no managed install was attempted.
- The session took 2 minutes 33 seconds and produced more than 20 recommendation rows. The user observed some `git show` errors for catalog paths that exist at the pinned revision. These UX and fidelity observations are recorded without inferring a cause; no independent reproduction established why those commands failed.
- This observation demonstrates a successful model-backed invocation and remote canonical catalog retrieval after the earlier failures. It does not repeat or replace the managed CLI lifecycle evidence in the original report.

### Claude Code availability

Claude Code was unavailable in the validation environment (`claude --version` returned command not found). It was not installed. Native skill discovery and `/setup-ai` invocation therefore remain **BLOCKED / UNAVAILABLE**; placement under `.claude/skills/` in the earlier CLI fixture is only file lifecycle evidence, not native discovery.

### Updated Issue #19 acceptance status

The six criteria below correspond to the issue's acceptance criteria. Status incorporates the original report and the later Codex observation.

| Issue #19 criterion | Status | Current evidence |
| --- | --- | --- |
| Analyze both projects from setup-ai-only bootstrap; produce different, relevant recommendations while preserving existing configuration | PASS | Original disposable-project analysis; later user-observed CappyHub read-only recommendations at the pinned canonical revision |
| Install/adopt in both projects and selectively apply a real upstream skill change | PASS | Original disposable CLI lifecycle evidence, revisions A–C, manifests, and hashes |
| Cover local edits, unknown baselines, conflicts/stale plans, removal, missing files, and offline/source reporting | PASS | Original manual clone and automated fixture evidence |
| Cover multi-target recovery and fresh-clone manifest reconstruction, including unavailable pins and unsupported targets | PASS | Original recovery tests and separate clone restore evidence |
| Verify actual native discovery for both Codex and Claude Code | BLOCKED / UNAVAILABLE | Codex discovery and successful invocation are evidenced; Claude Code runtime was unavailable |
| Run catalog validation and configured CLI checks with reproducible results | PASS | Original report records 99 passing unit tests, catalog validation, and diff check at that validation time |

The later Codex observation strengthens the first criterion and confirms remote retrieval/read-only recommendation behavior for CappyHub. It does not clear the Claude Code portion of the native-discovery criterion. Issue #19 remains open, and the post-MVP dependency gate remains unsatisfied until the outstanding acceptance criterion is resolved and reviewed/integrated.
