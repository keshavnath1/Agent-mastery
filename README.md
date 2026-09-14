# Agent-Mastery SAS Migration Template

This repository is a **clean-slate, specification-driven framework** for migrating a SAS workload to a backend-neutral Python semantic core and then, when required, to an approved execution runtime. It is designed for GitHub Copilot Agent Mode and uses small verb-based skills, durable artifacts, deterministic gates, bounded recovery, independent review, and explicit human approval.

> This branch contains the reusable migration machinery only. It intentionally contains **no SAS program, SAS log, LST output, business CSV, generated Python implementation, generated test fixture, prediction, run state, tie-out evidence, or cluster log**.

## What is included

| Included | Purpose |
|---|---|
| `AGENTS.md` | Repository-wide operating contract and authority boundaries |
| `.github/prompts/` | Short user-facing Copilot commands that route work |
| `.github/skills/` | Twenty lifecycle and recovery skills with references, schemas, templates, and evaluations |
| `config/workflow.yaml` | Machine-readable five-act lifecycle, gates, canonical artifacts, and recovery sequence |
| `contracts/` | JSON schemas for durable run state, evidence, and semantic IR |
| `scripts/` | Framework validation, intake inventory, and status helpers used by active skills |
| `docs/runbooks/` | Intake, Git, local execution, cluster evidence, and Stage Result contracts |
| `examples/lc-logit-01/` | Documentation-only example showing how one score-only migration used the framework |

## What is intentionally excluded

| Excluded | Where it belongs during a real migration |
|---|---|
| SAS source, includes, logs, and LST files | Local `intake/` folders; ignored by Git by default |
| Input, prepared, coefficient, and expected-output CSVs | Local `intake/data/`; ignored by Git by default |
| Generated Python semantic or adapter code | Created by the approved `generate` or `adapt` stage |
| Generated unit, contract, parity, and fixture files | Created by the approved `test` stage |
| Run state, trace, policy registry, evidence, reviews, and releases | Created on a dedicated migration branch; deliberately absent from this public template |
| Incoming cluster logs and manifests | Local `cluster_evidence/incoming/`; ignored by Git by default |

## Lifecycle model

```text
USER PROMPT
    ↓
orchestrate reads durable state
    ↓
exactly one authorized skill
    ↓
named artifact + PASS / FAIL / BLOCKED
    ↓
state update + copy-ready next message
    ↓
STOP
```

The five lifecycle acts are:

```text
Align
  interview → specify → decide

Reuse / Reconstruct
  harvest → import → trace → map → model
  (harvest and import are optional)

Build / Prove
  generate → test → validate

Adapt / Operate
  adapt → ingest → review → release
  (runtime stages execute only when the approved scope requires them)

Improve
  learn
```

A failed or blocked gate opens the bounded recovery loop:

```text
ingest → diagnose → repair → review → retry earliest failed gate
```

Human approval gates are mandatory. An agent may prepare evidence and recommend a decision, but it may not approve intent, requirements, architecture, evidence changes, repairs, release, or learning promotion on the human's behalf.

## Clean-checkout quick start

### 1. Clone the reusable branch

```bash
git clone --branch agent-mastery-template \
  https://github.com/keshavnath1/Agent-mastery.git
cd Agent-mastery
```

### 2. Create the local Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
python scripts/validate_project.py
python scripts/validate_agent_architecture.py
```

These commands validate only the framework. They do not execute SAS or perform a migration.

### 3. Add your source material locally

Place your own files in the matching folders:

```text
intake/
├── sas/       # SAS programs and includes
├── logs/      # SAS execution logs
├── lst/       # SAS listing output
├── data/      # input and trusted reference/output CSVs
└── patterns/  # optional reusable pattern bundles or source ADRs
```

The template ignores these contents by default. Do not force-add business data, credentials, raw predictions, or proprietary code to Git.

### 4. Open the repository in VS Code

Use **GitHub Copilot Agent Mode** and begin with a short router prompt:

```text
/start-migration new <MODULE-ID>

I want to migrate the SAS problem represented by the files under intake. Start with intake readiness only. Invoke exactly one authorized skill, produce the Stage Result, and stop.
```

Replace `<MODULE-ID>` with a neutral identifier such as `CUSTOMER-RISK-01` or `FORECAST-01`.

### 5. Follow the generated next message

Every Stage Result ends with:

```text
Next permitted command: ...
Next action: ...
Copy/paste next:
...
```

Review the artifact and SHA-256 before pasting the next approval. Do not use `/run-next-stage` as permission to cross more than one stage or human gate.

## Common Copilot entry points

| Prompt | Use |
|---|---|
| `/start-migration new <MODULE-ID>` | Start a new migration at intake readiness |
| `/start-migration resume <MODULE-ID>` | Read durable state and report the next authorized skill |
| `/start-migration restart <MODULE-ID>` | Propose an auditable reset plan and stop for approval |
| `/run-next-stage <MODULE-ID>` | Execute exactly one currently authorized lifecycle skill |
| `/run-stage1 <MODULE-ID>` | Compatibility alias for canonical trace extraction |
| `/run-stage2 <MODULE-ID>` | Compatibility alias for canonical policy mapping |
| `/seed-production-patterns ...` | Harvest reusable patterns from approved source workspaces |
| `/analyze-failure <MODULE-ID>` | Enter the bounded recovery loop after `FAIL` or `BLOCKED` |
| `/review-evidence <MODULE-ID>` | Perform independent read-only review |
| `/ingest-cluster-log <MODULE-ID>` | Normalize manually supplied runtime or cluster evidence |

The prompt is only the router. The selected skill owns the procedure, artifact, validation, state update, and stop behavior.

## Canonical artifacts

| Owning skill | Canonical artifact |
|---|---|
| `trace` | `stage1_extraction/output/execution_trace.json` |
| `map` | `policy/policy_registry.yaml` |
| `model` | `artifacts/semantic_ir/<module>.json` |
| `validate` | `artifacts/evidence/runs/<run-id>/evidence.json` |
| `review` | `artifacts/reviews/<run-id>.md` |
| `release` | `artifacts/releases/<run-id>/release_packet.md` |

Do not maintain competing editable copies of canonical artifacts. Reference them by repository-relative path and SHA-256.

## LC-LOGIT-01 example

The documentation under [`examples/lc-logit-01/`](examples/lc-logit-01/) describes a completed **50-record local demonstration** for a loan-risk logistic scoring use case. It shows the story, artifacts, gates, failure-recovery loop, and evidence boundary without distributing the original SAS, data, generated Python, fixtures, predictions, or run evidence.

The example proves only how the framework was applied. It is not an implementation starter and must not be treated as expected output for a new migration.

## Selected-runtime boundary

Local Python tests can establish semantic behavior on approved fixtures, but they do not automatically prove distributed execution, partition behavior, serialization, cluster configuration, performance, scalability, or production readiness. Those claims require an approved runtime ADR, a thin adapter, runtime evidence, independent review, and a separate release decision.

## Repository safety

The `.gitignore` protects local source intake, incoming runtime evidence, and common secret files. Generated code and lifecycle artifacts remain visible for review on a dedicated migration branch, while the clean-template validator rejects them from this reusable baseline. Before publishing any branch, inspect the staged diff and run a secret/data scan. Never force-add ignored business inputs merely to make a demonstration reproducible.

## Maintainer validation

```bash
python scripts/validate_project.py
python scripts/validate_agent_architecture.py
python -m unittest tests.architecture.test_agent_workflow
```

A fresh template checkout should pass these checks while containing no active module, no generated implementation, and no run evidence.

## Next reading

Read the following in order:

1. [`AGENTS.md`](AGENTS.md) for authority and execution rules.
2. [`config/workflow.yaml`](config/workflow.yaml) for acts, gates, and artifact paths.
3. [`docs/runbooks/STAGE_CONTRACT.md`](docs/runbooks/STAGE_CONTRACT.md) for the standard Stage Result.
4. [`docs/runbooks/INTAKE.md`](docs/runbooks/INTAKE.md) for local source onboarding.
5. [`examples/lc-logit-01/README.md`](examples/lc-logit-01/README.md) for the documentation-only example.
