# SAS Trace Contract

## Source discovery

Inspect all authorized SAS programs, logs, and LST files. Prioritize intake paths and explicit user scope. Do not ask for files already present. Record each relative path and source hash.

## SAS program extraction

| Category | Required metadata |
|---|---|
| Program | Path, name, entry-point status, source hash |
| Macros | Definitions, parameters, `%mend`, `%include`, invocations, unresolved references |
| DATA steps | Output and input datasets; `SET`, `MERGE`, `UPDATE`, `MODIFY`; BY keys; `RETAIN`; `KEEP`; `DROP`; `WHERE`; arrays and loops |
| PROC SQL | Created table, input tables, join types and conditions, groups, ordering, calculated columns, pass-through SQL, remerge risk |
| Procedures | SORT, SUMMARY, MEANS, TRANSPOSE, APPEND, EXPORT, DATASETS, LOGISTIC, and other material procedures with inputs/outputs |
| Dependencies | LIBNAME, FILENAME, formats, informats, model files, configuration, environment variables |
| Stateful/risky behavior | `FIRST.`/`LAST.`, `RETAIN`, `LAG`, `DIF`, `CALL SYMPUT`, `SYMGET`, arrays, iterative loops, `MORT`, `INTCK`, `INTNX`, implicit ordering |

Preserve dataset, variable, macro, and format names exactly when determinable. Attach file and line or block citations to every material claim.

## Log and LST extraction

Extract execution metadata only:

- Observation counts and created datasets.
- CPU and elapsed runtime.
- Errors and warnings.
- Relevant notes: zero observations, implicit conversion, truncation, uninitialized variables, merge anomalies, missing values, sort behavior, invalid data, convergence, and export completion.
- Source-to-log relationship and contradictions.

Do not classify routine informational notes as errors. Do not copy loan/customer records or sensitive identifiers into the trace.

## Cross-program reconstruction

Record produced and consumed datasets, includes and macro call graph, execution order when evidenced, unresolved dependencies, and high-risk patterns with source citations.

## Quality gates

The trace must inventory every scoped source file, parse as valid JSON, preserve exact names, cite evidence, expose uncertainty, avoid invented behavior, contain no raw records, and contain no generated migration or extraction code.
