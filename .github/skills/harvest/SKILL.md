---
name: harvest
description: Reverse-engineer reusable patterns from one or more read-only source workspaces using source ADRs, code, tests, and measured evidence. Use when approved production work may inform the target migration.
---

# Harvest

## Trigger

Use only when durable run state authorizes optional pattern harvesting or the user invokes `/seed-production-patterns`. Read `AGENTS.md`, the target SPEC/ADRs, and `references/adr-aware-harvest.md`.

## Required inputs

- Read-only source workspace and pinned commit.
- Active and superseded source ADRs.
- Explicit extraction scope and licensing/provenance policy.
- Referenced implementation, tests, examples, and runtime evidence.
- Target-independent bundle schema and performance-evidence contract.

## Workflow

1. Inventory all candidate workspaces, commits, ADRs, modules, tests, templates, and evidence.
2. Trace each candidate pattern from source ADR to implementation, tests, and observed runtime behavior.
3. Separate observed invariants, measured claims, source-specific assumptions, inferred rationale, and unsupported hypotheses.
4. Record applicability requirements, counterexamples, conflicts, licensing, secrets, and operational dependencies.
5. Classify patterns by responsibility and runtime family: semantic Python, LP Emulator, PySpark, Ray, Cython acceleration, testing/evidence, deployment, or other approved taxonomy.
6. Package each pattern with hashes, provenance, source citations, templates, rules, tests, and negative cases.
7. Validate each bundle against `schemas/pattern_bundle.schema.json`, run integrity and secret checks, seal it, and mark it `CANDIDATE`.
8. Stop for independent review. Do not import or modify the target workspace.

## Output artifacts

```text
artifacts/patterns/candidates/<bundle-id>/bundle.yaml
artifacts/patterns/candidates/<bundle-id>/manifest.yaml
```

Multiple bundles may be produced in one authorized harvest. Each remains independently versioned and sealed.

## Verification

- Source commit and ADR references resolve.
- Code/test/evidence citations and hashes resolve.
- Performance claims are measured or explicitly unverified.
- Applicability, counterexamples, licensing, and secrets are addressed.
- Bundle schema and negative cases pass.
- Source and target workspaces remain unchanged.

## Boundaries

Never modify source workspaces, fabricate missing ADR rationale, present inferred rationale as approved, claim performance without measurement, copy secrets or restricted data, import into the target, or mark a bundle approved.

## Stop conditions

Stop on missing commit, unavailable source ADR or approved inferred-rationale process, unresolved licensing, absent tests for a claimed invariant, missing performance evidence for a performance claim, secret detection, or unclear pattern ownership.
