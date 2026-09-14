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

1. Validate `config/tieout.yaml` against `contracts/tieout_contract.schema.json`; require status and oracle lock `APPROVED`, and verify the population choice, current phase, record count, selection policy, follow-up obligation, source, and rationale match the approved interview and SPEC.
2. Verify protected intake manifest, selector, source, fixture-input, fixture-manifest, oracle, contract, and current-commit provenance before executing implementation code; require every mandatory fixture coverage assertion to pass.
3. Run the earliest applicable frozen gate. When local SAS-to-Python parity is required, allocate the next append-only attempt ID and invoke `python3 scripts/project.py tieout --run-id <run-id> --attempt-id <attempt-id>` as an agent-owned helper.
4. Require `scripts/run_tieout.py` to invoke the approved producer without a shell, verify the privacy-safe selected-key digest, compare configured keys and columns, enforce the selected population record count and tolerances, echo the population/phase/follow-up obligation, hash keys and suppress values in mismatch evidence, and write `tieout_result.json`, `tieout_summary.md`, and `evidence.json` under the active run.
5. Validate JSON artifacts against their schemas; record Git commit, Python/platform, runner and contract hashes, intake/fixture/oracle hashes, decision basis, producer command, coverage/key/comparison summaries, and limitations. Classify `PASS`, `FAIL`, or `BLOCKED` exactly as emitted.
6. Append artifact paths and hashes to durable run-state history. A retry must create new evidence for the attempt and link the previous failed result; never overwrite or relabel prior evidence.
7. Stop at the first failed gate; do not execute later gates or broaden the proof claim. If `PHASED_50_THEN_FULL` is in its sample phase, record sample PASS only and keep the full-population gate open.

## Output artifact

`artifacts/evidence/runs/<run-id>/attempts/<attempt-id>/evidence.json`, with generated `tieout_result.json` and `tieout_summary.md` in the same attempt directory as governed local-parity artifacts when applicable.

## Verification

The evidence bundle, tie-out result, generated summary, selected population and phase, follow-up obligation, commit, runner, intake, selector/source/input, contract, oracle, and fixture hashes; coverage assertions; producer command; row/key/comparison summaries; decision rationale; and limitations are reproducible. A local parity claim cannot pass through unit tests or file existence alone.

## Boundaries and red flags

Never change expected output, oracle, fixture selection, tolerance, comparator, key, producer contract, evaluator, or proof boundary while validating. Never substitute a hand-written narrative for the generic runner’s evidence. Red flags include unapproved contract status, stale hashes, missing producer output, duplicate keys, missing/extra keys, raw keys in evidence, skipped comparisons, and unsupported completion claims.

## Stop conditions

Return `BLOCKED` when the population decision, phase, record count, follow-up obligation, approval, schema, intake/selector/source/input/oracle/fixture provenance, mandatory coverage, selection digest, producer, or required columns are missing, inconsistent, or stale. Return `FAIL` on key, count, or configured comparison failure. Hand failed evidence to `diagnose` and do not repair during validation.
