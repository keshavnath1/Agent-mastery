---
name: map
description: Map every traced SAS behavior and column dependency to an approved target responsibility and reusable pattern in the canonical policy_registry.yaml. Use after trace and before semantic modeling.
---

# Map

## Trigger

Use only when durable run state authorizes `map`. Read `AGENTS.md`, `config/workflow.yaml`, `references/behavior-mapping-contract.md`, the approved PRD/SPEC and target ADRs, and any applicable target taxonomy that is available.

## Required inputs

- Approved canonical `stage1_extraction/output/execution_trace.json` and hash.
- Approved module SPEC and target ADRs.
- Optional approved or candidate pattern catalogs with provenance. Their absence must not block runtime-neutral semantic mapping.
- Canonical policy-registry schema and template.

## Workflow

1. Read the trace and cited SAS source blocks together.
2. Build a column and dataset dependency graph.
3. Split the source into distinct business and execution behavior blocks.
4. For every block, record source citations, exact excerpt hash, inputs, outputs, dependencies, stateful constructs, complexity, semantic owner, adapter owner, tests, and unresolved questions.
5. Read the selected runtime from the approved PRD/SPEC and ADRs. Evaluate matching taxonomies and pattern catalogs when available; treat them as optional refinements rather than architectural authority.
6. Activate the LP Emulator taxonomy and Golden Rules only when an approved target ADR explicitly selects LP Emulator. Never apply LP Emulator names or rules to a generic PySpark, Ray, Python-only, Cython, or other runtime decision.
7. When no matching taxonomy exists, map runtime-neutral semantic responsibilities and record the adapter boundary required by the approved ADR. Keep unsupported implementation details explicitly unresolved.
8. Select a pattern only when provenance, applicability, constraints, and ownership are compatible with the SPEC and ADRs. Detect cross-bundle conflicts and reject duplicate semantic ownership; each business formula must have exactly one implementation owner.
9. Map every traced behavior, defer it with reason, or mark it unresolved; never force-fit.
10. Write `policy/policy_registry.yaml` from the canonical template and validate it against `schemas/policy_registry.schema.json`.
11. Calculate its hash, return `PASS`, `FAIL`, or `BLOCKED`, and stop without invoking `model`.

## Canonical output

```text
policy/policy_registry.yaml
```

Do not create a competing editable mapping artifact under `artifacts/plans/`.

## Verification

- Canonical trace path and hash match the approved input.
- Every traced behavior has one status: mapped, deferred, or unresolved.
- Exactly one semantic owner exists for each behavior and formula.
- Runtime adapters do not re-own business formulas.
- Selected patterns cite their bundle and source ADR provenance.
- LP Emulator module types and Golden Rules are used only under an approved ADR that explicitly selects LP Emulator.
- A missing matching taxonomy is not itself a blocker when runtime-neutral semantic responsibilities and an ADR-aligned adapter boundary can be recorded.
- YAML schema passes.

## Boundaries

Do not rewrite SAS behavior, resolve uncertainty by guess, import patterns, generate code, make a runtime decision, or allow an imported pattern or taxonomy to override the approved SPEC or ADR. Do not treat complexity as proof that a pattern is correct.

## Stop conditions

Stop on trace hash mismatch, missing or contradictory approved ADR, unresolved semantic owner, conflicting patterns, duplicate formula owner, incomplete dependency graph, or schema failure. Do not stop merely because an optional matching taxonomy or pattern catalog is unavailable.
