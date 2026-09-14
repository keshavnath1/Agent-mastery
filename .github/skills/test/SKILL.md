---
name: test
description: Create unit, contract, boundary, regression, fixture-provenance, and parity-runner tests from approved specifications. Use after generation and after every accepted defect.
---

# Test

## Trigger

Use when durable run state authorizes `test`. Read `AGENTS.md`, the approved SPEC, semantic IR, draft `config/tieout.yaml`, and generated producer entry point.

## Required inputs

SPEC, semantic IR, invariants, governed source/oracle policy, generated producer, comparison rules, and test-data selection policy.

## Workflow

1. Derive unit, contract, boundary, missing, category, state, negative, and regression tests from requirements rather than implementation structure.
2. Create the governed parity fixture using the approved selection policy. Preserve source hashes and never infer expected output from generated Python.
3. Create and validate `tests/fixtures/<module-id>/fixture_manifest.json` with `contracts/fixture_manifest.schema.json`; record fixture inputs, key columns, immutable SAS oracle path/hash, source provenance, record count, privacy boundary, and limitations.
4. Update only the draft fixture/oracle path and hash fields in `config/tieout.yaml`; validate it against `contracts/tieout_contract.schema.json` and present the exact contract/hash for human approval. Do not self-approve it.
5. Test that the producer creates the configured actual-output CSV with unique keys and required columns, cannot read or modify the oracle, and fails loudly on invalid inputs.
6. Exercise `scripts/run_tieout.py` with synthetic test-only PASS, FAIL, duplicate-key, missing-key, hash-mismatch, and unapproved-contract cases. Test evidence schema and key hashing.
7. Run the deterministic suite and stop without invoking `validate`.

## Output artifact

Tests under `tests/` plus governed `tests/fixtures/<module-id>/fixture_manifest.json` and a schema-valid draft tie-out contract ready for human approval.

## Verification

Fixture and oracle provenance validate; producer and comparator tests pass; negative cases fail or block as specified; protected source/oracle content remains unchanged. `python3 scripts/project.py smoke` verifies framework checks, followed by module tests owned by this skill.

## Boundaries and red flags

Do not weaken assertions, copy expected values from actual output, choose tolerances from observed Python deltas without human approval, expose raw keys in evidence, or mark the oracle lock approved. A unit-test PASS without a governed fixture and executable parity contract is not completion of this stage.

## Stop conditions

Stop when expected behavior, selection policy, oracle provenance, keys, comparison rules, tolerance, producer behavior, privacy boundary, or fixture approval is unknown.
