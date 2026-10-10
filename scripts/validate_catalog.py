#!/usr/bin/env python3
"""Lightweight consistency checks for the SetupSmith catalog."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def registry_names(section: str) -> set[str]:
    text = (ROOT / "registry.yaml").read_text(encoding="utf-8")
    match = re.search(rf"^{re.escape(section)}:\s*$(.*?)(?=^[A-Za-z_]+:|\Z)", text, re.M | re.S)
    if not match:
        return set()
    return set(re.findall(r"^  ([\w-]+):\s*$", match.group(1), re.M))


def check_registry_metadata(errors: list[str]) -> None:
    text = (ROOT / "registry.yaml").read_text(encoding="utf-8")
    valid_statuses = {"testing", "accepted", "rejected", "default", "replaced"}
    if re.search(r"^\s+(?:source|inspired_by|adapted_from|origin|provenance):", text, re.M):
        fail(errors, "registry contains provenance-only metadata")
    for section in ("skills", "agents", "project_instructions"):
        names = registry_names(section)
        section_match = re.search(rf"^{section}:\s*$(.*?)(?=^[A-Za-z_]+:|\Z)", text, re.M | re.S)
        body = section_match.group(1) if section_match else ""
        for name in names:
            entry = re.search(rf"^  {re.escape(name)}:\s*$(.*?)(?=^  [\w-]+:|\Z)", body, re.M | re.S)
            data = entry.group(1) if entry else ""
            status = re.search(r"^    status:\s*(\S+)\s*$", data, re.M)
            if not status or status.group(1) not in valid_statuses:
                fail(errors, f"registry {section}.{name} has missing or invalid status")


def check_registry_files(errors: list[str], section: str, directory: str, pattern: str) -> None:
    registered = registry_names(section)
    found = {p.parent.name if p.name == "SKILL.md" else p.stem for p in (ROOT / directory).glob(pattern)}
    for name in sorted(registered - found):
        fail(errors, f"registry {section}.{name} has no matching file")
    for name in sorted(found - registered):
        fail(errors, f"{directory}/{name} is not registered")


def main() -> int:
    errors: list[str] = []
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    for path in skills:
        content = path.read_text(encoding="utf-8")
        if not content.startswith("---\n"):
            fail(errors, f"{path.relative_to(ROOT)} has no YAML front matter")
            continue
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            fail(errors, f"{path.relative_to(ROOT)} has unclosed front matter")
            continue
        metadata = parts[1]
        name = re.search(r"^name:\s*([^\s#]+)\s*$", metadata, re.M)
        description = re.search(r"^description:\s*(.*?)\s*$", metadata, re.M)
        expected = path.parent.name
        if not name:
            fail(errors, f"{path.relative_to(ROOT)} is missing a valid name field")
        else:
            skill_name = name.group(1)
            if len(skill_name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_name):
                fail(errors, f"{path.relative_to(ROOT)} name does not meet Agent Skills naming requirements")
            if skill_name != expected:
                fail(errors, f"{path.relative_to(ROOT)} name '{skill_name}' does not match directory '{expected}'")
        if not description or not description.group(1):
            fail(errors, f"{path.relative_to(ROOT)} is missing a valid description field")
        elif len(description.group(1)) > 1024:
            fail(errors, f"{path.relative_to(ROOT)} description exceeds 1024 characters")
        if re.search(r"^metadata:\s*(?:#.*)?$", metadata, re.M):
            fail(errors, f"{path.relative_to(ROOT)} has empty metadata; omit it or provide string key-value fields")

    check_registry_files(errors, "skills", "skills", "*/SKILL.md")
    check_registry_files(errors, "agents", "agents", "*.md")
    check_registry_files(errors, "project_instructions", "project-instructions", "*.md")
    check_registry_metadata(errors)

    # Catch common repository-relative references in catalog and instruction docs.
    docs = list(ROOT.glob("*.md")) + list(ROOT.glob("**/*.md"))
    docs = list(set(docs))
    path_pattern = re.compile(r"(?<![\w./-])((?:skills|agents|rules|templates|project-instructions|scripts|docs)/[\w./-]+\.(?:md|py))(?![\w.-])")
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for ref in path_pattern.findall(text):
            if not (ROOT / ref).is_file():
                fail(errors, f"{doc.relative_to(ROOT)} references missing file '{ref}'")

    if errors:
        print("Catalog validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Catalog validation passed ({len(skills)} skills, {len(registry_names('agents'))} agents, {len(registry_names('project_instructions'))} Project Instructions).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
