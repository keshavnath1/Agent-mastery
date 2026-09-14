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
        self.input_path = self.fixture_dir / "input.csv"
        self.oracle_path = self.fixture_dir / "oracle.csv"
        self.input_path.write_text("id,input_score\nA,1.0\nB,2.0\n", encoding="utf-8")
        self.oracle_path.write_text("id,sas_score\nA,1.0\nB,2.0\n", encoding="utf-8")
        self.producer_path = self.root / "producer.py"
        self.producer_path.write_text(
            """from __future__ import annotations
import argparse
import csv
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--delta', type=float, default=0.0)
parser.add_argument('--duplicate', action='store_true')
parser.add_argument('--drop-last', action='store_true')
args = parser.parse_args()
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
            "selection_policy": "Two deterministic rows created only to test the reusable comparator.",
            "record_count": 2,
            "key_columns": ["id"],
            "sources": [
                {"path": "tests/fixtures/DEMO/input.csv", "sha256": sha256(self.input_path), "role": "input"},
                {"path": "tests/fixtures/DEMO/oracle.csv", "sha256": sha256(self.oracle_path), "role": "sas_reference"},
            ],
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
            "oracle": {"path": "tests/fixtures/DEMO/oracle.csv", "sha256": sha256(self.oracle_path)},
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
                "actual_output_path": "artifacts/generated/{run_id}/actual.csv",
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
            "output": {
                "result_path": "artifacts/evidence/runs/{run_id}/tieout_result.json",
                "evidence_path": "artifacts/evidence/runs/{run_id}/evidence.json",
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

    def _result(self, run_id: str) -> dict[str, object]:
        path = self.root / "artifacts" / "evidence" / "runs" / run_id / "tieout_result.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_pass_writes_schema_valid_evidence(self) -> None:
        code = runner.execute(self.contract_path, "RUN-PASS")
        self.assertEqual(code, 0)
        result = self._result("RUN-PASS")
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["row_counts"], {"actual": 2, "expected": 2, "matched": 2})
        evidence = self.root / "artifacts" / "evidence" / "runs" / "RUN-PASS" / "evidence.json"
        self.assertTrue(evidence.is_file())

    def test_numeric_mismatch_fails_and_hashes_keys(self) -> None:
        self.contract["producer"]["command"][-1] = "0.1"
        self._write_contract()
        code = runner.execute(self.contract_path, "RUN-FAIL")
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
        self.assertEqual(runner.execute(self.contract_path, "RUN-DUP"), 2)
        duplicate_result = self._result("RUN-DUP")
        self.assertEqual(duplicate_result["key_result"]["duplicate_actual_count"], 1)

        self.contract["producer"]["command"].pop()
        self.contract["producer"]["command"].append("--drop-last")
        self._write_contract()
        self.assertEqual(runner.execute(self.contract_path, "RUN-MISSING"), 2)
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
            runner.execute(self.contract_path, "RUN-BLOCKED")

    def test_stale_oracle_hash_is_blocked(self) -> None:
        self.oracle_path.write_text("id,sas_score\nA,9.0\nB,9.0\n", encoding="utf-8")
        with self.assertRaisesRegex(runner.TieoutError, "hash mismatch"):
            runner.execute(self.contract_path, "RUN-STALE")


if __name__ == "__main__":
    unittest.main()
