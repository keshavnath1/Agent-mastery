# Governed Learning-Memory Contract

## Purpose

The learning memory preserves **evidence-backed knowledge across migrations** without changing approved business intent. It is a controlled compilation layer between completed migration evidence and executable skills.

> The learning memory may explain, connect, and recommend. It is never the source of truth for requirements, architecture, expected results, tolerances, or release decisions.

## Four-layer model

| Layer | Contents | Authority |
|---|---|---|
| Raw migration evidence | Stage results, run state, tests, tie-out attempts, reviews, release outcomes, and runtime evidence | Immutable observations of what happened |
| Authoritative control plane | Human-approved PRD, SPEC, ADR, tie-out contract, schemas, oracle locks, and approvals | Defines intent, boundaries, and acceptance |
| Persistent learning memory | Recurring patterns, rejected interventions, skill-impact history, applicability, and proof limitations | Advisory knowledge compiled from cited evidence |
| Executable skills | `SKILL.md`, scripts, templates, references, and deterministic validators | Procedures used only after governed promotion |

The layers must remain distinct. A learning pattern cannot override the control plane, and a migration agent must not use the learning wiki as a hidden alternate requirement source.

## Durable artifacts

| Artifact | Canonical path | Rule |
|---|---|---|
| Audit-safe observation | `artifacts/learning/observations/<observation-id>.json` | Record observable actions, existing evidence paths and hashes, outcomes, decisions, and independent privacy review |
| Pattern page | `docs/learning/patterns/<pattern-id>.md` | Link at least two validated observations and record structured recurrence context before proposal |
| Skill-change proposal | `artifacts/learning/proposals/<proposal-id>.json` | Resolve real commits, target exactly one skill, preserve the exact Git patch, and freeze evaluator hashes |
| Independent review | `artifacts/learning/reviews/<review-id>.json` | Bind a different checker, exact candidate commit, frozen reruns, outputs, and verdict |
| Evolution log | `docs/learning/evolution-log.md` | Append-only chronology of observations, pattern changes, and promotion decisions |
| Skill-impact tracker | `docs/learning/skill-impact.md` | Append-only history of accepted, rejected, and rolled-back proposals |

`stage1_extraction/output/execution_trace.json` remains the canonical reconstructed SAS behavior trace. Do not create a second generic `trace.json` for learning history.

`learning-validate --all` reconciles observations, patterns, proposals, and reviews against the index, evolution log, and impact tracker. Before accepting a learning commit, pass `--base-ref <last-accepted-learning-commit>` so the validator rejects deleted history lines.

## Observation policy

An observation may record the invoked skill, commands or tools used, artifact paths and hashes, PASS/FAIL/BLOCKED outcome, failure classification, repair or review result, and attributable human decisions. Referenced paths must be repository-relative, contained inside the repository, exist, and match their declared SHA-256. It must not record hidden chain-of-thought, credentials, secrets, proprietary raw data, or unredacted mismatch values. An independent privacy reviewer must be named.

A single incident is a **regression case**, not a reusable pattern. Preserve it as an observation and add a focused evaluation if appropriate.

## Pattern policy

A candidate reusable pattern must:

1. Cite at least two validated observation files with distinct run IDs and verified hashes.
2. Separate observable symptoms from root-cause hypotheses.
3. Record successful, unsuccessful, and rejected interventions.
4. Record source commit, fixture, oracle, expected-output, evaluator, model, runtime, and population context for each occurrence.
5. State what the evidence does not prove.
6. Limit structured applicability to contexts present in occurrence evidence and forbid unvalidated transfer.
7. Remain `CANDIDATE` or `PROPOSED` until a separately validated skill change is human-approved.

Recurrence is necessary but not sufficient. Repeated incidents caused by the same contaminated fixture, stale oracle, evaluator, expected output, model-specific behavior, or copied assumption are not independent evidence. A checker other than the consolidator must record the recurrence conclusion.

## Proposal and validation policy

A proposal must change **one skill only** in an isolated Git worktree. The validator resolves baseline and candidate commits, verifies ancestry, recomputes the patch hash, compares patch bytes with Git, and rejects a diff that changes anything except the declared `SKILL.md`. The maker may not change the PRD, SPEC, ADR, tie-out contract, oracle, expected output, tolerance, evaluator, approval gate, or second skill to obtain a better result.

Architecture, normal, and pressure evaluators are frozen by path and SHA-256 before the candidate change. Any new regression fixture or evaluator change belongs in a separate evaluator-owned and human-approved baseline commit. Every validation and independent rerun records the command array, exit code, evaluator hash, result path, and result hash.

Promotion requires all of the following:

- Architecture validation passes.
- Normal regression evaluations pass.
- Pressure evaluations pass.
- The evidenced target improves or the documented defect is resolved.
- No governance control regresses.
- An independent checker whose identity differs from the author reviews the exact candidate commit, reruns every frozen evaluator with the same command arrays, and emits a schema-valid review artifact. An `ACCEPT` verdict must be backed by that checker's authenticated approved GitHub review on the exact commit.
- The proposal records a rollback strategy and preserves rejected history.
- Orchestration records `learn_review` and then `learn_promotion / PENDING_HUMAN_APPROVAL`. Promotion requires an authenticated GitHub pull-request review with state `APPROVED` on the exact commit. The validator resolves the review ID through `gh api`, verifies the human login and commit, and binds that identity to the hash-verified durable gate record.

A higher aggregate score cannot compensate for a governance regression. Failed and rejected proposals remain in the impact tracker so they are not silently repeated.

## Access boundary

During normal migration execution, specialist skills read only their approved inputs and active procedures. They do not browse the learning memory to invent requirements or bypass skill triggering. The `learn` stage may read accepted evidence and the learning memory to consolidate patterns and prepare one bounded proposal.

## Clean-template boundary

This public template contains contracts, inert templates, validators, and empty indexes only. It must contain no real observations, active patterns, skill proposals, customer evidence, private run state, or generated implementation.

## Design sources

This governed adaptation draws on the persistent LLM-maintained wiki pattern and the WikiSkill raw/wiki/skill separation, while retaining the repository's stronger specification, evidence, Git, separation-of-duties, and human-promotion controls:

- [A pattern for building personal knowledge bases using LLMs](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [WikiSkill: Skill Evolution with Persistent Knowledge](https://arxiv.org/html/2608.27454v1)
