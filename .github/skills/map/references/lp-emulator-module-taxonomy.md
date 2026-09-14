# LP Emulator Module Taxonomy

Load this reference only when an approved target ADR selects the LP Emulator architecture.

| Module type | Responsibility | Typical SAS evidence | Complexity signal |
|---|---|---|---|
| `data_prep_lss` | Stateless feature engineering and deterministic row transformations | Simple DATA steps, formats, assignments, filters | Usually LOW or MEDIUM |
| `panel` | Loan/group-level stateful accumulation with explicit reset boundaries | `RETAIN`, BY groups, `FIRST.`/`LAST.`, `LAG`, running balances | Usually HIGH |
| `scoring` | Coefficient loading, ordered accumulation, link function, and score output | PROC LOGISTIC score equation, SQL/data-step accumulation | Usually HIGH |
| `composed` | Ordered composition of multiple approved modules | Macros or flows orchestrating preparation, panel, and scoring | Usually HIGH |
| `lss_flow` | Runtime entry, orchestration boundary, and one final output write | Final DATA/EXPORT step or job-level flow | LOW or MEDIUM, but operationally critical |

## Ownership rule

The backend-neutral Python semantic core owns business formulas. LP Emulator modules compose and execute that core. PySpark partition code, serialization, and output writing are adapter responsibilities and must not duplicate scoring formulas.

## Applicability rule

If the target ADR selects Ray, plain Python, Cython acceleration, or another runtime, load the corresponding approved pattern taxonomy instead. Preserve the canonical policy registry but do not force LP Emulator module names onto an incompatible architecture.
