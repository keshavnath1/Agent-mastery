from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_learning_memory.py"
SPEC = importlib.util.spec_from_file_location("validate_learning_memory", SCRIPT)
assert SPEC and SPEC.loader
learning = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(learning)
REAL_VERIFY_GITHUB_APPROVAL = learning.verify_github_approval
TEMPLATES = ROOT / ".github" / "skills" / "learn" / "templates"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GovernedLearningMemoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.github_patcher = mock.patch.object(learning, "verify_github_approval")
        self.github_patcher.start()
        scratch_root = ROOT / "artifacts" / "learning" / "test-scratch"
        scratch_root.mkdir(parents=True, exist_ok=True)
        self.tempdir = tempfile.TemporaryDirectory(dir=scratch_root)
        self.root = Path(self.tempdir.name)
        self.baseline = self.git("rev-parse", "HEAD")
        self.candidate = self.make_candidate([".github/skills/test/SKILL.md"])
        self.bundle = self.create_bundle()

    def tearDown(self) -> None:
        self.github_patcher.stop()
        self.tempdir.cleanup()
        scratch_root = ROOT / "artifacts" / "learning" / "test-scratch"
        try:
            scratch_root.rmdir()
        except OSError:
            pass

    def git(self, *args: str, input_text: str | None = None, env: dict[str, str] | None = None) -> str:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, text=True, input=input_text, capture_output=True,
            env=env or os.environ.copy(), check=True,
        )
        return result.stdout.strip()

    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()

    def write_text(self, name: str, value: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
        return path

    def write_json(self, name: str, value: dict) -> Path:
        return self.write_text(name, json.dumps(value, indent=2) + "\n")

    def ref(self, path: Path, identifier: str | None = None) -> dict:
        value = {"path": self.rel(path), "sha256": digest(path)}
        if identifier is not None:
            value["id"] = identifier
        return value

    def make_candidate(self, changed_paths: list[str]) -> str:
        index = self.root / f"index-{len(list(self.root.glob('index-*')))}"
        env = os.environ.copy()
        env.update({
            "GIT_INDEX_FILE": str(index),
            "GIT_AUTHOR_NAME": "Synthetic Test",
            "GIT_AUTHOR_EMAIL": "synthetic@example.invalid",
            "GIT_COMMITTER_NAME": "Synthetic Test",
            "GIT_COMMITTER_EMAIL": "synthetic@example.invalid",
        })
        self.git("read-tree", self.baseline, env=env)
        for relative in changed_paths:
            original = self.git("show", f"{self.baseline}:{relative}")
            blob = self.git("hash-object", "-w", "--stdin", input_text=original + "\n# synthetic candidate\n")
            self.git("update-index", "--add", "--cacheinfo", "100644", blob, relative, env=env)
        tree = self.git("write-tree", env=env)
        return self.git("commit-tree", tree, "-p", self.baseline, "-m", "synthetic learning candidate", env=env)

    def observation(self, identifier: str, run_id: str, module_id: str, evidence: list[tuple[Path, str]], author: str) -> dict:
        value = json.loads((TEMPLATES / "learning_observation.template.json").read_text(encoding="utf-8"))
        value.update({
            "record_status": "RECORDED",
            "observation_id": identifier,
            "run_id": run_id,
            "module_id": module_id,
            "recorded_at": "2026-09-20T12:00:00Z",
            "recorded_by": {"identity": author, "role": "analyst"},
            "skill_invoked": "validate",
            "outcome": "PASS",
            "input_evidence": [{**self.ref(path), "kind": kind} for path, kind in evidence],
            "output_evidence": [],
            "observable_events": ["The frozen evaluator reproduced the recorded boundary."],
            "failure": None,
            "candidate_pattern_ids": ["PATTERN-001"],
            "privacy_review": {
                "contains_chain_of_thought": False,
                "contains_secrets": False,
                "contains_raw_business_data": False,
                "redactions": [],
                "reviewer": {"identity": f"privacy-{author}", "role": "checker"},
                "reviewed_at": "2026-09-20T12:30:00Z",
            },
        })
        return value

    def write_pattern(self, metadata: dict, body: str, name: str = "pattern.md") -> Path:
        path = self.root / name
        path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---" + body, encoding="utf-8")
        return path

    def create_bundle(self) -> dict:
        evidence_one = self.write_text("evidence/run-one.txt", "PASS one\n")
        evidence_two = self.write_text("evidence/run-two.txt", "PASS two\n")
        fixture_one = self.write_text("evidence/fixture-one.txt", "fixture one\n")
        fixture_two = self.write_text("evidence/fixture-two.txt", "fixture two\n")
        state_one = self.write_json("evidence/state-one.json", {"run_id": "RUN-001", "module_id": "MODULE-001", "stage": "validate", "status": "PASS", "attempts": 0, "history": []})
        state_two = self.write_json("evidence/state-two.json", {"run_id": "RUN-002", "module_id": "MODULE-002", "stage": "validate", "status": "PASS", "attempts": 0, "history": []})
        evaluator_manifest = ROOT / "scripts/validate_agent_architecture.py"
        observation_one = self.write_json(
            "observations/one.json",
            self.observation(
                "OBS-001", "RUN-001", "MODULE-001",
                [(state_one, "run_state"), (fixture_one, "other"), (evaluator_manifest, "other"), (evidence_one, "test_result")],
                "observer-one",
            ),
        )
        observation_two = self.write_json(
            "observations/two.json",
            self.observation(
                "OBS-002", "RUN-002", "MODULE-002",
                [(state_two, "run_state"), (fixture_two, "other"), (evaluator_manifest, "other"), (evidence_two, "test_result")],
                "observer-two",
            ),
        )

        template = (TEMPLATES / "learning_pattern.template.md").read_text(encoding="utf-8")
        _, frontmatter, body = template.split("---", 2)
        pattern = yaml.safe_load(frontmatter)
        contexts = [
            {
                "source_commit": self.baseline,
                "source_platform": "sas",
                "migration_mode": "score_only",
                "semantic_boundary": "approved_coefficients",
                "run_state": self.ref(state_one),
                "fixture": self.ref(fixture_one),
                "oracle": None,
                "expected_output": None,
                "evaluator_manifest": self.ref(evaluator_manifest),
                "result": self.ref(evidence_one),
                "agent_model": "copilot-agent",
                "target_runtime": "local_python",
                "population_scope": "governed_sample",
            },
            {
                "source_commit": self.candidate,
                "source_platform": "sas",
                "migration_mode": "score_only",
                "semantic_boundary": "approved_coefficients",
                "run_state": self.ref(state_two),
                "fixture": self.ref(fixture_two),
                "oracle": None,
                "expected_output": None,
                "evaluator_manifest": self.ref(evaluator_manifest),
                "result": self.ref(evidence_two),
                "agent_model": "copilot-agent",
                "target_runtime": "local_python",
                "population_scope": "governed_sample",
            },
        ]
        pattern.update({
            "record_status": "RECORDED",
            "pattern_id": "PATTERN-001",
            "status": "CANDIDATE",
            "title": "Preserve exact coefficient representation",
            "summary": "Independent runs failed when coefficient representation was shortened.",
            "consolidated_by": {"identity": "pattern-author", "role": "analyst"},
            "occurrences": [
                {
                    "observation_id": "OBS-001",
                    "observation_path": self.rel(observation_one),
                    "observation_sha256": digest(observation_one),
                    "run_id": "RUN-001",
                    "module_id": "MODULE-001",
                    "context": contexts[0],
                },
                {
                    "observation_id": "OBS-002",
                    "observation_path": self.rel(observation_two),
                    "observation_sha256": digest(observation_two),
                    "run_id": "RUN-002",
                    "module_id": "MODULE-002",
                    "context": contexts[1],
                },
            ],
            "independence_review": {
                "reviewer": {"identity": "recurrence-checker", "role": "checker"},
                "reviewed_at": "2026-09-20T13:00:00Z",
                "conclusion": "INDEPENDENT",
                "rationale": "The runs use distinct commits, fixtures, modules, and evidence records.",
            },
            "applicability": {
                "source_platforms": ["sas"],
                "migration_modes": ["score_only"],
                "semantic_boundaries": ["approved_coefficients"],
                "target_runtimes": ["local_python"],
                "model_families": ["copilot-agent"],
                "population_scopes": ["governed_sample"],
                "required_preconditions": ["approved oracle provenance"],
            },
            "does_not_prove": ["full population parity"],
            "prohibited_generalizations": ["Do not infer distributed-runtime behavior."],
            "candidate_skill_targets": [".github/skills/test/SKILL.md"],
            "promotion": {
                "human_decision": "PENDING",
                "run_state_path": None,
                "run_state_sha256": None,
                "promotion_commit": None,
                "github_review": None,
            },
            "sensitivity": {
                "public_template_safe": False,
                "contains_raw_business_data": False,
                "contains_secrets": False,
                "contains_chain_of_thought": False,
                "reviewer": {"identity": "pattern-privacy-checker", "role": "checker"},
                "reviewed_at": "2026-09-20T13:10:00Z",
            },
        })
        pattern_path = self.write_pattern(pattern, body)

        patch = self.write_text(
            "proposal/skill.patch",
            self.git("diff", "--binary", self.baseline, self.candidate, "--", ".github/skills/test/SKILL.md") + "\n",
        )
        evaluators = {
            "architecture": ROOT / "scripts/validate_agent_architecture.py",
            "normal": ROOT / ".github/skills/test/evals/cases.md",
            "pressure": ROOT / ".github/skills/learn/evals/cases.md",
        }
        result_files = {kind: self.write_text(f"proposal/{kind}.txt", f"{kind}: PASS\n") for kind in evaluators}
        runs = [
            {
                "kind": kind,
                "command": ["python3", self.rel(evaluator)],
                "exit_code": 0,
                "result": "PASS",
                "result_path": self.rel(result_files[kind]),
                "result_sha256": digest(result_files[kind]),
                "evaluator_sha256": digest(evaluator),
            }
            for kind, evaluator in evaluators.items()
        ]
        review = {
            "schema_version": "1.0",
            "record_status": "RECORDED",
            "review_id": "REVIEW-001",
            "proposal_id": "PROPOSAL-001",
            "author_identity": "proposal-author",
            "reviewer": {"identity": "independent-checker", "role": "checker"},
            "reviewed_at": "2026-09-20T14:00:00Z",
            "candidate_commit": self.candidate,
            "verdict": "ACCEPT",
            "github_review": {
                "repository": "example/repository",
                "pull_request": 1,
                "review_id": 10,
                "reviewer_login": "independent-checker",
                "reviewed_commit": self.candidate,
            },
            "reruns": copy.deepcopy(runs),
            "findings": [],
            "privacy_review": {"contains_chain_of_thought": False, "contains_secrets": False, "contains_raw_business_data": False},
        }
        review_path = self.write_json("reviews/review.json", review)

        proposal = json.loads((TEMPLATES / "skill_change_proposal.template.json").read_text(encoding="utf-8"))
        proposal.update({
            "record_status": "RECORDED",
            "proposal_id": "PROPOSAL-001",
            "status": "CANDIDATE_FOR_PROMOTION",
            "created_at": "2026-09-20T13:30:00Z",
            "author": {"identity": "proposal-author", "role": "analyst"},
            "target_skill": "test",
            "target_skill_path": ".github/skills/test/SKILL.md",
            "source_patterns": [self.ref(pattern_path, "PATTERN-001")],
            "baseline_commit": self.baseline,
            "candidate_commit": self.candidate,
            "patch": self.ref(patch),
            "frozen_evaluators": [
                {"kind": kind, "path": self.rel(evaluator), "sha256": digest(evaluator)}
                for kind, evaluator in evaluators.items()
            ],
            "validation": {
                "runs": copy.deepcopy(runs),
                "governance_regressions": [],
                "target_improved_or_defect_resolved": True,
                "result": "PASS",
            },
            "independent_review": self.ref(review_path, "REVIEW-001"),
            "proof_boundary": ["Synthetic governed-learning validation only."],
        })
        proposal_path = self.write_json("proposal/proposal.json", proposal)
        return {
            "observations": [observation_one, observation_two],
            "pattern": pattern_path,
            "pattern_metadata": pattern,
            "pattern_body": body,
            "review": review_path,
            "proposal": proposal_path,
            "proposal_data": proposal,
        }

    def test_committed_templates_are_valid_and_inert(self) -> None:
        learning.validate_observation(TEMPLATES / "learning_observation.template.json")
        learning.validate_pattern(TEMPLATES / "learning_pattern.template.md")
        learning.validate_proposal(TEMPLATES / "skill_change_proposal.template.json")
        learning.validate_review(TEMPLATES / "learning_review.template.json")

    def test_valid_evidence_backed_bundle(self) -> None:
        for observation in self.bundle["observations"]:
            learning.validate_observation(observation)
        learning.validate_pattern(self.bundle["pattern"])
        learning.validate_review(self.bundle["review"])
        learning.validate_proposal(self.bundle["proposal"])

    def test_hash_mismatch_and_missing_evidence_are_rejected(self) -> None:
        observation = json.loads(self.bundle["observations"][0].read_text(encoding="utf-8"))
        observation["input_evidence"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(learning.ValidationFailure, "SHA-256 mismatch"):
            learning.validate_observation(self.write_json("bad-hash.json", observation))
        observation["input_evidence"][0]["path"] = self.rel(self.root / "missing.txt")
        with self.assertRaisesRegex(learning.ValidationFailure, "does not exist"):
            learning.validate_observation(self.write_json("missing-evidence.json", observation))

    def test_external_and_traversal_paths_are_rejected(self) -> None:
        with self.assertRaisesRegex(learning.ValidationFailure, "escapes repository"):
            learning.safe_repo_path("../../etc/passwd", self.root / "source.json")
        outside = Path(tempfile.gettempdir()) / "outside-learning.json"
        with self.assertRaisesRegex(learning.ValidationFailure, "absolute paths are forbidden"):
            learning.safe_repo_path(str(outside), self.root / "source.json")

    def test_fabricated_or_correlated_recurrence_is_rejected(self) -> None:
        pattern = copy.deepcopy(self.bundle["pattern_metadata"])
        pattern["occurrences"][1]["observation_id"] = "FABRICATED"
        path = self.write_pattern(pattern, self.bundle["pattern_body"], "fabricated.md")
        with self.assertRaisesRegex(learning.ValidationFailure, "does not match"):
            learning.validate_pattern(path)
        pattern = copy.deepcopy(self.bundle["pattern_metadata"])
        for key in ["source_commit", "fixture", "oracle", "expected_output", "evaluator_manifest", "agent_model", "target_runtime", "population_scope"]:
            pattern["occurrences"][1]["context"][key] = copy.deepcopy(pattern["occurrences"][0]["context"][key])
        observation = json.loads(self.bundle["observations"][1].read_text(encoding="utf-8"))
        extra_refs = [pattern["occurrences"][0]["context"]["fixture"]]
        for ref in extra_refs:
            if not any(item["path"] == ref["path"] for item in observation["input_evidence"]):
                observation["input_evidence"].append({**ref, "kind": "other"})
        correlated_observation = self.write_json("observations/correlated-two.json", observation)
        pattern["occurrences"][1]["observation_path"] = self.rel(correlated_observation)
        pattern["occurrences"][1]["observation_sha256"] = digest(correlated_observation)
        path = self.write_pattern(pattern, self.bundle["pattern_body"], "correlated.md")
        with self.assertRaisesRegex(learning.ValidationFailure, "contexts are identical"):
            learning.validate_pattern(path)

    def test_untested_model_or_runtime_transfer_is_rejected(self) -> None:
        pattern = copy.deepcopy(self.bundle["pattern_metadata"])
        pattern["applicability"]["target_runtimes"].append("pyspark")
        path = self.write_pattern(pattern, self.bundle["pattern_body"], "runtime-transfer.md")
        with self.assertRaisesRegex(learning.ValidationFailure, "contexts not present"):
            learning.validate_pattern(path)
        pattern = copy.deepcopy(self.bundle["pattern_metadata"])
        pattern["applicability"]["model_families"].append("different-model")
        path = self.write_pattern(pattern, self.bundle["pattern_body"], "model-transfer.md")
        with self.assertRaisesRegex(learning.ValidationFailure, "contexts not present"):
            learning.validate_pattern(path)

    def test_nonexistent_commit_and_wrong_git_diff_are_rejected(self) -> None:
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        proposal["candidate_commit"] = "f" * 40
        with self.assertRaisesRegex(learning.ValidationFailure, "commit does not exist"):
            learning.validate_proposal(self.write_json("missing-commit.json", proposal))
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        multi = self.make_candidate([".github/skills/test/SKILL.md", ".github/skills/validate/SKILL.md"])
        proposal["candidate_commit"] = multi
        with self.assertRaisesRegex(learning.ValidationFailure, "must change exactly"):
            learning.validate_proposal(self.write_json("multi-skill.json", proposal))

    def test_protected_contract_or_evaluator_change_is_rejected_by_diff(self) -> None:
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        protected = self.make_candidate([".github/skills/test/SKILL.md", "config/tieout.yaml"])
        proposal["candidate_commit"] = protected
        with self.assertRaisesRegex(learning.ValidationFailure, "must change exactly"):
            learning.validate_proposal(self.write_json("protected-change.json", proposal))
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        evaluator = self.make_candidate([".github/skills/test/SKILL.md", ".github/skills/test/evals/cases.md"])
        proposal["candidate_commit"] = evaluator
        with self.assertRaisesRegex(learning.ValidationFailure, "must change exactly"):
            learning.validate_proposal(self.write_json("evaluator-change.json", proposal))

    def test_tampered_patch_and_frozen_evaluator_are_rejected(self) -> None:
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        bad_patch = self.write_text("proposal/tampered.patch", "not the git diff\n")
        proposal["patch"] = self.ref(bad_patch)
        with self.assertRaisesRegex(learning.ValidationFailure, "patch content"):
            learning.validate_proposal(self.write_json("tampered-patch.json", proposal))
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        proposal["validation"]["runs"][0]["evaluator_sha256"] = "f" * 64
        with self.assertRaisesRegex(learning.ValidationFailure, "different evaluator hash"):
            learning.validate_proposal(self.write_json("changed-evaluator.json", proposal))

    def test_self_review_and_unreviewed_candidate_are_rejected(self) -> None:
        review = json.loads(self.bundle["review"].read_text(encoding="utf-8"))
        review["reviewer"]["identity"] = review["author_identity"]
        self_review = self.write_json("reviews/self-review.json", review)
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        proposal["independent_review"] = self.ref(self_review, "REVIEW-001")
        with self.assertRaisesRegex(learning.ValidationFailure, "cannot independently review"):
            learning.validate_proposal(self.write_json("self-reviewed-proposal.json", proposal))
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        proposal["independent_review"] = None
        with self.assertRaisesRegex(learning.ValidationFailure, "requires validation PASS and independent review"):
            learning.validate_proposal(self.write_json("unreviewed-proposal.json", proposal))

    def test_review_cannot_substitute_evaluator_command_or_result(self) -> None:
        original = json.loads(self.bundle["review"].read_text(encoding="utf-8"))
        review = copy.deepcopy(original)
        review["reruns"][0]["evaluator_sha256"] = "f" * 64
        path = self.write_json("reviews/substituted-evaluator.json", review)
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        proposal["independent_review"] = self.ref(path, "REVIEW-001")
        with self.assertRaisesRegex(learning.ValidationFailure, "substituted the frozen"):
            learning.validate_proposal(self.write_json("substituted-evaluator-proposal.json", proposal))

        review = copy.deepcopy(original)
        review["reruns"][0]["command"] = ["python3", "unrelated.py"]
        path = self.write_json("reviews/substituted-command.json", review)
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        proposal["independent_review"] = self.ref(path, "REVIEW-001")
        with self.assertRaisesRegex(learning.ValidationFailure, "changed the frozen"):
            learning.validate_proposal(self.write_json("substituted-command-proposal.json", proposal))

        review = copy.deepcopy(original)
        review["reruns"][0]["result_sha256"] = "e" * 64
        path = self.write_json("reviews/forged-result.json", review)
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        proposal["independent_review"] = self.ref(path, "REVIEW-001")
        with self.assertRaisesRegex(learning.ValidationFailure, "SHA-256 mismatch"):
            learning.validate_proposal(self.write_json("forged-result-proposal.json", proposal))

    def test_governance_regression_cannot_be_traded_for_pass(self) -> None:
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        proposal["validation"]["governance_regressions"] = ["weakened promotion gate"]
        with self.assertRaisesRegex(learning.ValidationFailure, "governance regressions"):
            learning.validate_proposal(self.write_json("unsafe-proposal.json", proposal))

    def test_secret_and_private_reasoning_content_are_rejected(self) -> None:
        observation = json.loads(self.bundle["observations"][0].read_text(encoding="utf-8"))
        observation["observable_events"] = ["pass" + "word=" + "abcdefghijklmnop"]
        with self.assertRaisesRegex(learning.ValidationFailure, "secret material"):
            learning.validate_observation(self.write_json("secret-observation.json", observation))
        observation["observable_events"] = ["Captured hidden reasoning from the model."]
        with self.assertRaisesRegex(learning.ValidationFailure, "private reasoning"):
            learning.validate_observation(self.write_json("reasoning-observation.json", observation))

    def test_promoted_change_requires_matching_human_gate(self) -> None:
        proposal = copy.deepcopy(self.bundle["proposal_data"])
        proposal["status"] = "PROMOTED"
        with self.assertRaisesRegex(learning.ValidationFailure, "requires human approval"):
            learning.validate_proposal(self.write_json("unapproved-promotion.json", proposal))

        state = {
            "run_id": "RUN-PROMOTION-001",
            "module_id": "FRAMEWORK-LEARNING",
            "stage": "learn_promotion",
            "status": "APPROVED",
            "attempts": 0,
            "history": [],
            "human_gate": {
                "gate_type": "learning_promotion",
                "subject_kind": "skill_proposal",
                "subject_id": "PROPOSAL-001",
                "candidate_commit": "f" * 40,
                "review_id": "REVIEW-001",
                "decision": "APPROVED",
                "actor_identity": "human-owner",
                "actor_role": "human_approver",
                "recorded_at": "2026-09-20T15:00:00Z",
            },
        }
        state_path = self.write_json("promotion-state.json", state)
        proposal["human_promotion"] = {
            "decision": "APPROVED",
            "run_state_path": self.rel(state_path),
            "run_state_sha256": digest(state_path),
            "promotion_commit": self.candidate,
            "github_review": {
                "repository": "example/repository",
                "pull_request": 1,
                "review_id": 1,
                "reviewer_login": "human-owner",
                "reviewed_commit": self.candidate,
            },
        }
        with self.assertRaisesRegex(learning.ValidationFailure, "candidate_commit does not match"):
            learning.validate_proposal(self.write_json("wrong-commit-promotion.json", proposal))

    def test_github_approval_verifier_binds_review_identity_state_and_commit(self) -> None:
        attestation = {
            "repository": "example/repository",
            "pull_request": 7,
            "review_id": 42,
            "reviewer_login": "human-reviewer",
            "reviewed_commit": self.candidate,
        }
        response = mock.Mock(
            returncode=0,
            stdout=json.dumps({
                "id": 42,
                "state": "APPROVED",
                "commit_id": self.candidate,
                "user": {"login": "human-reviewer", "type": "User"},
            }),
            stderr="",
        )
        with mock.patch.object(learning.subprocess, "run", return_value=response):
            REAL_VERIFY_GITHUB_APPROVAL(attestation, self.candidate, self.root / "proposal.json")

        bad = copy.deepcopy(response)
        bad.stdout = json.dumps({
            "id": 42,
            "state": "CHANGES_REQUESTED",
            "commit_id": self.candidate,
            "user": {"login": "human-reviewer", "type": "User"},
        })
        with mock.patch.object(learning.subprocess, "run", return_value=bad):
            with self.assertRaisesRegex(learning.ValidationFailure, "not the declared approved review"):
                REAL_VERIFY_GITHUB_APPROVAL(attestation, self.candidate, self.root / "proposal.json")


if __name__ == "__main__":
    unittest.main()
