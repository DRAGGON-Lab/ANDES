import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("candidate", ROOT / "adapters/codex/candidate.py")
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


class CoreTests(unittest.TestCase):
    def test_native_frontmatter_matches_the_catalog(self):
        data = candidate.load_core(ROOT)
        for item in data["components"]:
            if item["kind"] == "skill":
                text = (ROOT / item["path"]).read_text()
                header, separator, body = text.partition("\n---\n")
                self.assertTrue(text.startswith("---\n") and separator and body.strip())
                metadata = yaml.safe_load(header.removeprefix("---\n"))
                self.assertEqual(metadata["name"], item["invocation"])
                self.assertEqual(metadata["description"], item["description"])

    def test_all_four_direct_targets_are_valid(self):
        data = candidate.load_core(ROOT)
        expected = {"andes-orient", "andes-contract", "andes-verify", "andes-handoff"}
        self.assertEqual({c["invocation"] for c in data["components"] if c["kind"] == "skill"}, expected)
        for name in expected:
            selected = candidate.select_skill(ROOT, name)
            self.assertEqual(selected["invocation"], name)
        with self.assertRaisesRegex(ValueError, "unknown"):
            candidate.select_skill(ROOT, "unavailable")

    def test_projection_is_temporary_and_content_preserving(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            manifest = candidate.project_core(ROOT, project)
            for entry in manifest["files"]:
                self.assertEqual((ROOT / entry["source"]).read_bytes(),
                                 (project / entry["destination"]).read_bytes())
            self.assertIn((ROOT / "CONSTITUTION.md").read_text(), (project / "AGENTS.md").read_text())
            self.assertEqual(len(list((project / ".agents/skills").glob("*/SKILL.md"))), 4)
            self.assertTrue((project / ".agents/skills/andes-orient/references/revision-mismatch.md").is_file())
            with self.assertRaises(ValueError):
                candidate.project_core(ROOT, project)

    def test_source_repository_is_not_an_install_target(self):
        with self.assertRaises(ValueError):
            candidate.project_core(ROOT, ROOT / ".agents")

    def test_native_selection_rejects_ambiguous_names(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            candidate.project_core(ROOT, project)
            path = str(project / ".agents/skills/andes-verify/SKILL.md")
            entries = [{"name": "andes-verify", "path": path}]
            self.assertEqual(candidate.native_skill(ROOT, project, "andes-verify", entries)["path"], str(Path(path).resolve()))
            with self.assertRaisesRegex(ValueError, "ambiguous"):
                candidate.native_skill(ROOT, project, "andes-verify", entries * 2)
            with self.assertRaises(ValueError):
                candidate.native_skill(ROOT, project, "andes-verify", [
                    {"name": "andes-verify", "path": str(ROOT / "CONSTITUTION.md")}])
