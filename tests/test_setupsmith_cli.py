import json
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "setupsmith.py"
SPEC = importlib.util.spec_from_file_location("setupsmith", SCRIPT)
SETUPSMITH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SETUPSMITH)


class CatalogDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "catalog"
        self.root.mkdir()
        (self.root / "registry.yaml").write_text(
            "version: 0.1.0\nskills:\n  guide:\n    status: testing # active\n"
            "agents:\n  helper:\n    status: 'accepted' # reviewed\n",
            encoding="utf-8",
        )
        (self.root / "skills" / "guide" / "references").mkdir(parents=True)
        (self.root / "skills" / "guide" / "SKILL.md").write_text(
            "---\nname: guide\ndescription: A guide skill for discovery tests.\n---\n",
            encoding="utf-8",
        )
        (self.root / "skills" / "guide" / "references" / "detail.md").write_text("resource", encoding="utf-8")
        (self.root / "agents").mkdir()
        (self.root / "agents" / "helper.md").write_text("agent", encoding="utf-8")
        (self.root / "rules").mkdir()
        (self.root / "rules" / "local.md").write_text("rule", encoding="utf-8")
        (self.root / "templates").mkdir()
        (self.root / "templates" / "unregistered.md").write_text("template", encoding="utf-8")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.commit = self.git("rev-parse", "HEAD")

    def tearDown(self):
        self.temporary.cleanup()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True).strip()

    def run_discovery(self, *extra):
        result = subprocess.run(["python3", str(SCRIPT), "discover", "--source", str(self.root), *extra],
                                cwd=self.root.parent, text=True, capture_output=True)
        return result.returncode, json.loads(result.stdout) if result.stdout else None

    def test_discovers_current_kinds_resources_and_registry_status(self):
        code, report = self.run_discovery()
        self.assertEqual(code, 0, report)
        self.assertEqual(report["resolved_revision"], self.commit)
        self.assertEqual(report["configured_ref"], "refs/heads/main")
        found = {item["id"]: item for item in report["artifacts"]}
        self.assertEqual(set(found), {"skills/guide", "agents/helper", "rules/local", "templates/unregistered"})
        self.assertEqual(found["skills/guide"]["catalog_status"], "testing")
        self.assertEqual(found["agents/helper"]["catalog_status"], "accepted")
        self.assertEqual(found["rules/local"]["metadata"], "missing_status")
        self.assertIn("skills/guide/references/detail.md", found["skills/guide"]["paths"])
        self.assertIsNone(found["templates/unregistered"]["catalog_status"])

    def test_explicit_tag_and_revision_are_reported_as_resolved_commit(self):
        self.git("tag", "v1")
        code, report = self.run_discovery("--ref", "refs/tags/v1")
        self.assertEqual(code, 0, report)
        self.assertEqual(report["configured_ref"], "refs/tags/v1")
        self.assertEqual(report["resolved_revision"], self.commit)
        code, report = self.run_discovery("--ref", self.commit)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["configured_ref"], self.commit)
        self.assertEqual(report["resolved_revision"], self.commit)

    def test_missing_registry_is_explicitly_reported(self):
        (self.root / "registry.yaml").unlink()
        self.git("add", "-u")
        self.git("commit", "-qm", "without registry")
        code, report = self.run_discovery()
        self.assertEqual(code, 2)
        self.assertFalse(report["complete"])
        self.assertTrue(any("registry.yaml is missing" in warning for warning in report["warnings"]))

    def test_symlinked_resources_are_reported_without_following_them(self):
        outside = Path(self.temporary.name) / "outside-secret.md"
        outside.write_text("do not inspect", encoding="utf-8")
        resource = self.root / "skills" / "guide" / "references" / "outside.md"
        os.symlink(outside, resource)
        self.git("add", ".")
        self.git("commit", "-qm", "symlink resource")
        code, report = self.run_discovery()
        self.assertEqual(code, 2)
        self.assertFalse(report["complete"])
        self.assertTrue(any("is a symbolic link" in error for error in report["errors"]))
        self.assertNotIn("do not inspect", json.dumps(report))

    def test_invalid_entry_and_registry_status_make_partial_discovery(self):
        (self.root / "skills" / "broken").mkdir()
        (self.root / "skills" / "broken" / "README.md").write_text("invalid skill", encoding="utf-8")
        (self.root / "registry.yaml").write_text("skills:\n  broken:\n    status: unknown\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "invalid")
        code, report = self.run_discovery()
        self.assertEqual(code, 2)
        self.assertFalse(report["complete"])
        self.assertTrue(any("missing SKILL.md" in error for error in report["errors"]))
        self.assertTrue(any("invalid status" in warning for warning in report["warnings"]))

    def test_invalid_skill_metadata_is_reported_as_incomplete(self):
        skill_file = self.root / "skills" / "guide" / "SKILL.md"
        cases = [
            ("missing frontmatter", "name: guide\ndescription: Missing delimiters.\n", "frontmatter"),
            ("unclosed frontmatter", "---\nname: guide\ndescription: Missing closing delimiter.\n", "unclosed"),
            ("missing description", "---\nname: guide\n---\n", "description field"),
            ("mismatched name", "---\nname: other\ndescription: Mismatched directory.\n---\n", "does not match directory"),
            ("invalid name", "---\nname: Guide\ndescription: Invalid naming.\n---\n", "naming requirements"),
        ]
        for label, content, expected_error in cases:
            with self.subTest(label=label):
                skill_file.write_text(content, encoding="utf-8")
                self.git("add", "skills/guide/SKILL.md")
                self.git("commit", "-qm", label)
                code, report = self.run_discovery()
                self.assertEqual(code, 2, report)
                self.assertFalse(report["complete"])
                self.assertNotIn("skills/guide", {item["id"] for item in report["artifacts"]})
                self.assertTrue(any(
                    "invalid skill metadata guide" in error and expected_error in error
                    for error in report["errors"]
                ), report["errors"])

    def test_invalid_ref_and_unavailable_source_are_errors(self):
        code, report = self.run_discovery("--ref", "missing-ref")
        self.assertEqual(code, 2)
        self.assertFalse(report["complete"])
        self.assertIn("cannot resolve source", report["errors"][0])
        result = subprocess.run(["python3", str(SCRIPT), "discover", "--source", str(self.root / "absent")],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot resolve source", json.loads(result.stdout)["errors"][0])

    def test_discovery_does_not_write_to_target_project(self):
        target = Path(self.temporary.name) / "target"
        target.mkdir()
        before = set(target.iterdir())
        result = subprocess.run(["python3", str(SCRIPT), "discover", "--source", str(self.root)],
                                cwd=target, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(set(target.iterdir()), before)


class SkillInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.source = self.base / "catalog"
        (self.source / "skills" / "guide" / "references").mkdir(parents=True)
        (self.source / "skills" / "guide" / "SKILL.md").write_text(
            "---\nname: guide\ndescription: Fixture installer skill.\n---\nBody.\n", encoding="utf-8")
        (self.source / "skills" / "guide" / "references" / "nested").mkdir()
        (self.source / "skills" / "guide" / "references" / "nested" / "blob.bin").write_bytes(b"\x00\xff\x10")
        (self.source / "skills" / "extra").mkdir()
        (self.source / "skills" / "extra" / "SKILL.md").write_text(
            "---\nname: extra\ndescription: Second fixture skill.\n---\nExtra.\n", encoding="utf-8")
        (self.source / "registry.yaml").write_text("skills:\n  guide:\n    status: testing\n", encoding="utf-8")
        for catalog_dir in ("agents", "rules", "templates"):
            path = self.source / catalog_dir
            path.mkdir()
            (path / "fixture.md").write_text("reference-only fixture\n", encoding="utf-8")
        self.git(self.source, "init", "-q", "-b", "main")
        self.git(self.source, "config", "user.name", "Fixture")
        self.git(self.source, "config", "user.email", "fixture@example.invalid")
        self.git(self.source, "remote", "add", "origin", "https://example.invalid/canonical/catalog.git")
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-qm", "fixture")
        self.project = self.base / "project"
        self.project.mkdir()
        self.git(self.project, "init", "-q", "-b", "main")
        self.git(self.project, "config", "user.name", "Fixture")
        self.git(self.project, "config", "user.email", "fixture@example.invalid")
        (self.project / "AGENTS.md").write_text("project owned\n", encoding="utf-8")
        self.git(self.project, "add", "AGENTS.md")
        self.git(self.project, "commit", "-qm", "project")

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def git(cwd, *args):
        return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()

    def run_install(self, response="", preview=False, skills=("guide",), assistants=("codex", "claude-code")):
        output = io.StringIO()
        errors = io.StringIO()

        class InteractiveInput(io.StringIO):
            def isatty(self):
                return True

        arguments = ["install", "--source", str(self.source)]
        for skill in skills:
            arguments.extend(["--skill", skill])
        for assistant in assistants:
            arguments.extend(["--assistant", assistant])
        arguments.extend(["--project", str(self.project)])
        if preview:
            arguments.append("--preview-only")
        with patch.object(sys, "stdin", InteractiveInput(response)), redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(arguments)
        return code, output.getvalue() + errors.getvalue()

    def test_preview_decline_and_confirmed_install_preserve_full_tree(self):
        code, preview = self.run_install(preview=True)
        self.assertEqual(code, 0)
        self.assertIn("Immutable revision:", preview)
        self.assertIn(".agents/skills/guide/references/nested/blob.bin", preview)
        self.assertFalse((self.project / ".agents").exists())
        self.assertFalse((self.project / ".setupsmith").exists())
        code, declined = self.run_install("no\n")
        self.assertEqual(code, 0)
        self.assertIn("Declined", declined)
        self.assertFalse((self.project / ".agents").exists())
        code, installed = self.run_install("INSTALL\n")
        self.assertEqual(code, 0, installed)
        for relative in (".agents/skills/guide", ".claude/skills/guide"):
            self.assertEqual((self.project / relative / "references/nested/blob.bin").read_bytes(), b"\x00\xff\x10")
        self.assertEqual((self.project / "AGENTS.md").read_text(encoding="utf-8"), "project owned\n")
        manifest_path = self.project / ".setupsmith/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        serialized = manifest_path.read_text(encoding="utf-8")
        entry = manifest["artifacts"][0]
        self.assertEqual(entry["id"], "skills/guide")
        self.assertEqual(entry["revision"], self.git(self.source, "rev-parse", "HEAD"))
        self.assertRegex(entry["content_digest"], r"^[a-f0-9]{64}$")
        self.assertEqual({t["assistant"] for t in entry["targets"]}, {"codex", "claude-code"})
        self.assertNotIn(str(self.base), serialized)
        self.assertNotIn("token", serialized.lower())
        before_files = {p.relative_to(self.project).as_posix(): p.read_bytes()
                        for p in self.project.rglob("*") if p.is_file()}
        before_manifest = manifest_path.stat().st_mtime_ns
        code, repeated = self.run_install("INSTALL\n")
        self.assertEqual(code, 0, repeated)
        after_files = {p.relative_to(self.project).as_posix(): p.read_bytes()
                       for p in self.project.rglob("*") if p.is_file()}
        self.assertEqual(before_files, after_files)
        self.assertEqual(before_manifest, manifest_path.stat().st_mtime_ns)

    def test_unmanaged_destination_and_local_modification_are_refused(self):
        occupied = self.project / ".agents/skills/guide"
        occupied.mkdir(parents=True)
        (occupied / "SKILL.md").write_text("owned\n", encoding="utf-8")
        code, message = self.run_install("INSTALL\n")
        self.assertEqual(code, 2)
        self.assertIn("occupied unmanaged", message)
        self.assertEqual((occupied / "SKILL.md").read_text(encoding="utf-8"), "owned\n")

    def test_destination_symlink_escape_is_refused(self):
        outside = self.base / "outside"
        outside.mkdir()
        os.symlink(outside, self.project / ".agents")
        code, message = self.run_install("INSTALL\n")
        self.assertEqual(code, 2)
        self.assertIn("contains symlink", message)
        self.assertEqual(list(outside.iterdir()), [])

    def test_noninteractive_write_is_refused(self):
        args = ["install", "--source", str(self.source), "--skill", "guide",
                "--assistant", "codex", "--project", str(self.project)]
        with patch.object(sys, "stdin", io.StringIO("")), redirect_stderr(io.StringIO()) as errors:
            code = SETUPSMITH.main(args)
        self.assertEqual(code, 2)
        self.assertIn("interactive confirmation", errors.getvalue())
        self.assertFalse((self.project / ".agents").exists())

    def test_multiple_selected_skills_share_one_approval_batch(self):
        code, output = self.run_install("INSTALL\n", skills=("guide", "extra"))
        self.assertEqual(code, 0, output)
        self.assertIn("Selected skills: guide, extra", output)
        manifest = json.loads((self.project / ".setupsmith/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual({entry["id"] for entry in manifest["artifacts"]}, {"skills/guide", "skills/extra"})
        self.assertTrue((self.project / ".agents/skills/extra/SKILL.md").is_file())

    def test_assistant_selection_leaves_other_native_destination_untouched(self):
        code, output = self.run_install("INSTALL\n", assistants=("codex",))
        self.assertEqual(code, 0, output)
        self.assertTrue((self.project / ".agents/skills/guide/SKILL.md").is_file())
        self.assertFalse((self.project / ".claude").exists())
        manifest = json.loads((self.project / ".setupsmith/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([target["assistant"] for target in manifest["artifacts"][0]["targets"]], ["codex"])

    def test_modified_managed_files_are_refused(self):
        code, output = self.run_install("INSTALL\n")
        self.assertEqual(code, 0, output)
        changed = self.project / ".agents/skills/guide/references/nested/blob.bin"
        changed.write_bytes(b"local change")
        code, message = self.run_install("INSTALL\n", skills=("guide",))
        self.assertEqual(code, 2)
        self.assertIn("local changes", message)
        self.assertEqual(changed.read_bytes(), b"local change")

    def test_source_traversal_name_is_refused(self):
        code, message = self.run_install("INSTALL\n", skills=("../AGENTS.md",))
        self.assertEqual(code, 2)
        self.assertIn("invalid skill", message)
        self.assertEqual((self.project / "AGENTS.md").read_text(encoding="utf-8"), "project owned\n")

    def test_catalog_registry_status_does_not_gate_skill_installation(self):
        (self.source / "registry.yaml").unlink()
        self.git(self.source, "add", "-u")
        self.git(self.source, "commit", "-qm", "without registry")
        code, output = self.run_install("INSTALL\n", skills=("guide",))
        self.assertEqual(code, 0, output)
        self.assertTrue((self.project / ".agents/skills/guide/SKILL.md").is_file())

    def test_failed_file_write_rolls_back_without_manifest_success(self):
        original_replace = os.replace

        def fail_destination(source, destination):
            if str(destination).endswith("/.agents/skills/guide"):
                raise OSError("injected rename failure")
            return original_replace(source, destination)

        with patch.object(SETUPSMITH.os, "replace", side_effect=fail_destination):
            code, message = self.run_install("INSTALL\n")
        self.assertEqual(code, 2)
        self.assertIn("injected rename failure", message)
        self.assertFalse((self.project / ".agents/skills/guide").exists())
        self.assertFalse((self.project / ".setupsmith/manifest.json").exists())

    def test_destination_change_after_preview_is_refused(self):
        def create_occupied_destination(_prompt):
            occupied = self.project / ".agents/skills/guide"
            occupied.mkdir(parents=True)
            (occupied / "SKILL.md").write_text("new local content", encoding="utf-8")
            return "INSTALL"

        output = io.StringIO()
        errors = io.StringIO()
        class InteractiveInput(io.StringIO):
            def isatty(self):
                return True
        args = ["install", "--source", str(self.source), "--skill", "guide",
                "--assistant", "codex", "--project", str(self.project)]
        with patch.object(sys, "stdin", InteractiveInput("")), patch("builtins.input", side_effect=create_occupied_destination), redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(args)
        self.assertEqual(code, 2)
        self.assertIn("stale preview", errors.getvalue())
        self.assertEqual((self.project / ".agents/skills/guide/SKILL.md").read_text(encoding="utf-8"), "new local content")

    def test_source_revision_change_after_preview_is_refused(self):
        def change_source(_prompt):
            (self.source / "catalog-change.txt").write_text("changed after preview\n", encoding="utf-8")
            self.git(self.source, "add", "catalog-change.txt")
            self.git(self.source, "commit", "-qm", "source changed")
            return "INSTALL"

        output = io.StringIO()
        errors = io.StringIO()
        class InteractiveInput(io.StringIO):
            def isatty(self):
                return True
        args = ["install", "--source", str(self.source), "--skill", "guide",
                "--assistant", "codex", "--project", str(self.project)]
        with patch.object(sys, "stdin", InteractiveInput("")), patch("builtins.input", side_effect=change_source), redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(args)
        self.assertEqual(code, 2)
        self.assertIn("source revision changed", errors.getvalue())
        self.assertFalse((self.project / ".agents").exists())
        self.assertFalse((self.project / ".setupsmith").exists())

    def test_malformed_manifest_shapes_are_refused_without_tracebacks(self):
        manifest_path = self.project / ".setupsmith/manifest.json"
        manifest_path.parent.mkdir()
        entry = {
                "id": "skills/guide", "source": "https://example.invalid/catalog.git",
                "configured_ref": "refs/heads/main", "revision": "a" * 40,
                "content_digest": "b" * 64, "files": {"SKILL.md": "c" * 64},
                "targets": [{"assistant": "codex", "path": None, "state": "installed"}],
            }
        malformed = ["null", json.dumps({"schema_version": 1, "artifacts": [entry]})]
        invalid_url_entry = dict(entry, source="https://[bad/catalog.git", targets=[
            {"assistant": "codex", "path": ".agents/skills/guide", "state": "installed"}])
        malformed.append(json.dumps({"schema_version": 1, "artifacts": [invalid_url_entry]}))
        for value in malformed:
            with self.subTest(value=value):
                manifest_path.write_text(value, encoding="utf-8")
                code, message = self.run_install("INSTALL\n")
                self.assertEqual(code, 2)
                self.assertIn("setupsmith:", message)
                self.assertNotIn("Traceback", message)
        self.assertFalse((self.project / ".agents").exists())


if __name__ == "__main__":
    unittest.main()
