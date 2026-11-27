# Foundation development workflow

A1.4 / issue #18 review candidate, L2. Owner: platform engineer; reviewer: independent security agent. Prerequisites A1.1 and A1.3 accepted. This task adds templates, local checks and a proposed GitHub Actions workflow. It does not apply protection settings, publish a candidate or authorize merge/release.

## Local and CI verification

After `uv sync --locked`, run:

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_catalog_fixtures.py
.venv/bin/python upstream/check_inventory.py
.venv/bin/python scripts/check_secrets.py
```

The catalog fixture check invokes the real validator CLI: one valid catalog must exit 0, and all seven invalid catalogs must exit 1 with the expected rejection category. An unexpected pass, rejection, diagnostic or missing fixture fails the check. This is separate from unit assertions. The inventory check covers source/provenance metadata consistency; it is not license clearance.

`.github/workflows/foundation.yml` runs these commands on pull requests and main pushes using an Ubuntu runner, Python 3.12, pinned uv, the committed lockfile and full-SHA action references. The job has read-only contents permission, checkout does not persist credentials, caches are disabled, no secrets or write tokens are passed to tests, and untrusted PR code is never run in a privileged `pull_request_target` context. Dependency setup uses network access; the tests/checks do not require it. No deployment, publication or GitHub mutation step exists. The job timeout is ten minutes.

## Secret scan policy and limits

The pinned detect-secrets 1.5.0 library is used with an explicit list of pattern detectors. No entropy detector, online verification, custom external plugin, global baseline or user configuration is loaded. It scans tracked and non-ignored untracked working-tree files; in CI these are the candidate checkout. It does not scan history or ignored files and is not a guarantee that arbitrary confidential data will be recognized.

Only path, line and detector type are emitted, JSON escaped; scanner source output and exception details are suppressed. Exit 0 means no pattern finding, 1 means potential secrets, 2 means scanner failure/unscannable input. Symlinks and files outside the selected root fail rather than being followed. All files currently in this text-only repository are in scope; binary support is not claimed.

The standard inline allowlist filter is enabled for reviewed false positives. The sole initial exception is the public `detect-secrets==1.5.0` package declaration in pyproject.toml. Additions to these annotations require human review; this CI check cannot prevent a candidate from changing its own scanner or suppressions. Never paste a detected credential into an issue, PR, test expectation, baseline or log; review privately and rotate actual credentials through the appropriate owner. Negative tests generate a synthetic value in a temporary file and check both rejection and absence of that value from stdout/stderr.

## Proposed protection rules — not applied

Once the workflow has a successful hosted run and the maintainer approves the exact administrative change:

- Protect main with pull requests and at least one independent human approval; dismiss stale approvals and require approval after the most recent push.
- Require the `Foundation checks` check from GitHub Actions against the current candidate and require resolved review conversations.
- Disallow force pushes and branch deletion; restrict bypass/administrative exceptions to accountable maintainers and record any exception.
- Preserve read-only default workflow permissions and separately restricted release credentials. No test job receives release or administration authority.

Before applying, verify plan/organization capabilities, permissions, exact required-check identity and availability of another human reviewer. Record any unsupported rule; do not silently substitute weaker protection or lock out the sole maintainer. A separate human administrative action is required. A workflow and tests are not an enforcement boundary when a PR can modify both.

## Observed settings and acceptance

The independent read-only snapshot is in `docs/evidence/a1-4-settings-observed.json`: main reported `protected: false` at baseline `5b838b1`, and the ruleset listing including parent rulesets was empty on 27 November 2026. The proposal above is not active protection.

Local pass/fail evidence and independent review belong in `docs/evidence/a1-4.md`. Hosted GitHub Actions behavior, effective permissions and protection enforcement remain unverified until the concrete candidate is published and observed. #18 and #4 must not be closed as fully verified based solely on local runs. Human acceptance is separate from merge/release authority.
