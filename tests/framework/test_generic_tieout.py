from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

TEMPLATE_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = TEMPLATE_ROOT / "scripts" / "run_tieout.py"
SPEC = importlib.util.spec_from_file_location("generic_tieout_runner", RUNNER_PATH)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GenericTieoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "contracts").mkdir()
        for name in [
            "tieout_contract.schema.json",
            "tieout_result.schema.json",
            "fixture_manifest.schema.json",
            "evidence_bundle.schema.json",
        ]:
            (self.root / "contracts" / name).write_bytes((TEMPLATE_ROOT / "contracts" / name).read_bytes())
        self.fixture_dir = self.root / "tests" / "fixtures" / "DEMO"
        self.fixture_dir.mkdir(parents=True)
        self.intake_manifest_path = self.root / "artifacts" / "evidence" / "intake_manifest.json"
        self.intake_manifest_path.parent.mkdir(parents=True)
        self.intake_manifest_path.write_text(json.dumps({"file_count": 2, "files": []}, indent=2) + "\n", encoding="utf-8")
        self.input_path = self.fixture_dir / "input.csv"
        self.oracle_path = self.fixture_dir / "oracle.csv"
        self.input_path.write_text("id,input_score\nA,1.0\nB,2.0\n", encoding="utf-8")
        self.oracle_path.write_text("id,sas_score\nA,1.0\nB,2.0\n", encoding="utf-8")
        self.selector_path = self.root / "selector.py"
        self.selector_path.write_text("# deterministic synthetic fixture selector\n", encoding="utf-8")
        self.producer_path = self.root / "producer.py"
        self.producer_path.write_text(
            """from __future__ import annotations
import argparse
import csv
from pathlib import Path
import time

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--delta', type=float, default=0.0)
parser.add_argument('--duplicate', action='store_true')
parser.add_argument('--drop-last', action='store_true')
parser.add_argument('--fail', action='store_true')
parser.add_argument('--sleep', type=float, default=0.0)
args = parser.parse_args()
if args.fail:
    raise SystemExit(7)
if args.sleep:
    time.sleep(args.sleep)
with Path(args.input).open(newline='', encoding='utf-8') as handle:
    rows = list(csv.DictReader(handle))
if args.drop_last:
    rows = rows[:-1]
if args.duplicate and rows:
    rows.append(dict(rows[0]))
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=['id', 'python_score'])
    writer.writeheader()
    for row in rows:
        writer.writerow({'id': row['id'], 'python_score': float(row['input_score']) + args.delta})
""",
            encoding="utf-8",
        )
        self.manifest_path = self.fixture_dir / "fixture_manifest.json"
        manifest = {
            "module_id": "DEMO",
            "fixture_kind": "SYNTHETIC_FRAMEWORK_TEST",
            "selection_version": "test-1",
            "selection_policy": "Two deterministic rows created only to test the reusable comparator.",
            "selector": {"path": "selector.py", "sha256": sha256(self.selector_path), "command": ["{python}", "selector.py"]},
            "record_count": 2,
            "key_columns": ["id"],
            "sources": [
                {"path": "tests/fixtures/DEMO/input.csv", "sha256": sha256(self.input_path), "role": "input"},
                {"path": "tests/fixtures/DEMO/oracle.csv", "sha256": sha256(self.oracle_path), "role": "sas_reference"},
            ],
            "source_observations": [{"name": "eligible_rows", "value": 2, "evidence": "tests/fixtures/DEMO/input.csv"}],
            "transformations": [],
            "coverage_assertions": [
                {"name": "record_count", "mandatory": True, "status": "PASS", "required": 2, "observed": 2},
                {"name": "unique_keys", "mandatory": True, "status": "PASS", "required": 2, "observed": 2},
            ],
            "selection_reason_counts": {"deterministic_synthetic_rows": 2},
            "selected_key_hashes_sha256": runner.selected_keys_digest([("A",), ("B",)]),
            "fixture_inputs": [
                {"path": "tests/fixtures/DEMO/input.csv", "sha256": sha256(self.input_path)}
            ],
            "oracle": {
                "path": "tests/fixtures/DEMO/oracle.csv",
                "sha256": sha256(self.oracle_path),
                "columns": ["id", "sas_score"],
                "created_from_sas_reference_only": True,
            },
            "privacy": {"contains_raw_sensitive_rows": False, "distribution_allowed": False},
            "limitations": ["Synthetic framework validation only."],
        }
        self.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.contract_path = self.root / "config" / "tieout.yaml"
        self.contract_path.parent.mkdir()
        self.contract = {
            "status": "APPROVED",
            "module_id": "DEMO",
            "contract_version": "test-1",
            "scope": {
                "fixture_kind": "SYNTHETIC_FRAMEWORK_TEST",
                "record_count": 2,
                "proves": ["Generic keyed comparator framework behavior."],
                "does_not_prove": ["Any real SAS migration behavior."],
            },
            "key_columns": ["id"],
            "intake_manifest": {"path": "artifacts/evidence/intake_manifest.json", "sha256": sha256(self.intake_manifest_path)},
            "oracle": {
                "path": "tests/fixtures/DEMO/oracle.csv",
                "sha256": sha256(self.oracle_path),
                "format": "csv",
                "representation_note": "Synthetic decimal values are exact for framework testing.",
            },
            "fixture_manifest": {
                "path": "tests/fixtures/DEMO/fixture_manifest.json",
                "sha256": sha256(self.manifest_path),
            },
            "producer": {
                "command": [
                    "{python}",
                    "producer.py",
                    "--input",
                    "tests/fixtures/DEMO/input.csv",
                    "--out",
                    "{actual_output_path}",
                    "--delta",
                    "0.0",
                ],
                "cwd": ".",
                "actual_output_path": "artifacts/generated/{run_id}/{attempt_id}/actual.csv",
                "timeout_seconds": 30,
            },
            "comparisons": [
                {
                    "name": "score",
                    "expected_column": "sas_score",
                    "actual_column": "python_score",
                    "mode": "absolute",
                    "tolerance": 1e-12,
                    "scale_floor": 1e-15,
                    "null_equal": False,
                }
            ],
            "decision_basis": {
                "source": "synthetic framework test",
                "rationale": "Exercise deterministic keyed comparison without asserting real migration behavior.",
            },
            "output": {
                "result_path": "artifacts/evidence/runs/{run_id}/attempts/{attempt_id}/tieout_result.json",
                "summary_path": "artifacts/evidence/runs/{run_id}/attempts/{attempt_id}/tieout_summary.md",
                "evidence_path": "artifacts/evidence/runs/{run_id}/attempts/{attempt_id}/evidence.json",
            },
            "privacy": {"hash_keys_in_evidence": True, "include_values_in_evidence": False, "max_mismatches": 10},
            "oracle_lock": {
                "status": "APPROVED",
                "human_approval_required": True,
                "approved_by": "framework-test",
                "approved_on": "2026-09-14",
                "approval_scope": "Synthetic framework validation only.",
                "implementation_may_modify": False,
            },
            "notes": ["Synthetic test contract."],
        }
        self._write_contract()
        self.patchers = [
            patch.object(runner, "ROOT", self.root),
            patch.object(runner, "CONTRACT_SCHEMA", self.root / "contracts" / "tieout_contract.schema.json"),
            patch.object(runner, "RESULT_SCHEMA", self.root / "contracts" / "tieout_result.schema.json"),
            patch.object(runner, "FIXTURE_SCHEMA", self.root / "contracts" / "fixture_manifest.schema.json"),
            patch.object(runner, "EVIDENCE_SCHEMA", self.root / "contracts" / "evidence_bundle.schema.json"),
        ]
        for patcher in self.patchers:
            patcher.start()

    def tearDown(self) -> None:
        for patcher in reversed(self.patchers):
            patcher.stop()
        self.temporary.cleanup()

    def _write_contract(self) -> None:
        self.contract_path.write_text(yaml.safe_dump(self.contract, sort_keys=False), encoding="utf-8")

    def _result(self, run_id: str, attempt_id: str = "attempt-001") -> dict[str, object]:
        path = self.root / "artifacts" / "evidence" / "runs" / run_id / "attempts" / attempt_id / "tieout_result.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_pass_writes_schema_valid_evidence(self) -> None:
        code = runner.execute(self.contract_path, "RUN-PASS", "attempt-001")
        self.assertEqual(code, 0)
        result = self._result("RUN-PASS")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["row_counts"], {"actual": 2, "expected": 2, "matched": 2})
        evidence = self.root / "artifacts" / "evidence" / "runs" / "RUN-PASS" / "attempts" / "attempt-001" / "evidence.json"
        summary = self.root / "artifacts" / "evidence" / "runs" / "RUN-PASS" / "attempts" / "attempt-001" / "tieout_summary.md"
        self.assertTrue(evidence.is_file())
        self.assertTrue(summary.is_file())
        self.assertIn("**PASS**", summary.read_text(encoding="utf-8"))
        evidence_document = json.loads(evidence.read_text(encoding="utf-8"))
        self.assertEqual(evidence_document["provenance"]["intake_manifest_sha256"], sha256(self.intake_manifest_path))
        self.assertEqual(evidence_document["summary"]["fixture_coverage"]["failed"], 0)

    def test_numeric_mismatch_fails_and_hashes_keys(self) -> None:
        self.contract["producer"]["command"][-1] = "0.1"
        self._write_contract()
        code = runner.execute(self.contract_path, "RUN-FAIL", "attempt-001")
        self.assertEqual(code, 2)
        result = self._result("RUN-FAIL")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["comparisons"][0]["failures"], 2)
        self.assertEqual(len(result["mismatches"][0]["key_hash"]), 64)
        self.assertIsNone(result["mismatches"][0]["expected"])
        self.assertIsNone(result["mismatches"][0]["actual"])
        self.assertNotIn("A", json.dumps(result["mismatches"]))

    def test_duplicate_and_missing_keys_fail(self) -> None:
        self.contract["producer"]["command"].append("--duplicate")
        self._write_contract()
        self.assertEqual(runner.execute(self.contract_path, "RUN-DUP", "attempt-001"), 2)
        duplicate_result = self._result("RUN-DUP")
        self.assertEqual(duplicate_result["key_result"]["duplicate_actual_count"], 1)

        self.contract["producer"]["command"].pop()
        self.contract["producer"]["command"].append("--drop-last")
        self._write_contract()
        self.assertEqual(runner.execute(self.contract_path, "RUN-MISSING", "attempt-001"), 2)
        missing_result = self._result("RUN-MISSING")
        self.assertEqual(missing_result["key_result"]["missing_count"], 1)

    def test_unapproved_contract_is_blocked(self) -> None:
        self.contract["status"] = "DRAFT"
        self.contract["oracle_lock"]["status"] = "UNAPPROVED"
        self.contract["oracle_lock"]["approved_by"] = None
        self.contract["oracle_lock"]["approved_on"] = None
        self.contract["oracle_lock"]["approval_scope"] = None
        self._write_contract()
        with self.assertRaisesRegex(runner.TieoutError, "human-approved"):
            runner.execute(self.contract_path, "RUN-BLOCKED", "attempt-001")

    def test_stale_oracle_hash_is_blocked(self) -> None:
        self.oracle_path.write_text("id,sas_score\nA,9.0\nB,9.0\n", encoding="utf-8")
        with self.assertRaisesRegex(runner.TieoutError, "hash mismatch"):
            runner.execute(self.contract_path, "RUN-STALE", "attempt-001")

    def test_stale_intake_hash_is_blocked(self) -> None:
        self.contract["intake_manifest"]["sha256"] = "0" * 64
        self._write_contract()
        with self.assertRaisesRegex(runner.TieoutError, "Intake manifest hash mismatch"):
            runner.execute(self.contract_path, "RUN-INTAKE-STALE", "attempt-001")

    def test_failed_coverage_is_blocked(self) -> None:
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["coverage_assertions"][0]["status"] = "FAIL"
        self.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.contract["fixture_manifest"]["sha256"] = sha256(self.manifest_path)
        self._write_contract()
        with self.assertRaisesRegex(runner.TieoutError, "Mandatory fixture coverage assertions failed"):
            runner.execute(self.contract_path, "RUN-COVERAGE-FAIL", "attempt-001")

    def test_stale_selector_and_input_hashes_are_blocked(self) -> None:
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["selector"]["sha256"] = "0" * 64
        self.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.contract["fixture_manifest"]["sha256"] = sha256(self.manifest_path)
        self._write_contract()
        with self.assertRaisesRegex(runner.TieoutError, "Fixture selector hash mismatch"):
            runner.execute(self.contract_path, "RUN-SELECTOR-STALE", "attempt-001")

        manifest["selector"]["sha256"] = sha256(self.selector_path)
        manifest["fixture_inputs"][0]["sha256"] = "0" * 64
        self.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.contract["fixture_manifest"]["sha256"] = sha256(self.manifest_path)
        self._write_contract()
        with self.assertRaisesRegex(runner.TieoutError, "Fixture input 0 hash mismatch"):
            runner.execute(self.contract_path, "RUN-INPUT-STALE", "attempt-001")

    def test_selection_digest_mismatch_is_blocked(self) -> None:
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["selected_key_hashes_sha256"] = "0" * 64
        self.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.contract["fixture_manifest"]["sha256"] = sha256(self.manifest_path)
        self._write_contract()
        with self.assertRaisesRegex(runner.TieoutError, "Oracle key selection digest"):
            runner.execute(self.contract_path, "RUN-DIGEST-FAIL", "attempt-001")

    def test_producer_failure_and_timeout_are_blocked_with_evidence(self) -> None:
        self.contract["producer"]["command"].append("--fail")
        self._write_contract()
        self.assertEqual(runner.execute(self.contract_path, "RUN-PRODUCER-FAIL", "attempt-001"), 3)
        self.assertEqual(self._result("RUN-PRODUCER-FAIL")["status"], "BLOCKED")

        self.contract["producer"]["command"].pop()
        self.contract["producer"]["command"].extend(["--sleep", "2"])
        self.contract["producer"]["timeout_seconds"] = 1
        self._write_contract()
        self.assertEqual(runner.execute(self.contract_path, "RUN-PRODUCER-TIMEOUT", "attempt-001"), 3)
        self.assertEqual(self._result("RUN-PRODUCER-TIMEOUT")["status"], "BLOCKED")

    def test_producer_output_is_deterministic_and_attempts_are_append_only(self) -> None:
        self.assertEqual(runner.execute(self.contract_path, "RUN-DETERMINISM", "attempt-001"), 0)
        first = self.root / "artifacts" / "generated" / "RUN-DETERMINISM" / "attempt-001" / "actual.csv"
        first_result = self.root / "artifacts" / "evidence" / "runs" / "RUN-DETERMINISM" / "attempts" / "attempt-001" / "tieout_result.json"
        self.assertEqual(runner.execute(self.contract_path, "RUN-DETERMINISM", "attempt-002"), 0)
        second = self.root / "artifacts" / "generated" / "RUN-DETERMINISM" / "attempt-002" / "actual.csv"
        second_result = self.root / "artifacts" / "evidence" / "runs" / "RUN-DETERMINISM" / "attempts" / "attempt-002" / "tieout_result.json"
        self.assertEqual(sha256(first), sha256(second))
        self.assertTrue(first_result.is_file())
        self.assertTrue(second_result.is_file())
        self.assertEqual(json.loads(first_result.read_text(encoding="utf-8"))["attempt_id"], "attempt-001")
        self.assertEqual(json.loads(second_result.read_text(encoding="utf-8"))["attempt_id"], "attempt-002")

    def test_invalid_attempt_id_is_blocked(self) -> None:
        with self.assertRaisesRegex(runner.TieoutError, "attempt_id"):
            runner.execute(self.contract_path, "RUN-INVALID-ATTEMPT", "../overwrite")


if __name__ == "__main__":
    unittest.main()
