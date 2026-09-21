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
| `contracts/` | JSON schemas for durable run state, semantic IR, governed fixtures, tie-out contracts/results, and evidence |
| `scripts/` | Framework validation, intake inventory, status, and the generic contract-driven tie-out runner used by active skills |
| `docs/runbooks/` | Intake, Git, local execution, cluster evidence, and Stage Result contracts |
| `docs/learning/` | Empty governed learning-memory index, evolution log, skill-impact tracker, contract, and pattern directory |
| `examples/lc-logit-01/` | Documentation-only example showing how one score-only migration used the framework |

## What is intentionally excluded

| Excluded | Where it belongs during a real migration |
|---|---|
| SAS source, includes, logs, and LST files | Local `intake/` folders; ignored by Git by default |
| Input, prepared, coefficient, and expected-output CSVs | Local `intake/data/`; ignored by Git by default |
| Generated Python semantic or adapter code | Created by the approved `generate` or `adapt` stage |
| Generated unit, contract, parity, and fixture files | Created by the approved `test` stage |
| Run state, trace, policy registry, evidence, reviews, and releases | Created on a dedicated migration branch; deliberately absent from this public template |
| Real learning observations, active patterns, and skill-change proposals | Created by `learn` from accepted evidence on a governed program branch |
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

## Governed learning memory

The `learn` stage now provides a persistent, cross-migration memory without creating an autonomous self-modifying agent:

```text
accepted evidence → audit-safe observation → independent recurrence?
    → candidate pattern → one-skill proposal
    → frozen architecture + normal + pressure validation
    → independent rerun/review → durable human promotion gate
```

The learning memory is an **advisory layer**, not another source of business truth. PRD, SPEC, ADR, tie-out contracts, oracle locks, evidence, and human decisions remain authoritative. A reusable pattern links and hash-verifies at least two observations with structured recurrence context, explicit applicability, prohibited generalizations, and proof limitations. A proposal resolves real Git commits, verifies an exact one-skill diff and patch, freezes evaluator hashes and commands, preserves result files, requires a different checker, and stops at `learn_promotion / PENDING_HUMAN_APPROVAL`. Promotion then requires an authenticated approved GitHub review on the exact candidate commit. The proposal cannot change expected outputs, tolerances, evaluators, approval gates, or a second skill to obtain PASS.

The repository stores only observable events and evidence references—never private chain-of-thought, secrets, raw customer data, or unredacted prediction values. See [`docs/learning/WIKI_CONTRACT.md`](docs/learning/WIKI_CONTRACT.md) and [`docs/runbooks/GOVERNED_LEARNING.md`](docs/runbooks/GOVERNED_LEARNING.md).

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

## How parity and tie-out are created

Copying SAS files and reference CSVs into `intake/` does not immediately run parity. If the user requests tie-out, `interview` first presents a human choice:

| Choice | Meaning |
|---|---|
| `GOVERNED_SAMPLE_50` | Fast, deterministic 50-record demonstration; PASS proves only the selected governed sample. |
| `FULL_POPULATION` | Compare every eligible keyed record; requires a complete oracle plus bounded compute/runtime feasibility. |
| `PHASED_50_THEN_FULL` | Run the 50-record gate first, then require a separate full-population contract and approval. |
| `CUSTOM_GOVERNED_SAMPLE` | Use a human-selected count with deterministic selection and mandatory coverage assertions. |

The agent recommends an option with trade-offs but never selects it. The workflow must then approve an executable evidence contract:

```text
interview records the human-selected population, current phase, oracle, and proof goal
    ↓
specify freezes population/follow-up obligations, intake/oracle provenance, keys, coverage policy, metrics, tolerance rationale, producer, and proof boundary
    ↓
generate creates the Python semantic core and actual-output producer
    ↓
test creates a deterministic selector, governed fixture manifest and coverage assertions, locks every source/oracle hash, and tests the generic comparator
    ↓
human approves the exact tie-out contract and hashes
    ↓
validate runs the generic keyed tie-out and emits detailed result, human-readable summary, and PASS / FAIL / BLOCKED evidence
```

The active `validate` skill invokes `python3 scripts/project.py tieout --run-id <run-id> --attempt-id <attempt-id>` internally. Users should continue using Copilot prompts rather than running this helper manually. The runner is module-neutral: it reads only the approved `config/tieout.yaml`; verifies intake, selector, source, input, fixture, and oracle hashes; requires mandatory coverage assertions and the selected-key digest; runs the declared producer without a shell; detects duplicate/missing/extra keys; applies every configured comparison; suppresses raw mismatch values; and writes schema-valid `tieout_result.json`, generated `tieout_summary.md`, and `evidence.json`.

See [`docs/runbooks/LOCAL_PARITY.md`](docs/runbooks/LOCAL_PARITY.md). An unapproved population choice or incomplete tie-out contract must return `BLOCKED`; unit tests alone cannot be presented as parity. A phased 50-record PASS keeps the full-population gate open.

A concise Copilot start request is:

```text
/start-migration new <MODULE-ID>

Inspect the private files under intake. I want SAS-to-Python migration with keyed tie-out. Present the tie-out population choices, recommend one with trade-offs, execute exactly one authorized skill, and stop at every human gate.
```

## Canonical artifacts

| Owning skill | Canonical artifact |
|---|---|
| `trace` | `stage1_extraction/output/execution_trace.json` |
| `map` | `policy/policy_registry.yaml` |
| `model` | `artifacts/semantic_ir/<module>.json` |
| `validate` | Attempt-specific `tieout_result.json`, generated `tieout_summary.md`, and `evidence.json` under `artifacts/evidence/runs/<run-id>/attempts/<attempt-id>/` when local parity is required |
| `review` | `artifacts/reviews/<run-id>.md` |
| `release` | `artifacts/releases/<run-id>/release_packet.md` |
| `learn` | Observation under `artifacts/learning/observations/`, candidate pattern under `docs/learning/patterns/`, proposal under `artifacts/learning/proposals/`, or independent review under `artifacts/learning/reviews/` |

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
python scripts/smoke_test.py
```

A fresh template checkout should pass structural and architecture validation plus synthetic generic tie-out cases for PASS, numerical/key failure, failed coverage, stale provenance, selection-digest mismatch, producer failure/timeout, determinism, and unapproved contracts while containing no active module, no generated implementation, and no real run evidence.

## Next reading

Read the following in order:

1. [`AGENTS.md`](AGENTS.md) for authority and execution rules.
2. [`config/workflow.yaml`](config/workflow.yaml) for acts, gates, and artifact paths.
3. [`docs/runbooks/STAGE_CONTRACT.md`](docs/runbooks/STAGE_CONTRACT.md) for the standard Stage Result.
4. [`docs/runbooks/INTAKE.md`](docs/runbooks/INTAKE.md) for local source onboarding.
5. [`docs/runbooks/LOCAL_PARITY.md`](docs/runbooks/LOCAL_PARITY.md) for contract-driven SAS-to-Python tie-out.
6. [`docs/runbooks/GOVERNED_LEARNING.md`](docs/runbooks/GOVERNED_LEARNING.md) for cross-migration learning and human promotion.
7. [`examples/lc-logit-01/README.md`](examples/lc-logit-01/README.md) for the documentation-only example.
