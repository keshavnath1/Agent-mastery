---
description: Start, resume, or restart a migration module through durable state and one bounded skill at a time.
argument-hint: "[new|resume|restart] [module-id]"
---
Read `AGENTS.md`, `.github/copilot-instructions.md`, and `config/workflow.yaml`. Determine whether the explicit user intent is `new`, `resume`, or `restart`. For `restart`, invoke `orchestrate` and then only `restart`; produce a reset plan and stop before mutation. For `new`, create or propose the intake-ready run according to the workflow contract. For `resume`, read the newest run-state JSON and report the next permitted skill. Never execute more than one skill or cross a human gate in this response.
