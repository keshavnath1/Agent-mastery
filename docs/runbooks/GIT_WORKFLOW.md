# Git and Worktree Runbook

## Template baseline

The reusable branch contains only framework machinery and documentation. Do not commit local source intake, generated implementation, fixtures, predictions, run evidence, or cluster logs to the public template branch.

Create a separate migration branch or repository for an actual module. Commit accepted artifacts in small, reviewable checkpoints only after the corresponding deterministic and human gates pass.

## Stage checkpoints

Use the active module ID in focused commit messages:

```text
intake(MODULE-01): inventory approved source packet
spec(MODULE-01): approve observable behavior
adr(MODULE-01): select semantic and runtime boundaries
trace(MODULE-01): reconstruct SAS behavior
map(MODULE-01): register behavior ownership
model(MODULE-01): add semantic IR
gen(MODULE-01): implement semantic core
test(MODULE-01): add approved verification assets
validate(MODULE-01): record bounded behavior evidence
adapt(MODULE-01): add selected-runtime adapter
review(MODULE-01): accept bounded evidence
release(MODULE-01): record human decision
```

Do not combine a specification, oracle, key, expected-output, tolerance, or evaluator change with an implementation repair.

## Isolated repair

Create one worktree for one approved diagnosis:

```bash
git worktree add ../migration-wt-<run-id> -b repair/<run-id>
cd ../migration-wt-<run-id>
```

The repair commit may touch only the diagnosed owning layer and its regression test. The maker must not approve its own repair. After independent review, merge normally; never force-push or rewrite shared history.

## Protected evidence

Expected outputs, tolerances, evaluators, PRDs, specifications, ADRs, contracts, and source intake are protected during implementation repair. If one must change, open a separate human-approved requirements or evidence-contract lane.

## Stop and clean up

After merge or rejection:

```bash
git worktree remove ../migration-wt-<run-id>
git branch -d repair/<run-id>   # only after merge
git branch -D repair/<run-id>   # only after explicit rejection or abandonment
```

Do not delete a worktree containing uncommitted evidence or an unreviewed repair.
