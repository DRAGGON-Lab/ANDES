"""Validate local canonical catalogs without loading instructions or executing tools."""
import argparse
from graphlib import CycleError, TopologicalSorter
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).resolve().parents[1] / "schemas/catalog-v1.schema.json"
LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
            "CC0-1.0", "CC-BY-4.0", "CC-BY-SA-4.0"}


def identity(item):
    return item["id"] + "@" + item["version"]


def _compose(data, profiles=(), component=None):
    components = {identity(c): c for c in data["components"]}
    profile_map = {identity(p): p for p in data["profiles"]}
    pending = list(data["core"])
    for profile in profiles:
        if profile not in profile_map:
            raise ValueError("unknown profile: " + profile)
        pending.extend(profile_map[profile]["components"])
    if component is not None:
        if component not in components or components[component]["kind"] != "skill":
            raise ValueError("unknown invocable skill: " + component)
        pending.append(component)
    selected = set()
    while pending:
        key = pending.pop()
        if key not in components:
            raise ValueError("missing dependency: " + key)
        if key in selected:
            continue
        item = components[key]
        if item["lifecycle"] not in ("active", "deprecated"):
            raise ValueError("unselectable lifecycle: " + key)
        selected.add(key)
        pending.extend(item["requires"])
    if not any(components[key]["kind"] == "norm" for key in selected):
        raise ValueError("core must include a norm")
    for key in sorted(selected):
        if selected.intersection(components[key]["conflicts"]):
            raise ValueError("incompatible composition: " + key)
    return sorted(selected)


def validate(data, root=None, *, verified_paths=None):
    schema = json.loads(SCHEMA.read_text())
    errors = [
        "schema: " + "/".join(map(str, error.absolute_path)) + ": " + error.message
        for error in Draft202012Validator(schema).iter_errors(data)
    ]
    if errors:
        return sorted(errors)
    items = data["components"] + data["profiles"]
    if len({x["id"] for x in items}) != len(items):
        return ["duplicate ID (one local version per stable ID)"]
    components = {identity(c): c for c in data["components"]}
    invocations = [c["invocation"] for c in components.values() if c["kind"] == "skill"]
    if len(set(invocations)) != len(invocations):
        errors.append("duplicate invocation")
    if verified_paths is None:
        root = Path(root).resolve()
    for key, item in components.items():
        if verified_paths is not None:
            valid_path = item["path"] in verified_paths
        else:
            path = Path(item["path"])
            try:
                resolved = (root / path).resolve()
                valid_path = not path.is_absolute() and resolved.is_relative_to(root) and resolved.is_file()
            except (OSError, RuntimeError, ValueError):
                valid_path = False
        if not valid_path:
            errors.append("invalid content path: " + key)
        provenance = item["provenance"]
        if provenance["license"] not in LICENSES:
            errors.append("unresolved license: " + key)
        if provenance["kind"] == "upstream" and (
            provenance["review_status"] != "accepted" or not provenance["review_evidence"].strip()
        ):
            errors.append("unreviewed upstream: " + key)
        for dependency in item["requires"]:
            if dependency not in components:
                errors.append("missing dependency: " + dependency)
        for conflict in item["conflicts"]:
            if conflict not in components:
                errors.append("unknown conflict: " + conflict)
    try:
        tuple(TopologicalSorter({k: c["requires"] for k, c in components.items()}).static_order())
    except CycleError:
        errors.append("dependency cycle")
    # Every declared profile must work with the mandatory core. Combinations
    # of profiles are checked by compose(), not assumed compatible.
    selections = [({}, "core")]
    selections += [({"profiles": [identity(p)]}, identity(p)) for p in data["profiles"]]
    selections += [({"component": k}, k) for k, c in components.items()
                   if c["kind"] == "skill" and c["lifecycle"] in ("active", "deprecated")]
    for selection, label in selections:
        try:
            _compose(data, **selection)
        except ValueError as error:
            errors.append(label + ": " + str(error))
    return sorted(set(errors))


def compose(data, root=None, profiles=(), component=None, *, verified_paths=None):
    errors = validate(data, root, verified_paths=verified_paths)
    if errors:
        raise ValueError("\n".join(errors))
    return _compose(data, profiles, component)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--root", type=Path, help="content root; default: catalog's directory")
    parser.add_argument("--profile", action="append", default=[])
    parser.add_argument("--component", help="explicit canonical skill ID@version")
    args = parser.parse_args()
    try:
        data = json.loads(args.catalog.read_text())
        selected = compose(data, root=args.root or args.catalog.parent,
                           profiles=args.profile, component=args.component)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps({"selected": selected}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
