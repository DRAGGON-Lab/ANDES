import importlib.util
import logging
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_secrets", ROOT / "scripts/check_secrets.py")
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class DevelopmentChecks(unittest.TestCase):
    def test_secret_check_pass_fail_and_redaction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "fixture.txt"
            command = [sys.executable, str(ROOT / "scripts/check_secrets.py"),
                       "--root", directory, path.name]
            path.write_text("ordinary public documentation\n")
            clean = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(clean.returncode, 0, clean.stderr)
            synthetic_value = "andes" + "-synthetic-credential-for-negative-test"
            path.write_text("password = '" + synthetic_value + "'\n")
            bad = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1, bad.stderr)
            self.assertIn('"line": 1', bad.stderr)
            self.assertNotIn(synthetic_value, bad.stdout + bad.stderr)
            self.assertNotIn(path.read_text().strip(), bad.stdout + bad.stderr)

    def test_unscannable_input_is_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/check_secrets.py"),
                 "--root", directory, "missing.txt"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)

    def test_catalog_ci_fixture_statuses(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/check_catalog_fixtures.py")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("seven negative CLI statuses 1", result.stdout)

    def test_pattern_scan_does_not_verify_credentials_online(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.txt"
            path.write_text("token = '" + "ghp_" + "a" * 36 + "'\n")
            with patch("requests.sessions.Session.request", side_effect=AssertionError("network forbidden")):
                findings = scanner.scan(directory, [path.name])
            self.assertTrue(findings)

    def test_upstream_diagnostics_never_emit_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "public.txt"
            path.write_text("public fixture")
            logger = logging.getLogger("detect-secrets")
            original_state = logger.disabled
            with self.assertNoLogs(logger, level="ERROR"):
                with patch.object(scanner.SecretsCollection, "scan_file",
                                  side_effect=lambda filename: logger.error("synthetic-sensitive-diagnostic")):
                    scanner.scan(directory, [path.name])
            self.assertEqual(logger.disabled, original_state)

    def test_workflow_authority_boundaries(self):
        # BaseLoader preserves the YAML 1.2 event key 'on' as a string.
        workflow = yaml.load((ROOT / ".github/workflows/foundation.yml").read_text(),
                             Loader=yaml.BaseLoader)
        self.assertEqual(set(workflow["on"]), {"pull_request", "push"})
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        job = workflow["jobs"]["foundation"]
        self.assertNotIn("permissions", job)
        self.assertEqual(job["timeout-minutes"], "10")
        steps = job["steps"]
        for step in steps:
            if "uses" in step:
                self.assertRegex(step["uses"], r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+@[0-9a-f]{40}$")
        checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["persist-credentials"], "false")
        self.assertNotRegex((ROOT / ".github/workflows/foundation.yml").read_text(),
                            r"\$\{\{[^}]*\bsecrets\.")


if __name__ == "__main__":
    unittest.main()
