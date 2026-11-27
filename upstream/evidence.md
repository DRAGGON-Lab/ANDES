# A1.2 evidence and acceptance packet

Task: #2, source inventory/provenance, attempt 2026-11-27. User authorized the staged plan and independent agent review. HEAD is `5b838b1c87db01330d1eef1f6fa2bd93c5340178`; initial checkout clean. Candidate consists only of new `upstream/` files; no commit, release, issue change or upstream import. Human accepted this audit in chat on 27 November 2026 ("I accept this"). Acceptance covers the audit and its stated limitations, not upstream copying or release.

## Observed checks

- Source method: connected GitHub GET of each pinned commit/tree and 19 raw files. `observations.json` identifies raw URLs and Git blob fingerprints; `inventory.json` identifies six complete source tree requests. No upstream scripts executed. Coverage is tree-level enumeration plus selected-body review, not a complete legal/dependency audit of all enumerated components.
- `python3 upstream/check_inventory.py`: pass on 2026-11-27 at 16:29:07 UTC. Six pinned sources and ten selected component records internally consistent. Initial run failed because the inventory's license-file list omitted the Isambard `LICENSES/` contents; repaired the metadata and reran successfully.
- Observation metadata check: pass; all 19 records have immutable revision/blob identities and observed reads. An initial ad hoc assertion incorrectly expected 21 reads; counting the request list established 19 and the corrected assertion passed. No missing read is concealed by that correction.
- Whitespace checks: `git diff --no-index --check /dev/null upstream/README.md` and the corresponding commands for `inventory.json`, `check_inventory.py`, and `observations.json` emitted no diagnostics. Exit 1 represents new-file differences. Plain `git diff --check` also passed but does not cover these untracked files.
- Local environment: macOS 27.2.1 arm64; Python 3.9.6 (system interpreter). The inventory checker uses only the standard library; the planned Python 3.12/uv/JSON Schema stack has not been introduced under this documentation task.

Candidate SHA-256 fingerprints, before adding this packet:

| File | SHA-256 |
|---|---|
| README.md | `96b1034c84c81a63ed56c638fc32f58859ca0416dedcf36a741c1419f6092f3a` |
| inventory.json | `15a4771ad803347c6fcdd4180b3b7536b13dba5216bf6a9d620af3de4dbd0667` |
| check_inventory.py | `a65a884fbaefc5d1ca69f703c107ad250bf13c8ec60efba677632346d78a1db5` |
| observations.json | `e97480aadd30be4fb653dcd3272f6573519a85a616ba816fa163d7c1253c324c` |

## Quality dimensions

| Dimension | Status | Rationale |
|---|---|---|
| Functional correctness | partial | Inventory consistency passes; no ANDES runtime feature is implemented. |
| Engineering quality | pass | Independent agent found no blocking defect; checker reproduced at the fingerprints above. |
| Mathematical correctness | not_applicable | No mathematical result produced. |
| Scientific validity | not_applicable | No empirical/scientific effectiveness claim made. |
| Reproducibility | partial | Reviewer reproduced local check, ten component reads, Isambard annotations and pstack tree; did not independently refetch all six trees. |
| Human understanding | not_run | Maintainer has not yet reviewed/explained or accepted the candidate. |

## Acceptance and next action

Independent review: `/root/audit_review` reported no blocking defect at the four fingerprints above. The reviewer reproduced the checker using Python 3.9.6, independently fetched all ten immutable component bodies plus Isambard `REUSE.toml`, and checked pstack's complete tree, blob identities and component license location. No copied instruction bodies, private content or authority expansion was found. The reviewer required this evidence packet, now present. The JSON's `reviewer_disposition` fields preserve the initial pending state; this packet supersedes that state for the inventory review only, not future import clearance.

Review limitations: no recursive dependency clearance, no independent refetch of all six trees, no legal clearance. The checker uses Python assertions: run the documented command without optimization (`-O` or `PYTHONOPTIMIZE`). Maintainer/IP acceptance remains pending. All component imports remain blocked pending review of the exact proposed adaptation; proprietary content is reference only. Readable inventory completeness is separate from clearance to copy or release.

The acceptance above supersedes the pending maintainer-acceptance statements in this historical packet. Human understanding beyond review/acceptance was not assessed. Next: #16 may now begin from this accepted inventory. Issue #3 remains a separately authorized discovery task. Epic #4 and child issues remain open in GitHub; no merged or released state is claimed.
