import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "setupsmith.py"


class CatalogDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "catalog"
        self.root.mkdir()
        (self.root / "registry.yaml").write_text(
            "version: 0.1.0\nskills:\n  guide:\n    status: testing\n"
            "agents:\n  helper:\n    status: accepted\n",
            encoding="utf-8",
        )
        (self.root / "skills" / "guide" / "references").mkdir(parents=True)
        (self.root / "skills" / "guide" / "SKILL.md").write_text("---\nname: guide\n---\n", encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
