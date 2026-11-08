import hashlib
import datetime as dt
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe


class UnionGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture = probe.selected_capture()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cal-union-guard-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / "payload.txt"
        self.path.write_bytes(b"selected\n")
        self.row = {"path": "payload.txt", "sha256": hashlib.sha256(self.path.read_bytes()).hexdigest()}

    def test_selected_current_family_union_has_no_conflicting_pins(self):
        rows, count, chain = probe.family_selection(self.capture)
        self.assertEqual(chain["instance"], probe.FAMILY.name)
        self.assertEqual((count, len(rows)), (5139, 1942))
        self.assertEqual(probe.verify_boundary(probe.ROOT, rows, self.capture), 1942)

    def test_changed_native_chain_receipt_refuses_selection(self):
        with patch.object(probe, "CHAIN_SHA", "0" * 64):
            with self.assertRaisesRegex(ValueError, "CHAIN_RECEIPT_CHANGED"):
                probe.family_selection(self.capture)

    def test_changed_bytes_refuse_at_exit(self):
        with self.assertRaisesRegex(ValueError, "selected source input bytes changed"):
            with probe.guard_window(self.root, [self.row], self.capture):
                self.path.write_bytes(b"changed\n")

    def test_wrong_pin_and_symlink_refuse_at_entry(self):
        wrong = dict(self.row, sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "selected source input bytes changed"):
            with probe.guard_window(self.root, [wrong], self.capture):
                self.fail("body entered after wrong pin")
        self.path.unlink()
        self.path.symlink_to("elsewhere")
        with self.assertRaises((OSError, ValueError)):
            probe.verify_boundary(self.root, [self.row], self.capture)

    def test_conflict_refused_and_body_error_retained_with_exit_error(self):
        with self.assertRaisesRegex(ValueError, "UNION_PIN_CONFLICT"):
            probe.union_rows([{"files": [self.row]}, {"files": [dict(self.row, sha256="0" * 64)]}])
        with self.assertRaises(BaseExceptionGroup) as caught:
            with probe.guard_window(self.root, [self.row], self.capture):
                self.path.write_bytes(b"changed\n")
                raise RuntimeError("caller failed")
        self.assertEqual(len(caught.exception.exceptions), 2)
        self.assertIsInstance(caught.exception.exceptions[0], RuntimeError)
        self.assertIsInstance(caught.exception.exceptions[1], ValueError)

    def test_source_period_refuses_before_entry_and_after_expiry(self):
        past = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(ValueError, "SOURCE_PERIOD_EXPIRED"):
            with probe.guard_window(self.root, [self.row], self.capture, source_expires_at=past):
                self.fail("expired source entered body")
        soon = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(milliseconds=100)).isoformat()
        with self.assertRaisesRegex(ValueError, "SOURCE_PERIOD_EXPIRED"):
            with probe.guard_window(self.root, [self.row], self.capture, source_expires_at=soon):
                time.sleep(.15)


if __name__ == "__main__":
    unittest.main()
