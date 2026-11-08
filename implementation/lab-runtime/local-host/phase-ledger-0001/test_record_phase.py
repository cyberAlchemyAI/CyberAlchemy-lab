import datetime as dt
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from record_phase import record


class PhaseLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.selection = self.home / "selection.json"
        self.receipt = self.home / "receipt.json"

    def select(self, seconds):
        expires = (dt.datetime.now(dt.timezone.utc) +
                   dt.timedelta(seconds=seconds)).isoformat()
        self.selection.write_text(json.dumps({"expires_at": expires}))

    def test_real_duration_failure_and_output_are_sanitized(self):
        self.select(60)
        value = record("reader", self.selection, self.receipt,
                       [sys.executable, "-c", "import time,sys; time.sleep(.02); "
                        "print('SECRET_OUTPUT'); print('SECRET_ERROR', file=sys.stderr); sys.exit(7)"])
        self.assertEqual(value["exit_code"], 7)
        self.assertGreater(value["monotonic_seconds"], 0)
        self.assertTrue(value["ended_before_strictest_deadline"])
        raw = self.receipt.read_bytes()
        self.assertNotIn(b"SECRET_OUTPUT", raw)
        self.assertNotIn(b"SECRET_ERROR", raw)
        self.assertEqual(stat.S_IMODE(self.receipt.stat().st_mode), 0o600)

    def test_expired_source_refuses_before_command(self):
        self.select(-1)
        marker = self.home / "marker"
        with self.assertRaisesRegex(ValueError, "LEASE_EXPIRED_BEFORE_PHASE"):
            record("source", self.selection, self.receipt,
                   [sys.executable, "-c", f"open({str(marker)!r},'w').close()"])
        self.assertFalse(marker.exists())
        self.assertFalse(self.receipt.exists())

    def test_stricter_lease_and_exclusive_receipt(self):
        self.select(60)
        early = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=20)).isoformat()
        leases = ["reader=" + early, "context=" + early, "session=" + early]
        value = record("session", self.selection, self.receipt,
                       [sys.executable, "-c", "pass"], deadlines=leases)
        self.assertEqual(value["strictest_deadline"], value["deadlines"]["session"])
        marker = self.home / "unexpected-repeat"
        with self.assertRaises(FileExistsError):
            record("session", self.selection, self.receipt,
                   [sys.executable, "-c", f"open({str(marker)!r},'w').close()"],
                   deadlines=leases)
        self.assertFalse(marker.exists())

    def test_session_without_real_lease_fields_refuses(self):
        self.select(60)
        with self.assertRaisesRegex(ValueError, "EPHEMERAL_LEASE_MISSING"):
            record("session", self.selection, self.receipt,
                   [sys.executable, "-c", "pass"])
        self.assertFalse(self.receipt.exists())

    def test_timeout_and_spawn_error_leave_terminal_receipts(self):
        self.select(60)
        timed = record("source", self.selection, self.receipt,
                       [sys.executable, "-c", "import time; time.sleep(1)"],
                       timeout_seconds=.01)
        self.assertEqual((timed["exit_code"], timed["failure_kind"]), (124, "timeout"))
        self.assertEqual(json.loads(self.receipt.read_bytes())["exit_code"], 124)
        another = self.home / "another.json"
        missing = record("source", self.selection, another,
                         [str(self.home / "missing-executable")])
        self.assertEqual((missing["exit_code"], missing["failure_kind"]),
                         (127, "spawn_error"))
        self.assertEqual(json.loads(another.read_bytes())["exit_code"], 127)


if __name__ == "__main__":
    unittest.main()
