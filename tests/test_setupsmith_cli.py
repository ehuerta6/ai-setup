import json
import hashlib
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
        result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stderr + result.stdout)
        return result.stdout.strip()

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

    def run_adopt(self, mappings=(), response="", preview=False, source=None, interactive=True):
        output = io.StringIO()
        errors = io.StringIO()

        class InteractiveInput(io.StringIO):
            def isatty(self):
                return interactive

        arguments = ["adopt", "--source", str(source or self.source), "--project", str(self.project)]
        for mapping in mappings:
            arguments.extend(["--map", mapping])
        if preview:
            arguments.append("--preview-only")
        with patch.object(sys, "stdin", InteractiveInput(response)), redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(arguments)
        return code, output.getvalue() + errors.getvalue()

    @staticmethod
    def write_existing_skill(path, text="Canonical fixture.\n", resource=b"resource\x00", skill_name="guide"):
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: Fixture installer skill.\n---\n" + text, encoding="utf-8")
        (path / "references").mkdir()
        (path / "references/data.bin").write_bytes(resource)

    def project_file_snapshot(self):
        return {path.relative_to(self.project).as_posix(): path.read_bytes()
                for path in self.project.rglob("*") if path.is_file()}

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

    def test_additional_target_from_same_verified_revision_preserves_baseline(self):
        code, output = self.run_install("INSTALL\n", assistants=("codex",))
        self.assertEqual(code, 0, output)
        manifest_path = self.project / ".setupsmith/manifest.json"
        before = json.loads(manifest_path.read_text(encoding="utf-8"))["artifacts"][0]

        code, output = self.run_install("INSTALL\n", assistants=("claude-code",))

        self.assertEqual(code, 0, output)
        after = json.loads(manifest_path.read_text(encoding="utf-8"))["artifacts"][0]
        for field in ("source", "configured_ref", "revision", "content_digest", "files"):
            self.assertEqual(after[field], before[field])
        self.assertEqual({target["assistant"] for target in after["targets"]}, {"codex", "claude-code"})
        self.assertEqual((self.project / ".agents/skills/guide/SKILL.md").read_bytes(),
                         (self.project / ".claude/skills/guide/SKILL.md").read_bytes())

    def test_additional_target_at_new_revision_is_rejected_without_changes(self):
        code, output = self.run_install("INSTALL\n", assistants=("codex",))
        self.assertEqual(code, 0, output)
        before = self.project_file_snapshot()
        (self.source / "skills/guide/SKILL.md").write_text(
            "---\nname: guide\ndescription: Fixture installer skill.\n---\nRevision B.\n", encoding="utf-8")
        self.git(self.source, "add", "skills/guide/SKILL.md")
        self.git(self.source, "commit", "-qm", "revision B")

        code, output = self.run_install("INSTALL\n", assistants=("claude-code",))

        self.assertEqual(code, 2)
        self.assertIn("provenance or verified content baseline", output)
        self.assertIn("No project files changed", output)
        self.assertEqual(self.project_file_snapshot(), before)
        self.assertFalse((self.project / ".claude/skills/guide").exists())

    def test_additional_target_from_different_git_source_is_rejected_without_changes(self):
        code, output = self.run_install("INSTALL\n", assistants=("codex",))
        self.assertEqual(code, 0, output)
        before = self.project_file_snapshot()
        self.git(self.source, "remote", "set-url", "origin", "https://example.invalid/other-catalog.git")

        code, output = self.run_install("INSTALL\n", assistants=("claude-code",))

        self.assertEqual(code, 2)
        self.assertIn("provenance or verified content baseline", output)
        self.assertIn("No project files changed", output)
        self.assertEqual(self.project_file_snapshot(), before)
        self.assertFalse((self.project / ".claude/skills/guide").exists())

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
        self.assertEqual(code, 2, output.getvalue() + errors.getvalue())
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
        malformed.append(json.dumps({"schema_version": 1, "artifacts": [dict(entry, baseline_state=[])]}))
        malformed.append(json.dumps({"schema_version": 1, "artifacts": [dict(entry, content_digest=[])]}))
        malformed.append(json.dumps({"schema_version": 1, "artifacts": [entry, entry]}))
        for value in malformed:
            with self.subTest(value=value):
                manifest_path.write_text(value, encoding="utf-8")
                code, message = self.run_install("INSTALL\n")
                self.assertEqual(code, 2)
                self.assertIn("setupsmith:", message)
                self.assertNotIn("Traceback", message)
        self.assertFalse((self.project / ".agents").exists())

    def test_adopts_exact_native_match_with_verified_baseline_and_preserves_bytes(self):
        destination = self.project / ".agents/skills/guide"
        import shutil
        destination.parent.mkdir(parents=True)
        shutil.copytree(self.source / "skills/guide", destination)
        before = self.project_file_snapshot()
        code, preview = self.run_adopt((".agents/skills/guide=skills/guide",), preview=True)
        self.assertEqual(code, 0, preview)
        self.assertIn("verified content baseline", preview)
        self.assertEqual(self.project_file_snapshot(), before)
        code, output = self.run_adopt((".agents/skills/guide=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 0, output)
        manifest = json.loads((self.project / ".setupsmith/manifest.json").read_text())
        entry = manifest["artifacts"][0]
        self.assertEqual(entry["baseline_state"], "verified")
        self.assertEqual(entry["targets"][0]["adoption"], "adopted")
        self.assertEqual(entry["revision"], self.git(self.source, "rev-parse", "HEAD"))
        self.assertEqual(entry["targets"][0]["path"], ".agents/skills/guide")
        self.assertEqual(self.project_file_snapshot()[".agents/skills/guide/references/nested/blob.bin"], b"\x00\xff\x10")
        self.assertEqual({key: value for key, value in self.project_file_snapshot().items()
                          if key != ".setupsmith/manifest.json"},
                         {key: value for key, value in before.items()})

    def test_explicit_custom_adoption_records_unknown_without_rewriting_tree(self):
        destination = self.project / ".claude/skills/guide"
        self.write_existing_skill(destination, "Customized locally.\n", b"custom\x00bytes")
        before = self.project_file_snapshot()
        code, output = self.run_adopt((".claude/skills/guide=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 0, output)
        manifest = json.loads((self.project / ".setupsmith/manifest.json").read_text())
        entry = manifest["artifacts"][0]
        self.assertEqual(entry["baseline_state"], "unknown")
        self.assertEqual(entry["targets"][0]["adoption"], "adopted")
        self.assertIsNone(entry["revision"])
        self.assertEqual(entry["files"]["references/data.bin"],
                         __import__("hashlib").sha256(b"custom\x00bytes").hexdigest())
        after = self.project_file_snapshot()
        for path, content in before.items():
            self.assertEqual(after[path], content)

    def test_explicit_local_name_mapping_reloads_and_accepts_later_target(self):
        first = self.project / ".agents/skills/local-name"
        second = self.project / ".claude/skills/local-name"
        self.write_existing_skill(first, "Local version.\n", b"local\x00bytes", skill_name="local-name")
        import shutil
        shutil.copytree(first, second)
        before = self.project_file_snapshot()

        mapping = ".agents/skills/local-name=skills/guide"
        code, output = self.run_adopt((mapping,), "INSTALL\n")
        self.assertEqual(code, 0, output)
        manifest_path = self.project / ".setupsmith/manifest.json"
        manifest = SETUPSMITH.load_manifest(manifest_path)
        entry = manifest["artifacts"][0]
        self.assertEqual(entry["id"], "skills/guide")
        self.assertEqual(entry["targets"][0]["path"], ".agents/skills/local-name")
        self.assertEqual(entry["baseline_state"], "unknown")

        code, output = self.run_adopt((".claude/skills/local-name=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 0, output)
        updated = SETUPSMITH.load_manifest(manifest_path)["artifacts"][0]
        self.assertEqual({target["path"] for target in updated["targets"]},
                         {".agents/skills/local-name", ".claude/skills/local-name"})
        self.assertEqual(updated["id"], "skills/guide")
        after = self.project_file_snapshot()
        for path, content in before.items():
            self.assertEqual(after[path], content, path)

        adopted_bytes = {path: content for path, content in after.items()
                         if path.startswith((".agents/skills/local-name/", ".claude/skills/local-name/"))}
        code, output = self.run_install("INSTALL\n", skills=("extra",), assistants=("codex",))
        self.assertEqual(code, 0, output)
        installed_manifest = SETUPSMITH.load_manifest(manifest_path)
        self.assertEqual({entry["id"] for entry in installed_manifest["artifacts"]},
                         {"skills/guide", "skills/extra"})
        installed_project = self.project_file_snapshot()
        for path, content in adopted_bytes.items():
            self.assertEqual(installed_project[path], content, path)

    def test_adopt_rejects_unsafe_local_basename(self):
        self.write_existing_skill(self.project / ".agents/skills/guide")
        code, output = self.run_adopt((".agents/skills/local name=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 2)
        self.assertIn("unsafe or invalid adoption mapping", output)
        self.assertFalse((self.project / ".setupsmith/manifest.json").exists())

    def test_installer_cannot_replace_or_reclassify_unknown_baseline(self):
        destination = self.project / ".agents/skills/guide"
        self.write_existing_skill(destination, "Customized locally.\n")
        code, output = self.run_adopt((".agents/skills/guide=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 0, output)
        files_before = self.project_file_snapshot()
        manifest_before = (self.project / ".setupsmith/manifest.json").read_bytes()
        code, output = self.run_install("INSTALL\n", assistants=("codex",))
        self.assertEqual(code, 2)
        self.assertIn("provenance or verified content baseline", output)
        self.assertEqual(self.project_file_snapshot(), files_before)
        self.assertEqual((self.project / ".setupsmith/manifest.json").read_bytes(), manifest_before)

    def test_candidate_name_is_not_automatically_adopted_and_mapping_is_required(self):
        self.write_existing_skill(self.project / ".agents/skills/guide", "Different.\n")
        code, report = self.run_adopt(preview=True)
        self.assertEqual(code, 0, report)
        self.assertIn("name/path only; unverified", report)
        self.assertFalse((self.project / ".setupsmith/manifest.json").exists())

    def test_duplicate_mappings_and_existing_ownership_are_rejected(self):
        import shutil
        first = self.project / ".agents/skills/guide"
        first.parent.mkdir(parents=True)
        shutil.copytree(self.source / "skills/guide", first)
        mapping = ".agents/skills/guide=skills/guide"
        code, output = self.run_adopt((mapping, mapping), "INSTALL\n")
        self.assertEqual(code, 2)
        self.assertIn("only once", output)
        self.assertFalse((self.project / ".setupsmith/manifest.json").exists())
        other = self.project / ".claude/skills/guide"
        other.parent.mkdir(parents=True)
        shutil.copytree(self.source / "skills/guide", other)
        code, output = self.run_adopt((".agents/skills/guide=skills/guide",
                                       ".claude/skills/guide=skills/guide"), "INSTALL\n")
        self.assertEqual(code, 0, output)
        entry = json.loads((self.project / ".setupsmith/manifest.json").read_text())["artifacts"][0]
        self.assertEqual({target["path"] for target in entry["targets"]},
                         {".agents/skills/guide", ".claude/skills/guide"})

    def test_preexisting_manifest_ownership_cannot_be_reassigned(self):
        self.write_existing_skill(self.project / ".agents/skills/guide")
        code, output = self.run_adopt((".agents/skills/guide=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 0, output)
        before = (self.project / ".setupsmith/manifest.json").read_bytes()
        code, output = self.run_adopt((".agents/skills/guide=skills/extra",), "INSTALL\n")
        self.assertEqual(code, 2)
        self.assertIn("already managed", output)
        self.assertEqual((self.project / ".setupsmith/manifest.json").read_bytes(), before)

    def test_already_managed_exact_skill_is_idempotent(self):
        self.write_existing_skill(self.project / ".agents/skills/guide")
        mapping = ".agents/skills/guide=skills/guide"
        self.assertEqual(self.run_adopt((mapping,), "INSTALL\n")[0], 0)
        manifest = self.project / ".setupsmith/manifest.json"
        before = manifest.read_bytes()
        modified = manifest.stat().st_mtime_ns
        code, output = self.run_adopt((mapping,), "INSTALL\n")
        self.assertEqual(code, 0, output)
        self.assertIn("no files or manifest rewritten", output)
        self.assertEqual(manifest.read_bytes(), before)
        self.assertEqual(manifest.stat().st_mtime_ns, modified)

    def test_unselected_candidate_remains_unmanaged_and_legacy_is_labeled(self):
        self.write_existing_skill(self.project / ".agents/skills/guide")
        self.write_existing_skill(self.project / ".codex/skills/guide")
        before_legacy = (self.project / ".codex/skills/guide/SKILL.md").read_bytes()
        code, report = self.run_adopt(preview=True)
        self.assertEqual(code, 0, report)
        self.assertIn("legacy/non-native", report)
        code, output = self.run_adopt((".agents/skills/guide=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 0, output)
        self.assertEqual((self.project / ".codex/skills/guide/SKILL.md").read_bytes(), before_legacy)
        entry = json.loads((self.project / ".setupsmith/manifest.json").read_text())["artifacts"][0]
        self.assertEqual([target["assistant"] for target in entry["targets"]], ["codex"])

    def test_symlink_escape_and_path_traversal_are_refused(self):
        outside = self.base / "outside"
        self.write_existing_skill(outside)
        (self.project / ".agents/skills").mkdir(parents=True)
        os.symlink(outside, self.project / ".agents/skills/guide")
        code, output = self.run_adopt((".agents/skills/guide=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 2)
        self.assertIn("not safely discovered", output)
        self.assertEqual(set(outside.iterdir()), {outside / "SKILL.md", outside / "references"})
        code, output = self.run_adopt(("../AGENTS.md=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 2)
        self.assertFalse((self.project / ".setupsmith/manifest.json").exists())

    def test_unavailable_canonical_revision_allows_only_explicit_unknown_mapping(self):
        self.write_existing_skill(self.project / ".agents/skills/guide", "Customized.\n")
        source = "https://example.invalid/catalog.git"
        with patch.object(SETUPSMITH, "resolve_source", side_effect=SETUPSMITH.DiscoveryError("offline")):
            code, output = self.run_adopt((".agents/skills/guide=skills/guide",), "INSTALL\n", source=source)
        self.assertEqual(code, 0, output)
        self.assertIn("Resolved immutable revision: none", output)
        entry = json.loads((self.project / ".setupsmith/manifest.json").read_text())["artifacts"][0]
        self.assertIsNone(entry["revision"])
        self.assertIsNone(entry["configured_ref"])
        self.assertEqual(entry["baseline_state"], "unknown")

    def test_noninteractive_adoption_refuses_manifest_write(self):
        self.write_existing_skill(self.project / ".agents/skills/guide")
        code, output = self.run_adopt((".agents/skills/guide=skills/guide",), interactive=False)
        self.assertEqual(code, 2)
        self.assertIn("interactive confirmation", output)
        self.assertFalse((self.project / ".setupsmith/manifest.json").exists())

    def test_declined_adoption_does_not_write_manifest_or_change_files(self):
        self.write_existing_skill(self.project / ".agents/skills/guide")
        before = self.project_file_snapshot()
        code, output = self.run_adopt((".agents/skills/guide=skills/guide",), "no\n")
        self.assertEqual(code, 0, output)
        self.assertIn("Declined", output)
        self.assertEqual(self.project_file_snapshot(), before)

    def test_stale_preview_rechecks_adopted_content(self):
        destination = self.project / ".agents/skills/guide"
        self.write_existing_skill(destination)
        args = ["adopt", "--source", str(self.source), "--project", str(self.project),
                "--map", ".agents/skills/guide=skills/guide"]
        output = io.StringIO()
        errors = io.StringIO()
        class InteractiveInput(io.StringIO):
            def isatty(self): return True
        def change_content(_prompt):
            (destination / "SKILL.md").write_text("changed after preview", encoding="utf-8")
            return "INSTALL"
        with patch.object(sys, "stdin", InteractiveInput("")), patch("builtins.input", side_effect=change_content), redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(args)
        self.assertEqual(code, 2)
        self.assertIn("stale preview", errors.getvalue())
        self.assertFalse((self.project / ".setupsmith/manifest.json").exists())

    def test_manifest_write_failure_leaves_imported_files_unchanged(self):
        destination = self.project / ".agents/skills/guide"
        self.write_existing_skill(destination)
        before = self.project_file_snapshot()
        original_replace = os.replace
        def fail_manifest(source, target):
            if str(target).endswith(".setupsmith/manifest.json"):
                raise OSError("injected manifest failure")
            return original_replace(source, target)
        with patch.object(SETUPSMITH.os, "replace", side_effect=fail_manifest):
            code, output = self.run_adopt((".agents/skills/guide=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 2)
        self.assertIn("injected manifest failure", output)
        self.assertEqual(self.project_file_snapshot(), before)
        self.assertFalse((self.project / ".setupsmith").exists())

    def test_issue_11_schema_one_manifest_remains_verified_and_compatible(self):
        code, output = self.run_install("INSTALL\n", assistants=("codex",))
        self.assertEqual(code, 0, output)
        manifest_path = self.project / ".setupsmith/manifest.json"
        manifest_before = json.loads(manifest_path.read_text())
        self.assertNotIn("baseline_state", manifest_before["artifacts"][0])
        code, output = self.run_adopt((".agents/skills/guide=skills/guide",), "INSTALL\n")
        self.assertEqual(code, 0, output)
        self.assertIn("no files or manifest rewritten", output)
        manifest_after = json.loads(manifest_path.read_text())
        self.assertEqual(manifest_after, manifest_before)



class SkillCheckTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.remote = self.base / "catalog.git"
        self.git(self.base, "init", "--bare", "-q", str(self.remote))
        self.source = self.base / "catalog"
        self.source.mkdir()
        self.git(self.source, "init", "-q", "-b", "main")
        self.git(self.source, "config", "user.name", "Fixture")
        self.git(self.source, "config", "user.email", "fixture@example.invalid")
        self.write_source_tree("Guide A line.\n", "helper A line.\n", b"\x00A")
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-qm", "revision A")
        self.revision_a = self.git(self.source, "rev-parse", "HEAD")
        self.digest_a, self.hashes_a, _ = SETUPSMITH.tree_identity(self.source / "skills/guide")
        self.git(self.source, "remote", "add", "origin", self.remote.as_uri())
        self.git(self.source, "push", "-u", "origin", "main")
        self.project = self.base / "project"
        self.project.mkdir()
        self.git(self.project, "init", "-q", "-b", "main")
        self.git(self.project, "config", "user.name", "Fixture")
        self.git(self.project, "config", "user.email", "fixture@example.invalid")
        self.git(self.project, "commit", "--allow-empty", "-qm", "project")
        self.copy_source_to_target(".agents/skills/guide")
        self.copy_source_to_target(".claude/skills/guide")
        self.manifest_path = self.project / ".setupsmith/manifest.json"
        self.write_manifest()

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def git(cwd, *args):
        result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stderr + result.stdout)
        return result.stdout.strip()

    def write_source_tree(self, skill_text, helper_text, binary):
        skill = self.source / "skills/guide"
        (skill / "references").mkdir(parents=True, exist_ok=True)
        (skill / "assets").mkdir(exist_ok=True)
        (skill / "SKILL.md").write_text(
            "---\nname: guide\ndescription: Fixture comparison skill.\n---\n" + skill_text,
            encoding="utf-8")
        (skill / "references/helper.md").write_text(helper_text, encoding="utf-8")
        (skill / "assets/data.bin").write_bytes(binary)

    def copy_source_to_target(self, relative):
        import shutil
        target = self.project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.source / "skills/guide", target)

    def write_manifest(self, *, source=None, configured_ref="refs/heads/main", revision=None,
                       baseline_state="verified", targets=None, files=None, digest=None):
        entry = {"id": "skills/guide", "source": source or "https://example.invalid/catalog.git",
                 "configured_ref": configured_ref, "revision": revision or self.revision_a,
                 "content_digest": self.digest_a, "files": self.hashes_a,
                 "targets": targets or [
                     {"assistant": "codex", "path": ".agents/skills/guide", "state": "installed"},
                     {"assistant": "claude-code", "path": ".claude/skills/guide", "state": "installed"}]}
        if baseline_state != "verified":
            entry["baseline_state"] = baseline_state
            entry["revision"] = revision
            for target in entry["targets"]:
                target["adoption"] = "adopted"
        if files is not None:
            entry["files"] = files
        if digest is not None:
            entry["content_digest"] = digest
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps({"schema_version": 1, "artifacts": [entry]}, indent=2),
                                      encoding="utf-8")

    def push_revision_b(self, *, skill_text="Guide A line.\n", helper_text="helper B line.\n",
                        binary=b"\x00A", add_file=True):
        self.write_source_tree(skill_text, helper_text, binary)
        if add_file:
            (self.source / "skills/guide/references/new.md").write_text("added upstream\n", encoding="utf-8")
        self.git(self.source, "add", "-A")
        self.git(self.source, "commit", "-qm", "revision B")
        revision = self.git(self.source, "rev-parse", "HEAD")
        self.git(self.source, "push", "origin", "main")
        return revision

    def run_command(self, command="check", *, skills=()):
        output, errors = io.StringIO(), io.StringIO()
        args = [command, "--project", str(self.project)]
        for skill in skills:
            args.extend(["--skill", skill])
        resolve = SETUPSMITH.resolve_source
        def local_resolve(source, configured_ref, checkout):
            if source == "https://example.invalid/catalog.git":
                source = str(self.source)
            return resolve(source, configured_ref, checkout)
        with patch.object(SETUPSMITH, "resolve_source", side_effect=local_resolve), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(args)
        return code, output.getvalue(), errors.getvalue()

    def run_remove(self, targets, *, preview=False, response="REMOVE", tty=True):
        output, errors = io.StringIO(), io.StringIO()
        args = ["remove", "--project", str(self.project)]
        for target in targets:
            args.extend(["--target", target])
        if preview:
            args.append("--preview-only")
        with patch("builtins.input", return_value=response), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: tty})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(args)
        return code, output.getvalue(), errors.getvalue()

    def test_remove_one_target_keeps_sibling_and_manifest_entry(self):
        code, output, errors = self.run_remove(["skills/guide=.agents/skills/guide"])
        self.assertEqual(code, 0, errors)
        self.assertIn("destinations remaining: .claude/skills/guide", output)
        self.assertFalse((self.project / ".agents/skills/guide").exists())
        self.assertTrue((self.project / ".claude/skills/guide/SKILL.md").is_file())
        entry = json.loads(self.manifest_path.read_text())["artifacts"][0]
        self.assertEqual(entry["targets"], [{"assistant": "claude-code", "path": ".claude/skills/guide", "state": "installed"}])

    def test_remove_final_target_preserves_unrelated_manifest_entry(self):
        manifest = json.loads(self.manifest_path.read_text())
        other = dict(manifest["artifacts"][0], id="skills/other", targets=[
            {"assistant": "codex", "path": ".agents/skills/other", "state": "installed"}])
        manifest["artifacts"].append(other)
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        code, _, errors = self.run_remove(["skills/guide=.agents/skills/guide", "skills/guide=.claude/skills/guide"])
        self.assertEqual(code, 0, errors)
        self.assertFalse((self.project / ".agents/skills/guide").exists())
        self.assertFalse((self.project / ".claude/skills/guide").exists())
        remaining = json.loads(self.manifest_path.read_text())["artifacts"]
        self.assertEqual([entry["id"] for entry in remaining], ["skills/other"])

    def test_remove_preview_decline_and_noninteractive_refuse_without_writes(self):
        before = self.tree_snapshot()
        code, output, errors = self.run_remove(["skills/guide=.agents/skills/guide"], preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn("Proposed manifest:", output)
        self.assertIn("files/directories proposed for removal", output)
        self.assertEqual(self.tree_snapshot(), before)
        code, output, errors = self.run_remove(["skills/guide=.agents/skills/guide"], response="no")
        self.assertEqual(code, 0, errors)
        self.assertIn("Declined", output)
        self.assertEqual(self.tree_snapshot(), before)
        code, _, errors = self.run_remove(["skills/guide=.agents/skills/guide"], tty=False)
        self.assertEqual(code, 2)
        self.assertIn("requires interactive terminal approval", errors)
        self.assertEqual(self.tree_snapshot(), before)

    def test_remove_refuses_local_modification_unknown_identity_mismatch_and_unmanaged_target(self):
        skill_file = self.project / ".agents/skills/guide/SKILL.md"
        skill_file.write_text(skill_file.read_text() + "local\n", encoding="utf-8")
        code, _, errors = self.run_remove(["skills/guide=.agents/skills/guide"], preview=True)
        self.assertEqual(code, 2)
        self.assertIn("locally changed or unexpected content", errors)
        skill_file.write_text(skill_file.read_text().replace("local\n", ""), encoding="utf-8")
        code, _, errors = self.run_remove(["skills/guide=.agents/skills/not-guide"], preview=True)
        self.assertEqual(code, 2)
        self.assertIn("not uniquely owned", errors)
        self.write_manifest(baseline_state="unknown", revision=None)
        code, output, errors = self.run_remove(["skills/guide=.agents/skills/guide"], preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn("canonical history unverified", output)
        self.assertTrue((self.project / ".agents/skills/guide/SKILL.md").is_file())

    def test_remove_refuses_unrecorded_empty_directory(self):
        unexpected = self.project / ".agents/skills/guide/user-notes/empty"
        unexpected.mkdir(parents=True)
        code, _, errors = self.run_remove(["skills/guide=.agents/skills/guide"], preview=True)
        self.assertEqual(code, 2)
        self.assertIn("unexpected or missing directories", errors)
        self.assertTrue(unexpected.is_dir())

    def test_remove_refuses_legacy_managed_target_without_changes(self):
        import shutil
        legacy = self.project / ".codex/skills/guide"
        legacy.parent.mkdir(parents=True)
        shutil.move(self.project / ".agents/skills/guide", legacy)
        manifest = json.loads(self.manifest_path.read_text())
        manifest["artifacts"][0]["targets"][0] = {
            "assistant": "codex-legacy", "path": ".codex/skills/guide", "state": "installed"}
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        before = self.tree_snapshot()
        code, _, errors = self.run_remove(["skills/guide=.codex/skills/guide"], preview=True)
        self.assertEqual(code, 2)
        self.assertIn("unsupported managed assistant target: codex-legacy", errors)
        self.assertEqual(self.tree_snapshot(), before)

    def test_remove_adopted_custom_path_and_stale_or_symlinked_target_refusal(self):
        import shutil
        shutil.move(self.project / ".agents/skills/guide", self.project / ".agents/skills/local-guide")
        manifest = json.loads(self.manifest_path.read_text())
        manifest["artifacts"][0]["targets"][0]["path"] = ".agents/skills/local-guide"
        manifest["artifacts"][0]["targets"][0]["adoption"] = "adopted"
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        code, output, errors = self.run_remove(["skills/guide=.agents/skills/local-guide"], preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn(".agents/skills/local-guide/", output)
        self.assertNotIn(".agents/skills/guide/", output)
        before = self.tree_snapshot()
        code, _, errors = self.run_remove(["skills/guide=.agents/skills/local-guide"], tty=False)
        self.assertEqual(code, 2)
        self.assertEqual(self.tree_snapshot(), before)
        shutil.rmtree(self.project / ".agents/skills/local-guide")
        (self.project / ".agents/skills/local-guide").symlink_to(self.base / "outside")
        code, _, errors = self.run_remove(["skills/guide=.agents/skills/local-guide"], preview=True)
        self.assertEqual(code, 2)
        self.assertIn("symlink", errors)

    def test_remove_stale_content_after_confirmation_is_refused(self):
        target_file = self.project / ".agents/skills/guide/SKILL.md"
        def edit_then_confirm(prompt):
            target_file.write_text(target_file.read_text() + "concurrent\n", encoding="utf-8")
            return "REMOVE"
        before_manifest = self.manifest_path.read_bytes()
        output, errors = io.StringIO(), io.StringIO()
        with patch("builtins.input", side_effect=edit_then_confirm), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["remove", "--project", str(self.project), "--target",
                                    "skills/guide=.agents/skills/guide"])
        self.assertEqual(code, 2)
        self.assertIn("stale preview or changed content", errors.getvalue())
        self.assertTrue(target_file.is_file())
        self.assertIn("concurrent", target_file.read_text())
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)

    def test_remove_detects_edit_in_check_to_rename_window_and_restores_it(self):
        original_replace = os.replace
        target_file = self.project / ".agents/skills/guide/SKILL.md"
        def edit_before_rename(source, destination):
            if str(destination).endswith("target-0"):
                target_file.write_text(target_file.read_text() + "concurrent\n", encoding="utf-8")
            return original_replace(source, destination)
        before_manifest = self.manifest_path.read_bytes()
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(os, "replace", side_effect=edit_before_rename), \
                patch("builtins.input", return_value="REMOVE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["remove", "--project", str(self.project), "--target",
                                    "skills/guide=.agents/skills/guide"])
        self.assertEqual(code, 2)
        self.assertIn("staged destination changed during removal", errors.getvalue())
        self.assertTrue(target_file.is_file())
        self.assertIn("concurrent", target_file.read_text())
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)

    def test_remove_filesystem_failure_restores_staged_target_and_manifest(self):
        original_replace = os.replace
        calls = 0
        def fail_target_stage(source, destination):
            nonlocal calls
            if str(destination).endswith("target-0"):
                calls += 1
                raise OSError("injected staging failure")
            return original_replace(source, destination)
        before_manifest = self.manifest_path.read_bytes()
        before_tree = SETUPSMITH.tree_identity(self.project / ".agents/skills/guide")[0]
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(os, "replace", side_effect=fail_target_stage), \
                patch("builtins.input", return_value="REMOVE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["remove", "--project", str(self.project), "--target",
                                    "skills/guide=.agents/skills/guide"])
        self.assertEqual(code, 2)
        self.assertIn("original destinations restored", errors.getvalue())
        self.assertEqual(calls, 1)
        self.assertEqual(SETUPSMITH.tree_identity(self.project / ".agents/skills/guide")[0], before_tree)
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)

    def test_remove_manifest_failure_restores_destinations_and_manifest(self):
        original_replace = os.replace
        def fail_manifest(source, destination):
            if str(destination).endswith("/.setupsmith/manifest.json"):
                raise OSError("injected manifest replacement failure")
            return original_replace(source, destination)
        before_manifest = self.manifest_path.read_bytes()
        before_tree = SETUPSMITH.tree_identity(self.project / ".agents/skills/guide")[0]
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(os, "replace", side_effect=fail_manifest), \
                patch("builtins.input", return_value="REMOVE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["remove", "--project", str(self.project), "--target",
                                    "skills/guide=.agents/skills/guide"])
        self.assertEqual(code, 2)
        self.assertIn("original destinations restored", errors.getvalue())
        self.assertEqual(SETUPSMITH.tree_identity(self.project / ".agents/skills/guide")[0], before_tree)
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)

    def test_remove_batch_failure_restores_previously_staged_target(self):
        original_replace = os.replace
        def fail_second_stage(source, destination):
            if str(destination).endswith("target-1"):
                raise OSError("injected second target failure")
            return original_replace(source, destination)
        before_manifest = self.manifest_path.read_bytes()
        before_trees = {path: SETUPSMITH.tree_identity(self.project / path)[0] for path in
                        (".agents/skills/guide", ".claude/skills/guide")}
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(os, "replace", side_effect=fail_second_stage), \
                patch("builtins.input", return_value="REMOVE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["remove", "--project", str(self.project), "--target",
                                    "skills/guide=.agents/skills/guide", "--target",
                                    "skills/guide=.claude/skills/guide"])
        self.assertEqual(code, 2)
        self.assertIn("original destinations restored", errors.getvalue())
        for path, digest in before_trees.items():
            self.assertEqual(SETUPSMITH.tree_identity(self.project / path)[0], digest)
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)

    def run_install(self, response="INSTALL\n"):
        output, errors = io.StringIO(), io.StringIO()
        args = ["install", "--source", "https://example.invalid/catalog.git",
                "--ref", "refs/heads/main", "--skill", "guide",
                "--assistant", "codex", "--assistant", "claude-code",
                "--project", str(self.project)]
        class InteractiveInput(io.StringIO):
            def isatty(self):
                return True
        resolve = SETUPSMITH.resolve_source
        def local_resolve(source, configured_ref, checkout):
            if source == "https://example.invalid/catalog.git":
                source = str(self.source)
            return resolve(source, configured_ref, checkout)
        with patch.object(SETUPSMITH, "resolve_source", side_effect=local_resolve), \
                patch.object(sys, "stdin", InteractiveInput(response)), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(args)
        return code, output.getvalue(), errors.getvalue()

    def run_update(self, *, selection=("--all-safe",), response="", preview=False, interactive=True):
        output, errors = io.StringIO(), io.StringIO()
        args = ["update", "--project", str(self.project), *selection]
        if preview:
            args.append("--preview-only")
        class InteractiveInput(io.StringIO):
            def isatty(self):
                return interactive
        resolve = SETUPSMITH.resolve_source
        def local_resolve(source, configured_ref, checkout):
            if source == "https://example.invalid/catalog.git":
                source = str(self.source)
            return resolve(source, configured_ref, checkout)
        with patch.object(SETUPSMITH, "resolve_source", side_effect=local_resolve), \
                patch.object(sys, "stdin", InteractiveInput(response)), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(args)
        return code, output.getvalue(), errors.getvalue()

    def run_restore(self, response="", preview=False, interactive=True):
        output, errors = io.StringIO(), io.StringIO()
        args = ["restore", "--project", str(self.project)]
        if preview:
            args.append("--preview-only")
        original_git = SETUPSMITH.git
        def local_git(*git_args, cwd=None):
            rewritten = tuple(str(self.source) if str(arg) == "https://example.invalid/catalog.git" else arg
                              for arg in git_args)
            return original_git(*rewritten, cwd=cwd)
        class InteractiveInput(io.StringIO):
            def isatty(self):
                return interactive
        with patch.object(SETUPSMITH, "git", side_effect=local_git), \
                patch.object(sys, "stdin", InteractiveInput(response)), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(args)
        return code, output.getvalue(), errors.getvalue()

    def tree_snapshot(self):
        entries = {}
        for path in self.project.rglob("*"):
            relative = path.relative_to(self.project).as_posix()
            if path.is_symlink():
                entries[relative] = ("symlink", os.readlink(path))
            elif path.is_dir():
                entries[relative] = ("dir",)
            else:
                entries[relative] = ("file", path.read_bytes())
        return entries

    def test_current_verified_installation(self):
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("codex: CURRENT", output)
        self.assertIn("claude-code: CURRENT", output)
        self.assertIn(self.revision_a, output)

    def test_adopted_local_path_check_and_diff_are_read_only_and_honest(self):
        self.git(self.source, "remote", "set-url", "origin", "https://example.invalid/catalog.git")
        import shutil
        self.manifest_path.unlink()
        shutil.rmtree(self.project / ".agents/skills/guide")
        shutil.rmtree(self.project / ".claude/skills/guide")
        destination = self.project / ".agents/skills/local-name"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.source / "skills/guide", destination)
        skill_md = destination / "SKILL.md"
        skill_md.write_text(skill_md.read_text(encoding="utf-8").replace("name: guide", "name: local-name")
                            .replace("Guide A line.", "Customized at adoption.\n"), encoding="utf-8")
        adopt_args = ["adopt", "--source", str(self.source), "--project", str(self.project),
                      "--map", ".agents/skills/local-name=skills/guide"]
        adopt_output, adopt_errors = io.StringIO(), io.StringIO()

        class InteractiveInput(io.StringIO):
            def isatty(self):
                return True

        with patch.object(sys, "stdin", InteractiveInput("")), \
                patch("builtins.input", return_value="INSTALL"), \
                redirect_stdout(adopt_output), redirect_stderr(adopt_errors):
            code = SETUPSMITH.main(adopt_args)
        self.assertEqual(code, 0, adopt_errors.getvalue() + adopt_output.getvalue())

        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        entry = manifest["artifacts"][0]
        self.assertEqual(entry["id"], "skills/guide")
        self.assertEqual(entry["targets"][0]["path"], ".agents/skills/local-name")
        self.assertEqual(entry["baseline_state"], "unknown")
        self.assertIsNone(entry["revision"])
        manifest_after_adopt = self.manifest_path.read_bytes()

        # An install must read the schema and protect an unknown-baseline adoption.
        install_output, install_errors = io.StringIO(), io.StringIO()
        with patch.object(sys, "stdin", InteractiveInput("")), \
                redirect_stdout(install_output), redirect_stderr(install_errors):
            install_code = SETUPSMITH.main(["install", "--source", str(self.source), "--skill", "guide",
                                            "--assistant", "codex", "--project", str(self.project)])
        self.assertEqual(install_code, 2)
        self.assertIn("provenance or verified content baseline",
                      install_errors.getvalue() + install_output.getvalue())
        self.assertEqual(self.manifest_path.read_bytes(), manifest_after_adopt)

        local_file = destination / "references/helper.md"
        local_file.write_text("Changed after adoption.\n", encoding="utf-8")
        expected_before = entry["files"]["references/helper.md"]
        expected_after = hashlib.sha256(b"Changed after adoption.\n").hexdigest()
        before_checks = self.tree_snapshot()
        code, check_output, errors = self.run_command("check")
        self.assertEqual(code, 0, errors)
        self.assertIn("skills/guide", check_output)
        self.assertIn("UNKNOWN_BASELINE", check_output)
        self.assertIn("LOCAL_DIVERGENCE", check_output)
        self.assertIn("references/helper.md", check_output)
        self.assertIn(".agents/skills/local-name", check_output)
        self.assertIn(expected_before, check_output)
        self.assertIn(expected_after, check_output)
        self.assertNotIn("CURRENT", check_output)
        self.assertEqual(self.tree_snapshot(), before_checks)

        code, diff_output, errors = self.run_command("diff")
        self.assertEqual(code, 0, errors)
        self.assertIn("UNKNOWN_BASELINE", diff_output)
        self.assertIn("LOCAL_DIVERGENCE", diff_output)
        self.assertIn("references/helper.md", diff_output)
        self.assertIn("observed hashes only", diff_output)
        self.assertNotIn("Baseline ", diff_output)
        self.assertIn(expected_before, diff_output)
        self.assertIn(expected_after, diff_output)
        self.assertEqual(self.tree_snapshot(), before_checks)

    def test_adopted_path_validator_keeps_install_naming_and_ownership_strict(self):
        custom_target = {"assistant": "codex", "path": ".agents/skills/local-name",
                         "state": "installed", "adoption": "adopted"}
        self.write_manifest(baseline_state="unknown", targets=[custom_target])
        self.assertEqual(len(SETUPSMITH.load_check_manifest(self.manifest_path)["artifacts"]), 1)

        installed_custom = dict(custom_target, adoption="installed")
        self.write_manifest(targets=[installed_custom])
        code, _, errors = self.run_command()
        self.assertEqual(code, 2)
        self.assertIn("conflicting target path", errors)

        unsafe_custom = dict(custom_target, path=".agents/skills/../outside")
        self.write_manifest(baseline_state="unknown", targets=[unsafe_custom])
        code, _, errors = self.run_command()
        self.assertEqual(code, 2)
        self.assertIn("conflicting target path", errors)

        duplicate_owner = dict(custom_target)
        self.write_manifest(baseline_state="unknown", targets=[custom_target, duplicate_owner])
        code, _, errors = self.run_command()
        self.assertEqual(code, 2)
        self.assertIn("conflicting target ownership", errors)

    def test_upstream_support_file_change_and_text_diff(self):
        revision_b = self.push_revision_b()
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("UPSTREAM_UPDATE", output)
        code, diff, errors = self.run_command("diff")
        self.assertEqual(code, 0, errors)
        self.assertIn(f"Baseline {self.revision_a}/references/helper.md", diff)
        self.assertIn(f"Upstream {revision_b}/references/helper.md", diff)
        self.assertIn("-helper A line.", diff)
        self.assertIn("+helper B line.", diff)
        self.assertIn("added upstream", diff)

    def test_upstream_support_file_removal_is_reported(self):
        (self.source / "skills/guide/references/helper.md").unlink()
        self.git(self.source, "add", "-A")
        self.git(self.source, "commit", "-qm", "remove support file")
        self.git(self.source, "push", "origin", "main")
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("upstream removed: references/helper.md", output)
        code, diff, _ = self.run_command("diff")
        self.assertIn("Baseline ", diff)
        self.assertIn("/references/helper.md", diff)
        self.assertIn("+++ /dev/null", diff)

    def test_local_only_change_reports_local_divergence(self):
        local = self.project / ".agents/skills/guide/references/helper.md"
        local.write_text("locally changed\n", encoding="utf-8")
        code, output, _ = self.run_command()
        self.assertEqual(code, 0)
        self.assertIn("codex: LOCAL_DIVERGENCE", output)
        self.assertIn("claude-code: CURRENT", output)
        code, diff, _ = self.run_command("diff")
        self.assertEqual(code, 0)
        self.assertIn("→ Local .agents/skills/guide", diff)
        self.assertIn("-helper A line.", diff)
        self.assertIn("+locally changed", diff)

    def test_simultaneous_upstream_and_local_changes_are_separate(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        before_manifest = self.manifest_path.read_bytes()
        (self.project / ".agents/skills/guide/references/helper.md").write_text("local helper\n", encoding="utf-8")
        code, output, _ = self.run_command()
        self.assertEqual(code, 0)
        self.assertIn("codex:", output)
        self.assertIn("UPSTREAM_UPDATE", output)
        self.assertIn("LOCAL_DIVERGENCE", output)
        code, diff, _ = self.run_command("diff")
        self.assertIn("→ Upstream ", diff)
        self.assertIn("→ Local .agents/skills/guide", diff)

    def test_missing_installation_and_upstream_removal(self):
        import shutil
        shutil.rmtree(self.project / ".agents/skills/guide")
        code, output, _ = self.run_command()
        self.assertEqual(code, 0)
        self.assertIn("codex: MISSING_INSTALLATION", output)
        self.write_source_tree("Guide A line.\n", "helper A line.\n", b"\x00A")
        shutil.rmtree(self.source / "skills/guide")
        self.git(self.source, "add", "-A")
        self.git(self.source, "commit", "-qm", "remove upstream skill")
        self.git(self.source, "push", "origin", "main")
        code, output, _ = self.run_command()
        self.assertEqual(code, 0)
        self.assertIn("UPSTREAM_REMOVED", output)

    def test_binary_resource_changes_show_digests(self):
        self.push_revision_b(binary=b"\x00B", add_file=False)
        code, diff, errors = self.run_command("diff")
        self.assertEqual(code, 0, errors)
        self.assertIn("Binary resource assets/data.bin: modified", diff)
        self.assertIn("sha256=", diff)

    def test_unknown_baseline_reports_local_changes_without_fabricated_diff(self):
        target = self.project / ".agents/skills/guide/references/helper.md"
        target.write_text("changed since import\n", encoding="utf-8")
        self.write_manifest(baseline_state="unknown")
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("UNKNOWN_BASELINE, LOCAL_DIVERGENCE", output)
        code, diff, _ = self.run_command("diff")
        self.assertIn("text diff unavailable", diff)
        self.assertNotIn("Baseline unknown/skills/guide", diff)

    def test_targets_are_reported_independently(self):
        (self.project / ".agents/skills/guide/SKILL.md").write_text("codex edit", encoding="utf-8")
        code, output, _ = self.run_command()
        self.assertEqual(code, 0)
        self.assertIn("codex: LOCAL_DIVERGENCE", output)
        self.assertIn("claude-code: CURRENT", output)

    def test_unavailable_source_is_explicit_and_no_cache_is_claimed(self):
        self.write_manifest(source="https://example.invalid/missing.git")
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("SOURCE_UNAVAILABLE", output)
        self.assertIn("no cached source was used", output)

    def test_unknown_target_is_unsupported_without_reading_arbitrary_path(self):
        entry_target = {"assistant": "future-agent", "path": "AGENTS.md", "state": "installed"}
        self.write_manifest(targets=[entry_target])
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("future-agent: UNSUPPORTED_TARGET", output)
        self.assertNotIn("LOCAL_DIVERGENCE", output)

    def test_restore_preview_decline_approved_pinned_revision_and_repeat_noop(self):
        import shutil
        self.git(self.project, "add", ".")
        self.git(self.project, "commit", "-qm", "commit managed manifest and skills")
        clone = self.base / "restore-clone"
        subprocess.run(["git", "clone", "-q", str(self.project), str(clone)], check=True)
        self.project = clone
        self.manifest_path = self.project / ".setupsmith/manifest.json"
        shutil.rmtree(self.project / ".agents/skills/guide")
        shutil.rmtree(self.project / ".claude/skills/guide")
        self.push_revision_b(skill_text="Guide B line.\n", binary=b"\x00B")
        before_manifest = self.manifest_path.read_bytes()
        code, preview, errors = self.run_restore(preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn(self.revision_a, preview)
        self.assertIn(".agents/skills/guide", preview)
        self.assertIn(".claude/skills/guide", preview)
        self.assertIn("assets/data.bin", preview)
        self.assertFalse((self.project / ".agents/skills/guide").exists())
        code, declined, errors = self.run_restore(response="no\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Declined", declined)
        self.assertFalse((self.project / ".claude/skills/guide").exists())
        code, restored, errors = self.run_restore(response="RESTORE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Restored and verified", restored)
        for destination in (self.project / ".agents/skills/guide", self.project / ".claude/skills/guide"):
            self.assertEqual(SETUPSMITH.tree_identity(destination)[0], self.digest_a)
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)
        code, repeated, errors = self.run_restore(response="RESTORE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Already restored and verified", repeated)
        self.assertIn("No verified missing destinations", repeated)

    def test_restore_preserves_unknown_custom_files_and_refuses_occupied_paths(self):
        import shutil
        custom = self.project / ".agents/skills/local-guide"
        shutil.copytree(self.source / "skills/guide", custom)
        (custom / "SKILL.md").write_text("custom user instructions\n", encoding="utf-8")
        target = {"assistant": "codex", "path": ".agents/skills/local-guide",
                  "state": "installed", "adoption": "adopted"}
        self.write_manifest(baseline_state="unknown", targets=[target])
        before = self.tree_snapshot()
        code, output, errors = self.run_restore(preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn("UNKNOWN_BASELINE", output)
        self.assertIn("missing custom files must be supplied separately", output)
        self.assertEqual(self.tree_snapshot(), before)

        self.write_manifest()
        shutil.rmtree(self.project / ".agents/skills/guide")
        shutil.copytree(self.source / "skills/guide", self.project / ".agents/skills/guide")
        (self.project / ".agents/skills/guide/SKILL.md").write_text("unmanaged occupied content")
        before = self.tree_snapshot()
        code, output, errors = self.run_restore(preview=True)
        self.assertEqual(code, 2, errors)
        self.assertIn("DESTINATION_CONFLICT", output)
        self.assertIn("no project files changed", output)
        self.assertEqual(self.tree_snapshot(), before)

    def test_restore_refuses_unavailable_pinned_revision_and_noninteractive_write(self):
        import shutil
        shutil.rmtree(self.project / ".agents/skills/guide")
        shutil.rmtree(self.project / ".claude/skills/guide")
        self.write_manifest(revision="0" * 40)
        before = self.tree_snapshot()
        code, output, errors = self.run_restore(preview=True)
        self.assertEqual(code, 2, errors)
        self.assertIn("SOURCE_UNAVAILABLE_OR_CONFLICT", output)
        self.assertEqual(self.tree_snapshot(), before)
        self.write_manifest()
        before_normal = self.tree_snapshot()
        code, _, errors = self.run_restore(interactive=False)
        self.assertEqual(code, 2)
        self.assertIn("requires interactive terminal approval", errors)
        self.assertEqual(self.tree_snapshot(), before_normal)

    def test_restore_rechecks_existing_targets_after_approval(self):
        import shutil
        shutil.rmtree(self.project / ".claude/skills/guide")

        def edit_existing_and_approve(prompt):
            (self.project / ".agents/skills/guide/SKILL.md").write_text("changed during approval\n")
            return "RESTORE"

        with patch("builtins.input", side_effect=edit_existing_and_approve):
            code, output, errors = self.run_restore(response="RESTORE\n")
        self.assertEqual(code, 2)
        self.assertIn("already-restored destination changed", errors)
        self.assertFalse((self.project / ".claude/skills/guide").exists())

    def test_restore_verified_adopted_local_path(self):
        import shutil
        custom = self.project / ".agents/skills/local-guide"
        shutil.copytree(self.project / ".agents/skills/guide", custom)
        shutil.rmtree(self.project / ".agents/skills/guide")
        targets = [
            {"assistant": "codex", "path": ".agents/skills/local-guide", "state": "installed", "adoption": "adopted"},
            {"assistant": "claude-code", "path": ".claude/skills/guide", "state": "installed"},
        ]
        self.write_manifest(targets=targets)
        shutil.rmtree(custom)
        shutil.rmtree(self.project / ".claude/skills/guide")
        code, preview, errors = self.run_restore(preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn(".agents/skills/local-guide", preview)
        code, _, errors = self.run_restore(response="RESTORE\n")
        self.assertEqual(code, 0, errors)
        self.assertEqual(SETUPSMITH.tree_identity(custom)[0], self.digest_a)
        self.assertEqual(SETUPSMITH.tree_identity(self.project / ".claude/skills/guide")[0], self.digest_a)

    def test_restore_refuses_manifest_digest_mismatch_and_destination_symlink(self):
        import shutil
        self.write_manifest(digest="a" * 64)
        before = self.tree_snapshot()
        code, output, errors = self.run_restore(preview=True)
        self.assertEqual(code, 2, errors)
        self.assertIn("SOURCE_UNAVAILABLE_OR_CONFLICT", output)
        self.assertEqual(self.tree_snapshot(), before)

        self.write_manifest()
        shutil.rmtree(self.project / ".agents/skills/guide")
        outside = self.base / "outside-target"
        outside.mkdir()
        (outside / "keep.txt").write_text("untouched\n")
        (self.project / ".agents/skills/guide").symlink_to(outside, target_is_directory=True)
        before_outside = (outside / "keep.txt").read_bytes()
        code, output, errors = self.run_restore(preview=True)
        self.assertEqual(code, 2, errors)
        self.assertIn("DESTINATION_CONFLICT", output)
        self.assertEqual((outside / "keep.txt").read_bytes(), before_outside)

    def test_restore_reports_injected_placement_failure_without_partial_tree(self):
        import shutil
        shutil.rmtree(self.project / ".agents/skills/guide")
        shutil.rmtree(self.project / ".claude/skills/guide")
        original_replace = os.replace

        def fail_destination_placement(source, destination):
            if Path(destination).name == "guide" and ".agents/skills" in str(destination):
                raise OSError("injected placement failure")
            return original_replace(source, destination)

        before_manifest = self.manifest_path.read_bytes()
        with patch.object(SETUPSMITH.os, "replace", side_effect=fail_destination_placement):
            code, _, errors = self.run_restore(response="RESTORE\n")
        self.assertEqual(code, 2)
        self.assertIn("injected placement failure", errors)
        self.assertIn("completed writes were removed", errors)
        self.assertFalse((self.project / ".agents/skills/guide").exists())
        self.assertFalse((self.project / ".claude/skills/guide").exists())
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)

    def test_restore_labels_unsupported_legacy_target_without_reading_it(self):
        target = {"assistant": "codex-legacy", "path": ".codex/skills/guide", "state": "installed"}
        self.write_manifest(targets=[target])
        before = self.tree_snapshot()
        code, output, errors = self.run_restore(preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn("UNSUPPORTED_TARGET codex-legacy", output)
        self.assertIn("No verified missing destinations", output)
        self.assertEqual(self.tree_snapshot(), before)

    def test_install_update_restore_missing_destination_uses_updated_manifest_pin(self):
        import shutil
        shutil.rmtree(self.project / ".agents/skills/guide")
        shutil.rmtree(self.project / ".claude/skills/guide")
        self.manifest_path.unlink()
        code, output, errors = self.run_install()
        self.assertEqual(code, 0, output + errors)
        self.assertEqual(json.loads(self.manifest_path.read_text())["artifacts"][0]["revision"], self.revision_a)

        revision_b = self.push_revision_b(skill_text="Guide B line.\n", binary=b"\x00B")
        code, output, errors = self.run_update(response="UPDATE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Updated successfully", output)
        self.assertEqual(json.loads(self.manifest_path.read_text())["artifacts"][0]["revision"], revision_b)

        revision_c = self.push_revision_b(skill_text="Guide C line.\n", binary=b"\x00C")
        manifest_after_update = self.manifest_path.read_bytes()
        current_target = self.project / ".claude/skills/guide/SKILL.md"
        current_target_stat = current_target.stat()
        shutil.rmtree(self.project / ".agents/skills/guide")
        code, output, errors = self.run_restore(response="RESTORE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn(revision_b, output)
        self.assertNotIn(revision_c, output)
        self.assertEqual(SETUPSMITH.tree_identity(self.project / ".agents/skills/guide")[0], self.digest(revision_b))
        self.assertEqual(current_target.stat().st_mtime_ns, current_target_stat.st_mtime_ns)
        self.assertEqual(self.manifest_path.read_bytes(), manifest_after_update)

    def test_restore_then_update_moves_from_pinned_revision_to_configured_ref(self):
        import shutil
        shutil.rmtree(self.project / ".agents/skills/guide")
        shutil.rmtree(self.project / ".claude/skills/guide")
        revision_b = self.push_revision_b(skill_text="Guide B line.\n", binary=b"\x00B")
        code, output, errors = self.run_restore(response="RESTORE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn(self.revision_a, output)
        self.assertEqual(SETUPSMITH.tree_identity(self.project / ".agents/skills/guide")[0], self.digest_a)
        self.assertEqual(json.loads(self.manifest_path.read_text())["artifacts"][0]["revision"], self.revision_a)

        code, output, errors = self.run_update(response="UPDATE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn(revision_b, output)
        self.assertEqual(SETUPSMITH.tree_identity(self.project / ".agents/skills/guide")[0], self.digest(revision_b))
        self.assertEqual(SETUPSMITH.tree_identity(self.project / ".claude/skills/guide")[0], self.digest(revision_b))

    def test_restore_does_not_rewrite_current_target_when_another_is_missing(self):
        import shutil
        shutil.rmtree(self.project / ".claude/skills/guide")
        current_file = self.project / ".agents/skills/guide/SKILL.md"
        before_stat = current_file.stat()
        before_bytes = current_file.read_bytes()
        before_manifest = self.manifest_path.read_bytes()
        code, output, errors = self.run_restore(response="RESTORE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Already restored and verified: .agents/skills/guide", output)
        after_stat = current_file.stat()
        self.assertEqual(current_file.read_bytes(), before_bytes)
        self.assertEqual((after_stat.st_ino, after_stat.st_mtime_ns), (before_stat.st_ino, before_stat.st_mtime_ns))
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)

    def test_restore_preserves_unrelated_managed_entry(self):
        import shutil
        other_source = self.source / "skills/other"
        other_source.mkdir(parents=True)
        (other_source / "SKILL.md").write_text(
            "---\nname: other\ndescription: Unrelated fixture skill.\n---\nOther.\n", encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-qm", "add unrelated skill")
        other_revision = self.git(self.source, "rev-parse", "HEAD")
        self.git(self.source, "push", "origin", "main")
        other_digest, other_hashes, _ = SETUPSMITH.tree_identity(other_source)
        other_target = self.project / ".agents/skills/other"
        shutil.copytree(other_source, other_target)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        other_entry = {"id": "skills/other", "source": "https://example.invalid/catalog.git",
                       "configured_ref": "refs/heads/main", "revision": other_revision,
                       "content_digest": other_digest, "files": other_hashes,
                       "targets": [{"assistant": "codex", "path": ".agents/skills/other",
                                    "state": "installed"}]}
        manifest["artifacts"].append(other_entry)
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        shutil.rmtree(self.project / ".claude/skills/guide")
        before_other = SETUPSMITH.tree_identity(other_target)
        before_entry = json.loads(self.manifest_path.read_text(encoding="utf-8"))["artifacts"][1]
        code, output, errors = self.run_restore(response="RESTORE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Restored and verified: .claude/skills/guide", output)
        self.assertEqual(SETUPSMITH.tree_identity(other_target), before_other)
        after_manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(after_manifest["artifacts"][1], before_entry)

    def test_configured_tag_ref_is_not_silently_switched_to_branch_head(self):
        self.git(self.source, "tag", "release-a", self.revision_a)
        self.git(self.source, "push", "origin", "refs/tags/release-a")
        self.push_revision_b()
        self.write_manifest(configured_ref="refs/tags/release-a")
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("configured ref: refs/tags/release-a", output)
        self.assertIn(f"current upstream: {self.revision_a} (fresh)", output)
        self.assertIn("CURRENT", output)
        self.assertNotIn("UPSTREAM_UPDATE", output)

    def test_unavailable_recorded_revision_is_not_replaced_with_current(self):
        self.write_manifest(revision="0" * 40)
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("SOURCE_UNAVAILABLE", output)
        self.assertIn("cannot retrieve recorded revision", output)
        self.assertIn("current upstream:", output)
        self.assertNotIn("UPSTREAM_UPDATE", output)
        self.assertNotIn("CURRENT", output)

    def test_invalid_manifest_and_symlink_conflicts_fail_clearly(self):
        self.write_manifest()
        malformed = json.loads(self.manifest_path.read_text())
        malformed["artifacts"].append(malformed["artifacts"][0])
        self.manifest_path.write_text(json.dumps(malformed), encoding="utf-8")
        code, _, errors = self.run_command()
        self.assertEqual(code, 2)
        self.assertIn("duplicate artifact identity", errors)
        self.write_manifest()
        import shutil
        shutil.rmtree(self.project / ".agents/skills/guide")
        outside = self.base / "outside"
        shutil.copytree(self.source / "skills/guide", outside)
        os.symlink(outside, self.project / ".agents/skills/guide")
        code, output, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("codex: DESTINATION_CONFLICT", output)
        self.assertTrue((outside / "SKILL.md").is_file())

    def test_update_preview_decline_approval_and_repeat_noop(self):
        revision_b = self.push_revision_b(skill_text="Guide B line.\n", binary=b"\x00B")
        before = self.tree_snapshot()
        code, preview, errors = self.run_update(preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn("SetupSmith update selection", preview)
        self.assertIn("skills/guide", preview)
        self.assertIn(revision_b, preview)
        self.assertIn("Binary resource", preview)
        self.assertEqual(self.tree_snapshot(), before)
        code, declined, errors = self.run_update(response="no\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Declined", declined)
        self.assertEqual(self.tree_snapshot(), before)
        code, updated, errors = self.run_update(response="UPDATE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Updated successfully", updated)
        for destination in (self.project / ".agents/skills/guide", self.project / ".claude/skills/guide"):
            self.assertEqual(SETUPSMITH.tree_identity(destination)[0], self.digest(revision_b))
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        entry = manifest["artifacts"][0]
        self.assertEqual(entry["revision"], revision_b)
        self.assertEqual(entry["files"], SETUPSMITH.tree_identity(self.source / "skills/guide")[1])
        updated_snapshot = self.tree_snapshot()
        code, again, errors = self.run_update(response="UPDATE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("No artifacts selected", again)
        self.assertEqual(self.tree_snapshot(), updated_snapshot)

    def digest(self, revision):
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory) / "source"
            self.git(self.source, "worktree", "add", "--quiet", "--detach", str(checkout), revision)
            try:
                return SETUPSMITH.tree_identity(checkout / "skills/guide")[0]
            finally:
                self.git(self.source, "worktree", "remove", "--force", str(checkout))

    def test_update_select_none_and_noninteractive_are_write_free(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        before = self.tree_snapshot()
        code, output, errors = self.run_update(selection=("--none",), response="UPDATE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("No artifacts selected", output)
        self.assertEqual(self.tree_snapshot(), before)
        code, _, errors = self.run_update(selection=("--all-safe",), interactive=False)
        self.assertEqual(code, 2)
        self.assertIn("requires interactive terminal approval", errors)
        self.assertEqual(self.tree_snapshot(), before)

    def test_update_can_select_one_artifact_and_preserves_other_managed_skills(self):
        other_source = self.source / "skills/other"
        other_source.mkdir(parents=True)
        (other_source / "SKILL.md").write_text(
            "---\nname: other\ndescription: Another fixture skill.\n---\nOther A.\n", encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-qm", "add other skill")
        revision = self.git(self.source, "rev-parse", "HEAD")
        self.git(self.source, "push", "origin", "main")
        digest, hashes, _ = SETUPSMITH.tree_identity(other_source)
        import shutil
        other_target = self.project / ".agents/skills/other"
        other_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(other_source, other_target)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"].append({"id": "skills/other", "source": "https://example.invalid/catalog.git",
                                      "configured_ref": "refs/heads/main", "revision": revision,
                                      "content_digest": digest, "files": hashes,
                                      "targets": [{"assistant": "codex", "path": ".agents/skills/other",
                                                   "state": "installed"}]})
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (self.source / "skills/guide/SKILL.md").write_text(
            "---\nname: guide\ndescription: Fixture comparison skill.\n---\nGuide B line.\n", encoding="utf-8")
        (other_source / "SKILL.md").write_text(
            "---\nname: other\ndescription: Another fixture skill.\n---\nOther B.\n", encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-qm", "update both skills")
        self.git(self.source, "push", "origin", "main")
        other_before = SETUPSMITH.tree_identity(other_target)[0]
        other_manifest_before = next(item for item in manifest["artifacts"] if item["id"] == "skills/other")
        code, output, errors = self.run_update(selection=("--skill", "guide"), response="UPDATE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Selected skills/guide", output)
        self.assertNotIn("Selected skills/other", output)
        self.assertEqual(SETUPSMITH.tree_identity(other_target)[0], other_before)
        updated = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        other_after = next(item for item in updated["artifacts"] if item["id"] == "skills/other")
        self.assertEqual(other_after, other_manifest_before)

    def test_update_select_all_safe_excludes_local_edits_and_unknown_baselines(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        (self.project / ".agents/skills/guide/references/helper.md").write_text("local change\n")
        before = self.tree_snapshot()
        code, output, errors = self.run_update(selection=("--all-safe",), preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn("target .agents/skills/guide is missing, unsafe, or differs", output)
        self.assertIn("No artifacts selected", output)
        self.assertEqual(self.tree_snapshot(), before)
        self.write_manifest(baseline_state="unknown")
        before_unknown = self.tree_snapshot()
        code, output, errors = self.run_update(selection=("--all-safe",), preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn("unknown baseline", output)
        self.assertEqual(self.tree_snapshot(), before_unknown)

    def test_update_stale_destination_and_upstream_removed_refusal(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        original_resolve = SETUPSMITH.resolve_source
        changed = False
        before_manifest = self.manifest_path.read_bytes()
        def change_destination_after_preview(source, configured_ref, checkout):
            nonlocal changed
            resolved = original_resolve(self.source if source == "https://example.invalid/catalog.git" else source,
                                        configured_ref, checkout)
            if changed:
                changed = True
                (self.project / ".agents/skills/guide/SKILL.md").write_text("concurrent change\n")
            else:
                changed = True
            return resolved
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(SETUPSMITH, "resolve_source", side_effect=change_destination_after_preview), \
                patch("builtins.input", return_value="UPDATE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["update", "--project", str(self.project), "--all-safe"])
        self.assertEqual(code, 2)
        self.assertIn("stale preview", errors.getvalue())
        self.assertIn("concurrent change", (self.project / ".agents/skills/guide/SKILL.md").read_text())
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertFalse(any("recovery" in target for target in manifest["artifacts"][0]["targets"]))

    def test_update_refuses_source_or_manifest_changes_after_preview(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        before_manifest = self.manifest_path.read_bytes()
        original_resolve = SETUPSMITH.resolve_source
        calls = 0
        def advance_source(source, configured_ref, checkout):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.write_source_tree("Guide C line.\n", "helper C line.\n", b"\x00C")
                self.git(self.source, "add", ".")
                self.git(self.source, "commit", "-qm", "revision C")
                self.git(self.source, "push", "origin", "main")
            return original_resolve(self.source if source == "https://example.invalid/catalog.git" else source,
                                    configured_ref, checkout)
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(SETUPSMITH, "resolve_source", side_effect=advance_source), \
                patch("builtins.input", return_value="UPDATE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["update", "--project", str(self.project), "--all-safe"])
        self.assertEqual(code, 2)
        self.assertIn("stale preview", errors.getvalue())
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)

        # A separate stale-manifest change is detected after the same preview boundary.
        self.push_revision_b(skill_text="Guide D line.\n")
        calls = 0
        before_files = {path: (self.project / path).read_bytes() for path in
                        (".agents/skills/guide/SKILL.md", ".claude/skills/guide/SKILL.md")}
        def alter_manifest(source, configured_ref, checkout):
            nonlocal calls
            result = original_resolve(self.source if source == "https://example.invalid/catalog.git" else source,
                                      configured_ref, checkout)
            calls += 1
            if calls == 2:
                current = json.loads(self.manifest_path.read_text(encoding="utf-8"))
                current["concurrent_change"] = True
                self.manifest_path.write_text(json.dumps(current), encoding="utf-8")
            return result
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(SETUPSMITH, "resolve_source", side_effect=alter_manifest), \
                patch("builtins.input", return_value="UPDATE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["update", "--project", str(self.project), "--all-safe"])
        self.assertEqual(code, 2, output.getvalue() + errors.getvalue())
        self.assertIn("manifest changed", errors.getvalue())
        for path, content in before_files.items():
            self.assertEqual((self.project / path).read_bytes(), content)

    def test_update_manifest_replace_failure_restores_all_targets(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        before_manifest = self.manifest_path.read_bytes()
        before_trees = {path: SETUPSMITH.tree_identity(self.project / path)[0] for path in
                        (".agents/skills/guide", ".claude/skills/guide")}
        original_replace = os.replace
        original_resolve = SETUPSMITH.resolve_source
        replace_calls = []
        def fail_manifest_replace(source, destination):
            replace_calls.append(str(destination))
            if str(destination).endswith("/.setupsmith/manifest.json"):
                raise OSError("injected manifest replacement failure")
            return original_replace(source, destination)
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(os, "replace", side_effect=fail_manifest_replace), \
                patch.object(SETUPSMITH, "resolve_source", side_effect=lambda source, ref, checkout: original_resolve(
                    self.source if source == "https://example.invalid/catalog.git" else source, ref, checkout)), \
                patch("builtins.input", return_value="UPDATE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["update", "--project", str(self.project), "--all-safe"])
        self.assertEqual(code, 2, output.getvalue() + errors.getvalue() + repr(replace_calls))
        self.assertIn("injected manifest replacement failure", errors.getvalue())
        self.assertEqual(self.manifest_path.read_bytes(), before_manifest)
        for path, digest in before_trees.items():
            self.assertEqual(SETUPSMITH.tree_identity(self.project / path)[0], digest)
        code, retry_output, retry_errors = self.run_update(response="UPDATE\n")
        self.assertEqual(code, 0, retry_errors)
        self.assertIn("Updated successfully", retry_output)
        updated = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertNotEqual(updated["artifacts"][0]["revision"], self.revision_a)

    def test_update_never_removes_upstream_deleted_skill(self):
        import shutil
        shutil.rmtree(self.source / "skills/guide")
        self.git(self.source, "add", "-A")
        self.git(self.source, "commit", "-qm", "remove upstream skill")
        self.git(self.source, "push", "origin", "main")
        before = self.tree_snapshot()
        code, output, errors = self.run_update(selection=("--all-safe",), preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn("UPSTREAM_REMOVED", output)
        self.assertIn("upstream skill removed; deletion is prohibited", output)
        self.assertEqual(self.tree_snapshot(), before)

    def test_update_rejects_special_files_in_managed_tree(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        fifo = self.project / ".agents/skills/guide/local-pipe"
        os.mkfifo(fifo)
        code, output, errors = self.run_update(selection=("--all-safe",), preview=True)
        self.assertEqual(code, 0, errors)
        self.assertIn("DESTINATION_CONFLICT", output)
        self.assertIn("target .agents/skills/guide is missing, unsafe, or differs", output)
        self.assertTrue(fifo.is_fifo())
        self.assertIn("Guide A line", (self.project / ".agents/skills/guide/SKILL.md").read_text())

    def test_update_preserves_unrestored_backup_outside_temporary_stage(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        original_replace = os.replace
        original_resolve = SETUPSMITH.resolve_source
        baseline_digest = self.digest(self.revision_a)
        def fail_codex_install_and_claude_restore(source, destination):
            source_path = str(source)
            destination_path = str(destination)
            if destination_path.endswith("/.agents/skills/guide") and "/staged-" in source_path:
                raise OSError("injected target placement failure")
            if destination_path.endswith("/.claude/skills/guide") and "/.setupsmith-recovery-" in source_path:
                raise OSError("injected target restore failure")
            return original_replace(source, destination)
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(os, "replace", side_effect=fail_codex_install_and_claude_restore), \
                patch.object(SETUPSMITH, "resolve_source", side_effect=lambda source, ref, checkout:
                             original_resolve(self.source if source == "https://example.invalid/catalog.git"
                                              else source, ref, checkout)), \
                patch("builtins.input", return_value="UPDATE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["update", "--project", str(self.project), "--all-safe"])
        self.assertEqual(code, 2)
        self.assertIn("original backups preserved", errors.getvalue())
        recovery_dirs = list(self.project.glob(".setupsmith-recovery-*"))
        self.assertEqual(len(recovery_dirs), 1)
        backups = list(recovery_dirs[0].iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual(SETUPSMITH.tree_identity(backups[0])[0], baseline_digest)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["artifacts"][0]["revision"], self.revision_a)
        recovery_targets = [target for target in manifest["artifacts"][0]["targets"] if "recovery" in target]
        self.assertEqual(len(recovery_targets), 1)
        self.assertEqual(recovery_targets[0]["recovery"]["state"], "incomplete")
        code, report, errors = self.run_command()
        self.assertEqual(code, 0, errors)
        self.assertIn("RECOVERY_INCOMPLETE", report)
        self.assertIn("recovery_path", report)

    def test_update_rollback_preserves_concurrent_edit_and_records_incomplete_target(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        original_replace = os.replace
        original_resolve = SETUPSMITH.resolve_source
        def edit_codex_then_fail_claude(source, destination):
            source_text, destination_text = str(source), str(destination)
            if destination_text.endswith("/.agents/skills/guide") and "/staged-" in source_text:
                claude_skill = self.project / ".claude/skills/guide/SKILL.md"
                claude_skill.write_text(claude_skill.read_text() + "concurrent edit\n", encoding="utf-8")
                raise OSError("injected second target placement failure")
            if (destination_text.endswith("/.claude/skills/guide")
                    and "/.setupsmith-recovery-" in source_text):
                raise OSError("injected rollback refusal")
            return original_replace(source, destination)
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(os, "replace", side_effect=edit_codex_then_fail_claude), \
                patch.object(SETUPSMITH, "resolve_source", side_effect=lambda source, ref, checkout:
                             original_resolve(self.source if source == "https://example.invalid/catalog.git"
                                              else source, ref, checkout)), \
                patch("builtins.input", return_value="UPDATE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["update", "--project", str(self.project), "--all-safe"])
        self.assertEqual(code, 2)
        self.assertIn("did not overwrite concurrent destination .claude/skills/guide", errors.getvalue())
        self.assertIn("target outcomes", errors.getvalue())
        self.assertIn("RECOVERY_INCOMPLETE", errors.getvalue())
        claude_skill = self.project / ".claude/skills/guide/SKILL.md"
        self.assertIn("concurrent edit", claude_skill.read_text())
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["artifacts"][0]["revision"], self.revision_a)
        self.assertTrue(any(target.get("recovery", {}).get("state") == "incomplete"
                            for target in manifest["artifacts"][0]["targets"]))
        self.assertEqual(SETUPSMITH.tree_identity(self.project / ".agents/skills/guide")[0], self.digest(self.revision_a))

    def test_update_retry_after_reconciliation_clears_recovery_marker(self):
        revision_b = self.push_revision_b(skill_text="Guide B line.\n")
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        for target in manifest["artifacts"][0]["targets"]:
            target["recovery"] = {"state": "incomplete", "observed_state": "present"}
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        code, output, errors = self.run_update(selection=("--all-safe",), response="UPDATE\n")
        self.assertEqual(code, 0, errors)
        self.assertIn("Updated successfully", output)
        updated = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(updated["artifacts"][0]["revision"], revision_b)
        self.assertTrue(all("recovery" not in target for target in updated["artifacts"][0]["targets"]))

    def test_update_detects_concurrent_edit_while_staging_original_backup(self):
        self.push_revision_b(skill_text="Guide B line.\n")
        original_replace = os.replace
        original_resolve = SETUPSMITH.resolve_source
        def edit_before_backup(source, destination):
            if str(destination).endswith("backup-0"):
                target_file = self.project / ".claude/skills/guide/SKILL.md"
                target_file.write_text(target_file.read_text() + "concurrent edit\n", encoding="utf-8")
            return original_replace(source, destination)
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(os, "replace", side_effect=edit_before_backup), \
                patch.object(SETUPSMITH, "resolve_source", side_effect=lambda source, ref, checkout:
                             original_resolve(self.source if source == "https://example.invalid/catalog.git"
                                              else source, ref, checkout)), \
                patch("builtins.input", return_value="UPDATE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["update", "--project", str(self.project), "--all-safe"])
        self.assertEqual(code, 2)
        self.assertIn("destination changed while being staged", errors.getvalue())
        self.assertIn("restored changed content without overwriting it", errors.getvalue())
        target_file = self.project / ".claude/skills/guide/SKILL.md"
        self.assertIn("concurrent edit", target_file.read_text())
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["artifacts"][0]["revision"], self.revision_a)
        self.assertTrue(any(target.get("recovery", {}).get("state") == "incomplete"
                            for target in manifest["artifacts"][0]["targets"]))

    def test_update_batch_reports_rollback_for_each_independent_artifact(self):
        other_source = self.source / "skills/other"
        other_source.mkdir(parents=True)
        (other_source / "SKILL.md").write_text(
            "---\nname: other\ndescription: Independent fixture skill.\n---\nOther A.\n", encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-qm", "add independent skill")
        revision_a = self.git(self.source, "rev-parse", "HEAD")
        self.git(self.source, "push", "origin", "main")
        other_digest, other_hashes, _ = SETUPSMITH.tree_identity(other_source)
        other_target = self.project / ".agents/skills/other"
        other_target.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copytree(other_source, other_target)
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"].append({"id": "skills/other", "source": "https://example.invalid/catalog.git",
                                      "configured_ref": "refs/heads/main", "revision": revision_a,
                                      "content_digest": other_digest, "files": other_hashes,
                                      "targets": [{"assistant": "codex", "path": ".agents/skills/other",
                                                   "state": "installed"}]})
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (self.source / "skills/guide/SKILL.md").write_text(
            "---\nname: guide\ndescription: Fixture comparison skill.\n---\nGuide B line.\n", encoding="utf-8")
        (other_source / "SKILL.md").write_text(
            "---\nname: other\ndescription: Independent fixture skill.\n---\nOther B.\n", encoding="utf-8")
        self.git(self.source, "add", ".")
        self.git(self.source, "commit", "-qm", "update independent skills")
        self.git(self.source, "push", "origin", "main")
        original_replace = os.replace
        original_resolve = SETUPSMITH.resolve_source
        def fail_other_install(source, destination):
            if str(destination).endswith("/.agents/skills/other") and "/staged-" in str(source):
                raise OSError("injected second artifact failure")
            return original_replace(source, destination)
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(os, "replace", side_effect=fail_other_install), \
                patch.object(SETUPSMITH, "resolve_source", side_effect=lambda source, ref, checkout:
                             original_resolve(self.source if source == "https://example.invalid/catalog.git"
                                              else source, ref, checkout)), \
                patch("builtins.input", return_value="UPDATE"), \
                patch.object(sys, "stdin", type("TTY", (io.StringIO,), {"isatty": lambda self: True})("")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = SETUPSMITH.main(["update", "--project", str(self.project), "--all-safe"])
        self.assertEqual(code, 2)
        self.assertIn(".agents/skills/other: ROLLED BACK", errors.getvalue())
        self.assertIn(".agents/skills/guide: ROLLED BACK", errors.getvalue())
        self.assertEqual(SETUPSMITH.tree_identity(self.project / ".agents/skills/guide")[0], self.digest(self.revision_a))
        self.assertEqual(SETUPSMITH.tree_identity(other_target)[0], other_digest)
        after = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual({entry["id"]: entry["revision"] for entry in after["artifacts"]},
                         {"skills/guide": self.revision_a, "skills/other": revision_a})

    def test_malicious_source_scheme_and_ref_are_rejected_before_git_access(self):
        self.write_manifest(source="ext://command/example")
        with patch.object(SETUPSMITH, "resolve_source") as resolve:
            code, _, errors = self.run_command()
        self.assertEqual(code, 2)
        self.assertIn("invalid source locator", errors)
        resolve.assert_not_called()
        self.write_manifest(configured_ref="--upload-pack=command")
        with patch.object(SETUPSMITH, "resolve_source") as resolve:
            code, _, errors = self.run_command()
        self.assertEqual(code, 2)
        self.assertIn("unsafe configured ref", errors)
        resolve.assert_not_called()

    def test_repeated_check_is_stable_and_read_only(self):
        before = self.tree_snapshot()
        first = self.run_command()
        second = self.run_command()
        self.assertEqual(first, second)
        self.assertEqual(self.tree_snapshot(), before)
        diff = self.run_command("diff")
        self.assertEqual(self.tree_snapshot(), before)

if __name__ == "__main__":
    unittest.main()
