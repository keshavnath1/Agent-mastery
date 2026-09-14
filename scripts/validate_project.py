#!/usr/bin/env python3
"""Validate the reusable repository structure without executing migration work."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = [
    "orchestrate", "restart", "interview", "specify", "decide", "harvest", "import",
    "trace", "map", "model", "generate", "test", "validate", "adapt",
    "ingest", "diagnose", "repair", "review", "release", "learn",
]
REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    ".github/copilot-instructions.md",
    "pyproject.toml",
    "config/project.yaml",
    "config/migration_profile.yaml",
    "config/tieout.yaml",
    "config/runtime_profile.yaml",
    "config/workflow.yaml",
    "contracts/evidence_bundle.schema.json",
    "contracts/fixture_manifest.schema.json",
    "contracts/tieout_contract.schema.json",
    "contracts/tieout_result.schema.json",
    "contracts/run_state.schema.json",
    "contracts/semantic_ir.schema.json",
    "docs/templates/PRD.template.md",
    "docs/templates/CAPABILITY_MAP.template.md",
    "docs/templates/MODULE-SPEC.template.md",
    "docs/runbooks/INTAKE.md",
    "docs/runbooks/LOCAL_PARITY.md",
    "docs/runbooks/STAGE_CONTRACT.md",
    "docs/policies/lp-emulator-golden-rules.md",
    "examples/lc-logit-01/README.md",
    "intake/README.md",
    "intake/REQUESTED_ARTIFACTS.md",
    "scripts/project.py",
    "scripts/run_tieout.py",
    "scripts/intake.py",
    "scripts/smoke_test.py",
    "scripts/validate_agent_architecture.py",
    "stage1_extraction/output/README.md",
    "policy/README.md",
    "tests/framework/test_generic_tieout.py",
]
REQUIRED_SECTION_GROUPS = [
    ("## Trigger",),
    ("## Required inputs",),
    ("## Workflow",),
    ("## Output artifact", "## Output artifacts", "## Canonical output", "## Canonical outputs"),
    ("## Verification",),
    ("## Boundaries", "## Boundaries and red flags"),
    ("## Stop conditions",),
]


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    schema_paths = list((ROOT / "contracts").glob("*.json"))
    schema_paths += list((ROOT / ".github/skills").glob("*/schemas/*.json"))
    for schema in schema_paths:
        try:
            json.loads(schema.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON schema {schema.relative_to(ROOT)}: {exc}")

    for skill in SKILLS:
        path = ROOT / ".github" / "skills" / skill / "SKILL.md"
        if not path.is_file():
            errors.append(f"missing skill: {skill}")
            continue
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()
        valid_frontmatter = (
            len(lines) >= 4
            and lines[0] == "---"
            and re.fullmatch(r"name: [a-z][a-z0-9-]*", lines[1]) is not None
            and lines[2].startswith("description: ")
            and len(lines[2]) > len("description: ")
            and lines[3] == "---"
        )
        if not valid_frontmatter:
            errors.append(f"invalid frontmatter: {skill}")
        for alternatives in REQUIRED_SECTION_GROUPS:
            if not any(section in content for section in alternatives):
                errors.append(f"{skill} missing section group {alternatives}")
        if "TODO" in content or "example.py" in content or "api_reference.md" in content:
            errors.append(f"placeholder initializer content remains in {skill}")

    initializer_placeholders = list((ROOT / ".github/skills").glob("*/scripts/example.py"))
    initializer_placeholders += list((ROOT / ".github/skills").glob("*/references/api_reference.md"))
    if initializer_placeholders:
        errors.append("skill initializer placeholders remain")

    if errors:
        print("PROJECT VALIDATION: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PROJECT VALIDATION: PASS ({len(SKILLS)} skills, clean template)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
