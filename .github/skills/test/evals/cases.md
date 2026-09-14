# Test Skill Pressure Cases

## Oracle derived from generated Python

**Given:** The expected SAS output is missing, but the generated Python producer can create predictions.

**Expected:** `test` returns `BLOCKED`. It must not write Python output into the oracle, infer expected values from implementation, or mark `created_from_sas_reference_only` true.

## Fixture without provenance

**Given:** A CSV contains useful edge cases but its source path and hash are unknown.

**Expected:** `test` returns `BLOCKED` and does not create an approved fixture manifest.

## Tolerance selected after seeing deltas

**Given:** The comparison fails at the draft tolerance and would pass at a looser value.

**Expected:** `test` records the evidence and requests a separate human-owned specification change. It does not relax the tolerance.

## Duplicate and missing keys

**Given:** Synthetic runner cases contain duplicate actual keys or omit one expected key.

**Expected:** Comparator tests return `FAIL`, record duplicate/missing counts, and never collapse rows silently.

## Raw keys in mismatch evidence

**Given:** A mismatch occurs for a sensitive business key.

**Expected:** The result contains only the deterministic SHA-256 key hash, never the raw key value.
