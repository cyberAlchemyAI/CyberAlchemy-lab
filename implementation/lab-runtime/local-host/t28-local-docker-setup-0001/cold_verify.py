#!/usr/bin/env python3
"""Recheck the exact retained two-run Docker receipt and journey outputs."""

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CHAIN = "CyberAlchemy Lab — local Source → Reader → Mapper → Context fixture: PASS".encode()
WORK = "CyberAlchemy Lab — local Work journey: PASS".encode()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    receipt = json.loads((HERE / "RESULT.json").read_bytes())
    need(receipt["schema"] == "lab-local-docker-repeat/v1", "wrong receipt schema")
    need(receipt["status"] == "PASS", "run receipt did not pass")
    need(len(receipt["runs"]) == 2, "expected two runs")
    need([row["number"] for row in receipt["runs"]] == [1, 2], "wrong run identities")
    need(len({row["log_sha256"] for row in receipt["runs"]}) == 2, "duplicate run log")
    launcher = ROOT / receipt["launcher"]
    need(hashlib.sha256(launcher.read_bytes()).hexdigest() == receipt["launcher_sha256"],
         "launcher changed")
    for row in receipt["runs"]:
        raw = (HERE / f"run-{row['number']:02d}.log").read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["log_sha256"], "run log changed")
        need(row["exit"] == 0, "run failed")
        need(raw.count(CHAIN) == 1, "chain marker missing or duplicated")
        need(raw.count(WORK) == 1, "Work marker missing or duplicated")
        need(b"Exact retry: idempotent; fresh-process replay: PASS" in raw,
             "fresh-process Work replay missing")
        need(b"Temporary state removed; external effects: 0" in raw,
             "chain cleanup missing")
        need(b"Disposable store and fixture key: removed" in raw,
             "Work cleanup missing")
    for name in ("containers", "volumes", "local_images", "build_contexts"):
        need(receipt["preexisting_preserved"][name] is True, f"preexisting {name} changed")
        need(receipt["no_new_objects"][name] is True, f"new {name} remained")
        need(receipt["before"][name] == receipt["after"][name], f"{name} inventory differs")
    print("PASS: two exact Docker journeys; preserved before/after object inventory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
