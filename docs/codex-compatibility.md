# Codex compatibility spike — A2.1

Review candidate for issue #3. Baseline `1c77c37dd03dbdb24d17dee8ead1955573798e90` includes the human-merged audit, catalog and CI PRs #68–#70. Main's [hosted foundation run](https://github.com/DRAGGON-Lab/ANDES/actions/runs/46052068780) passed. This report is a capability spike, not an installation/release claim or permission change.

Owner: platform engineer; independent architect reviews the exact candidate; rigour L2, Delegate mode. Scope: native discovery/metadata, instruction precedence, role/packaging investigation, synthetic coexistence, minimal-adapter alternatives and reproducible evidence. Non-goals: production installer, release resolver, mission runtime, live-account changes and paid execution. Acceptance is unchanged from #3: recorded official sources/runtime, executable discovery/precedence where available, explicit role/packaging status, matrix and reviewed adapter ADR, preserved personal state and sufficient A2.2 scoping.

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
| Explicit invocation, routing, selective loading | No turn/start request was sent. | not_run; still required by A1.5 |
| Real-account preservation | Sanitized child environment, temporary state, ephemeral credential storage and OS-denied real-home/keychain access. | controls pass; no live account migration or configuration used |

The role/packaging not_run results are explicit findings allowed by #3's discovery contract, not claims of unsupported native functionality. The observed role is the config_file declaration, not standalone-agent discovery or role-file validation. Current documentation also describes standalone agent TOML files requiring name, description and developer_instructions, with permissions inherited from the parent. The synthetic referenced file follows that documented shape; no role-local sandbox enforcement is assumed. Standalone discovery and execution still need separate probes. The observed minimum supports a project-local candidate fixture; production distribution and autonomy remain unverified.

## Reproduction and isolation

Run `.venv/bin/python probes/codex_discovery.py` on this supported macOS setup. The script uses the installed executable, no downloads. Nested sandbox launch may require approval outside the surrounding execution sandbox; it never drops its own narrower macOS policy. The checkout must be under the actual user-home tree because its public README is the harmless denied-read control; otherwise fail-closed behavior is expected, not a portability pass.

The probe creates a fresh temporary Git project, synthetic home/state and two skills, instruction markers and a role declaration. The child receives only explicitly constructed environment values; parent environment is untouched. Native executable-directory reads are permitted; other real-home reads, keychain access, administrator skill roots and external writes are denied. Network is denied. Controls require successful sandbox launch followed by OS-denied real-home read, outside-fixture write and loopback bind before native initialization.

Only initialize, initialized, skills/list, config/read and thread/start are used. Starting a temporary read-only thread observes instruction sources; no user turn, model inference, tool execution or role spawn is requested. Native state and stderr capture stay in the temporary fixture and are removed after termination. Raw native logs and personal records are not published.

Existing unit/fixture checks do not exercise this native probe. Native validation is the separate executable observation with synthetic negative isolation controls. It must be rerun after relevant probe/runtime changes; ordinary Linux CI does not certify macOS compatibility.

## Minimal adapter and next contract

See proposed [ADR-004](decisions/ADR-004.md): use canonical runtime-neutral content with a thin project-local skill projection in an isolated candidate fixture first. Keep native paths/metadata in the adapter, preserve the existing Constitution and personal configuration, and defer marketplace/global installation until tested. A1.5 must still establish explicit invocation, correct routing and selective loading before acceptance.

A2.2 can now scope local immutable release/profile resolution against accepted A1.3 IDs and provenance, while recording this exact native environment. Its contract must address managed file ownership, collision handling, checksums and unsupported environments; it must not infer update/rollback safety or generic role support from this spike.

## Sources and integrity

Official pages consulted through the current manual cache fetched on 27 November 2026: [Build skills](https://learn.chatgpt.com/docs/build-skills.md), [AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md.md), [App Server](https://learn.chatgpt.com/docs/app-server.md), [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md), and [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference). Installed `codex --version`, `codex app-server --help` and `codex plugin --help` supplied runtime evidence. Documentation guided the tests; actual results establish observed behavior.

No upstream instruction bodies, private histories, real credentials, third-party skills or account configuration were copied. Synthetic probe text is original. Evidence and six separate quality statuses are in `docs/evidence/a2-1.md`. Human acceptance and independent review remain separate gates; accepting a compatibility report cannot substitute for A1.5's missing native behavior checks.
