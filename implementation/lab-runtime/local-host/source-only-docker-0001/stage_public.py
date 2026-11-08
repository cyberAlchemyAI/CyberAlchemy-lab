"""Materialize only the pinned public cut in a fresh disposable scratch root.

This is a reversible input-copy operation. It never imports Source or opens a
historical branch.snapshot body. Source build/cold replay remain unrun.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from prepare_public import (HERE, REPO, NEW_FAMILY, EXCLUDED, public_bytes,
                            require, sha)


def stage(attempt: Path) -> dict:
    require(attempt.is_absolute() and attempt.parent == Path("/tmp") and
            attempt.name.startswith("cal-source-only-dev-20261020-0001-") and
            not attempt.exists(), "fresh exact /tmp attempt required")
    plan = json.loads((HERE / "public-cut.json").read_bytes())
    require(plan["effect"] == "NOT_RUN" and plan["excluded_historical_archive_paths"] == sorted(EXCLUDED)
            and plan["public_historical_rows"] == 891 and len(plan["generated_bindings"]) == 8,
            "closed public cut required")
    root = attempt / "root"
    attempt.mkdir(mode=0o700)
    root.mkdir(mode=0o755)
    copied = []
    for row in plan["public_inputs"]:
        name = row["path"]
        raw = public_bytes(name, row["sha256"])
        dest = root / name
        require(dest.is_relative_to(root) and not dest.exists(), "duplicate public stage target")
        dest.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
        with dest.open("xb") as stream:
            stream.write(raw)
        dest.chmod(0o444)
        copied.append(name)
    for row in plan["generated_bindings"]:
        name = row["path"]
        require(name not in EXCLUDED and not name.endswith("/branch.snapshot") and
                (name.startswith(NEW_FAMILY + "/") or name == plan["new_authorization"]["path"]),
                "generated target escaped public cut")
        source = HERE / "generated" / name
        require(source.is_file() and not source.is_symlink() and sha(source.read_bytes()) == row["sha256"],
                "generated input differs")
        dest = root / name
        require(not dest.exists(), "generated target collided")
        dest.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
        dest.write_bytes(source.read_bytes())
        dest.chmod(0o444)
        copied.append(name)
    output_parent = root / NEW_FAMILY
    for name in ("packages", "receipts"):
        target = output_parent / name
        require(not target.exists(), "Source output parent already exists")
        target.mkdir(mode=0o700)
    evidence = attempt / "evidence"
    evidence.mkdir(mode=0o700)
    require({p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()} == set(copied),
            "staged file inventory differs")
    result = {"schema_version": "lab-source-only-docker-stage/v1-inactive",
              "effect": "NOT_RUN", "attempt": str(attempt), "root": str(root),
              "source_manifest_sha256": plan["source_manifest"]["sha256"],
              "files": len(copied), "protected_archives_present": False,
              "package_0001_present": False}
    (evidence / "stage-result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", type=Path, required=True)
    ns = parser.parse_args()
    print(json.dumps(stage(ns.attempt), sort_keys=True))
