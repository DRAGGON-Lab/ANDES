"""Offline pattern-based secret check. Report locations/types, never matched values."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys

from detect_secrets import SecretsCollection
from detect_secrets.core.log import log as scanner_log
from detect_secrets.settings import transient_settings

# Explicit pattern plugins avoid entropy alarms on reproducibility hashes.
# No verification filters, external baselines, external plugins or network calls.
PLUGINS = ("AWSKeyDetector", "AzureStorageKeyDetector", "GitHubTokenDetector",
           "GitLabTokenDetector", "JwtTokenDetector", "PrivateKeyDetector",
           "SlackDetector", "StripeDetector", "KeywordDetector", "ArtifactoryDetector")


def scan(root, paths):
    root = Path(root).resolve()
    findings = []
    # Suppress third-party diagnostics, which are not under our redaction contract.
    # Never emit captured output or exception text from the scanner.
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        previous = scanner_log.disabled
        scanner_log.disabled = True
        try:
            with transient_settings({
                "plugins_used": [{"name": name} for name in PLUGINS],
                "filters_used": [
                    {"path": "detect_secrets.filters.allowlist.is_line_allowlisted"},
                ],
            }):
                for name in paths:
                    path = root / name
                    if path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file():
                        raise ValueError("unscannable path")
                    # The upstream scanner logs and skips some read errors;
                    # establish readability before relying on its result.
                    with path.open("rb") as source:
                        source.read(1)
                    secrets = SecretsCollection()
                    secrets.scan_file(str(path))
                    for results in secrets.json().values():
                        for item in results:
                            findings.append({"path": str(Path(name)), "line": item["line_number"],
                                             "type": item["type"]})
        finally:
            scanner_log.disabled = previous
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args()
    try:
        paths = args.paths
        if not paths:
            result = subprocess.run(["git", "ls-files", "--cached", "--others",
                                     "--exclude-standard", "-z"], cwd=args.root,
                                    capture_output=True, check=True, timeout=30)
            paths = list(dict.fromkeys(x.decode("utf-8") for x in result.stdout.split(b"\0") if x))
        if not paths:
            raise ValueError("no input files")
        findings = scan(args.root, paths)
    except Exception:
        print("FAIL: secret scanner could not complete; no source diagnostics displayed", file=sys.stderr)
        return 2
    for finding in findings:
        print(json.dumps(finding, ensure_ascii=True), file=sys.stderr)
    if findings:
        print("FAIL: potential secrets; review reported locations privately", file=sys.stderr)
        return 1
    print("PASS: offline pattern secret scan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
