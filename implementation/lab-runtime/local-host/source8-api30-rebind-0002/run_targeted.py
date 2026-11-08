"""Run only the versioned Session expiry case against frozen API33."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OLD_HARNESS = HERE.with_name("source8-api30-rebind-0001")
sys.path.insert(0, str(OLD_HARNESS))
from run_successor import OUTPUT, SuccessResult, digest, package_at  # noqa: E402
from timer_test import successor_class  # noqa: E402

SOURCE_SHA = "e400703a2ace9ea1899d7abf15023632a83235e1e15f5459970b1ed8d12a37dd"
PROFILE_SHA = "c86a04159a99d607f15f42078ae64b108ef5007e121f830d54174f0167b8813a"
ORIGINAL_TEST_SHA = "8ce3da4b1b4141e01c97f2168ff7483f836248c8d6693f079daee3f6ceb78e42"
RESULT = HERE / "working" / "targeted-timer-result-0001.json"


def bindings():
    original_test = OUTPUT / "test_custody_sessions.py"
    timer_source = HERE / "timer_test.py"
    if (digest(OUTPUT / "source-manifest.json") != SOURCE_SHA or
            digest(OUTPUT / "contract-profile.json") != PROFILE_SHA or
            digest(original_test) != ORIGINAL_TEST_SHA):
        raise ValueError("frozen API33 timer test selection differs")
    return {"api_source_manifest_sha256": SOURCE_SHA,
            "api_profile_sha256": PROFILE_SHA,
            "original_test_sha256": ORIGINAL_TEST_SHA,
            "timer_successor_sha256": digest(timer_source)}


def run():
    selected = bindings()
    package = package_at(OUTPUT)
    module = __import__(package + ".test_custody_sessions", fromlist=["Sessions"])
    module.PROFILE = PROFILE_SHA
    cls = successor_class(module.Sessions, module)
    case = cls("test_27_actual_expiry_timer_disposes")
    start = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    outcome = unittest.TextTestRunner(verbosity=2, resultclass=SuccessResult).run(
        unittest.TestSuite([case]))
    unchanged = bindings() == selected
    receipt = {"schema": "cal-api33-versioned-session-timer-targeted/v1",
               "authority_effect": "none", "selected_bindings": selected,
               "selected_bytes_unchanged_during_run": unchanged,
               "started_at_utc": started,
               "completed_at_utc": datetime.now(timezone.utc).isoformat(),
               "monotonic_elapsed_seconds": round(time.monotonic() - start, 3),
               "tests_run": outcome.testsRun,
               "case_rows": list(outcome.case_rows.values()),
               "failures": [(test.id(), message[-2000:]) for test, message in outcome.failures],
               "errors": [(test.id(), message[-2000:]) for test, message in outcome.errors],
               "result": "PASS" if outcome.wasSuccessful() and unchanged else "FAIL"}
    RESULT.parent.mkdir(mode=0o700, exist_ok=True)
    if RESULT.exists():
        raise ValueError("targeted timer result already exists")
    RESULT.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"result": receipt["result"], "tests_run": receipt["tests_run"],
                      "elapsed_seconds": receipt["monotonic_elapsed_seconds"]}))
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
