---
description: Restart an existing migration module from raw source intake while preserving history and prior evidence.
argument-hint: "[module-id]"
---
Read `AGENTS.md`, `config/workflow.yaml`, and the latest run state. Invoke `orchestrate` in restart mode and then only the `restart` skill. Produce and validate `artifacts/restarts/<restart-id>/reset_plan.yaml`; show exact classifications and proposed moves; stop for human approval before changing files or run state. Never execute intake or a downstream migration skill in this response.
