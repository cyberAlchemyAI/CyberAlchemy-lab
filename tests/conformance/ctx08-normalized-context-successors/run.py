#!/usr/bin/env python3
"""Run the digest-bound CTX08 normalized context successor conformance suite."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
SOURCE = ROOT / "suite.json"
PROJECTION = ROOT / "TESTING.md"
RECEIPT = ROOT / "receipts/last-run.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_renderer():
    path = ROOT / "render.py"
    spec = importlib.util.spec_from_file_location("ctx08_conformance_renderer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render


def main() -> int:
    suite = load(SOURCE)
    bound_materials = []
    for item in suite["bound_materials"]:
        path = LAB / item["path"]
        actual = sha(path)
        bound_materials.append({**item, "actual": actual, "current": actual == item["sha256"]})

    projection_parity = PROJECTION.is_file() and PROJECTION.read_text(encoding="utf-8") == load_renderer()(suite)
    tests = []
    materials_current = all(item["current"] for item in bound_materials)
    if materials_current and projection_parity:
        for item in suite["tests"]:
            completed = subprocess.run(item["command"], cwd=LAB, text=True, capture_output=True, check=False)
            stdout = completed.stdout.rstrip().splitlines()
            stderr = completed.stderr.rstrip().splitlines()
            passed = completed.returncode == item["expected_exit_code"] and stdout == item["expected_stdout"]
            tests.append(
                {
                    "test_id": item["test_id"],
                    "expected_exit_code": item["expected_exit_code"],
                    "actual_exit_code": completed.returncode,
                    "expected_stdout": item["expected_stdout"],
                    "stdout": stdout,
                    "stderr": stderr,
                    "result": "PASS" if passed else "FAIL",
                }
            )

    passed_count = sum(item["result"] == "PASS" for item in tests)
    result = "PASS" if materials_current and projection_parity and passed_count == len(suite["tests"]) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-conformance-run/v1",
        "suite_id": suite["suite_id"],
        "subject": suite["subject"],
        "run_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": result,
        "authority_effect": "none",
        "bound_materials": bound_materials,
        "projection_parity": projection_parity,
        "tests": tests,
        "summary": {"passed": passed_count, "total": len(suite["tests"])},
        "current_gate_state": "candidate-ready-for-exact-context-and-lineage-owner-review" if result == "PASS" else "not_evaluable",
        "claim_ceiling": suite["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX08_CONFORMANCE={result}")
    print(f"TESTS={passed_count}/{len(suite['tests'])}")
    print(f"CURRENT_GATE_STATE={receipt['current_gate_state']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
