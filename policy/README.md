# Canonical Stage 2 Output

The `map` skill creates the authoritative artifact here:

```text
policy_registry.yaml
```

Do not create or edit that file manually. `/run-stage2` routes through durable state to `map`, which consumes the approved canonical trace, applies only ADR-authorized taxonomies and patterns, writes the YAML, validates its schema, records its hash, and stops for review. No duplicate editable registry is maintained elsewhere.
