#!/usr/bin/env python3
"""Inert preselection, skew, fragmentation, and postcustody replay tests."""
import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("source8_control_v5", HERE / "control.py")
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


def item(kind, action, cid, n, rw=None):
    actor = {"ID": cid if kind == "container" else "selected"}
    if kind == "volume":
        actor["Attributes"] = {"container": cid, "read/write": rw}
    return {"Type": kind, "Action": action, "timeNano": n, "Actor": actor}


class Boundaries(unittest.TestCase):
    def witness(self):
        rd, wr = os.pipe()
        os.set_blocking(rd, False)
        self.addCleanup(os.close, wr)
        self.addCleanup(os.close, rd)
        value = control.EventStream.__new__(control.EventStream)
        value.kind = "global"
        value.volume = "selected"
        value.process = Process(rd)
        value.partial = b""
        value.events = [item("container", "create", "preselect", 100)]
        value.anchor_cid = "preselect"
        value.anchor_index = 0
        value.terminal_cid = "terminal"
        value.terminal_index = None
        value.final_cid = None
        value.final_index = None
        value.volume_destroy_expected = False
        value.volume_destroy_seen = False
        value.volume_create_seen = False
        value.closed = False
        return value, wr

    def emit(self, wr, *items):
        os.write(wr, ("\n".join(json.dumps(x) for x in items) + "\n").encode())

    def test_foreign_create_after_preselection_before_volume_create_refused(self):
        w, fd = self.witness()
        self.emit(fd, item("container", "create", "foreign", 99))
        with self.assertRaisesRegex(control.Unknown, "UNADMITTED_CONTAINER_CREATE foreign"):
            w.poll(({"preselect"}, set()))

    def test_foreign_rw_mount_after_volume_create_before_type_anchors_refused(self):
        w, fd = self.witness()
        self.emit(fd, item("volume", "create", "", 101),
                  item("volume", "mount", "foreign", 99, "true"))
        with self.assertRaisesRegex(control.Unknown, "COMPETING_RW_MOUNT_EVENT foreign"):
            w.poll(({"preselect"}, set()))
        self.assertTrue(w.volume_create_seen)

    def test_foreign_create_during_two_stream_terminal_skew_refused(self):
        w, fd = self.witness()
        w.terminal_index = None
        self.emit(fd, item("container", "create", "foreign-skew", 103))
        with self.assertRaisesRegex(control.Unknown, "UNADMITTED_CONTAINER_CREATE foreign-skew"):
            w.poll(({"preselect", "terminal"}, set()))

    def test_fragmented_final_event_is_refused(self):
        w, fd = self.witness()
        w.terminal_index = 0
        w.final_cid = "final"
        w.final_index = 0
        foreign = json.dumps(item("container", "create", "foreign-final", 105)).encode()
        os.write(fd, foreign[:len(foreign) // 2])
        with patch.object(control.time, "monotonic", side_effect=[0, 3]):
            with self.assertRaisesRegex(control.Unknown, "INCOMPLETE_FINAL_EVENT_LINE global"):
                w.drain_complete(({"preselect", "final"}, set()))

    def test_fragment_completion_parses_and_refuses_foreign_create(self):
        w, fd = self.witness()
        foreign = (json.dumps(item("container", "create", "foreign-fragment", 105)) + "\n").encode()
        os.write(fd, foreign[:len(foreign) // 2])
        w.poll(({"preselect"}, set()))
        self.assertTrue(w.partial)
        os.write(fd, foreign[len(foreign) // 2:])
        with self.assertRaisesRegex(control.Unknown, "UNADMITTED_CONTAINER_CREATE foreign-fragment"):
            w.drain_complete(({"preselect"}, set()))

    def test_postcustody_replay_mismatch_refuses_missing_live_event(self):
        w, _ = self.witness()
        live = [item("volume", "create", "", 101),
                item("container", "create", "writer", 102),
                item("volume", "mount", "writer", 103, "true"),
                item("container", "create", "terminal", 104),
                item("volume", "destroy", "", 105),
                item("container", "create", "final", 106)]
        w.events.extend(live)
        w.terminal_index = 4
        w.final_cid = "final"
        w.final_index = 6
        w.volume_create_seen = True
        w.volume_destroy_expected = True
        w.volume_destroy_seen = True
        w._replay = lambda: live[:-1] + [item("container", "create", "foreign-tail", 105), live[-1]]
        with self.assertRaisesRegex(control.Unknown, "EVENT_REPLAY_MISMATCH global"):
            w.reconcile(({"preselect", "writer", "terminal", "final"}, {"writer"}), "writer")

    def test_postcustody_replay_includes_selection_and_destroy(self):
        w, _ = self.witness()
        live = [item("volume", "create", "", 101),
                item("container", "create", "writer", 102),
                item("volume", "mount", "writer", 103, "true"),
                item("container", "create", "terminal", 104),
                item("volume", "destroy", "", 105),
                item("container", "create", "final", 106)]
        w.events.extend(live)
        w.terminal_index = 4
        w.final_cid = "final"
        w.final_index = 6
        w.volume_create_seen = True
        w.volume_destroy_expected = True
        w.volume_destroy_seen = True
        w._replay = lambda: live
        result = w.reconcile(({"preselect", "writer", "terminal", "final"}, {"writer"}), "writer")
        self.assertEqual((result["live_event_count"], result["replay_event_count"]), (6, 6))


if __name__ == "__main__":
    unittest.main()
