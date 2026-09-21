---
name: orchestrate
description: Control migration start, resume, restart, stage order, durable run state, attempt limits, artifact handoffs, and human gates. Use whenever a prompt starts, continues, recovers, or restarts a module.
---

# Orchestrate

## Trigger

Use whenever a user prompt requests `new`, `resume`, `restart`, stage continuation, failure recovery, or review. Read `AGENTS.md` and `config/workflow.yaml` before selecting work.

## Required inputs

- Explicit user intent and module ID.
- Latest durable run-state JSON, if one exists.
- Workflow transition contract.
- Previous stage artifact, hash, and gate result.
- Protected and mutable path policy.

## Workflow

1. Classify the user intent as `new`, `resume`, `restart`, `continue`, `recover`, or `review`.
2. Read the latest run state and verify it against `config/workflow.yaml`.
3. Confirm the prior required artifact exists at its canonical path and that its recorded hash and gate result are valid.
4. Select exactly one permitted skill. For restart, select only `restart`. For a failed gate, open or resume the bounded recovery loop.
5. Record the selected skill, inputs, expected canonical output, mutable paths, protected paths, attempt count, and required human gate.
6. Invoke the selected skill. Deterministic tools may be used by that skill; do not ask the user to run them manually.
7. Require the skill to write and verify its named artifact and return `PASS`, `FAIL`, or `BLOCKED`.
8. Update durable state atomically. Stop at every human gate and after every skill invocation.
9. Derive the next permitted command from the updated state. Write a complete `Copy/paste next` Copilot message using actual module, run, artifact path, hash, approval scope, one permitted skill, and stop point. For `FAIL` or `BLOCKED`, route to the earliest owning recovery step instead of normal progression.
10. End with the complete Stage Result block in `docs/runbooks/STAGE_CONTRACT.md`.
11. For learning proposals, enforce `learn → learn_review → learn_promotion`. Authorize `review` only at `learn_review`; after an `ACCEPT` review, write `learn_promotion / PENDING_HUMAN_APPROVAL` bound to the proposal ID, review ID, and candidate commit, then stop. Record `APPROVED` or `REJECTED` only after the human explicitly replies.

## Canonical outputs

Orchestrate writes only durable control records under `artifacts/run_state/`. It references specialist artifacts by canonical path and hash; it never duplicates their content.

## Verification

- Transition is allowed by `config/workflow.yaml`.
- Exactly one specialist skill ran.
- Required input artifact and output artifact are versioned and hash-addressed.
- Protected paths did not change.
- Human gates were not crossed automatically.
- A learning promotion state names the exact subject, independent review, candidate commit, human actor, and decision timestamp.
- Restart stopped at `intake / READY`.
- `Next action` explains the required human action in plain language.
- `Copy/paste next` is complete, uses actual known identifiers and hashes, invokes no more than one specialist skill, and matches durable state.
- Missing hashes produce a request-for-hash message rather than fabricated approval wording.

## Boundaries

Do not perform specialist analysis, generate code, approve evidence, change protected artifacts, skip a stage, cross a human gate, or declare release. A generated approval message is a proposed user action and must never be recorded as approval until the human sends it. Never treat a free-text agent field as human approval. Do not convert user-facing prompts into large workflow documents; prompts route and skills execute.

## Stop conditions

Stop on missing or contradictory state, invalid transition, missing artifact, hash mismatch, dirty protected path, unavailable decision owner, repeated failure without new evidence, or exhausted attempt limit.
