# ANDES

**Agentic Norms for Disciplined Engineering and Science**

ANDES is DRAGGON Lab's framework for rigorous AI-assisted software engineering, scientific research and researcher development. It connects reusable methods, deterministic tools, auditable evidence and accountable human review.

**Status:** the [A1 foundation epic](https://github.com/DRAGGON-Lab/ANDES/issues/4) and prerequisite [A2.1 compatibility spike](https://github.com/DRAGGON-Lab/ANDES/issues/3) are accepted and closed at reviewed main `0f28ee50709354b255e39b325a37b8ce33ccc219`. [Hosted Foundation checks passed](https://github.com/DRAGGON-Lab/ANDES/actions/runs/46088248359). This is a source-level foundation, not an installable or released ANDES product. A1 acceptance does not complete M1's planned distribution gates.

## Implemented foundation

| Capability | Implementation and evidence |
|---|---|
| Canonical catalog and profile contracts | Versioned JSON Schema, local dependency/composition/provenance validation, positive fixture and seven negative fixtures; [contract](docs/catalog-contract.md). |
| Four original core skills | Orient, contract, verify and handoff, with progressive [routing pointers](skills/ROUTING.md) and [core catalog](catalog/core.json). |
| Temporary project-local Codex projection | Candidate-only adapter preserving source bytes; no personal installation. [Bounded forward test and explicit native loading](docs/core-fixture.md) were independently reviewed. |
| Native compatibility probes | Recorded discovery, instruction-source ordering and metadata evidence for Codex 0.172.0 on macOS ARM64; [capability matrix](docs/codex-compatibility.md). |
| Automated verification | 25 unit tests, catalog CLI acceptance/rejection, core/provenance checks and redacted offline secret scanning in [GitHub Actions](.github/workflows/foundation.yml). |
| Upstream provenance inventory | Six pinned sources and ten examined candidates; [inventory](upstream/README.md). Inventory acceptance does not clear future copying. |

The [current-state reconciliation](docs/evidence/foundation-closeout.md) links accepted tasks, merged PRs, ADRs and dated evidence. [Historical receipts](docs/evidence/README.md) retain their original inputs, failures, omissions and fingerprints.

## Local setup and verification

Prerequisites: Git, uv and Python 3.12+. Foundation verification used uv 0.13.10; the CI workflow pins that version. uv may acquire a managed interpreter/dependency cache; dependencies are installed in the project-local `.venv`. This does not install ANDES into Codex.

```sh
git clone https://github.com/DRAGGON-Lab/ANDES.git
cd ANDES
git rev-parse HEAD
git status --short
uv sync --locked
.venv/bin/python -m unittest discover -s tests -v
```

Use an existing authorized checkout instead of cloning again when appropriate. Run the [complete verification sequence](docs/development-workflow.md#local-and-ci-verification) before handoff. It includes the seven-negative catalog fixture check, core validation, provenance, secret scan and `git diff --check`.

Native probes are separate manual macOS fixtures, not ordinary Linux CI or installation commands. See their environment, isolation and approval requirements in the [compatibility report](docs/codex-compatibility.md) and [core fixture guide](docs/core-fixture.md).

## Verified limits and planned product

The bounded evidence establishes independent agent workflow selection/execution and actual explicit CLI skill-input assembly. It does **not** verify native implicit routing, successful native model inference, native relative-reference following, native role execution, production plugin installation, cross-platform native compatibility, or release installation/update/rollback. These are not supported foundation claims; this does not assert that Codex itself lacks those capabilities.

Pinned distribution, domain/scientific and HPC profiles, Neruda integration, mission coordination, Arena and Dreaming remain planned capabilities under separate tasks and gates. No production installer, general runtime, release resolver or release is provided. ANDES remains independent of ECx, and [Neruda](https://github.com/DRAGGON-Lab/Neruda) remains separately versioned.

## Start here

| Document | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) / [AGENT.md](AGENT.md) | Startup instructions, task authority, coordination and handoff |
| [CONSTITUTION.md](CONSTITUTION.md) | Mandatory norms, rigour and evidence requirements |
| [PRODUCT.md](PRODUCT.md) / [ARCHITECTURE.md](ARCHITECTURE.md) | Product targets, implemented boundaries and remaining roadmap |
| [Development workflow](docs/development-workflow.md) | Setup, local/hosted checks and secret-scan limits |
| [Design baseline](docs/design-baseline.md) / [ADRs](docs/decisions/) | Approved direction and consequential decisions |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Public/private boundaries, review and release governance |

## Governance and license

Public infrastructure, private research, controlled stable releases. Unpublished evidence, private histories, credentials and protected evaluation data do not belong here. Original code uses the existing [MIT license](LICENSE); upstream terms remain applicable.

[Repository protection is proposed, not applied](docs/repository-protection.md). A passing workflow is not a required merge check unless repository settings enforce it. Human acceptance, administrative changes, publication and stable release authority remain separate.
