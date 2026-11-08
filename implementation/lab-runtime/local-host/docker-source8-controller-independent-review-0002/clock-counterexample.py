#!/usr/bin/python3.14 -I
"""Inert counterexample: event timestamp regression hides a foreign grant."""

import json
import os
from pathlib import Path


candidate = Path(__file__).resolve().parent.parent / "docker-source8-controller-candidate-0002"
namespace = {"__name__": "review_captured_control"}
exec(compile((candidate / "control.py").read_bytes(),
             "<review-captured-control>", "exec"), namespace)


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


read_fd, write_fd = os.pipe()
try:
    os.set_blocking(read_fd, False)
    witness = namespace["ContainerEvents"].__new__(namespace["ContainerEvents"])
    witness.since_ns = 100
    witness.process = Process(read_fd)
    witness.partial = b""
    witness.events = []
    witness.closed = False

    for cid, timestamp in (("foreign-rw-grant", 99), ("writer", 101)):
        item = {"Type": "container", "Action": "create", "timeNano": timestamp,
                "Actor": {"ID": cid}}
        os.write(write_fd, (json.dumps(item) + "\n").encode())
    witness.poll({"writer"})
    assert [item["Actor"]["ID"] for item in witness.events] == ["writer"]

    class Replay:
        stdout = (json.dumps({"Type": "container", "Action": "create",
                              "timeNano": 101, "Actor": {"ID": "writer"}}) + "\n")

    namespace["docker"] = lambda *args, **kwargs: Replay()
    namespace["time"].time_ns = lambda: 102
    result = witness.reconcile({"writer"}, "writer")
    assert result["created_cids"] == ["writer"]
    print(json.dumps({"status": "CLOCK_REGRESSION_COUNTEREXAMPLE",
                      "foreign_create_timeNano": 99, "since_ns": 100,
                      "created_cids_accepted": result["created_cids"]},
                     sort_keys=True))
finally:
    os.close(write_fd)
    os.close(read_fd)
