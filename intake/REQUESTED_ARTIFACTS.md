# Requested Source Artifacts

Supply only the artifacts relevant to the SAS problem being migrated. Preserve original names, contents, and relationships. The interview and specification stages determine which inputs become authoritative.

## Priority 1 — source reconstruction

| Place under | Supply | Notes |
|---|---|---|
| `intake/sas/` | Main SAS programs | Preserve original filenames and ordering |
| `intake/sas/` | Included macros and `%include` files | Preserve relative relationships when possible |
| `intake/logs/` | Matching execution logs | Prefer the exact runs that produced trusted outputs |
| `intake/lst/` | Matching listing output | Include procedure output, warnings, errors, parameters, and control totals when available |
| `intake/data/` | Run manifests and control totals | Record row counts, keys, rejects, status, and provenance |

## Priority 2 — behavior validation

| Place under | Supply | Notes |
|---|---|---|
| `intake/data/` | Approved input or prepared-input fixture | The human must approve keys and coverage boundaries |
| `intake/data/` | Trusted expected-output files | Preserve source values and provenance |
| `intake/data/` | Parameter, lookup, format, or class-level files | Supply every external dependency that affects behavior |
| `intake/data/` | Numeric and categorical summaries | Useful for population, schema, and preparation reconciliation |
| `intake/data/` | Approved acceptance manifest | Define what records and outputs are in scope without inventing tolerances |

The exact evidence depends on the SAS workload. A scoring program may need coefficients and keyed predictions; an ETL, report, forecast, optimization, or simulation program will require a different contract.

## Priority 3 — runtime and reusable patterns

| Place under | Supply | Notes |
|---|---|---|
| `intake/patterns/` | Approved source-workspace bundle or source ADRs | Include provenance, assumptions, code, tests, templates, and measured evidence |
| `cluster_evidence/incoming/` | Driver and executor logs | Supply only after an approved runtime execution |
| `cluster_evidence/incoming/` | Runtime configuration | Include source commit, environment/image, scheduler configuration, and parameters |
| `cluster_evidence/incoming/` | Input/output manifests and metrics | Preserve original files unchanged |

## Safety and repository rules

Do not commit credentials, private keys, tokens, unrestricted production extracts, raw predictions, or proprietary source to the public template branch. The `intake/` contents are ignored by Git by default. Do not rename or edit source artifacts merely to make an intake gate pass. Large or restricted data may be represented by an approved manifest plus a smaller governed fixture.

After copying files, start through GitHub Copilot Agent Mode:

```text
/start-migration new <MODULE-ID>

Start with intake readiness only. Invoke exactly one authorized skill, produce the complete Stage Result, and stop.
```

The intake skill may invoke deterministic inventory and hashing tools internally. It must not execute the supplied SAS or other untrusted attachments.
