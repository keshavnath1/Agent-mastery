---
name: import
description: Evaluate and selectively import compatible patterns from multiple sealed bundles into the target workspace. Use only after bundle review and target PRD, SPEC, and ADR approval.
---

# Import

## Trigger

Use only when durable state authorizes optional import and candidate bundles have passed independent review. Read `AGENTS.md`, target PRD/SPEC/ADRs, and `references/multi-bundle-compatibility.md`.

## Required inputs

- One or more sealed candidate bundles and hashes.
- Approved target PRD, module SPEC, migration profile, and ADRs.
- Compatibility-matrix schema and exact human pattern selection.
- Mutable/protected path policy and clean Git baseline.

## Workflow

1. Verify every bundle's integrity, provenance, source ADRs, licensing, evidence status, and approval state.
2. Classify patterns by responsibility and runtime family.
3. Compare source assumptions and constraints with the target SPEC and ADRs.
4. Detect incompatible assumptions, duplicate semantic owners, conflicting templates, unsupported runtime dependencies, and unmeasured performance claims.
5. Write and validate a multi-bundle compatibility matrix. Show selected, rejected, deferred, and unresolved patterns with reasons.
6. Produce an exact import preview containing source bundle, source hash, target path, operation, ownership, validation, and rollback plan.
7. Stop for human selection and approval. Do not change the target while the matrix is `PROPOSED`.
8. After approval, import only selected assets in an isolated branch or worktree, record origin metadata, run static target validation, and create a rollback commit.
9. Write the import report and stop. Do not invoke `trace`, `map`, or `generate` automatically.

## Output artifacts

```text
artifacts/patterns/imports/<import-id>/compatibility_matrix.yaml
artifacts/patterns/imports/<import-id>/import_preview.yaml
artifacts/patterns/imports/<import-id>/import_report.md
```

## Verification

- All bundle hashes and source ADR references resolve.
- No responsibility has multiple active semantic owners.
- Imported patterns comply with target SPEC and ADRs.
- No unselected or protected file changed.
- Origin metadata and rollback commit exist.
- Target static validation passes.

## Boundaries

Never import blindly, select on source popularity alone, treat source performance as target proof, modify protected evidence, import an unapproved bundle, activate incompatible runtimes, or let an adapter duplicate semantic formulas.

## Stop conditions

Stop on failed integrity, incompatible assumptions, duplicate ownership, missing target ADR, unresolved licensing, secret detection, missing human selection, dirty baseline, protected-path change, or failed target validation.
