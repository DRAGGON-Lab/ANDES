# Minimal core and candidate routing fixture — A1.5

Accepted A1.5 implementation, merged in [PR #73](https://github.com/DRAGGON-Lab/ANDES/pull/73); [issue #21](https://github.com/DRAGGON-Lab/ANDES/issues/21) and epic #4 are closed at reviewed main `0f28ee50709354b255e39b325a37b8ce33ccc219`. Historical native/forward checks used their recorded candidate inputs and environments, including baseline `1c77c37`; this guide does not redate those observations. The accepted bounded criteria and limits are reconciled in [foundation closeout](evidence/foundation-closeout.md).

## Core and boundary

`catalog/core.json` uses the accepted catalog contract for the Constitution, routing pointers and four focused workflows: andes-orient, andes-contract, andes-verify and andes-handoff. The instructions are original ANDES text derived from its approved policy; no third-party skill bodies were imported. All six components are mandatory catalog selections, which does not mean every skill body enters context. Component version 0.1.0 identifies the source core; the projection remains a candidate test fixture, not an installable release.

The router points to one workflow for the current need; explicit invocation bypasses routing while retaining policy and permissions. There is no new orchestration service, general classifier, installer, global configuration or domain profile.

`adapters/codex/candidate.py` validates the core and projects only into an empty temporary project outside the source checkout. It preserves source bytes in four native skill folders and their resources, and creates a temporary AGENTS instruction chain from the canonical Constitution and router. A projection manifest records source/destination/hash. No personal installation is performed. Native invocation uses the path returned by discovery, rejects duplicate names and rejects paths outside that projection.

## Behavioral checks

1. **Independent workflow selection and task execution.** An evaluating agent received only the synthetic request, raw candidate/evidence and discovery metadata in an isolated workspace. It was not given the expected workflow or answer. It selected andes-verify, inspected that body, invoked the native candidate adapter with the selected name, and reproduced a failing test despite the completion note claiming all tests passed. It left source/acceptance unchanged and reported separate quality dimensions. This exercises a real agent's workflow choice; it is not a statistical reliability claim.
2. **Native explicit invocation and progressive loading.** The selected skill is supplied to an actual Codex CLI 0.172.0 app-server through turn/start's skill input item. A loopback-only capture observes the actual provider request: selected full body and Constitution present; other three full bodies and the unneeded orientation reference absent. The capture is configured to return HTTP 400 deliberately, without inference; receipt of that response is not an assertion. This establishes host-side invocation/request assembly, not CLI implicit matching, model obedience or a completed CLI model turn.
3. **Local structural/regression checks.** Twenty-five tests cover existing contracts/checks plus four target selections, frontmatter/catalog agreement, temporary projection/content preservation, ambiguity and path rejection. All four skills passed the skill-creator quick validator. The core catalog passes the same CLI used in CI.

The independent task execution and native loading checks are complementary. The task is executed by the current agent host; the sandboxed CLI proves the selected instructions reach its model-input boundary. No claim is made that the sandboxed CLI itself chose the skill implicitly or reasoned over the task. Those broader behaviors are not enabled or certified here.

## Reproduction

First run `uv sync --locked` in the source checkout. The first two commands are local checks. The last two are optional manual fixture reproductions on the recorded macOS environment, requiring their own current authorization; they are not installation or successful-inference commands. This documentation closeout does not rerun them.

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_catalog.py catalog/core.json --root .
.venv/bin/python probes/prepare_core_case.py
.venv/bin/python probes/core_loading.py --skill andes-verify
```

The preparation command prints a disposable workspace. Give an independent agent its AGENTS.md, brief.txt and candidate-skills.json, permit read-only inspection/local stdlib tests and the named native loading probe, and request a report. Do not provide the intended skill or result. The normalization code is deliberately defective synthetic evaluation input, not an ANDES implementation. Its test failure is the expected evidence the verification workflow should expose.

The native probe requires the tested macOS environment and may need approval to launch its own sandbox and loopback listener. The Codex child receives a sanitized environment and ephemeral state; the OS policy denies real-home/keychain reads, outside-fixture writes and network except the capture's single localhost port. A successful sandbox launch and denied-read/write/bind/other-port controls must pass before native startup. The capture performs no inference, forwards nothing and rejects unexpected authorization headers. It retains only presence/control summaries, not raw request bodies. Native stderr capture is inside the temporary fixture; state is removed after termination.

The native probe is separate from ordinary Linux CI. Its intentional provider error is not a successful model completion. Relative resource files are preserved under the selected skill directory; the tested verification case does not need the orientation example, and automatic/model-mediated following of that link is not established.

## Evidence and acceptance

The normalized forward report, real failing-test output and boundary-case results are in `docs/evidence/a1-5-forward*`. Input fingerprints and unchanged-input assertions tie the result to the synthetic case. Only the verification skill body was reported read; native request inspection separately establishes absence of the other bodies/reference at the captured input boundary.

The [historical acceptance packet](evidence/a1-5.md) and its original manifest preserve the independent review and exact candidate identities, including the distinction between routing in the agent host and loading in the CLI. Subsequent human acceptance, merges, hosted CI and closure are linked in [foundation closeout](evidence/foundation-closeout.md). They do not establish installation, administrative protection or release readiness.
