#!/usr/bin/env python3
"""Run CTX01 post-admission conformance and protected-surface checks."""

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
    results = []
    for test in suite["tests"]:
        process = subprocess.run(test["command"], cwd=LAB, text=True, capture_output=True, check=False)
        stdout = process.stdout.splitlines()
        results.append({"test_id": test["test_id"], "result": "PASS" if process.returncode == 0 and all(line in stdout for line in test["expected_stdout"]) else "FAIL", "exit_code": process.returncode, "expected_stdout": test["expected_stdout"], "stdout": stdout, "stderr": process.stderr.splitlines()})
    protected = [{"path": path, "expected": expected, "actual": sha(LAB / path), "result": "PASS" if sha(LAB / path) == expected else "FAIL"} for path, expected in suite["protected_hashes"].items()]
    projection = OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(suite)
    result = "PASS" if all(item["result"] == "PASS" for item in results + protected) and projection else "FAIL"
    receipt = {"schema_version": "cyberalchemy-lab-conformance-run/v1", "suite_id": suite["suite_id"], "subject": suite["subject"], "run_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "result": result, "authority_effect": "none", "projection_parity": projection, "tests": results, "protected_hashes": protected, "summary": {"passed": sum(item["result"] == "PASS" for item in results), "total": len(results), "protected_passed": sum(item["result"] == "PASS" for item in protected), "protected_total": len(protected)}, "current_gate_state": "ctx01-artifact-types-admitted-owner-bindings-not-yet-authorized", "claim_ceiling": suite["claim_ceiling"]}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX01_ADMISSION_CONFORMANCE={result}")
    print(f"TESTS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"PROTECTED_HASHES={receipt['summary']['protected_passed']}/{receipt['summary']['protected_total']}")
    print(f"CURRENT_GATE_STATE={receipt['current_gate_state']}")
    for item in results + protected:
        if item["result"] == "FAIL":
            print(f"FAIL {item.get('test_id', item.get('path'))}: {item}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
