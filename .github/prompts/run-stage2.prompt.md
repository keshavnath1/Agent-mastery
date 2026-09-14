---
description: Legacy-compatible Stage 2 command that runs the current map skill when durable state authorizes mapping.
argument-hint: "[optional module-id]"
---
Read `AGENTS.md`, `config/workflow.yaml`, the approved module SPEC and ADRs, and the latest run-state JSON. Refuse if `map` is not the next permitted skill. Invoke `orchestrate` and then only `map`. Consume the approved canonical `stage1_extraction/output/execution_trace.json`, load the applicable pattern catalog, validate against `.github/skills/map/schemas/policy_registry.schema.json`, write the canonical `policy/policy_registry.yaml`, record its path and hash in run state, and stop. Do not invoke `model` automatically.
