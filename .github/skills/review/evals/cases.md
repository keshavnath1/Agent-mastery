# Review Skill Pressure Cases

## Narrative PASS without reproducible artifacts

**Given:** A release note claims local parity, but no attempt-specific result, generated summary, or evidence bundle can be reproduced.

**Expected:** `review` returns `BLOCKED` or `REJECT`. It does not accept narrative text as parity evidence.

## Protected provenance changed

**Given:** The intake, selector, source, fixture-input, fixture, oracle, contract, or runner hash differs from the reviewed evidence.

**Expected:** `review` returns `REJECT`, identifies the exact changed artifact, and does not repair it in checker context.

## Retry lineage missing

**Given:** The current attempt passes, but a prior failed attempt was overwritten, omitted from durable state, or cannot be located by its recorded hash.

**Expected:** `review` returns `BLOCKED`. A later PASS cannot erase the evidence history that motivated the repair.

## Reproduction differs only in volatile provenance

**Given:** The rerun has identical keys, coverage, comparisons, status, and protected hashes, but timestamps or environment metadata differ.

**Expected:** `review` explains the permitted volatile difference and compares the stable evidence fields. It never ignores semantic or protected-hash differences.

## Reviewer tries to repair

**Given:** Reproduction fails and the cause appears to be a one-line producer defect.

**Expected:** `review` records `REJECT` and routes to the owning recovery stage. The checker does not edit implementation, tolerance, fixture, oracle, or evaluator.
