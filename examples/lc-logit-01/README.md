# LC-LOGIT-01: Documentation-Only Example

This example explains how the agent-mastery lifecycle was applied to a **score-only loan-risk logistic regression migration**. It intentionally contains no proprietary or generated execution assets.

> Do not use this example as a requirements source, oracle, fixture, tolerance, or implementation for another module. A new migration must derive and approve its own contracts.

## Business story

The legacy SAS process fitted a logistic model and produced keyed risk scores. The tracer bullet kept model fitting in SAS and asked a backend-neutral Python semantic core to consume frozen coefficients and prepared inputs, reproduce the linear predictor and probability, and compare keyed results before any selected-runtime claim.

## Lifecycle journey

| Act | Skills demonstrated | Human or deterministic result |
|---|---|---|
| Align | `interview → specify → decide` | The human approved score-only scope, the prepared-input boundary, acceptance evidence, and a backend-neutral semantic-core ADR |
| Reuse / Reconstruct | `trace → map → model` | The agents produced the canonical SAS execution trace, policy registry, and semantic IR; optional `harvest/import` were skipped because no approved source workspace was supplied |
| Build / Prove | `generate → test → validate` | The semantic implementation and tests were generated from approved contracts; the 50-record local tie-out passed at its separately approved tolerance |
| Recovery | `ingest → diagnose → repair → review` | An initial precision failure was diagnosed at the evidence-fixture layer, repaired without changing the semantic formula, and independently reviewed |
| Adapt / Operate | `review → release` for the local demo | The release decision was bounded to local Python demonstration evidence; distributed runtime proof remained out of scope |
| Improve | `learn` | A candidate lesson about high-precision SAS coefficient export was recorded for later human promotion |

## Example acceptance result

| Measure | Demonstration result |
|---|---:|
| Governed records | 50 |
| Missing expected keys | 0 |
| Extra produced keys | 0 |
| Maximum linear-predictor delta | `2.72655e-11` |
| Maximum probability delta | `6.77780e-12` |
| Separately approved absolute tolerance | `1.0e-10` |
| Failures at the approved tolerance | 0 |

The values above are a historical teaching example only. They are not template defaults and are deliberately absent from `config/tieout.yaml`.

## What the example proved

The run established **local Python semantic-core demonstration parity for the governed 50 records**. It showed that requirements, ADRs, canonical trace and mapping artifacts, generated code, tests, evidence, recovery, review, and learning could be connected through durable state and human gates.

## What the example did not prove

It did not prove full-population parity, PySpark or another selected runtime, distributed partition behavior, cluster configuration, performance, scalability, operational monitoring, or production readiness.

## Suggested presentation sequence

```text
SAS business problem
    ↓
interviewed and approved intent
    ↓
PRD / module SPEC / ADR
    ↓
canonical trace / policy registry / semantic IR
    ↓
generated backend-neutral Python
    ↓
governed 50-record test and tie-out
    ↓
FAIL → diagnose → repair → independent review
    ↓
local-demo release decision and bounded learning
```

The most important teaching point is not that an agent generated code. It is that **the agent could not legitimately proceed without approved artifacts, deterministic evidence, and explicit human decisions—and it knew when to stop**.

## Assets intentionally not published

```text
SAS programs and includes
SAS logs and LST output
raw or prepared business data
coefficients and expected predictions
generated Python implementation
generated tests and fixtures
run-state JSON
tie-out detail and evidence bundles
review and release artifacts
cluster logs or credentials
```

Anyone using this repository should begin with their own local `intake/` files and `/start-migration new <MODULE-ID>`.
