import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/catalog"
spec = importlib.util.spec_from_file_location("validate_catalog", ROOT / "scripts/validate_catalog.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.good = json.loads((FIXTURES / "valid.json").read_text())

    def test_minimal_core_and_direct_invocation(self):
        self.assertEqual(module.validate(self.good, FIXTURES), [])
        self.assertEqual(module.compose(self.good, FIXTURES, component="andes.fixture.verify@1.0.0"),
                         ["andes.fixture.norms@1.0.0", "andes.fixture.verify@1.0.0"])

    def test_published_invalid_fixtures(self):
        for path in sorted((FIXTURES / "invalid").glob("*.json")):
            with self.subTest(path=path.name):
                fixture = json.loads(path.read_text())
                errors = module.validate(fixture["catalog"], FIXTURES)
                self.assertTrue(any(fixture["expected_error"] in e for e in errors), errors)

    def test_dependency_closure_is_deterministic(self):
        data = copy.deepcopy(self.good)
        data["profiles"].append({"id": "andes.fixture.extra", "version": "1.0.0",
                                 "description": "Synthetic profile",
                                 "components": ["andes.fixture.verify@1.0.0"]})
        self.assertEqual(module.validate(data, FIXTURES), [])
        self.assertEqual(module.compose(data, FIXTURES, profiles=["andes.fixture.extra@1.0.0"]),
                         ["andes.fixture.norms@1.0.0", "andes.fixture.verify@1.0.0"])

    def test_unknown_selection_is_rejected(self):
        with self.assertRaises(ValueError):
            module.compose(self.good, FIXTURES, profiles=["unknown@1.0.0"])

    def test_path_escape_and_missing_content(self):
        for path in ("../outside.md", "/etc/passwd", "content/missing.md"):
            data = copy.deepcopy(self.good)
            data["components"][0]["path"] = path
            self.assertTrue(any("content path" in e for e in module.validate(data, FIXTURES)))

    def test_native_metadata_is_not_canonical(self):
        data = copy.deepcopy(self.good)
        data["components"][1]["codex"] = {"enabled": True}
        self.assertTrue(module.validate(data, FIXTURES))

    def test_unsupported_and_blank_licenses_are_rejected(self):
        for license_id in (" ", "made-up-license", "LicenseRef-ARR"):
            data = copy.deepcopy(self.good)
            data["components"][1]["provenance"]["license"] = license_id
            with self.assertRaisesRegex(ValueError, "unresolved license"):
                module.compose(data, FIXTURES)

    def test_profile_pair_conflict_is_not_silently_overridden(self):
        data = copy.deepcopy(self.good)
        for name in ("a", "b"):
            item = copy.deepcopy(data["components"][1])
            item.update(id="andes.fixture." + name, kind="tool")
            item.pop("invocation")
            data["components"].append(item)
            data["profiles"].append({"id": "andes.profile." + name, "version": "1.0.0",
                                     "description": name, "components": [module.identity(item)]})
        data["components"][-1]["conflicts"] = ["andes.fixture.a@1.0.0"]
        self.assertEqual(module.validate(data, FIXTURES), [])
        with self.assertRaisesRegex(ValueError, "incompatible composition"):
            module.compose(data, FIXTURES, profiles=["andes.profile.a@1.0.0", "andes.profile.b@1.0.0"])

    def test_duplicate_invocations_are_rejected(self):
        data = copy.deepcopy(self.good)
        item = copy.deepcopy(data["components"][1])
        item["id"] = "andes.fixture.other"
        data["components"].append(item)
        self.assertIn("duplicate invocation", module.validate(data, FIXTURES))

    def test_schema_is_valid_and_unsupported_version_is_rejected(self):
        module.Draft202012Validator.check_schema(json.loads(module.SCHEMA.read_text()))
        with self.assertRaisesRegex(ValueError, "schema"):
            module.compose({"schema_version": "2.0.0"}, FIXTURES)

    def test_cli_exit_status_and_json_output(self):
        script = str(ROOT / "scripts/validate_catalog.py")
        good = subprocess.run([sys.executable, script, str(FIXTURES / "valid.json")],
                              capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout), {"selected": ["andes.fixture.norms@1.0.0"]})
        for value in ("{", json.dumps({"schema_version": "unknown"})):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.json"
                path.write_text(value)
                bad = subprocess.run([sys.executable, script, str(path)],
                                     capture_output=True, text=True)
                self.assertEqual(bad.returncode, 1)
                self.assertEqual(bad.stdout, "")
                self.assertTrue(bad.stderr)

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / "outside.md"
            outside.write_text("synthetic external content")
            content_root = Path(directory) / "root"
            content_root.mkdir()
            (content_root / "link.md").symlink_to(outside)
            data = copy.deepcopy(self.good)
            for item in data["components"]:
                item["path"] = "link.md"
            self.assertTrue(any("content path" in e for e in module.validate(data, content_root)))

    def test_nul_path_returns_validation_error(self):
        data = copy.deepcopy(self.good)
        data["components"][1]["path"] = "content/\u0000bad.md"
        self.assertTrue(any("content path" in e for e in module.validate(data, FIXTURES)))

    def test_identifier_fields_reject_trailing_newline(self):
        for field in ("id", "version", "invocation"):
            data = copy.deepcopy(self.good)
            data["components"][1][field] += "\n"
            self.assertTrue(any("schema:" in e for e in module.validate(data, FIXTURES)), field)
        data = copy.deepcopy(self.good)
        data["core"][0] += "\n"
        self.assertTrue(any("schema:" in e for e in module.validate(data, FIXTURES)))
        data = copy.deepcopy(self.good)
        data["components"][1]["provenance"] = {
            "kind": "upstream", "license": "MIT", "attribution": "Synthetic author",
            "source_url": "https://example.invalid/source", "source_path": "SKILL.md",
            "revision": "0" * 40 + "\n", "review_status": "accepted",
            "review_evidence": "synthetic fixture, no real import clearance",
        }
        self.assertTrue(any("schema:" in e for e in module.validate(data, FIXTURES)))


if __name__ == "__main__":
    unittest.main()
