import datetime as dt
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compose
import probe


class OriginalCallbackWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture = probe.selected_capture()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cal-original-callback-window-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file = self.root / "input"
        self.file.write_bytes(b"bound input\n")
        self.row = {"path": "input", "sha256": hashlib.sha256(self.file.read_bytes()).hexdigest()}
        self.calls = []
        self.grant = True
        self.lease = True
        self.key = Ed25519PrivateKey.generate()
        self.message = b"selected package"
        self.signature = self.key.sign(self.message)

    def checks(self):
        def source():
            self.calls.append("source")
        def package():
            self.calls.append("package")
            self.key.public_key().verify(self.signature, self.message)
        def policy():
            self.calls.append("policy")
            if not self.grant:
                raise ValueError("POLICY_REVOKED")
        def lease():
            self.calls.append("lease")
            if not self.lease:
                raise ValueError("LEASE_EXPIRED")
        return compose.OriginalChecks(source, package, policy, lease)

    def test_callbacks_run_once_per_boundary_and_real_bytes_are_verified(self):
        with compose.original_callback_window(self.root, [self.row], self.capture, self.checks()):
            self.assertEqual(self.calls, ["source", "package", "policy", "lease"])
        self.assertEqual(self.calls, ["source", "package", "policy", "lease"] * 2)

    def test_wrong_signature_refuses_entry(self):
        self.signature = self.key.sign(b"different package")
        with self.assertRaises(InvalidSignature):
            with compose.original_callback_window(self.root, [self.row], self.capture, self.checks()):
                self.fail("entered with wrong signature")
        self.assertEqual(self.calls, ["source", "package"])

    def test_revocation_and_lease_expiry_refuse_exit(self):
        with self.assertRaisesRegex(ValueError, "POLICY_REVOKED"):
            with compose.original_callback_window(self.root, [self.row], self.capture, self.checks()):
                self.grant = False
        self.assertEqual(self.calls, ["source", "package", "policy", "lease"] * 2)
        self.calls.clear()
        self.grant = True
        with self.assertRaisesRegex(ValueError, "LEASE_EXPIRED"):
            with compose.original_callback_window(self.root, [self.row], self.capture, self.checks()):
                self.lease = False

    def test_changed_bytes_and_body_error_both_survive_exit(self):
        with self.assertRaises(BaseExceptionGroup) as caught:
            with compose.original_callback_window(self.root, [self.row], self.capture, self.checks()):
                self.file.write_bytes(b"changed\n")
                raise RuntimeError("BODY_FAILED")
        self.assertIsInstance(caught.exception.exceptions[0], RuntimeError)
        self.assertIsInstance(caught.exception.exceptions[1], ValueError)
        self.assertEqual(self.calls, ["source", "package", "policy", "lease"] * 2)

    def test_expired_source_refuses_entry_and_exit(self):
        past = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1)).isoformat()
        with self.assertRaisesRegex(ValueError, "SOURCE_PERIOD_EXPIRED"):
            with compose.original_callback_window(self.root, [self.row], self.capture, self.checks(), source_expires_at=past):
                self.fail("expired source entered")
        self.assertEqual(self.calls, [])
        now = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(milliseconds=100)).isoformat()
        with self.assertRaisesRegex(ValueError, "SOURCE_PERIOD_EXPIRED"):
            with compose.original_callback_window(self.root, [self.row], self.capture, self.checks(), source_expires_at=now):
                import time
                time.sleep(.15)

    def test_non_callable_original_refused(self):
        with self.assertRaisesRegex(ValueError, "ORIGINAL_CALLBACK_REQUIRED"):
            compose.OriginalChecks(lambda: None, None, lambda: None, lambda: None)


if __name__ == "__main__":
    unittest.main()
