# Capability Map: <MODULE-ID>

**Status:** DRAFT — human approval required
**PRD:** `<path and SHA-256>`

| Capability ID | Outcome | Inputs | Owning skill | Output artifact | Exit gate | Dependencies |
|---|---|---|---|---|---|---|
| C01 | Confirm migration intent | Interview answers and intake manifest | `interview` | Interview decisions | Human approval | None |
| C02 | Define testable behavior | Approved interview decisions | `specify` | PRD, capability map, module SPEC | Human approval | C01 |
| C03 | Select architecture | Approved requirements | `decide` | ADR | Human approval | C02 |
| C04 | Reconstruct source behavior | Approved source artifacts | `trace` | Canonical execution trace | Deterministic validation | C03 |
| C05 | Map responsibilities | Approved trace and ADR | `map` | Canonical policy registry | Deterministic validation | C04 |
| C06 | Define semantic contract | Approved mapping | `model` | Semantic IR | Deterministic validation | C05 |
| C07 | Build semantic implementation | Approved SPEC, ADR, and semantic IR | `generate` | Generated implementation | Deterministic validation | C06 |
| C08 | Build verification assets | Generated implementation and approved evidence contract | `test` | Tests and fixtures | Deterministic validation | C07 |
| C09 | Prove approved behavior | Frozen evidence contract and expected outputs | `validate` | Evidence bundle | PASS / FAIL / BLOCKED | C08 |
| C10 | Adapt and operate when required | Approved runtime ADR and local evidence | `adapt`, `ingest`, `review`, `release` | Adapter, runtime evidence, review, release packet | Human release decision | C09 |
| C11 | Promote reusable learning | Accepted independent evidence | `learn` | Candidate learning record | Human promotion decision | C10 |

Customize this map to the actual SAS problem. Add, remove, or split capabilities only through the approved specification process. Optional reuse stages (`harvest`, `import`) and selected-runtime stages execute only when their prerequisites and approved scope require them.
