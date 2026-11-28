# Foundation development workflow

The A1.4 checks/templates and subsequent A1.5 core check are implemented, accepted and merged. Issues [#18](https://github.com/DRAGGON-Lab/ANDES/issues/18) and [#4](https://github.com/DRAGGON-Lab/ANDES/issues/4) are closed. [Current reconciliation](evidence/foundation-closeout.md) links the reviewed main revision, acceptance and hosted results. Repository protection remains an unapplied administrative recommendation, not a property conferred by CI.

## Local and CI verification

With uv and Python 3.12+ available, run from the repository root:

```sh
uv sync --locked
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_catalog_fixtures.py
.venv/bin/python scripts/validate_catalog.py catalog/core.json --root .
.venv/bin/python upstream/check_inventory.py
.venv/bin/python scripts/check_secrets.py
git diff --check
```

uv installs the locked verification dependencies into `.venv`; it may use/download a managed interpreter and package cache. It does not install ANDES into a real Codex home. Record the actual revision, dirty state, inputs, environment, results and omissions for each substantial run.

The catalog fixture check invokes the real validator CLI: one valid catalog must exit 0, and all seven invalid catalogs must exit 1 with the expected category. Unexpected status/diagnostics or missing cases fail it. The separate core check validates the actual source catalog. The inventory check verifies source/provenance metadata consistency, not legal clearance.

`.github/workflows/foundation.yml` runs the checks on pull requests and main pushes using Ubuntu, Python 3.12, uv 0.13.10, full-SHA actions and the committed lockfile. Its job has contents-read permission, nonpersisted checkout credentials, disabled caches, no supplied secrets/write tokens and a ten-minute timeout. It does not use privileged pull_request_target execution or deploy/publish/mutate GitHub. Dependency setup needs network; tests/checks do not. [Hosted checks passed at reviewed main](https://github.com/DRAGGON-Lab/ANDES/actions/runs/46088248359); a closeout-local rerun is a distinct observation, not a new hosted run.

## Native fixtures are separate

The accepted [compatibility probe](codex-compatibility.md) and [core loading fixture](core-fixture.md) have recorded independent macOS ARM64 evidence for CLI 0.172.0. They are not run by ordinary Linux CI and do not establish cross-platform native compatibility.

The core capture observes explicit skill-input assembly and absent unneeded bodies/references; its endpoint is configured for an error without inference. It does not verify native implicit matching, successful native inference, relative-reference following, role execution, production plugin installation or release installation/rollback. Manual reproduction needs its own appropriate environment and authorization; the documentation closeout does not rerun these probes.

## Secret scan policy and limits

Pinned detect-secrets 1.5.0 uses explicit offline pattern detectors plus the reviewed inline-allowlist filter. No entropy detector, online credential verification, external plugin, global baseline or personal configuration is loaded. It scans tracked and non-ignored untracked working-tree files, not history/ignored files, and cannot guarantee detection of arbitrary confidential data.

Only JSON-escaped path, line and detector type are emitted; raw matching values and third-party diagnostics are suppressed. Exit 0 means no pattern finding, 1 means potential secrets, and 2 means scanner failure/unscannable input. Symlinks/outside-root inputs fail rather than being followed. Binary support is not claimed.

The initial inline exception is the public detect-secrets package declaration in pyproject.toml. Human review is required for suppression/scanner changes; a candidate cannot provide independent enforcement of its own checks. Review actual findings privately and handle real credentials through the appropriate owner, never by pasting them into logs, fixtures, issues or PRs. Synthetic tests cover rejection, redaction, failure and absence of online verification.

## Administrative protection decision

[Repository protection recommendation](repository-protection.md) specifies pull requests, exact check identity/source, human review, resolved conversations, force/deletion restrictions, sole-maintainer implications and rollback. It is explicit but **unapplied**. The [read-only settings snapshot](evidence/foundation-settings-observed.json) reports main unprotected and no listed rulesets; detailed protection settings returned 403 to the integration. Recheck them with authorized administrative access before any separately approved application.

## Evidence and acceptance

[Historical receipts](evidence/README.md) preserve original revisions, failures and pending statements. Their later acceptance, merges and hosted results are reconciled in [foundation closeout](evidence/foundation-closeout.md). Foundation acceptance does not clear future upstream imports or authorize a release, later-task implementation, settings changes or production installation.
