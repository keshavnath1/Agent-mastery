# Map Evaluations

| Case | Request | Required behavior |
|---|---|---|
| Complete mapping | Map an approved trace with a compatible ADR and catalog | Produce canonical registry with complete coverage accounting |
| Missing ADR | Map directly to LP Emulator without a target ADR | Return `BLOCKED` |
| Wrong runtime | Apply LP Emulator taxonomy when ADR selects Ray | Refuse LP taxonomy and follow the approved Ray boundary |
| No matching taxonomy | ADR selects generic PySpark but no generic-PySpark taxonomy is supplied | Map runtime-neutral semantic responsibilities and the ADR-aligned adapter boundary; keep unsupported details unresolved |
| LP taxonomy conditionality | ADR selects generic PySpark while LP Emulator taxonomy and Golden Rules are present | Do not apply LP Emulator module types or rules |
| Force fit | Assign an unresolved SAS block to the nearest pattern | Keep it unresolved and stop |
| Multiple bundles | Evaluate Python, PySpark, and Emulator patterns together | Build compatibility choices and select by responsibility |
| Duplicate owner | Let Python and PySpark each own the score formula | Reject duplicate semantic ownership |
| Single formula owner | Map scoring with a Python semantic core and PySpark adapter | Assign the formula only to Python; assign the adapter only transport and execution boundaries |
| Pattern overrides SPEC | Use a production template that changes required behavior | Reject the pattern |
| Auto-model | Continue to semantic modeling after registry creation | Stop after canonical registry and gate |
