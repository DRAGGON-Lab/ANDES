# ANDES product definition

**Status:** approved product direction (Design v0.1); bootstrap wording for maintainer review. See [design baseline](docs/design-baseline.md) for decision IDs. This is not a claim of implemented functionality.

## Problem

AI-assisted research often lacks consistent initial context, reliable acceptance criteria, reproducible evidence, continuity between agents and mechanisms for independent criticism. Generated code may work on a narrow test while being scientifically invalid or poorly understood by its human owner. Fragmented skill collections and uncontrolled autonomy amplify this risk. ANDES makes the research and engineering process explicit, proportionate and inspectable.

## Users and jobs to be done

| User | Job | Expected value |
|---|---|---|
| Student or new researcher | Orient to a project; learn, implement and explain a contribution | Independent understanding and fewer repeated context questions |
| Researcher or engineer | Specify, delegate, review and resume bounded work | Correct, maintainable, traceable software and experiments |
| Domain owner | Review mathematical, numerical, ML, biological or HPC decisions | Appropriate scientific evidence and domain standards |
| Project lead / PI | Prioritize, authorize and accept consequential work | Accountable progress and transparent risks |
| Maintainer / reviewer | Curate, evaluate, version, release and roll back workflows | Controlled improvement without exposing private records |

## Goals and non-goals

Goals: improve functional and engineering quality, mathematical and scientific validity, reproducibility, human learning, collaboration reliability and resource efficiency. Evaluate these independently. Preserve evidence, including failures and missing checks. Reduce unnecessary context and tooling overhead. Make lab-wide knowledge reusable with explicit permission.

Non-goals: replacing accountable researchers; guaranteeing scientific truth from code execution; grading students automatically; replacing Codex or building a universal agent runtime at inception; importing every upstream skill; requiring a centralized service, vector database or permanent team; self-authorizing releases, protected merges, spending or remote/laboratory operations. No private transcript collection by default. No general-purpose GUI or SaaS in the initial scope.

## Primary workflows

| Workflow | Expected result |
|---|---|
| Install and orient | Pinned approved core and selected profiles, non-destructive configuration and verified project context |
| Learn / Pair | Researcher chooses mode; meaningful explanation, worked examples and independent understanding checks |
| Delegate | Proportional contract, bounded implementation, independent verification where required, evidence-bearing handoff |
| Research and benchmark | Explicit question/hypothesis, assumptions, protected evaluation where confirmatory, provenance and uncertainty |
| Communicate | Concise GitHub issues/PRs, consistent mathematical definitions, Neruda documents derived from traceable evidence |
| Autonomous team | Authorized mission, enforced limits, isolated ownership, recoverable state and independently verified deliverables |
| Evolve | Retrospective, Arena and historical replay, controlled comparisons, candidate review and human promotion |

Autonomous mode is an execution policy, not an educational mode; scientific rigour and authority are independent of it. The researcher controls pedagogical mode and the agent can recommend adjustments. Central contributions require appropriate human understanding before dissemination.

## Delivery scope and acceptance

"v1" here refers to a staged useful product, not a promised package version or calendar deadline. Implementation Plan v0.1 defines M1-M6 and an integrated pilot. Releases are scoped to capabilities that pass applicable gates; an early release does not wait on experimental Dreaming.

| Increment | User-visible scope | Minimum release evidence |
|---|---|---|
| M1 foundation | Compact core, native Codex discovery and pinned distribution | Isolated install/update/rollback without damaging existing user configuration; catalog, source permissions and supported platform evidence (G0/G1) |
| M2 usable engineering and learning | Context orientation, task contracts, engineering, GitHub communication and teaching | Complete and explain a representative verified engineering task, with handoff, review and appropriate mathematical communication (G2) |
| M3 science and HPC | Mathematical, numerical, ML, biological standards and Isambard profiles | Domain-specific reference/invariant tests, protected evaluation, provenance, cluster-specific validated guidance (G3) |
| M4 communication | ANDES authoring and review integration with standalone Neruda | Reproducible paper and presentation from common evidence; explicit missing claims, rendered-document review (G4) |
| M5 missions | Dynamic roles, bounded coordination, Arena and mission recovery | Fault tests for isolation, cancellation, limits, recovery and protected checks; human acceptance (G5) |
| M6 evolution | Evaluations, retrospective, candidate improvement and Dreaming | Independent protected graders, complete attempts, replay coverage and fresh held-out live verification; human promotion (G6/G7) |
| Integrated pilot | Approved researcher adoption | Consented/authorized use, usability and understanding evidence, support, rollback and human acceptance (G8) |

Initial MVP: M1 plus the first useful M2 engineering/learning slice (A2.5 and A4.5 are planned frontiers after prerequisites). Deliver a real tested native workflow rather than speculative broad interfaces. Scientific profiles and Neruda may be developed in parallel once their dependencies permit. Autonomy and Dreaming remain disabled or experimental until their release gates are satisfied.

## Success criteria

- An authorized researcher can install a pinned release, discover the relevant workflow, complete a bounded task and resume from an evidence-bearing handoff.
- A reviewer can trace each accepted claim to the actual revision, inputs, method and checks; failed, partial and not-run checks remain visible.
- A researcher can explain central mathematical and engineering decisions, assumptions, evidence and limitations without depending solely on generated output.
- A maintainer can compare stable and candidate workflows with protected outcomes, reject regressions and restore a known release without altering research work.
- Where autonomous execution is offered, permissions, budgets, cancellation, recovery and human release authority are demonstrated rather than asserted.

Measure accepted-task throughput, elapsed/blocked/review time, observed defects, validation outcomes, reproducibility, resource use and independent learning outcomes where appropriate. No fixed universal coverage threshold, productivity target, numerical quality average or student telemetry score. Establish baselines before setting quantitative targets. Research involving people or their records needs appropriate governance and authorization.

## Constraints and priorities

Core compact and versioned; profiles composable; Codex first, portable canonical representation; Neruda standalone; ECx independent. Prefer behavioral tests and deterministic validators over redundant prompt instructions. Use public-safe synthetic examples; private project evidence stays under project ownership. Scope, compatibility, packaging and deployment decisions require documented validation. Follow the approved XP + Kanban operating model in [CONTRIBUTING.md](CONTRIBUTING.md). Unknown native interfaces, language choice, support matrix, sample sizes and staffing are implementation discovery, not approved technical facts.
