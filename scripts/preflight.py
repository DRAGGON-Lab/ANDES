"""Read-only preflight and install preview for a pinned project-local release."""
import sys

sys.dont_write_bytecode = True

import argparse
from contextlib import contextmanager, ExitStack
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from types import SimpleNamespace
import unicodedata

import resolve_release as releases

FORMAT = "1.0.0"
INSTRUCTION_BUDGET = 32 * 1024
SKILL_HEADER_BUDGET = 4096
BLOCK_START = b"<!-- BEGIN ANDES CORE -->"
BLOCK_END = b"<!-- END ANDES CORE -->"
ROUTER = "skills/ROUTING.md"
CONSTITUTION = "CONSTITUTION.md"
NAME = re.compile(rb"[a-z][a-z0-9-]*")
DESCRIPTION = re.compile(rb"[A-Za-z0-9][^\x00-\x1f\x7f]*")
RESERVED_MARKDOWN = {"agents.md", "agents.override.md", "skill.md"}
AMBIGUOUS_NAMES = {b"true", b"false", b"null", b"yes", b"no", b"on", b"off"}
RULE = re.compile(r"N(?:0[1-9]|1[0-2])|rigour|evidence|explanation|authority")


def finding(code, scope, path, message, **details):
    return {"code": code, "scope": scope, "path": path, "message": message, **details}


class Blocked(ValueError):
    def __init__(self, code, scope, path, message):
        self.findings = [finding(code, scope, path, message)]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def fold(name):
    return unicodedata.normalize("NFKC", name).casefold()


def lookup(directory, name, scope, path):
    matches = [entry for entry in os.listdir(directory) if fold(entry) == fold(name)]
    if not matches:
        return None
    if matches != [name]:
        raise Blocked("unsafe_path", scope, path, "Use the exact path spelling and remove case or Unicode aliases.")
    return os.stat(name, dir_fd=directory, follow_symlinks=False)


@contextmanager
def at_path(root, relative, scope):
    """Yield the final parent descriptor and name, or None for a missing parent."""
    parts = PurePosixPath(relative).parts
    directory = root
    with ExitStack() as stack:
        for index, part in enumerate(parts[:-1], 1):
            path = "/".join(parts[:index])
            info = lookup(directory, part, scope, path)
            if info is None:
                directory = None
                break
            if not stat.S_ISDIR(info.st_mode):
                raise Blocked("unsafe_path", scope, path, "Use a real directory without links.")
            directory = stack.enter_context(releases.open_directory(part, path, directory))
        yield directory, parts[-1]


@contextmanager
def root_directory(path, scope):
    if not path.is_absolute() or path == Path("/") or ".." in path.parts:
        raise Blocked("unsafe_path", scope, ".", "Supply an absolute physical directory path without '..'.")
    if not all((hasattr(os, "O_NOFOLLOW"), hasattr(os, "O_DIRECTORY"),
                {os.open, os.stat} <= os.supports_dir_fd, os.listdir in os.supports_fd,
                os.stat in os.supports_follow_symlinks)):
        raise Blocked("host_unsupported", "host", ".", "Descriptor-relative no-follow reads are unavailable.")
    with releases.open_directory("/", scope) as filesystem:
        with at_path(filesystem, path.relative_to("/").as_posix(), scope) as (parent, name):
            info = lookup(parent, name, scope, ".") if parent is not None else None
            if info is None or not stat.S_ISDIR(info.st_mode):
                raise Blocked("unsafe_path", scope, ".", "Supply an existing real directory without links.")
            with releases.open_directory(name, scope, parent) as root:
                yield root


def entry(root, path, scope):
    with at_path(root, path, scope) as (parent, name):
        return lookup(parent, name, scope, path) if parent is not None else None


def read_at(root, path, scope, limit):
    with at_path(root, path, scope) as (parent, name):
        if parent is None or lookup(parent, name, scope, path) is None:
            raise Blocked("unsafe_path", scope, path, "A required file is missing.")
        try:
            with releases.open_regular(parent, name, path) as stream:
                return stream.read(limit)
        except (ValueError, OSError):
            raise Blocked("unsafe_path", scope, path, "Use a readable regular file without links.") from None


def detect_host(binary, protected):
    system = os.uname()
    host = {"platform": system.sysname.lower(), "architecture": system.machine, "codex_version": None}
    if (host["platform"], host["architecture"]) != ("darwin", "arm64"):
        return host

    if not binary.is_absolute():
        raise Blocked("host_unsupported", "host", ".", "Pass an absolute path to an installed Codex executable.")
    try:
        binary = binary.resolve(strict=True)
    except (OSError, RuntimeError):
        raise Blocked("host_unsupported", "host", ".", "Pass an existing Codex executable.") from None
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise Blocked("host_unsupported", "host", ".", "Pass an executable Codex binary.")
    if any(binary.is_relative_to(path) for path in (protected[0], *protected[2:])):
        raise Blocked("host_unsupported", "host", ".", "Use a trusted executable outside the project, Codex home and artifact.")

    quoted_binary = json.dumps(str(binary))
    denied = " ".join("(subpath " + json.dumps(str(path)) + ")" for path in sorted(set(protected)))
    policy = "\n".join((
        "(version 1)", "(allow default)", "(deny network*)", "(deny file-write*)",
        "(deny process-fork)", "(deny process-exec)",
        "(allow process-exec (literal " + quoted_binary + "))",
        '(deny file-read* (subpath "/Users") (subpath "/Volumes") (subpath "/Library/Keychains")'
        ' (subpath "/private/etc/codex") (subpath "/etc/codex") ' + denied + ")",
        "(allow file-read* (literal " + quoted_binary + "))",
        '(deny mach-lookup (global-name "com.apple.securityd") (global-name "com.apple.securityd.xpc"))',
    ))
    try:
        result = subprocess.run(
            ["/usr/bin/sandbox-exec", "-p", policy, str(binary), "--version"],
            cwd="/var/empty", stdin=subprocess.DEVNULL, capture_output=True, timeout=5,
            env={"PATH": "/usr/bin:/bin", "HOME": "/var/empty", "CODEX_HOME": "/var/empty",
                 "CODEX_SQLITE_HOME": "/var/empty", "TMPDIR": "/var/empty", "LANG": "C"},
        )
    except (OSError, subprocess.TimeoutExpired):
        raise Blocked("host_unsupported", "host", ".", "Run the version probe where the macOS sandbox can launch.") from None
    match = re.fullmatch(rb"codex-cli ([0-9]+\.[0-9]+\.[0-9]+)\r?\n", result.stdout)
    if result.returncode != 0 or not match:
        raise Blocked("host_unsupported", "host", ".", "The sandboxed version probe failed. Check the executable and sandbox access.")
    host["codex_version"] = match[1].decode("ascii")
    return host


def reject_present(root, paths, scope, code, message):
    for path in paths:
        if entry(root, path, scope) is not None:
            raise Blocked(code, scope, path, message)


def skill_name(raw):
    lines = raw.split(b"\n")
    if len(lines) < 5 or lines[0].removesuffix(b"\r") != b"---":
        return None
    fields = {}
    for line in lines[1:-1]:
        line = line.removesuffix(b"\r")
        if line == b"---":
            if set(fields) != {b"name", b"description"}:
                return None
            name, description = fields[b"name"], fields[b"description"]
            if (not NAME.fullmatch(name) or name in AMBIGUOUS_NAMES or not DESCRIPTION.fullmatch(description)
                    or b": " in description or b" #" in description):
                return None
            try:
                description.decode("utf-8")
            except UnicodeDecodeError:
                return None
            return name.decode("ascii")
        key, separator, value = line.partition(b": ")
        if not separator or key in fields or key not in (b"name", b"description"):
            return None
        fields[key] = value
    return None


def existing_skill_names(root, path, scope):
    info = entry(root, path, scope)
    if info is None:
        return []
    if not stat.S_ISDIR(info.st_mode):
        raise Blocked("unsafe_path", scope, path, "Use a real skill directory without links.")
    names = []
    with at_path(root, path, scope) as (parent, name):
        with releases.open_directory(name, path, parent) as skills:
            for folder in sorted(os.listdir(skills)):
                if folder.startswith("."):
                    raise Blocked("unknown_skill_metadata", scope, path, "Inspect hidden entries in the skill directory.")
                info = lookup(skills, folder, scope, path)
                if not stat.S_ISDIR(info.st_mode):
                    raise Blocked("unsafe_path", scope, path, "Inspect unexpected entries in the skill directory.")
                with releases.open_directory(folder, path, skills) as skill:
                    try:
                        raw = read_at(skill, "SKILL.md", scope, SKILL_HEADER_BUDGET)
                    except Blocked:
                        raise Blocked("unknown_skill_metadata", scope, path, "Use a regular SKILL.md in each skill folder.") from None
                    name = skill_name(raw)
                    if name is None:
                        raise Blocked("unknown_skill_metadata", scope, path, "Review unsupported skill front matter.")
                    names.append(name)
    return names


def project_snapshot(project, codex_home, result):
    marker = entry(project, ".git", "project")
    if marker is None or not (stat.S_ISDIR(marker.st_mode) or stat.S_ISREG(marker.st_mode) and marker.st_nlink == 1):
        raise Blocked("unsafe_path", "project", ".git", "Choose the root of a Git project or worktree.")
    reject_present(project, ("AGENTS.override.md",), "project", "instruction_override",
                   "Review the root override before supplying a project root.")
    reject_present(codex_home, ("AGENTS.override.md", "AGENTS.md"), "codex-home", "global_instructions",
                   "Global instructions require separate review. Use an isolated Codex home for this preview.")
    for root, scope, prefix in ((project, "project", ".codex/"), (codex_home, "codex-home", "")):
        reject_present(root, tuple(prefix + name for name in ("config.toml", "rules", "hooks.json", "plugins", "config.d")),
                       scope, "unknown_configuration",
                       "Review this configuration separately or choose an isolated root.")
    reject_present(project, (".andes",), "project", "destination_conflict",
                   "The project already contains .andes. Review its ownership before proceeding.")
    if entry(project, "AGENTS.md", "project") is None:
        return None
    raw = read_at(project, "AGENTS.md", "project", INSTRUCTION_BUDGET + 1)
    result["instructions"] = {"agents_sha256": digest(raw)}
    if len(raw) > INSTRUCTION_BUDGET:
        result["instructions"] = None
        raise Blocked("instruction_budget", "project", "AGENTS.md", "Reduce the root instructions to fit the supported budget.")
    if BLOCK_START in raw or BLOCK_END in raw:
        raise Blocked("destination_conflict", "project", "AGENTS.md", "Review ownership of the existing ANDES block.")
    require_text(raw, "project", "AGENTS.md")
    return raw


def require_text(raw, scope, path):
    try:
        if raw.startswith(b"\xef\xbb\xbf") or b"\x00" in raw:
            raise ValueError
        return raw.decode("utf-8")
    except ValueError:
        raise Blocked("invalid_instructions", scope, path, "Use UTF-8 text without a byte-order mark or NUL.") from None


def instructions_review(path, manifest, original, policy, result):
    state = {"agents_sha256": digest(original), "policy_sha256": digest(policy)}
    result["instructions"] = state
    if path is None:
        raise Blocked("instruction_review_required", "project", "AGENTS.md",
                      "Review the project instructions against the pinned ANDES policy and supply the confirmed record.")
    keys = {"schema_version", "manifest_sha256", "confirmed", "decision", "findings", *state}
    try:
        with root_directory(path.absolute().parent, "review") as root:
            raw = read_at(root, path.name, "review", 64 * 1024 + 1)
        if len(raw) > 64 * 1024:
            raise ValueError
        value = releases.parse_json(raw, "review")
        if (not isinstance(value, dict) or set(value) != keys or value["schema_version"] != FORMAT
                or value["confirmed"] is not True or not isinstance(value["findings"], list)
                or value["decision"] != ("blocked" if value["findings"] else "compatible")):
            raise ValueError
        for item in value["findings"]:
            if (not isinstance(item, dict) or set(item) != {"line", "rule", "classification"}
                    or type(item["line"]) is not int or not 1 <= item["line"] <= len(original.splitlines())
                    or not isinstance(item["rule"], str) or not RULE.fullmatch(item["rule"])
                    or item["classification"] not in ("conflict", "uncertain")):
                raise ValueError
    except (ValueError, OSError):
        raise Blocked("instruction_review_invalid", "review", ".", "Supply a valid human-confirmed review record.") from None
    if any(value[key] != expected for key, expected in {**state, "manifest_sha256": manifest}.items()):
        raise Blocked("instruction_review_stale", "project", "AGENTS.md", "Review the current file against the current pinned ANDES policy.")
    if value["findings"]:
        blocked = Blocked("instruction_conflict", "project", "AGENTS.md", "")
        blocked.findings = [
            finding("instruction_" + item["classification"], "project", "AGENTS.md",
                    "Resolve the cited guidance and repeat the review.",
                    line=item["line"], rule=item["rule"])
            for item in sorted(value["findings"], key=lambda item: (item["line"], item["rule"], item["classification"]))
        ]
        raise blocked


def verified_bytes(root, record, limit):
    raw = read_at(root, record["path"], "artifact", limit + 1)
    if len(raw) > limit or digest(raw) != record["sha256"]:
        raise Blocked("artifact_rejected", "artifact", record["path"], "Reverify a stable snapshot with supported file sizes.")
    return raw


def supported_markdown(path):
    return path.endswith(".md") and all(
        not part.startswith(".") and fold(part) not in RESERVED_MARKDOWN for part in PurePosixPath(path).parts
    )


def projection(resolution, catalog, artifact, project):
    operations = []
    names = set()
    norms = {}
    router = None
    catalog_by_id = {releases.validate_catalog.identity(item): item for item in catalog["components"]}
    for item in resolution["components"]:
        path = item["path"]
        if item["kind"] != "skill":
            if not supported_markdown(path):
                raise Blocked("unsupported_layout", "artifact", path, "Use Markdown without hidden or native control paths.")
            operations.append(copy_operation(item, ".andes/content/" + path))
            if item["kind"] == "norm":
                norms[path] = verified_bytes(artifact, item, INSTRUCTION_BUDGET)
            elif path == ROUTER:
                router = verified_bytes(artifact, item, INSTRUCTION_BUDGET)
            continue
        name = catalog_by_id[item["identity"]]["invocation"]
        source = "skills/" + name + "/"
        destination = ".agents/skills/" + name
        raw = verified_bytes(artifact, item, 1024 * 1024)
        if path != source + "SKILL.md" or skill_name(raw[:SKILL_HEADER_BUDGET]) != name:
            raise Blocked("unsupported_layout", "artifact", path, "Use the canonical skill path and matching name and description.")
        reject_present(project, (destination,), "project", "destination_conflict",
                       "This skill destination is occupied. Review its ownership before proceeding.")
        names.add(name)
        operations.append(copy_operation(item, destination + "/SKILL.md"))
        for resource in resolution["resources"]:
            if not resource["path"].startswith(source):
                continue
            relative = resource["path"].removeprefix(source)
            if not relative.startswith("references/") or not supported_markdown(relative):
                raise Blocked("unsupported_layout", "artifact", resource["path"],
                              "Place skill resources under references/ as Markdown without native control filenames.")
            operations.append(copy_operation(resource, destination + "/" + relative))
    if CONSTITUTION not in norms or router is None:
        raise Blocked("unsupported_layout", "artifact", ".", "Select the Constitution norm and routing playbook.")
    policy_parts = [(CONSTITUTION, norms.pop(CONSTITUTION)), *sorted(norms.items()), (ROUTER, router)]
    for path, raw in policy_parts:
        require_text(raw, "artifact", path)
        if not raw.strip() or BLOCK_START in raw or BLOCK_END in raw:
            raise Blocked("invalid_instructions", "artifact", path, "Use non-empty policy text without reserved block markers.")
    block = b"\n\n".join((
        BLOCK_START, b"Compatible project guidance refines development practices within the ANDES Constitution "
        b"and the host's instruction precedence. It does not authorize exceptions to mandatory norms.",
        *(raw.rstrip(b"\r\n") for _, raw in policy_parts), BLOCK_END, b"",
    ))
    return sorted(operations, key=lambda operation: operation["destination"]), names, block


def copy_operation(item, destination):
    return {"action": "copy", "source": item["path"], "destination": destination, "sha256": item["sha256"]}


def inspect_skills(project, home, codex_home, selected):
    names = set()
    for root, scope, path in ((project, "project", ".agents/skills"),
                              (home, "home", ".agents/skills"), (codex_home, "codex-home", "skills")):
        for name in existing_skill_names(root, path, scope):
            if name in selected or name in names:
                raise Blocked("skill_name_conflict", scope, path, "Review duplicate skill names in the inspected roots.")
            names.add(name)


def preflight(args, result):
    scopes = [(args.project, "project"), (args.home, "home"), (args.codex_home, "codex-home")]
    if args.command == "install":
        scopes.append((args.artifact, "artifact"))
    with ExitStack() as stack:
        roots = [stack.enter_context(root_directory(path, scope)) for path, scope in scopes]
        project, home, codex_home = roots[:3]
        if (args.project == args.home or args.project.is_relative_to(args.codex_home)
                or args.codex_home.is_relative_to(args.project)
                or args.command == "install" and any(
                    args.artifact.is_relative_to(path) or path.is_relative_to(args.artifact)
                    for path in (args.project, args.codex_home))):
            raise Blocked("unsafe_path", "project", ".", "Use distinct project, Codex home and artifact roots.")
        result["host"] = host = detect_host(args.codex_bin, [path for path, _ in scopes])
        adapter = releases.SUPPORTED_ADAPTER
        if (host["platform"], host["architecture"], host["codex_version"]) != (
            adapter["platform"], adapter["architecture"], adapter["runtime"]["version"]
        ):
            raise Blocked("host_unsupported", "host", ".", "Use Codex CLI 0.172.0 on Darwin arm64.")
        original = project_snapshot(project, codex_home, result)
        if args.command == "doctor":
            inspect_skills(project, home, codex_home, set())
            if original is not None:
                raise Blocked("instruction_review_required", "project", "AGENTS.md",
                              "Run install --dry-run with a pinned release to prepare an instruction review.")
            return
        try:
            resolution, catalog = releases.resolve_with_catalog(SimpleNamespace(
                artifact=args.artifact, release=args.release, manifest_sha256=args.manifest_sha256,
                profile=args.profile, adapter=releases.validate_catalog.identity(adapter),
                runtime_version=host["codex_version"], platform=host["platform"], architecture=host["architecture"],
            ))
        except (OSError, ValueError, RecursionError):
            raise Blocked("artifact_rejected", "artifact", "manifest.json",
                          "Check the external pin, artifact inventory and profile selection with resolve_release.py.") from None
        operations, selected, block = projection(resolution, catalog, roots[3], project)
        inspect_skills(project, home, codex_home, selected)
        previous = original if original is not None else b""
        if len(block) + len(previous) > INSTRUCTION_BUDGET:
            raise Blocked("instruction_budget", "project", "AGENTS.md", "Reduce the combined root instructions to at most 32 KiB.")
        if original is not None:
            instructions_review(args.instructions_review, resolution["manifest_sha256"], previous, block, result)
        elif args.instructions_review is not None:
            raise Blocked("instruction_review_stale", "project", "AGENTS.md", "Omit the instruction review for a project without AGENTS.md.")
        operations.append({
            "action": "create" if original is None else "prepend_reviewed_block",
            "destination": "AGENTS.md", "block": block.decode("utf-8"),
            "previous_sha256": None if original is None else digest(previous),
            "sha256": digest(block + previous),
        })
        result["plan"] = {
            **{key: resolution[key] for key in ("release", "source", "manifest_sha256", "profiles", "adapter")},
            "approval_required": True, "operations": operations,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="check the host and project", allow_abbrev=False)
    install = commands.add_parser("install", help="preview a pinned release", allow_abbrev=False)
    for subparser in (doctor, install):
        subparser.add_argument("--project", type=Path, required=True)
        subparser.add_argument("--home", type=Path, required=True)
        subparser.add_argument("--codex-home", type=Path, required=True)
        subparser.add_argument("--codex-bin", type=Path, required=True)
    install.add_argument("--dry-run", action="store_true", required=True)
    install.add_argument("artifact", type=Path)
    install.add_argument("--release", required=True)
    install.add_argument("--manifest-sha256", required=True)
    install.add_argument("--profile", action="append", default=[])
    install.add_argument("--instructions-review", type=Path)
    args = parser.parse_args()
    result = {"schema_version": FORMAT, "command": args.command, "status": "ready", "host": None,
              "instructions": None, "plan": None, "findings": []}
    try:
        preflight(args, result)
    except Blocked as error:
        result["findings"] = error.findings
    except (OSError, ValueError, RecursionError):
        result["findings"] = [finding("unsafe_path", "preflight", ".", "Check the spelling, type and readability of the supplied paths.")]
    if result["findings"]:
        result.update(status="blocked", plan=None)
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(result["status"] == "blocked")


if __name__ == "__main__":
    sys.exit(main())
