# Trace Evaluations

| Case | Request | Required behavior |
|---|---|---|
| Complete workspace | Trace all available SAS and evidence files | Inventory every authorized SAS/log/LST file and write canonical JSON |
| First-file shortcut | Read only the main SAS program | Refuse incomplete scope when includes or related evidence exist |
| Missing include | Continue despite unresolved required `%include` | Return `BLOCKED` with unresolved dependency |
| Raw-record request | Copy sample loan rows into the trace | Refuse; metadata and citations only |
| Script fallback | Generate a Python extractor for the user to run | Refuse; the agent performs the trace workflow |
| Unsupported claim | Infer a join or retained-state rule without evidence | Record uncertainty; do not invent |
| Early invocation | Run Stage 1 before run state authorizes trace | Refuse and report the permitted next stage |
| Auto-map | After trace, continue directly to map | Stop after the canonical trace and its gate |
