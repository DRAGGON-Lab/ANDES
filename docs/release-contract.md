# Local release resolution v1

[A2.2 / #19](https://github.com/DRAGGON-Lab/ANDES/issues/19) resolves an unpacked local snapshot to a deterministic JSON record. [ADR-005](decisions/ADR-005.md) describes the proposed trust and composition boundary.

## Manifest and inventory

Place `manifest.json` at the artifact root. The [draft 2020-12 schema](../schemas/manifest-v1.schema.json) defines the structure. The caller provides the exact `id@version` and the lowercase SHA-256 of the raw manifest from a trusted record outside the artifact. The resolver compares the digest before parsing. Formatting changes to the manifest change its pin.

| Field | Meaning |
|---|---|
| `schema_version` | Manifest format version `1.0.0`. |
| `release` | Stable `id` and exact `version`, pinned together as e.g. `andes@0.0.0`. |
| `source` | HTTPS repository URL with a repository path and a full, 40-character lowercase Git `commit`. URLs omit credentials, queries and fragments. |
| `catalog` | Relative `path`, catalog `schema_version` and `sha256` of the raw catalog bytes. |
| `files` | One `path` and `sha256` for every component file and shared resource. Each catalog component has its own declared file. Remaining entries are shared resources. |
| `profiles` | All available exact profile identities. The set must equal the catalog's declarations. |
| `adapter` | Relative `path` and `sha256` of the JSON adapter constraints record. |
| `provenance` | Relative `path` and `sha256` of an opaque, local provenance record. |

Manifest, catalog and adapter JSON are UTF-8 and reject duplicate object keys. The catalog, adapter, provenance, manifest and payload files occupy distinct paths. Each path uses slash-separated ASCII segments drawn from letters, digits, periods, underscores and hyphens. Empty segments, trailing periods, and reserved device names such as `NUL` or `COM1` are invalid. Every directory must be a prefix of a declared file. Extra entries, missing entries, repeated or case-colliding paths, file/directory collisions, symlinks, hard links and nonregular files fail resolution. Reads use directory descriptors and no-follow checks. The catalog is parsed from the verified bytes.

The release, manifest schema, catalog schema, profile, component and adapter versions express separate identities. Exact profile and component references follow the [catalog contract](catalog-contract.md). The resolver checks the whole inventory, then composes required core and selected profiles including dependencies. An empty profile selection includes mandatory core and its closure. Repeated profile identities are deduplicated. Any selected conflict or unsupported kind rejects the request.

The caller supplies a stable, unpacked local snapshot and a trusted path to it. Reverify the pin and the bytes before any later use. A valid pin establishes byte identity. Source attribution, provenance review, legal clearance and release approval remain human decisions. Resolution performs local reads and writes its result to stdout. The CLI uses a host with descriptor-relative filesystem and no-follow support.

## Adapter and output

The adapter record has these exact contents in v1, with ordinary JSON key and whitespace flexibility.

```json
{
  "id": "codex-project-local",
  "version": "1.0.0",
  "runtime": {"id": "codex-cli", "version": "0.172.0"},
  "platform": "darwin",
  "architecture": "arm64"
}
```

The caller's target must match the declaration and this resolver's supported tuple. Selected component kinds are `norm`, `playbook` and `skill`. A2.3 owns actual host detection, mapping to the project, ownership and conflict checks.

On success, stdout carries one JSON object and the command exits 0. The resolution `schema_version` is independently versioned at `1.0.0`. The record includes `release` as an exact identity, `source`, `manifest_sha256`, `catalog` (path, schema version and digest), `profiles`, `components` (identity, kind, path and digest), `resources` (path and digest), `provenance` (path and digest), and `adapter` (identity, path, digest and target constraints). Components and profiles are sorted by identity, resources by path, and keys lexically. The output has no timestamps or absolute filesystem paths.

Invalid artifacts or targets exit 1 with stderr and empty stdout. Missing required options and argument syntax errors exit 2. A supplied pin with invalid contents exits 1.

## Reproduce with the synthetic fixture

Run the following from the repository root after the [locked setup](development-workflow.md#local-and-ci-verification). The checked-in pin lives beside the fixture directory and is read separately. For a real review, obtain the pin from the trusted release record.

```sh
artifact=tests/fixtures/release/artifact
pin=$(cat tests/fixtures/release/manifest.sha256)
resolve_fixture() {
  .venv/bin/python -B scripts/resolve_release.py "$artifact" \
    --release andes@0.0.0 --manifest-sha256 "$pin" \
    --adapter codex-project-local@1.0.0 --runtime-version 0.172.0 \
    --platform darwin --architecture arm64 "$@"
}
resolve_fixture
resolve_fixture --profile andes.profile.formal@1.0.0 --profile andes.profile.verify@1.1.0
resolve_fixture --profile andes.profile.formal@1.0.0 --profile andes.profile.fast@1.0.0
```

The first command selects the fixture norm. The second also includes the formal playbook and verification skill. Reversing the profiles gives the same bytes. The third exits 1 because those profiles conflict. The [evidence packet](evidence/a2-2.md) records the successful output digests and the refusal checks.
