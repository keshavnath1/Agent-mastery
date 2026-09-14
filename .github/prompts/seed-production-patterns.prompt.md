---
description: Harvest one or more approved production workspaces into sealed candidate pattern bundles without importing them.
argument-hint: "[source workspace paths or bundle scope]"
---
Read `AGENTS.md`, the approved target PRD/SPEC/ADRs, `config/workflow.yaml`, and the latest run state. Invoke `orchestrate` and then only `harvest`. Treat every source workspace as read-only; require pinned commits, source ADRs, code, tests, provenance, applicability, counterexamples, and measured evidence for performance claims. Produce sealed candidate bundles and stop for independent review. Do not import, generate, or change target implementation in this response.
