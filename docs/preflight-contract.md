# Codex project preflight v1

[A2.3](https://github.com/DRAGGON-Lab/ANDES/issues/24) checks a project-root Codex launch and previews a pinned release. Doctor and install dry-run perform local reads and send a JSON report to stdout. An install plan requires separate approval and live revalidation in [A2.4](https://github.com/DRAGGON-Lab/ANDES/issues/25).

## Inputs and results

Both commands require `--project`, `--home`, `--codex-home`, and `--codex-bin`. Supply existing physical directory paths and the trusted absolute Codex executable. The project needs a root Git directory or worktree marker. Use a stable local snapshot of each input during a run. Dry-run also takes the artifact directory, exact `--release`, trusted `--manifest-sha256`, repeatable `--profile`, and optional `--instructions-review`. [Release contract](release-contract.md)

The host check measures Darwin arm64 and runs only `codex --version` under the macOS sandbox with a timeout and an empty home, denying writes, network, subprocesses and reads under the explicitly supplied roots. The trusted executable is the allowed exception in its directory. The supported runtime is Codex CLI 0.172.0. Raw process diagnostics are suppressed.

The report has `schema_version` 1.0.0, command, ready or blocked status, observed host, instruction review digests when available, findings, and a plan when the install preview is ready. Exit 0 means ready for the stated check. Exit 1 means a blocker and a null plan. Usage errors exit 2. Resolve findings and rerun to continue. Output paths identify their scope and use project-relative or scope-relative spellings.

The planner checks the root `AGENTS.override.md`, the supplied Codex home's global instruction files, and known configuration entrypoints. It reports the presence of `config.toml`, `config.d`, `rules`, `hooks.json` or `plugins` under the project’s `.codex` or supplied Codex home. It leaves their contents unread. Review those configurations separately or use an isolated Codex home. The check covers the named roots for a project-root launch. Nested working directories, alternate discovery settings and managed system configuration require separate verification.

Dry-run uses the original artifact and external pin. It plans selected Markdown norms and playbooks under `.andes/content/` and canonical `skills/<invocation>/SKILL.md` files into `.agents/skills/<invocation>/`. It includes declared Markdown beneath each selected skill's `references/`; other shared files are verified as part of the artifact. Native control filenames and hidden paths are refused in copied Markdown. The first supported skill metadata shape has two plain fields, `name` and `description`, in the first 4096 bytes. Selected skill bodies can be at most 1 MiB. Existing project, user and Codex-home skill roots are inspected for duplicate names and unknown metadata. A pre-existing `.andes` or selected skill directory blocks the plan even if its contents appear identical.

## Review project guidance

1. Run dry-run with the pinned artifact. If the project has `AGENTS.md`, the report requests a review and includes the exact project and policy digests. The policy is the rendered ANDES block assembled from the verified Constitution, other selected norms in path order and the router.
2. Have an ANDES reviewer read the repository file as evidence. Compare each instruction with the pinned Constitution and applicable rigour, evidence, explanation and authority sections. A command such as `make check` can refine how the project verifies work. A directive to report success before verification conflicts with N06. Flag both contradictions and ambiguous guidance, cite the line and governing rule, and explain the reason locally. Obtain the project owner's confirmation of the review.
3. Supply the confirmed record with `--instructions-review`. The record uses `schema_version` 1.0.0, the pinned `manifest_sha256`, the report's `agents_sha256` and `policy_sha256`, `confirmed: true`, `decision` of `compatible` or `blocked`, and a `findings` list. Each finding has a one-based `line`, a `rule` of N01–N12 or `rigour`, `evidence`, `explanation`, `authority`, and a `classification` of `conflict` or `uncertain`. Use an empty list only for a human-confirmed compatible review. Keep private rationale and excerpts in the authorized project context. The caller supplies this record from their trusted reviewer. The CLI verifies binding and structure while semantic judgment remains with the reviewer and project owner.

For a compatible file the plan previews `prepend_reviewed_block`, with the pinned block, existing file digest and exact resulting digest. Existing bytes occupy an unchanged suffix. For a fresh project it previews `create`. Unknown prior ANDES blocks, root overrides and combined instructions over 32 KiB block both routes as applicable. The intended scope is the repository root. Codex can load additional instructions when launched in a nested directory. [Codex instruction discovery and budget](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

## Reproduce

From the ANDES checkout, after `uv sync --locked`, use the checked-in synthetic bytes and a new temporary target. On macOS the version check may need to run outside an outer sandbox that disallows launching its own sandbox.

```sh
fixture=$(mktemp -d)
fixture=$(cd "$fixture" && pwd -P)
mkdir -p "$fixture/project" "$fixture/home/.codex"
git init -q "$fixture/project"
set -- --project "$fixture/project" --home "$fixture/home" \
  --codex-home "$fixture/home/.codex" --codex-bin "$(command -v codex)"
.venv/bin/python -B scripts/preflight.py doctor "$@"
.venv/bin/python -B scripts/preflight.py install --dry-run "$(pwd -P)/tests/fixtures/preflight/artifact" \
  --release andes@0.0.0 --manifest-sha256 "$(cat tests/fixtures/preflight/manifest.sha256)" "$@"
```

Use the absolute physical path of the fixture artifact when invoking the command. On any Foundation CI host, the CLI tests reproduce preflight with synthetic host detection. Before any later write, A2.4 must remeasure the host, reverify the artifact and scope, compare the reviewed existing bytes and conflict state, and obtain approval tied to the exact target and regenerated plan.
