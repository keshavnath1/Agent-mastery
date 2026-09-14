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
2. Implement and test from the approved population choice. `GOVERNED_SAMPLE_50` and the sample phase of `PHASED_50_THEN_FULL` require exactly 50 governed records; `FULL_POPULATION` requires every eligible keyed input and oracle record plus source-count reconciliation; `CUSTOM_GOVERNED_SAMPLE` requires the human-approved count and deterministic policy. Preserve selector path, command, version, and SHA-256; never infer expected output from generated Python.
3. Create and validate `tests/fixtures/<module-id>/fixture_manifest.json` with `contracts/fixture_manifest.schema.json`; record source and fixture hashes, streamed/source observations, approved transformations or reconstruction deviations, mandatory module-defined coverage assertions, privacy-safe selection-reason counts, selected-key digest, immutable SAS oracle, record count, and limitations.
4. Update only the draft fixture/oracle path and hash fields in `config/tieout.yaml`; validate it against `contracts/tieout_contract.schema.json` and present the exact contract/hash for human approval. Do not self-approve it.
5. Test that the producer creates the configured actual-output CSV with unique keys and required columns, produces byte-identical output on a repeated run, cannot read or modify the oracle, and fails loudly on invalid inputs.
6. Test fixture invariants explicitly: selected population choice and current phase, approved record count, key uniqueness, exact fixture/oracle key-set alignment, every mandatory coverage assertion, and the full-population follow-up flag. A phased sample PASS must leave the later full gate open.
7. Exercise `scripts/run_tieout.py` with synthetic test-only PASS, numerical FAIL, duplicate/missing/extra keys, failed coverage, stale intake/oracle/fixture/selector/input hashes, producer failure/timeout, selection-digest mismatch, and unapproved-contract cases. Test schemas, generated summary, proof boundary, and privacy-safe mismatch evidence.
8. Run the deterministic suite and stop without invoking `validate`.

## Output artifact

Tests under `tests/` plus governed `tests/fixtures/<module-id>/fixture_manifest.json` and a schema-valid draft tie-out contract ready for human approval.

## Verification

The selected population, phase, count, follow-up obligation, fixture, selector, intake, source, input, and oracle provenance validate; every mandatory coverage assertion passes; producer repeatability and comparator tests pass; negative cases fail or block as specified; protected source/oracle content remains unchanged. `python3 scripts/project.py smoke` verifies framework checks, followed by module tests owned by this skill.

## Boundaries and red flags

Do not weaken assertions, copy expected values from actual output, choose tolerances from observed Python deltas without human approval, expose raw keys in evidence, or mark the oracle lock approved. A unit-test PASS without a governed fixture and executable parity contract is not completion of this stage.

## Stop conditions

Stop when the population choice, current phase, follow-up obligation, expected behavior, selection policy, oracle provenance, keys, comparison rules, tolerance, producer behavior, privacy boundary, or fixture approval is unknown.
