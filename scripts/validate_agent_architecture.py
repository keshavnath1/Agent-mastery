#!/usr/bin/env python3
"""Validate the reusable agent-mastery template without executing migration work."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import yaml

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

    tieout = yaml.safe_load(text("config/tieout.yaml"))
    require(tieout.get("status") == "UNAPPROVED_TEMPLATE", "Tie-out contract must be unapproved", errors)
    require(tieout.get("module_id") is None, "Tie-out contract must not contain a module ID", errors)
    require(tieout.get("key_columns") == [], "Template must not invent tie-out keys", errors)
    require(tieout.get("required_prediction_columns") == [], "Template must not invent output columns", errors)
    require(tieout.get("comparisons") == [], "Template must not invent metrics or tolerances", errors)
    require(tieout.get("oracle_lock", {}).get("implementation_may_modify") is False, "Implementation must not modify the tie-out contract", errors)

    workflow = yaml.safe_load(text("config/workflow.yaml"))
    rules = workflow["control_rules"]
    require(rules["one_skill_per_prompt"] is True, "one_skill_per_prompt must be true", errors)
    require(rules["stop_at_human_gate"] is True, "stop_at_human_gate must be true", errors)
    require(rules["self_approval_forbidden"] is True, "self_approval_forbidden must be true", errors)
    require(workflow["canonical_artifacts"]["execution_trace"] == "stage1_extraction/output/execution_trace.json", "Wrong canonical trace path", errors)
    require(workflow["canonical_artifacts"]["policy_registry"] == "policy/policy_registry.yaml", "Wrong canonical policy registry path", errors)
    require(workflow["canonical_artifacts"]["tieout_contract"] == "config/tieout.yaml", "Wrong canonical tie-out path", errors)
    require(workflow["canonical_artifacts"]["module_spec"] == "docs/specs/<module>.md", "Module SPEC path must be runtime-neutral", errors)
    require(workflow["canonical_artifacts"]["implementation"] == "src/sas_migration/semantic/", "Implementation path must be generic", errors)
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

    trace_skill = text(".github/skills/trace/SKILL.md")
    map_skill = text(".github/skills/map/SKILL.md")
    map_contract = text(".github/skills/map/references/behavior-mapping-contract.md")
    map_pressure = text(".github/skills/map/evals/cases.md")
    orchestrate_skill = text(".github/skills/orchestrate/SKILL.md")
    orchestrate_pressure = text(".github/skills/orchestrate/evals/cases.md")
    stage_contract = text("docs/runbooks/STAGE_CONTRACT.md")
    specify_skill = text(".github/skills/specify/SKILL.md")
    restart_skill = text(".github/skills/restart/SKILL.md")

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
    require("approved project-level contracts" in specify_skill, "Specify does not preserve approved project contracts", errors)
    require("config/tieout.yaml" in restart_skill, "Restart does not account for approved tie-out contracts", errors)
    require("runtime-neutral semantic responsibilities" in map_skill, "Map skill lacks taxonomy-neutral fallback", errors)
    require("optional refinements" in map_contract, "Map contract does not make taxonomies optional", errors)
    require("explicitly selects LP Emulator" in map_contract, "Map contract lacks the LP Emulator ADR boundary", errors)
    require("No matching taxonomy" in map_pressure, "Map evaluations lack taxonomy-neutral fallback coverage", errors)
    require("Single formula owner" in map_pressure, "Map evaluations lack single formula-owner coverage", errors)

    schema_paths = [
        ROOT / ".github/skills/trace/schemas/execution_trace.schema.json",
        ROOT / ".github/skills/map/schemas/policy_registry.schema.json",
        ROOT / ".github/skills/restart/schemas/reset_plan.schema.json",
        ROOT / ".github/skills/harvest/schemas/pattern_bundle.schema.json",
        ROOT / ".github/skills/import/schemas/compatibility_matrix.schema.json",
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

    for relative in [
        ".github/skills/restart/evals/cases.md",
        ".github/skills/specify/evals/cases.md",
        ".github/skills/trace/evals/cases.md",
        ".github/skills/map/evals/cases.md",
        ".github/skills/harvest/evals/cases.md",
        ".github/skills/import/evals/cases.md",
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
