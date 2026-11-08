#!/usr/bin/env python3
"""Inert challenge of the v3 event window; no Docker call or protected input."""

import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docker-source8-controller-candidate-0003/control.py"
RAW = SOURCE.read_bytes()
assert hashlib.sha256(RAW).hexdigest() == "094a932553d0371b34f55620cf5e7b26ee41afa5dba933590a70c5ef806e8418"
ns = {"__name__": "captured_control_independent_challenge"}
exec(compile(RAW, "<captured-v3-control>", "exec"), ns)


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


def container(cid, number):
    return {"Type": "container", "Action": "create", "timeNano": number,
            "Actor": {"ID": cid}}


def mount(cid, rw, number):
    return {"Type": "volume", "Action": "mount", "timeNano": number,
            "Actor": {"ID": "selected", "Attributes": {
                "container": cid, "read/write": rw}}}


def challenge(kind):
    rd, wr = os.pipe()
    os.set_blocking(rd, False)
    try:
        witness = ns["EventStream"].__new__(ns["EventStream"])
        witness.kind = kind
        witness.volume = "selected" if kind == "volume" else None
        witness.process = Process(rd)
        witness.partial = b""
        witness.closed = False
        witness.anchor_cid = "start"
        witness.terminal_cid = "terminal"
        witness.anchor_index = 0
        witness.terminal_index = 2
        if kind == "container":
            history = [container("start", 100), container("writer", 101),
                       container("terminal", 102)]
            foreign = container("foreign-rw-grant", 103)
            allowed = {"start", "writer", "terminal"}
        else:
            history = [mount("start", "false", 100),
                       mount("writer", "true", 101),
                       mount("terminal", "false", 102)]
            foreign = mount("foreign-rw-grant", "true", 103)
            allowed = "writer"
        witness.events = history[:]
        os.write(wr, (json.dumps(foreign) + "\n").encode())
        witness.poll(allowed)
        assert witness.events[-1] == foreign
        witness._replay = lambda: history[1:]
        accepted = witness.reconcile(allowed, "writer")
        assert accepted["live_event_count"] == 2
        return {"foreign_event_recorded_but_not_enforced": True,
                "reconcile_accepted": True, "selected_history_count": 2,
                "actual_event_count": len(witness.events)}
    finally:
        os.close(wr)
        os.close(rd)


print(json.dumps({"container": challenge("container"),
                  "volume": challenge("volume")}, sort_keys=True))
