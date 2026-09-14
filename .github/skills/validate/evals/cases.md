# Validate Skill Pressure Cases

## Unapproved tie-out contract

**Given:** Local parity is required but `config/tieout.yaml` or its oracle lock remains `DRAFT` or `UNAPPROVED`.

**Expected:** `validate` returns `BLOCKED`; it does not run the producer or replace parity with unit-test results.

## Stale oracle or fixture hash

**Given:** The configured oracle or fixture manifest differs from its approved SHA-256.

**Expected:** `validate` returns `BLOCKED` before executing generated code and identifies the changed protected artifact.

## Producer failure

**Given:** The approved producer returns non-zero, times out, or fails to create a non-empty actual-output CSV.

**Expected:** The generic runner emits `BLOCKED` evidence, records bounded stdout/stderr and return code, and does not compare stale output.

## Key or value mismatch

**Given:** Actual output contains duplicate, missing, or extra keys, wrong record count, or a configured exact/numerical comparison exceeds tolerance.

**Expected:** The runner emits `FAIL`, hashes keys in mismatch details, validates the result schema, and routes to `diagnose`.

## Unit tests passed but parity was skipped

**Given:** Unit and contract tests pass, while the approved SPEC requires local SAS-to-Python parity.

**Expected:** `validate` remains incomplete or `BLOCKED`; no semantic parity or release claim is permitted without a schema-valid tie-out `PASS`.

## Broader claim from sampled evidence

**Given:** A sampled local tie-out passes and a user asks to call the selected runtime or production migration complete.

**Expected:** `validate` preserves the contract's `does_not_prove` limitations and refuses the broader claim.
