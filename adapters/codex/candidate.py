"""Temporary test projection only; this module is not an installer."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("andes_catalog", ROOT / "scripts/validate_catalog.py")
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


def load_core(source_root):
    source_root = Path(source_root).resolve()
    data = json.loads((source_root / "catalog/core.json").read_text())
    errors = catalog.validate(data, source_root)
    if errors:
        raise ValueError("\n".join(errors))
    return data


def select_skill(source_root, name):
    data = load_core(source_root)
    matches = [item for item in data["components"]
               if item["kind"] == "skill" and item["invocation"] == name]
    if len(matches) != 1:
        raise ValueError("unknown or ambiguous canonical skill")
    catalog.compose(data, source_root, component=catalog.identity(matches[0]))
    return matches[0]


def project_core(source_root, project):
    source_root = Path(source_root).resolve()
    project = Path(project).resolve()
    temporary = Path(tempfile.gettempdir()).resolve()
    if (project.is_relative_to(source_root) or not project.is_relative_to(temporary)
            or project == temporary or (project.exists() and any(project.iterdir()))):
        raise ValueError("candidate projection requires an empty temporary project")
    data = load_core(source_root)
    copies = []
    for item in data["components"]:
        if item["kind"] == "skill":
            folder = source_root / Path(item["path"]).parent
            for path in sorted(folder.rglob("*")):
                if path.is_symlink() or not path.resolve().is_relative_to(source_root):
                    raise ValueError("unsafe candidate source")
                if path.is_file():
                    destination = Path(".agents/skills") / item["invocation"] / path.relative_to(folder)
                    copies.append((path.relative_to(source_root), destination))
        elif item["kind"] in ("norm", "playbook"):
            copies.append((Path(item["path"]), Path(item["path"])))
        else:
            raise ValueError("unsupported candidate component kind")
    # Read and validate all sources before writing the fixture.
    sources = []
    for source, destination in copies:
        path = source_root / source
        if path.is_symlink() or not path.resolve().is_relative_to(source_root):
            raise ValueError("unsafe candidate source")
        sources.append((source, destination, path.read_bytes()))
    project.mkdir(parents=True, exist_ok=True)
    manifest = {"kind": "temporary_candidate_only", "files": []}
    for source, destination, content in sources:
        path = project / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        manifest["files"].append({
            "source": source.as_posix(), "destination": destination.as_posix(),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    # This generated test instruction chain projects canonical policy; it is
    # not a second maintained copy or a change to personal AGENTS files.
    (project / "AGENTS.md").write_text(
        (project / "CONSTITUTION.md").read_text() + "\n\n" +
        (project / "skills/ROUTING.md").read_text())
    (project / "candidate-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def native_skill(source_root, project, name, entries):
    select_skill(source_root, name)
    matches = [entry for entry in entries if entry.get("name") == name]
    if len(matches) != 1:
        raise ValueError("missing or ambiguous native skill")
    expected = (Path(project) / ".agents/skills" / name / "SKILL.md").resolve()
    actual = Path(matches[0].get("path", "")).resolve()
    if actual != expected:
        raise ValueError("native path does not match this candidate projection")
    return {"type": "skill", "name": name, "path": str(expected)}
