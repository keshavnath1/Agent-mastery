from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "intake"
OUTPUT = ROOT / "artifacts" / "evidence" / "intake_manifest.json"
ALLOWED_AREAS = ("sas", "logs", "lst", "data", "patterns")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> dict[str, object]:
    files = []
    for area in ALLOWED_AREAS:
        base = INTAKE / area
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.name == ".gitkeep":
                continue
            if path.is_symlink():
                raise RuntimeError(f"Symlink is not allowed in intake: {path}")
            files.append({
                "area": area,
                "path": path.relative_to(ROOT).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            })
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_policy": "inventory_only_no_source_execution",
        "file_count": len(files),
        "files": files,
    }


def main() -> int:
    manifest = build_manifest()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {manifest['file_count']} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
