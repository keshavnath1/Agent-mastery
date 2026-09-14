---
description: Legacy-compatible Stage 1 command that runs the current trace skill when durable state authorizes tracing.
argument-hint: "[optional module-id or source scope]"
---
Read `AGENTS.md`, `config/workflow.yaml`, and the latest run-state JSON. Refuse if `trace` is not the next permitted skill. Invoke `orchestrate` and then only `trace`. Require `.github/skills/trace/references/sas-trace-contract.md`, validate against `.github/skills/trace/schemas/execution_trace.schema.json`, write the canonical `stage1_extraction/output/execution_trace.json`, record its path and hash in run state, and stop. Do not invoke `map` automatically and do not generate an extraction script.
