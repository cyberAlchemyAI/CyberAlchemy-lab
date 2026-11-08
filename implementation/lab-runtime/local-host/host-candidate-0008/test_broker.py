#!/usr/bin/env python3
"""Disposable unprivileged tests; never touch the proposed host paths."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import hashlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import broker  # noqa: E402
import snapshot_verify  # noqa: E402


class BrokerFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cal-host-candidate-0008-", dir="/tmp")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("instances", "custody", "target"):
            (self.root / name).mkdir(mode=0o700)
        self.uid, self.gid = os.getuid(), os.getgid()
        self.device = os.stat(self.root).st_dev
        self.instances = os.open(self.root / "instances", broker.O_DIR)
        self.custody = os.open(self.root / "custody", broker.O_DIR)
        self.target = os.open(self.root / "target", broker.O_DIR)
        self.addCleanup(os.close, self.instances)
        self.addCleanup(os.close, self.custody)
        self.addCleanup(os.close, self.target)
        self.mount_id = broker.mount_id(self.instances)
        (self.root / "slot").write_bytes(b"fixture slot only\n")
        self.slot = os.open(self.root / "slot", os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
        self.addCleanup(os.close, self.slot)
        self.digest = "a" * 64
        self.name = "i-" + self.digest[:16] + "-e1"
        self.attempt = broker.SelectedAttempt(self.digest, "e1", self.name, self.slot)

    def prepare(self):
        value = broker._prepare_fixture_child(
            self.instances, self.custody, self.attempt, parent_uid=self.uid,
            parent_gid=self.gid, service_uid=self.uid, service_gid=self.gid,
            device=self.device, expected_mount_id=self.mount_id)
        self.addCleanup(value.close)
        return value

    def test_first_instant_mode_record_and_replay_refusal(self):
        original_mkdir = broker.os.mkdir
        seen = []

        def inspect_mkdir(name, *, mode, dir_fd):
            original_mkdir(name, mode=mode, dir_fd=dir_fd)
            first = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
            seen.append((mode, first.st_mode & 0o777))

        with patch.object(broker.os, "mkdir", inspect_mkdir):
            value = self.prepare()
        self.assertEqual(seen, [(0o700, 0o700)])
        self.assertFalse(os.get_inheritable(value.child_fd))
        claim = self.root / "custody" / (self.digest + "-e1.claim.json")
        prepared = self.root / "custody" / (self.digest + "-e1.prepared.json")
        slot_stat = os.fstat(self.slot)
        slot_claim = self.root / "custody" / f"slot-{slot_stat.st_dev:x}-{slot_stat.st_ino:x}.claim.json"
        self.assertEqual(json.loads(claim.read_text())["state"], "claimed")
        self.assertEqual(json.loads(prepared.read_text())["child_inode"], value.child_inode)
        self.assertEqual(json.loads(slot_claim.read_text())["state"], "slot-reserved")
        self.assertEqual(claim.stat().st_mode & 0o777, 0o600)
        self.assertEqual(prepared.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(broker.Refused):
            self.prepare()

    def test_one_held_slot_cannot_create_a_second_epoch_child(self):
        self.prepare()
        second = broker.SelectedAttempt(self.digest, "e2", "i-" + self.digest[:16] + "-e2", self.slot)
        with self.assertRaisesRegex(broker.Refused, "slot already reserved"):
            broker._prepare_fixture_child(self.instances, self.custody, second,
                                 parent_uid=self.uid, parent_gid=self.gid,
                                 service_uid=self.uid, service_gid=self.gid,
                                 device=self.device, expected_mount_id=self.mount_id)
        self.assertFalse((self.root / "instances" / second.child_name).exists())

    def test_instances_and_custody_must_be_distinct_inodes(self):
        with self.assertRaisesRegex(broker.Refused, "same inode"):
            broker._prepare_fixture_child(self.instances, self.instances, self.attempt,
                                 parent_uid=self.uid, parent_gid=self.gid,
                                 service_uid=self.uid, service_gid=self.gid,
                                 device=self.device, expected_mount_id=self.mount_id)
        self.assertEqual(list((self.root / "instances").iterdir()), [])

    def test_instances_fsync_precedes_prepared_record(self):
        original_fsync = broker.os.fsync
        original_write = broker._write_exclusive
        instances_synced = False

        def record_fsync(fd):
            nonlocal instances_synced
            if fd == self.instances:
                instances_synced = True
            return original_fsync(fd)

        def record_write(directory_fd, name, body):
            if name.endswith(".prepared.json"):
                self.assertTrue(instances_synced)
            return original_write(directory_fd, name, body)

        with patch.object(broker.os, "fsync", record_fsync), patch.object(broker, "_write_exclusive", record_write):
            self.prepare()

    def test_nofollow_chain_and_existing_symlink_refusal(self):
        (self.root / "alias").symlink_to("instances", target_is_directory=True)
        anchor = os.open(self.root, broker.O_DIR)
        try:
            with self.assertRaises(OSError):
                broker.open_directory_chain(anchor, ("alias",), uid=self.uid,
                                            gid=self.gid, modes=(0o700,), device=self.device,
                                            expected_mount_id=self.mount_id)
            fd = broker.open_directory_chain(anchor, ("instances",), uid=self.uid,
                                             gid=self.gid, modes=(0o700,), device=self.device,
                                             expected_mount_id=self.mount_id)
            self.assertFalse(os.get_inheritable(fd))
            os.close(fd)
        finally:
            os.close(anchor)
        (self.root / "instances" / self.name).symlink_to(self.root / "target", target_is_directory=True)
        with self.assertRaises(broker.Refused):
            self.prepare()
        self.assertEqual(list((self.root / "custody").iterdir()), [])

    def test_fd_exec_noninheritance_even_without_subprocess_close_fds(self):
        value = self.prepare()
        fds = [self.instances, self.custody, self.slot, value.child_fd]
        code = "import os,sys; print(''.join('1' if os.path.exists('/proc/self/fd/'+x) else '0' for x in sys.argv[1:]))"
        completed = subprocess.run([sys.executable, "-c", code, *(str(fd) for fd in fds)],
                                   check=True, capture_output=True, text=True, close_fds=False)
        self.assertEqual(completed.stdout.strip(), "0" * len(fds))

    def test_target_identity_comparison_refuses_substitution(self):
        value = self.prepare()
        identity = broker.check_target_identity(value, self.instances, self.name,
                                                parent_uid=self.uid, parent_gid=self.gid,
                                                parent_mode=0o700, parent_device=self.device)
        self.assertEqual(identity["source_inode"], value.child_inode)
        self.assertEqual(identity["host_mount_id"], value.host_mount_id)
        (self.root / "target" / "other").mkdir(mode=0o700)
        with self.assertRaises(broker.Refused):
            broker.check_target_identity(value, self.target, "other",
                                         parent_uid=self.uid, parent_gid=self.gid,
                                         parent_mode=0o700, parent_device=self.device)
        (self.root / "target" / "alias").symlink_to(self.root / "instances" / self.name)
        with self.assertRaises(OSError):
            broker.check_target_identity(value, self.target, "alias",
                                         parent_uid=self.uid, parent_gid=self.gid,
                                         parent_mode=0o700, parent_device=self.device)

    def test_same_uid_fixture_is_negative_control_not_isolation_proof(self):
        self.prepare()
        code = "import os,sys; print(os.listdir(sys.argv[1]))"
        completed = subprocess.run([sys.executable, "-c", code,
                                    str(self.root / "instances")],
                                   check=True, capture_output=True, text=True)
        self.assertIn(self.name, completed.stdout)
        # Root ownership + installed proc/mount denial cannot be tested as this UID.

    def test_exact_read_only_snapshot_and_alias_refusal(self):
        snapshot = self.root / "snapshot"
        snapshot.mkdir(mode=0o700)
        (snapshot / "src").mkdir(mode=0o700)
        member = snapshot / "src" / "run.py"
        member.write_bytes(b"fixture program\n")
        member.chmod(0o444)
        (snapshot / "src").chmod(0o555)
        snapshot.chmod(0o555)
        fd = os.open(snapshot, broker.O_DIR)
        try:
            manifest = {"schema": "cal-snapshot-0005", "root_uid": self.uid,
                        "root_gid": self.gid, "root_mode": "0555",
                        "root_device": self.device, "root_mount_id": broker.mount_id(fd),
                        "members": [
                            {"path": "src", "kind": "directory", "mode": "0555"},
                            {"path": "src/run.py", "kind": "file", "mode": "0444",
                             "sha256": hashlib.sha256(b"fixture program\n").hexdigest()}]}
        finally:
            os.close(fd)
        self.assertEqual(snapshot_verify.verify(snapshot, manifest)["member_count"], 2)
        snapshot.chmod(0o755)
        (snapshot / "surprise").write_bytes(b"x")
        snapshot.chmod(0o555)
        with self.assertRaises(broker.Refused):
            snapshot_verify.verify(snapshot, manifest)
        snapshot.chmod(0o755)
        (snapshot / "surprise").unlink()
        (snapshot / "src").chmod(0o755)
        member.unlink()
        member.symlink_to(self.root / "slot")
        (snapshot / "src").chmod(0o555)
        snapshot.chmod(0o555)
        with self.assertRaises(OSError):
            snapshot_verify.verify(snapshot, manifest)

    def test_snapshot_hash_does_not_prove_concurrent_path_custody(self):
        snapshot = self.root / "snapshot-race"
        snapshot.mkdir(mode=0o700)
        member = snapshot / "input.txt"
        original = b"selected input\n"
        member.write_bytes(original)
        member.chmod(0o444)
        snapshot.chmod(0o555)
        fd = os.open(snapshot, broker.O_DIR)
        try:
            manifest = {"schema": "cal-snapshot-0005", "root_uid": self.uid,
                        "root_gid": self.gid, "root_mode": "0555",
                        "root_device": self.device, "root_mount_id": broker.mount_id(fd),
                        "members": [{"path": "input.txt", "kind": "file", "mode": "0444",
                                     "sha256": hashlib.sha256(original).hexdigest()}]}
        finally:
            os.close(fd)
        original_read = snapshot_verify.os.read
        swapped = False

        def swap_path_before_read(file_fd, length):
            nonlocal swapped
            if not swapped:
                snapshot.chmod(0o755)
                member.unlink()
                member.write_bytes(b"different input\n")
                member.chmod(0o444)
                snapshot.chmod(0o555)
                swapped = True
            return original_read(file_fd, length)

        with patch.object(snapshot_verify.os, "read", swap_path_before_read):
            # The held descriptor still hashes the old inode. The result is
            # deliberately a negative control, not a custody PASS.
            self.assertEqual(snapshot_verify.verify(snapshot, manifest)["member_count"], 1)
        self.assertTrue(swapped)
        self.assertNotEqual(hashlib.sha256(member.read_bytes()).hexdigest(),
                            manifest["members"][0]["sha256"])

    def test_closed_epoch_and_exact_instance_grammar_before_writes(self):
        for epoch in ("e0", "e01", "e-1", "E1", "../e1", "e1/other", "e12345678901"):
            candidate = broker.SelectedAttempt(self.digest, epoch,
                                               "i-" + self.digest[:16] + "-" + epoch,
                                               self.slot)
            with self.subTest(epoch=epoch), self.assertRaises(broker.Refused):
                candidate.validate()
        self.assertEqual(list((self.root / "custody").iterdir()), [])

    def test_held_slot_and_intent_bytes_are_bound_before_effect(self):
        intent_bytes = b"fixture Root intent bytes\n"
        intent_path = self.root / "intent"
        intent_path.write_bytes(intent_bytes)
        intent_path.chmod(0o600)
        (self.root / "slot").chmod(0o600)
        input_parent = os.open(self.root, broker.O_DIR)
        self.addCleanup(os.close, input_parent)
        intent_fd = broker.open_noatime_input(input_parent, "intent",
                                              uid=self.uid, gid=self.gid, mode=0o600)
        self.addCleanup(os.close, intent_fd)
        slot_fd = broker.open_noatime_input(input_parent, "slot",
                                            uid=self.uid, gid=self.gid, mode=0o600)
        self.addCleanup(os.close, slot_fd)
        digest = hashlib.sha256(intent_bytes).hexdigest()
        attempt = broker.SelectedAttempt(digest, "e1", "i-" + digest[:16] + "-e1", slot_fd)
        slot_stat = os.fstat(slot_fd)
        binding = broker.BoundInputs(intent_fd, digest, self.uid, self.gid, 0o600,
                                     hashlib.sha256(b"fixture slot only\n").hexdigest(),
                                     self.uid, self.gid, 0o600,
                                     slot_stat.st_dev, slot_stat.st_ino)
        binding.verify(attempt)
        with self.assertRaisesRegex(broker.Refused, "HOST_ACTIVATION_DISABLED"):
            broker.prepare_bound_child(self.instances, self.custody, attempt, binding,
                                       parent_uid=self.uid, parent_gid=self.gid,
                                       service_uid=20001, service_gid=20001,
                                       device=self.device, expected_mount_id=self.mount_id)
        self.assertEqual(list((self.root / "custody").iterdir()), [])
        intent_path.write_bytes(b"changed intent\n")
        with self.assertRaises(broker.Refused):
            binding.verify(attempt)
        intent_path.write_bytes(intent_bytes)
        (self.root / "slot").write_bytes(b"changed slot\n")
        with self.assertRaises(broker.Refused):
            binding.verify(attempt)

    def test_noatime_reads_and_plain_fd_refusal(self):
        intent = self.root / "intent-atime"
        intent.write_bytes(b"fixture Root\n")
        intent.chmod(0o600)
        slot = self.root / "slot-atime"
        slot.write_bytes(b"fixture slot\n")
        slot.chmod(0o600)
        stale = time.time_ns() - 30 * 24 * 3600 * 1_000_000_000
        for path in (intent, slot):
            os.utime(path, ns=(stale, os.stat(path).st_mtime_ns))
        input_parent = os.open(self.root, broker.O_DIR)
        self.addCleanup(os.close, input_parent)
        intent_fd = broker.open_noatime_input(input_parent, "intent-atime",
                                              uid=self.uid, gid=self.gid, mode=0o600)
        slot_fd = broker.open_noatime_input(input_parent, "slot-atime",
                                            uid=self.uid, gid=self.gid, mode=0o600)
        self.addCleanup(os.close, intent_fd)
        self.addCleanup(os.close, slot_fd)
        digest = hashlib.sha256(b"fixture Root\n").hexdigest()
        attempt = broker.SelectedAttempt(digest, "e1", "i-" + digest[:16] + "-e1", slot_fd)
        st = os.fstat(slot_fd)
        binding = broker.BoundInputs(intent_fd, digest, self.uid, self.gid, 0o600,
                                     hashlib.sha256(b"fixture slot\n").hexdigest(),
                                     self.uid, self.gid, 0o600, st.st_dev, st.st_ino)
        binding.verify(attempt)
        self.assertEqual(intent.stat().st_atime_ns, stale)
        self.assertEqual(slot.stat().st_atime_ns, stale)
        plain_fd = os.open(intent, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        self.addCleanup(os.close, plain_fd)
        plain_binding = broker.BoundInputs(plain_fd, digest, self.uid, self.gid, 0o600,
                                           binding.slot_sha256, self.uid, self.gid,
                                           0o600, st.st_dev, st.st_ino)
        with self.assertRaisesRegex(broker.Refused, "O_NOATIME_REQUIRED_BEFORE_READ"):
            plain_binding.verify(attempt)
        self.assertEqual(intent.stat().st_atime_ns, stale)
        with patch.object(broker.os, "O_NOATIME", None):
            with self.assertRaisesRegex(broker.Refused, "O_NOATIME unavailable"):
                broker.open_noatime_input(input_parent, "intent-atime",
                                          uid=self.uid, gid=self.gid, mode=0o600)
    def test_attachment_detects_same_uid_replacement_in_scratch(self):
        value = self.prepare()
        self.assertEqual(
            broker.verify_named_attachment(self.instances, self.name, value.child_fd,
                                           parent_uid=self.uid, parent_gid=self.gid,
                                           child_uid=self.uid, child_gid=self.gid,
                                           parent_mode=0o700, child_mode=0o700,
                                           device=self.device, expected_mount_id=self.mount_id),
            (value.child_device, value.child_inode))
        os.rename(self.root / "instances" / self.name,
                  self.root / "instances" / (self.name + "-old"))
        (self.root / "instances" / self.name).mkdir(mode=0o700)
        with self.assertRaisesRegex(broker.Refused, "detached or replaced"):
            broker.verify_named_attachment(self.instances, self.name, value.child_fd,
                                           parent_uid=self.uid, parent_gid=self.gid,
                                           child_uid=self.uid, child_gid=self.gid,
                                           parent_mode=0o700, child_mode=0o700,
                                           device=self.device, expected_mount_id=self.mount_id)

    def test_no_host_activation_entrypoint(self):
        with self.assertRaisesRegex(broker.Refused, "HOST_ACTIVATION_DISABLED"):
            broker.activation_capability()
        with self.assertRaisesRegex(broker.Refused, "HOST_ACTIVATION_DISABLED"):
            broker.prepare_child(self.instances, self.custody, self.attempt)
        with patch.object(broker, "_read_held_regular", side_effect=AssertionError("input read")):
            with self.assertRaisesRegex(broker.Refused, "HOST_ACTIVATION_DISABLED"):
                broker.prepare_bound_child(self.instances, self.custody, self.attempt,
                                           None, parent_uid=0, parent_gid=0,
                                           service_uid=20001, service_gid=20001,
                                           device=self.device, expected_mount_id=self.mount_id)
        with self.assertRaisesRegex(broker.Refused, "FIXTURE_ONLY_NO_ROOT_WRITES"):
            broker._prepare_fixture_child(self.instances, self.custody, self.attempt,
                                          parent_uid=0, parent_gid=0,
                                          service_uid=20001, service_gid=20001,
                                          device=self.device, expected_mount_id=self.mount_id)
        with patch.object(broker.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(broker.Refused, "FIXTURE_ONLY_NO_ROOT_WRITES"):
                broker._write_exclusive(self.custody, "must-not-exist", {})
        outside = self.root / "other"
        outside.mkdir(mode=0o700)
        outside_fd = os.open(outside, broker.O_DIR)
        self.addCleanup(os.close, outside_fd)
        with self.assertRaisesRegex(broker.Refused, "FIXTURE_SCOPE_REQUIRED"):
            broker._write_exclusive(outside_fd, "must-not-exist", {})
        self.assertEqual(list((self.root / "custody").iterdir()), [])
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
