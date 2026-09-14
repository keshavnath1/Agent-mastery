---
name: generate
description: Generate the backend-neutral Python semantic implementation from the approved SPEC, policy registry, semantic IR, and target ADRs. Use only after all prerequisite gates pass.
---

# Generate

## Trigger

Use only when durable run state authorizes `generate`. Read `AGENTS.md`, `config/workflow.yaml`, the approved SPEC and ADRs, canonical `policy/policy_registry.yaml`, and approved semantic IR.

## Required inputs

- Approved module SPEC and acceptance criteria.
- Approved target ADRs.
- Canonical policy registry and hash.
- Approved semantic IR and implementation plan.
- Selected imported patterns with provenance, if any.
- Applicable coding policies. Load `docs/policies/lp-emulator-golden-rules.md` only when an approved ADR activates it.

## Workflow

1. Verify that every implemented requirement resolves to the SPEC, semantic IR, and policy-registry behavior ID.
2. Generate the smallest pure Python/NumPy semantic core; preserve keys, types, missing values, categories, formulas, state reset, and calculation order.
3. Keep runtime-specific code out of the semantic core and prevent duplicate formula ownership.
4. Apply selected patterns and rule IDs only within their approved applicability.
5. Add requirement and behavior citations to code and tests.
6. Run approved static and unit checks through the skill workflow.
7. Write the implementation evidence, return `PASS`, `FAIL`, or `BLOCKED`, and stop without invoking `test`.

## Output artifact

```text
src/sas_migration/semantic/
```

## Verification

Every implementation unit traces to approved requirements and behavior IDs; applicable Golden Rules and approved exceptions are cited; static and unit checks pass; protected artifacts remain unchanged.

## Boundaries

Do not change PRD, SPEC, ADRs, semantic IR, policy registry, expected evidence, keys, tolerances, comparator, or protected outputs. Do not embed PySpark, Ray, Cython, or LP Emulator runtime code in the semantic formula owner. Do not invent missing behavior.

## Stop conditions

Stop on incomplete IR, unresolved policy entry, missing approval, conflicting pattern, duplicate semantic owner, rule conflict, or any required unapproved assumption.
