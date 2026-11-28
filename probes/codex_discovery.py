"""Offline macOS Codex compatibility spike; no turns, credentials or model calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import tempfile
import time


def sandbox_policy(fixture, binary, protected_root):
    quote = lambda p: json.dumps(str(p))
    return "\n".join((
        "(version 1)", "(allow default)", "(deny network*)",
        "(deny file-write*)",
        "(allow file-write* (subpath " + quote(fixture) + "))",
        '(allow file-write* (literal "/dev/null"))',
        "(deny file-read* (subpath " + quote(protected_root) + "))",
        "(allow file-read* (subpath " + quote(binary.parent) + "))",
        "(allow file-read* (subpath " + quote(fixture) + "))",
        '(deny file-read* (subpath "/etc/codex") (subpath "/private/etc/codex"))',
        '(deny file-read* (subpath "/Library/Keychains"))',
        '(deny mach-lookup (global-name "com.apple.securityd") (global-name "com.apple.securityd.xpc"))',
    ))


def response(process, request_id, buffer):
    deadline = time.monotonic() + 20
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        while time.monotonic() < deadline:
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                message = json.loads(line)
                if message.get("id") == request_id:
                    if "error" in message:
                        raise RuntimeError("native RPC rejected request")
                    return message["result"], buffer
            events = selector.select(max(0, deadline - time.monotonic()))
            if not events:
                break
            chunk = os.read(process.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError("native RPC ended before response")
            buffer += chunk
    raise TimeoutError("native RPC timed out")


def probe(binary):
    binary = Path(binary).resolve(strict=True)
    protected_root = Path.home().resolve()
    with tempfile.TemporaryDirectory(prefix="andes-codex-spike-") as outer:
        fixture = Path(outer).resolve() / "isolated"
        fixture.mkdir()
        user_root = fixture / "user"
        state = fixture / "state"
        project = fixture / "project"
        temporary = fixture / "tmp"
        for path in (user_root, state, project, temporary):
            path.mkdir()
        # These are child-process environment inputs only; parent environment is untouched.
        environment = {"PATH": "/usr/bin:/bin", "HOME": str(user_root),
                       "CODEX_HOME": str(state), "CODEX_SQLITE_HOME": str(state),
                       "TMPDIR": str(temporary), "LANG": "en_US.UTF-8"}
        (state / "config.toml").write_text(
            'cli_auth_credentials_store = "ephemeral"\n[analytics]\nenabled = false\n'
            '[agents.fixture_reviewer]\ndescription = "Synthetic reviewer role"\n'
            'config_file = "./fixture-reviewer.toml"\n')
        (state / "fixture-reviewer.toml").write_text(
            'name = "fixture_reviewer"\ndescription = "Synthetic reviewer role"\n'
            'developer_instructions = "Synthetic reviewer, no execution authority."\n')
        subprocess.run(["/usr/bin/git", "init", "--quiet", str(project)],
                       env=environment, check=True, capture_output=True, timeout=10)
        for root, name in ((project, "andes-probe-project"), (user_root, "andes-probe-user")):
            skill = root / ".agents" / "skills" / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: " + name + "\ndescription: Synthetic offline discovery marker.\n---\n"
                "Synthetic probe body; no operational permissions.\n")
        nested = project / "nested"
        nested.mkdir()
        instruction_paths = [state / "AGENTS.md", project / "AGENTS.md",
                             nested / "AGENTS.override.md"]
        for number, path in enumerate(instruction_paths):
            path.write_text("Synthetic instruction marker " + str(number) + "\n")
        (nested / "AGENTS.md").write_text("This sibling instruction must be overridden.\n")
        preserved = [state / "config.toml", user_root / ".agents/skills/andes-probe-user/SKILL.md"]
        before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in preserved]
        policy = sandbox_policy(fixture, binary, protected_root)
        prefix = ["/usr/bin/sandbox-exec", "-p", policy]
        launch = subprocess.run(prefix + ["/usr/bin/true"], env=environment,
                                capture_output=True, timeout=10)
        if launch.returncode:
            raise RuntimeError("sandbox launch unavailable; controls/native probe not run")
        # Prove protections before starting Codex. No private file is opened:
        # this repository's public README represents the denied real-home tree.
        public_readme = Path(__file__).resolve().parents[1] / "README.md"
        read = subprocess.run(prefix + ["/bin/cat", str(public_readme)], env=environment,
                              capture_output=True, timeout=10)
        sentinel = Path(outer) / "must-not-be-written"
        write = subprocess.run(prefix + ["/bin/sh", "-c", 'echo probe > "$1"', "probe", str(sentinel)],
                               env=environment, capture_output=True, timeout=10)
        network = subprocess.run(
            prefix + ["/usr/bin/python3", "-c",
                      'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0))'],
            env=environment, capture_output=True, timeout=10)
        controls = {"real_home_read_denied": read.returncode != 0 and b"Operation not permitted" in read.stderr,
                    "outside_write_denied": write.returncode != 0 and not sentinel.exists()
                    and b"Operation not permitted" in write.stderr,
                    "network_bind_denied": network.returncode != 0 and b"Operation not permitted" in network.stderr}
        if not all(controls.values()):
            raise RuntimeError("isolation control failed; native process not started")
        with tempfile.TemporaryFile(dir=temporary) as errors:
            process = subprocess.Popen(
                prefix + [str(binary), "--no-daemon", "app-server", "--strict-config"],
                cwd=project, env=environment, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=errors)
            try:
                def send(message):
                    process.stdin.write(json.dumps(message).encode() + b"\n")
                    process.stdin.flush()
                send({"method": "initialize", "id": 1,
                      "params": {"clientInfo": {"name": "andes_offline_probe", "version": "0.1.0"}}})
                initialized, buffer = response(process, 1, b"")
                send({"method": "initialized", "params": {}})
                send({"method": "skills/list", "id": 2,
                      "params": {"cwds": [str(project)], "forceReload": True}})
                skills, buffer = response(process, 2, buffer)
                entries = [entry for group in skills.get("data", []) for entry in group.get("skills", [])]
                expected = {"andes-probe-project", "andes-probe-user"}
                observed = sorted({entry.get("name") for entry in entries if entry.get("name") in expected})
                metadata_verified = all(
                    entry.get("description") == "Synthetic offline discovery marker."
                    and Path(entry.get("path", "")).name == "SKILL.md"
                    for entry in entries if entry.get("name") in expected)
                send({"method": "config/read", "id": 3, "params": {"includeLayers": False}})
                config, buffer = response(process, 3, buffer)
                roles = config.get("config", {}).get("agents", {})
                role = roles.get("fixture_reviewer", {})
                role_observed = (
                    role.get("description") == "Synthetic reviewer role"
                    and Path(role.get("config_file", "")).name == "fixture-reviewer.toml")
                send({"method": "thread/start", "id": 4,
                      "params": {"cwd": str(nested), "approvalPolicy": "never",
                                 "sandbox": "read-only"}})
                thread, buffer = response(process, 4, buffer)
                source_paths = thread.get("instructionSources", [])
                labels = {str(path): name for path, name in zip(
                    instruction_paths, ("global", "project", "nested_override"))}
                source_order = [labels.get(str(path), "unexpected_source") for path in source_paths]
                result = {
                    "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                    "controls": controls, "fixture_skills": observed,
                    "both_fixture_scopes_discovered": set(observed) == expected,
                    "minimal_skill_metadata_verified": metadata_verified,
                    "discovery_errors": sum(len(group.get("errors", [])) for group in skills.get("data", [])),
                    "initialized_user_agent": initialized.get("userAgent"),
                    "instruction_source_order": source_order,
                    "instruction_override_and_order_verified": source_order == [
                        "global", "project", "nested_override"],
                    "role_definition_in_effective_config": role_observed,
                    "synthetic_user_files_unchanged": before == [
                        hashlib.sha256(path.read_bytes()).hexdigest() for path in preserved],
                    "turns_started": 0, "model_calls": 0,
                    "limitations": ["Skill listing is not instruction loading or implicit routing",
                                    "Role execution and packaging/install not tested",
                                    "Source order is observed, model obedience is not evaluated"],
                }
                if not result["both_fixture_scopes_discovered"] or not metadata_verified:
                    raise RuntimeError("required synthetic skill scopes not discovered")
                if not result["instruction_override_and_order_verified"]:
                    raise RuntimeError("instruction source ordering not established: " + repr(source_order))
                if not role_observed or not result["synthetic_user_files_unchanged"]:
                    raise RuntimeError("role metadata/coexistence probe failed")
                return result
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                process.stdin.close()
                process.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default=shutil.which("codex"))
    args = parser.parse_args()
    if not args.codex:
        parser.error("installed Codex executable required")
    print(json.dumps(probe(args.codex), indent=2))


if __name__ == "__main__":
    main()
