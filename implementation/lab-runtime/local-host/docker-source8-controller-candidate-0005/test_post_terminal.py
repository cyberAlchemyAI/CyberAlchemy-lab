#!/usr/bin/env python3
"""Inert event-window and two-stream skew controls; no Docker effects."""
import importlib.util
import json
import os
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("source8_control_v4", HERE / "control.py")
control = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(control)


class Reader:
    def __init__(self, fd):
        self.fd = fd

    def fileno(self):
        return self.fd


class Process:
    def __init__(self, fd):
        self.stdout = Reader(fd)

    def poll(self):
        return None


def container(cid, n, action="create"):
    return {"Type": "container", "Action": action, "timeNano": n,
            "Actor": {"ID": cid}}


def volume(cid, rw, n, action="mount"):
    return {"Type": "volume", "Action": action, "timeNano": n,
            "Actor": {"ID": "selected", "Attributes": {
                "container": cid, "read/write": rw}}}


class InertWindowTests(unittest.TestCase):
    def witness(self, kind, *, terminal=True, final=False, destroy_expected=False):
        rd, wr = os.pipe()
        os.set_blocking(rd, False)
        self.addCleanup(os.close, wr)
        self.addCleanup(os.close, rd)
        value = control.EventStream.__new__(control.EventStream)
        value.kind = kind
        value.volume = "selected" if kind == "volume" else None
        value.process = Process(rd)
        value.partial = b""
        value.closed = False
        value.anchor_cid = "start"
        value.anchor_index = 0
        value.terminal_cid = "terminal"
        value.terminal_index = 2 if terminal else None
        value.final_cid = "final" if kind == "container" else "selected"
        value.final_index = 4 if final else None
        value.volume_destroy_expected = destroy_expected
        value.volume_destroy_seen = final if kind == "volume" else False
        value.events = ([container("start", 100), container("writer", 101),
                         container("terminal", 102)] if kind == "container" else
                        [volume("start", "false", 100), volume("writer", "true", 101),
                         volume("terminal", "false", 102)])
        return value, wr

    def test_foreign_create_after_terminal_refused(self):
        witness, wr = self.witness("container")
        os.write(wr, (json.dumps(container("foreign-stopped-rw", 99)) + "\n").encode())
        with self.assertRaisesRegex(control.Unknown, "UNADMITTED_CONTAINER_CREATE"):
            witness.poll({"start", "writer", "terminal"})

    def test_foreign_rw_mount_after_terminal_refused(self):
        witness, wr = self.witness("volume")
        os.write(wr, (json.dumps(volume("foreign-rw", "true", 99)) + "\n").encode())
        with self.assertRaisesRegex(control.Unknown, "COMPETING_RW_MOUNT_EVENT"):
            witness.poll("writer")

    def test_container_terminal_before_volume_terminal_skew_refuses(self):
        witness, wr = self.witness("container")
        os.write(wr, (json.dumps(container("foreign-skew", 103)) + "\n").encode())
        with self.assertRaisesRegex(control.Unknown, "UNADMITTED_CONTAINER_CREATE"):
            witness.poll({"start", "writer", "terminal"})

    def test_volume_destroy_before_container_final_skew_refuses(self):
        witness, wr = self.witness("container")
        os.write(wr, (json.dumps(container("foreign-after-volume-destroy", 104)) + "\n").encode())
        with self.assertRaisesRegex(control.Unknown, "UNADMITTED_CONTAINER_CREATE"):
            witness.poll({"start", "writer", "terminal", "final"})

    def test_foreign_create_after_final_container_barrier_refused(self):
        witness, wr = self.witness("container", final=True)
        os.write(wr, (json.dumps(container("foreign-after-final", 105)) + "\n").encode())
        with self.assertRaisesRegex(control.Unknown, "UNADMITTED_CONTAINER_CREATE"):
            witness.poll({"start", "writer", "terminal", "final"})

    def test_recreate_after_final_volume_destroy_refused(self):
        witness, wr = self.witness("volume", final=True, destroy_expected=True)
        os.write(wr, (json.dumps({"Type": "volume", "Action": "create",
                                  "timeNano": 105, "Actor": {"ID": "selected"}}) + "\n").encode())
        with self.assertRaisesRegex(control.Unknown, "VOLUME_RECREATE_EVENT"):
            witness.poll("writer")

    def test_unexpected_destroy_and_recreate_refuse(self):
        witness, wr = self.witness("volume")
        os.write(wr, (json.dumps({"Type": "volume", "Action": "destroy",
                                  "timeNano": 103, "Actor": {"ID": "selected"}}) + "\n").encode())
        with self.assertRaisesRegex(control.Unknown, "UNEXPECTED_VOLUME_DESTROY_EVENT"):
            witness.poll("writer")
        witness, wr = self.witness("volume", destroy_expected=True)
        os.write(wr, (json.dumps({"Type": "volume", "Action": "create",
                                  "timeNano": 103, "Actor": {"ID": "selected"}}) + "\n").encode())
        with self.assertRaisesRegex(control.Unknown, "VOLUME_RECREATE_EVENT"):
            witness.poll("writer")

    def test_replay_requires_final_not_intermediate_terminal(self):
        witness, _ = self.witness("container")
        with self.assertRaisesRegex(control.Unknown, "EVENT_BARRIERS_INCOMPLETE"):
            witness.reconcile({"start", "writer", "terminal"}, "writer")


if __name__ == "__main__":
    unittest.main()
