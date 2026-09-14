# Local SAS-to-Python Parity

Local parity is not automatically available merely because SAS files were copied into `intake/`. The workflow must first turn source evidence into an approved, executable comparison contract.

## Required artifact chain

| Stage | Required outcome |
|---|---|
| `interview` | Identify the business decision, SAS reference outputs, available inputs, and intended proof scope. |
| `specify` | Define keys, fixture policy, expected and actual columns, comparison modes, tolerances, producer command, and claim limitations in the module SPEC and draft `config/tieout.yaml`. |
| `trace → map → model` | Reconstruct cited behavior and one semantic owner for every business formula. |
| `generate` | Create the pure Python implementation and deterministic producer command declared by the draft tie-out contract. |
| `test` | Create unit/contract tests, governed fixture inputs, immutable SAS oracle, and schema-valid fixture manifest; populate exact hashes and request contract approval. |
| Human gate | Approve the exact tie-out contract, oracle hash, fixture-manifest hash, tolerance, and proof boundary. |
| `validate` | Execute the generic runner and emit schema-valid `tieout_result.json` plus `evidence.json`. |

## Generic tie-out contract

`config/tieout.yaml` is inert while its status is `UNAPPROVED_TEMPLATE` or `DRAFT`. Before execution it must identify:

- an explicit module and record count;
- one or more key columns;
- a repository-relative SAS oracle and SHA-256;
- a governed fixture manifest and SHA-256;
- a non-shell producer command and bounded timeout;
- the generated actual-output path under `artifacts/generated/<run-id>/`;
- one or more exact, absolute, or relative comparisons;
- human-approved tolerances where numerical comparison is used;
- evidence output paths, privacy limits, and proof exclusions;
- an approved oracle lock.

The contract is validated by `contracts/tieout_contract.schema.json`.

## Generic runner

The active `validate` skill invokes:

```text
python3 scripts/project.py tieout --run-id <run-id>
```

This is an agent-owned deterministic helper, not the normal user interface. The runner performs these steps in order:

1. Validate the approved contract and oracle lock.
2. Verify oracle and fixture-manifest hashes.
3. Resolve only repository-contained paths and an argv-list producer command.
4. Run the producer with `shell=False` and a bounded timeout.
5. Require a non-empty actual-output CSV under the active run.
6. Enforce required key and comparison columns.
7. Detect duplicate, missing, and extra keys.
8. Apply every configured exact, absolute, or relative comparison.
9. Hash key values in detailed mismatch evidence.
10. Write and schema-validate `tieout_result.json` and `evidence.json`.

Exit code `0` means `PASS`, `2` means `FAIL`, and `3` means `BLOCKED`.

## Proof boundary

A PASS proves only the scope written in the approved contract. A sampled local parity result does not automatically prove full-population behavior, a selected distributed runtime, cluster execution, performance, scalability, production readiness, or financial outcomes.

## Failure routing

A key/count/comparison mismatch returns `FAIL` and routes to `diagnose`. Missing approval, stale hashes, absent artifacts, invalid schemas, producer failures, or unsafe paths return `BLOCKED`. The validator must not change the expected evidence or tolerance to make the gate pass.
