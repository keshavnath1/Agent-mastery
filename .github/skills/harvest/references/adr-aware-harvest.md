# ADR-Aware Harvesting

A source ADR explains why a pattern exists in its original context. It is evidence, not authority over the target project. Harvest active and superseded ADRs, referenced code, tests, runtime evidence, assumptions, alternatives, consequences, and counterexamples. When no ADR exists, label reconstructed rationale `INFERRED_NOT_APPROVED` and require human review before the bundle becomes import-eligible.

Each pattern must preserve the chain:

```text
source commit → source ADR → code → tests → runtime evidence → applicability → bundle hash
```

The target PRD, SPEC, and ADR later decide whether the pattern may be imported. Source success never proves target compatibility.
