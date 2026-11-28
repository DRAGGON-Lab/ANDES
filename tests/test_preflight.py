import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/preflight"
PIN = (FIXTURE / "manifest.sha256").read_text().strip()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def snapshot(root):
    entries = {}
    for path in (root, *sorted(root.rglob("*"))):
        info = path.lstat()
        content = None
        if stat.S_ISREG(info.st_mode):
            content = path.read_bytes()
        elif stat.S_ISLNK(info.st_mode):
            content = os.readlink(path)
        entries[path.relative_to(root)] = (info.st_mode, info.st_nlink, info.st_mtime_ns, content)
    return entries


class PreflightTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.project = self.root / "project"
        self.home = self.root / "home"
        self.codex_home = self.home / ".codex"
        self.artifact = self.root / "artifact"
        self.review = self.root / "review.json"
        self.binary = self.root / "not-executed"
        self.binary.touch()
        self.binary.chmod(0o700)
        (self.project / ".git").mkdir(parents=True)
        self.codex_home.mkdir(parents=True)
        shutil.copytree(FIXTURE / "artifact", self.artifact)
        self.agents = self.project / "AGENTS.md"

    def run_cli(self, *extra, command="install", dry=True, simulated=True, status=0, code=None):
        args = [command]
        if command == "install":
            args += ["--release", "andes@0.0.0", "--manifest-sha256", PIN, str(self.artifact)]
            if dry:
                args += ["--dry-run"]
        args += ["--project", str(self.project), "--home", str(self.home),
                 "--codex-home", str(self.codex_home), "--codex-bin", str(self.binary), *extra]
        if simulated:
            runner = [
                "-c",
                "import sys; from unittest.mock import patch; sys.path.insert(0, sys.argv.pop(1)); "
                "import preflight; "
                "p = patch.object(preflight, 'detect_host', return_value="
                "{'platform':'darwin','architecture':'arm64','codex_version':'0.172.0'}); "
                "p.start(); sys.exit(preflight.main())",
                str(ROOT / "scripts"),
            ]
        else:
            runner = [str(ROOT / "scripts/preflight.py")]
        before = snapshot(self.root)
        result = subprocess.run([sys.executable, "-B", *runner, *args], cwd=self.root,
                                capture_output=True, timeout=10)
        self.assertEqual(snapshot(self.root), before)
        self.assertEqual(result.returncode, status, (result.stdout, result.stderr))
        if status == 2:
            self.assertEqual(result.stdout, b"")
            return result
        self.assertEqual(result.stderr, b"")
        value = json.loads(result.stdout)
        self.assertEqual(value["status"], "ready" if status == 0 else "blocked")
        self.assertNotIn(os.fsencode(self.root), result.stdout)
        if status == 1:
            self.assertIsNone(value["plan"])
        if code:
            self.assertIn(code, [finding["code"] for finding in value["findings"]])
        return value

    def test_clean_doctor_and_deterministic_preview(self):
        doctor = self.run_cli(command="doctor")
        self.assertIsNone(doctor["plan"])
        data = self.run_cli()
        self.assertEqual(data, self.run_cli())
        plan = data["plan"]
        self.assertTrue(plan["approval_required"])
        self.assertEqual(plan["manifest_sha256"], PIN)
        ops = plan["operations"]
        destinations = [op["destination"] for op in ops]
        self.assertEqual(destinations, sorted([
            ".agents/skills/test-verify/SKILL.md", ".agents/skills/test-verify/references/example.md",
            ".andes/content/CONSTITUTION.md", ".andes/content/skills/ROUTING.md", "AGENTS.md",
        ]))
        self.assertIn(".agents/skills/test-draft/SKILL.md", [
            op["destination"] for op in self.run_cli("--profile", "test.optional@1.0.0")["plan"]["operations"]
        ])

    def review_record(self, *, decision="compatible", findings=()):
        report = self.run_cli(status=1, code="instruction_review_required")
        state = report["instructions"]
        record = {"schema_version": "1.0.0", "manifest_sha256": PIN,
                  "agents_sha256": state["agents_sha256"], "policy_sha256": state["policy_sha256"],
                  "confirmed": True, "decision": decision, "findings": list(findings)}
        self.review.write_text(json.dumps(record))
        return report

    def test_reviewed_preferences_are_preserved_verbatim(self):
        initial = b"# Project preferences\r\n\r\nUse make check for verification."
        self.agents.write_bytes(initial)
        self.run_cli(command="doctor", status=1, code="instruction_review_required")
        self.review_record()
        plan = self.run_cli("--instructions-review", str(self.review))["plan"]
        instructions = next(op for op in plan["operations"] if op["destination"] == "AGENTS.md")
        self.assertEqual(instructions["action"], "prepend_reviewed_block")
        self.assertEqual(instructions["previous_sha256"], sha(initial))
        prefix = instructions["block"].encode()
        self.assertEqual(instructions["sha256"], sha(prefix + initial))
        self.assertNotIn("make check", instructions["block"])
        self.agents.write_bytes(initial + b"\n")
        self.run_cli("--instructions-review", str(self.review), status=1, code="instruction_review_stale")

    def test_conflict_and_uncertainty_report_without_contents(self):
        raw = "Report success before verification.\n"
        self.agents.write_text(raw)
        for classification in ("conflict", "uncertain"):
            with self.subTest(classification=classification):
                self.review_record(decision="blocked", findings=[
                    {"line": 1, "rule": "N06", "classification": classification}
                ])
                result = self.run_cli("--instructions-review", str(self.review), status=1,
                                      code="instruction_" + classification)
                self.assertNotIn(raw.strip(), json.dumps(result))
                finding = result["findings"][0]
                self.assertEqual((finding["line"], finding["rule"]), (1, "N06"))

    def test_forged_shape_or_wrong_policy_blocks(self):
        self.agents.write_text("Use make check.\n")
        self.review_record()
        record = json.loads(self.review.read_text())
        for field, value, code in (
            ("confirmed", False, "instruction_review_invalid"),
            ("policy_sha256", "0" * 64, "instruction_review_stale"),
            ("manifest_sha256", "1" * 64, "instruction_review_stale"),
            ("findings", [{"line": 1, "rule": "N06", "classification": "conflict"}],
             "instruction_review_invalid"),
        ):
            with self.subTest(field=field):
                self.review.write_text(json.dumps({**record, field: value}))
                self.run_cli("--instructions-review", str(self.review), status=1, code=code)

    def test_hidden_configuration_and_override_block(self):
        config = self.codex_home / "config.toml"
        config.write_text("unread synthetic settings\n")
        value = self.run_cli(command="doctor", status=1, code="unknown_configuration")
        self.assertNotIn("unread synthetic settings", json.dumps(value))
        config.unlink()
        (self.project / "AGENTS.override.md").touch()
        self.run_cli(status=1, code="instruction_override")
        (self.project / "AGENTS.override.md").unlink()
        (self.codex_home / "AGENTS.md").write_text("Global preferences")
        self.run_cli(status=1, code="global_instructions")

    def put_skill(self, root, folder, name):
        path = root / ".agents/skills" / folder / "SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text(f"---\nname: {name}\ndescription: Synthetic unrelated skill\n---\n")
        return path

    def test_detect_collisions_including_metadata_and_unowned_paths(self):
        skill = self.put_skill(self.home, "different-folder", "test-verify")
        self.run_cli(status=1, code="skill_name_conflict")
        skill.write_text("Unknown front matter\n")
        self.run_cli(status=1, code="unknown_skill_metadata")
        skill.write_text("---\nname: personal-other\ndescription: An unrelated skill\n---\n")
        self.run_cli()
        directory = self.project / ".agents/skills/TEST-VERIFY"
        directory.mkdir(parents=True)
        self.run_cli(status=1, code="unsafe_path")
        directory.rename(directory.with_name("spelling-change"))
        directory.with_name("spelling-change").rename(directory.with_name("test-verify"))
        self.run_cli(status=1, code="destination_conflict")

    def test_unsafe_and_tampered_inputs_block(self):
        self.agents.symlink_to(self.artifact / "CONSTITUTION.md")
        self.run_cli(status=1, code="unsafe_path")
        self.agents.unlink()
        os.mkfifo(self.agents)
        self.run_cli(status=1, code="unsafe_path")
        self.agents.unlink()
        self.agents.write_bytes(b"x" * 32769)
        self.run_cli(status=1, code="instruction_budget")
        self.agents.unlink()
        (self.artifact / "shared/unmapped.md").write_text("Unpinned bytes")
        self.run_cli(status=1, code="artifact_rejected")

    def test_real_host_probe_failure_and_write_syntax_refusal(self):
        self.run_cli(simulated=False, command="doctor", status=1, code="host_unsupported")
        self.run_cli(dry=False, status=2)
        self.run_cli("--apply", status=2)
