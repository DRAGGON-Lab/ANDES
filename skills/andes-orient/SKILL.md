---
name: andes-orient
description: Establish repository identity, accepted task and evidence freshness when starting or resuming repository work with missing context.
---

# Orient to the current task

Recover enough verified context to choose the next permitted action.

Inspect repository identity, exact revision, dirty state and applicable instructions. Find the accepted task, its dependencies and the most recent authorized handoff. Treat the handoff as a claim: check its artifact/revision before reusing a passing result.

Report the objective and acceptance criteria, relevant permissions and protected inputs, unresolved blockers, and the next action on the satisfied dependency frontier. Preserve unrelated edits. Retrieve only relevant project records; private histories are not an orientation source by default.

When a resumed handoff names a different revision, consult [the revision mismatch example](references/revision-mismatch.md). Otherwise leave it unloaded.

If the task and current evidence are already clear, continue the requested work without repeating orientation or opening a new approval flow.
