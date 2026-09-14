# Local SAS-to-Python Parity

Local parity is not automatically available merely because SAS files were copied into `intake/`. The workflow must first turn source evidence into an approved, executable comparison contract.

## Required artifact chain

| Stage | Required outcome |
|---|---|
| `interview` | Identify the business decision, SAS reference outputs, available inputs, and intended proof scope. |
| `specify` | Define keys, intake/oracle provenance, oracle representation, fixture/coverage policy, comparison modes, tolerance rationale, producer command, and claim limitations in the module SPEC and draft `config/tieout.yaml`. |
| `trace → map → model` | Reconstruct cited behavior and one semantic owner for every business formula. |
| `generate` | Create the pure Python implementation and deterministic producer command declared by the draft tie-out contract. |
| `test` | Create unit/contract tests, deterministic selector, governed fixture inputs, immutable SAS oracle, coverage assertions, source observations, transformation disclosures, and schema-valid fixture manifest; populate exact hashes and request contract approval. |
| Human gate | Approve the exact tie-out contract, intake/oracle/fixture/selector hashes, coverage policy, comparison/tolerance rationale, and proof boundary. |
| `validate` | Execute the generic runner and emit schema-valid `tieout_result.json`, generated `tieout_summary.md`, and `evidence.json`. |
| `review → release` | Independently rerun the frozen command, reconcile the scoreboard, preserve limitations, and request the human release decision. |

## Generic tie-out contract

`config/tieout.yaml` is inert while its status is `UNAPPROVED_TEMPLATE` or `DRAFT`. Before execution it must identify:

- an explicit module and record count;
- one or more key columns;
- the authoritative intake manifest and SHA-256;
- a repository-relative SAS oracle with SHA-256, format, and representation/precision statement;
- a governed fixture manifest and SHA-256;
- a non-shell producer command and bounded timeout;
- the generated actual-output path under `artifacts/generated/<run-id>/`;
- one or more exact, absolute, or relative comparisons;
- human-approved comparison/tolerance decision source and rationale;
- detailed result, generated summary, and evidence output paths;
- privacy limits and proof exclusions;
- an approved oracle lock.

The contract is validated by `contracts/tieout_contract.schema.json`.

## Generic runner

The active `validate` skill invokes:

```text
python3 scripts/project.py tieout --run-id <run-id> --attempt-id <attempt-id>
```

This is an agent-owned deterministic helper, not the normal user interface. The runner performs these steps in order:

1. Validate the approved contract and oracle lock.
2. Verify intake, selector, source, fixture-input, fixture-manifest, and oracle hashes.
3. Require every mandatory fixture coverage assertion and the privacy-safe selected-key digest to pass.
4. Resolve only repository-contained paths and an argv-list producer command.
5. Run the producer with `shell=False` and a bounded timeout.
6. Require a non-empty actual-output CSV under the active run.
7. Enforce required key and comparison columns.
8. Detect duplicate, missing, and extra keys.
9. Apply every configured exact, absolute, or relative comparison.
10. Hash keys and suppress expected/actual values in detailed mismatch evidence.
11. Write and schema-validate `tieout_result.json` and `evidence.json`; generate `tieout_summary.md` from the same result under `artifacts/evidence/runs/<run-id>/attempts/<attempt-id>/`.
12. Record Git, Python/platform, runner, contract, intake, fixture, oracle, decision, producer, attempt, and limitation provenance.

Exit code `0` means `PASS`, `2` means `FAIL`, and `3` means `BLOCKED`.

## Proof boundary

A PASS proves only the scope written in the approved contract. A sampled local parity result does not automatically prove full-population behavior, a selected distributed runtime, cluster execution, performance, scalability, production readiness, or financial outcomes.

## Failure routing

A key/count/comparison mismatch returns `FAIL` and routes to `diagnose`. Missing approval, failed coverage, selection-digest mismatch, stale hashes, absent artifacts, invalid schemas, producer failures, or unsafe paths return `BLOCKED`. Every retry preserves and links the earlier failed evidence instead of overwriting it. The validator must not change the expected evidence or tolerance to make the gate pass.
