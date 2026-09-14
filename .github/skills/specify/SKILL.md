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
2. Verify the approved interview decision for local tie-out and population: `GOVERNED_SAMPLE_50`, `FULL_POPULATION`, `PHASED_50_THEN_FULL`, or `CUSTOM_GOVERNED_SAMPLE`. Never infer or replace the choice.
3. Split the work into independently testable capabilities and assign stable behavior IDs.
4. For every required parity claim, define the selected population choice, current phase, record count, deterministic selection policy, full-population follow-up obligation, keys, governed fixture policy and coverage assertions, immutable intake-manifest hash, immutable SAS oracle path/hash/format/representation, expected and actual columns, comparison mode, human-approved tolerance, producer entry point, and proof boundary.
5. Record the human decision source and rationale for population, comparison modes, and tolerances; observed data may inform a recommendation but cannot silently define acceptance.
6. For `PHASED_50_THEN_FULL`, define two separate evidence gates. The first contract uses the 50-record sample phase and retains `full_population_followup_required: true`; its PASS cannot satisfy the later full-population contract or release claim.
7. Materialize those decisions in `config/tieout.yaml` using `contracts/tieout_contract.schema.json`; keep status `DRAFT` until the population, intake, fixture, oracle, selector, comparison, decision-basis, and exact contract hashes receive human approval.
8. Carry any separately approved contract values and limitations into the PRD and module SPEC without broadening the claim.
9. Record unknown population, keys, oracle files, metrics, tolerances, producer behavior, and owners as unresolved; do not create an empty parity contract and later call validation complete.
10. Validate the PRD, capability map, module SPEC, and draft tie-out contract, then request human approval.

## Output artifact

Updated `docs/PRD.md`, `docs/CAPABILITY_MAP.md`, module SPEC, and schema-valid draft `config/tieout.yaml`.

## Verification

Every required behavior maps to a deterministic unit, contract, parity, or runtime check. A local parity requirement has one human-selected population choice and a complete executable draft contract, not only prose. A phased choice exposes two independent gates. No open decision is disguised as fact.

## Boundaries and red flags

Do not write implementation code, derive expected outputs from generated Python, invent or change the tie-out population, invent keys or tolerances, mark the oracle lock approved, or broaden the proof boundary. Red flags include missing oracle provenance, a shell-string producer command, unbounded execution, mutable expected evidence, and parity listed in the SPEC without a matching contract entry.

## Stop conditions

Stop when the tie-out population choice, phase or follow-up obligation, acceptance behavior, keys, intake provenance, oracle ownership or representation, comparison metric, tolerance rationale, fixture coverage policy, producer entry point, or approver is ambiguous.
