# Canonical Stage 1 Output

The `trace` skill creates the authoritative artifact here:

```text
execution_trace.json
```

Do not create or edit that file manually. `/run-stage1` routes through durable state to `trace`, which loads the SAS trace reference, writes the JSON, validates its schema, records its hash, and stops for review. No duplicate editable trace is maintained elsewhere.
