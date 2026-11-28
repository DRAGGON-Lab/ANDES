# Agent collaboration guide

Read [AGENTS.md](AGENTS.md) for the startup entry and [CONSTITUTION.md](CONSTITUTION.md) for the normative rules. This file is the operational coordination guide, not a separate policy or a grant of permissions. The [foundation closeout](docs/evidence/foundation-closeout.md) records accepted A1/A2.1 work; do not reimplement it under later tasks.

## Roles

- Human maintainer / project lead: approves scope, consequential decisions, permissions, public-safe publication, release and exceptions within policy. Designate domain and independent reviewers as required.
- ChatGPT / planning agent: clarify requirements, inspect sources, compare alternatives, write task contracts and decompose work; review whether evidence addresses intent. Recommendations are not decisions until approved.
- Codex / execution agent: implement accepted bounded work; test, refactor, document and return evidence. Do not silently expand task scope or modify protected settings.
- Independent reviewer: inspect exact artifact and contract; reproduce critical checks and report findings; not the sole responsible human approver.

## Start each task

1. Read repository instructions, product, relevant architecture and accepted ADRs/decision references. Inspect `git rev-parse HEAD` and `git status --short`; preserve unrelated edits. Confirm assigned task, allowed paths and authority. Treat previous handoffs as claims to revalidate against artifacts.
2. Recommend L0-L3 rigour, mode and relevant context. Establish or recover a contract before consequential work. L1: objective, acceptance and constraints; L2/L3/autonomous: formal scope, motivation, dependencies, protected invariants, roles, evidence and escalation. Do not lower criteria after starting.
3. Identify whether the next useful action is planning (ambiguous requirements, architectural tradeoff, unknown capability, broad refactor) or execution (approved bounded contract). Return unknown technology questions to planning/discovery and human review. No speculative implementation API.
4. Work from the unblocked dependency frontier. One owner per overlapping write scope. Use isolated worktrees when justified; no unrelated branch or configuration changes. Keep work small, readable and runnable when the capability exists.

## Execution and verification rules

Use behavior-driven TDD for meaningful changes where practical: reproduce, define an independent observable check, implement the smallest correction, refactor and rerun. Write tests for non-trivial logic and failure paths. If failing-first is impractical, explain why and use the closest meaningful check. Never weaken protected tests. Update docs, provenance and ADRs when accepted behavior changes. Do not invent a test command or claim a pass without execution; the [development workflow](docs/development-workflow.md) lists the implemented test, catalog, provenance and secret checks. Keep hosted Foundation checks working. Native probes have separate recorded macOS environments and are not part of ordinary Linux CI; no container setup is required.

Use the separate quality dimensions and statuses from the Constitution. Distinguish code correctness, mathematical/numerical correctness, scientific validity, reproducibility and human understanding. Preserve negative and timed-out attempts. For an L2/L3 task, independent review at exact revision is required; report reproduced defects, statically established violations and unverified risks separately. Independent review does not override human acceptance.

## Boundaries and escalation

Routine read-only investigation and explicitly scoped implementation/test execution are allowed only within granted access and budget. Escalate requirement or interface changes, material dependencies, installation/repair, protected evaluation changes, sensitive data, unsafe or irreversible operations, costs, production, remote jobs, publication or scope/budget extensions. No agent may independently approve canonical releases, protected branch merge, resource expansion, permission changes, deletion of important data or sharing restricted records. Repository edits and checks are permitted within an explicitly authorized task; retain authorization already granted in the session. These instruction files do not independently authorize GitHub publication, administrative settings, protected merges or releases. Review authorization is not publication authorization.

A long-running mission needs an independently enforceable approved contract, protected gates, bounded retries, checkpoints, cancellation and recovery. If enforcement is unavailable, stop rather than rely on a prompt. Any changes to protected criteria need recorded human approval. Never confuse a budget-exhausted or blocked task with a successful one.

## Progress and handoff

Use a short decision-rich update, not a transcript:

```text
Task / objective / acceptance:
Repository, exact revision, dirty state, release/profile identity:
Scope and granted permissions; owner / reviewer:
Completed actions and changed files:
Checks: method or command, input identity, environment, result, timestamp, artifact:
Unresolved failures / omissions / risks:
Accepted decisions and proposals needing human review:
Next executable action and prerequisites:
```

Use `pass`, `fail`, `partial`, `not_run`, `not_applicable` with rationale; not-run is not pass. Do not copy credentials, private session history or learning records. When writing equations, follow the ordered definition convention; use graphs, diagrams, code and worked examples where they improve understanding. A researcher should be able to explain central decisions and limitations.

## ADR and change-control triggers

Draft an ADR for meaningful competing approaches, shared interfaces/schema changes, new dependencies/runtime assumptions, material permissions, cost/security/reproducibility tradeoffs or hard-to-reverse migrations. Record status, alternatives, rationale, consequences, risks, validation and revisit triggers. A proposal does not override accepted design. Stop and request planning/human review before substantial unapproved refactors. Keep each PR a concise why/change/evidence/risk briefing following [CONTRIBUTING.md](CONTRIBUTING.md).
