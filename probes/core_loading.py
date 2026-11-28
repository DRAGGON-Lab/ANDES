"""Capture native skill injection locally; never call an external model provider."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading

from codex_discovery import response, sandbox_policy

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("candidate", ROOT / "adapters/codex/candidate.py")
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def run_probe(binary, skill_name):
    binary = Path(binary).resolve(strict=True)
    candidate.select_skill(ROOT, skill_name)
    captured = queue.Queue(maxsize=2)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            self.send_response(204 if self.path == "/health" else 404)
            self.end_headers()

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 2 * 1024 * 1024:
                self.send_error(413)
                return
            try:
                payload = json.loads(self.rfile.read(length))
                captured.put_nowait((payload, bool(self.headers.get("Authorization"))))
            except (ValueError, queue.Full):
                self.send_error(400)
                return
            # This is deliberately not a model implementation or a scripted
            # answer. The native turn cannot complete with an inference result.
            body = b'{"error":{"message":"Offline capture only; no inference","type":"invalid_request_error"}}'
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        server.daemon_threads = True
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            port = server.server_address[1]
            with tempfile.TemporaryDirectory(prefix="andes-core-native-") as outer:
                fixture = Path(outer).resolve() / "isolated"
                fixture.mkdir()
                state, user_root, temporary = (fixture / name for name in ("state", "user", "tmp"))
                for directory in (state, user_root, temporary):
                    directory.mkdir()
                project = fixture / "project"
                projection = candidate.project_core(ROOT, project)
                environment = {"PATH": "/usr/bin:/bin", "HOME": str(user_root),
                               "CODEX_HOME": str(state), "CODEX_SQLITE_HOME": str(state),
                               "TMPDIR": str(temporary), "LANG": "en_US.UTF-8"}
                (state / "config.toml").write_text(
                    'cli_auth_credentials_store = "ephemeral"\n'
                    'model = "andes-offline-fixture"\nmodel_provider = "fixture"\n'
                    '[analytics]\nenabled = false\n'
                    '[model_providers.fixture]\nname = "Offline capture only"\n'
                    'base_url = "http://127.0.0.1:' + str(port) + '/v1"\n'
                    'wire_api = "responses"\nrequires_openai_auth = false\n'
                    'request_max_retries = 0\nstream_max_retries = 0\n')
                subprocess.run(["/usr/bin/git", "init", "--quiet", str(project)],
                               env=environment, check=True, capture_output=True, timeout=10)
                policy = sandbox_policy(fixture, binary, Path.home().resolve())
                policy += '\n(allow network-outbound (remote ip "localhost:' + str(port) + '"))'
                prefix = ["/usr/bin/sandbox-exec", "-p", policy]

                def control(command):
                    return subprocess.run(prefix + command, env=environment,
                                          capture_output=True, timeout=10)

                launch = control(["/usr/bin/true"])
                if launch.returncode:
                    diagnostic = launch.stderr.decode("utf-8", errors="replace").splitlines()
                    raise RuntimeError("nested sandbox launch unavailable: " +
                                       (diagnostic[0] if diagnostic else "no diagnostic"))
                read = control(["/bin/cat", str(ROOT / "README.md")])
                sentinel = Path(outer) / "outside-denied"
                write = control(["/bin/sh", "-c", 'echo probe > "$1"', "probe", str(sentinel)])
                bind = control(["/usr/bin/python3", "-c",
                                'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0))'])
                denied_port = port - 1 if port > 1 else port + 1
                outbound = control(["/usr/bin/python3", "-c",
                                    'import socket; socket.create_connection(("127.0.0.1", ' +
                                    str(denied_port) + '), timeout=1)'])
                health = control(["/usr/bin/curl", "--silent", "--max-time", "2", "--noproxy", "*",
                                  "http://127.0.0.1:" + str(port) + "/health"])
                controls = {
                    "real_home_read_denied": read.returncode != 0 and b"Operation not permitted" in read.stderr,
                    "outside_write_denied": write.returncode != 0 and not sentinel.exists()
                    and b"Operation not permitted" in write.stderr,
                    "network_bind_denied": bind.returncode != 0 and b"Operation not permitted" in bind.stderr,
                    "other_port_denied": outbound.returncode != 0 and b"Operation not permitted" in outbound.stderr,
                    "capture_endpoint_reachable": health.returncode == 0,
                }
                if not all(controls.values()):
                    raise RuntimeError("isolation controls failed: " + repr(controls))
                with tempfile.TemporaryFile(dir=temporary) as errors:
                    process = subprocess.Popen(
                        prefix + [str(binary), "--no-daemon", "app-server", "--strict-config"],
                        cwd=project, env=environment, stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, stderr=errors)
                    try:
                        def send(method, request_id, params):
                            message = {"method": method, "params": params}
                            if request_id is not None:
                                message["id"] = request_id
                            process.stdin.write(json.dumps(message).encode() + b"\n")
                            process.stdin.flush()

                        send("initialize", 1, {"clientInfo": {
                            "name": "andes_core_capture", "version": "0.1.0"}})
                        initialized, buffer = response(process, 1, b"")
                        send("initialized", None, {})
                        send("skills/list", 2, {"cwds": [str(project)], "forceReload": True})
                        listed, buffer = response(process, 2, buffer)
                        entries = [entry for group in listed.get("data", [])
                                   for entry in group.get("skills", [])]
                        item = candidate.native_skill(ROOT, project, skill_name, entries)
                        send("thread/start", 3, {"cwd": str(project),
                                                "approvalPolicy": "never", "sandbox": "read-only"})
                        started, buffer = response(process, 3, buffer)
                        send("turn/start", 4, {"threadId": started["thread"]["id"], "input": [
                            {"type": "text", "text": "$" + skill_name +
                             " Assess the supplied synthetic bounded task; no edits or external actions."},
                            item]})
                        response(process, 4, buffer)
                        payload, auth_present = captured.get(timeout=20)
                        if auth_present:
                            raise RuntimeError("unexpected authorization at synthetic endpoint")
                        context = "\n".join(strings(payload))
                        data = candidate.load_core(ROOT)
                        body_presence = {}
                        for component in data["components"]:
                            if component["kind"] == "skill":
                                text = (ROOT / component["path"]).read_text()
                                body = text.partition("\n---\n")[2].strip()
                                body_presence[component["invocation"]] = body in context
                        reference = (ROOT / "skills/andes-orient/references/revision-mismatch.md").read_text().strip()
                        result = {
                            "runtime_user_agent": initialized.get("userAgent"),
                            "controls": controls, "selected_skill": skill_name,
                            "native_body_presence": body_presence,
                            "unneeded_reference_absent": reference not in context,
                            "constitution_present": (ROOT / "CONSTITUTION.md").read_text().strip() in context,
                            "projection_file_count": len(projection["files"]),
                            "configured_provider_response": 400, "model_completion_evaluated": False,
                            "external_model_calls": 0,
                        }
                        if not body_presence[skill_name] or any(
                            present for name, present in body_presence.items() if name != skill_name
                        ) or not result["unneeded_reference_absent"] or not result["constitution_present"]:
                            raise RuntimeError("native loading assertions failed: " + repr(result))
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
        finally:
            server.shutdown()
            worker.join(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--skill", default="andes-verify",
                        choices=("andes-orient", "andes-contract", "andes-verify", "andes-handoff"))
    args = parser.parse_args()
    if not args.codex:
        parser.error("installed Codex required")
    print(json.dumps(run_probe(args.codex, args.skill), indent=2))


if __name__ == "__main__":
    main()
