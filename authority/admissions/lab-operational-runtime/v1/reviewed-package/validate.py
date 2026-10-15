#!/usr/bin/env python3
"""Run bounded integration checks and bind their actual outcomes to exact bytes."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest

from lab_runtime.common import atomic, byte_digest, digest, encoded, load, require
from lab_runtime.protocols import SCHEMAS

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[2]


class EvidenceResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checks = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.checks.append({"test": test.id(), "result": "PASS"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.checks.append({"test": test.id(), "result": "FAIL", "detail": self._exc_info_to_string(err, test)})

    def addError(self, test, err):
        super().addError(test, err)
        self.checks.append({"test": test.id(), "result": "ERROR", "detail": self._exc_info_to_string(err, test)})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    for name, schema in SCHEMAS.items():
        require(load(PACKAGE / "schemas" / (name + ".schema.json")) == schema, "schema export drift: " + name)
    files = sorted(p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts and "receipts" not in p.parts)
    before = [{"path": p.relative_to(REPO).as_posix(), "sha256": byte_digest(p.read_bytes())} for p in files]
    started = time.monotonic()
    suite = unittest.defaultTestLoader.discover(str(PACKAGE / "tests"))
    result = unittest.TextTestRunner(verbosity=2, resultclass=EvidenceResult).run(suite)
    demonstration = subprocess.run([sys.executable, str(PACKAGE / "demo.py")], capture_output=True, text=True) if result.wasSuccessful() else None
    demo = json.loads(demonstration.stdout) if demonstration and demonstration.returncode == 0 else {"result": "NOT-PASS", "detail": demonstration.stderr if demonstration else "tests failed"}
    unchanged = all(byte_digest((REPO / x["path"]).read_bytes()) == x["sha256"] for x in before)
    passed = result.wasSuccessful() and result.testsRun > 0 and demo["result"] == "PASS" and unchanged
    report = {"schema_version": "lab-runtime-validation-receipt/v1", "result": "PASS" if passed else "FAIL",
              "tests_run": result.testsRun, "checks": result.checks, "elapsed_seconds": round(time.monotonic() - started, 3),
              "source_manifest": before, "source_manifest_digest": digest(before), "sources_unchanged_during_validation": unchanged,
              "dependencies": {n: importlib.metadata.version(n) for n in ("jsonschema", "cryptography")},
              "demonstration": demo, "authority_effect": "none", "repository_admission_effect": "none",
              "claim_ceiling": "Exact candidate local runtime implementation checks and isolated process-interruption evidence; no implementation admission, production durability, external authority or live deployment."}
    if args.write_receipt:
        atomic(PACKAGE / "receipts/validation.json", encoded(report))
    print(encoded({k: v for k, v in report.items() if k not in ("source_manifest", "checks", "demonstration")}).decode(), end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
