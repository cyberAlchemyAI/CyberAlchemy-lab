#!/usr/bin/env python3
"""Repeat the disposable local Docker product and preserve unrelated state."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
LAUNCH = ROOT / "implementation/lab-runtime/local-host/run-local-product.sh"


def docker(*args: str) -> set[str]:
    run = subprocess.run(["docker", *args], text=True, capture_output=True, check=True)
    return set(filter(None, run.stdout.splitlines()))


def snapshot() -> dict[str, list[str]]:
    return {
        "containers": sorted(docker("ps", "-a", "--format", "{{.ID}}")),
        "volumes": sorted(docker("volume", "ls", "-q")),
        "local_images": sorted(x for x in docker("image", "ls", "--format", "{{.Repository}}:{{.Tag}}")
                               if x.startswith("cyberalchemy-lab-local-host:local-")),
        "build_contexts": sorted(str(x) for x in Path("/tmp").glob("cal-local-product-context-*")),
    }


def main() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    start = snapshot()
    runs = []
    try:
        for number in (1, 2):
            before = time.monotonic()
            with (HERE / f"run-{number:02d}.log").open("wb") as output:
                try:
                    result = subprocess.run([str(LAUNCH)], cwd=ROOT, stdout=output,
                                            stderr=subprocess.STDOUT, timeout=2400, check=False)
                    exit_code = result.returncode
                except subprocess.TimeoutExpired:
                    exit_code = "timeout"
            log = (HERE / f"run-{number:02d}.log").read_bytes()
            runs.append({"number": number, "exit": exit_code,
                         "elapsed_seconds": round(time.monotonic() - before, 3),
                         "log_sha256": hashlib.sha256(log).hexdigest(),
                         "chain_pass": b"Source" in log and b"Context" in log and b"PASS" in log,
                         "work_pass": b"CyberAlchemy Lab" in log and b"PASS" in log})
            if exit_code != 0 or not runs[-1]["chain_pass"] or not runs[-1]["work_pass"]:
                break
    finally:
        end = snapshot()
        preserved = {name: set(values).issubset(end[name]) for name, values in start.items()}
        no_new = {name: set(end[name]).issubset(values) for name, values in start.items()}
        passed = (len(runs) == 2 and all(r["exit"] == 0 and r["chain_pass"]
                                          and r["work_pass"] for r in runs)
                  and all(preserved.values()) and all(no_new.values()))
        receipt = {"schema": "lab-local-docker-repeat/v1", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                   "launcher": str(LAUNCH.relative_to(ROOT)),
                   "launcher_sha256": hashlib.sha256(LAUNCH.read_bytes()).hexdigest(),
                   "before": start, "runs": runs, "after": end,
                   "preexisting_preserved": preserved, "no_new_objects": no_new,
                   "status": "PASS" if passed else "FAIL"}
        (HERE / "RESULT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "runs": runs,
                      "preexisting_preserved": preserved, "no_new_objects": no_new}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
