# Copilot Instructions

Follow root `AGENTS.md` and `config/workflow.yaml` as the authoritative repository contracts.

This is a clean template. Files under `examples/` are teaching material only. They are never approved requirements, expected outputs, tolerances, runtime choices, or evidence for a new module.

For every user-facing prompt:

1. Read the latest durable run state; if no run exists, recognize clean-template state.
2. Invoke `orchestrate`.
3. Select exactly one workflow-authorized specialist skill.
4. Let that skill invoke approved deterministic tools internally.
5. Require its named canonical output and `PASS`, `FAIL`, or `BLOCKED` evidence.
6. Record the result in durable state when a run exists.
7. Stop after one skill and at every human gate.
8. End with the complete Stage Result from `docs/runbooks/STAGE_CONTRACT.md`, including `Next action` and an exact `Copy/paste next` message derived from durable state.
9. Use actual artifact paths and SHA-256 values in approval text. If a required hash is missing, request it without advancing; never invent it.

Do not ask the user to run helper scripts as the normal lifecycle interface. Do not duplicate specialist procedures in prompts. Do not infer business intent from source code, cross a human gate, approve your own work, or change expected evidence, keys, tolerances, evaluators, protected source files, or locked patterns to make a gate pass.

Create the semantic implementation only after approved requirements, specification, ADRs, trace, mapping, and semantic IR exist. Prefer a backend-neutral Python core when the approved ADR selects it, and keep selected-runtime adapters thin. Imported patterns may inform implementation but never override the approved PRD, module SPEC, or target ADR.

Canonical compatibility artifacts are:

```text
trace → stage1_extraction/output/execution_trace.json
map   → policy/policy_registry.yaml
```

Reference them by canonical path and hash; do not maintain competing editable copies.

`config/tieout.yaml` begins as an unapproved template. The owning requirements process must define and obtain human approval for the actual module's keys, metrics, fixtures, expected outputs, tolerances, and proof boundary. Never copy the LC-LOGIT-01 example's values into a new module unless the human independently approves them for that module.

Always state what evidence does and does not prove. Local semantic evidence is not automatically full-population, selected-runtime, distributed, cluster, performance, scalability, or production evidence.
