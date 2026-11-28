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

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/release"
PIN = (FIXTURE / "manifest.sha256").read_text().strip()
FORMAL = "andes.profile.formal@1.0.0"
VERIFY = "andes.profile.verify@1.1.0"
FAST = "andes.profile.fast@1.0.0"


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


class ReleaseCliTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.work = Path(directory.name)
        self.artifact = self.work / "artifact"
        self.reset_artifact()
        self.home = self.work / "home"
        self.codex_home = self.home / ".codex"
        self.codex_home.mkdir(parents=True)
        (self.codex_home / "config.toml").write_text("synthetic home sentinel\n")
        self.script = ROOT / "scripts/resolve_release.py"
        self.pin = PIN
        self.target = {
            "--release": "andes@0.0.0",
            "--adapter": "codex-project-local@1.0.0",
            "--runtime-version": "0.172.0",
            "--platform": "darwin",
            "--architecture": "arm64",
        }

    def reset_artifact(self):
        if self.artifact.exists():
            shutil.rmtree(self.artifact)
        shutil.copytree(FIXTURE / "artifact", self.artifact)

    def document(self, name):
        return json.loads((self.artifact / name).read_bytes())

    def write(self, name, value):
        raw = (json.dumps(value, indent=2) + "\n").encode()
        (self.artifact / name).write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def repin(self, manifest):
        self.pin = self.write("manifest.json", manifest)

    def update_record(self, key, change):
        manifest = self.document("manifest.json")
        path = manifest[key]["path"]
        record = self.document(path)
        change(record)
        manifest[key]["sha256"] = self.write(path, record)
        self.repin(manifest)

    def run_cli(self, *profiles, omit_pin=False, artifact=None, extra=()):
        target = dict(self.target)
        if not omit_pin:
            target["--manifest-sha256"] = self.pin
        command = [sys.executable, str(self.script), str(artifact or self.artifact)]
        for option, value in target.items():
            command.extend((option, value))
        for profile in profiles:
            command.extend(("--profile", profile))
        before = (snapshot(self.artifact), snapshot(self.home))
        result = subprocess.run(
            command + list(extra),
            cwd=self.work,
            env={**os.environ, "HOME": str(self.home), "CODEX_HOME": str(self.codex_home)},
            capture_output=True,
            timeout=10,
        )
        self.assertEqual((snapshot(self.artifact), snapshot(self.home)), before)
        return result

    def accept(self, *profiles, **kwargs):
        result = self.run_cli(*profiles, **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        return result.stdout

    def reject(self, diagnostic, *profiles, status=1, **kwargs):
        result = self.run_cli(*profiles, **kwargs)
        self.assertEqual(result.returncode, status, result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertIn(diagnostic, result.stderr.decode())

    def test_pinned_core_and_handoff(self):
        output = json.loads(self.accept())
        manifest = self.document("manifest.json")
        self.assertEqual(output["schema_version"], "1.0.0")
        self.assertEqual(output["release"], "andes@0.0.0")
        self.assertEqual(output["source"], manifest["source"])
        self.assertEqual(output["manifest_sha256"], PIN)
        self.assertEqual(output["catalog"], manifest["catalog"])
        self.assertEqual(output["profiles"], [])
        self.assertEqual(output["components"], [
            {"identity": "andes.fixture.norms@1.0.0", "kind": "norm", **manifest["files"][0]},
        ])
        self.assertEqual(output["resources"], [manifest["files"][-1]])
        self.assertEqual(output["provenance"], manifest["provenance"])
        self.assertEqual(output["adapter"], {
            "identity": "codex-project-local@1.0.0", **manifest["adapter"],
            "runtime": {"id": "codex-cli", "version": "0.172.0"},
            "platform": "darwin", "architecture": "arm64",
        })

    def test_repeat_and_profile_reordering_are_byte_identical(self):
        output = self.accept(FORMAL, VERIFY)
        self.assertEqual(self.accept(VERIFY, FORMAL, FORMAL), output)
        self.assertEqual(self.accept(FORMAL, VERIFY), output)
        relocated = self.work / "relocated"
        shutil.copytree(self.artifact, relocated)
        self.assertEqual(self.accept(FORMAL, VERIFY, artifact=relocated), output)
        content = json.loads(output)
        self.assertEqual(content["profiles"], [FORMAL, VERIFY])
        self.assertEqual([item["identity"] for item in content["components"]], [
            "andes.fixture.formal@1.0.0", "andes.fixture.norms@1.0.0", "andes.fixture.verify@2.0.0",
        ])
        self.assertEqual(json.loads(self.accept(FORMAL))["components"], content["components"])
        self.assertNotIn(str(self.work).encode(), output)

    def test_missing_malformed_and_mismatched_pin(self):
        self.reject("--manifest-sha256", omit_pin=True, status=2)
        self.reject("unrecognized arguments", extra=("--unexpected",), status=2)
        for self.pin in (PIN.upper(), "latest", PIN + "\n"):
            self.reject("lowercase SHA-256")
        (self.artifact / "manifest.json").write_bytes(b"not JSON")
        self.pin = PIN
        self.reject("manifest.json: SHA-256 mismatch")

    def test_integrity_checks_include_unselected_content_and_metadata(self):
        for path in ("catalog.json", "content/norms.md", "content/fast.md", "metadata/adapter.json",
                     "metadata/provenance.md", "content/references/checklist.md"):
            with self.subTest(path=path):
                self.reset_artifact()
                file = self.artifact / path
                file.write_bytes(file.read_bytes() + b"tampered")
                self.reject(path + ": SHA-256 mismatch")

    def test_inventory_rejects_missing_and_undeclared_entries(self):
        resource = self.artifact / "content/references/checklist.md"
        resource.unlink()
        self.reject("missing entry: content/references/checklist.md")
        self.reset_artifact()
        (self.artifact / ".undeclared").write_text("extra")
        self.reject("undeclared entry: .undeclared")
        self.reset_artifact()
        (self.artifact / "empty").mkdir()
        self.reject("undeclared entry: empty")
        self.reset_artifact()
        (self.artifact / "manifest.json").unlink()
        self.reject("manifest.json")

    def test_duplicate_json_members_are_refused(self):
        for path, key in (("manifest.json", "manifest"), ("catalog.json", "catalog"),
                          ("metadata/adapter.json", "adapter")):
            with self.subTest(key=key):
                self.reset_artifact()
                file = self.artifact / path
                raw = file.read_bytes().replace(b"{", b'{"duplicate": 1, "duplicate": 2,', 1)
                file.write_bytes(raw)
                digest = hashlib.sha256(raw).hexdigest()
                if key == "manifest":
                    self.pin = digest
                else:
                    manifest = self.document("manifest.json")
                    manifest[key]["sha256"] = digest
                    self.repin(manifest)
                self.reject("duplicate JSON key")

    def test_unsupported_schemas(self):
        for key in ("manifest", "catalog declaration", "catalog"):
            with self.subTest(key=key):
                self.reset_artifact()
                manifest = self.document("manifest.json")
                if key == "catalog":
                    self.update_record("catalog", lambda record: record.update(schema_version="2.0.0"))
                else:
                    declaration = manifest if key == "manifest" else manifest["catalog"]
                    declaration["schema_version"] = "2.0.0"
                    self.repin(manifest)
                self.reject("schema_version")

    def test_selection_rejects_unknown_and_conflicting_identities(self):
        self.target["--release"] = "andes@1.0.0"
        self.reject("release identity mismatch")
        self.target["--release"] = "andes@0.0.0"
        self.reject("unknown profile", "missing@1.0.0")
        self.reject("unknown profile", "andes.profile.verify@1.0.0")
        self.reject("incompatible composition", FORMAL, FAST)

    def test_catalog_must_agree_with_full_release_inventory(self):
        self.update_record("catalog", lambda data: data["components"][2]["requires"].append("missing@1.0.0"))
        self.reject("missing dependency")
        self.reset_artifact()
        self.update_record("catalog", lambda data: data["components"][0].update(path="missing.md"))
        self.reject("invalid content path")
        self.reset_artifact()
        self.update_record("catalog", lambda data: data["components"][2].update(path="content/norms.md"))
        self.reject("component paths must be distinct")
        self.reset_artifact()
        self.update_record("catalog", lambda data: data["components"][0].update(path="metadata/provenance.md"))
        self.reject("invalid content path")
        self.reset_artifact()
        manifest = self.document("manifest.json")
        manifest["profiles"].remove(FAST)
        self.repin(manifest)
        self.reject("available profiles must match the catalog")

    def test_rejects_incompatible_targets_and_unsupported_declarations(self):
        for option, value in (
            ("--adapter", "codex-project-local@1.0.1"), ("--runtime-version", "0.172.1"),
            ("--platform", "linux"), ("--architecture", "x86_64"),
        ):
            with self.subTest(option=option):
                previous = self.target[option]
                self.target[option] = value
                self.reject("adapter target mismatch")
                self.target[option] = previous
        self.target["--runtime-version"] = "0.172.1"
        self.update_record("adapter", lambda data: data["runtime"].update(version="0.172.1"))
        self.reject("unsupported adapter constraints")

    def test_selected_kind_must_be_supported(self):
        self.update_record("catalog", lambda data: data["components"][2].update(kind="tool"))
        self.accept()
        self.reject("unsupported component kind", FORMAL)

    def test_mutable_or_non_https_references_are_rejected(self):
        for key, value in (("commit", "main"), ("commit", "0" * 39), ("commit", "A" * 40),
                           ("repository", "http://example.invalid/andes.git"),
                           ("repository", "https://"), ("repository", "https://example.invalid/andes.git?ref=main"),
                           ("repository", "https://../repo"), ("repository", "https://example.invalid:99999/repo")):
            with self.subTest(key=key, value=value):
                manifest = self.document("manifest.json")
                manifest["source"][key] = value
                self.repin(manifest)
                self.reject("source")
                self.reset_artifact()
        self.target["--release"] = "stable"
        self.pin = PIN
        self.reject("exact id@version")
        self.target["--release"] = "andes@0.0.0"
        self.reject("exact id@version", "andes.profile.formal@latest")

    def test_unsafe_declared_paths(self):
        for path in ("../norms.md", "/norms.md", "content//norms.md", "content/./norms.md",
                     "content\\norms.md", "content/café.md", "content/file.", "content/COM1.md",
                     "content/norms.md/", "content/norms.md\n"):
            with self.subTest(path=path):
                manifest = self.document("manifest.json")
                manifest["files"][0]["path"] = path
                self.repin(manifest)
                self.reject("path")
                self.reset_artifact()

    def test_duplicate_case_and_directory_colliding_declarations(self):
        for path, diagnostic in (
            ("content/norms.md", "duplicate file path"),
            ("manifest.json", "duplicate file path"),
            ("Content/other.md", "case-colliding path"),
            ("content/NORMS.md", "case-colliding path"),
            ("content/norms.md/child.md", "file/directory collision"),
            ("content", "file/directory collision"),
        ):
            with self.subTest(path=path):
                manifest = self.document("manifest.json")
                manifest["files"].append({"path": path, "sha256": "0" * 64})
                self.repin(manifest)
                self.reject(diagnostic)
                self.reset_artifact()

    def test_unsafe_filesystem_entries(self):
        outside = self.work / "outside.md"
        file = self.artifact / "content/norms.md"
        outside.write_bytes(file.read_bytes())
        for create, diagnostic in (
            (lambda: file.symlink_to(outside), "symlink"),
            (lambda: os.link(outside, file), "hard link"),
            (lambda: os.mkfifo(file), "nonregular"),
            (lambda: file.mkdir(), "nonregular"),
        ):
            self.reset_artifact()
            file.unlink()
            create()
            self.reject(diagnostic)
        self.reset_artifact()
        alias = self.work / "alias"
        alias.symlink_to(self.artifact, target_is_directory=True)
        self.reject("artifact directory", artifact=str(alias) + "/")
        references = self.artifact / "content/references"
        references.rename(self.work / "references")
        references.symlink_to(self.work / "references", target_is_directory=True)
        self.reject("symlink")

    def test_resolver_creates_no_bytecode_in_tool_tree(self):
        scripts = self.work / "scripts"
        scripts.mkdir()
        self.script = scripts / self.script.name
        for path in (ROOT / "scripts/resolve_release.py", ROOT / "scripts/validate_catalog.py"):
            shutil.copyfile(path, scripts / path.name)
        shutil.copytree(ROOT / "schemas", self.work / "schemas")
        before = snapshot(scripts)
        self.accept()
        self.pin = "0" * 64
        self.reject("SHA-256 mismatch")
        self.assertEqual(snapshot(scripts), before)


class ManifestSchemaTests(unittest.TestCase):
    def test_schema_and_public_fixture(self):
        schema = json.loads((ROOT / "schemas/manifest-v1.schema.json").read_text())
        manifest = json.loads((FIXTURE / "artifact/manifest.json").read_bytes())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(manifest)
