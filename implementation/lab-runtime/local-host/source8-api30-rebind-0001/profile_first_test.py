"""Time actual API33 first Session fixture phases without recording private data."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
import time
import unittest

from run_successor import OUTPUT, digest, package_at


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> dict:
    profiler = Path(__file__).resolve()
    profiler_sha = digest(profiler)
    package = package_at(OUTPUT)
    module = importlib.import_module(package + ".test_custody_sessions")
    module.PROFILE = digest(OUTPUT / "contract-profile.json")
    cls = module.Sessions
    phases = []

    def measured(label, action):
        started = stamp()
        monotonic = time.monotonic()
        outcome = "PASS"
        try:
            reply = action()
            if label.startswith("operation:") and isinstance(reply, dict):
                outcome = "PASS" if reply.get("kind") == "result" else "API-ERROR"
            return reply
        except BaseException:
            outcome = "ERROR"
            raise
        finally:
            phases.append({"phase": label, "started_at_utc": started,
                           "completed_at_utc": stamp(),
                           "monotonic_elapsed_seconds": round(time.monotonic() - monotonic, 3),
                           "result": outcome})
            print("PHASE", label, phases[-1]["monotonic_elapsed_seconds"], outcome, flush=True)

    old_class_setup = cls.setUpClass.__func__
    old_setup = cls.setUp
    old_invoke = cls.invoke
    old_teardown = cls.tearDown
    cls.setUpClass = classmethod(lambda selected: measured("setUpClass", lambda: old_class_setup(selected)))
    cls.setUp = lambda self: measured("setUp", lambda: old_setup(self))
    cls.invoke = lambda self, call, **options: measured("operation:" + call.get("operation", "unknown"),
                                                        lambda: old_invoke(self, call, **options))
    cls.tearDown = lambda self: measured("tearDown", lambda: old_teardown(self))
    started = stamp()
    monotonic = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.TestSuite([cls("test_00_all_eleven_actual_operations")]))
    report = {"result": "PASS" if result.wasSuccessful() and result.testsRun == 1 else "FAIL",
              "started_at_utc": started, "completed_at_utc": stamp(),
              "monotonic_elapsed_seconds": round(time.monotonic() - monotonic, 3),
              "tests_run": result.testsRun,
              "errors": [case.id() for case, _ in result.errors],
              "failures": [case.id() for case, _ in result.failures],
              "phases": phases,
              "profiler_sha256": profiler_sha,
              "profiler_unchanged_during_run": digest(profiler) == profiler_sha,
              "successor_manifest_sha256": digest(OUTPUT / "source-manifest.json")}
    out = Path(__file__).resolve().parent / "working"
    out.mkdir(mode=0o700, exist_ok=True)
    (out / "profile-first-test-result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


if __name__ == "__main__":
    raise SystemExit(0 if main()["result"] == "PASS" else 1)
