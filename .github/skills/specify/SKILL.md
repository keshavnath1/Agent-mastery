---
name: specify
description: Create or refine the PRD, capability map, module specification, and executable draft evidence contract. Use after interview decisions are recorded and before implementation.
---

# Specify

## Trigger

Use when durable run state authorizes `specify`. Read `AGENTS.md`, `config/workflow.yaml`, the approved interview decisions, and the intake manifest.

## Required inputs

Approved migration profile, intake manifest, business context, available SAS reference outputs, and any separately approved project-level contracts.

## Workflow

1. State the outcome, user problem, scope, exclusions, invariants, commands, and success criteria.
2. Split the work into independently testable capabilities and assign stable behavior IDs.
3. For every required parity claim, define keys, governed fixture policy and coverage assertions, immutable intake-manifest hash, immutable SAS oracle path/hash/format/representation, expected and actual columns, comparison mode, human-approved tolerance, producer entry point, and proof boundary.
4. Record the human decision source and rationale for comparison modes and tolerances; observed data may inform the decision but cannot silently define acceptance.
5. Materialize those decisions in `config/tieout.yaml` using `contracts/tieout_contract.schema.json`; keep status `DRAFT` until the intake, fixture, oracle, selector, comparison, decision-basis, and exact contract hashes receive human approval.
6. Carry any separately approved contract values and limitations into the PRD and module SPEC without broadening the claim.
7. Record unknown keys, oracle files, metrics, tolerances, producer behavior, and owners as unresolved; do not create an empty parity contract and later call validation complete.
8. Validate the PRD, capability map, module SPEC, and draft tie-out contract, then request human approval.

## Output artifact

Updated `docs/PRD.md`, `docs/CAPABILITY_MAP.md`, module SPEC, and schema-valid draft `config/tieout.yaml`.

## Verification

Every required behavior maps to a deterministic unit, contract, parity, or runtime check. A local parity requirement has a complete executable draft contract, not only prose. No open decision is disguised as fact.

## Boundaries and red flags

Do not write implementation code, derive expected outputs from generated Python, invent keys or tolerances, mark the oracle lock approved, or broaden the proof boundary. Red flags include missing oracle provenance, a shell-string producer command, unbounded execution, mutable expected evidence, and parity listed in the SPEC without a matching contract entry.

## Stop conditions

Stop when acceptance behavior, keys, intake provenance, oracle ownership or representation, comparison metric, tolerance rationale, fixture coverage policy, producer entry point, or approver is ambiguous.
