#!/usr/bin/env python3
"""Read-only discovery of SetupSmith catalog artifacts from a Git source."""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


class DiscoveryError(Exception):
    pass


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
                value = field.group(2).strip("\"'")
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only SetupSmith catalog discovery")
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("discover", help="discover catalog artifacts from a Git source")
    command.add_argument("--source", required=True, help="Git repository locator")
    command.add_argument("--ref", help="branch, tag, or revision; default is the source's advertised default branch")
    args = parser.parse_args(argv)
    try:
        with tempfile.TemporaryDirectory(prefix="setupsmith-discovery-") as temporary:
            root = Path(temporary) / "source"
            configured, revision, default = resolve_source(args.source, args.ref, root)
            report = discover(root, args.source, configured, revision, default)
            print(json.dumps(report, indent=2))
            return 0 if report["complete"] else 2
    except (DiscoveryError, OSError, UnicodeError) as exc:
        print(json.dumps({"source": args.source, "configured_ref": args.ref or "DEFAULT",
                          "complete": False, "artifacts": [], "errors": [str(exc)], "warnings": []}, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
