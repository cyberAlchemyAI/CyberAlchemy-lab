#!/usr/bin/python3.14 -I
"""Inert regression: post-anchor events with lower timeNano must not vanish."""

import json
import os
from pathlib import Path

namespace = {"__name__": "captured_control_test"}
source = (Path(__file__).resolve().parent / "control.py").read_bytes()
exec(compile(source, "<captured-control-test>", "exec"), namespace)


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


def case(kind, foreign):
    read_fd, write_fd = os.pipe()
    try:
        os.set_blocking(read_fd, False)
        witness = namespace["EventStream"].__new__(namespace["EventStream"])
        witness.kind = kind
        witness.volume = "selected" if kind == "volume" else None
        witness.process = Process(read_fd)
        witness.partial = b""
        witness.events = [{"Type": kind, "Action": "create", "timeNano": 100,
                           "Actor": {"ID": "start"}}]
        witness.anchor_cid = "start"
        witness.anchor_index = 0
        witness.terminal_cid = None
        witness.terminal_index = None
        witness.final_cid = None
        witness.final_index = None
        witness.volume_destroy_expected = False
        witness.volume_destroy_seen = False
        witness.closed = False
        os.write(write_fd, (json.dumps(foreign) + "\n").encode())
        try:
            witness.poll({"writer"} if kind == "container" else "writer")
        except namespace["Unknown"] as exc:
            assert str(exc).startswith(("UNADMITTED_CONTAINER_CREATE",
                                        "COMPETING_RW_MOUNT_EVENT")), str(exc)
            return str(exc)
        raise AssertionError("REGRESSED_TIMESTAMP_FOREIGN_EVENT_ACCEPTED")
    finally:
        os.close(write_fd)
        os.close(read_fd)


container = {"Type": "container", "Action": "create", "timeNano": 99,
             "Actor": {"ID": "foreign-rw-grant"}}
volume = {"Type": "volume", "Action": "mount", "timeNano": 99,
          "Actor": {"ID": "selected", "Attributes": {
              "container": "foreign-rw-grant", "read/write": "true"}}}
print(json.dumps({"status": "REGRESSED_TIMESTAMPS_REFUSED",
                  "container": case("container", container),
                  "volume": case("volume", volume)}, sort_keys=True))
