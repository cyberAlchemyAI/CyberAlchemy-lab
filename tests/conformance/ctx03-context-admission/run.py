#!/usr/bin/env python3
"""Run CTX03 post-admission checks."""

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
    tests = []
    for item in suite["tests"]:
        process = subprocess.run(item["command"], cwd=LAB, text=True, capture_output=True, check=False)
        stdout = process.stdout.splitlines()
        passed = process.returncode == 0 and all(line in stdout for line in item["expected_stdout"])
        tests.append({"test_id": item["test_id"], "result": "PASS" if passed else "FAIL", "exit_code": process.returncode, "expected_stdout": item["expected_stdout"], "stdout": stdout, "stderr": process.stderr.splitlines()})
    protected = []
    for path, expected in suite["protected_hashes"].items():
        actual = sha(LAB / path)
        protected.append({"path": path, "expected": expected, "actual": actual, "result": "PASS" if actual == expected else "FAIL"})
    projection = OUTPUT.is_file() and OUTPUT.read_text(encoding="utf-8") == render(suite)
    result = "PASS" if projection and all(item["result"] == "PASS" for item in tests + protected) else "FAIL"
    receipt = {
        "schema_version": "cyberalchemy-lab-conformance-run/v1",
        "suite_id": suite["suite_id"],
        "subject": suite["subject"],
        "run_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "result": result,
        "authority_effect": "none",
        "projection_parity": projection,
        "tests": tests,
        "protected_hashes": protected,
        "summary": {"passed": sum(item["result"] == "PASS" for item in tests), "total": len(tests), "protected_passed": sum(item["result"] == "PASS" for item in protected), "protected_total": len(protected)},
        "current_gate_state": "governance-and-ontology-lifecycle-context-language-pairs-admitted",
        "next_gate": "context-map-candidate-authorship-requires-route-reentry",
        "claim_ceiling": suite["claim_ceiling"],
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CTX03_CONTEXT_ADMISSION_CONFORMANCE={result}")
    print(f"TESTS={receipt['summary']['passed']}/{receipt['summary']['total']}")
    print(f"PROTECTED_HASHES={receipt['summary']['protected_passed']}/{receipt['summary']['protected_total']}")
    print(f"CURRENT_GATE_STATE={receipt['current_gate_state']}")
    print(f"NEXT_GATE={receipt['next_gate']}")
    for item in tests + protected:
        if item["result"] == "FAIL":
            print(f"FAIL {item.get('test_id', item.get('path'))}: {item}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
