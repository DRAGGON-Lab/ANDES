# Repository protection decision — proposed, unapplied

Prepared for the foundation closeout of **Agentic Norms for Disciplined Engineering and Science**. This is an administrative recommendation, not approval to change settings. Foundation acceptance and operational CI do not mean merge protection is active.

## Read-only observations

At the [28 November 2026 snapshot](evidence/foundation-settings-observed.json), main was `0f28ee50709354b255e39b325a37b8ce33ccc219` with protected=false. The ruleset list including parents was empty. Foundation checks succeeded from GitHub Actions (app ID 15368). No required-check enforcement was observed.

The integration received 403, Resource not accessible by integration, from the detailed branch-protection endpoint. This is an access limit, not proof that a particular setting is absent or that the maintainer lacks administrative rights. An authorized administrator must inspect effective rules and permissions before applying a proposal. No settings were changed by this closeout.

## Recommended normal configuration

Use a repository branch ruleset named foundation-main targeting only refs/heads/main. Prepare it disabled; activate only after separate explicit human authorization of the exact settings and bypass policy. Confirm GitHub plan/role capabilities and any inherited rules first.

| Control | Proposed value |
|---|---|
| Integration path | Changes enter main through a pull request; no routine direct pushes. |
| Required check | Foundation checks, with expected source GitHub Actions/app ID 15368; verify the actual check identity before selection. |
| Freshness | Require checks against an up-to-date main base; job names remain unique across workflows. |
| Human review | One eligible human approval, independent of author and latest pusher; dismiss stale approvals and require approval after the latest reviewable push. |
| Conversations | Resolve review conversations before merge. |
| History restrictions | Block force pushes and branch deletion. |
| Normal bypass | Empty bypass list, including no routine maintainer/admin/app exemption. Do not grant a broad bypass merely to satisfy a review requirement. |
| Existing workflow authority | Keep contents-read job permissions, nonpersisted checkout credentials and restricted release credentials. No deployment/release authority is added. |

Do not add merge queues, deployment gates or signing requirements as an implicit part of this proposal. Required checks cannot replace independent review: a PR can edit the workflow and its tests. Candidate changes to check identity or suppression policy need review, not an automatic settings update.

## Sole-maintainer decision

GitHub does not count an author's own approval. An agent using the maintainer's GitHub identity does not create an independent human reviewer. Before activating the normal review rule, confirm a second eligible human can review and an authorized administrator can recover access.

If only one human is available, stop activation and obtain a separate decision: appoint a reviewer through an authorized access change, defer the review rule, or approve a bounded review-only exception. Do not silently set the approval count to zero or substitute automated approval.

Any exception must identify the PR, reason, accountable human, independent critique, expiry and restoration owner. Retain pull requests, passing checks, resolved conversations and force/deletion restrictions; do not use a broad ruleset bypass that also waives CI. An administrative edit limited to review requirements needs its own approval and recorded before/after state. This document does not authorize such an edit or weaken the Constitution's L2 review/acceptance requirements.

## Application validation and rollback

For a later separately authorized administrative task:

1. Export/snapshot all existing applicable rules, IDs, enforcement/bypass settings and main SHA into the authorized administrative record. Re-read effective rules; today's empty-list observation is not a future rollback snapshot.
2. Obtain human approval of the exact proposed delta, sole-maintainer choice, validation plan and rollback owner. Stage the new ruleset disabled and inspect its target/check identity before activation.
3. After approved activation, verify effective settings and representative PR behavior: absent review, unresolved conversations and failing/missing checks block merge; a reviewed, current, passing PR can proceed. Test force/deletion behavior only with separately authorized disposable branches/rules, never destructively against main.
4. If enforcement blocks legitimate work or behaves unexpectedly, stop merges and preserve the failing PR/check evidence. Prefer a narrowly approved repair to check identity or review settings.
5. If rollback is explicitly authorized, restore the saved prior configuration. Disable only the newly introduced ruleset when the prior state had no such ruleset; preserve unrelated/inherited rules. Restore modified pre-existing fields from their snapshot. Disabling rather than deleting preserves the new ruleset for inspection.
6. Re-read rules and inspect the merge UI after restoration; record actor, UTC time, exact delta, reason and resulting protection gaps. If baseline protection was absent, rollback returns to that weaker state—it is not evidence of a protected repository. Re-enable only after a new approved correction and verification.

No rollback command is executed here. Administrative recovery access and rights must be confirmed by the maintainer, not inferred from this integration's read access.

## Primary references

Consulted 28 November 2026: GitHub's [branch protection behavior](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), [ruleset management and reversible disabling](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/managing-rulesets-for-a-repository), and [eligible reviews/self-approval limits](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews). These describe available mechanisms; they do not establish ANDES's effective settings or grant authority.
