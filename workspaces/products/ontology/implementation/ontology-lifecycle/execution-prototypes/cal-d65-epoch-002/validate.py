#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
RUNNER = HERE / "runner.py"
RECEIPT = HERE / "receipts/prototype.json"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=LAB,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> int:
    first = run("--mode", "prototype", "--write-receipt")
    if first.returncode != 0:
        print(first.stdout, end="")
        return first.returncode
    first_bytes = RECEIPT.read_bytes()
    second = run("--mode", "prototype", "--write-receipt")
    if second.returncode != 0:
        print(second.stdout, end="")
        return second.returncode
    second_bytes = RECEIPT.read_bytes()
    live = run("--mode", "live")
    try:
        live_output = json.loads(live.stdout)
    except json.JSONDecodeError:
        live_output = {}
    receipt = json.loads(second_bytes)
    passed = (
        first_bytes == second_bytes
        and receipt.get("result") == "PASS"
        and len(receipt.get("execution_trace", [])) == 10
        and receipt.get("source_event_count") == 7
        and receipt.get("target_event_count") == 11
        and receipt.get("rollback_result") == "PASS"
        and receipt.get("mutation_probes_passed") == receipt.get("mutation_probes_total") == 10
        and receipt.get("prototype_execution_ready") is True
        and receipt.get("live_execution_ready") is False
        and receipt.get("temporary_target_removed") is True
        and receipt.get("runtime_activated") is False
        and receipt.get("cutover_performed") is False
        and receipt.get("external_effects") is False
        and live.returncode == 2
        and live_output.get("result") == "BLOCK"
        and len(live_output.get("missing_prerequisites", [])) == 6
        and live_output.get("external_effects") is False
    )
    output = {
        "envelope_id": receipt.get("envelope_id"),
        "result": "PASS" if passed else "BLOCK",
        "deterministic_prototype_runs": 2,
        "receipt_sha256": hashlib.sha256(second_bytes).hexdigest(),
        "state_machine_steps": len(receipt.get("execution_trace", [])),
        "event_migration": f"{receipt.get('source_event_count')}->{receipt.get('target_event_count')}",
        "mutation_probes": f"{receipt.get('mutation_probes_passed')}/{receipt.get('mutation_probes_total')}",
        "rollback_result": receipt.get("rollback_result"),
        "prototype_execution_ready": receipt.get("prototype_execution_ready"),
        "live_execution_refusal": "PASS" if live.returncode == 2 and live_output.get("result") == "BLOCK" else "BLOCK",
        "live_execution_ready": False,
        "runtime_activated": False,
        "cutover_performed": False,
        "external_effects": False,
        "authority_effect": "none"
    }
    print(json.dumps(output, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
