#!/usr/bin/env python3
"""Execute one original candidate Work workflow in a fresh Python process."""

from __future__ import annotations

import atexit
import json
from pathlib import Path
import sys

from inventory import ROOT


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in {"engineering", "research"}:
        raise ValueError("usage: worker.py engineering|research OUTPUT")
    kind, output = sys.argv[1], Path(sys.argv[2]).resolve()
    # This formal Session carrier is an intermediate input to the original
    # WorkflowRun constructor, never a retained task-local report member.
    atexit.register(lambda: (output / "selected-actor-records.json").unlink(missing_ok=True))
    if kind == "engineering":
        example = ROOT / "implementation/lab-workflows/candidates/v1/examples/engineering"
        sys.path.insert(0, str(example))
        from test_engineering import INPUTS, INPUT_SHA
        from run_episode import execute_episode
        result = execute_episode(INPUTS, INPUT_SHA, output,
                                 {"result": "NOT-RUN", "tests": 0})
        summary = {"workflow": kind, "assessment": result["assessment"]["disposition"],
                   "event_count": len(result["events"]), "source_correction": result["receipt"]["posture"]}
    else:
        example = ROOT / "implementation/lab-workflows/candidates/v1/examples/research"
        sys.path.insert(0, str(example))
        from run_episode import execute_episode, byte_sha, EXAMPLE
        inputs = EXAMPLE / "packages/0007"
        result = execute_episode(inputs, byte_sha((inputs / "selection.json").read_bytes()), output)
        summary = {"workflow": kind, "assessment": result["assessment"]["disposition"],
                   "event_count": len(json.loads((output / "transitions.json").read_bytes())),
                   "replay_stdout_count": len(list(output.glob("sample-*.stdout")))}
    # Original candidate examples retain formal AgentSession records in this
    # intermediate file. The WorkflowRun already binds the selected actor and
    # the local output check does not require those private-formal bodies.
    (output / "selected-actor-records.json").unlink()
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
