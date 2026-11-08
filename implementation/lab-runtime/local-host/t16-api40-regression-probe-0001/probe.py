"""Reproduce one API40 inherited-case setup failure without counting a test pass."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
INTERFACE = ROOT / "product/lab/release-candidates/v1/interface"
API = INTERFACE / "api-integration-v40-current-t06-0001"
ADAPTER = INTERFACE / "current-source-adapter-v2-action-0148"
TEST = "api-integration-v40-current-t06-0001.test_guarded_reads.GuardedReads.test_snapshot_header_mutation_rejected"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> dict:
    api_manifest = API / "source-manifest.json"
    adapter_manifest = ADAPTER / "source-manifest.json"
    test_file = API / "test_guarded_reads.py"
    selected = {
        "api_manifest_sha256": sha(api_manifest),
        "adapter_manifest_sha256": sha(adapter_manifest),
        "test_file_sha256": sha(test_file),
    }
    api = json.loads(api_manifest.read_bytes())
    adapter = json.loads(adapter_manifest.read_bytes())
    environment = {
        "python": platform.python_version(),
        "jsonschema": importlib.metadata.version("jsonschema"),
        "cryptography": importlib.metadata.version("cryptography"),
    }
    if environment != api["environment"]:
        raise ValueError("host differs from selected API40 environment")
    if adapter["environment"] == environment:
        raise ValueError("adapter environment mismatch no longer reproduced")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(INTERFACE)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    process = subprocess.run([sys.executable, "-B", "-m", "unittest", TEST, "-v"],
                             cwd=ROOT, env=env, capture_output=True, timeout=60)
    output = (process.stdout + process.stderr).decode("utf-8", errors="replace")
    if (process.returncode == 0 or "Ran 0 tests" not in output or
            "independent source environment differs" not in output or
            "setUpClass" not in output):
        raise ValueError("selected API40 regression outcome changed")
    if {"api_manifest_sha256": sha(api_manifest),
        "adapter_manifest_sha256": sha(adapter_manifest),
        "test_file_sha256": sha(test_file)} != selected:
        raise ValueError("selected bytes changed during probe")
    return {
        "schema_version": "lab-t16-api40-regression-probe/v1",
        "selected": selected,
        "test_id": TEST,
        "host_environment": environment,
        "adapter_environment": adapter["environment"],
        "process_exit_code": process.returncode,
        "tests_executed": 0,
        "setup_error": "independent source environment differs",
        "outcome": "SETUP-ERROR-BEFORE-CASE",
        "case_passed": False,
        "full_t16_regression_complete": False,
        "authority_effect": "none",
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
