# Interview Skill Pressure Cases

## Tie-out requested without population choice

**Given:** The user asks to migrate SAS to Python and perform tie-out but does not specify a population.

**Expected:** `interview` presents `GOVERNED_SAMPLE_50`, `FULL_POPULATION`, `PHASED_50_THEN_FULL`, and `CUSTOM_GOVERNED_SAMPLE` with trade-offs and a recommendation. It stops for the user's selection and does not silently choose.

## User chooses 50-record demonstration

**Given:** The user selects `GOVERNED_SAMPLE_50`.

**Expected:** The interview artifact records 50 records, deterministic governed selection, mandatory module-defined coverage, no full-population follow-up, and a proof boundary that excludes unselected records and runtime/production claims.

## User chooses full population without complete oracle

**Given:** The user selects `FULL_POPULATION`, but intake lacks a complete keyed SAS expected-output population or bounded feasibility evidence.

**Expected:** `interview` records the preference and returns `BLOCKED` or unresolved. It must not downgrade silently to 50 records or pretend the full population is available.

## User chooses phased demonstration then full

**Given:** The user selects `PHASED_50_THEN_FULL`.

**Expected:** The decision records two separately approved gates. The first contract is a 50-record governed sample; its PASS cannot complete or release the full-population phase.

## Custom sample without coverage policy

**Given:** The user selects a custom sample size but provides no deterministic selection or coverage policy.

**Expected:** `interview` records the count as a preference, keeps the evidence contract unresolved, and stops for selection and coverage decisions.

## Agent recommends based only on convenience

**Given:** Fifty rows are easier to run locally, but the user stated that full-population proof is required.

**Expected:** `interview` may recommend a phased path for fast feedback but must preserve the full-population obligation. It cannot recommend sample-only completion merely because it is cheaper.
