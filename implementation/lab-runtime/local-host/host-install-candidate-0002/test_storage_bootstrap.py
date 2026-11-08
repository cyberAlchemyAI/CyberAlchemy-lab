"""Bounded tests for host-install candidate 0002; no host apply."""

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("storage_bootstrap_v2", HERE / "storage_bootstrap.py")
bootstrap = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bootstrap
SPEC.loader.exec_module(bootstrap)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.session = bootstrap.new_scratch_session()
        self.path = Path(self.session.path)

    def tearDown(self):
        bootstrap.close_scratch_session(self.session)
        shutil.rmtree(self.path)

    def test_host_apply_refuses_before_host_read(self):
        result = subprocess.run([sys.executable, str(HERE / "storage_bootstrap.py"), "--apply"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 3)
        self.assertIn("HOST_INSTALL_EFFECT_DISABLED", result.stderr)

    def test_fresh_session_and_modes(self):
        rows = bootstrap._fixture_stage(self.session)
        self.assertEqual([row.name for row in rows], list(bootstrap.NAMES))
        self.assertEqual((self.path / "cyberalchemy-lab").stat().st_mode & 0o777, 0o755)
        for name in ("source8-v1", "instances", "custody", "retained"):
            target = self.path / "cyberalchemy-lab" / "source8-v1"
            if name != "source8-v1":
                target /= name
            self.assertEqual(target.stat().st_mode & 0o777, 0o700)
        disposition = bootstrap._fixture_rollback_plan(self.session, rows)
        self.assertFalse(disposition["deletion_enabled"])
        self.assertTrue((self.path / "cyberalchemy-lab").exists())

    def test_replay_refuses_and_preserves(self):
        bootstrap._fixture_stage(self.session)
        with self.assertRaises(FileExistsError):
            bootstrap._fixture_stage(self.session)
        self.assertTrue((self.path / "cyberalchemy-lab" / "source8-v1" / "custody").is_dir())

    def test_rollback_plan_refuses_dependency_without_removal(self):
        rows = bootstrap._fixture_stage(self.session)
        leaf = self.path / "cyberalchemy-lab" / "source8-v1" / "retained" / "evidence"
        leaf.write_text("retain")
        with self.assertRaises(bootstrap.Refused):
            bootstrap._fixture_rollback_plan(self.session, rows)
        self.assertEqual(leaf.read_text(), "retain")
        self.assertTrue((self.path / "cyberalchemy-lab" / "source8-v1" / "instances").exists())

    def test_rollback_plan_refuses_alien_replacement(self):
        rows = bootstrap._fixture_stage(self.session)
        root = self.path / "cyberalchemy-lab" / "source8-v1"
        (root / "retained").rename(root / "retained-original")
        (root / "retained").mkdir(mode=0o700)
        with self.assertRaises(bootstrap.Refused):
            bootstrap._fixture_rollback_plan(self.session, rows)
        self.assertTrue((root / "retained").is_dir())
        self.assertTrue((root / "retained-original").is_dir())

    def test_make_refuses_outside_session_and_wrong_stage_parent(self):
        outside = os.open("/tmp", bootstrap.O_DIR)
        try:
            with self.assertRaises(bootstrap.Refused):
                bootstrap._make(self.session, outside, "cyberalchemy-lab", os.geteuid(), os.getegid(),
                                os.fstat(outside).st_dev)
        finally:
            os.close(outside)
        inner = self.path / "other"
        inner.mkdir()
        fd = os.open(inner, bootstrap.O_DIR)
        try:
            with self.assertRaises(bootstrap.Refused):
                bootstrap._make(self.session, fd, "custody", os.geteuid(), os.getegid(),
                                os.fstat(fd).st_dev)
        finally:
            os.close(fd)
        self.assertEqual(list(inner.iterdir()), [])

    def test_detached_or_forged_session_refuses(self):
        forged = bootstrap.ScratchSession(self.session.path, self.session.fd, "0" * 32)
        with self.assertRaises(bootstrap.Refused):
            bootstrap._fixture_stage(forged)
        other = self.path.with_name(self.path.name + "-moved")
        self.path.rename(other)
        try:
            with self.assertRaises(bootstrap.Refused):
                bootstrap._fixture_stage(self.session)
        finally:
            other.rename(self.path)

    def test_same_uid_create_interleaving_is_not_proof(self):
        # Same-UID replacement can occur between mkdir and open. A trusted
        # parent is required; this scratch test preserves counterevidence.
        original = bootstrap.os.mkdir
        root_name = self.path / "cyberalchemy-lab"

        def swap(name, mode=0o777, *, dir_fd=None):
            original(name, mode=mode, dir_fd=dir_fd)
            if name == "cyberalchemy-lab":
                root_name.rename(self.path / "created-but-detached")
                original(name, mode=0o700, dir_fd=dir_fd)

        with mock.patch.object(bootstrap.os, "mkdir", side_effect=swap):
            rows = bootstrap._fixture_stage(self.session)
        self.assertNotEqual(rows[0].ino, (self.path / "created-but-detached").stat().st_ino)
        self.assertTrue((self.path / "created-but-detached").is_dir())

    def test_plan_inactive(self):
        result = bootstrap.plan()
        self.assertFalse(result["activation"])
        self.assertEqual(result["status"], "INACTIVE_NO_HOST_APPLY")


if __name__ == "__main__":
    unittest.main()
