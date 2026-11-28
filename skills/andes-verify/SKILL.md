---
name: andes-verify
description: Check a change or completion claim against acceptance criteria and observed evidence, including failed, stale and missing checks.
---

# Verify against acceptance evidence

Compare the candidate and its actual evidence with the accepted outcome.

Identify the exact candidate revision/dirty state, acceptance criteria, relevant inputs and environment. Inspect the recorded command, exit status and artifact rather than trusting a completion summary. Reproduce the smallest relevant check when authorized and practical. An unexpected failure remains a failure; a check on a different revision is stale evidence.

Report functional correctness, engineering quality, mathematical correctness, scientific validity, reproducibility and human understanding separately. Use pass, fail, partial, not_run or not_applicable with an evidence pointer and rationale. Do not average the dimensions or infer scientific validity from software tests.

Preserve negative results and omissions, including a missing tool or unavailable environment. Name blocking findings, review requirements and the next permitted check. Do not turn a local pass, independent review or merge into release or target-environment acceptance. Recommend completion only when the accepted criteria are met.
