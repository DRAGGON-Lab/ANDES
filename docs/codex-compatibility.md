# Codex compatibility spike — A2.1

Accepted A2.1 spike, merged in [PR #72](https://github.com/DRAGGON-Lab/ANDES/pull/72); [issue #3](https://github.com/DRAGGON-Lab/ANDES/issues/3) is closed. The current source foundation is reviewed main `0f28ee50709354b255e39b325a37b8ce33ccc219`. The discovery observations below retain their original baseline `1c77c37`, recorded versions and inputs; later A1.5 explicit-loading evidence is identified separately. See [closeout](evidence/foundation-closeout.md). This is not installation/release or administrative authority.

The spike received independent architect review and maintainer acceptance under L2 rigour. Scope: native discovery/metadata, instruction precedence, role/packaging investigation, synthetic coexistence, minimal-adapter alternatives and reproducible evidence. Non-goals: production installer, release resolver, mission runtime, live-account changes and paid execution. Acceptance is unchanged from #3: recorded official sources/runtime, executable discovery/precedence where available, explicit role/packaging status, matrix and reviewed adapter ADR, preserved personal state and sufficient A2.2 scoping.

## Observations and limits

Observed environment: macOS 27.2.1 arm64, Codex CLI 0.172.0, Python 3.12.16. Binary and probe hashes, timestamp and normalized output are recorded in `docs/evidence/a2-1-result.json`; the complete candidate is fingerprinted in the companion manifest. Other CLI versions, IDE/cloud surfaces, Linux and Windows are not tested.

| Capability | Observation | Status / boundary |
|---|---|---|
| Repository skill discovery | Synthetic `.agents/skills/<name>/SKILL.md` found through `skills/list`. | pass in this environment |
| User skill discovery | Synthetic user-home skill found alongside project skill. | pass in this isolated home |
| Minimal metadata | Name, exact description and SKILL.md filename returned. | pass; richer metadata not tested |
| Native instruction precedence | `thread/start` returned global → project → nested AGENTS.override.md sources, omitting sibling AGENTS.md. | pass for source selection/order; model obedience not evaluated |
| Role definition format | Strict config accepted `[agents.fixture_reviewer]`, description and config_file reference; `config/read` returned the declaration. | partial; role file execution/instructions and spawning not tested |
| Native packaging commands | Installed CLI help exposes plugin add/list/remove and marketplace commands. | command presence observed; all installation/distribution behavior not_run |
| Project/user coexistence | Both distinct synthetic skills found; synthetic user skill and config file hashes unchanged. | pass for this case; name collisions and arbitrary personal configurations not tested |
| Native profile composition | Catalog composition checks exist separately under A1.3. | not_run natively; no equivalence inferred |
| Explicit skill input assembly / selective loading | The later A1.5 capture observed the selected body and Constitution, with other full bodies/reference absent. | verified request boundary only; see [core fixture](core-fixture.md) |
| Workflow selection | A1.5 independently exercised one agent's workflow choice and task review in its host. | bounded fixture; not CLI implicit matching |
| Native implicit routing, inference and relative-reference following | Not evaluated by either accepted fixture. | not_run; not supported foundation claims |
| Real-account preservation | Sanitized child environment, temporary state, ephemeral credential storage and OS-denied real-home/keychain access. | controls pass; no live account migration or configuration used |

The role/packaging not_run results are explicit findings allowed by #3's discovery contract, not claims of unsupported native functionality. The observed role is the config_file declaration, not standalone-agent discovery or role-file validation. Current documentation also describes standalone agent TOML files requiring name, description and developer_instructions, with permissions inherited from the parent. The synthetic referenced file follows that documented shape; no role-local sandbox enforcement is assumed. Standalone discovery and execution still need separate probes. The observed minimum supports a project-local candidate fixture; production distribution and autonomy remain unverified.

## Reproduction and isolation

For optional reproduction after `uv sync --locked`, run `.venv/bin/python probes/codex_discovery.py` on the recorded macOS setup. This closeout does not rerun the probe or establish a production support matrix. The script uses the installed executable, no downloads. Nested sandbox launch may require approval outside the surrounding execution sandbox; it never drops its own narrower macOS policy. The checkout must be under the actual user-home tree because its public README is the harmless denied-read control; otherwise fail-closed behavior is expected, not a portability pass.

The probe creates a fresh temporary Git project, synthetic home/state and two skills, instruction markers and a role declaration. The child receives only explicitly constructed environment values; parent environment is untouched. Native executable-directory reads are permitted; other real-home reads, keychain access, administrator skill roots and external writes are denied. Network is denied. Controls require successful sandbox launch followed by OS-denied real-home read, outside-fixture write and loopback bind before native initialization.

The discovery probe uses only initialize, initialized, skills/list, config/read and thread/start. Starting its temporary read-only thread observes instruction sources; it requests no user turn, model inference, model-initiated tool execution or role spawn. The separate A1.5 loading probe does call turn/start, but only against an isolated loopback capture configured for an error response without inference. Native state and stderr capture stay in the temporary fixture and are removed after termination. Raw native logs and personal records are not published.

Existing unit/fixture checks do not exercise this native probe. Native validation is the separate executable observation with synthetic negative isolation controls. It must be rerun after relevant probe/runtime changes; ordinary Linux CI does not certify macOS compatibility.

## Minimal adapter and next contract

Accepted [ADR-004](decisions/ADR-004.md) governs the implemented candidate projection: use canonical runtime-neutral content with a thin project-local skill projection in an isolated candidate fixture first. Keep native paths/metadata in the adapter, preserve the existing Constitution and personal configuration, and defer marketplace/global installation until tested. A1.5 subsequently satisfied its bounded agent-selection and native explicit-assembly fixture; the remaining unverified model/installation behaviors are not implied by either acceptance.

A2.2 remains separate planned work for local immutable release/profile resolution against accepted A1.3 IDs and provenance, while recording this exact native environment. Its contract must address managed file ownership, collision handling, checksums and unsupported environments; it must not infer update/rollback safety or generic role support from this spike.

## Sources and integrity

Official pages consulted through the current manual cache fetched on 27 November 2026: [Build skills](https://learn.chatgpt.com/docs/build-skills.md), [AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md), [App Server](https://learn.chatgpt.com/docs/app-server.md), [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md), and [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference). Installed `codex --version`, `codex app-server --help` and `codex plugin --help` supplied runtime evidence. Documentation guided the tests; actual results establish observed behavior.

No upstream instruction bodies, private histories, real credentials, third-party skills or account configuration were copied. Synthetic probe text is original. Evidence and six separate quality statuses are in `docs/evidence/a2-1.md`. Subsequent human acceptance and closure are linked in [closeout](evidence/foundation-closeout.md); historical pending statements remain dated attempt records. No acceptance substitutes for the unverified native/production behaviors listed above.
