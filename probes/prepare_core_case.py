"""Prepare a persistent synthetic workspace for an independent core forward test."""
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("candidate", ROOT / "adapters/codex/candidate.py")
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


def main():
    data = json.loads((ROOT / "tests/fixtures/core-routing/case.json").read_text())
    allowed = {"labels.py", "test_labels.py", "completion-note.txt"}
    if set(data["files"]) != allowed:
        raise ValueError("unexpected synthetic fixture files")
    project = Path(tempfile.mkdtemp(prefix="andes-core-case-")) / "project"
    candidate.project_core(ROOT, project)
    (project / "brief.txt").write_text(data["request"])
    for name, content in data["files"].items():
        (project / name).write_text(content)
    metadata = [
        {"name": item["invocation"], "description": item["description"],
         "path": str(project / ".agents/skills" / item["invocation"] / "SKILL.md")}
        for item in candidate.load_core(ROOT)["components"] if item["kind"] == "skill"
    ]
    (project / "candidate-skills.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(project.resolve())


if __name__ == "__main__":
    main()
