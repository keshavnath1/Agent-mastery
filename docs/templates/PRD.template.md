# Product Requirements Document: <MODULE-ID>

**Status:** DRAFT — human approval required

**Owner:** <business owner>

**Source run:** <run-id>
**Interview artifact:** <path and SHA-256>

## Outcome and user problem

Describe the business decision, calculation, report, model, or workflow that the SAS assets currently support. State who uses the result and why preserving behavior matters.

## Approved source boundary

| Source artifact | Role | Authority | SHA-256 |
|---|---|---|---|
| `<path>` | `<program/log/LST/input/reference>` | `<authoritative/supporting>` | `<hash>` |

## In scope

Describe only the behavior approved for the current tracer bullet.

## Out of scope

List behaviors, runtimes, datasets, deployment targets, performance claims, and operational capabilities that this run will not prove.

## Invariants

| Invariant | Verification method | Owning gate |
|---|---|---|
| `<behavior that must not change>` | `<deterministic check>` | `<stage>` |

## Acceptance evidence

Define keys, expected outputs, comparison metrics, tolerances, fixture or population boundary, and the exact claim a passing result supports. Do not borrow values from examples.

## Runtime direction

Record candidate semantic and selected runtimes as unresolved until the `decide` stage approves the relevant ADR.

## Human gates and owners

| Decision | Approver | Status |
|---|---|---|
| Migration intent | `<name or role>` | `PENDING` |
| PRD and module SPEC | `<name or role>` | `PENDING` |
| Architecture decision | `<name or role>` | `PENDING` |
| Evidence contract or oracle | `<name or role>` | `PENDING` |
| Merge and release | `<name or role>` | `PENDING` |

## Open decisions

List unknowns explicitly. Do not disguise them as facts or infer them from code alone.
