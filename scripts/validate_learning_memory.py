#!/usr/bin/env python3
"""Validate governed learning-memory artifacts without executing migration work."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
REQUIRED_PATTERN_SECTIONS = [
    "## Observable symptoms",
    "## Evidence-backed strategy",
    "## Unsuccessful or rejected interventions",
    "## Applicability and preconditions",
    "## Does not prove",
    "## Candidate skill impact",
    "## Human decision",
]
SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|password|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}"),
]
PRIVATE_REASONING = re.compile(r"(?i)\b(?:chain[- ]of[- ]thought|hidden reasoning|private reasoning)\b")


class ValidationFailure(Exception):
    """Raised when a governed learning artifact violates its contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_repo_path(raw: str, source: Path) -> Path:
    relative = Path(raw)
    if relative.is_absolute():
        raise ValidationFailure(f"{source}: absolute paths are forbidden: {raw}")
    candidate = (ROOT / relative).resolve()
    root = ROOT.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValidationFailure(f"{source}: path escapes repository: {raw}")
    return candidate


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationFailure(f"{path}: cannot read valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationFailure(f"{path}: root must be an object")
    return value


def load_schema(name: str) -> dict[str, Any]:
    return load_json(CONTRACTS / name)


def validate_schema(instance: dict[str, Any], schema_name: str, source: Path) -> None:
    validator = Draft202012Validator(load_schema(schema_name), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    if errors:
        details = "; ".join(
            f"{'/'.join(str(item) for item in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors[:8]
        )
        raise ValidationFailure(f"{source}: schema validation failed: {details}")


def parse_pattern(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValidationFailure(f"{path}: pattern must start with YAML frontmatter")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValidationFailure(f"{path}: YAML frontmatter is not closed") from exc
    metadata = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(metadata, dict):
        raise ValidationFailure(f"{path}: frontmatter must be a mapping")
    return metadata, "\n".join(lines[end + 1 :])


def scan_text(value: str, source: Path) -> None:
    if PRIVATE_REASONING.search(value):
        raise ValidationFailure(f"{source}: private reasoning language is forbidden in learning records")
    for pattern in SECRET_PATTERNS:
        if pattern.search(value):
            raise ValidationFailure(f"{source}: possible secret material detected")


def scan_structure(value: Any, source: Path) -> None:
    if isinstance(value, dict):
        for child in value.values():
            scan_structure(child, source)
    elif isinstance(value, list):
        for child in value:
            scan_structure(child, source)
    elif isinstance(value, str):
        scan_text(value, source)


def verify_file_ref(ref: dict[str, Any], source: Path) -> Path:
    path = safe_repo_path(ref["path"], source)
    if not path.is_file():
        raise ValidationFailure(f"{source}: referenced file does not exist: {ref['path']}")
    actual = sha256_file(path)
    if actual != ref["sha256"]:
        raise ValidationFailure(f"{source}: SHA-256 mismatch for {ref['path']}: expected {ref['sha256']}, got {actual}")
    return path


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise ValidationFailure(f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result


def verify_commit(commit: str, source: Path) -> None:
    result = git("cat-file", "-e", f"{commit}^{{commit}}", check=False)
    if result.returncode != 0:
        raise ValidationFailure(f"{source}: Git commit does not exist: {commit}")


def verify_distinct_kinds(items: list[dict[str, Any]], source: Path) -> dict[str, dict[str, Any]]:
    by_kind = {item["kind"]: item for item in items}
    expected = {"architecture", "normal", "pressure"}
    if set(by_kind) != expected or len(items) != 3:
        raise ValidationFailure(f"{source}: exactly one architecture, normal, and pressure record is required")
    return by_kind


def validate_observation(path: Path) -> dict[str, Any]:
    observation = load_json(path)
    validate_schema(observation, "learning_observation.schema.json", path)
    if observation["record_status"] == "TEMPLATE":
        return observation
    scan_structure(observation, path)
    for ref in observation["input_evidence"] + observation["output_evidence"]:
        verify_file_ref(ref, path)
    if observation["outcome"] in {"FAIL", "BLOCKED"} and observation["failure"] is None:
        raise ValidationFailure(f"{path}: FAIL/BLOCKED observations require a failure classification")
    if observation["outcome"] == "PASS" and observation["failure"] is not None:
        raise ValidationFailure(f"{path}: PASS observations cannot carry an active failure")
    for decision in observation["human_decisions"]:
        if decision["status"] != "PENDING":
            actor = decision.get("decided_by")
            if not actor or actor["role"] != "human_approver" or not decision.get("decided_at"):
                raise ValidationFailure(f"{path}: completed human decisions require an attributable human approver and timestamp")
    author = observation["recorded_by"]["identity"]
    reviewer = observation["privacy_review"]["reviewer"]["identity"]
    if author == reviewer:
        raise ValidationFailure(f"{path}: privacy reviewer must be independent from the observation author")
    return observation


def validate_pattern(path: Path) -> dict[str, Any]:
    pattern, body = parse_pattern(path)
    validate_schema(pattern, "learning_pattern.schema.json", path)
    for heading in REQUIRED_PATTERN_SECTIONS:
        if heading not in body:
            raise ValidationFailure(f"{path}: missing required section {heading!r}")
    if pattern["record_status"] == "TEMPLATE":
        return pattern
    scan_structure(pattern, path)
    scan_text(body, path)
    runs: set[str] = set()
    signatures: set[tuple[Any, ...]] = set()
    observed_dimensions = {
        "source_platforms": set(),
        "migration_modes": set(),
        "semantic_boundaries": set(),
        "target_runtimes": set(),
        "model_families": set(),
        "population_scopes": set(),
    }
    for occurrence in pattern["occurrences"]:
        ref = {"path": occurrence["observation_path"], "sha256": occurrence["observation_sha256"]}
        observation_path = verify_file_ref(ref, path)
        observation = validate_observation(observation_path)
        if observation["observation_id"] != occurrence["observation_id"] or observation["run_id"] != occurrence["run_id"] or observation["module_id"] != occurrence["module_id"]:
            raise ValidationFailure(f"{path}: occurrence does not match its referenced observation")
        if pattern["pattern_id"] not in observation["candidate_pattern_ids"]:
            raise ValidationFailure(f"{path}: referenced observation does not nominate pattern {pattern['pattern_id']}")
        runs.add(occurrence["run_id"])
        context = occurrence["context"]
        verify_commit(context["source_commit"], path)
        context_refs = [context["run_state"], context["evaluator_manifest"], context["result"]]
        context_refs.extend(ref for ref in (context["fixture"], context["oracle"], context["expected_output"]) if ref is not None)
        verified_context: list[tuple[str, str]] = []
        for context_ref in context_refs:
            verify_file_ref(context_ref, path)
            verified_context.append((context_ref["path"], context_ref["sha256"]))
            if not any(evidence["path"] == context_ref["path"] and evidence["sha256"] == context_ref["sha256"] for evidence in observation["input_evidence"] + observation["output_evidence"]):
                raise ValidationFailure(f"{path}: recurrence context file is not cited by observation {occurrence['observation_id']}: {context_ref['path']}")
        run_state_path = safe_repo_path(context["run_state"]["path"], path)
        state = load_json(run_state_path)
        validate_schema(state, "run_state.schema.json", run_state_path)
        if state["run_id"] != occurrence["run_id"] or state["module_id"] != occurrence["module_id"]:
            raise ValidationFailure(f"{path}: recurrence run state does not match occurrence run/module")
        def ref_signature(ref: dict[str, Any] | None) -> tuple[str, str] | None:
            return None if ref is None else (ref["path"], ref["sha256"])

        signature = (
            context["source_commit"], ref_signature(context["fixture"]), ref_signature(context["oracle"]),
            ref_signature(context["expected_output"]), ref_signature(context["evaluator_manifest"]),
            context["agent_model"], context["target_runtime"], context["population_scope"],
        )
        signatures.add(signature)
        observed_dimensions["source_platforms"].add(context["source_platform"])
        observed_dimensions["migration_modes"].add(context["migration_mode"])
        observed_dimensions["semantic_boundaries"].add(context["semantic_boundary"])
        observed_dimensions["target_runtimes"].add(context["target_runtime"])
        observed_dimensions["model_families"].add(context["agent_model"])
        observed_dimensions["population_scopes"].add(context["population_scope"])
    if len(runs) < 2:
        raise ValidationFailure(f"{path}: reusable pattern requires at least two independent run IDs")
    if len(signatures) < 2:
        raise ValidationFailure(f"{path}: recurrence contexts are identical and cannot establish independence")
    review = pattern["independence_review"]
    if review["conclusion"] != "INDEPENDENT":
        raise ValidationFailure(f"{path}: reusable pattern requires an independent recurrence conclusion")
    author = pattern["consolidated_by"]["identity"]
    if review["reviewer"]["identity"] == author:
        raise ValidationFailure(f"{path}: recurrence reviewer must be independent from the consolidator")
    if pattern["sensitivity"]["reviewer"]["identity"] == author:
        raise ValidationFailure(f"{path}: privacy reviewer must be independent from the consolidator")
    for field, observed in observed_dimensions.items():
        claimed = set(pattern["applicability"][field])
        if not claimed <= observed:
            raise ValidationFailure(f"{path}: applicability {field} includes contexts not present in occurrence evidence")
    if pattern["status"] == "PROMOTED":
        promotion = pattern["promotion"]
        if promotion["promotion_commit"] is None:
            raise ValidationFailure(f"{path}: promoted pattern requires a promotion commit")
        verify_commit(promotion["promotion_commit"], path)
        external_review_id = str(promotion["github_review"]["review_id"]) if promotion["github_review"] else None
        validate_human_gate(
            promotion, path, "pattern", pattern["pattern_id"], promotion["promotion_commit"],
            external_review_id, promotion["github_review"],
        )
    return pattern


def validate_review(path: Path) -> dict[str, Any]:
    review = load_json(path)
    validate_schema(review, "learning_review.schema.json", path)
    if review["record_status"] == "TEMPLATE":
        return review
    scan_structure(review, path)
    verify_commit(review["candidate_commit"], path)
    if review["author_identity"] == review["reviewer"]["identity"]:
        raise ValidationFailure(f"{path}: proposal author cannot independently review the proposal")
    reruns = verify_distinct_kinds(review["reruns"], path)
    for result in reruns.values():
        verify_file_ref({"path": result["result_path"], "sha256": result["result_sha256"]}, path)
    if review["verdict"] == "ACCEPT":
        if review["github_review"] is None or review["github_review"]["reviewer_login"] != review["reviewer"]["identity"]:
            raise ValidationFailure(f"{path}: ACCEPT requires an authenticated GitHub review by the named checker")
        verify_github_approval(review["github_review"], review["candidate_commit"], path)
        for kind, result in reruns.items():
            if result["result"] != "PASS" or result["exit_code"] != 0:
                raise ValidationFailure(f"{path}: accepted review requires PASS and exit code 0 for {kind}")
    return review


def verify_github_approval(attestation: dict[str, Any] | None, candidate_commit: str, source: Path) -> None:
    if attestation is None:
        raise ValidationFailure(f"{source}: promoted artifact requires a GitHub approval attestation")
    if attestation["reviewed_commit"] != candidate_commit:
        raise ValidationFailure(f"{source}: GitHub approval attestation targets the wrong commit")
    endpoint = f"repos/{attestation['repository']}/pulls/{attestation['pull_request']}/reviews/{attestation['review_id']}"
    result = subprocess.run(["gh", "api", endpoint], cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise ValidationFailure(f"{source}: cannot verify GitHub approval with the authenticated connector: {result.stderr.strip() or result.stdout.strip()}")
    try:
        review = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValidationFailure(f"{source}: GitHub approval response is not valid JSON") from exc
    if review.get("id") != attestation["review_id"] or review.get("state") != "APPROVED":
        raise ValidationFailure(f"{source}: GitHub review is not the declared approved review")
    user = review.get("user") or {}
    if user.get("login") != attestation["reviewer_login"] or user.get("type") != "User":
        raise ValidationFailure(f"{source}: GitHub reviewer identity does not match the attestation")
    if review.get("commit_id") != candidate_commit:
        raise ValidationFailure(f"{source}: GitHub review did not approve the promoted commit")


def validate_human_gate(gate: dict[str, Any], source: Path, subject_kind: str, subject_id: str, candidate_commit: str, review_id: str | None, github_review: dict[str, Any] | None) -> None:
    decision = gate["human_decision"] if "human_decision" in gate else gate["decision"]
    if decision != "APPROVED":
        raise ValidationFailure(f"{source}: promoted artifact requires human approval")
    if not gate.get("run_state_path") or not gate.get("run_state_sha256"):
        raise ValidationFailure(f"{source}: approved promotion requires a run-state path and SHA-256")
    ref = {
        "path": gate["run_state_path"],
        "sha256": gate["run_state_sha256"],
    }
    state_path = verify_file_ref(ref, source)
    state = load_json(state_path)
    validate_schema(state, "run_state.schema.json", state_path)
    record = state.get("human_gate") or {}
    if state.get("stage") != "learn_promotion" or state.get("status") != "APPROVED":
        raise ValidationFailure(f"{source}: promotion run state is not learn_promotion/APPROVED")
    expected = {
        "gate_type": "learning_promotion",
        "subject_kind": subject_kind,
        "subject_id": subject_id,
        "candidate_commit": candidate_commit,
        "review_id": review_id,
        "decision": "APPROVED",
        "actor_role": "human_approver",
    }
    for key, value in expected.items():
        if record.get(key) != value:
            raise ValidationFailure(f"{source}: promotion run state {key} does not match the promoted artifact")
    if not record.get("actor_identity") or not record.get("recorded_at"):
        raise ValidationFailure(f"{source}: promotion run state lacks attributable human identity or timestamp")
    if github_review is None:
        raise ValidationFailure(f"{source}: promoted artifact requires a GitHub approval attestation")
    if record["actor_identity"] != github_review["reviewer_login"]:
        raise ValidationFailure(f"{source}: durable human actor does not match the authenticated GitHub reviewer")
    verify_github_approval(github_review, candidate_commit, source)


def validate_proposal(path: Path) -> dict[str, Any]:
    proposal = load_json(path)
    validate_schema(proposal, "skill_change_proposal.schema.json", path)
    expected_path = f".github/skills/{proposal['target_skill']}/SKILL.md"
    if proposal["target_skill_path"] != expected_path:
        raise ValidationFailure(f"{path}: target_skill_path must match target_skill")
    if proposal["record_status"] == "TEMPLATE":
        return proposal
    scan_structure(proposal, path)
    target = safe_repo_path(proposal["target_skill_path"], path)
    if not target.is_file():
        raise ValidationFailure(f"{path}: declared target skill does not exist")
    for ref in proposal["source_patterns"]:
        pattern_path = verify_file_ref(ref, path)
        pattern = validate_pattern(pattern_path)
        if pattern["pattern_id"] != ref["id"]:
            raise ValidationFailure(f"{path}: source pattern ID does not match {ref['path']}")
    verify_commit(proposal["baseline_commit"], path)
    candidate = proposal["candidate_commit"]
    if candidate is not None:
        verify_commit(candidate, path)
        if git("merge-base", "--is-ancestor", proposal["baseline_commit"], candidate, check=False).returncode != 0:
            raise ValidationFailure(f"{path}: baseline commit is not an ancestor of candidate commit")
        changed = [line for line in git("diff", "--name-only", proposal["baseline_commit"], candidate).stdout.splitlines() if line]
        if changed != [proposal["target_skill_path"]]:
            raise ValidationFailure(f"{path}: candidate diff must change exactly {proposal['target_skill_path']}; got {changed}")
        patch_path = verify_file_ref(proposal["patch"], path)
        expected_patch = git("diff", "--binary", proposal["baseline_commit"], candidate, "--", proposal["target_skill_path"]).stdout.encode("utf-8")
        if patch_path.read_bytes() != expected_patch:
            raise ValidationFailure(f"{path}: patch content does not match the declared Git diff")
    elif proposal["status"] not in {"DRAFT", "TEMPLATE"}:
        raise ValidationFailure(f"{path}: non-draft proposal requires a candidate commit")
    evaluators = verify_distinct_kinds(proposal["frozen_evaluators"], path)
    for item in evaluators.values():
        verify_file_ref(item, path)
    runs = verify_distinct_kinds(proposal["validation"]["runs"], path)
    for kind, result in runs.items():
        verify_file_ref({"path": result["result_path"], "sha256": result["result_sha256"]}, path)
        if result["evaluator_sha256"] != evaluators[kind]["sha256"]:
            raise ValidationFailure(f"{path}: {kind} validation used a different evaluator hash")
    validation = proposal["validation"]
    if validation["result"] == "PASS":
        for kind, result in runs.items():
            if result["result"] != "PASS" or result["exit_code"] != 0:
                raise ValidationFailure(f"{path}: PASS requires successful {kind} validation")
        if validation["governance_regressions"]:
            raise ValidationFailure(f"{path}: PASS cannot contain governance regressions")
        if not validation["target_improved_or_defect_resolved"]:
            raise ValidationFailure(f"{path}: PASS must demonstrate improvement or resolve the evidenced defect")
    if proposal["status"] in {"CANDIDATE_FOR_PROMOTION", "PROMOTED"}:
        if validation["result"] != "PASS" or proposal["independent_review"] is None:
            raise ValidationFailure(f"{path}: candidate or promoted change requires validation PASS and independent review")
        review_path = verify_file_ref(proposal["independent_review"], path)
        review = validate_review(review_path)
        if review["review_id"] != proposal["independent_review"]["id"] or review["proposal_id"] != proposal["proposal_id"]:
            raise ValidationFailure(f"{path}: independent review identifiers do not match proposal")
        if review["author_identity"] != proposal["author"]["identity"] or review["candidate_commit"] != candidate:
            raise ValidationFailure(f"{path}: independent review does not cover the proposal author and candidate commit")
        if review["verdict"] != "ACCEPT":
            raise ValidationFailure(f"{path}: candidate promotion requires an ACCEPT review")
        review_runs = verify_distinct_kinds(review["reruns"], path)
        for kind in ("architecture", "normal", "pressure"):
            if review_runs[kind]["evaluator_sha256"] != evaluators[kind]["sha256"]:
                raise ValidationFailure(f"{path}: independent review substituted the frozen {kind} evaluator")
            if review_runs[kind]["command"] != runs[kind]["command"]:
                raise ValidationFailure(f"{path}: independent review changed the frozen {kind} command")
    if proposal["status"] == "PROMOTED":
        assert proposal["independent_review"] is not None
        validate_human_gate(
            proposal["human_promotion"], path, "skill_proposal", proposal["proposal_id"],
            candidate, proposal["independent_review"]["id"], proposal["human_promotion"]["github_review"],
        )
        if proposal["human_promotion"]["promotion_commit"] != candidate:
            raise ValidationFailure(f"{path}: promotion commit must equal the reviewed candidate commit")
    return proposal


def discover(kind: str) -> list[Path]:
    locations = {
        "observation": ROOT / "artifacts/learning/observations",
        "pattern": ROOT / "docs/learning/patterns",
        "proposal": ROOT / "artifacts/learning/proposals",
        "review": ROOT / "artifacts/learning/reviews",
    }
    suffixes = {"observation": "*.json", "pattern": "*.md", "proposal": "*.json", "review": "*.json"}
    location = locations[kind]
    return sorted(path for path in location.rglob(suffixes[kind]) if path.name != ".gitkeep") if location.exists() else []


def reconcile_indexes() -> None:
    index = (ROOT / "docs/learning/index.md").read_text(encoding="utf-8")
    evolution = (ROOT / "docs/learning/evolution-log.md").read_text(encoding="utf-8")
    impact = (ROOT / "docs/learning/skill-impact.md").read_text(encoding="utf-8")
    for path in discover("observation"):
        identifier = load_json(path)["observation_id"]
        if identifier not in evolution:
            raise ValidationFailure(f"{path}: observation is missing from evolution-log.md")
    for path in discover("pattern"):
        identifier = parse_pattern(path)[0]["pattern_id"]
        if identifier not in index or identifier not in evolution:
            raise ValidationFailure(f"{path}: pattern is missing from index.md or evolution-log.md")
    for path in discover("proposal"):
        identifier = load_json(path)["proposal_id"]
        if identifier not in impact or identifier not in evolution:
            raise ValidationFailure(f"{path}: proposal is missing from skill-impact.md or evolution-log.md")
    for path in discover("review"):
        identifier = load_json(path)["review_id"]
        if identifier not in evolution:
            raise ValidationFailure(f"{path}: review is missing from evolution-log.md")


def validate_append_only(base_ref: str) -> None:
    verify_commit(base_ref, ROOT / "<base-ref>")
    history_paths = [
        "docs/learning/index.md",
        "docs/learning/evolution-log.md",
        "docs/learning/skill-impact.md",
    ]
    diff = git("diff", "--unified=0", base_ref, "--", *history_paths).stdout.splitlines()
    removed = [line for line in diff if line.startswith("-") and not line.startswith("---")]
    if removed:
        raise ValidationFailure(f"learning history is not append-only relative to {base_ref}: {removed[:3]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observation", action="append", default=[], type=Path)
    parser.add_argument("--pattern", action="append", default=[], type=Path)
    parser.add_argument("--proposal", action="append", default=[], type=Path)
    parser.add_argument("--review", action="append", default=[], type=Path)
    parser.add_argument("--all", action="store_true", help="Validate every active learning-memory artifact")
    parser.add_argument("--templates", action="store_true", help="Validate the committed inert templates")
    parser.add_argument("--base-ref", help="Require indexes and logs to contain no deleted lines relative to this commit")
    args = parser.parse_args()

    work: list[tuple[str, Path]] = []
    work.extend(("observation", path) for path in args.observation)
    work.extend(("pattern", path) for path in args.pattern)
    work.extend(("proposal", path) for path in args.proposal)
    work.extend(("review", path) for path in args.review)
    if args.all:
        for kind in ("observation", "pattern", "proposal", "review"):
            work.extend((kind, path) for path in discover(kind))
    if args.templates or not work:
        base = ROOT / ".github/skills/learn/templates"
        work.extend([
            ("observation", base / "learning_observation.template.json"),
            ("pattern", base / "learning_pattern.template.md"),
            ("proposal", base / "skill_change_proposal.template.json"),
            ("review", base / "learning_review.template.json"),
        ])

    validators = {
        "observation": validate_observation,
        "pattern": validate_pattern,
        "proposal": validate_proposal,
        "review": validate_review,
    }
    errors: list[str] = []
    seen: set[tuple[str, Path]] = set()
    for kind, raw_path in work:
        try:
            if raw_path.is_absolute():
                path = raw_path.resolve()
                root = ROOT.resolve()
                if path != root and root not in path.parents:
                    raise ValidationFailure(f"{ROOT / '<cli>'}: path escapes repository: {raw_path}")
            else:
                path = safe_repo_path(str(raw_path), ROOT / "<cli>")
        except ValidationFailure as exc:
            errors.append(str(exc))
            continue
        key = (kind, path.resolve())
        if key in seen:
            continue
        seen.add(key)
        if not path.is_file():
            errors.append(f"{path}: file does not exist")
            continue
        try:
            validators[kind](path)
        except (OSError, yaml.YAMLError, ValidationFailure) as exc:
            errors.append(str(exc))

    if args.all:
        try:
            reconcile_indexes()
        except (OSError, yaml.YAMLError, ValidationFailure) as exc:
            errors.append(str(exc))
    if args.base_ref:
        try:
            validate_append_only(args.base_ref)
        except ValidationFailure as exc:
            errors.append(str(exc))

    if errors:
        print("LEARNING MEMORY VALIDATION: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"LEARNING MEMORY VALIDATION: PASS ({len(seen)} artifacts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
