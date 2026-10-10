# Managed skill installation

SetupSmith's standalone CLI supports deterministic, project-local installation of selected skills. Catalog discovery and installation do not require an LLM or the `setup-ai` skill. Sync, existing-skill adoption, updates, and removal are not implemented.

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

## Safety and current limits

- Only skills are managed; agents, rules, templates, and Project Instructions remain reference-only.
- Existing unmanaged destinations, locally changed managed files, invalid source metadata, source symlinks, destination symlinks, and traversal are refused.
- The exact source revision, manifest, and destinations are rechecked after confirmation and before writes. A stale plan is refused.
- New directories are staged and content-verified before placement. A failed installation attempts to remove completed writes and restore the prior manifest, and reports any rollback failure.
- Repeating an unchanged installation is a no-op, including no manifest rewrite.
- Changes to a managed skill after installation are reported as conflicts; the CLI does not repair or update them.
- Local source paths are accepted only when their Git repository has a credential-free portable `origin` URL; that URL is what the manifest records.
- Global installation, existing-skill adoption, source refresh workflows, update/diff, sync, removal, and multi-target update recovery are out of scope.
