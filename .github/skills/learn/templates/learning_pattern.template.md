---
schema_version: "1.0"
record_status: TEMPLATE
pattern_id: PATTERN-TEMPLATE-001
status: TEMPLATE
title: Replace with an evidence-backed pattern title
summary: Replace with a concise synthesis; this template is not reusable knowledge.
consolidated_by:
  identity: template-author
  role: analyst
occurrences:
  - observation_id: OBS-TEMPLATE-001
    observation_path: artifacts/learning/observations/OBS-TEMPLATE-001.json
    observation_sha256: "0000000000000000000000000000000000000000000000000000000000000000"
    run_id: RUN-TEMPLATE-001
    module_id: MODULE-TEMPLATE-001
    context:
      source_commit: "0000000000000000000000000000000000000000"
      source_platform: replace-source
      migration_mode: replace-mode
      semantic_boundary: replace-boundary
      run_state:
        path: artifacts/run_state/RUN-TEMPLATE-001.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
      fixture: null
      oracle: null
      expected_output: null
      evaluator_manifest:
        path: REPLACE/WITH/EVALUATOR-MANIFEST-001.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
      result:
        path: REPLACE/WITH/RESULT-001.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
      agent_model: replace-model
      target_runtime: replace-runtime
      population_scope: replace-population
  - observation_id: OBS-TEMPLATE-002
    observation_path: artifacts/learning/observations/OBS-TEMPLATE-002.json
    observation_sha256: "0000000000000000000000000000000000000000000000000000000000000000"
    run_id: RUN-TEMPLATE-002
    module_id: MODULE-TEMPLATE-002
    context:
      source_commit: "0000000000000000000000000000000000000000"
      source_platform: replace-source
      migration_mode: replace-mode
      semantic_boundary: replace-boundary
      run_state:
        path: artifacts/run_state/RUN-TEMPLATE-002.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
      fixture: null
      oracle: null
      expected_output: null
      evaluator_manifest:
        path: REPLACE/WITH/EVALUATOR-MANIFEST-002.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
      result:
        path: REPLACE/WITH/RESULT-002.json
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"
      agent_model: replace-model
      target_runtime: replace-runtime
      population_scope: replace-population
independence_review:
  reviewer:
    identity: template-checker
    role: checker
  reviewed_at: "2000-01-01T00:00:00Z"
  conclusion: INSUFFICIENT
  rationale: This inert template has no independent evidence and cannot be promoted.
applicability:
  source_platforms:
    - replace-source
  migration_modes:
    - replace-mode
  semantic_boundaries:
    - replace-boundary
  target_runtimes:
    - replace-runtime
  model_families:
    - replace-model
  population_scopes:
    - replace-population
  required_preconditions:
    - Replace all template values with evidence-backed preconditions.
does_not_prove:
  - This inert template proves nothing.
prohibited_generalizations:
  - Do not copy template values into an active migration.
candidate_skill_targets: []
validation_required:
  architecture: true
  normal: true
  pressure: true
  independent_review: true
promotion:
  human_decision: PENDING
  run_state_path: null
  run_state_sha256: null
  promotion_commit: null
  github_review: null
sensitivity:
  public_template_safe: true
  contains_raw_business_data: false
  contains_secrets: false
  contains_chain_of_thought: false
  reviewer:
    identity: template-privacy-checker
    role: checker
  reviewed_at: "2000-01-01T00:00:00Z"
---

# Replace with the pattern title

## Observable symptoms

Describe only evidence-backed symptoms and cite observation IDs.

## Evidence-backed strategy

Describe the smallest strategy supported by independent occurrences.

## Unsuccessful or rejected interventions

Record failed or rejected approaches so they are not silently repeated.

## Applicability and preconditions

Explain the exact source, semantic, runtime, population, data, and model boundaries.

## Does not prove

State all unproven populations, runtimes, model transfers, performance claims, and production conditions.

## Candidate skill impact

Name at most one skill per proposal and explain the hypothesized improvement.

## Human decision

Record the independent review and durable human promotion or rejection gate.
