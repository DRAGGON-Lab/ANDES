# Resume with a revision mismatch

Example: a handoff reports passing tests at revision A, but the checkout is revision B. Preserve the historical result for A; do not label B as tested. Inspect which relevant files and inputs changed, identify the smallest check that can establish the current claim, and report not_run until it actually executes. If execution needs missing authority, leave that specific gate explicit.

This is an illustrative procedure, not a task/evidence wire schema or permission grant.
