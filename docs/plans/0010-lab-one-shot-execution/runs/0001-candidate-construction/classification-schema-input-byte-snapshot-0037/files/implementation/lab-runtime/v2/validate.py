#!/usr/bin/env python3
"""Run bounded integration checks and bind their actual outcomes to exact bytes."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    parser.add_argument("--workers", type=int, default=1, help="Run independent checks in isolated processes (1-16).")
    args = parser.parse_args()
    require(1 <= args.workers <= 16, "workers must be between 1 and 16")
    for name, schema in SCHEMAS.items():
        require(load(PACKAGE / "schemas" / (name + ".schema.json")) == schema, "schema export drift: " + name)
    files = sorted(p for p in PACKAGE.rglob("*") if p.is_file() and "__pycache__" not in p.parts and "receipts" not in p.parts)
    before = [{"path": p.relative_to(REPO).as_posix(), "sha256": byte_digest(p.read_bytes())} for p in files]
    started = time.monotonic()
    suite = unittest.defaultTestLoader.discover(str(PACKAGE / "tests"))
    if args.workers == 1:
        result = unittest.TextTestRunner(verbosity=2, resultclass=EvidenceResult).run(suite)
        checks, tests_run, successful = result.checks, result.testsRun, result.wasSuccessful()
    else:
        def cases(group):
            for item in group:
                if isinstance(item, unittest.TestSuite):
                    yield from cases(item)
                else:
                    yield item.id()
        def run_case(test_id):
            run = subprocess.run([sys.executable, "-m", "unittest", "-v", test_id],
                                 cwd=PACKAGE / "tests", capture_output=True, text=True)
            passed = run.returncode == 0 and "Ran 1 test" in run.stderr
            return {"test": test_id, "result": "PASS" if passed else "FAIL", "exit_code": run.returncode,
                    "output": run.stdout + run.stderr}
        ids = list(cases(suite))
        require(len(ids) == len(set(ids)), "duplicate discovered test IDs")
        checks = []
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(run_case, test_id) for test_id in ids]
            for future in as_completed(futures):
                check = future.result()
                checks.append(check)
                print(f"{len(checks)}/{len(ids)} {check['test']} ... {check['result']}", file=sys.stderr, flush=True)
        checks.sort(key=lambda check: check["test"])
        tests_run, successful = len(checks), all(check["result"] == "PASS" for check in checks)
    demonstration = subprocess.run([sys.executable, str(PACKAGE / "demo.py")], capture_output=True, text=True) if successful else None
    demo = json.loads(demonstration.stdout) if demonstration and demonstration.returncode == 0 else {"result": "NOT-PASS", "detail": demonstration.stderr if demonstration else "tests failed"}
    unchanged = all(byte_digest((REPO / x["path"]).read_bytes()) == x["sha256"] for x in before)
    passed = successful and tests_run > 0 and demo["result"] == "PASS" and unchanged
    report = {"schema_version": "lab-runtime-validation-receipt/v1", "result": "PASS" if passed else "FAIL",
              "tests_run": tests_run, "checks": checks, "workers": args.workers,
              "check_isolation": "separate-process-and-temporary-store" if args.workers > 1 else "temporary-store-per-check",
              "elapsed_seconds": round(time.monotonic() - started, 3),
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
