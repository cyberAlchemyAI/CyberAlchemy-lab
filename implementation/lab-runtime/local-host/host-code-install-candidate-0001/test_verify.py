"""Bounded tests for inactive code-install preflight."""

from __future__ import annotations

import importlib.util
import hashlib
import os
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location("host_code_install_verify", Path(__file__).with_name("verify.py"))
assert SPEC and SPEC.loader
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cal-code-install-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.py"
        self.source.write_bytes(b"one pinned byte string\n")
        self.digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        (self.root / "usr" / "local" / "libexec").mkdir(parents=True)
        for path in (self.root, self.root / "usr", self.root / "usr" / "local",
                     self.root / "usr" / "local" / "libexec"):
            path.chmod(0o700)

    def test_exact_preflight_is_inactive(self):
        result = verify.preflight(self.source, str(self.root), os.geteuid(), self.digest)
        self.assertEqual(result["status"], "INACTIVE_PREFLIGHT_ONLY")
        self.assertFalse(result["apply_enabled"])
        self.assertFalse((self.root / "usr/local/libexec/cal-host-storage-release-0001").exists())

    def test_source_old_atime_unchanged(self):
        old_ns = 1_600_000_000_000_000_000
        os.utime(self.source, ns=(old_ns, old_ns))
        payload, result = verify.source_bytes(self.source, self.digest)
        self.assertEqual(payload, b"one pinned byte string\n")
        self.assertEqual(result["atime_ns"], old_ns)
        self.assertEqual(self.source.stat().st_atime_ns, old_ns)

    def test_changed_source_refuses(self):
        self.source.write_bytes(b"changed")
        with self.assertRaisesRegex(verify.Refused, "SOURCE_HASH_CHANGED"):
            verify.source_bytes(self.source, self.digest)

    def test_source_symlink_refuses(self):
        link = self.root / "source-link.py"
        link.symlink_to(self.source)
        with self.assertRaisesRegex(verify.Refused, "SOURCE_NOATIME_OPEN_REFUSED"):
            verify.source_bytes(link, self.digest)

    def test_destination_name_consumed_refuses(self):
        (self.root / "usr/local/libexec/cal-host-storage-release-0001").mkdir()
        with self.assertRaisesRegex(verify.Refused, "CODE_PACKAGE_NAME_ALREADY_CONSUMED"):
            verify.destination_preimage(str(self.root), os.geteuid())

    def test_writable_ancestor_refuses(self):
        (self.root / "usr/local").chmod(0o777)
        with self.assertRaisesRegex(verify.Refused, "DESTINATION_ANCESTOR_UNTRUSTED"):
            verify.destination_preimage(str(self.root), os.geteuid())

    def test_symlink_ancestor_refuses(self):
        (self.root / "usr/local/libexec").rmdir()
        (self.root / "usr/local/libexec").symlink_to(self.root)
        with self.assertRaises(OSError):
            verify.destination_preimage(str(self.root), os.geteuid())

    def test_live_apply_always_refuses_before_plan(self):
        import subprocess
        result = subprocess.run(["python3", "-B", str(Path(__file__).with_name("verify.py")),
                                 "--apply"], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 3)
        self.assertIn("HOST_CODE_INSTALL_NOT_RELEASED", result.stderr)


if __name__ == "__main__":
    unittest.main()
