"""Synthetic-only independent review. No Docker or private preflight."""
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

REPO = Path("/home/vlad_/projects/CyberAlchemy-lab")
BASE = REPO / "implementation/lab-runtime/local-host/reader-only-unified-0006"
FREEZE = "a4d424959bf6846194ca101f6ac2f80b4d6fbf91e35e7db835de157c61c845df"

def verify():
    raw = (BASE / "freeze.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != FREEZE:
        raise RuntimeError("FREEZE_DRIFT")
    rows = json.loads(raw)["file_bindings"]
    for row in rows:
        raw = (REPO / row["path"]).read_bytes()
        if len(raw) != row["size"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise RuntimeError("MEMBER_DRIFT")
    return len(rows)

verify()
sys.path.insert(0, str(BASE))
import test_controller
import test_reader_once
c = test_controller.c
observations = []

class Independent(unittest.TestCase):
    def setUp(self):
        self.fixture = test_controller.ControllerTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def recover(self):
        f = self.fixture
        with mock.patch.multiple(c, EFFECT_ENABLED=True, EVIDENCE=f.evidence), \
             mock.patch.object(c, "inspected", side_effect=f.last_fake.inspected), \
             mock.patch.object(c, "cli", side_effect=AssertionError("NO_DAEMON_COMMAND")):
            return c.recover_consumed()

    def test_original_close_counterexample_inverted(self):
        f = self.fixture
        real_close = os.close
        calls = []
        def close(fd):
            target = os.readlink(f"/proc/self/fd/{fd}")
            real_close(fd)
            if target == str(f.evidence) and not calls:
                calls.append(fd)
                raise OSError("once-only synthetic close uncertainty")
        with mock.patch.object(c.os, "close", side_effect=close):
            with self.assertRaises(BaseExceptionGroup):
                f.execute_fake("success")
        self.assertEqual(len(calls), 1)
        self.assertEqual(json.loads((f.evidence / "reader-once.terminal.json").read_bytes())["overall"], "UNKNOWN")
        self.assertFalse((f.evidence / "reader-once.final.json").exists())
        self.assertFalse((f.evidence / "reader-once.finalized").exists())
        recovered = self.recover()
        self.assertEqual(recovered["finalization"], "MISSING_OR_FAILED")
        self.assertTrue(recovered["absent"])
        observations.append("R01: outer-close fault leaves provisional UNKNOWN; cleanup-only succeeds")

    def test_final_readback_close_uncertainty(self):
        f = self.fixture
        real_close = os.close
        calls = []
        def close(fd):
            target = os.readlink(f"/proc/self/fd/{fd}")
            real_close(fd)
            # _bounded_read_held closes via os.close; final writer uses file.close.
            if target == str(f.evidence / "reader-once.final.json") and not calls:
                calls.append(fd)
                raise OSError("final readback close uncertainty")
        with mock.patch.object(c.os, "close", side_effect=close):
            with self.assertRaises(OSError):
                f.execute_fake("success")
        self.assertEqual(len(calls), 1)
        self.assertTrue((f.evidence / "reader-once.final.json").is_file())
        self.assertFalse((f.evidence / "reader-once.finalized").exists())
        self.assertEqual(self.recover()["finalization"], "MISSING_OR_FAILED")
        observations.append("final readback close fault: uncommitted file cannot block recovery")

    def test_marker_present_but_final_missing(self):
        f = self.fixture
        f.execute_fake("success")
        (f.evidence / "reader-once.final.json").unlink()
        recovered = self.recover()
        self.assertEqual(recovered["operation"], "UNKNOWN")
        self.assertEqual(recovered["finalization"], "INVALID_UNKNOWN")
        observations.append("marker alone cannot establish PASS")

    def test_provisional_digest_mismatch(self):
        f = self.fixture
        f.execute_fake("success")
        p = f.evidence / "reader-once.terminal.json"
        p.write_bytes(p.read_bytes() + b" ")
        self.assertEqual(self.recover()["finalization"], "INVALID_UNKNOWN")
        observations.append("changed provisional bytes invalidate final binding")

    def test_clean_final_blocks_recovery(self):
        f = self.fixture
        _, result = f.execute_fake("success")
        self.assertEqual(result["overall"], "PASS")
        self.assertEqual(json.loads((f.evidence / "reader-once.terminal.json").read_bytes())["overall"], "UNKNOWN")
        marker = f.evidence / "reader-once.finalized"
        self.assertEqual(marker.stat().st_mode & 0o777, 0o700)
        self.assertEqual(list(marker.iterdir()), [])
        with self.assertRaisesRegex(ValueError, "successful consumed attempt"):
            self.recover()
        observations.append("clean final+marker positive; no repeat cleanup/effect")

suite = unittest.TestSuite([
    unittest.defaultTestLoader.loadTestsFromModule(test_controller),
    unittest.defaultTestLoader.loadTestsFromModule(test_reader_once),
    unittest.defaultTestLoader.loadTestsFromTestCase(Independent),
])
result = unittest.TextTestRunner(verbosity=1).run(suite)
post = verify()
print(json.dumps({"checks": result.testsRun, "success": result.wasSuccessful(),
                  "independent_checks": observations, "optimized": sys.flags.optimize,
                  "freeze_members_pre_post": post, "private_body_read": False,
                  "docker_called": False,
                  "future_attempt_absent": not Path("/tmp/cal-reader-only-dev-20261020-0001-unified6").exists()},
                 sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
