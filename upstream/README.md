# A1.2 upstream inventory

Review candidate for [issue #2](https://github.com/DRAGGON-Lab/ANDES/issues/2), part of epic #4. Baseline: `5b838b1c87db01330d1eef1f6fa2bd93c5340178`; observed 27 November 2026. No upstream instructions, scripts, evaluation inputs or configuration are imported. The JSON contains public path metadata and original audit judgments, not an installable catalog or a grant of reuse permission.

## Contract and method

Owner: source curator (implementation agent). Reviewer: separate independent agent; maintainer/IP reviewer resolves material rights uncertainty and accepts this task. Rigour L2, Delegate mode. Authorized writes are this `upstream/` report, inventory, checker and evidence. Acceptance remains the six criteria in issue #2: source revisions/access, selected component provenance, overlap/conflicts, blocked unclear imports, design mapping, and independent review. Human acceptance is pending.

The investigation has three units: enumerate all six source trees; compare capability families; inspect selected component bodies and applicable terms. GitHub GET requests retrieved immutable commit trees and raw files through the connected GitHub tool. All tree responses were non-truncated. `inventory.json` records source SHAs, tree URLs, complete in-scope skill paths/blob identities and ten individually examined candidates. Enumeration is not a claim that every skill body or its license has been audited. Component dependencies below are observed references or runtime assumptions, not a recursively cleared dependency closure.

## Capability inventory and recommendations

| Source | Families observed in path index / examined material | Foundation disposition |
|---|---|---|
| ECx | Coding/testing/review; research, writing, context/memory; roles and evaluator-related paths; multiple native skill representations | Conceptually adapt bounded verification only; defer runtime, memory and evaluator machinery. No personal configuration dependency. |
| ECC | Coding/testing/review; research/writing; context and tool integration; multiple runtime variants | Same engineering families as ECx. Select one canonical ANDES procedure rather than importing both. |
| pstack (`cursor/plugins/pstack/`) | Design, premise criticism, teaching, verification, evidence trails, arena, swarm and automation | Consider design/evidence ideas; defer topology, automation and arena. Other plugins in this monorepo are outside the requested source scope. |
| Matt Pocock skills | Engineering design, TDD, review, triage, research/spec/tickets; productivity/product work | Consider behavioral TDD and bounded planning; do not adopt tracker configuration or broad skill installation. |
| Dream-RSI | Exploration policies, replay worlds, evaluator-based policy selection | Defer to M6. README describes methodology, not independent evidence of effectiveness for ANDES. No benchmark assets, API calls or runtime installation. |
| Isambard skills | Login, scheduling, Python/modules, containers, GPU/distributed computing, storage/accounting, support and responsible-AI policy | Reference official guidance for later HPC work. No copying of proprietary policy; general skills require separate CC-BY-SA handling and component review. |

The immutable source links and exact revisions are in `inventory.json`. Its path index deliberately retains mirrors so coverage can be checked; mirrors are not separate ANDES capabilities. ECx declares ECC origin in examined skills. Similar names do not establish byte identity or prove which fork is preferable.

## Component rights and conflicts

Each selected component has an exact source/path/blob, license paths, attribution, dependencies, disposition, rationale and approved-design mapping in the JSON. Root terms were read for ECx, ECC, Matt Pocock and Dream-RSI; pstack's own `pstack/LICENSE` was read rather than assuming monorepo-wide terms. The complete trees were inspected for license/notice locations. The selected MIT skill paths have no closer license file in those trees. Root licenses do not establish rights for every other component or linked asset.

- **ECx/ECC verification:** both use an 80% coverage target and secret grep examples that can disclose matching values. ECx's build pipeline lacks the failure handling present in the examined ECC version. ANDES must preserve exit status, redact secret findings and use proportionate checks. These procedures are conceptual candidates, not drop-in commands.
- **TDD overlap:** ECx/ECC and Matt Pocock all cover behavioral tests. Universal coverage targets, automatic checkpoint commits, mandatory repeated seam approval and a blanket ban on refactoring during the loop are not ANDES defaults. Keep one focused canonical method based on the Constitution and project contract.
- **pstack evidence/design:** useful ideas overlap ANDES ADRs and handoffs. The evidence skill references scripts, other skills and transcript access, and demands cross-vendor review. None of those dependencies or private-record practices is adopted. Architecture references arena, which remains deferred.
- **Dream-RSI:** root Apache-2.0 terms do not cover the externally downloaded SimpleTES AGPL-3.0 tasks as MIT material. README identifies separately licensed KernelBench assets and external evaluators. No individual runtime component is proposed for core import, so deeper code/dependency/NOTICE clearance is deferred until a concrete import exists.
- **Isambard:** `LICENCE`, `REUSE.toml`, the responsible-AI skill frontmatter and `LICENSES/LicenseRef-ARR.txt` were inspected. General skill content is assigned CC-BY-SA-4.0, but the policy skill is explicitly overridden to all-rights-reserved. Its copying is blocked. The general skills are not cleared for MIT relicensing; attribution/share-alike and institutional requirements need review before any adaptation. Public access does not authorize remote cluster execution.

MIT candidates require preservation of the copyright and permission notices for substantial reuse. Apache candidates would require license and applicable notices plus modification notices. These are recorded obligations, not legal clearance or human acceptance. No source is approved for wholesale import, and no private ECx history or configuration was examined.

## Handoff to A1.3

Prefer original orient/contract/verify/handoff text grounded in ANDES's existing canonical documents. Reuse selected ideas only after reviewing the exact future text and dependency closure. Keep provenance and lifecycle eligibility explicit, separate inventory from the active catalog, deduplicate purpose before native representation, and reject compositions that override mandatory norms. Do not start #16 until this audit has independent review and maintainer acceptance. #3 is a separate eligible discovery task; #18 and #21 remain gated.

## Verification

Run `python3 upstream/check_inventory.py` for local consistency and exact candidate file fingerprints. This check is offline: it does not establish source rights or refetch remote evidence. Reproduce source observations with GET on the stored tree URLs and immutable component/license blob URLs; compare returned Git blob identities. No executable ANDES feature exists in this task, so failing-first product tests are not applicable. `evidence.md` records actual checks, review, quality dimensions and omissions.
