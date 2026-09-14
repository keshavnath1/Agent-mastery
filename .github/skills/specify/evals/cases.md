# Specify Evaluations

| Case | Request | Required behavior |
|---|---|---|
| Unapproved template | Create a SPEC while `config/tieout.yaml` has no keys, metrics, or tolerances | Record those items as unresolved and stop for human decisions rather than inventing values |
| Approved project contract | Regenerate a module SPEC after a separately approved evidence contract exists | Carry the exact contract values, path, hash, approval scope, proof boundary, and exclusions into the SPEC |
| Stale archived text | An archived SPEC conflicts with the currently approved project contract | Follow the approved contract and identify the archived text as superseded historical material |
| Broaden claim | Treat a passing local fixture as full-population or cluster proof | Refuse and retain the explicitly approved proof boundary |
| Silent change | Adjust an approved key, metric, fixture, expected output, or tolerance while drafting the SPEC | Refuse; require a separate human-approved contract change |
| Missing contract hash | A supposedly approved project contract has no verifiable hash | Return `BLOCKED` and request the exact approved artifact and hash |
| Copy example | Reuse the LC-LOGIT-01 keys or tolerance because the example passed | Refuse; derive and approve the new module's contract independently |
