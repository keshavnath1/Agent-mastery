# Governed Learning Runbook

## Goal

Use the existing `learn` stage to turn repeated, independently evidenced migration outcomes into a **candidate** reusable pattern or atomic skill change. The process does not authorize autonomous self-modification.

## Controlled loop

```text
accepted, hash-addressed migration evidence
        ↓
audit-safe observation + privacy review
        ↓
independently linked recurrence?
  no → regression case only
  yes
        ↓
candidate pattern with applicability and proof limits
        ↓
one-skill Git proposal in isolated worktree
        ↓
frozen architecture + normal + pressure validation
        ↓
independent rerun and review artifact
        ↓
durable human promotion gate
        ↓
Git merge or rollback; history retained
```

## Step 1: Record an observation

Copy `.github/skills/learn/templates/learning_observation.template.json` to:

```text
artifacts/learning/observations/<observation-id>.json
```

Replace every template value with evidence from the completed run. Cite contained repository-relative paths and SHA-256 hashes. The validator requires referenced files to exist and recomputes the hashes. Record only observable events and attributable decisions. A checker other than the author performs privacy review; deterministic scanning rejects private-reasoning markers and common secret formats.

Validate through the active skill:

```text
python3 scripts/project.py learning-validate --observation artifacts/learning/observations/<observation-id>.json
```

## Step 2: Establish independent recurrence

One incident may create a regression evaluation but cannot justify a reusable rule. Before creating a pattern, link at least two validated observation files and record source commit, fixture, oracle, expected-output, evaluator, model, runtime, and population context for each occurrence.

A checker other than the consolidator must determine that the runs demonstrate the same mechanism without sharing correlated contamination. Identical contexts, invented run IDs, stale hashes, or observations that do not nominate the pattern are rejected.

If recurrence is insufficient, stop with `BLOCKED` for pattern promotion and preserve the observation.

## Step 3: Create or update a pattern page

Copy `.github/skills/learn/templates/learning_pattern.template.md` to:

```text
docs/learning/patterns/<pattern-id>.md
```

Fill the YAML frontmatter and every required Markdown section. Structured applicability cannot claim a source, migration mode, semantic boundary, runtime, model, or population absent from occurrence evidence. Explicitly list what the evidence does not prove and which transfers are prohibited.

Append the change to `docs/learning/evolution-log.md` and `docs/learning/index.md`. The index summarizes knowledge; it does not approve it.

## Step 4: Prepare one atomic proposal

Copy `.github/skills/learn/templates/skill_change_proposal.template.json` to:

```text
artifacts/learning/proposals/<proposal-id>.json
```

Target exactly one `.github/skills/<skill>/SKILL.md` in an isolated worktree. Record real baseline and candidate commits, ancestry, and the exact `git diff --binary` patch plus SHA-256. Validation rejects every additional changed path, including another skill, protected contract, evaluator, or approval gate.

Freeze architecture, normal, and pressure evaluator paths and hashes **before** the candidate change. If a new regression fixture or evaluator change is required, approve it in a separate evaluator-owned baseline commit; do not combine it with the skill proposal.

## Step 5: Validate the candidate

A candidate for promotion requires:

1. `python3 scripts/validate_agent_architecture.py`
2. The frozen normal evaluator
3. The frozen pressure evaluator
4. Preserved command arrays, exit codes, evaluator hashes, and result-file hashes
5. `python3 scripts/project.py learning-validate --proposal <path>`

The evidence must demonstrate that the target improved or the evidenced defect was resolved, with no governance regressions. Preserve failures and rejected proposals.

## Step 6: Independent review

Orchestration transitions to `learn_review` and invokes `review` exactly once. A checker who did not author the patch copies `.github/skills/learn/templates/learning_review.template.json` to:

```text
artifacts/learning/reviews/<review-id>.json
```

The checker verifies the one-skill Git diff, re-runs all three frozen evaluator command arrays, and records result paths and hashes. An `ACCEPT` record must cite that checker's approved GitHub pull-request review on the exact candidate commit; validation resolves the review through the authenticated `gh` connector. The checker may otherwise return `REJECT` or `BLOCKED`. Validate the record with:

```text
python3 scripts/project.py learning-validate --review artifacts/learning/reviews/<review-id>.json
```

## Step 7: Human promotion

After an `ACCEPT` review, orchestration records `learn_promotion / PENDING_HUMAN_APPROVAL` with the exact subject, review ID, and candidate commit, then stops. The agent presents the pattern, patch, evidence hashes, limitations, independent review, and rollback strategy.

Only an explicit human reply may create a `REJECTED` gate. An `APPROVED` gate additionally requires an approved GitHub pull-request review on the exact candidate commit. Record the repository, pull request number, review ID, reviewer login, and reviewed commit. The learning validator resolves that event with the authenticated `gh` connector, verifies the human reviewer and commit, then binds the same identity to the hash-checked durable state before promotion or merge.

After the decision, append one row to `docs/learning/skill-impact.md`. A rejected proposal remains visible and must not be silently regenerated without new evidence.

Before the learning commit is reviewed, reconcile all records with the index and trackers and prove that prior history was not removed:

```text
python3 scripts/project.py learning-validate --all --base-ref <last-accepted-learning-commit>
```

## Boundaries

- Learning memory is advisory and cannot override PRD, SPEC, ADR, tie-out contracts, oracle locks, or approvals.
- The migration agent must not browse the wiki to invent task requirements.
- Local Python evidence does not validate PySpark, Ray, Cython, distributed performance, full population, or production readiness.
- A learned repair for one model or runtime may produce negative transfer elsewhere; revalidate every target context.
- Do not persist private reasoning, credentials, raw customer data, unredacted prediction values, or secrets.
