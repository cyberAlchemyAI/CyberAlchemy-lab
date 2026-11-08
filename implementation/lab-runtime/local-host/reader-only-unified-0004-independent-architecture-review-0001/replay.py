"""Independent synthetic-only review: never call private preflight or Docker."""
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

REPO = Path("/home/vlad_/projects/CyberAlchemy-lab")
BASE = REPO / "implementation/lab-runtime/local-host/reader-only-unified-0004"
FREEZE = "17e8d7703388e9f9314cca74c6d0fb38aa3b3808946a649c7eb96f3264282dc4"


def verified():
    raw = (BASE / "freeze.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != FREEZE:
        raise RuntimeError("FREEZE_DRIFT")
    manifest = json.loads(raw)
    for row in manifest["file_bindings"]:
        member = (REPO / row["path"]).read_bytes()
        if len(member) != row["size"] or hashlib.sha256(member).hexdigest() != row["sha256"]:
            raise RuntimeError("MEMBER_DRIFT")
    return len(manifest["file_bindings"])


count = verified()
sys.path.insert(0, str(BASE))
import test_controller
import test_reader_once
c = test_controller.c
suite = unittest.TestSuite([
    unittest.defaultTestLoader.loadTestsFromModule(test_controller),
    unittest.defaultTestLoader.loadTestsFromModule(test_reader_once),
])
result = unittest.TextTestRunner(verbosity=1).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)

# Reuse only the frozen synthetic fixture. The primary counterexample adds
# assertions on durable evidence and cleanup-only reachability that the
# inherited test (which only checks raised error) does not make.
fixture = test_controller.ControllerTests()
fixture.setUp()
observed = {}
try:
    real_close = os.close
    triggered = []
    def close_once(fd):
        target = os.readlink(f"/proc/self/fd/{fd}")
        real_close(fd)
        if target == str(fixture.evidence) and not triggered:
            triggered.append(True)
            raise OSError("synthetic close uncertainty after real close")
    try:
        with mock.patch.object(c.os, "close", side_effect=close_once):
            fixture.execute_fake("success")
    except BaseExceptionGroup:
        observed["outer_run"] = "RAISED_UNKNOWN"
    else:
        raise RuntimeError("EXPECTED_CLOSE_FAILURE")
    terminal = json.loads((fixture.evidence / "reader-once.terminal.json").read_bytes())
    if terminal["overall"] != "PASS" or not triggered:
        raise RuntimeError("COUNTEREXAMPLE_NOT_REPRODUCED")
    observed["durable_terminal"] = terminal
    with mock.patch.multiple(c, EFFECT_ENABLED=True, EVIDENCE=fixture.evidence), \
         mock.patch.object(c, "settle", side_effect=AssertionError("MUST_NOT_REACH_DOCKER")):
        try:
            c.recover_consumed()
        except ValueError as error:
            if str(error) != "successful consumed attempt needs no recovery":
                raise
            observed["recovery"] = "REFUSED_BECAUSE_DURABLE_PASS"
        else:
            raise RuntimeError("EXPECTED_RECOVERY_REFUSAL")
finally:
    fixture.doCleanups()
observed.update(schema_version="reader-unified-static-review-observation/v1",
                author_tests=result.testsRun, author_tests_pass=True,
                independent_counterexamples=1, frozen_members_pre_post=verified(),
                optimized=sys.flags.optimize,
                selected_attempt_absent=not Path("/tmp/cal-reader-only-dev-20261020-0001-unified4").exists(),
                private_body_read=False, docker_called=False,
                fixture_cleanup="COMPLETE")
print(json.dumps(observed, sort_keys=True))
