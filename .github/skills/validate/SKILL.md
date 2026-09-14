---
name: validate
description: Execute frozen unit, contract, local parity, and runtime gates and compare produced evidence with approved expectations. Use after tests and code or adapter changes and before review.
---

# Validate

## Trigger

Use when durable run state authorizes `validate`. Read `AGENTS.md`, the approved SPEC, current commit, `config/tieout.yaml`, and protected oracle/fixture hashes.

## Required inputs

Implementation, tests, human-approved tie-out contract and oracle lock, immutable expected artifacts, governed fixture manifest, generated producer entry point, and current commit.

## Workflow

1. Validate `config/tieout.yaml` against `contracts/tieout_contract.schema.json`; require status and oracle lock `APPROVED` for any required local parity claim.
2. Verify protected oracle and fixture-manifest hashes before executing implementation code.
3. Run the earliest applicable frozen gate. When local SAS-to-Python parity is required, invoke `python3 scripts/project.py tieout --run-id <run-id>` as an agent-owned helper.
4. Require `scripts/run_tieout.py` to invoke the approved producer without a shell, compare configured keys and columns, enforce record count and tolerances, hash keys in mismatch evidence, and write both `tieout_result.json` and `evidence.json` under the active run.
5. Validate both artifacts against their schemas, record command/environment/output/limitations, and classify `PASS`, `FAIL`, or `BLOCKED` exactly as emitted.
6. Stop at the first failed gate; do not execute later gates or broaden the proof claim.

## Output artifact

`artifacts/evidence/runs/<run-id>/evidence.json`, with `tieout_result.json` as the governed local-parity detail artifact when applicable.

## Verification

The evidence bundle, tie-out result, contract hash, oracle hash, fixture-manifest hash, producer command, row counts, key counts, comparison summaries, and limitations are reproducible. A local parity claim cannot pass through unit tests or file existence alone.

## Boundaries and red flags

Never change expected output, oracle, fixture selection, tolerance, comparator, key, producer contract, evaluator, or proof boundary while validating. Never substitute a hand-written narrative for the generic runner’s evidence. Red flags include unapproved contract status, stale hashes, missing producer output, duplicate keys, missing/extra keys, raw keys in evidence, skipped comparisons, and unsupported completion claims.

## Stop conditions

Return `BLOCKED` when approval, schema, oracle, fixture, hash, producer, or required columns are missing. Return `FAIL` on key, count, or configured comparison failure. Hand failed evidence to `diagnose` and do not repair during validation.
