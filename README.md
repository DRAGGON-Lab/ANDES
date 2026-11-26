# ANDES

**Agentic Network for Disciplined Engineering and Science**

ANDES is DRAGGON Lab's framework for rigorous AI-assisted software engineering, scientific research and researcher development. It connects researchers, reusable engineering methods, bounded agent teams, deterministic tools and auditable evidence. The aim is reliable knowledge and independent human competence, not simply more AI-generated output.

**Status:** design approved; initial documentation under review. No installable ANDES release, native adapter, mission runtime or evaluator is available in this repository at the inspected bootstrap baseline. Design v0.1 is not a software release number.

## What ANDES will provide

- A compact versioned core, composable domain profiles and focused skills for engineering, mathematical reasoning, reproducible research and learning.
- Proportional task contracts, progressive project context, evidence-based verification, GitHub communication and recoverable handoffs.
- Codex-first integration with portable canonical skill definitions, preserving personal configuration and credentials.
- Dedicated scientific profiles, including HPC and Bristol Isambard script development using vetted official guidance.
- Dynamic agent teams, bounded long-running missions, Arena and Dreaming, introduced only after their respective safeguards and evaluation gates pass.
- Scientific writing and presentation workflows that use [Neruda](https://github.com/DRAGGON-Lab/Neruda), a separately versioned, independently usable document framework.

ANDES is independent of ECx. Existing personal experiments and runtime assumptions are not mandatory dependencies. Selected upstream methods enter through reviewed adaptation and provenance records.

## Start here

| Document | Purpose |
|---|---|
| [PRODUCT.md](PRODUCT.md) | Users, scope, workflows and success criteria |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Component boundaries, integration and planned delivery |
| [CONSTITUTION.md](CONSTITUTION.md) | Norms, rigour and evidence requirements |
| [AGENTS.md](AGENTS.md) | Compact agent startup entry |
| [AGENT.md](AGENT.md) | ChatGPT/Codex coordination and execution rules |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution, review and release governance |
| [Design baseline](docs/design-baseline.md) | Approved decision references and authority |
| [ADR-001](docs/decisions/ADR-001.md) | Independent modular core and adapter boundary |

## Development status and local setup

Once this bootstrap is approved and merged, clone the repository using your authorized Git account and inspect the actual checkout:

```sh
git clone https://github.com/DRAGGON-Lab/ANDES.git
cd ANDES
git rev-parse HEAD
git status --short
```

At the pre-bootstrap revision these are source-inspection steps only; there is no ANDES installer or test runner to invoke. Read the current repository instructions and selected approved work item before editing. The first technical work is an upstream licensing/inventory audit (A1.2) and an isolated native Codex compatibility spike (A2.1). The latter must establish real discovery, precedence, role support and packaging evidence. Do not assume ECx's Node runtime, a native plugin path or a particular CLI.

### Planned layout

```text
ANDES/
  README.md  PRODUCT.md  ARCHITECTURE.md
  CONSTITUTION.md  AGENTS.md  AGENT.md  CONTRIBUTING.md
  docs/                     approved design pointers and ADRs
  skills/ principles/       canonical focused guidance
  profiles/ playbooks/      compatible composition and workflows
  agents/ schemas/          bounded roles and contracts
  adapters/codex/           tested native integration
  templates/ upstream/      reusable templates and provenance
  tests/ examples/          synthetic positive/negative fixtures
  runtime/                  deterministic mechanisms as needed
  evaluations/ dreaming/    staged experimental capabilities
```

Only the foundational documentation is proposed now. Create future modules incrementally when there is an accepted task and defined responsibility. No frontend, network service, database or Docker Compose deployment is required at bootstrap. Use isolated temporary homes for the adapter spike; containers are an option for reproducible tests or later containment, not a substitute for validating native behavior.

### Verification

There are no executable ANDES-specific checks yet. A1.4 and subsequent tasks establish documented CI and test entry points. Review the docs against Design v0.1, check links, preserve the MIT license, confirm public-safe contents and ensure no runtime commands are represented as working prematurely. Once code exists, run the actual checks documented in the repository; do not invent passing receipts.

## Working with ChatGPT and Codex

Use ChatGPT for investigation, decision reduction, task contracts and architecture review. Use Codex for explicitly authorized, scoped changes and executable evidence. Humans accept requirements, consequential decisions and stable releases. Start each session from [AGENTS.md](AGENTS.md); work in small verified slices under XP + Kanban. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Governance and license

Public infrastructure, private research, controlled stable releases. Unpublished evidence, private agent histories, personal learning records, credentials, protected graders and restricted data do not belong here. Public development does not imply release approval. Original code uses the existing [MIT license](LICENSE); upstream components retain their applicable notices and permissions. Review any contribution for university IP, confidentiality, security and third-party terms before publication.
