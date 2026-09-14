# Cluster Evidence Runbook

The first cluster run is manual. Record the Git commit, runtime profile, pod template, executor image, input manifest, output manifest, driver log, executor-log summary, and metrics. Copy original files to `cluster_evidence/incoming/`; normalization writes to `cluster_evidence/normalized/` and never edits the originals.

A cluster failure activates `ingest → diagnose → repair → review`. One failed gate, one hypothesis, and one owning-layer change are allowed per repair attempt.
