# LP Emulator Ten Golden Rules

**Status:** Candidate policy. It becomes applicable only when an approved target ADR selects the LP Emulator architecture and references this version.

| # | Rule |
|---:|---|
| 1 | Preserve every approved feature-engineering column name exactly unless the SPEC defines an explicit mapping. |
| 2 | Preserve approved business formulas and calculation order exactly. |
| 3 | Load model coefficients from an approved YAML/CSV artifact; never hard-code fitted values. |
| 4 | Translate SAS DATA-step iteration into vectorized NumPy where semantics permit, or explicit Python accumulation where state/order requires it. |
| 5 | Represent SAS BY-group processing as a single loan/group dictionary flowing through the composed module chain with explicit reset boundaries. |
| 6 | Avoid persistence of SAS-style intermediate datasets; pass approved in-memory state between semantic modules unless an ADR requires persistence. |
| 7 | Write output once at the end through the approved CSV/output writer. |
| 8 | Translate SAS macro orchestration into `ComposedModule` chaining with explicit module order and ownership. |
| 9 | Preserve approved SAS variable names as Python dictionary keys unless the SPEC defines a traceable mapping. |
| 10 | Preserve the approved output schema, keys, column semantics, types, and ordering policy. |

## Modern ownership safeguards

The backend-neutral Python semantic core owns business formulas. LP Emulator and PySpark components own composition, partition transport, schema conversion, serialization, and final writing; they must not maintain a separate implementation of scoring mathematics. Imported production patterns inform implementation but never override the module SPEC, target ADR, or protected evidence.

## Validation

A generated or imported module must cite the applicable rule IDs, source trace behavior IDs, policy-registry entries, tests, and approved exceptions. A rule conflict returns `BLOCKED`; it is not silently resolved by the generator.
