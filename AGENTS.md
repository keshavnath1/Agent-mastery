# Agent Operating Contract

## Mission

Preserve approved SAS business behavior while moving execution through a backend-neutral semantic core to an approved runtime. Prefer evidence, reversible changes, and explicit uncertainty over plausible completion claims.

## Clean-template state

This branch contains project machinery only. It has no active module, approved PRD, module SPEC, target ADR, oracle, generated implementation, test fixture, run state, or evidence. Files under `examples/` are documentation-only teaching material and are never authoritative inputs for a new migration.

## Mandatory read order

1. `README.md`
2. `config/project.yaml`
3. `config/migration_profile.yaml`
4. `config/workflow.yaml`
5. `docs/PRD.md` after `specify` creates it
6. `docs/CAPABILITY_MAP.md` after `specify` creates it
7. The active module specification and approved ADRs
8. The latest run state under `artifacts/run_state/`
9. The triggered skill under `.github/skills/`

## Canonical skill sequence

```text
interview → specify → decide
→ harvest/import when reuse is needed
→ trace → map → model
→ generate → test → validate
→ adapt → ingest → review → release
→ learn
```

A user-facing prompt invokes `orchestrate`, which reads durable state and authorizes exactly one specialist skill. Every skill writes one named artifact, verifies it, records `PASS`, `FAIL`, or `BLOCKED`, and stops. A failed gate activates the bounded `ingest → diagnose → repair → review` recovery loop. `/start-migration restart` invokes only `restart`, preserves history, and stops at `intake / READY`.

`harvest` and `import` run only when approved source workspaces are supplied. `adapt` and runtime-evidence `ingest` run only when the approved scope includes a selected runtime. A skill is not executed merely to demonstrate that it exists.

## Authority boundaries

| Role | Allowed | Forbidden |
|---|---|---|
| Analyst | Interview, specify, trace, map, model | Change implementation or expected evidence |
| Maker | Generate, adapt, repair one owning layer | Change PRD, ADR, expected output, tolerance, evaluator, or lock |
| Explorer | Inspect and diagnose evidence | Edit implementation |
| Checker | Execute deterministic validation and review | Repair while reviewing |
| Orchestrator | Enforce sequence, state, and limits | Approve evidence or release |
| Human approver | Approve intent, PRD/SPEC, ADRs, evidence contracts, repair integration, merge, release, and learning promotion | Delegate accountability to an agent |

## Protected paths

An implementation or repair task must not modify these paths unless the task is explicitly a separately approved specification or evidence-contract change:

```text
docs/PRD.md
docs/CAPABILITY_MAP.md
docs/specs/
docs/adrs/
config/tieout.yaml
contracts/
intake/
artifacts/evidence/oracle/
stage1_extraction/output/execution_trace.json
policy/policy_registry.yaml
```

Never edit source files under `intake/`. Never execute untrusted SAS, notebook, shell, or binary attachments during intake. Raw and reference data are local by default and must not be force-added to Git.

## Specification and evidence contracts

Source code and examples do not define business intent. `interview` records the human's intended outcome and boundary. `specify` creates the PRD, capability map, and module SPEC. `decide` records architecture choices in ADRs. Only then may trace, mapping, modeling, generation, and testing proceed.

`config/tieout.yaml` begins as `UNAPPROVED_TEMPLATE`. The owning requirements process must define and obtain human approval for keys, metrics, deterministic fixture/coverage policy, immutable intake and SAS-oracle path/hash/representation, generated-output producer, comparison/tolerance rationale, privacy limits, and proof boundaries. `test` must create a schema-valid governed fixture manifest containing selector/source/input hashes, source observations, approved transformations, mandatory coverage assertions, privacy-safe selection reasons, and the selected-key digest, then present the completed contract for approval. `validate` must execute the generic keyed tie-out runner whenever local parity is required; unit tests or file existence cannot substitute for schema-valid `tieout_result.json`, generated `tieout_summary.md`, and `evidence.json`. An implementation, validator, repair, reviewer, or example must never invent or relax these values to obtain `PASS`.

## Stage contract

Prompts are thin routers. Every prompt must read durable state through `orchestrate`, invoke exactly one permitted skill, and stop at human gates. Every skill must state its trigger, inputs, workflow, canonical output, verification, boundaries, red flags, and stop conditions. Every stage ends with the complete Stage Result in `docs/runbooks/STAGE_CONTRACT.md`.

The result must include a plain-language `Next action` and an exact `Copy/paste next` Copilot message using the current module, run, artifact path, SHA-256, approval scope, one permitted skill, and stop point. If required information is unavailable, request it without advancing rather than inventing it.

Canonical compatibility artifacts are:

```text
trace → stage1_extraction/output/execution_trace.json
map   → policy/policy_registry.yaml
```

Reference canonical artifacts by path and hash; never maintain competing editable copies.

## Governed learning memory

The `learn` stage may compile accepted migration outcomes into an audit-safe observation, a candidate pattern, and at most one atomic skill-change proposal. Follow `docs/learning/WIKI_CONTRACT.md` and validate these artifacts with `scripts/validate_learning_memory.py`.

The learning memory is advisory. It cannot override the PRD, SPEC, ADR, tie-out contract, oracle lock, expected output, tolerance, evaluator, review, or human decision. Ordinary migration skills must not browse it as a hidden requirements source. Record observable actions, results, paths, hashes, and attributable decisions; never persist private chain-of-thought, secrets, raw business data, or unredacted mismatch values.

A single incident may become a regression case but not a reusable rule. Pattern promotion requires at least two independently linked and hash-verified run observations, structured fixture/oracle/evaluator/model/runtime/population context, explicit applicability and `does_not_prove` boundaries, architecture and normal and pressure validation against frozen evaluator hashes, independent review, rollback history, and human approval. Revalidate every model, runtime, population, and production context; success in local Python must not be generalized to PySpark, Ray, Cython, full population, distributed performance, or production readiness.

A skill proposal must resolve real Git commits and an exact patch, and `git diff` must change exactly one declared `SKILL.md`. Evaluator or governance changes require a separate approved baseline commit. Promotion follows `learn → learn_review → learn_promotion`; the final durable state must bind the proposal or pattern, independent review, candidate commit, attributable human approver, and timestamp.

## Evidence rules

1. Work on the earliest failed gate.
2. Use one hypothesis and one owning-layer change per repair.
3. Use an isolated Git worktree for each repair.
4. The maker cannot change expected evidence or evaluators.
5. The checker cannot repair while reviewing.
6. Stop after three repair attempts or two repeats of the same failure without new evidence.
7. File existence is not proof of success; execute the relevant deterministic validator.
8. When local tie-out is requested, `interview` must present `GOVERNED_SAMPLE_50`, `FULL_POPULATION`, `PHASED_50_THEN_FULL`, and `CUSTOM_GOVERNED_SAMPLE`; the human selects one. Never default from file size, prior examples, or convenience.
9. A local parity claim requires an approved `config/tieout.yaml`; the selected population and phase; locked intake, selector/source/input, fixture, and oracle hashes; passed mandatory coverage assertions; a matching selected-key digest; and schema-valid PASS artifacts from `scripts/run_tieout.py`. A phased sample PASS does not satisfy its full-population follow-up gate.
10. Preserve every failed and retried evidence artifact with hashes and lineage; never overwrite a failure or relabel it as PASS.
11. Independent review must rerun the frozen command, and release metrics must be derived from reviewed evidence rather than copied by hand.
12. Do not claim semantic parity, selected-runtime proof, oracle lock, ROI, release, or completion without corresponding approved evidence.
13. State proof boundaries explicitly; sample evidence does not prove unselected records, and local evidence does not automatically prove full-population or distributed behavior.
14. Preserve rejected learning proposals and their evidence; a higher aggregate evaluation score cannot compensate for a weakened governance control.

## Git rules

Use small commits named by stage and module, for example:

```text
spec(MODULE-01): define approved behavior
model(MODULE-01): add semantic IR
fix(MODULE-01): correct one owning layer
review(MODULE-01): accept bounded evidence
```

Do not rewrite shared history, force-push, or combine evidence-contract changes with implementation repairs. A lock, tolerance, expected output, or evaluator change requires a separate human-approved commit.

## Agent-owned deterministic commands

These commands are tools used by active skills; users normally invoke repository prompts in Copilot Agent Mode.

```bash
python3 scripts/project.py validate
python3 scripts/project.py intake
python3 scripts/project.py status
python3 scripts/project.py tieout --run-id <run-id> --attempt-id <attempt-id>
python3 scripts/project.py learning-validate --all
python3 scripts/validate_agent_architecture.py
```

## Stop conditions

Stop and request human input when required source artifacts are missing, the specification is ambiguous, the target runtime conflicts with an ADR, a protected artifact must change, evidence is contradictory, a retry limit is reached, a required hash is missing, or a human approval gate is pending.
