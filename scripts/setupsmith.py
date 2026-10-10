#!/usr/bin/env python3
"""Discover catalog artifacts and install explicitly selected skills from Git sources."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath


class DiscoveryError(Exception):
    pass


class InstallError(Exception):
    pass


def validate_source_argument(source: str) -> None:
    """Reject URL credentials before Git can include the locator in an error."""
    from urllib.parse import urlsplit
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", source):
        try:
            parsed = urlsplit(source)
        except ValueError as exc:
            raise InstallError("invalid source URL") from exc
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise InstallError("source URL must not contain embedded credentials or query data")


def validate_skill_metadata(path: Path, directory_name: str) -> list[str]:
    """Validate the required Agent Skills fields using catalog conventions."""
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read {path.name}: {exc}"]

    if not content.startswith("---\n"):
        return ["missing YAML frontmatter"]
    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return ["unclosed YAML frontmatter"]

    metadata = parts[1]
    errors = []
    name = re.search(r"^name:\s*([^\s#]+)\s*$", metadata, re.M)
    description = re.search(r"^description:\s*(.*?)\s*$", metadata, re.M)
    if not name:
        errors.append("missing or invalid name field")
    else:
        skill_name = name.group(1)
        if len(skill_name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_name):
            errors.append("name does not meet Agent Skills naming requirements")
        if skill_name != directory_name:
            errors.append(f"name '{skill_name}' does not match directory '{directory_name}'")
    if not description or not description.group(1):
        errors.append("missing valid description field")
    elif len(description.group(1)) > 1024:
        errors.append("description exceeds 1024 characters")
    return errors


def scalar_without_yaml_comment(value: str) -> str:
    """Remove a YAML comment without treating a # inside quotes as a comment."""
    quote = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if quote and character == quote:
            quote = None
        elif not quote and character in {"'", '"'}:
            quote = character
        elif not quote and character == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise DiscoveryError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def resolve_source(source: str, configured_ref: str | None, checkout: Path) -> tuple[str, str, str]:
    """Fetch source into a temporary checkout and pin discovery to one commit."""
    source_url = str(Path(source).resolve()) if Path(source).exists() else source
    try:
        symref = git("ls-remote", "--symref", source_url, "HEAD")
        default_ref = next((line.split()[1] for line in symref.splitlines()
                            if line.startswith("ref: ") and line.endswith("\tHEAD")), None)
        if configured_ref is None:
            if not default_ref:
                raise DiscoveryError("source did not advertise a default branch; provide --ref")
            chosen_ref = default_ref
        else:
            chosen_ref = configured_ref
        git("init", "-q", str(checkout))
        git("-C", str(checkout), "remote", "add", "origin", source_url)
        git("-C", str(checkout), "fetch", "--quiet", "--no-tags", "origin", chosen_ref)
        commit = git("-C", str(checkout), "rev-parse", "FETCH_HEAD^{commit}")
        git("-C", str(checkout), "checkout", "--quiet", "--detach", commit)
    except DiscoveryError as exc:
        raise DiscoveryError(f"cannot resolve source {source!r} ref {configured_ref or 'DEFAULT'}: {exc}") from exc
    return chosen_ref, commit, default_ref or ""


def parse_registry(path: Path) -> tuple[dict[tuple[str, str], str], list[str]]:
    statuses: dict[tuple[str, str], str] = {}
    issues: list[str] = []
    if not path.exists():
        return statuses, ["registry.yaml is missing; catalog status is unavailable"]
    section = None
    artifact = None
    seen: set[tuple[str, str]] = set()
    valid = {"testing", "accepted", "rejected", "default", "replaced"}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#") or line.startswith("version:"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section = line[:-1]
            artifact = None
            if section not in {"skills", "agents", "rules", "templates", "project_instructions"}:
                issues.append(f"registry.yaml:{number}: unsupported section {section!r}")
            continue
        if section is None:
            issues.append(f"registry.yaml:{number}: entry outside a catalog section")
            continue
        entry = re.fullmatch(r"  ([A-Za-z0-9_-]+):\s*", line)
        field = re.fullmatch(r"    ([A-Za-z0-9_-]+):\s*(.*?)\s*", line)
        if entry:
            artifact = entry.group(1)
            key = (section, artifact)
            if key in seen:
                issues.append(f"registry.yaml:{number}: duplicate entry {section}.{artifact}")
            seen.add(key)
            continue
        if field and artifact:
            if field.group(1) == "status":
                value = scalar_without_yaml_comment(field.group(2)).strip("\"'")
                if value not in valid:
                    issues.append(f"registry.yaml:{number}: invalid status {value!r} for {section}.{artifact}")
                else:
                    statuses[(section, artifact)] = value
            continue
        issues.append(f"registry.yaml:{number}: unsupported registry syntax")
    return statuses, issues


def discover(root: Path, source: str, configured_ref: str, commit: str, default_ref: str) -> dict:
    statuses, warnings = parse_registry(root / "registry.yaml")
    artifacts = []
    errors = []

    def add(kind: str, identity: str, paths: list[Path]) -> None:
        if not paths:
            errors.append(f"invalid {kind} {identity}: no catalog files")
            return
        status = statuses.get((kind, identity))
        artifacts.append({
            "id": f"{kind}/{identity}", "type": kind, "source": source,
            "configured_ref": configured_ref, "revision": commit,
            "catalog_status": status,
            "metadata": "registered" if status else "missing_status",
            "paths": [p.relative_to(root).as_posix() for p in sorted(paths)],
        })

    dirs = {"skills": "skills", "agents": "agents", "rules": "rules", "templates": "templates"}
    for kind, dirname in dirs.items():
        base = root / dirname
        if base.is_symlink():
            errors.append(f"invalid catalog directory: {dirname}/ is a symbolic link")
            continue
        if not base.is_dir():
            errors.append(f"missing catalog directory: {dirname}/")
            continue
        if kind == "skills":
            for child in sorted(base.iterdir()):
                if child.is_symlink():
                    errors.append(f"invalid skill entry: {child.relative_to(root).as_posix()} is a symbolic link")
                    continue
                if not child.is_dir():
                    errors.append(f"unsupported skills entry: {child.relative_to(root).as_posix()} (expected directory)")
                    continue
                skill_file = child / "SKILL.md"
                if not skill_file.is_file():
                    errors.append(f"invalid skill {child.name}: missing SKILL.md")
                    continue
                metadata_errors = validate_skill_metadata(skill_file, child.name)
                if metadata_errors:
                    errors.extend(f"invalid skill metadata {child.name}: {error}" for error in metadata_errors)
                    continue
                resources = []
                for path in child.rglob("*"):
                    if path.is_symlink():
                        errors.append(f"unsupported skill resource: {path.relative_to(root).as_posix()} is a symbolic link")
                    elif path.is_file():
                        resources.append(path)
                add(kind, child.name, resources)
        else:
            for path in base.iterdir():
                if path.is_symlink():
                    errors.append(f"unsupported {kind} entry: {path.relative_to(root).as_posix()} is a symbolic link")
                elif path.is_file() and path.suffix.lower() == ".md":
                    add(kind, path.stem, [path])
                else:
                    errors.append(f"unsupported {kind} entry: {path.relative_to(root).as_posix()}")
    for (kind, identity), status in statuses.items():
        if kind in dirs and not any(a["id"] == f"{kind}/{identity}" for a in artifacts):
            warnings.append(f"registry entry {kind}/{identity} has no discovered artifact (status {status})")
    artifacts.sort(key=lambda a: a["id"])
    return {"source": source, "configured_ref": configured_ref, "resolved_revision": commit,
            "default_ref": default_ref or None, "complete": not errors and not warnings,
            "artifacts": artifacts, "errors": errors, "warnings": warnings}


def tree_identity(skill_dir: Path) -> tuple[str, dict[str, str], list[Path]]:
    """Hash every regular file by relative path and bytes; reject links and special files."""
    files = []
    for path in sorted(skill_dir.rglob("*")):
        relative = path.relative_to(skill_dir)
        if path.is_symlink():
            raise InstallError(f"unsafe source symlink: {relative.as_posix()}")
        if path.is_dir():
            continue
        if not path.is_file() or relative.is_absolute() or ".." in relative.parts:
            raise InstallError(f"unsupported source resource: {relative.as_posix()}")
        if "\\" in relative.as_posix():
            raise InstallError(f"non-portable source path: {relative.as_posix()}")
        files.append(path)
    file_hashes = {}
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(skill_dir).as_posix()
        data = path.read_bytes()
        encoded = relative.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
        file_hashes[relative] = hashlib.sha256(data).hexdigest()
    return digest.hexdigest(), file_hashes, files


def portable_source_locator(source: str) -> str:
    """Return a portable, credential-free source locator for the manifest."""
    candidate = source
    if Path(source).exists():
        try:
            candidate = git("config", "--get", "remote.origin.url", cwd=Path(source).resolve())
        except DiscoveryError as exc:
            raise InstallError("local source has no remote.origin.url; use a canonical Git URL") from exc
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", candidate):
        from urllib.parse import urlsplit
        try:
            parsed = urlsplit(candidate)
        except ValueError as exc:
            raise InstallError("invalid source URL") from exc
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise InstallError("source URL must not contain embedded credentials")
        if not parsed.hostname or "\n" in candidate:
            raise InstallError("invalid source URL")
        return candidate
    if re.fullmatch(r"[A-Za-z0-9_.-]+@[A-Za-z0-9.-]+:[A-Za-z0-9_./-]+(?:\.git)?", candidate):
        return candidate
    raise InstallError("source locator is not portable; provide a credential-free Git URL")


def ensure_no_symlink_components(root: Path, relative: Path) -> None:
    current = root
    for part in relative.parts:
        if part in {"", ".", ".."}:
            raise InstallError(f"unsafe destination path: {relative.as_posix()}")
        current = current / part
        if current.is_symlink():
            raise InstallError(f"destination path contains symlink: {current}")


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": 1, "artifacts": []}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"cannot read manifest {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != 1 or not isinstance(value.get("artifacts"), list):
        raise InstallError("unsupported or invalid .setupsmith/manifest.json")
    for entry in value["artifacts"]:
        if not isinstance(entry, dict) or not re.fullmatch(r"skills/[a-z0-9]+(?:-[a-z0-9]+)*", str(entry.get("id", ""))):
            raise InstallError("manifest contains an invalid artifact identity")
        for key in ("source", "configured_ref", "revision", "content_digest"):
            if not isinstance(entry.get(key), str) or not entry[key]:
                raise InstallError(f"manifest artifact {entry['id']} has an invalid {key}")
        if Path(entry["source"]).is_absolute() or not (
                re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", entry["source"])
                or re.fullmatch(r"[A-Za-z0-9_.-]+@[A-Za-z0-9.-]+:[A-Za-z0-9_./-]+(?:\.git)?", entry["source"])):
            raise InstallError(f"manifest artifact {entry['id']} has a non-portable source locator")
        try:
            portable_source_locator(entry["source"])
        except InstallError as exc:
            raise InstallError(f"manifest artifact {entry['id']} has an invalid source locator") from exc
        if not re.fullmatch(r"[0-9a-f]{40,64}", entry["revision"]):
            raise InstallError(f"manifest artifact {entry['id']} has an invalid source revision")
        if not re.fullmatch(r"[0-9a-f]{64}", entry["content_digest"]):
            raise InstallError(f"manifest artifact {entry['id']} has an invalid content digest")
        files = entry.get("files")
        if not isinstance(files, dict) or not files:
            raise InstallError(f"manifest artifact {entry['id']} has no verified file baseline")
        for relative, digest in files.items():
            if not isinstance(relative, str):
                raise InstallError(f"manifest artifact {entry['id']} contains an invalid file path")
            file_path = PurePosixPath(relative)
            if (file_path.is_absolute() or ".." in file_path.parts or "\\" in relative
                    or not re.fullmatch(r"[0-9a-f]{64}", str(digest))):
                raise InstallError(f"manifest artifact {entry['id']} contains an unsafe file baseline")
        targets = entry.get("targets")
        if not isinstance(targets, list) or not targets:
            raise InstallError(f"manifest artifact {entry['id']} has no managed targets")
        for target in targets:
            if not isinstance(target, dict):
                raise InstallError(f"manifest artifact {entry['id']} contains an invalid target")
            assistant = target.get("assistant")
            relative_path = target.get("path")
            if not isinstance(assistant, str) or not isinstance(relative_path, str):
                raise InstallError(f"manifest artifact {entry['id']} contains an invalid target")
            expected_prefix = {"codex": ".agents/skills", "claude-code": ".claude/skills"}.get(assistant)
            target_path = PurePosixPath(relative_path)
            if (not expected_prefix or target_path.is_absolute() or ".." in target_path.parts or "\\" in relative_path
                    or target_path.as_posix() != f"{expected_prefix}/{entry['id'].split('/', 1)[1]}"
                    or target.get("state") != "installed"):
                raise InstallError(f"manifest artifact {entry['id']} contains an unsafe target")
    return value


def file_hashes_on_disk(directory: Path) -> dict[str, str]:
    result = {}
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        if path.is_symlink():
            raise InstallError(f"installed destination contains symlink: {relative.as_posix()}")
        if path.is_file():
            result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def render_preview(source: str, configured_ref: str, revision: str, plans: list[dict],
                   targets: list[str], root: Path, manifest_path: Path, manifest: dict) -> str:
    lines = ["SetupSmith install preview", f"Source: {source}", f"Configured ref: {configured_ref}",
             f"Immutable revision: {revision}",
             f"Selected skills: {', '.join(plan['skill'] for plan in plans)}",
             f"Assistant targets: {', '.join(targets)}", f"Project: {root}", "Planned files:"]
    for plan in plans:
        lines.append(f"Skill {plan['artifact_id']} (sha256 {plan['digest']}):")
        for target, relative, _, state in plan["destinations"]:
            lines.append(f"  {relative}/ ({state})")
            if state != "new":
                continue
            for path in plan["files"]:
                path_relative = path.relative_to(plan["skill_dir"]).as_posix()
                data = path.read_bytes()
                lines.append(f"    + {relative / path_relative} ({len(data)} bytes)")
                try:
                    rendered = data.decode("utf-8")
                except UnicodeDecodeError:
                    rendered = f"[binary bytes, hex: {data.hex()}]"
                lines.append(f"      content: {json.dumps(rendered, ensure_ascii=True)}")
    lines.append(f"Manifest: {Path('.setupsmith/manifest.json')}")
    if any(state.startswith("conflict") for plan in plans for _, _, _, state in plan["destinations"]):
        lines.append("Manifest: unchanged because the plan contains conflicts.")
    else:
        proposed_entries = []
        for plan in plans:
            if plan["existing_entry"]:
                lines.append("Existing manifest entry: present")
            managed_targets = list((plan["existing_entry"] or {}).get("targets", []))
            for target, relative, _, _ in plan["destinations"]:
                if not any(item.get("assistant") == target and item.get("path") == relative.as_posix() for item in managed_targets):
                    managed_targets.append({"assistant": target, "path": relative.as_posix(), "state": "installed"})
            proposed_entries.append({"id": plan["artifact_id"], "source": source,
                                     "configured_ref": configured_ref, "revision": revision,
                                     "content_digest": plan["digest"], "files": plan["hashes"],
                                     "targets": sorted(managed_targets, key=lambda item: item["assistant"])})
        lines.append("Proposed manifest entries:")
        lines.append(json.dumps(proposed_entries, indent=2, sort_keys=True))
    return "\n".join(lines)


def install(args: argparse.Namespace) -> int:
    if len(set(args.assistant)) != len(args.assistant):
        raise InstallError("assistant targets must be selected only once")
    if not args.skill or len(set(args.skill)) != len(args.skill):
        raise InstallError("select one or more distinct skills")
    if not sys.stdin.isatty() and not args.preview_only:
        raise InstallError("interactive confirmation is required; rerun in a terminal (or use --preview-only)")
    with tempfile.TemporaryDirectory(prefix="setupsmith-install-source-") as temporary:
        source_root = Path(temporary) / "source"
        configured, revision, default_ref = resolve_source(args.source, args.ref, source_root)
        report = discover(source_root, args.source, configured, revision, default_ref)
        source_locator = portable_source_locator(args.source)
        project_arg = Path(args.project).expanduser()
        if not project_arg.is_dir():
            raise InstallError(f"target project does not exist: {args.project}")
        try:
            root = Path(git("rev-parse", "--show-toplevel", cwd=project_arg)).resolve()
        except DiscoveryError as exc:
            raise InstallError("target must be inside a Git project") from exc
        manifest_rel = Path(".setupsmith") / "manifest.json"
        ensure_no_symlink_components(root, manifest_rel)
        manifest_path = root / manifest_rel
        manifest = load_manifest(manifest_path)
        plans = []
        conflicts = []
        for skill in args.skill:
            artifact_id = f"skills/{skill}"
            found = any(item["id"] == artifact_id for item in report["artifacts"])
            relevant_errors = [error for error in report["errors"]
                               if f"skills/{skill}/" in error or f"skills/{skill} " in error
                               or f"skill {skill}:" in error or f"skill metadata {skill}:" in error]
            if relevant_errors:
                raise InstallError(f"invalid selected skill {skill}: " + "; ".join(relevant_errors))
            if not found:
                raise InstallError(f"unknown or invalid skill: {skill}")
            skill_dir = source_root / "skills" / skill
            digest, hashes, files = tree_identity(skill_dir)
            existing_entry = next((entry for entry in manifest["artifacts"] if entry.get("id") == artifact_id), None)
            destinations = []
            for target in args.assistant:
                prefix = ".agents/skills" if target == "codex" else ".claude/skills"
                relative = Path(prefix) / skill
                ensure_no_symlink_components(root, relative)
                destination = root / relative
                if destination.exists():
                    managed = next((item for item in (existing_entry or {}).get("targets", [])
                                    if item.get("assistant") == target and item.get("path") == relative.as_posix()), None)
                    if not managed:
                        state = "conflict (occupied unmanaged)"
                        conflicts.append(f"occupied unmanaged destination: {relative.as_posix()}")
                    elif file_hashes_on_disk(destination) != existing_entry.get("files"):
                        state = "conflict (local modification)"
                        conflicts.append(f"managed destination has local changes: {relative.as_posix()}")
                    elif existing_entry.get("content_digest") != digest or existing_entry.get("revision") != revision:
                        state = "conflict (update unsupported)"
                        conflicts.append(f"managed destination differs from requested source; updates are not supported: {relative.as_posix()}")
                    else:
                        state = "unchanged (no-op)"
                else:
                    state = "new"
                destinations.append((target, relative, destination, state))
            plans.append({"skill": skill, "artifact_id": artifact_id, "skill_dir": skill_dir,
                          "digest": digest, "hashes": hashes, "files": files,
                          "existing_entry": existing_entry, "destinations": destinations})
        preview = render_preview(source_locator, configured, revision, plans,
                                 args.assistant, root, manifest_path, manifest)
        print(preview)
        if conflicts:
            print("Conflicts: " + "; ".join(conflicts) + ". No project files changed.")
            return 2
        if args.preview_only:
            print("Preview only; no project files changed.")
            return 0
        try:
            answer = input("Type INSTALL to apply exactly this plan, or anything else to decline: ")
        except EOFError:
            print("Declined; no project files changed.")
            return 0
        if answer != "INSTALL":
            print("Declined; no project files changed.")
            return 0
        # Re-resolve and re-check source and destinations immediately before the first write.
        latest_ref, latest_revision, _ = resolve_source(args.source, args.ref, Path(temporary) / "recheck")
        if latest_ref != configured or latest_revision != revision:
            raise InstallError("stale preview: source revision changed; preview again")
        ensure_no_symlink_components(root, manifest_rel)
        current_manifest = load_manifest(manifest_path)
        if current_manifest != manifest:
            raise InstallError("stale preview: manifest changed; preview again")
        for plan in plans:
            for _, relative, destination, state in plan["destinations"]:
                ensure_no_symlink_components(root, relative)
                if state == "new" and destination.exists():
                    raise InstallError(f"stale preview: destination is now occupied: {relative.as_posix()}")
                if state != "new" and (not destination.exists() or file_hashes_on_disk(destination) != plan["hashes"]):
                    raise InstallError(f"stale preview: managed files changed: {relative.as_posix()}")
        if all(plan["existing_entry"]
               and plan["existing_entry"].get("source") == source_locator
               and plan["existing_entry"].get("configured_ref") == configured
               and all(state == "unchanged (no-op)" for _, _, _, state in plan["destinations"])
               for plan in plans):
            print("Already installed and unchanged; no files or manifest rewritten.")
            return 0
        completed = []
        staging_paths = []
        manifest_temp = None
        old_manifest_bytes = manifest_path.read_bytes() if manifest_path.exists() else None
        manifest_dir = root / ".setupsmith"
        manifest_dir.mkdir(exist_ok=True)
        try:
            entries = []
            for plan in plans:
                for target, relative, destination, state in plan["destinations"]:
                    if state == "unchanged (no-op)":
                        continue
                    ensure_no_symlink_components(root, relative)
                    staging = destination.parent / f".{destination.name}.setupsmith-{os.getpid()}"
                    if staging.exists():
                        raise InstallError(f"staging path already exists: {staging}")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    ensure_no_symlink_components(root, relative)
                    staging_paths.append(staging)
                    shutil.copytree(plan["skill_dir"], staging, symlinks=False)
                    if tree_identity(staging)[0] != plan["digest"]:
                        raise InstallError(f"staged content verification failed: {relative.as_posix()}")
                    os.replace(staging, destination)
                    completed.append(destination)
                targets = list((plan["existing_entry"] or {}).get("targets", []))
                for target, relative, _, _ in plan["destinations"]:
                    if not any(item.get("assistant") == target and item.get("path") == relative.as_posix() for item in targets):
                        targets.append({"assistant": target, "path": relative.as_posix(), "state": "installed"})
                entries.append({"id": plan["artifact_id"], "source": source_locator,
                                "configured_ref": configured, "revision": revision,
                                "content_digest": plan["digest"], "files": plan["hashes"],
                                "targets": sorted(targets, key=lambda item: item["assistant"])})
            changed_ids = {entry["id"] for entry in entries}
            artifacts = [item for item in manifest["artifacts"] if item.get("id") not in changed_ids]
            artifacts.extend(entries)
            updated = {"schema_version": 1, "artifacts": sorted(artifacts, key=lambda item: item["id"])}
            data = (json.dumps(updated, indent=2, sort_keys=True) + "\n").encode("utf-8")
            ensure_no_symlink_components(root, manifest_rel)
            file_descriptor, temp_name = tempfile.mkstemp(prefix=".manifest-", suffix=".tmp", dir=manifest_dir)
            manifest_temp = Path(temp_name)
            with os.fdopen(file_descriptor, "wb") as temporary_manifest:
                temporary_manifest.write(data)
                temporary_manifest.flush()
                os.fsync(temporary_manifest.fileno())
            os.replace(manifest_temp, manifest_path)
            manifest_temp = None
        except Exception as exc:
            cleanup_failures = []
            if manifest_temp and manifest_temp.exists():
                try:
                    manifest_temp.unlink()
                except OSError as cleanup_error:
                    cleanup_failures.append(f"could not remove manifest staging file {manifest_temp}: {cleanup_error}")
            for staging in staging_paths:
                if staging.exists():
                    try:
                        shutil.rmtree(staging)
                    except OSError as cleanup_error:
                        cleanup_failures.append(f"could not remove staging path {staging}: {cleanup_error}")
            for destination in reversed(completed):
                try:
                    shutil.rmtree(destination)
                except OSError as cleanup_error:
                    cleanup_failures.append(f"could not roll back {destination}: {cleanup_error}")
            try:
                if old_manifest_bytes is None:
                    manifest_path.unlink(missing_ok=True)
                else:
                    manifest_path.write_bytes(old_manifest_bytes)
            except OSError as cleanup_error:
                cleanup_failures.append(f"could not restore manifest {manifest_path}: {cleanup_error}")
            detail = "; ".join(cleanup_failures)
            raise InstallError(f"installation failed: {exc}" + (f"; partial state: {detail}" if detail else "; completed writes were rolled back")) from exc
        print("Installed successfully: " + ", ".join(plan["skill"] for plan in plans))
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discover and install selected SetupSmith catalog skills")
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("discover", help="discover catalog artifacts from a Git source")
    command.add_argument("--source", required=True, help="Git repository locator")
    command.add_argument("--ref", help="branch, tag, or revision; default is the source's advertised default branch")
    install_command = sub.add_parser("install", help="preview and explicitly approve selected skill installation")
    install_command.add_argument("--source", required=True, help="canonical Git repository locator")
    install_command.add_argument("--ref", help="configured branch, tag, or revision; defaults to source branch")
    install_command.add_argument("--skill", required=True, action="append", help="skill directory name; repeat for a batch")
    install_command.add_argument("--assistant", required=True, action="append", choices=("codex", "claude-code"),
                                 help="assistant target; repeat to select both")
    install_command.add_argument("--project", required=True, help="existing target Git project")
    install_command.add_argument("--preview-only", action="store_true", help="show the plan without prompting or writing")
    args = parser.parse_args(argv)
    try:
        validate_source_argument(args.source)
        if args.command == "install":
            return install(args)
        with tempfile.TemporaryDirectory(prefix="setupsmith-discovery-") as temporary:
            root = Path(temporary) / "source"
            configured, revision, default = resolve_source(args.source, args.ref, root)
            report = discover(root, args.source, configured, revision, default)
            print(json.dumps(report, indent=2))
            return 0 if report["complete"] else 2
    except InstallError as exc:
        print(f"setupsmith: {exc}", file=sys.stderr)
        return 2
    except (DiscoveryError, OSError, UnicodeError) as exc:
        print(json.dumps({"source": args.source, "configured_ref": args.ref or "DEFAULT",
                          "complete": False, "artifacts": [], "errors": [str(exc)], "warnings": []}, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
