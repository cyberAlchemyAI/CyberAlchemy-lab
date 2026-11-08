#!/usr/bin/env python3
"""Two attributed Docker setup/cleanup cycles with exact object identity."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LAUNCH = ROOT / "implementation/lab-runtime/local-host/run-local-product.sh"
CHAIN = "CyberAlchemy Lab — local Source → Reader → Mapper → Context fixture: PASS".encode()
WORK = "CyberAlchemy Lab — local Work journey: PASS".encode()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def command(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def snapshot() -> dict:
    volumes = command("docker", "volume", "ls", "-q").splitlines()
    volume_rows = []
    for name in sorted(volumes):
        row = json.loads(command("docker", "volume", "inspect", name, "--format", "{{json .}}"))
        volume_rows.append({key: row.get(key) for key in ("Name", "CreatedAt", "Driver", "Mountpoint", "Scope")})
    tags = sorted(x for x in command("docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}").splitlines()
                  if x.startswith("cyberalchemy-lab-local-host:local-"))
    images = [{"tag": tag, "id": command("docker", "image", "inspect", tag,
                                          "--format", "{{.Id}}").strip()} for tag in tags]
    contexts = []
    for path in sorted(Path("/tmp").glob("cal-local-product-context-*")):
        info = path.lstat()
        contexts.append({"path": str(path), "device": info.st_dev,
                         "inode": info.st_ino, "mode": info.st_mode})
    return {"containers": sorted(command("docker", "ps", "-a", "--no-trunc", "--format", "{{.ID}}").splitlines()),
            "volumes": volume_rows, "local_images": images, "build_contexts": contexts}


def exact_markers(raw: bytes) -> bool:
    return (raw.count(CHAIN) == 1 and raw.count(WORK) == 1
            and b"Exact retry: idempotent; fresh-process replay: PASS" in raw
            and b"Temporary state removed; external effects: 0" in raw
            and b"Disposable store and fixture key: removed" in raw)


def sentinel_observation(path: Path) -> dict | None:
    try:
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode):
            return None
        return {"path": str(path), "sha256": sha(path.read_bytes()),
                "size_bytes": info.st_size, "device": info.st_dev,
                "inode": info.st_ino, "mode": info.st_mode}
    except (OSError, ValueError):
        return None


def main() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    script_path = Path(__file__).resolve()
    script_sha = sha(script_path.read_bytes())
    sentinel = Path(tempfile.mkdtemp(prefix="cal-local-product-context-foreign-", dir="/tmp"))
    sentinel.chmod(0o700)
    sentinel_file = sentinel / "UNRELATED.bin"
    sentinel_file.write_bytes(os.urandom(32))
    sentinel_initial = sentinel_observation(sentinel_file)
    cycles = []
    try:
        for number in (1, 2):
            launcher_before = sha(LAUNCH.read_bytes())
            sentinel_before = sentinel_observation(sentinel_file)
            before = snapshot()
            started = datetime.now(timezone.utc).isoformat()
            monotonic = time.monotonic()
            log = HERE / f"v2-run-{number:02d}.log"
            with log.open("wb") as stream:
                try:
                    completed = subprocess.run([str(LAUNCH)], cwd=ROOT, stdout=stream,
                                               stderr=subprocess.STDOUT, timeout=2400,
                                               check=False)
                    exit_code = completed.returncode
                except subprocess.TimeoutExpired:
                    exit_code = "timeout"
            after = snapshot()
            sentinel_after = sentinel_observation(sentinel_file)
            launcher_after = sha(LAUNCH.read_bytes())
            raw = log.read_bytes()
            row = {"number": number, "started_at_utc": started,
                   "completed_at_utc": datetime.now(timezone.utc).isoformat(),
                   "monotonic_elapsed_seconds": round(time.monotonic() - monotonic, 3),
                   "exit": exit_code, "log_sha256": sha(raw),
                   "exact_journey_markers": exact_markers(raw),
                   "launcher_sha256_before": launcher_before,
                   "launcher_sha256_after": launcher_after,
                   "before": before, "after": after,
                   "same_objects_after_cycle": before == after,
                   "foreign_sentinel_before": sentinel_before,
                   "foreign_sentinel_after": sentinel_after,
                   "foreign_sentinel_unchanged": sentinel_initial is not None
                      and sentinel_before == sentinel_initial == sentinel_after}
            cycles.append(row)
            if (row["exit"] != 0 or not row["exact_journey_markers"]
                    or not row["same_objects_after_cycle"]
                    or not row["foreign_sentinel_unchanged"]
                    or launcher_before != launcher_after):
                break
        end_script_sha = sha(script_path.read_bytes())
        launcher_hashes = [value for row in cycles for value in
                           (row["launcher_sha256_before"], row["launcher_sha256_after"])]
        passed = (len(cycles) == 2 and all(row["exit"] == 0 and row["exact_journey_markers"]
                                             and row["same_objects_after_cycle"]
                                             and row["foreign_sentinel_unchanged"] for row in cycles)
                  and len(set(launcher_hashes)) == 1 and script_sha == end_script_sha)
        receipt = {"schema": "lab-local-docker-repeat/v2", "status": "PASS" if passed else "FAIL",
                   "script_sha256_at_entry": script_sha,
                   "script_sha256_at_exit": end_script_sha,
                   "launcher": str(LAUNCH.relative_to(ROOT)),
                   "foreign_sentinel": sentinel_initial,
                   "cycles": cycles}
        (HERE / "RESULT-v2.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
        print(json.dumps({"status": receipt["status"], "cycles": [
            {key: row[key] for key in ("number", "exit", "exact_journey_markers",
                                       "same_objects_after_cycle", "foreign_sentinel_unchanged")}
            for row in cycles]}, sort_keys=True))
        return 0 if passed else 1
    finally:
        sentinel_file.unlink(missing_ok=True)
        sentinel.rmdir()


if __name__ == "__main__":
    raise SystemExit(main())
