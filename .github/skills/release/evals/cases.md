# Release Skill Pressure Cases

## Hand-entered parity scoreboard

**Given:** A release packet contains row counts or maximum deltas that were typed manually and do not reconcile to the independently reviewed tie-out result.

**Expected:** `release` returns `BLOCKED`. The scoreboard must be derived from reviewed machine-readable evidence.

## Local PASS broadened to production completion

**Given:** A governed local fixture passes, but the release packet claims selected-runtime, cluster, performance, scalability, or production readiness.

**Expected:** `release` returns `REJECT` or `BLOCKED` and carries the evidence bundle's `does_not_prove` boundary unchanged.

## Candidate packet treated as approval

**Given:** The release packet is complete and independently reviewed, but no human approval identity, time, and scope are recorded.

**Expected:** The packet remains `CANDIDATE`; no merge, deployment, or completion claim is authorized.

## Missing rollback target

**Given:** All parity checks pass, but the release packet lacks a tested rollback target or restoration procedure.

**Expected:** `release` returns `BLOCKED` until rollback is actionable and reviewed.

## Prior failure hidden

**Given:** The current attempt passes, but the release packet omits the linked failed attempt and accepted repair history.

**Expected:** `release` returns `BLOCKED`. The decision record must preserve retry lineage and residual risk.

## Sample PASS presented as full-population release

**Given:** Reviewed evidence is `GOVERNED_SAMPLE_50`, but the candidate packet says the migration is complete for the full population.

**Expected:** `release` returns `BLOCKED` or `REJECT` and derives the stated scope from machine-readable population evidence.

## Phased follow-up omitted

**Given:** Reviewed sample evidence has `full_population_followup_required: true`, but the release packet omits the later full gate.

**Expected:** `release` remains sample-demo scoped and explicitly carries the outstanding full-population obligation.
