# Reusable Parity Capability Audit

## Root cause

The first clean-slate publication correctly removed LC-LOGIT-01 source, generated Python, fixtures, predictions, and evidence. It also removed the module-specific fixture builder and tie-out runner without replacing them with a module-neutral execution framework. The original `test` and `validate` skills therefore described parity but could not guarantee it.

## Capability comparison

| Tested LC-LOGIT-01 capability | Generic repair status | Remaining reusable control |
|---|---|---|
| Canonical intake manifest and source SHA-256 values | Intake manifest already exists | Bind its exact path/hash into the approved tie-out contract and emitted evidence |
| Deterministic, bounded fixture selection | Fixture manifest schema exists | Require a deterministic selector command/version and approved selection policy |
| Balanced outcomes, category completeness, score-band spread, and numeric boundaries | Basic record count is enforced | Represent module-defined coverage assertions generically and require all mandatory assertions to pass |
| Streaming source counts and explicit reconstruction deviations | Not represented | Record source observations and transformations/deviations in the fixture manifest |
| Selection reason for every selected record | Not represented generically | Record aggregate reason counts or hashed-key reasons without publishing raw identifiers |
| Immutable SAS oracle with full-precision export | Oracle path/hash is enforced | Record oracle format, provenance, and precision/representation statement in the approved contract |
| Frozen keys, columns, metrics, and tolerances | Enforced by contract schema | Add required human decision rationale for comparison modes and tolerances |
| Pure Python scorer with duplicate-key rejection | Producer contract exists | Require producer tests for output schema, uniqueness, deterministic repeatability, and oracle isolation |
| Missing, extra, duplicate key detection | Implemented | Retain counts and privacy-safe mismatch samples |
| Exact, absolute, and relative comparisons | Implemented | Retain metric-specific tolerance echo, failure counts, and maximum deltas |
| PASS/FAIL/BLOCKED detailed result | Implemented | Add a human-readable summary generated from the same result, never hand-maintained |
| Evidence includes run, command, commit, intake/config hashes, summary, and limitations | Partially implemented | Add Git commit, Python/platform, runner hash, intake-manifest hash, summary artifact, and contract decision basis |
| Failed validation routes to diagnose/repair/review | Skills already define recovery | Require run-state history to link failed and retried result hashes; never overwrite prior evidence |
| Review reruns the deterministic command | Generic review exists | Require review to consume and independently reproduce tie-out result, summary, contract, fixture coverage, and limitations |
| Release packet presents parity headline and proof boundary | Generic release exists | Require the release packet to derive its scoreboard from reviewed evidence and preserve limitations verbatim |

## Publication boundary

The reusable branch must provide contracts, schemas, deterministic runners, pressure tests, and documentation only. It must not include LC-LOGIT-specific SAS, raw/reference CSVs, generated scorer code, fixed keys, fixed columns, fixture size, tolerances, predictions, run state, or accepted evidence.

## Completion rule

A clean-template run may claim local SAS-to-Python parity only when all of the following exist at exact hashes:

1. an approved module SPEC and tie-out contract;
2. an authoritative intake manifest;
3. a governed fixture manifest with passed coverage assertions;
4. an immutable SAS oracle;
5. a deterministic, oracle-isolated actual-output producer;
6. a schema-valid `tieout_result.json` with `PASS`;
7. a matching evidence bundle and generated human-readable summary;
8. an independent review that reruns the frozen command;
9. an explicit proof boundary in the release decision.

## Second verification outcome

The second audit re-read the tested LC-LOGIT-01 fixture builder, fixture contract tests, selection manifest, comparator, detailed evidence, durable run state, release packet, and the reusable review/release skills. The generic framework now closes every reusable gap listed above:

| Control | Generic implementation |
|---|---|
| Intake and oracle authority | Approved contract freezes intake path/hash plus oracle path/hash, format, and representation statement. |
| Deterministic fixture construction | Manifest records selector path/hash/command/version, source and input hashes, source observations, approved transformations, limitations, and the selected-key digest. |
| Module-specific coverage without hard-coded LC-LOGIT rules | Manifest carries required assertions with observed values and PASS/FAIL status; the runner blocks if any mandatory assertion fails. |
| Producer isolation and repeatability | `generate` and `test` require stable ordering, unique keys, byte-identical repeated output, and no oracle access. |
| Keyed comparator | Generic runner enforces record count, duplicate/missing/extra keys, exact/absolute/relative rules, tolerance echo, failures, and maximum deltas. |
| Privacy-safe evidence | Detailed mismatches contain deterministic key hashes and reasons while raw keys and compared values remain suppressed by default. |
| Reproducible evidence | Result, generated Markdown summary, and evidence bundle record commit, Python/platform, runner, contract, intake, fixture, oracle, producer, decision rationale, and limitations. |
| Append-only retry history | Every validation attempt uses `artifacts/evidence/runs/<run-id>/attempts/<attempt-id>/`; invalid attempt IDs and path escape are rejected. |
| Independent review | Reviewer reruns the frozen command, reconciles result/summary/evidence, verifies protected hashes and retry lineage, and cannot repair. |
| Evidence-derived release | Release scoreboard is derived from independently reviewed machine-readable evidence; proof exclusions, rollback, candidate status, and human approval remain mandatory. |

These controls are module-neutral. The clean branch still contains no SAS source, business data, LC-LOGIT-specific scorer, fixture, predictions, accepted run state, or parity evidence.
