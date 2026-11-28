# Foundation evidence index

Start with the [current foundation reconciliation](foundation-closeout.md). A1 and prerequisite A2.1 are accepted/closed at reviewed main `0f28ee50709354b255e39b325a37b8ce33ccc219`. This index points to subsequent acceptance rather than rewriting earlier observations.

## Dated receipts and supersession

| Historical record | What remains historical | Subsequent acceptance/current status |
|---|---|---|
| [A1.2 inventory receipt](../../upstream/evidence.md) | Source reads, selected-path audit, failed/corrected checks, original fingerprints and import restrictions. | [#2 closed](https://github.com/DRAGGON-Lab/ANDES/issues/2), [PR #68 merged](https://github.com/DRAGGON-Lab/ANDES/pull/68); inventory acceptance does not clear imports. |
| [A1.3 catalog receipt](a1-3.md) | Its 12/14-test attempts, input revisions, repairs and original manifest. | [#16 closed](https://github.com/DRAGGON-Lab/ANDES/issues/16), [PR #69 merged](https://github.com/DRAGGON-Lab/ANDES/pull/69); later total of 25 tests belongs to the later foundation revision. |
| [A1.4 development receipt](a1-4.md) and [old settings snapshot](a1-4-settings-observed.json) | Local runs, redaction repair, pre-publication not_run statements and old settings read. | [#18 closed](https://github.com/DRAGGON-Lab/ANDES/issues/18), [PR #70 merged](https://github.com/DRAGGON-Lab/ANDES/pull/70); later hosted result and fresh settings snapshot are in the reconciliation. Protection remains unapplied. |
| [A2.1 initial discovery](a2-1-discovery.md) and [extended receipt](a2-1.md) | Limited first matrix, actual native versions/results, earlier source-byte omission and recorded script identities. | [#3 closed](https://github.com/DRAGGON-Lab/ANDES/issues/3), [PR #72 merged](https://github.com/DRAGGON-Lab/ANDES/pull/72), ADR-004 approved. A1.5 supplies later explicit-loading evidence; it does not change what the discovery probe did. |
| [A1.5 receipt](a1-5.md), [native summary](a1-5-native.json) and [forward report](a1-5-forward.json) | The bounded selection/loading fixture, synthetic failures, corrected status label and exact source/attempt hashes. | [#21 closed](https://github.com/DRAGGON-Lab/ANDES/issues/21), [PR #73 merged](https://github.com/DRAGGON-Lab/ANDES/pull/73); [epic #4 acceptance](https://github.com/DRAGGON-Lab/ANDES/issues/4) confirms the scoped gate. |

Pending-acceptance/publication/hosted-run statements inside these old records refer to those attempts. The [later reconciliation](foundation-closeout.md) supersedes those lifecycle statements, not the original commands, timestamps, omissions, failures or input identities. Acceptance does not establish an unperformed human-understanding assessment or any unsupported native capability.

## Manifests

The original a1-3, a1-4, a2-1 and a1-5 manifests are preserved unchanged. They fingerprint their reviewed candidates, not every later checkout. Later naming, tooling and documentation changes can legitimately differ; use the original receipt/revision to interpret a mismatch. Never regenerate an old manifest to make a later tree appear to be the original input.

The new [preservation inventory](foundation-preserved.sha256) fingerprints all 16 pre-existing evidence files at the reviewed main, including upstream/evidence.md. The closeout's own manifest and check receipt are separate current artifacts. No earlier evidence or failed attempt was rewritten for this documentation update.
