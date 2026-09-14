---
description: Open or continue a bounded recovery loop at the earliest failed gate without editing implementation.
argument-hint: "[optional failure evidence path]"
---
Read `AGENTS.md`, `config/workflow.yaml`, the latest run-state JSON, and the failed gate. Invoke `orchestrate`. If evidence is not normalized, invoke only `ingest`, write the normalized evidence artifact, and stop. If normalized evidence already exists, invoke only `diagnose`, produce one failure class, one evidence-cited hypothesis, one owning layer, and a proposed loop contract, then stop for approval. Never invoke `repair` or modify implementation in this response.
