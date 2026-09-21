---
name: learn
description: Convert repeated independent migration evidence into governed learning observations, candidate reusable patterns, and atomic skill-change proposals. Use after completed incidents, reviews, or releases; never use it for autonomous self-promotion.
---

# Learn

## Trigger

Use this skill only when `learn` is the active stage in `artifacts/run_state/` after accepted incident, review, or release evidence exists. Read `AGENTS.md`, `docs/learning/WIKI_CONTRACT.md`, and the latest durable state before execution.

## Required inputs

Require accepted incident records, regression results, review decisions, recurrence evidence, source commits, and immutable artifact hashes. When proposing a change, require the current skill, a frozen evaluator set, an isolated Git worktree, and a named independent checker.

## Workflow

1. Copy `templates/learning_observation.template.json` and record one audit-safe observation under `artifacts/learning/observations/`. Include only observable actions, tool results, artifact paths and hashes, outcomes, failure classification, and attributable decisions. A checker other than the author performs the privacy review.
2. Validate the observation with `python3 scripts/project.py learning-validate --observation <path>`. The validator resolves every repository-relative path, rejects repository escape, requires files to exist, recomputes SHA-256 values, and scans structured content for private-reasoning and common secret markers.
3. Decide whether the behavior recurred in at least two independent run IDs. For each occurrence, link a validated observation and record source commit, fixture, oracle, expected-output, evaluator, model, runtime, and population context. Treat a single incident as a regression case. Treat identical or contaminated contexts as correlated. Require a checker other than the consolidator to record `INDEPENDENT` before proposing reuse.
4. When recurrence is sufficient, create or update one pattern from `templates/learning_pattern.template.md` under `docs/learning/patterns/`. Cite immutable evidence; state applicability, preconditions, rejected interventions, `does_not_prove`, and prohibited cross-model, cross-runtime, population, performance, and production generalizations. Claimed model, runtime, and population scopes cannot exceed occurrence evidence.
5. Update `docs/learning/index.md` and append the consolidation event to `docs/learning/evolution-log.md`. These pages are advisory navigation, not authority.
6. If a procedural change is warranted, copy `templates/skill_change_proposal.template.json` and propose the smallest change to exactly one `.github/skills/<skill>/SKILL.md` in an isolated worktree. Record existing baseline and candidate commits plus the exact `git diff --binary` patch. Do not change PRD, SPEC, ADR, tie-out contract, oracle, expected output, tolerance, evaluator, approval gate, or any second skill.
7. Freeze architecture, normal, and pressure evaluators by path and SHA-256 **before** the candidate change. If a new regression fixture is required, create and approve it in a separate evaluator-owned commit, then select that commit as the baseline. Run the frozen suites and preserve command arrays, exit codes, evaluator hashes, and result-file hashes. Do not edit, delete, or relax an evaluator inside the skill proposal.
8. Transition to `learn_review`. A checker who is not the proposal author copies `templates/learning_review.template.json`, independently reruns all three frozen suites, and writes `artifacts/learning/reviews/<review-id>.json`. The validator binds the author, reviewer, proposal ID, exact candidate commit, evaluator hashes, rerun outputs, and verdict.
9. Append the candidate, rejection, promotion, or rollback outcome to `docs/learning/skill-impact.md`; preserve the patch and evidence even when rejected. A rejected proposal must not be regenerated without new evidence.
10. After an `ACCEPT` review, orchestrate creates `learn_promotion / PENDING_HUMAN_APPROVAL` state and stops. Only the human's explicit reply plus an approved GitHub pull-request review on the exact candidate commit may produce an `APPROVED` durable gate record. Record repository, pull request, review ID, reviewer login, and reviewed commit; the validator resolves the authenticated review through `gh api` and binds it to the durable state before merge or promotion.

## Output artifact

Name exactly one primary output in the Stage Result:

- insufficient recurrence: `artifacts/learning/observations/<observation-id>.json`;
- evidenced reusable knowledge: `docs/learning/patterns/<pattern-id>.md`;
- validated procedural candidate: `artifacts/learning/proposals/<proposal-id>.json`;
- independent review: `artifacts/learning/reviews/<review-id>.json`.

Supporting index, log, evaluator result, patch, state, and impact-tracker changes must be listed separately in `Files changed`.

## Verification

The selected primary artifact must pass `scripts/validate_learning_memory.py`. The validator verifies repository containment, file existence, SHA-256 values, linked IDs, Git commit existence and ancestry, an exact one-skill Git diff, exact patch bytes, frozen evaluators and commands, validation outputs, checker independence, an authenticated GitHub approval, and the durable human gate. A higher score cannot compensate for a governance regression.

## Boundaries and red flags

The learning memory cannot override approved control-plane artifacts and must not be exposed to ordinary migration skills as a hidden requirement source. Do not promote a single incident, private production detail, model-specific workaround, local-runtime result, or unmeasured performance claim as a general rule. Red flags include self-attested PASS without files, absolute or escaping paths, invented hashes or commits, correlated evidence presented as recurrence, missing provenance, changed protected paths, self-authored expected output, evaluator relaxation, deleted rejected history, self-review, skipped promotion state, or agent-labeled human approval.

## Stop conditions

Stop with `BLOCKED` when recurrence, independence, provenance, privacy, applicability, Git diff, evaluator freeze, validation, checker independence, or human approval is insufficient. Preserve the observation and failure evidence; do not manufacture a pattern or broaden its scope.
