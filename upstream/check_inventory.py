"""Check A1.2 inventory consistency; this is not an A1.3 catalog validator."""
import hashlib
import json
import re
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    data = json.loads((root / "inventory.json").read_text())
    expected = {
        "Gonza10V/ECx", "affaan-m/ECC", "cursor/plugins",
        "mattpocock/skills", "google-research/dream-rsi",
        "isambard-sc/skills.isambard.ac.uk",
    }
    sources = {s["repository"]: s for s in data["sources"]}
    assert len(sources) == len(data["sources"]) == 6
    assert set(sources) == expected
    ids = set()
    for source in sources.values():
        assert re.fullmatch(r"[0-9a-f]{40}", source["revision"])
        assert source["access"] == "public_read_observed"
        assert source["tree_truncated"] is False
        paths = [p["path"] for p in source["skill_paths"]]
        assert len(paths) == len(set(paths))
        for item in source["skill_paths"]:
            assert re.fullmatch(r"[0-9a-f]{40}", item["blob_sha"])
    for component in data["components"]:
        assert component["id"] not in ids
        ids.add(component["id"])
        source = sources[component["repository"]]
        assert component["revision"] == source["revision"]
        assert component["url"].endswith(component["revision"] + "/" + component["path"])
        assert component["import_status"] == "blocked_pending_component_import_review"
        assert set(component["license_paths"]) <= set(source["license_files"])
        for field in ("attribution", "dependencies", "adaptation_rationale", "design_decisions"):
            assert component[field]
        if component["path"].endswith("/SKILL.md"):
            assert {"path": component["path"], "blob_sha": component["blob_sha"]} in source["skill_paths"]
    assert len(ids) == 10
    print("PASS: six pinned sources, ten blocked-import candidate records; internal consistency only")
    for name in ("README.md", "inventory.json", "check_inventory.py"):
        print(hashlib.sha256((root / name).read_bytes()).hexdigest(), name)


if __name__ == "__main__":
    main()
