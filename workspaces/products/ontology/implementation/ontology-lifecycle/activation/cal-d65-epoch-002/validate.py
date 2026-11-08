#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
RUNNER = HERE / "run.py"
RECEIPT = HERE / "receipts/shadow-activation.json"


def main() -> int:
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--write-receipt"],
        cwd=LAB,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.returncode != 0:
        print(completed.stdout, end="")
        return completed.returncode
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    passed = (
        receipt.get("result") == "PASS"
        and receipt.get("deterministic_runs") == 2
        and receipt.get("source_event_count") == 7
        and receipt.get("target_event_count") == 11
        and receipt.get("rust_public_contract_tests_per_run") == 4
        and receipt.get("mutation_probes_passed") == receipt.get("mutation_probes_total") == 10
        and receipt.get("rollback_result") == "PASS"
        and receipt.get("protected_byte_drift") == []
        and receipt.get("final_gate_eligible") is True
        and receipt.get("runtime_activated") is False
        and receipt.get("cutover_authorized") is False
        and receipt.get("cutover_performed") is False
        and receipt.get("authority_effect") == "none"
    )
    print(json.dumps({
        "activation_rehearsal_id": receipt.get("activation_rehearsal_id"),
        "result": "PASS" if passed else "BLOCK",
        "deterministic_runs": receipt.get("deterministic_runs"),
        "event_migration": f"{receipt.get('source_event_count')}->{receipt.get('target_event_count')}",
        "mutation_probes": f"{receipt.get('mutation_probes_passed')}/{receipt.get('mutation_probes_total')}",
        "rollback_result": receipt.get("rollback_result"),
        "final_gate_eligible": receipt.get("final_gate_eligible"),
        "runtime_activated": False,
        "cutover_authorized": False,
        "cutover_performed": False,
        "authority_effect": "none"
    }, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
