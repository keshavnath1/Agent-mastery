---
description: Continue the active module by invoking exactly one skill authorized by durable run state.
argument-hint: "[optional module-id]"
---
Read `AGENTS.md`, `.github/copilot-instructions.md`, `config/workflow.yaml`, and the newest run-state JSON. Verify the previous required artifact and gate result. Invoke `orchestrate`, then exactly one next permitted skill. The skill may invoke approved deterministic tools internally; never ask the user to run them manually. Stop after writing and verifying the skill's named artifact. Do not cross a human gate. End with the standard Stage Result block defined in `docs/runbooks/STAGE_CONTRACT.md`.
