#!/usr/bin/env python3
"""Lightweight consistency checks for the ai-setup catalog."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


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
    print(f"Catalog validation passed ({len(skills)} skills, {len(list((ROOT / 'agents').glob('*.md')))} agents, {len(list((ROOT / 'project-instructions').glob('*.md')))} Project Instructions).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
