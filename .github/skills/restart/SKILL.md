---
name: restart
description: Plan and execute a human-approved restart of an existing migration module while preserving raw inputs, Git history, and prior run evidence. Use only when the user explicitly requests restart rather than resume.
---

# Restart

## Trigger

Use only after an explicit user request to restart an existing module. Read `AGENTS.md`, the workflow contract, the latest run state, and `references/restart-policy.md` before proposing changes.

## Required inputs

- Module ID and restart reason.
- Current Git status and commit.
- All run-state records for the module.
- Protected-path and artifact-ownership policy.
- Source-intake manifest and hashes.
- Separately approved project-level contracts and hashes, including `config/tieout.yaml` when applicable.
- Archive root and reset-plan schema.

## Workflow

1. Classify existing files as authoritative raw input, project machinery, historical evidence, unapproved experiment, or current approved artifact. Preserve separately approved project-level contracts as project machinery rather than archiving them with run-generated specifications.
2. Compare protected source hashes with the intake manifest and verify approved project-level contract hashes against the start commit.
3. Create a reset plan from `templates/reset_plan.template.yaml` and validate it against `schemas/reset_plan.schema.json`.
4. Record the previous run, proposed terminal status, archive destinations, new run ID, and paths that must not change.
5. Stop and request explicit human approval. Do not mutate files or run state while the plan is `PROPOSED`.
6. After approval, move only approved post-intake artifacts to the versioned archive, preserve Git history, mark the previous run `ABANDONED_BY_USER_RESET`, and create a new run at `intake / READY`.
7. Recompute protected hashes and verify that raw inputs are unchanged.
8. Write a restart result and stop. Do not execute intake or any later skill.

## Output artifacts

```text
artifacts/restarts/<restart-id>/reset_plan.yaml
artifacts/restarts/<restart-id>/restart_result.md
artifacts/run_state/<new-run-id>.json
```

## Verification

- Reset-plan schema passes.
- Protected source hashes and approved project-level contract hashes match before and after.
- Previous run remains present and is terminal.
- New run begins at `intake / READY` with zero attempts.
- No migration, test, tie-out, generation, or cluster command ran.

## Boundaries

Never delete Git history, raw source, logs, LST files, input/reference CSVs, or prior run-state records. Never mark PRD, SPEC, ADR, implementation, evidence, or patterns approved. Never advance beyond `intake / READY`.

## Stop conditions

Stop on dirty or unexplained Git state, protected-hash mismatch, unresolved ownership, missing approval, archive collision, or any request to delete history or continue automatically.
