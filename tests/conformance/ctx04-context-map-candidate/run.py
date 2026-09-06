#!/usr/bin/env python3
"""Run the CTX04 Context Map candidate conformance suite."""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from render import OUTPUT, SOURCE, render

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[2]
RECEIPT = ROOT / "receipts/last-run.json"


def main() -> int:
    suite = json.loads(SOURCE.read_text(encoding="utf-8"))
    projection_parity = OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(suite)
    results = []
    for test in suite["tests"]:
        process = subprocess.run(test["command"], cwd=LAB, text=True, capture_output=True, check=False)
        stdout = process.stdout.splitlines()
        expected = test["expected_stdout"]
        passed = process.returncode == test["expected_exit_code"] and all(line in stdout for line in expected)
        results.append({"test_id": test["test_id"], "result": "PASS" if passed else "FAIL", "actual_exit_code": process.returncode, "expected_exit_code": test["expected_exit_code"], "expected_stdout": expected, "stdout": stdout, "stderr": process.stderr.splitlines()})
    result = "PASS" if projection_parity and all(item["result"] == "PASS" for item in results) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-conformance-run/v1",
        "suite_id": suite["suite_id"],
        "subject": suite["subject"],
        "run_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": result,
        "authority_effect": "none",
        "projection_parity": projection_parity,
        "tests": results,
        "summary": {"passed": sum(item["result"] == "PASS" for item in results), "total": len(results)},
        "current_gate_state": "candidate-ready-for-exact-context-map-owner-review" if result == "PASS" else "blocked",
        "claim_ceiling": suite["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX04_CONFORMANCE={result}")
    print(f"TESTS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"CURRENT_GATE_STATE={receipt['current_gate_state']}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
