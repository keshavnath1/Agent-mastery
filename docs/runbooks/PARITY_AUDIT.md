# Clean-Slate Parity and Tie-Out Audit

## Finding

The published clean-slate branch correctly excludes LC-LOGIT-01 source, generated Python, fixtures, and evidence, but it also excludes the **generic executable bridge** that should recreate those assets for a new module. The lifecycle reaches `test` and `validate` only as prose contracts; no deterministic generic comparator or tie-out command exists.

| Area | Clean-template behavior | Working LC-LOGIT-01 behavior | Gap |
|---|---|---|---|
| `specify` | Defines a testable acceptance row in the module SPEC and may carry approved `config/tieout.yaml` values | Approved keys, oracle, columns, fixture scope, metrics, tolerance, and proof boundary were frozen | Structurally adequate, but no strict reusable schema binds these fields to an executable runner |
| `generate` | Creates a backend-neutral semantic implementation | Created the LC-LOGIT scorer and coefficient loader | Does not require a standard module scoring entry point that a generic tie-out runner can invoke |
| `test` | Creates tests and fixtures, then says “module-specific commands thereafter” | A 50-record governed fixture and contract tests were created | No required parity plan, actual-output producer, fixture manifest, or comparator dry run |
| `validate` | Says “run the earliest applicable gate” and emit evidence | A module-specific runner scored rows, compared keyed outputs, and wrote detailed evidence | No shipped gate command, comparator, result schema, or deterministic evidence writer |
| `scripts/project.py` | Supports only `validate`, `smoke`, `intake`, `status`, and `start` | Module-specific tie-out was run by `scripts/run_coverage_tieout.py` | No `tieout` subcommand available to the active `validate` skill |
| Evidence contracts | Generic evidence bundle allows arbitrary artifact objects | Detailed result records row counts, missing/extra keys, deltas, failures, limitations, and details | No strict generic tie-out-result schema |

## Root cause

The reusable branch removed the LC-LOGIT-specific runner and comparator to avoid publishing generated implementation. That exclusion was correct. The mistake was failing to replace them with a **module-neutral tie-out framework**. As a result, another agent can generate tests, but the framework does not force it to produce or execute a keyed oracle comparison.

## Required repair

The clean template needs a generic, contract-driven tie-out capability that remains inert until a human approves its configuration:

1. Add strict schemas for the tie-out contract and result.
2. Add a generic CSV comparator supporting one or more keys and multiple numerical or exact comparisons.
3. Add a deterministic `scripts/run_tieout.py` runner that validates the approved contract, optionally invokes an approved module producer command without a shell, verifies paths and hashes, compares expected and actual outputs, writes a versioned result and evidence bundle, and returns a non-zero exit code on `FAIL` or `BLOCKED`.
4. Add `python3 scripts/project.py tieout --run-id <id>` as an agent-owned helper, not a user-facing command.
5. Strengthen `generate` so each module provides the producer entry point declared by the approved contract.
6. Strengthen `test` so it creates a governed fixture manifest, expected-oracle lock, actual-output producer test, and comparator dry run.
7. Strengthen `validate` so local parity is mandatory whenever the approved SPEC requires it and so it cannot declare PASS without the generic tie-out evidence.
8. Add architecture and unit tests that prove the template remains inert while unapproved and executes a synthetic keyed parity case after approval.

This repair must not add SAS files, LC-LOGIT data, generated module Python, fixed tolerances, or copied example evidence to the public template.
