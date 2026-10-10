# Managed skill installation

SetupSmith's standalone CLI supports deterministic, project-local installation of selected skills, explicit adoption of existing skills, read-only checks and diffs, explicitly approved safe updates, manifest-based restoration of verified skills, and explicit managed-target removal. These commands do not require an LLM or the `setup-ai` skill. Automatic synchronization is not implemented.

## Commands

Discover a source catalog without changing the project:

```sh
python3 scripts/setupsmith.py discover --source https://github.com/owner/catalog.git
python3 scripts/setupsmith.py discover --source https://github.com/owner/catalog.git --ref refs/heads/main
```

Preview one or more specific skills and selected assistants without prompting or writing:

```sh
python3 scripts/setupsmith.py install \
  --source https://github.com/owner/catalog.git \
  --ref refs/heads/main \
  --skill research-and-compare \
  --skill review-pr \
  --assistant codex \
  --assistant claude-code \
  --project /path/to/project \
  --preview-only
```

Remove `--preview-only` to display the same preview and receive the final prompt. The CLI writes only if the user types `INSTALL` exactly. Any other answer declines the complete batch. A write invocation without a terminal is refused. Each selection is explicit; omitting `--ref` resolves and records the source's advertised default branch. Repeat `--skill` and `--assistant` to select a batch and its targets. The supported assistant values are `codex` and `claude-code`. Use Git's credential helper or SSH agent for private sources; URL credentials and query data are rejected so they cannot enter the manifest or error output.

The preview lists the source locator, configured ref, immutable commit, selected skills, destinations, every added relative file, text content or exact binary bytes, and the proposed manifest entries. The complete preview can be large for skills with many resources. A conflict, invalid catalog, unsupported assistant, or unsafe path stops before approval.

## Destinations and manifest

Project-local destinations follow the researched native layouts:

- Codex: `.agents/skills/<skill-name>/`
- Claude Code: `.claude/skills/<skill-name>/`

The CLI copies each skill directory, including nested and binary resources. It does not execute bundled files or modify `AGENTS.md`, `CLAUDE.md`, or other project instructions. These paths are the documented native layouts; the CLI does not verify runtime discovery. Claude Code runtime verification was unavailable during this batch.

The portable JSON manifest is `.setupsmith/manifest.json`, with schema version `1`:

```json
{
  "schema_version": 1,
  "artifacts": [
    {
      "id": "skills/research-and-compare",
      "source": "https://github.com/owner/catalog.git",
      "configured_ref": "refs/heads/main",
      "revision": "<immutable Git commit>",
      "content_digest": "<sha256 over sorted relative paths and file bytes>",
      "files": {
        "SKILL.md": "<sha256 of file bytes>"
      },
      "targets": [
        {"assistant": "codex", "path": ".agents/skills/research-and-compare", "state": "installed"}
      ]
    }
  ]
}
```

The tree digest includes each UTF-8 relative path and the exact bytes of each regular file in stable path order. Per-file SHA-256 values preserve a comparison baseline for later work. The manifest records source identity separately from `registry.yaml`, which remains catalog status metadata. It contains no machine-absolute paths or embedded URL credentials. SetupSmith does not create a Git commit in the target project.

## Adopting existing skills

`adopt` inspects `.agents/skills/` and `.claude/skills/` as native project destinations. It also lists `.codex/skills/` and `.ai/skills/` as legacy or non-native candidates; finding a directory there does not claim that an assistant discovers it. The initial command reports relative paths, assistant target, content digests, matching canonical identities when the complete file tree matches, existing manifest ownership, and match confidence. Names alone are only candidate hints.

Preview candidates without mapping:

```sh
python3 scripts/setupsmith.py adopt \
  --source https://github.com/owner/catalog.git \
  --project /path/to/project \
  --preview-only
```

Map each selected installation explicitly and review the proposed manifest:

```sh
python3 scripts/setupsmith.py adopt \
  --source https://github.com/owner/catalog.git \
  --ref refs/heads/main \
  --project /path/to/project \
  --map .agents/skills/research=skills/research-and-compare \
  --map .claude/skills/research=skills/research-and-compare
```

Without `--preview-only`, adoption requires typing `INSTALL` exactly in an interactive terminal. It writes only `.setupsmith/manifest.json`; selected skill trees remain at their existing paths and their bytes are not rewritten. Unselected candidates remain unmanaged. Conflicting ownership, duplicate paths, unsafe symlinks, invalid mappings, or files changed after preview stop the operation. Repeating an unchanged adoption is a no-op.

An exact full-tree match to a retrieved canonical skill records `baseline_state: "verified"`, the resolved immutable revision, and per-file baseline hashes. This establishes content identity at that revision, not when or how the existing files were installed. A customized tree or unavailable canonical skill records `baseline_state: "unknown"`, `revision: null`, and observed local hashes. Unknown hashes identify the imported state only; they do not prove canonical history. An unavailable source may leave `configured_ref` null when no ref was supplied or resolved. Unknown-baseline entries are rejected by the installer if a later install would replace or reinterpret the adopted files.

Schema version remains `1`. Existing Issue #11 entries with no `baseline_state` or target `adoption` fields continue to mean verified installations; they are not migrated or reclassified. New adoption targets record `adoption: "adopted"`, while each new artifact entry records its explicit `baseline_state`. An adopted target's `path` is its actual safe relative destination and may have a local directory name different from the canonical artifact ID. Its assistant-specific root must still be one of the supported layouts. Targets marked `installed` keep the canonical destination convention. An artifact may contain both installed and adopted targets when their content has the same verified baseline. `content_digest` and `files` describe the verified canonical baseline for verified entries and observed local content for unknown entries. These fields remain separate from `registry.yaml` catalog status.

## Read-only check and diff

Check every managed target against the immutable recorded baseline and its configured source ref:

```sh
python3 scripts/setupsmith.py check --project /path/to/project
```

Show text patches and binary path digests, optionally for one skill:

```sh
python3 scripts/setupsmith.py diff --project /path/to/project
python3 scripts/setupsmith.py diff --project /path/to/project --skill research-and-compare
```

The manifest determines which artifact and target SetupSmith manages. The filesystem determines the installed content. The CLI refreshes the exact configured ref stored for each artifact and displays its current resolved commit separately from the recorded baseline commit. It does not silently choose a different branch, tag, or latest release. Each target is reported independently, so Codex and Claude Code can have different states.

| State | Meaning |
| --- | --- |
| `CURRENT` | Verified baseline, current upstream, and this target's files match. |
| `UPSTREAM_UPDATE` | The configured upstream tree differs from the verified baseline. |
| `LOCAL_DIVERGENCE` | This target's files or directory structure differ from the recorded baseline or, for unknown baselines, from the observed hashes at adoption. |
| `RECOVERY_INCOMPLETE` | A previous update could not restore this target to its recorded baseline. The report includes the observed state and any preserved recovery path. |
| `MISSING_INSTALLATION` | The recorded destination is absent. |
| `UPSTREAM_REMOVED` | The configured current source no longer contains the skill. Local files are preserved. |
| `UNKNOWN_BASELINE` | No historical canonical revision is claimed; only observed local hashes can be checked. |
| `DESTINATION_CONFLICT` | The destination is unsafe, unreadable, symlinked, or not a skill directory. |
| `UNSUPPORTED_TARGET` | The recorded assistant target is unknown or is a legacy/non-native layout. |
| `SOURCE_UNAVAILABLE` | The configured ref or recorded revision could not be fetched or safely compared. |

States can appear together. For example, a target can have both `UPSTREAM_UPDATE` and `LOCAL_DIVERGENCE`. Text diffs label `Baseline → Upstream` and `Baseline → Local`; binary resources show changed paths and SHA-256 digests. Every resource in the skill tree is compared, not only `SKILL.md`.

The checker does not maintain an offline cache. If the configured source is unavailable, it reports `SOURCE_UNAVAILABLE`, identifies any local changes detectable from manifest hashes, and says that no cache was used. It does not claim the source is current or invent a revision. If no ref was recorded for an unknown-baseline entry, it will not select the source's default branch on the user's behalf.

Checks and diffs do not create a manifest, change installed files, write project instructions, apply updates, or remove upstream-deleted skills. The checker exits with an error for malformed manifest data or when the manifest's claimed verified baseline does not match the recorded immutable source revision.

## Selective updates

`update` uses the manifest's configured source/ref and the checker's verified baseline and local file comparisons. Choose one or more safe artifacts explicitly:

```sh
python3 scripts/setupsmith.py update --project /path/to/project --skill research-and-compare
python3 scripts/setupsmith.py update --project /path/to/project --skill research-and-compare --skill review-pr
```

Use `--all-safe` to select every eligible update or `--none` to select none. The command first prints the check report, the selected revisions and destinations, each added, modified, or removed file, relevant text patches, binary hashes, and manifest fields to update. `--preview-only` prints the complete selection and exits without prompting or writing. Selection is not approval: an applying invocation requires typing `UPDATE` exactly for the whole selected batch. A noninteractive applying invocation is refused.

An artifact is excluded from `--all-safe` when its baseline is unknown, a recorded target is missing, locally changed, unsafe, or unsupported, the source or pinned baseline cannot be verified, the upstream artifact was removed, or any target in its managed target set is unsafe. Requesting an excluded artifact explicitly is refused. A no-update artifact is not selected as work. Upstream removal never deletes an installed skill.

After confirmation, SetupSmith re-resolves each configured ref, checks that its revision, manifest, and every selected destination still match the approved preview, stages and hashes complete trees, then replaces all targets for each selected artifact and advances only those manifest baselines. A changed source ref, destination, or manifest makes the preview stale and refuses application. Repeating an update after the target revision is recorded is a no-op. On an application failure, the CLI verifies and attempts to restore replaced target trees and the prior manifest. It reports the state of every affected target and preserves original backups when safe restoration is blocked. If recovery is incomplete, the schema-1 manifest keeps its prior canonical baseline and adds an optional per-target `recovery` object containing `state: "incomplete"`, the observed filesystem state/digest, and a relative recovery path when a backup remains. This additive observation does not claim canonical provenance. `check` reports `RECOVERY_INCOMPLETE` while the target remains missing or differs from its recorded baseline; a safely reconciled target can be retried, and a successful update clears the recovery marker for its selected targets. Independent artifacts in the approved batch are rolled back where possible and reported individually. This update recovery behavior is separate from managed removal, tracked in #15.

## Restore from a committed manifest

In a fresh project clone, reconstruct missing supported targets from the exact immutable revisions recorded in `.setupsmith/manifest.json`:

```sh
python3 scripts/setupsmith.py restore --project /path/to/project --preview-only
python3 scripts/setupsmith.py restore --project /path/to/project
```

The preview names each artifact, pinned revision, digest, assistant destination, and every file to add. The manifest remains unchanged. The applying command requires typing `RESTORE` in a terminal; noninteractive writes are refused. SetupSmith fetches the recorded commit directly and verifies its complete file tree against the manifest. It never substitutes the configured ref's current revision. If the pinned commit is unavailable, or retrieved content disagrees with recorded hashes, restore reports the conflict and refuses the batch.

Only recorded Codex (`.agents/skills/<name>/`) and Claude Code (`.claude/skills/<name>/`) destinations are reconstructed. Adopted targets keep their recorded safe local path. Existing destinations that match the verified baseline are no-ops; occupied destinations with different content and unsafe paths or symlinks block restoration. Unknown-baseline customizations cannot be reconstructed from canonical history; present files are preserved, and missing custom content must be supplied separately. Legacy and other unsupported targets are reported without being described as restored. Repeating a successful restore does not rewrite files or the manifest.

## Explicit managed removal

Select each exact target independently. The canonical artifact ID identifies the manifest entry; the path is the actual recorded destination, including a custom adopted basename:

```sh
python3 scripts/setupsmith.py remove --project /path/to/project \
  --target skills/research-and-compare=.agents/skills/research-and-compare \
  --preview-only
python3 scripts/setupsmith.py remove --project /path/to/project \
  --target skills/research-and-compare=.agents/skills/research-and-compare
```

Repeat `--target` to select a batch or select another assistant's installation. The preview names the canonical artifact, assistant, exact path, baseline status, current content identity, files/directories, remaining destinations, and complete proposed manifest. `--preview-only` does not write. An applying invocation requires typing `REMOVE` once for the complete batch; declining or running without a terminal changes nothing.

Removal proceeds only when the manifest uniquely owns the exact destination and all recorded file hashes and tree identity still match. Unknown-baseline adopted content can be removed when it still matches its observed adoption identity; the preview explicitly says canonical history is unverified. Locally changed, missing, symlinked, unsafe, unsupported, or unmanaged destinations are refused. A stale manifest or changed destination after approval is refused. Destinations are staged for recovery while the manifest is updated; if staging or manifest replacement fails, SetupSmith restores the original destinations or reports the preserved recovery path. Removing one target leaves the artifact and its metadata when other targets remain. The final target removes only that artifact entry.

### Schema-1 adoption fields

The checker accepts the shared schema-1 contract for explicit adoption. Existing Issue #11 entries without `baseline_state` and target `adoption` fields remain verified installations. Adopted targets carry `adoption: "adopted"`; their target path may have a safe local basename that differs from the canonical artifact ID while remaining in the recorded assistant-specific layout. Installed targets retain the canonical basename. Verified entries identify the canonical commit and full-tree hashes. Unknown-baseline entries have `baseline_state: "unknown"`, `revision: null`, and observed file hashes. A configured ref may be null if it was not known. Observed hashes help detect changes after adoption but do not establish canonical history. This additive contract does not reinterpret older manifests.

## Safety and current limits

- Only skills are managed; agents, rules, templates, and Project Instructions remain reference-only.
- Existing unmanaged destinations, locally changed managed files, invalid source metadata, source symlinks, destination symlinks, and traversal are refused.
- The exact source revision, manifest, and destinations are rechecked after confirmation and before writes. A stale plan is refused.
- New directories are staged and content-verified before placement. A failed installation attempts to remove completed writes and restore the prior manifest, and reports any rollback failure.
- Repeating an unchanged installation is a no-op, including no manifest rewrite.
- Installation refuses a managed skill whose files have changed; `check` reports `LOCAL_DIVERGENCE` and `diff` shows the changes without repairing them.
- Local source paths are accepted only when their Git repository has a credential-free portable `origin` URL; that URL is what the manifest records.
- Global installation and background synchronization are out of scope.
