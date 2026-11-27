"""Exercise good and bad catalog inputs through the same CLI used in CI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/catalog"


def main():
    cases = [(FIXTURES / "valid.json", None)]
    with tempfile.TemporaryDirectory(prefix="andes-catalog-ci-") as directory:
        for fixture in sorted((FIXTURES / "invalid").glob("*.json")):
            data = json.loads(fixture.read_text())
            path = Path(directory) / fixture.name
            path.write_text(json.dumps(data["catalog"]))
            cases.append((path, data["expected_error"]))
        if len(cases) != 8:
            print("FAIL: expected one positive and seven negative catalog fixtures")
            return 1
        for path, expected_error in cases:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/validate_catalog.py"),
                 str(path), "--root", str(FIXTURES)],
                capture_output=True, text=True, timeout=30,
            )
            expected_status = 1 if expected_error else 0
            if result.returncode != expected_status or (
                expected_error and expected_error not in result.stderr
            ):
                print("FAIL: catalog fixture " + path.name)
                return 1
    print("PASS: positive CLI status 0; all seven negative CLI statuses 1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
