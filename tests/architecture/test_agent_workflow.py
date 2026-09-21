from __future__ import annotations

from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]


class AgentWorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = yaml.safe_load((ROOT / "config/workflow.yaml").read_text(encoding="utf-8"))

    def test_lifecycle_act_sequence(self) -> None:
        self.assertEqual(
            [act["skills"] for act in self.workflow["acts"]],
            [
                ["interview", "specify", "decide"],
                ["harvest", "import", "trace", "map", "model"],
                ["generate", "test", "validate"],
                ["adapt", "ingest", "review", "release"],
                ["learn"],
            ],
        )

    def test_one_skill_and_human_gate_rules(self) -> None:
        rules = self.workflow["control_rules"]
        self.assertTrue(rules["one_skill_per_prompt"])
        self.assertTrue(rules["stop_at_human_gate"])
        self.assertTrue(rules["self_approval_forbidden"])
        self.assertTrue(rules["deterministic_tools_invoked_by_skill"])
        self.assertTrue(rules["learning_memory_advisory_only"])
        self.assertEqual(rules["learning_independent_run_minimum"], 2)
        self.assertTrue(rules["learning_promotion_human_only"])

    def test_clean_template_has_no_active_module_or_approved_contract(self) -> None:
        project = yaml.safe_load((ROOT / "config/project.yaml").read_text(encoding="utf-8"))
        profile = yaml.safe_load((ROOT / "config/migration_profile.yaml").read_text(encoding="utf-8"))
        tieout = yaml.safe_load((ROOT / "config/tieout.yaml").read_text(encoding="utf-8"))

        self.assertEqual(project["status"], "TEMPLATE")
        self.assertIsNone(project["active_module"])
        self.assertIsNone(project["active_stage"])
        self.assertEqual(profile["status"], "UNAPPROVED_TEMPLATE")
        self.assertIsNone(profile["module_id"])
        self.assertIsNone(profile["local_tieout_requested"])
        self.assertIsNone(profile["tieout_population"]["choice"])
        self.assertIn("tieout_population_choice", profile["human_approval_required"])
        self.assertEqual(tieout["status"], "UNAPPROVED_TEMPLATE")
        self.assertIsNone(tieout["scope"]["population_choice"])
        self.assertIsNone(tieout["scope"]["current_phase"])
        self.assertIsNone(tieout["scope"]["full_population_followup_required"])
        self.assertEqual(tieout["key_columns"], [])
        self.assertIsNone(tieout["intake_manifest"]["path"])
        self.assertIsNone(tieout["oracle"]["path"])
        self.assertIsNone(tieout["oracle"]["format"])
        self.assertIsNone(tieout["decision_basis"]["source"])
        self.assertIsNone(tieout["fixture_manifest"]["path"])
        self.assertEqual(tieout["producer"]["command"], [])
        self.assertEqual(tieout["comparisons"], [])
        self.assertFalse(tieout["oracle_lock"]["implementation_may_modify"])

    def test_clean_template_has_no_generated_migration_outputs(self) -> None:
        self.assertFalse((ROOT / "docs/PRD.md").exists())
        self.assertFalse((ROOT / "docs/CAPABILITY_MAP.md").exists())
        self.assertEqual(list((ROOT / "docs/specs").glob("*.md")), [])
        self.assertEqual(list((ROOT / "docs/adrs").glob("*.md")), [])
        self.assertEqual(list((ROOT / "artifacts/run_state").glob("*.json")), [])
        self.assertFalse((ROOT / "stage1_extraction/output/execution_trace.json").exists())
        self.assertFalse((ROOT / "policy/policy_registry.yaml").exists())
        self.assertEqual(list((ROOT / "src/sas_migration").rglob("*.py")), [])
        self.assertEqual(
            [path for path in (ROOT / "artifacts/evidence").rglob("*") if path.is_file() and path.name != ".gitkeep"],
            [],
        )

    def test_intake_is_empty_and_ignored_by_default(self) -> None:
        allowed = {"README.md", "REQUESTED_ARTIFACTS.md", ".gitkeep"}
        unexpected = [path for path in (ROOT / "intake").rglob("*") if path.is_file() and path.name not in allowed]
        self.assertEqual(unexpected, [])

        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for path in ["intake/sas/*", "intake/logs/*", "intake/lst/*", "intake/data/*", "intake/patterns/*"]:
            self.assertIn(path, ignore)

    def test_stage_result_has_copy_ready_next_message(self) -> None:
        fields = set(self.workflow["stage_result_fields"])
        self.assertTrue({"next_permitted_command", "next_action", "copy_paste_next"} <= fields)

        contract = (ROOT / "docs/runbooks/STAGE_CONTRACT.md").read_text(encoding="utf-8")
        orchestrate = (ROOT / ".github/skills/orchestrate/SKILL.md").read_text(encoding="utf-8")
        evaluations = (ROOT / ".github/skills/orchestrate/evals/cases.md").read_text(encoding="utf-8")
        self.assertIn("**Next action:**", contract)
        self.assertIn("**Copy/paste next:**", contract)
        self.assertIn("Missing output hash", evaluations)
        self.assertIn("Copy/paste next", orchestrate)

    def test_canonical_artifact_paths_are_stable_and_generic(self) -> None:
        artifacts = self.workflow["canonical_artifacts"]
        self.assertEqual(artifacts["execution_trace"], "stage1_extraction/output/execution_trace.json")
        self.assertEqual(artifacts["policy_registry"], "policy/policy_registry.yaml")
        self.assertEqual(artifacts["tieout_contract"], "config/tieout.yaml")
        self.assertEqual(artifacts["module_spec"], "docs/specs/<module>.md")
        self.assertEqual(artifacts["semantic_ir"], "artifacts/semantic_ir/<module>.json")
        self.assertEqual(artifacts["implementation"], "src/sas_migration/semantic/")
        self.assertEqual(artifacts["tieout_result"], "artifacts/evidence/runs/<run-id>/attempts/<attempt-id>/tieout_result.json")
        self.assertEqual(artifacts["tieout_summary"], "artifacts/evidence/runs/<run-id>/attempts/<attempt-id>/tieout_summary.md")
        self.assertEqual(artifacts["learning_observation"], "artifacts/learning/observations/<observation-id>.json")
        self.assertEqual(artifacts["learning_pattern"], "docs/learning/patterns/<pattern-id>.md")
        self.assertEqual(artifacts["skill_change_proposal"], "artifacts/learning/proposals/<proposal-id>.json")
        self.assertEqual(artifacts["learning_review"], "artifacts/learning/reviews/<review-id>.json")

    def test_interview_requires_human_population_choice(self) -> None:
        choices = {
            "GOVERNED_SAMPLE_50",
            "FULL_POPULATION",
            "PHASED_50_THEN_FULL",
            "CUSTOM_GOVERNED_SAMPLE",
        }
        interview = (ROOT / ".github/skills/interview/SKILL.md").read_text(encoding="utf-8")
        start_prompt = (ROOT / ".github/prompts/start-migration.prompt.md").read_text(encoding="utf-8")
        interview_evals = (ROOT / ".github/skills/interview/evals/cases.md").read_text(encoding="utf-8")
        specify = (ROOT / ".github/skills/specify/SKILL.md").read_text(encoding="utf-8")
        validate = (ROOT / ".github/skills/validate/SKILL.md").read_text(encoding="utf-8")
        release = (ROOT / ".github/skills/release/SKILL.md").read_text(encoding="utf-8")
        for choice in choices:
            self.assertIn(choice, interview)
            self.assertIn(choice, start_prompt)
        self.assertIn("Tie-out requested without population choice", interview_evals)
        self.assertIn("full_population_followup_required", specify)
        self.assertIn("PHASED_50_THEN_FULL", validate)
        self.assertIn("full_population_followup_required", release)
        gate = next(gate for gate in self.workflow["human_gates"] if gate.get("after") == "interview")
        self.assertIn("tie-out population", gate["approval"])

    def test_generic_parity_framework_is_required_but_inert(self) -> None:
        for relative in [
            "scripts/run_tieout.py",
            "contracts/tieout_contract.schema.json",
            "contracts/tieout_result.schema.json",
            "contracts/fixture_manifest.schema.json",
            "docs/runbooks/LOCAL_PARITY.md",
            "tests/framework/test_generic_tieout.py",
        ]:
            self.assertTrue((ROOT / relative).is_file(), relative)

        generate = (ROOT / ".github/skills/generate/SKILL.md").read_text(encoding="utf-8")
        test = (ROOT / ".github/skills/test/SKILL.md").read_text(encoding="utf-8")
        validate = (ROOT / ".github/skills/validate/SKILL.md").read_text(encoding="utf-8")
        review = (ROOT / ".github/skills/review/SKILL.md").read_text(encoding="utf-8")
        release = (ROOT / ".github/skills/release/SKILL.md").read_text(encoding="utf-8")
        runner = (ROOT / "scripts/run_tieout.py").read_text(encoding="utf-8")
        self.assertIn("producer entry point", generate)
        self.assertIn("fixture_manifest.schema.json", test)
        self.assertIn("coverage assertions", test)
        self.assertIn("scripts/project.py tieout", validate)
        self.assertIn("--attempt-id", validate)
        self.assertIn("tieout_summary.md", validate)
        self.assertIn("population_scope", runner)
        self.assertIn("reproduced `tieout_result.json`", review)
        self.assertIn("parity scoreboard", release)
        self.assertIn("reviewed machine-readable evidence", release)
        self.assertIn("shell=False", runner)
        self.assertIn("selected_keys_digest", runner)
        self.assertIn("render_summary", runner)

    def test_recovery_loop_is_bounded(self) -> None:
        recovery = self.workflow["recovery_loop"]
        self.assertEqual(recovery["sequence"], ["ingest", "diagnose", "repair", "review"])
        self.assertTrue(recovery["require_loop_contract"])
        self.assertTrue(recovery["require_isolated_worktree"])
        self.assertEqual(self.workflow["control_rules"]["maximum_repair_attempts"], 3)

    def test_governed_learning_memory_is_present_but_inert(self) -> None:
        for relative in [
            "contracts/learning_observation.schema.json",
            "contracts/learning_pattern.schema.json",
            "contracts/skill_change_proposal.schema.json",
            "contracts/learning_review.schema.json",
            "scripts/validate_learning_memory.py",
            "docs/learning/WIKI_CONTRACT.md",
            "docs/runbooks/GOVERNED_LEARNING.md",
            ".github/skills/learn/evals/cases.md",
        ]:
            self.assertTrue((ROOT / relative).is_file(), relative)

        learn = (ROOT / ".github/skills/learn/SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / "docs/learning/WIKI_CONTRACT.md").read_text(encoding="utf-8")
        pressure = (ROOT / ".github/skills/learn/evals/cases.md").read_text(encoding="utf-8")
        self.assertIn("at least two independent run IDs", learn)
        self.assertIn("exactly one", learn)
        self.assertIn("learn_promotion / PENDING_HUMAN_APPROVAL", learn)
        self.assertIn("advisory", contract.lower())
        self.assertIn("Hidden reasoning capture", pressure)
        self.assertIn("Cross-model negative transfer", pressure)

        control = self.workflow["learning_control"]
        self.assertEqual(control["review_stage"], "learn_review")
        self.assertEqual(control["promotion_stage"], "learn_promotion")
        self.assertEqual(control["transitions"][1]["status"], "PENDING_HUMAN_APPROVAL")

        for relative in ["artifacts/learning/observations", "artifacts/learning/proposals", "artifacts/learning/reviews", "docs/learning/patterns"]:
            files = [path for path in (ROOT / relative).rglob("*") if path.is_file() and path.name != ".gitkeep"]
            self.assertEqual(files, [], relative)

    def test_all_prompt_routers_exist_and_use_orchestrate(self) -> None:
        for name in [
            "start-migration.prompt.md",
            "restart-migration.prompt.md",
            "run-next-stage.prompt.md",
            "run-stage1.prompt.md",
            "run-stage2.prompt.md",
            "seed-production-patterns.prompt.md",
            "ingest-cluster-log.prompt.md",
            "analyze-failure.prompt.md",
            "review-evidence.prompt.md",
        ]:
            prompt_path = ROOT / ".github/prompts" / name
            self.assertTrue(prompt_path.is_file(), name)
            prompt = prompt_path.read_text(encoding="utf-8")
            self.assertIn("AGENTS.md", prompt, name)
            self.assertIn("orchestrate", prompt, name)

    def test_lp_emulator_policy_is_adr_conditional(self) -> None:
        policy = (ROOT / "docs/policies/lp-emulator-golden-rules.md").read_text(encoding="utf-8")
        taxonomy = (ROOT / ".github/skills/map/references/lp-emulator-module-taxonomy.md").read_text(encoding="utf-8")
        self.assertIn("approved target ADR", policy)
        self.assertIn("approved target ADR", taxonomy)

    def test_map_follows_adr_without_matching_taxonomy(self) -> None:
        skill = (ROOT / ".github/skills/map/SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / ".github/skills/map/references/behavior-mapping-contract.md").read_text(encoding="utf-8")
        evaluations = (ROOT / ".github/skills/map/evals/cases.md").read_text(encoding="utf-8")

        self.assertIn("runtime-neutral semantic responsibilities", skill)
        self.assertIn("Do not stop merely because an optional matching taxonomy", skill)
        self.assertIn("optional refinements", contract)
        self.assertIn("explicitly selects LP Emulator", contract)
        self.assertIn("No matching taxonomy", evaluations)
        self.assertIn("Single formula owner", evaluations)

    def test_example_is_documentation_only_and_not_authoritative(self) -> None:
        example_dir = ROOT / "examples/lc-logit-01"
        files = [path for path in example_dir.rglob("*") if path.is_file()]
        self.assertTrue(files)
        self.assertTrue(all(path.suffix.lower() == ".md" for path in files))
        content = (example_dir / "README.md").read_text(encoding="utf-8").lower()
        self.assertIn("documentation-only", content)
        self.assertIn("not template defaults", content)
        self.assertIn("not an implementation starter", (ROOT / "README.md").read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
