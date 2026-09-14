---
name: generate
description: Generate the backend-neutral Python semantic implementation and approved parity-output producer from the SPEC, policy registry, semantic IR, target ADRs, and draft evidence contract.
---

# Generate

## Trigger

Use only when durable run state authorizes `generate`. Read `AGENTS.md`, `config/workflow.yaml`, the approved SPEC and ADRs, canonical policy registry, semantic IR, and schema-valid draft `config/tieout.yaml`.

## Required inputs

- Approved module SPEC and acceptance criteria.
- Approved target ADRs.
- Canonical policy registry and approved semantic IR.
- Draft tie-out contract containing the approved producer command shape and actual-output path.
- Selected imported patterns with provenance, if any.

## Workflow

1. Verify that every implemented requirement resolves to a SPEC, semantic IR, and policy-registry behavior ID.
2. Generate the smallest pure Python semantic core; preserve keys, types, missing values, categories, formulas, state reset, and calculation order.
3. Keep runtime-specific code out of the semantic core and prevent duplicate formula ownership.
4. Implement the deterministic producer command declared in `config/tieout.yaml`. It must read only governed fixture inputs and write only the configured actual-output CSV under `artifacts/generated/<run-id>/`.
5. Ensure the producer emits every configured key and actual comparison column, rejects duplicate keys, uses stable row and column ordering, returns non-zero on execution failure, and never reads the SAS oracle, expected columns, or prior actual output.
6. Make repeated runs over the same governed inputs byte-identical; expose no clock, randomness, network, or environment-dependent behavior unless the approved contract freezes it.
7. Apply selected patterns only within approved applicability, add requirement citations, and run static/unit checks.
8. Record implementation evidence and stop without invoking `test` or `validate`.

## Output artifact

```text
src/sas_migration/semantic/
```

plus the module-specific producer entry point declared by the approved contract.

## Verification

Every implementation unit traces to approved behavior IDs; the configured producer command resolves without a shell, creates byte-identical schema-valid CSV output from governed fixture inputs, enforces unique keys and stable ordering, and cannot access or rewrite protected oracle evidence.

## Boundaries

Do not change PRD, SPEC, ADRs, semantic IR, policy registry, expected evidence, fixture selection, keys, tolerances, comparator, proof boundary, or oracle lock. Do not embed selected-runtime code in the semantic formula owner. Never generate expected output from the implementation under test.

## Stop conditions

Stop on incomplete IR, unresolved policy, missing producer contract, missing approved input schema, duplicate semantic owner, rule conflict, oracle access by the producer, or any required unapproved assumption.
