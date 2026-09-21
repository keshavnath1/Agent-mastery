#!/usr/bin/env python3
"""Validate the reusable agent-mastery template without executing migration work."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PROMPTS = {
    "start-migration.prompt.md",
    "restart-migration.prompt.md",
    "run-next-stage.prompt.md",
    "run-stage1.prompt.md",
    "run-stage2.prompt.md",
    "seed-production-patterns.prompt.md",
    "ingest-cluster-log.prompt.md",
    "analyze-failure.prompt.md",
    "review-evidence.prompt.md",
}

REQUIRED_SKILLS = {
    "orchestrate", "restart", "interview", "specify", "decide", "harvest",
    "import", "trace", "map", "model", "generate", "test", "validate",
    "adapt", "ingest", "diagnose", "repair", "review", "release", "learn",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def visible_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return [item for item in path.rglob("*") if item.is_file() and item.name != ".gitkeep"]


def main() -> int:
    errors: list[str] = []

    prompts_dir = ROOT / ".github" / "prompts"
    skills_dir = ROOT / ".github" / "skills"
    prompt_names = {path.name for path in prompts_dir.glob("*.md")}
    skill_names = {path.name for path in skills_dir.iterdir() if path.is_dir()}
    require(REQUIRED_PROMPTS <= prompt_names, f"Missing prompts: {sorted(REQUIRED_PROMPTS - prompt_names)}", errors)
    require(REQUIRED_SKILLS <= skill_names, f"Missing skills: {sorted(REQUIRED_SKILLS - skill_names)}", errors)

    project = yaml.safe_load(text("config/project.yaml"))
    require(project.get("status") == "TEMPLATE", "Project must begin in TEMPLATE status", errors)
    require(project.get("active_module") is None, "Clean template must not select an active module", errors)
    require(project.get("active_stage") is None, "Clean template must not select an active stage", errors)

    migration_profile = yaml.safe_load(text("config/migration_profile.yaml"))
    require(migration_profile.get("status") == "UNAPPROVED_TEMPLATE", "Migration profile must be unapproved", errors)
    require(migration_profile.get("module_id") is None, "Migration profile must not contain a module ID", errors)
    require(migration_profile.get("migration_mode") is None, "Migration mode must be chosen through interview", errors)
    require(migration_profile.get("selected_adapter") is None, "Template must not select a runtime adapter", errors)
    require(migration_profile.get("local_tieout_requested") is None, "Template must not assume local tie-out", errors)
    population = migration_profile.get("tieout_population", {})
    require(population.get("choice") is None and population.get("record_count") is None, "Template must not select a tie-out population", errors)
    require("tieout_population_choice" in migration_profile.get("human_approval_required", []), "Migration profile lacks the population-choice human gate", errors)

    tieout = yaml.safe_load(text("config/tieout.yaml"))
    tieout_schema = json.loads(text("contracts/tieout_contract.schema.json"))
    tieout_schema_errors = sorted(Draft202012Validator(tieout_schema).iter_errors(tieout), key=lambda item: list(item.absolute_path))
    require(not tieout_schema_errors, f"Tie-out template fails its schema: {[error.message for error in tieout_schema_errors[:5]]}", errors)
    require(tieout.get("status") == "UNAPPROVED_TEMPLATE", "Tie-out contract must be unapproved", errors)
    require(tieout.get("module_id") is None, "Tie-out contract must not contain a module ID", errors)
    require(tieout.get("scope", {}).get("population_choice") is None, "Tie-out template must not select a population", errors)
    require(tieout.get("scope", {}).get("current_phase") is None, "Tie-out template must not select a phase", errors)
    require(tieout.get("scope", {}).get("full_population_followup_required") is None, "Tie-out template must not infer a full-population obligation", errors)
    require(tieout.get("key_columns") == [], "Template must not invent tie-out keys", errors)
    require(tieout.get("intake_manifest", {}).get("path") is None, "Template must not select an intake manifest", errors)
    require(tieout.get("oracle", {}).get("path") is None, "Template must not select a SAS oracle", errors)
    require(tieout.get("oracle", {}).get("format") is None, "Template must not assume an oracle format", errors)
    require(tieout.get("decision_basis", {}).get("source") is None, "Template must not invent a tolerance decision source", errors)
    require(tieout.get("fixture_manifest", {}).get("path") is None, "Template must not select a parity fixture", errors)
    require(tieout.get("producer", {}).get("command") == [], "Template must not invent a producer command", errors)
    require(tieout.get("comparisons") == [], "Template must not invent metrics or tolerances", errors)
    require(tieout.get("output", {}).get("result_path") == "artifacts/evidence/runs/{run_id}/attempts/{attempt_id}/tieout_result.json", "Wrong generic tie-out result path", errors)
    require(tieout.get("output", {}).get("summary_path") == "artifacts/evidence/runs/{run_id}/attempts/{attempt_id}/tieout_summary.md", "Wrong generic tie-out summary path", errors)
    require(tieout.get("oracle_lock", {}).get("implementation_may_modify") is False, "Implementation must not modify the tie-out contract", errors)

    workflow = yaml.safe_load(text("config/workflow.yaml"))
    rules = workflow["control_rules"]
    require(rules["one_skill_per_prompt"] is True, "one_skill_per_prompt must be true", errors)
    require(rules["stop_at_human_gate"] is True, "stop_at_human_gate must be true", errors)
    require(rules["self_approval_forbidden"] is True, "self_approval_forbidden must be true", errors)
    require(rules["learning_memory_advisory_only"] is True, "Learning memory must remain advisory", errors)
    require(rules["learning_independent_run_minimum"] == 2, "Reusable learning must require two independent runs", errors)
    require(rules["learning_promotion_human_only"] is True, "Learning promotion must remain human-only", errors)
    require(workflow["canonical_artifacts"]["execution_trace"] == "stage1_extraction/output/execution_trace.json", "Wrong canonical trace path", errors)
    require(workflow["canonical_artifacts"]["policy_registry"] == "policy/policy_registry.yaml", "Wrong canonical policy registry path", errors)
    require(workflow["canonical_artifacts"]["tieout_contract"] == "config/tieout.yaml", "Wrong canonical tie-out path", errors)
    require(workflow["canonical_artifacts"]["tieout_result"] == "artifacts/evidence/runs/<run-id>/attempts/<attempt-id>/tieout_result.json", "Wrong canonical tie-out result path", errors)
    require(workflow["canonical_artifacts"]["tieout_summary"] == "artifacts/evidence/runs/<run-id>/attempts/<attempt-id>/tieout_summary.md", "Wrong canonical tie-out summary path", errors)
    require(workflow["canonical_artifacts"]["module_spec"] == "docs/specs/<module>.md", "Module SPEC path must be runtime-neutral", errors)
    require(workflow["canonical_artifacts"]["implementation"] == "src/sas_migration/semantic/", "Implementation path must be generic", errors)
    require(workflow["canonical_artifacts"]["learning_observation"] == "artifacts/learning/observations/<observation-id>.json", "Wrong learning observation path", errors)
    require(workflow["canonical_artifacts"]["learning_pattern"] == "docs/learning/patterns/<pattern-id>.md", "Wrong learning pattern path", errors)
    require(workflow["canonical_artifacts"]["skill_change_proposal"] == "artifacts/learning/proposals/<proposal-id>.json", "Wrong skill proposal path", errors)
    require(workflow["canonical_artifacts"]["learning_review"] == "artifacts/learning/reviews/<review-id>.json", "Wrong learning review path", errors)
    require({"next_permitted_command", "next_action", "copy_paste_next"} <= set(workflow["stage_result_fields"]), "Stage Result lacks copy-ready next-action fields", errors)

    expected_order = [
        ["interview", "specify", "decide"],
        ["harvest", "import", "trace", "map", "model"],
        ["generate", "test", "validate"],
        ["adapt", "ingest", "review", "release"],
        ["learn"],
    ]
    require([act["skills"] for act in workflow["acts"]] == expected_order, "Workflow act order differs from the lifecycle contract", errors)
    require(workflow["recovery_loop"]["sequence"] == ["ingest", "diagnose", "repair", "review"], "Recovery sequence is incorrect", errors)
    learning_control = workflow["learning_control"]
    require(learning_control["review_stage"] == "learn_review" and learning_control["promotion_stage"] == "learn_promotion", "Learning review or promotion stage is not explicit", errors)
    require(learning_control["transitions"][1]["status"] == "PENDING_HUMAN_APPROVAL", "Learning promotion does not stop at a pending human gate", errors)
    interview_gate = next((gate for gate in workflow["human_gates"] if gate.get("after") == "interview"), {})
    require("tie-out population" in interview_gate.get("approval", ""), "Interview gate lacks tie-out population approval", errors)

    trace_skill = text(".github/skills/trace/SKILL.md")
    map_skill = text(".github/skills/map/SKILL.md")
    map_contract = text(".github/skills/map/references/behavior-mapping-contract.md")
    map_pressure = text(".github/skills/map/evals/cases.md")
    orchestrate_skill = text(".github/skills/orchestrate/SKILL.md")
    orchestrate_pressure = text(".github/skills/orchestrate/evals/cases.md")
    stage_contract = text("docs/runbooks/STAGE_CONTRACT.md")
    interview_skill = text(".github/skills/interview/SKILL.md")
    interview_pressure = text(".github/skills/interview/evals/cases.md")
    start_prompt = text(".github/prompts/start-migration.prompt.md")
    specify_skill = text(".github/skills/specify/SKILL.md")
    generate_skill = text(".github/skills/generate/SKILL.md")
    test_skill = text(".github/skills/test/SKILL.md")
    validate_skill = text(".github/skills/validate/SKILL.md")
    review_skill = text(".github/skills/review/SKILL.md")
    release_skill = text(".github/skills/release/SKILL.md")
    restart_skill = text(".github/skills/restart/SKILL.md")
    learn_skill = text(".github/skills/learn/SKILL.md")
    learn_pressure = text(".github/skills/learn/evals/cases.md")
    learning_contract = text("docs/learning/WIKI_CONTRACT.md")
    tieout_runner = text("scripts/run_tieout.py")
    learning_validator = text("scripts/validate_learning_memory.py")

    require("stage1_extraction/output/execution_trace.json" in trace_skill, "Trace skill lacks canonical path", errors)
    require("artifacts/traces/<module>.json" not in trace_skill, "Trace skill retains a competing editable path", errors)
    require("policy/policy_registry.yaml" in map_skill, "Map skill lacks canonical path", errors)
    require("artifacts/plans/<module>-mapping.json" not in map_skill, "Map skill retains a competing editable path", errors)
    require("exactly one permitted skill" in orchestrate_skill, "Orchestrate lacks one-skill rule", errors)
    require("Copy/paste next" in orchestrate_skill, "Orchestrate lacks copy-ready next-message rule", errors)
    require("**Next action:**" in stage_contract, "Stage contract lacks plain-language next action", errors)
    require("**Copy/paste next:**" in stage_contract, "Stage contract lacks copy-ready next message", errors)
    require("Missing output hash" in orchestrate_pressure, "Orchestrate evaluations lack missing-hash coverage", errors)
    require("Recovery handoff" in orchestrate_pressure, "Orchestrate evaluations lack recovery coverage", errors)
    for choice in ["GOVERNED_SAMPLE_50", "FULL_POPULATION", "PHASED_50_THEN_FULL", "CUSTOM_GOVERNED_SAMPLE"]:
        require(choice in interview_skill and choice in start_prompt, f"Interview/start prompt lacks population choice {choice}", errors)
    require("Tie-out requested without population choice" in interview_pressure and "Phased sample contract" in text(".github/skills/test/evals/cases.md"), "Population-choice pressure coverage is incomplete", errors)
    require("config/tieout.yaml" in specify_skill and "tieout_contract.schema.json" in specify_skill and "full_population_followup_required" in specify_skill, "Specify does not materialize the population-aware draft tie-out contract", errors)
    require("producer entry point" in generate_skill and "never reads the SAS oracle" in generate_skill, "Generate does not provide an oracle-isolated parity producer", errors)
    require("fixture_manifest.schema.json" in test_skill and "coverage assertions" in test_skill and "selected-key digest" in test_skill, "Test lacks governed fixture coverage and selection controls", errors)
    require("scripts/project.py tieout" in validate_skill and "--attempt-id" in validate_skill and "tieout_summary.md" in validate_skill and "PHASED_50_THEN_FULL" in validate_skill and "retry" in validate_skill, "Validate lacks population-aware parity evidence and retry history", errors)
    require("reproduced `tieout_result.json`" in review_skill and "limitations" in review_skill, "Review does not independently reproduce parity evidence", errors)
    require("parity scoreboard" in release_skill and "reviewed machine-readable evidence" in release_skill and "does_not_prove" in release_skill, "Release does not derive its claim from reviewed evidence", errors)
    require("shell=False" in tieout_runner and "selected_keys_digest" in tieout_runner and "render_summary" in tieout_runner and "attempt_id" in tieout_runner and "include_values_in_evidence" in text("config/tieout.yaml"), "Generic tie-out runner lacks safe execution, selection, append-only summary, or privacy controls", errors)
    require("config/tieout.yaml" in restart_skill, "Restart does not account for approved tie-out contracts", errors)
    require("runtime-neutral semantic responsibilities" in map_skill, "Map skill lacks taxonomy-neutral fallback", errors)
    require("optional refinements" in map_contract, "Map contract does not make taxonomies optional", errors)
    require("explicitly selects LP Emulator" in map_contract, "Map contract lacks the LP Emulator ADR boundary", errors)
    require("No matching taxonomy" in map_pressure, "Map evaluations lack taxonomy-neutral fallback coverage", errors)
    require("Single formula owner" in map_pressure, "Map evaluations lack single formula-owner coverage", errors)
    require("at least two independent run IDs" in learn_skill and "exactly one" in learn_skill and "learn_promotion / PENDING_HUMAN_APPROVAL" in learn_skill, "Learn skill lacks recurrence, atomicity, or durable promotion controls", errors)
    require("Hidden reasoning capture" in learn_pressure and "Cross-model negative transfer" in learn_pressure and "Aggregate score masks regression" in learn_pressure, "Learn evaluations lack privacy, transfer, or governance pressure cases", errors)
    require("advisory" in learning_contract.lower() and "chain-of-thought" in learning_contract, "Learning contract lacks authority or privacy boundary", errors)
    require("two independent run IDs" in learning_validator and "SHA-256 mismatch" in learning_validator and "candidate diff must change exactly" in learning_validator and "proposal author cannot independently review" in learning_validator, "Learning validator lacks recurrence, provenance, Git-diff, or independence enforcement", errors)

    schema_paths = [
        ROOT / ".github/skills/trace/schemas/execution_trace.schema.json",
        ROOT / ".github/skills/map/schemas/policy_registry.schema.json",
        ROOT / ".github/skills/restart/schemas/reset_plan.schema.json",
        ROOT / ".github/skills/harvest/schemas/pattern_bundle.schema.json",
        ROOT / ".github/skills/import/schemas/compatibility_matrix.schema.json",
        ROOT / "contracts/tieout_contract.schema.json",
        ROOT / "contracts/tieout_result.schema.json",
        ROOT / "contracts/fixture_manifest.schema.json",
        ROOT / "contracts/evidence_bundle.schema.json",
        ROOT / "contracts/learning_observation.schema.json",
        ROOT / "contracts/learning_pattern.schema.json",
        ROOT / "contracts/learning_review.schema.json",
        ROOT / "contracts/skill_change_proposal.schema.json",
    ]
    for path in schema_paths:
        require(path.exists(), f"Missing schema: {path.relative_to(ROOT)}", errors)
        if path.exists():
            json.loads(path.read_text(encoding="utf-8"))

    trace_template = json.loads(text(".github/skills/trace/templates/execution_trace.template.json"))
    for field in ["trace_version", "generated_by", "source_scope", "scripts", "logs", "cross_program_summary"]:
        require(field in trace_template, f"Trace template lost compatibility field: {field}", errors)

    restart_template = yaml.safe_load(text(".github/skills/restart/templates/reset_plan.template.yaml"))
    require(restart_template.get("module_id") == "", "Restart template must not select a module", errors)
    require(restart_template.get("approved_project_contracts") == [], "Restart template must not pre-approve contracts", errors)

    registry_template = yaml.safe_load(text(".github/skills/map/templates/policy_registry.template.yaml"))
    first_pattern = registry_template["patterns"][0]
    for field in ["sas_code_block", "target_module_type", "complexity"]:
        require(field in first_pattern, f"Policy registry lost compatibility field: {field}", errors)

    golden_rules = text("docs/policies/lp-emulator-golden-rules.md")
    for number in range(1, 11):
        require(f"| {number} |" in golden_rules, f"Golden Rule {number} missing", errors)
    require("approved target ADR" in golden_rules, "Golden Rules lack ADR applicability boundary", errors)

    require((ROOT / "docs/runbooks/LOCAL_PARITY.md").exists(), "Missing local parity runbook", errors)
    require((ROOT / "scripts/run_tieout.py").exists(), "Missing generic tie-out runner", errors)

    test_pressure = text(".github/skills/test/evals/cases.md")
    validate_pressure = text(".github/skills/validate/evals/cases.md")
    review_pressure = text(".github/skills/review/evals/cases.md")
    release_pressure = text(".github/skills/release/evals/cases.md")
    require("Coverage claim without assertions" in test_pressure and "Nondeterministic producer" in test_pressure, "Test evaluations lack coverage and determinism pressure cases", errors)
    require("Failed mandatory fixture coverage" in validate_pressure and "Retry overwrites failed evidence" in validate_pressure, "Validate evaluations lack coverage and append-only retry cases", errors)
    require("Retry lineage missing" in review_pressure and "Reviewer tries to repair" in review_pressure, "Review evaluations lack independence and retry-lineage cases", errors)
    require("Hand-entered parity scoreboard" in release_pressure and "Candidate packet treated as approval" in release_pressure, "Release evaluations lack evidence-derived scoreboard and human-gate cases", errors)

    for relative in [
        ".github/skills/interview/evals/cases.md",
        ".github/skills/restart/evals/cases.md",
        ".github/skills/specify/evals/cases.md",
        ".github/skills/test/evals/cases.md",
        ".github/skills/validate/evals/cases.md",
        ".github/skills/review/evals/cases.md",
        ".github/skills/release/evals/cases.md",
        ".github/skills/trace/evals/cases.md",
        ".github/skills/map/evals/cases.md",
        ".github/skills/harvest/evals/cases.md",
        ".github/skills/import/evals/cases.md",
        ".github/skills/learn/evals/cases.md",
    ]:
        require((ROOT / relative).exists(), f"Missing pressure evaluations: {relative}", errors)

    for prompt_name in REQUIRED_PROMPTS:
        prompt = text(f".github/prompts/{prompt_name}")
        require("AGENTS.md" in prompt, f"Prompt does not reference governance: {prompt_name}", errors)
        require("orchestrate" in prompt, f"Prompt does not route through orchestrate: {prompt_name}", errors)

    forbidden_outputs = [
        "docs/PRD.md",
        "docs/CAPABILITY_MAP.md",
        "stage1_extraction/output/execution_trace.json",
        "policy/policy_registry.yaml",
    ]
    for relative in forbidden_outputs:
        require(not (ROOT / relative).exists(), f"Clean template contains generated artifact: {relative}", errors)

    require(not list((ROOT / "artifacts/run_state").glob("*.json")), "Clean template contains durable run state", errors)
    require(not visible_files(ROOT / "artifacts/evidence"), "Clean template contains migration evidence", errors)
    require(not list((ROOT / "docs/specs").glob("*.md")), "Clean template contains an active module SPEC", errors)
    require(not list((ROOT / "docs/adrs").glob("*.md")), "Clean template contains an active ADR", errors)
    require(not list((ROOT / "src/sas_migration").rglob("*.py")), "Clean template contains generated Python", errors)
    require(not visible_files(ROOT / "tests/generated"), "Clean template contains generated tests or fixtures", errors)
    require(not visible_files(ROOT / "artifacts/learning/observations"), "Clean template contains real learning observations", errors)
    require(not visible_files(ROOT / "artifacts/learning/proposals"), "Clean template contains real skill-change proposals", errors)
    require(not visible_files(ROOT / "artifacts/learning/reviews"), "Clean template contains real learning reviews", errors)
    require(not visible_files(ROOT / "docs/learning/patterns"), "Clean template contains active learning patterns", errors)

    for relative in [
        "docs/learning/WIKI_CONTRACT.md",
        "docs/learning/index.md",
        "docs/learning/evolution-log.md",
        "docs/learning/skill-impact.md",
        "docs/runbooks/GOVERNED_LEARNING.md",
        "scripts/validate_learning_memory.py",
        ".github/skills/learn/templates/learning_observation.template.json",
        ".github/skills/learn/templates/learning_pattern.template.md",
        ".github/skills/learn/templates/skill_change_proposal.template.json",
        ".github/skills/learn/templates/learning_review.template.json",
        ".github/workflows/template-validation.yml",
    ]:
        require((ROOT / relative).is_file(), f"Missing governed learning-memory asset: {relative}", errors)

    allowed_intake = {"README.md", "REQUESTED_ARTIFACTS.md", ".gitkeep"}
    unexpected_intake = [path for path in (ROOT / "intake").rglob("*") if path.is_file() and path.name not in allowed_intake]
    require(not unexpected_intake, f"Clean template contains source intake: {[str(path.relative_to(ROOT)) for path in unexpected_intake]}", errors)

    example_files = visible_files(ROOT / "examples/lc-logit-01")
    require(bool(example_files), "LC-LOGIT-01 documentation example is missing", errors)
    require(all(path.suffix.lower() == ".md" for path in example_files), "Example contains executable or data assets", errors)
    example_text = text("examples/lc-logit-01/README.md")
    require("documentation-only" in example_text.lower(), "Example is not clearly labeled documentation-only", errors)
    require("not template defaults" in example_text.lower(), "Example does not forbid copying its values", errors)

    if errors:
        print("AGENT ARCHITECTURE VALIDATION: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"AGENT ARCHITECTURE VALIDATION: PASS ({len(skill_names)} skills, {len(prompt_names)} prompts, clean template)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
