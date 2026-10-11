#!/usr/bin/env python3
"""Lightweight consistency checks for the ai-setup catalog."""

import json
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


def check_skill_evaluations(errors: list[str]) -> None:
    """Validate lightweight skill evaluation fixtures and their instruction anchors."""
    fixture_path = ROOT / "evals/skills/cases.json"
    try:
        fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"evals/skills/cases.json is unreadable: {exc}")
        return
    if not isinstance(fixtures, dict):
        fail(errors, "evals/skills/cases.json must contain a JSON object")
        return

    cases = fixtures.get("routing_cases")
    if not isinstance(cases, list) or not cases:
        fail(errors, "skill evaluations need non-empty routing_cases")
        return

    covered: dict[str, set[str]] = {}
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(errors, f"skill evaluation routing case {index + 1} is not an object")
            continue
        target = case.get("target_skill")
        expected = case.get("expected_skill")
        kind = case.get("kind")
        prompt = case.get("prompt")
        if not all(isinstance(value, str) and value for value in (target, expected, kind, prompt)):
            fail(errors, f"skill evaluation routing case {index + 1} needs target_skill, expected_skill, kind, and prompt")
            continue
        if kind not in {"positive", "routing-away"}:
            fail(errors, f"skill evaluation routing case {index + 1} has invalid kind '{kind}'")
        if kind == "positive" and target != expected:
            fail(errors, f"positive skill evaluation case {index + 1} must expect its target skill")
        if kind == "routing-away" and target == expected:
            fail(errors, f"routing-away skill evaluation case {index + 1} must expect another skill")
        for name in {target, expected}:
            if not (ROOT / "skills" / name / "SKILL.md").is_file():
                fail(errors, f"skill evaluation case {index + 1} references missing skill '{name}'")
        covered.setdefault(target, set()).add(kind)

    for skill in ("grill-me", "implement-issue", "review-pr"):
        if covered.get(skill) != {"positive", "routing-away"}:
            fail(errors, f"skill evaluations need positive and routing-away cases for '{skill}'")

    behavior_checks = fixtures.get("behavior_checks")
    if not isinstance(behavior_checks, list) or not behavior_checks:
        fail(errors, "skill evaluations need non-empty behavior_checks")
        return
    checked: set[str] = set()
    for index, check in enumerate(behavior_checks):
        skill = check.get("skill") if isinstance(check, dict) else None
        anchor = check.get("instruction_anchor") if isinstance(check, dict) else None
        if not isinstance(skill, str) or not isinstance(anchor, str) or not anchor:
            fail(errors, f"skill evaluation behavior check {index + 1} needs skill and instruction_anchor")
            continue
        path = ROOT / "skills" / skill / "SKILL.md"
        if not path.is_file():
            fail(errors, f"skill evaluation behavior check {index + 1} references missing skill '{skill}'")
        elif anchor.casefold() not in path.read_text(encoding="utf-8").casefold():
            fail(errors, f"skill evaluation behavior anchor for '{skill}' was not found: {anchor}")
        checked.add(skill)
    for skill in ("grill-me", "implement-issue", "review-pr"):
        if skill not in checked:
            fail(errors, f"skill evaluations need an observable behavior check for '{skill}'")


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
    check_skill_evaluations(errors)

    # Catch common repository-relative references in catalog and instruction docs.
    docs = list(ROOT.glob("*.md")) + list(ROOT.glob("**/*.md"))
    docs = list(set(docs))
    path_pattern = re.compile(r"(?<![\w./-])((?:skills|agents|rules|templates|project-instructions|scripts)/[\w./-]+\.(?:md|py))(?![\w.-])")
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
