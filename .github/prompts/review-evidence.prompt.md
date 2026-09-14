---
description: Independently review a completed stage or repair through durable state and a fresh checker context.
argument-hint: "[module-id or artifact path]"
---
Read `AGENTS.md`, `.github/copilot-instructions.md`, `config/workflow.yaml`, and the latest run state. Invoke `orchestrate`; refuse unless `review` is the next permitted skill. Then invoke only `review` in fresh checker context, re-run the recorded deterministic verification, verify protected artifacts did not change, write the named review artifact, update durable state, and stop. Do not repair, approve, merge, release, or invoke another specialist skill in this response.
