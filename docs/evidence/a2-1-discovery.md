# A2.1 partial discovery receipt

Historical first-discovery receipt. The extended candidate in ../codex-compatibility.md and a2-1.md supersedes this initial capability matrix. This receipt is not acceptance of the full spike or any adapter/installation claim.

Baseline: `5b838b1c87db01330d1eef1f6fa2bd93c5340178`, with accepted A1.2/A1.3 and the separate A1.4 candidate dirty in the shared workspace. User authorized #3 in the staged plan and selected offline-first execution. Owner: platform engineer; L2; independent probe review pending.

## Method and result

Installed runtime: Codex CLI 0.172.0, macOS 27.2.1 arm64. Native binary SHA-256: `f30a99714dc984876864239ef60563949b1e21421a7c9180422f51fd39186bc6`. Command: `.venv/bin/python probes/codex_discovery.py`. Final probe-script SHA-256: `5b0a76b31db255df381ca7d84ff4bb1099b945b7bf874bf54f56e08eb1b7ee3e`.

The probe builds two synthetic skill files and a fresh Git project in temporary storage, uses an allowlisted child-process environment and ephemeral credential storage, and launches app-server directly with strict configuration and no shared daemon. Parent environment is unchanged. No turn/start request or model call is made.

macOS sandbox denies network, all writes except temporary fixture state and /dev/null, real-user-home reads except a read-only native executable directory, administrator skill roots, system keychain reads and securityd lookups. Temporary fixture reads are explicitly permitted. Before starting Codex, controls require successful sandbox launch, an OS-denied read of this public repository README under the real home, an OS-denied write outside the isolated directory, and an OS-denied loopback bind. No private configuration/history file is opened by the controls.

Initial execution inside the parent sandbox could not launch the nested sandbox. An early control implementation treated launch failures as resource denials; it was corrected to require successful launch before testing denials. Approved execution outside the parent sandbox, retaining the probe's own narrower OS sandbox, succeeded. After adding keychain restrictions and stronger error checks, another approved run also succeeded:

- real-home read denied: true;
- outside-fixture write denied: true;
- network bind denied: true;
- discovered `andes-probe-project` and `andes-probe-user`: true;
- discovery errors: zero;
- model calls and turns started: zero.

The response user agent was `andes_offline_probe/0.172.0 (Mac OS 27.2.1; arm64) unknown (andes_offline_probe; 0.1.0)`. Only marker names, control outcomes and runtime identity are retained; ephemeral native state is removed after the process exits.

## Capability matrix and remaining work

| Capability | Status | Limit |
|---|---|---|
| Project/user native skill discovery | pass | Both synthetic scopes discovered in this isolated CLI only. |
| Skill metadata | partial | Minimal name/description accepted; richer metadata not probed. |
| Explicit instruction injection/direct invocation | not_run | Listing a skill is not invocation. |
| Nested/global instruction precedence | not_run | Requires a separate observable probe. |
| Role definitions/execution | not_run | No role spawned or compatibility claim. |
| Packaging/install/update/rollback | not_run | No plugin installed or live account configuration changed. |
| Profile coexistence/implicit routing/selective loading | not_run | Requires separate fixtures and, if necessary, approved bounded model-backed evidence. |

Official manual pages read for probe design: [Build skills](https://learn.chatgpt.com/docs/build-skills.md), [Codex App Server](https://learn.chatgpt.com/docs/app-server.md), [AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md). Local manual cache was fetched during planning on 27 November 2026; installed CLI/help and observed native behavior remain authoritative for this probe. Documentation alone does not establish compatibility.

Independent static review by `/root/workflow_review` found no account-authority expansion/model-call path, and requested the script fingerprint and moving inherited stderr capture into the permitted fixture directory. Both corrections were made. A final approved execution at the script identity above repeated the same successful discovery and control results. The reviewer did not execute the probe or independently reproduce the OS controls.

Quality: functional correctness partial (discovery only); engineering quality partial (static review only); mathematical correctness not_applicable; scientific validity not_applicable; reproducibility partial (script, binary identity and commands recorded, independent execution pending); human understanding not_run. No scientific effectiveness claim, paid execution, credential copying, source redistribution, protected action or release.

Next: independently review isolation/probe evidence; complete the remaining spike dimensions and a minimal-adapter ADR before accepting #3. #21 remains blocked. This partial receipt does not select a production installer, support matrix or runtime architecture.
