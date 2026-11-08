#!/usr/bin/env python3
"""Exercise fail-closed D65-S4 validation in disposable package copies."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile


PACKAGE_ROOT = Path(__file__).resolve().parent


def run_case(name: str, mutate) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix=f"cal-d65-s4-{name}-") as directory:
        candidate = Path(directory) / "candidate"
        shutil.copytree(PACKAGE_ROOT, candidate)
        mutate(candidate)
        completed = subprocess.run(
            ["python3", str(candidate / "validate.py")],
            cwd=candidate,
            text=True,
            capture_output=True,
        )
        receipt = json.loads(completed.stdout)
        if completed.returncode == 0 or receipt.get("result") != "FAIL":
            raise RuntimeError(f"hostile case {name} did not fail closed")
        return {
            "case": name,
            "result": "PASS",
            "observed_failure_codes": sorted(
                {item["code"] for item in receipt.get("failures", [])}
            ),
        }


def drift_selected_digest(candidate: Path) -> None:
    path = candidate / "sources.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["records"][0]["sha256"] = "0" * 64
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def remove_relation_mapping(candidate: Path) -> None:
    path = candidate / "mappings/business-to-domainspec.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["relation_mappings"] = document["relation_mappings"][:-1]
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def inject_successor_artifact(candidate: Path) -> None:
    path = candidate / "domainspec/generated"
    path.mkdir(parents=True)
    (path / "graph.json").write_text("{}\n", encoding="utf-8")


def main() -> int:
    cases = [
        run_case("selected-digest-drift", drift_selected_digest),
        run_case("relation-mapping-gap", remove_relation_mapping),
        run_case("successor-artifact-injection", inject_successor_artifact),
    ]
    print(
        json.dumps(
            {
                "schema_version": "cal-d65-s4-hostile-check-receipt/v1",
                "result": "PASS",
                "cases": cases,
                "claim_ceiling": "Hostile PASS proves only that these three mutations fail closed; it grants no admission or successor authority.",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
