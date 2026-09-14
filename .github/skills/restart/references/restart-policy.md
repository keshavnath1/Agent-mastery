# Restart Policy

## Purpose

A restart creates a new auditable run from source intake without deleting or legitimizing prior experimental work.

## Classification

| Class | Typical paths | Restart treatment |
|---|---|---|
| Authoritative raw input | `intake/sas/`, `intake/logs/`, `intake/lst/`, approved CSVs | Preserve byte-for-byte and verify hashes |
| Project machinery | `AGENTS.md`, prompts, skills, schemas, scripts, workflow config, and separately approved project-level contracts such as `config/tieout.yaml` | Preserve at the approved commit and verify contract hashes |
| Historical run evidence | `artifacts/run_state/`, prior review and evidence bundles | Preserve and mark terminal where applicable |
| Unapproved experiment | Generated code, candidate fixtures, unapproved tests and evidence | Archive with provenance; never silently reuse |
| Approved artifact | Approved PRD, SPEC, ADR, oracle, implementation | Do not demote or move without the owning change process |

## Required state transition

```text
existing run → ABANDONED_BY_USER_RESET
new run → intake / READY / attempts 0
```

The new run must cite the reset plan, previous run ID, source manifest, protected hashes, approved project-level contract hashes, and start commit.

## Two-step authorization

1. `PROPOSED`: classify paths, calculate hashes, and show exact moves. No mutation is allowed.
2. `APPROVED`: execute only the approved moves and state transitions, verify hashes, write the result, and stop.

## Forbidden actions

Never delete prior run state, rewrite Git history, modify source inputs, execute supplied code, approve requirements or architecture, reuse candidate implementation as accepted work, or advance beyond intake.
