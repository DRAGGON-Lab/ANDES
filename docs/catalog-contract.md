# Local catalog and profile contract v1

Review candidate for A1.3 / issue #16. Prerequisite: A1.2 inventory accepted by the maintainer in chat on 27 November 2026, with its import restrictions retained. Rigour L2; implementation owner: architect agent; independent architect agent reviews the exact candidate; human acceptance remains required before dependent implementation.

## Representation and composition

`schemas/catalog-v1.schema.json` defines structural contract version `1.0.0`. This is a data format version, not an ANDES release. The local document holds components, mandatory core references, and profile definitions. Each stable ID has exactly one version in the document. References are exact `id@major.minor.patch` numeric triplets; no ranges, fetching, release solving, or cross-document resolution.

Components have an ID, version, description, kind, canonical content path, lifecycle, requires/conflicts lists, and provenance. Kinds are norm, principle, skill, playbook, role, and tool. Skills also declare a unique canonical invocation name. Native invocation syntax, metadata and role configuration belong in a later adapter; canonical names do not establish native support.

Core is always included and its dependency closure must contain a norm. Profiles add components and dependencies; they cannot remove core, replace a definition, change its version, or override instructions. Any declared one-sided conflict among selected components rejects the selection. Each profile is checked individually against core; selecting multiple profiles additionally checks their combined closure. Duplicate IDs, unknown references, dependency cycles, unsupported schema versions, and invalid content paths reject the catalog.

The compact core's intended responsibilities are orientation, a proportional contract, verification and handoff, under the existing Constitution. This task supplies synthetic fixtures only. A1.5 will author the real focused skills and minimal routing pointers. Catalog selection returns identities; it neither reads instruction bodies into agent context nor executes tools. Inclusion in the mandatory core is not a command to eagerly load every skill/reference body.

Direct invocation selects one skill by exact component reference and includes core plus its declared dependencies. This bypasses routing, not constitutional requirements or authorization. The canonical invocation name is metadata for adapters; the CLI's `--component` option exercises selection only.

## Provenance, lifecycle and precedence

Original components record license and attribution. Upstream components additionally record source URL, immutable SHA, source path, review status and review evidence. Only accepted upstream review with nonblank evidence is eligible in this catalog. The accepted inventory is not import clearance. Draft/unreviewed candidates remain in the inventory or review workspace rather than an eligible catalog.

The validator recognizes MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, CC0-1.0, CC-BY-4.0 and CC-BY-SA-4.0 identifiers. Other identifiers, unresolved terms and proprietary/ARR material fail closed. Adding an identifier or expression requires explicit contract review; a recognized identifier alone does not establish legal compatibility. Humans must verify attribution, notice/share-alike duties, dependency closure and the review evidence. The validator checks metadata, not the truth of an attestation or license compliance of prose.

Lifecycle is draft → active → deprecated → retired, under maintainer review. The catalog records a state; it does not enforce historical transitions or grant promotion authority. Only active/deprecated components may be selected; deprecated components retain their identity for migration, while draft/retired content may remain recorded but cannot enter a selected closure.

Constitutional norms remain mandatory; principles guide judgment; playbooks compose workflows; roles bound responsibility; tools identify deterministic mechanisms without granting execution permission. Profiles and project/task context may specialize behavior only within the Constitution, actual runtime instruction precedence and approved task authority. Catalog ordering cannot override host instructions; A2.1 must establish native precedence separately.

## Checks and interfaces

Setup: `uv sync --locked` (project-local environment; Python 3.12+). Offline repeat after setup: `.venv/bin/python -m unittest discover -s tests -v`.

Validate the positive fixture:

```sh
.venv/bin/python scripts/validate_catalog.py tests/fixtures/catalog/valid.json
.venv/bin/python scripts/validate_catalog.py tests/fixtures/catalog/valid.json --component andes.fixture.verify@1.0.0
```

CLI accepts a local catalog, optional `--root` content directory (defaults to the catalog's directory), repeated exact `--profile` references and optional `--component`. It prints sorted selected identities as JSON on success (exit 0); rejected input produces diagnostics on stderr (exit 1). Paths must resolve to existing files inside the content root; escaping symlinks are rejected. File existence is checked, but contents are not executed or interpreted.

Python helpers are `validate(data, root) -> list[str]` and `compose(data, root, profiles=(), component=None) -> list[str]`; composition always validates and raises `ValueError` for rejected documents/selections.

The synthetic negative fixtures wrap a catalog and expected diagnostic; tests extract the catalog before validation. They are test cases, not valid catalog documents. Tests cover duplicate IDs, dependency failures/cycles, unresolved licenses, upstream clearance, lifecycle, incompatible selections, path boundaries, schema boundaries and direct selection. Native discovery/routing, secret scans, GitHub CI, installation and release are outside #16.
