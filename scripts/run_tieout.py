#!/usr/bin/env python3
"""Execute an approved, module-neutral keyed SAS-to-Python tie-out contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SCHEMA = ROOT / "contracts" / "tieout_contract.schema.json"
RESULT_SCHEMA = ROOT / "contracts" / "tieout_result.schema.json"
FIXTURE_SCHEMA = ROOT / "contracts" / "fixture_manifest.schema.json"
EVIDENCE_SCHEMA = ROOT / "contracts" / "evidence_bundle.schema.json"
NULL_VALUES = {"", ".", "NA", "N/A", "NULL", "None", "null"}


class TieoutError(RuntimeError):
    """A deterministic contract, provenance, producer, or comparison failure."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        shell=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "UNAVAILABLE"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_document(document: Mapping[str, Any], schema_path: Path, label: str) -> None:
    validator = Draft202012Validator(load_json(schema_path))
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path))
    if errors:
        details = "; ".join(
            f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors[:10]
        )
        raise TieoutError(f"{label} schema validation failed: {details}")


def resolve_repo_path(value: str, label: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        raise TieoutError(f"{label} must be repository-relative: {value}")
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise TieoutError(f"{label} escapes the repository: {value}") from exc
    return resolved


def require_file(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise TieoutError(f"Missing non-empty {label}: {path.relative_to(ROOT)}")


def verify_hash(path: Path, expected: str, label: str) -> str:
    actual = sha256_file(path)
    if actual != expected:
        raise TieoutError(f"{label} hash mismatch for {path.relative_to(ROOT)}: expected {expected}, got {actual}")
    return actual


def substitute(value: str, tokens: Mapping[str, str]) -> str:
    output = value
    for name, replacement in tokens.items():
        output = output.replace("{" + name + "}", replacement)
    if "{" in output or "}" in output:
        raise TieoutError(f"Unsupported or unresolved command token: {value}")
    return output


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise TieoutError(f"CSV has no header: {path.relative_to(ROOT)}")
        return list(reader.fieldnames), list(reader)


def key_tuple(row: Mapping[str, str], columns: Sequence[str]) -> tuple[str, ...]:
    return tuple(str(row[column]) for column in columns)


def key_hash(key: Sequence[str]) -> str:
    encoded = json.dumps(list(key), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def selected_keys_digest(keys: Sequence[Sequence[str]]) -> str:
    hashes = sorted(key_hash(key) for key in keys)
    return hashlib.sha256(("\n".join(hashes) + "\n").encode("utf-8")).hexdigest()


def index_rows(
    rows: Sequence[Mapping[str, str]],
    keys: Sequence[str],
) -> tuple[dict[tuple[str, ...], Mapping[str, str]], list[tuple[str, ...]]]:
    indexed: dict[tuple[str, ...], Mapping[str, str]] = {}
    duplicates: list[tuple[str, ...]] = []
    for row in rows:
        row_key = key_tuple(row, keys)
        if row_key in indexed:
            duplicates.append(row_key)
        else:
            indexed[row_key] = row
    return indexed, duplicates


def is_null(value: str) -> bool:
    return value.strip() in NULL_VALUES


def public_value(value: str) -> str | float | None:
    if is_null(value):
        return None
    try:
        number = float(value)
    except ValueError:
        return value[:200]
    return number if math.isfinite(number) else value[:200]


def compare_value(expected: str, actual: str, rule: Mapping[str, Any]) -> tuple[bool, float | None, str]:
    expected_null = is_null(expected)
    actual_null = is_null(actual)
    if expected_null or actual_null:
        if expected_null and actual_null and bool(rule["null_equal"]):
            return True, None, "both_null"
        return False, None, "null_mismatch"

    mode = str(rule["mode"])
    if mode == "exact":
        return expected == actual, None, "exact_mismatch" if expected != actual else "match"

    try:
        expected_number = float(expected)
        actual_number = float(actual)
    except ValueError:
        return False, None, "non_numeric_value"
    if not math.isfinite(expected_number) or not math.isfinite(actual_number):
        return False, None, "non_finite_value"

    absolute_delta = abs(expected_number - actual_number)
    if mode == "absolute":
        delta = absolute_delta
    elif mode == "relative":
        scale = max(abs(expected_number), float(rule.get("scale_floor", 1e-15)))
        delta = absolute_delta / scale
    else:
        raise TieoutError(f"Unsupported comparison mode: {mode}")
    tolerance = float(rule["tolerance"])
    return delta <= tolerance, delta, "tolerance_exceeded" if delta > tolerance else "match"


def output_path(pattern: str, run_id: str, attempt_id: str, label: str) -> Path:
    path = resolve_repo_path(substitute(pattern, {"run_id": run_id, "attempt_id": attempt_id}), label)
    required_parent = (ROOT / "artifacts" / "evidence" / "runs" / run_id / "attempts" / attempt_id).resolve()
    try:
        path.relative_to(required_parent)
    except ValueError as exc:
        raise TieoutError(f"{label} must be under artifacts/evidence/runs/{run_id}/attempts/{attempt_id}/") from exc
    return path


def write_json(path: Path, document: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def result_population_scope(contract: Mapping[str, Any]) -> dict[str, Any]:
    scope = contract["scope"]
    return {
        "population_choice": scope["population_choice"],
        "current_phase": scope["current_phase"],
        "record_count": scope["record_count"],
        "selection_policy": scope["selection_policy"],
        "full_population_followup_required": scope["full_population_followup_required"],
        "decision_source": scope["decision_source"],
        "rationale": scope["rationale"],
    }


def blocked_result(
    contract: Mapping[str, Any],
    contract_path: Path,
    contract_hash: str,
    run_id: str,
    attempt_id: str,
    producer: Mapping[str, Any],
    reason: str,
    fixture_coverage: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    return {
        "module_id": str(contract["module_id"]),
        "run_id": run_id,
        "attempt_id": attempt_id,
        "gate": "local_parity_tieout",
        "status": "BLOCKED",
        "population_scope": result_population_scope(contract),
        "contract": {
            "path": contract_path.relative_to(ROOT).as_posix(),
            "sha256": contract_hash,
            "version": str(contract["contract_version"]),
        },
        "producer": producer,
        "fixture_coverage": dict(fixture_coverage or {"mandatory_assertions": 0, "passed": 0, "failed": 0}),
        "row_counts": {"expected": 0, "actual": 0, "matched": 0},
        "key_result": {
            "missing_count": 0,
            "extra_count": 0,
            "duplicate_expected_count": 0,
            "duplicate_actual_count": 0,
        },
        "comparisons": [
            {
                "name": str(rule["name"]),
                "mode": str(rule["mode"]),
                "tolerance": rule.get("tolerance"),
                "compared": 0,
                "failures": 0,
                "max_delta": None,
            }
            for rule in contract["comparisons"]
        ],
        "mismatches": [],
        "limitations": list(contract["scope"]["does_not_prove"]) + [reason],
    }


def render_summary(result: Mapping[str, Any], contract: Mapping[str, Any]) -> str:
    lines = [
        f"# {result['module_id']} Local Parity Result",
        "",
        f"> **{result['status']}** — governed SAS-to-Python keyed tie-out for run `{result['run_id']}`, attempt `{result['attempt_id']}`.",
        "",
        "## Approved population",
        "",
        f"- **Choice:** `{result['population_scope']['population_choice']}`",
        f"- **Current phase:** `{result['population_scope']['current_phase']}`",
        f"- **Record count:** `{result['population_scope']['record_count']}`",
        f"- **Selection policy:** {result['population_scope']['selection_policy']}",
        f"- **Full-population follow-up required:** `{result['population_scope']['full_population_followup_required']}`",
        f"- **Decision source:** {result['population_scope']['decision_source']}",
        f"- **Rationale:** {result['population_scope']['rationale']}",
        "",
        "## Scoreboard",
        "",
        "| Measure | Result |",
        "|---|---:|",
        f"| Expected rows | {result['row_counts']['expected']} |",
        f"| Actual rows | {result['row_counts']['actual']} |",
        f"| Matched keys | {result['row_counts']['matched']} |",
        f"| Missing keys | {result['key_result']['missing_count']} |",
        f"| Extra keys | {result['key_result']['extra_count']} |",
        f"| Duplicate expected keys | {result['key_result']['duplicate_expected_count']} |",
        f"| Duplicate actual keys | {result['key_result']['duplicate_actual_count']} |",
        f"| Mandatory fixture assertions passed | {result['fixture_coverage']['passed']} / {result['fixture_coverage']['mandatory_assertions']} |",
        "",
        "## Configured comparisons",
        "",
        "| Comparison | Mode | Tolerance | Compared | Failures | Maximum delta |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for comparison in result["comparisons"]:
        tolerance = "n/a" if comparison["tolerance"] is None else str(comparison["tolerance"])
        maximum = "n/a" if comparison["max_delta"] is None else str(comparison["max_delta"])
        lines.append(
            f"| {comparison['name']} | {comparison['mode']} | {tolerance} | {comparison['compared']} | {comparison['failures']} | {maximum} |"
        )
    lines.extend(["", "## Decision basis", "", f"- **Source:** {contract['decision_basis']['source']}", f"- **Rationale:** {contract['decision_basis']['rationale']}", "", "## Proof boundary", ""])
    lines.extend(f"- {item}" for item in result["limitations"])
    return "\n".join(lines) + "\n"


def build_evidence(
    result: Mapping[str, Any],
    contract: Mapping[str, Any],
    result_path: Path,
    summary_path: Path,
    contract_path: Path,
    contract_hash: str,
    intake_path: Path,
    intake_hash: str,
    oracle_path: Path,
    oracle_hash: str,
    fixture_path: Path,
    fixture_hash: str,
    actual_path: Path | None,
) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = [
        {"type": "tieout_result", "path": result_path.relative_to(ROOT).as_posix(), "sha256": sha256_file(result_path)},
        {"type": "tieout_summary", "path": summary_path.relative_to(ROOT).as_posix(), "sha256": sha256_file(summary_path)},
        {"type": "intake_manifest", "path": intake_path.relative_to(ROOT).as_posix(), "sha256": intake_hash},
        {"type": "oracle", "path": oracle_path.relative_to(ROOT).as_posix(), "sha256": oracle_hash},
        {"type": "fixture_manifest", "path": fixture_path.relative_to(ROOT).as_posix(), "sha256": fixture_hash},
    ]
    if actual_path is not None and actual_path.is_file():
        artifacts.append(
            {"type": "actual_output", "path": actual_path.relative_to(ROOT).as_posix(), "sha256": sha256_file(actual_path)}
        )
    runner_path = ROOT / "scripts" / "run_tieout.py"
    return {
        "module_id": result["module_id"],
        "gate": "local_parity_tieout",
        "status": result["status"],
        "artifacts": artifacts,
        "provenance": {
            "run_id": result["run_id"],
            "attempt_id": result["attempt_id"],
            "git_commit": git_commit(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "runner_path": "scripts/run_tieout.py",
            "runner_sha256": sha256_file(runner_path) if runner_path.is_file() else "UNAVAILABLE",
            "contract_path": contract_path.relative_to(ROOT).as_posix(),
            "contract_sha256": contract_hash,
            "intake_manifest_path": intake_path.relative_to(ROOT).as_posix(),
            "intake_manifest_sha256": intake_hash,
            "fixture_manifest_path": fixture_path.relative_to(ROOT).as_posix(),
            "fixture_manifest_sha256": fixture_hash,
            "oracle_path": oracle_path.relative_to(ROOT).as_posix(),
            "oracle_sha256": oracle_hash,
            "oracle_format": contract["oracle"]["format"],
            "oracle_representation_note": contract["oracle"]["representation_note"],
            "actual_output_path": actual_path.relative_to(ROOT).as_posix() if actual_path is not None and actual_path.is_file() else None,
            "actual_output_sha256": sha256_file(actual_path) if actual_path is not None and actual_path.is_file() else None,
            "decision_basis": contract["decision_basis"],
            "producer_command": result["producer"]["command"],
            "producer_cwd": result["producer"]["cwd"],
            "producer_return_code": result["producer"]["return_code"],
        },
        "summary": {
            "population_scope": result["population_scope"],
            "row_counts": result["row_counts"],
            "key_result": result["key_result"],
            "fixture_coverage": result["fixture_coverage"],
            "comparisons": result["comparisons"],
            "decision_basis": contract["decision_basis"],
        },
        "limitations": result["limitations"],
    }


def execute(contract_path: Path, run_id: str, attempt_id: str) -> int:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", attempt_id):
        raise TieoutError("attempt_id must contain only letters, digits, dot, underscore, or hyphen")
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    if not isinstance(contract, dict):
        raise TieoutError("Tie-out contract must be a YAML mapping")
    validate_document(contract, CONTRACT_SCHEMA, "Tie-out contract")
    if contract["status"] != "APPROVED" or contract["oracle_lock"]["status"] != "APPROVED":
        raise TieoutError("Tie-out contract and oracle lock must be human-approved before execution")

    contract_hash = sha256_file(contract_path)
    intake_path = resolve_repo_path(str(contract["intake_manifest"]["path"]), "intake_manifest.path")
    oracle_path = resolve_repo_path(str(contract["oracle"]["path"]), "oracle.path")
    fixture_path = resolve_repo_path(str(contract["fixture_manifest"]["path"]), "fixture_manifest.path")
    actual_pattern = str(contract["producer"]["actual_output_path"])
    actual_path = resolve_repo_path(substitute(actual_pattern, {"run_id": run_id, "attempt_id": attempt_id}), "producer.actual_output_path")
    required_actual_parent = (ROOT / "artifacts" / "generated" / run_id / attempt_id).resolve()
    try:
        actual_path.relative_to(required_actual_parent)
    except ValueError as exc:
        raise TieoutError(f"producer.actual_output_path must be under artifacts/generated/{run_id}/{attempt_id}/") from exc

    require_file(intake_path, "intake manifest")
    require_file(oracle_path, "oracle")
    require_file(fixture_path, "fixture manifest")
    intake_hash = verify_hash(intake_path, str(contract["intake_manifest"]["sha256"]), "Intake manifest")
    if str(contract["oracle"]["format"]).lower() != "csv":
        raise TieoutError("The generic tie-out runner currently requires oracle.format: csv")
    oracle_hash = verify_hash(oracle_path, str(contract["oracle"]["sha256"]), "Oracle")
    fixture_hash = verify_hash(fixture_path, str(contract["fixture_manifest"]["sha256"]), "Fixture manifest")
    fixture_document = load_json(fixture_path)
    validate_document(fixture_document, FIXTURE_SCHEMA, "Fixture manifest")
    if fixture_document["module_id"] != contract["module_id"]:
        raise TieoutError("Fixture manifest module_id does not match the tie-out contract")
    if fixture_document["record_count"] != contract["scope"]["record_count"]:
        raise TieoutError("Fixture manifest record_count does not match the tie-out contract")
    if fixture_document["key_columns"] != contract["key_columns"]:
        raise TieoutError("Fixture manifest key_columns do not match the tie-out contract")
    if fixture_document["oracle"]["path"] != contract["oracle"]["path"] or fixture_document["oracle"]["sha256"] != oracle_hash:
        raise TieoutError("Fixture manifest oracle lock does not match the tie-out contract")

    selector_path = resolve_repo_path(str(fixture_document["selector"]["path"]), "fixture.selector.path")
    require_file(selector_path, "fixture selector")
    verify_hash(selector_path, str(fixture_document["selector"]["sha256"]), "Fixture selector")
    for index, item in enumerate(fixture_document["sources"]):
        source_path = resolve_repo_path(str(item["path"]), f"fixture.sources[{index}].path")
        require_file(source_path, f"fixture source {index}")
        verify_hash(source_path, str(item["sha256"]), f"Fixture source {index}")
    for index, item in enumerate(fixture_document["fixture_inputs"]):
        input_path = resolve_repo_path(str(item["path"]), f"fixture.fixture_inputs[{index}].path")
        require_file(input_path, f"fixture input {index}")
        verify_hash(input_path, str(item["sha256"]), f"Fixture input {index}")

    mandatory_assertions = [item for item in fixture_document["coverage_assertions"] if item["mandatory"]]
    failed_assertions = [item for item in mandatory_assertions if item["status"] != "PASS"]
    fixture_coverage = {
        "mandatory_assertions": len(mandatory_assertions),
        "passed": len(mandatory_assertions) - len(failed_assertions),
        "failed": len(failed_assertions),
    }
    if failed_assertions:
        names = [str(item["name"]) for item in failed_assertions]
        raise TieoutError(f"Mandatory fixture coverage assertions failed: {names}")

    cwd = resolve_repo_path(str(contract["producer"]["cwd"]), "producer.cwd")
    if not cwd.is_dir():
        raise TieoutError(f"Producer working directory does not exist: {cwd.relative_to(ROOT)}")
    actual_path.parent.mkdir(parents=True, exist_ok=True)
    if actual_path.exists():
        actual_path.unlink()

    tokens = {
        "python": sys.executable,
        "root": str(ROOT),
        "run_id": run_id,
        "attempt_id": attempt_id,
        "actual_output_path": str(actual_path),
        "fixture_manifest_path": str(fixture_path),
        "intake_manifest_path": str(intake_path),
    }
    command = [substitute(str(item), tokens) for item in contract["producer"]["command"]]
    producer_record: dict[str, Any] = {
        "command": command,
        "cwd": cwd.relative_to(ROOT).as_posix(),
        "return_code": -1,
        "stdout": "",
        "stderr": "",
    }
    result_path = output_path(str(contract["output"]["result_path"]), run_id, attempt_id, "output.result_path")
    summary_path = output_path(str(contract["output"]["summary_path"]), run_id, attempt_id, "output.summary_path")
    evidence_path = output_path(str(contract["output"]["evidence_path"]), run_id, attempt_id, "output.evidence_path")

    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=int(contract["producer"]["timeout_seconds"]),
            check=False,
            shell=False,
        )
        producer_record.update(
            return_code=completed.returncode,
            stdout=completed.stdout[-20000:],
            stderr=completed.stderr[-20000:],
        )
    except subprocess.TimeoutExpired as exc:
        producer_record.update(
            return_code=124,
            stdout=(exc.stdout or "")[-20000:] if isinstance(exc.stdout, str) else "",
            stderr=(exc.stderr or "")[-20000:] if isinstance(exc.stderr, str) else "",
        )
        result = blocked_result(contract, contract_path, contract_hash, run_id, attempt_id, producer_record, "Producer timed out", fixture_coverage)
        validate_document(result, RESULT_SCHEMA, "Tie-out result")
        write_json(result_path, result)
        summary_path.write_text(render_summary(result, contract), encoding="utf-8")
        evidence = build_evidence(result, contract, result_path, summary_path, contract_path, contract_hash, intake_path, intake_hash, oracle_path, oracle_hash, fixture_path, fixture_hash, None)
        validate_document(evidence, EVIDENCE_SCHEMA, "Evidence bundle")
        write_json(evidence_path, evidence)
        print(f"Tie-out status: BLOCKED\nEvidence: {evidence_path.relative_to(ROOT)}")
        return 3

    if producer_record["return_code"] != 0 or not actual_path.is_file() or actual_path.stat().st_size == 0:
        reason = "Producer failed" if producer_record["return_code"] != 0 else "Producer did not create a non-empty actual-output CSV"
        result = blocked_result(contract, contract_path, contract_hash, run_id, attempt_id, producer_record, reason, fixture_coverage)
        validate_document(result, RESULT_SCHEMA, "Tie-out result")
        write_json(result_path, result)
        summary_path.write_text(render_summary(result, contract), encoding="utf-8")
        evidence = build_evidence(result, contract, result_path, summary_path, contract_path, contract_hash, intake_path, intake_hash, oracle_path, oracle_hash, fixture_path, fixture_hash, actual_path)
        validate_document(evidence, EVIDENCE_SCHEMA, "Evidence bundle")
        write_json(evidence_path, evidence)
        print(f"Tie-out status: BLOCKED\nEvidence: {evidence_path.relative_to(ROOT)}")
        return 3

    expected_fields, expected_rows = read_csv(oracle_path)
    actual_fields, actual_rows = read_csv(actual_path)
    keys = [str(item) for item in contract["key_columns"]]
    required_expected = keys + [str(rule["expected_column"]) for rule in contract["comparisons"]]
    required_actual = keys + [str(rule["actual_column"]) for rule in contract["comparisons"]]
    missing_expected_columns = sorted(set(required_expected) - set(expected_fields))
    missing_actual_columns = sorted(set(required_actual) - set(actual_fields))
    if missing_expected_columns or missing_actual_columns:
        raise TieoutError(
            f"Required columns missing; oracle={missing_expected_columns}, actual={missing_actual_columns}"
        )

    expected_by_key, duplicate_expected = index_rows(expected_rows, keys)
    actual_by_key, duplicate_actual = index_rows(actual_rows, keys)
    expected_selection_digest = selected_keys_digest(list(expected_by_key))
    if expected_selection_digest != fixture_document["selected_key_hashes_sha256"]:
        raise TieoutError("Oracle key selection digest does not match the governed fixture manifest")
    missing_keys = sorted(set(expected_by_key) - set(actual_by_key))
    extra_keys = sorted(set(actual_by_key) - set(expected_by_key))
    matched_keys = sorted(set(expected_by_key) & set(actual_by_key))

    mismatch_limit = int(contract["privacy"]["max_mismatches"])
    mismatches: list[dict[str, Any]] = []
    comparison_results: list[dict[str, Any]] = []
    for rule in contract["comparisons"]:
        compared = 0
        failures = 0
        deltas: list[float] = []
        for row_key in matched_keys:
            expected_value = str(expected_by_key[row_key][str(rule["expected_column"])])
            actual_value = str(actual_by_key[row_key][str(rule["actual_column"])])
            passed, delta, reason = compare_value(expected_value, actual_value, rule)
            compared += 1
            if delta is not None:
                deltas.append(delta)
            if not passed:
                failures += 1
                if len(mismatches) < mismatch_limit:
                    mismatches.append(
                        {
                            "key_hash": key_hash(row_key),
                            "comparison": str(rule["name"]),
                            "reason": reason,
                            "expected": None,
                            "actual": None,
                            "delta": delta,
                        }
                    )
        comparison_results.append(
            {
                "name": str(rule["name"]),
                "mode": str(rule["mode"]),
                "tolerance": rule.get("tolerance"),
                "compared": compared,
                "failures": failures,
                "max_delta": max(deltas) if deltas else None,
            }
        )

    expected_count = int(contract["scope"]["record_count"])
    record_count_mismatch = len(expected_rows) != expected_count or len(actual_rows) != expected_count
    failed = bool(
        missing_keys
        or extra_keys
        or duplicate_expected
        or duplicate_actual
        or record_count_mismatch
        or any(item["failures"] for item in comparison_results)
    )
    if record_count_mismatch and len(mismatches) < mismatch_limit:
        mismatches.append(
            {
                "key_hash": hashlib.sha256(b"record_count").hexdigest(),
                "comparison": "record_count",
                "reason": f"approved={expected_count}, oracle={len(expected_rows)}, actual={len(actual_rows)}",
                "expected": None,
                "actual": None,
                "delta": abs(expected_count - len(actual_rows)),
            }
        )

    result = {
        "module_id": str(contract["module_id"]),
        "run_id": run_id,
        "attempt_id": attempt_id,
        "gate": "local_parity_tieout",
        "status": "FAIL" if failed else "PASS",
        "population_scope": result_population_scope(contract),
        "contract": {
            "path": contract_path.relative_to(ROOT).as_posix(),
            "sha256": contract_hash,
            "version": str(contract["contract_version"]),
        },
        "producer": producer_record,
        "fixture_coverage": fixture_coverage,
        "row_counts": {"expected": len(expected_rows), "actual": len(actual_rows), "matched": len(matched_keys)},
        "key_result": {
            "missing_count": len(missing_keys),
            "extra_count": len(extra_keys),
            "duplicate_expected_count": len(duplicate_expected),
            "duplicate_actual_count": len(duplicate_actual),
        },
        "comparisons": comparison_results,
        "mismatches": mismatches,
        "limitations": list(contract["scope"]["does_not_prove"]),
    }
    validate_document(result, RESULT_SCHEMA, "Tie-out result")
    write_json(result_path, result)
    summary_path.write_text(render_summary(result, contract), encoding="utf-8")
    evidence = build_evidence(result, contract, result_path, summary_path, contract_path, contract_hash, intake_path, intake_hash, oracle_path, oracle_hash, fixture_path, fixture_hash, actual_path)
    validate_document(evidence, EVIDENCE_SCHEMA, "Evidence bundle")
    write_json(evidence_path, evidence)

    print(f"Tie-out status: {result['status']}")
    print(f"Rows: expected={len(expected_rows)}, actual={len(actual_rows)}, matched={len(matched_keys)}")
    print(f"Evidence: {evidence_path.relative_to(ROOT)}")
    return 0 if result["status"] == "PASS" else 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute an approved generic SAS-to-Python tie-out contract")
    parser.add_argument("--contract", default="config/tieout.yaml", help="Repository-relative contract path")
    parser.add_argument("--run-id", required=True, help="Existing durable run identifier")
    parser.add_argument("--attempt-id", required=True, help="Append-only validation attempt identifier, for example attempt-001")
    args = parser.parse_args()

    try:
        contract_path = resolve_repo_path(args.contract, "contract")
        require_file(contract_path, "tie-out contract")
        return execute(contract_path, args.run_id, args.attempt_id)
    except TieoutError as exc:
        print(f"Tie-out status: BLOCKED\nReason: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
