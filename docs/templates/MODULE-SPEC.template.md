# Module Specification: <MODULE-ID>

**Status:** DRAFT — human approval required

**PRD:** `<path and SHA-256>`
**Capability map:** `<path and SHA-256>`

## Objective

State the smallest end-to-end behavior this tracer bullet must preserve.

## Inputs

| Input | Type and schema | Authority | Missing or invalid behavior |
|---|---|---|---|
| `<name>` | `<definition>` | `<approved source>` | `<required handling>` |

## Outputs

| Output | Type and schema | Consumer | Required ordering or key behavior |
|---|---|---|---|
| `<name>` | `<definition>` | `<consumer>` | `<contract>` |

## Behavioral rules

Assign a stable behavior ID to each observable rule. Cite source locations or approved human decisions.

| Behavior ID | Rule | Source evidence | Semantic owner |
|---|---|---|---|
| B001 | `<rule>` | `<artifact and location>` | `<semantic core or adapter>` |

## State, ordering, and dependencies

Document retained state, grouping, ordering, macro expansion, joins, procedures, failure behavior, and cross-program dependencies that affect observable output.

## Acceptance contract

| Check | Keys | Expected evidence | Metric | Approved tolerance | Proof boundary |
|---|---|---|---|---|---|
| `<check>` | `<keys>` | `<artifact>` | `<metric>` | `<human-approved value>` | `<what PASS proves>` |

## Exclusions

State what this specification does not authorize or prove, including unselected runtimes and operational claims.

## Verification plan

Map each behavior ID to a deterministic unit, contract, parity, or runtime check. A required check must not be weakened by implementation or repair work.

## Unresolved decisions

List unknowns and their owners. Stop rather than inventing missing behavior, keys, expected values, tolerances, runtime configuration, or approvers.
