# Behavior Mapping Contract

## Authority precedence

Apply mapping authority in this order:

```text
approved PRD/SPEC → approved target ADRs → map procedure → optional taxonomy or pattern catalog
```

A taxonomy or harvested pattern may refine an approved decision; it must not replace, narrow, or contradict that decision. A missing optional taxonomy is not by itself a blocking condition.

## Dependency graph

Build column-level and dataset-level lineage from the canonical trace and cited source. Include derived columns, joins, sort/BY dependencies, retained state, macro-produced behavior, model inputs, and final outputs.

## Behavior blocks

Each registry entry must describe one coherent responsibility and contain:

- Stable behavior ID.
- Source paths, line/block citations, and exact excerpt hash.
- Input and output datasets/columns.
- Dependencies and required ordering.
- Stateful constructs and reset boundaries.
- Complexity: `LOW`, `MEDIUM`, or `HIGH`.
- Candidate patterns with provenance and applicability.
- Selected target responsibility and pattern, when justified.
- One semantic owner, optional adapter owner, and test owner.
- Deferred or unresolved reason.

## Pattern and taxonomy selection

Treat matching taxonomies and pattern catalogs as optional refinements. Evaluate multiple bundles together when supplied, identify incompatible assumptions, and reject duplicate semantic owners. Activate LP Emulator taxonomy and Golden Rules only when an approved target ADR explicitly selects LP Emulator; their mere presence in the workspace does not make them applicable.

When no matching runtime taxonomy exists, map each business behavior to a runtime-neutral semantic responsibility and record the adapter boundary selected by the ADR. Keep unsupported runtime implementation details unresolved rather than inventing them. A runtime adapter may own transport, partitioning, serialization, execution, and output integration; it must not independently own business formulas.

## Completion

Every traced behavior must be mapped, deferred with an explicit reason, or unresolved with a blocking question. Each business formula must have exactly one implementation owner. A registry with silent omissions or a taxonomy that contradicts the ADR cannot pass.
