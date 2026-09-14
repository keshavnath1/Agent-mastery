# Local Execution Runbook

## Clean-template checks

```bash
python3 scripts/project.py validate
python3 scripts/project.py smoke
python3 scripts/project.py status
```

These commands validate repository architecture only. A clean checkout has no generated semantic implementation or migration test suite.

## After approved generation

When durable state authorizes `generate`, place the backend-neutral semantic implementation under `src/sas_migration/semantic/`. When `test` is authorized, create module-owned verification assets under a clearly named subdirectory of `tests/generated/`.

The active skill—not the user—runs the deterministic checks required by the stage contract. Local execution proves only the behaviors, records, and metrics covered by the approved evidence contract. It does not automatically prove the complete source population, a selected distributed runtime, cluster configuration, performance, scalability, or production readiness.
