"""Resolve a pinned ANDES release from an unpacked local snapshot."""
import sys

# Loading the shared validator must not leave bytecode in the tool checkout.
sys.dont_write_bytecode = True

import argparse
from collections import defaultdict
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator

import validate_catalog

MANIFEST = "manifest.json"
SCHEMA = Path(__file__).resolve().parents[1] / "schemas/manifest-v1.schema.json"
IDENTITY = re.compile(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*@[0-9]+\.[0-9]+\.[0-9]+")
DEVICE_NAME = re.compile(r"CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9]", re.IGNORECASE)
SUPPORTED_ADAPTER = {
    "id": "codex-project-local",
    "version": "1.0.0",
    "runtime": {"id": "codex-cli", "version": "0.172.0"},
    "platform": "darwin",
    "architecture": "arm64",
}
SUPPORTED_KINDS = {"norm", "playbook", "skill"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"invalid JSON constant {value}")


def parse_json(raw, path):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (ValueError, RecursionError) as error:
        raise ValueError(f"{path}: {error}") from error


def check_digest(path, expected, digest):
    if expected != digest:
        raise ValueError(f"{path}: SHA-256 mismatch (expected {expected}, got {digest})")


@contextmanager
def open_directory(name, path, parent=None):
    try:
        fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
    except OSError as error:
        raise ValueError(f"{path}: cannot open directory without following links: {error.strerror}") from error
    try:
        yield fd
    finally:
        os.close(fd)


def require_regular(path, info):
    if stat.S_ISLNK(info.st_mode):
        raise ValueError(f"{path}: symlink")
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"{path}: nonregular file")
    if info.st_nlink != 1:
        raise ValueError(f"{path}: hard link")


@contextmanager
def open_regular(directory, name, path):
    try:
        before = os.stat(name, dir_fd=directory, follow_symlinks=False)
        require_regular(path, before)
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    except OSError as error:
        raise ValueError(f"{path}: cannot open regular file: {error.strerror}") from error
    with os.fdopen(fd, "rb") as stream:
        current = os.fstat(stream.fileno())
        require_regular(path, current)
        if not os.path.samestat(before, current):
            raise ValueError(f"{path}: file changed while opening")
        yield stream


def validate_manifest(manifest):
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    error = next(Draft202012Validator(schema).iter_errors(manifest), None)
    if error is not None:
        location = "/".join(map(str, error.absolute_path)) or "(root)"
        raise ValueError(f"{MANIFEST}: schema {location}: {error.message}")
    try:
        if urlsplit(manifest["source"]["repository"]).port == 0:
            raise ValueError("port must be nonzero")
    except ValueError as error:
        raise ValueError(f"{MANIFEST}: invalid source repository URL: {error}") from error


def declared_inventory(manifest, pin):
    files = {MANIFEST: pin}
    directories = set()
    for record in (manifest["catalog"], manifest["adapter"], manifest["provenance"], *manifest["files"]):
        path = record["path"]
        if path in files:
            raise ValueError(f"duplicate file path: {path}")
        parts = PurePosixPath(path)
        for part in parts.parts:
            if DEVICE_NAME.fullmatch(part.split(".", 1)[0]):
                raise ValueError(f"path contains a reserved device name: {path}")
        directories.update(parent.as_posix() for parent in parts.parents if parent.parts)
        files[path] = record["sha256"]

    collisions = directories.intersection(files)
    if collisions:
        raise ValueError(f"file/directory collision: {min(collisions)}")

    children = defaultdict(set)
    folded_paths = {}
    for path in sorted(directories | files.keys()):
        existing = folded_paths.setdefault(path.lower(), path)
        if path != existing:
            raise ValueError(f"case-colliding paths: {existing} and {path}")
        parent, _, name = path.rpartition("/")
        children[parent].add(name)
    return files, children


def verify_inventory(directory, parent, children, files, records):
    expected = children[parent]
    actual = set(os.listdir(directory))
    prefix = parent + "/" if parent else ""
    extra = actual - expected
    if extra:
        name = ascii(min(extra))[1:-1]
        raise ValueError(f"undeclared entry: {prefix}{name}")
    missing = expected - actual
    if missing:
        raise ValueError(f"missing entry: {prefix}{min(missing)}")
    for name in sorted(expected):
        path = prefix + name
        if path == MANIFEST:
            continue  # The manifest was opened safely and verified before parsing.
        if path in children:
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                raise ValueError(f"{path}: symlink")
            with open_directory(name, path, directory) as child:
                verify_inventory(child, path, children, files, records)
        else:
            with open_regular(directory, name, path) as stream:
                if path in records:
                    records[path] = stream.read()
                    digest = hashlib.sha256(records[path]).hexdigest()
                else:
                    digest = hashlib.file_digest(stream, "sha256").hexdigest()
            check_digest(path, files[path], digest)


def resolve_with_catalog(args):
    if re.fullmatch(r"[0-9a-f]{64}", args.manifest_sha256) is None:
        raise ValueError("--manifest-sha256 requires 64 lowercase SHA-256 hex digits")
    profiles = sorted(set(args.profile))
    for option, values in (("--release", [args.release]), ("--profile", profiles), ("--adapter", [args.adapter])):
        if any(IDENTITY.fullmatch(value) is None for value in values):
            raise ValueError(f"{option} requires an exact id@version")
    # The declared adapter target is independent of the resolver's host.
    if not (hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY")
            and {os.open, os.stat} <= os.supports_dir_fd
            and os.stat in os.supports_follow_symlinks and os.listdir in os.supports_fd):
        raise ValueError("resolver requires descriptor-relative, no-follow local filesystem operations")

    with open_directory(args.artifact, "artifact directory") as directory:
        with open_regular(directory, MANIFEST, MANIFEST) as stream:
            raw = stream.read()
        check_digest(MANIFEST, args.manifest_sha256, hashlib.sha256(raw).hexdigest())
        manifest = parse_json(raw, MANIFEST)
        validate_manifest(manifest)
        release = validate_catalog.identity(manifest["release"])
        if release != args.release:
            raise ValueError(f"release identity mismatch: manifest declares {release}")
        files, children = declared_inventory(manifest, args.manifest_sha256)
        catalog_path = manifest["catalog"]["path"]
        adapter_path = manifest["adapter"]["path"]
        records = {catalog_path: None, adapter_path: None}
        verify_inventory(directory, "", children, files, records)

    adapter = parse_json(records[adapter_path], adapter_path)
    if adapter != SUPPORTED_ADAPTER:
        raise ValueError(f"{adapter_path}: unsupported adapter constraints")
    adapter_identity = validate_catalog.identity(adapter)
    for option, declared, requested in (
        ("--adapter", adapter_identity, args.adapter),
        ("--runtime-version", adapter["runtime"]["version"], args.runtime_version),
        ("--platform", adapter["platform"], args.platform),
        ("--architecture", adapter["architecture"], args.architecture),
    ):
        if declared != requested:
            raise ValueError(f"adapter target mismatch: {option} must be {declared}")

    catalog = parse_json(records[catalog_path], catalog_path)
    payload = {item["path"]: item for item in manifest["files"]}
    try:
        selected = validate_catalog.compose(catalog, profiles=profiles, verified_paths=payload)
    except ValueError as error:
        raise ValueError(f"{catalog_path}: {error}") from error
    if catalog["schema_version"] != manifest["catalog"]["schema_version"]:
        raise ValueError(f"{catalog_path}: catalog schema_version must match the manifest")
    if set(manifest["profiles"]) != {validate_catalog.identity(profile) for profile in catalog["profiles"]}:
        raise ValueError(f"{catalog_path}: available profiles must match the catalog")

    by_identity = {validate_catalog.identity(item): item for item in catalog["components"]}
    component_paths = {item["path"] for item in by_identity.values()}
    if len(component_paths) != len(by_identity):
        raise ValueError(f"{catalog_path}: component paths must be distinct")
    components = []
    for identity in selected:
        item = by_identity[identity]
        if item["kind"] not in SUPPORTED_KINDS:
            raise ValueError(f"{identity}: unsupported component kind {item['kind']} for {adapter_identity}")
        components.append({"identity": identity, "kind": item["kind"], **payload[item["path"]]})

    resolution = {
        "schema_version": "1.0.0",
        "release": release,
        "source": manifest["source"],
        "manifest_sha256": args.manifest_sha256,
        "catalog": manifest["catalog"],
        "profiles": profiles,
        "components": components,
        "resources": [payload[path] for path in sorted(payload.keys() - component_paths)],
        "provenance": manifest["provenance"],
        "adapter": {
            **manifest["adapter"],
            "identity": adapter_identity,
            "runtime": adapter["runtime"],
            "platform": adapter["platform"],
            "architecture": adapter["architecture"],
        },
    }

    return resolution, catalog


def resolve(args):
    resolution, _ = resolve_with_catalog(args)
    return resolution


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("artifact", type=Path, help="stable unpacked artifact directory")
    parser.add_argument("--release", required=True, help="expected release id@version")
    parser.add_argument("--manifest-sha256", required=True, help="trusted external SHA-256 of raw manifest bytes")
    parser.add_argument("--profile", action="append", default=[], help="optional profile id@version, repeatable")
    parser.add_argument("--adapter", required=True, help="target adapter id@version")
    parser.add_argument("--runtime-version", required=True, help="target Codex CLI version")
    parser.add_argument("--platform", required=True, help="target platform")
    parser.add_argument("--architecture", required=True, help="target architecture")
    args = parser.parse_args()
    try:
        resolution = resolve(args)
    except (OSError, ValueError, RecursionError) as error:
        print(f"release resolution failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(resolution, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
