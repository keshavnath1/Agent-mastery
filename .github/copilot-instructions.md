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

`config/tieout.yaml` begins as an unapproved template. When the user requests local parity, `interview` must present `GOVERNED_SAMPLE_50`, `FULL_POPULATION`, `PHASED_50_THEN_FULL`, and `CUSTOM_GOVERNED_SAMPLE`, explain evidence/runtime trade-offs, recommend without selecting, and stop for human choice. `specify` must preserve that choice, current phase, record count, selection policy, full-population follow-up obligation, source, rationale, and approver in a schema-valid draft containing the module's keys; frozen intake and SAS-oracle hashes and representation; deterministic fixture and coverage policy; expected and actual columns; comparison modes and human decision rationale; producer command; privacy controls; and proof boundary. `generate` must implement a repeatable, oracle-isolated producer. `test` must create and hash the deterministic selector, governed sources/inputs, fixture manifest, coverage assertions, selected-key digest, and oracle; pressure-test the generic comparator; and stop for approval of the exact contract. `validate` must allocate an append-only attempt ID and invoke `python3 scripts/project.py tieout --run-id <run-id> --attempt-id <attempt-id>` internally and cannot report local parity PASS without schema-valid `tieout_result.json`, generated `tieout_summary.md`, and `evidence.json`. Failed/retried evidence is append-only; `review` must independently rerun it, and `release` must derive its scoreboard and limitations from reviewed evidence. A `PHASED_50_THEN_FULL` sample PASS keeps the full-population gate open and cannot authorize a full-population claim. Never copy the LC-LOGIT-01 example's values into a new module unless the human independently approves them for that module.

Always state what evidence does and does not prove. Local semantic evidence is not automatically full-population, selected-runtime, distributed, cluster, performance, scalability, or production evidence.
