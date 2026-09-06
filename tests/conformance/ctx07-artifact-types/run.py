#!/usr/bin/env python3
"""Run the complete CTX07 normalized artifact-type candidate suite."""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from render import OUTPUT, SOURCE, render

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
RECEIPT = ROOT / "receipts/last-run.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    suite = json.loads(SOURCE.read_text(encoding="utf-8"))
    projection_parity = OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(suite)
    material_results = []
    for name, binding in suite["bound_materials"].items():
        path = LAB / binding["path"]
        material_results.append({"name": name, "path": binding["path"], "expected": binding["sha256"], "actual": sha(path), "current": sha(path) == binding["sha256"]})
    results = []
    for test in suite["tests"]:
        process = subprocess.run(test["command"], cwd=LAB, text=True, capture_output=True, check=False)
        stdout = process.stdout.splitlines()
        results.append(
            {
                "test_id": test["test_id"],
                "result": "PASS" if process.returncode == test["expected_exit_code"] and all(line in stdout for line in test["expected_stdout"]) else "FAIL",
                "actual_exit_code": process.returncode,
                "expected_exit_code": test["expected_exit_code"],
                "expected_stdout": test["expected_stdout"],
                "stdout": stdout,
                "stderr": process.stderr.splitlines(),
            }
        )
    result = "PASS" if projection_parity and all(item["current"] for item in material_results) and all(item["result"] == "PASS" for item in results) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-conformance-run/v1",
        "suite_id": suite["suite_id"],
        "subject": suite["subject"],
        "run_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": result,
        "authority_effect": "none",
        "projection_parity": projection_parity,
        "bound_materials": material_results,
        "tests": results,
        "summary": {"passed": sum(item["result"] == "PASS" for item in results), "total": len(results)},
        "current_gate_state": "candidate-ready-for-exact-artifact-type-owner-review" if result == "PASS" else "blocked",
        "claim_ceiling": suite["claim_ceiling"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX07_CONFORMANCE={result}")
    print(f"TESTS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"CURRENT_GATE_STATE={receipt['current_gate_state']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
