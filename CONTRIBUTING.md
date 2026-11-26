# Contributing to ANDES

ANDES uses Extreme Programming (XP) and Kanban with evidence-based release gates. Small independently verifiable slices are preferred to large agent-generated changes. This policy is a review candidate; GitHub settings have not been configured by the bootstrap.

## Ownership and public boundary

A designated human lab maintainer approves canonical norms and stable releases; repository and profile maintainers accept scoped contributions under delegated policy. Project leads authorize project work. A producer must not be the sole final reviewer when L2/L3 independent review is required. Contributors and agents propose and evaluate improvements; they do not self-promote releases.

Public: reviewed infrastructure, synthetic examples, cleared source metadata and suitable aggregate evaluation findings. Restricted: unpublished research, sensitive inputs, private traces and learning records, credentials, evaluator-only fixtures and other data requiring controlled access. Obtain permissions and institutional IP/data approval as applicable. Do not expose secrets in diffs, issues, CI artifacts or logs. An MIT repository does not relicense third-party assets; preserve notices. Source audit before each import: exact repository/revision/path, applicable license, attribution, dependencies, intended adaptation, validation and reviewer disposition. ECx access does not itself authorize publication. Use official Isambard guidance only within permitted terms and execution procedures.

## Pull-based delivery

Backlog -> Ready -> In progress -> Independent review -> Verified -> Accepted -> Released (where applicable). Blocked items remain visible; resolve prerequisites before starting. Proposed initial limits: two implementation items and two waiting for active review across ANDES and Neruda; tune to reviewer capacity by explicit review. Weekly replenishment and demonstration, biweekly or failure-triggered retrospective, evidence-driven release review. Track accepted tasks, cycle/blocked/review time, defects, evidence and resource usage where observed. No automatic telemetry from private sessions.

### Definition of Ready

Authorized objective, scope and permissions; resolved blockers or a bounded discovery task; exact repository baseline and relevant decisions; clear owner/reviewer; acceptance criteria, required evidence, rigour and invariants; identified resources and protected inputs; verified public/private classification and source rights.

### Definition of Done

Current revision satisfies contract, no unrelated changes; appropriate observed tests, protected checks and independent review; all omissions and unresolved blocking findings explicit; traceable evidence with current inputs; relevant docs/ADRs/provenance/handoff; human understanding where applicable; human acceptance under approved policy. Release adds immutable pin, compatibility, changelog, rollback and applicable gate. Do not close blocked/exhausted work as successful.

## Issue and PR standard

Use concise human-readable issue titles and include motivation, objective, scope/constraints, independently verifiable acceptance checklist, dependencies and expected evidence; link the design/ADR and parent epic when relevant. Use native blocking/parent links when supported, explicit links otherwise. Split by vertical behavior except justified staged cross-cutting migrations.

PR body: **Why**, **What changed**, **Scope / related issue**, **Material tradeoffs** (if needed), **Blast radius / reversibility**, **Verification**. Include exact candidate revision, actual commands/results and artifacts, missing checks and limitations. Visuals, pseudocode and before/after evidence when they help. Aim for a one-minute reviewer briefing, not a transcript. Use close keywords only for fully satisfied and authorized issues. Review findings state severity, location, trigger, impact and how verified; label unverified risks. Do not open, close, publish or merge on the basis of this documentation alone. Machine-readable templates/CI checks are later approved work (A1.4/A4).

## Release and governance

Preserve MIT license; review upstream terms and permission before importing. Stable releases are explicitly human-approved immutable identities, independent of working branch visibility. Scope-specific gates G0 public safety, G1 core distribution, G2 engineering/learning, G3 scientific/HPC, G4 Neruda integration, G5 autonomy, G6 evaluation/evolution, G7 Dreaming and G8 integrated pilot are defined in the approved plan; affected gates must pass, unsupported features stay disabled. Candidate testing in isolated environments is not stable release approval. Roll back managed configuration without deleting research or unrelated personal edits.

Recommend required human PR reviews, applicable CI checks and restricted release credentials; apply branch/ruleset/description changes only by separately authorized administrative action. The initial baseline reported main unprotected, and effective rulesets/permissions require confirmation. Do not assume this proposal changes repository settings.
