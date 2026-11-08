"""Run one local native phase with a real-clock, output-sanitized timing receipt."""

import argparse
import datetime as dt
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def stamp(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def utc(value):
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise ValueError("UTC_DEADLINE_REQUIRED")
    return parsed


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def selection(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("SELECTION_ORIGIN_REFUSED")
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict) or not isinstance(value.get("expires_at"), str):
        raise ValueError("SOURCE_PERIOD_MISSING")
    deadline = utc(value["expires_at"])
    return digest(raw), deadline


def reserve_receipt(path):
    if path.parent.is_symlink() or not path.parent.is_dir():
        raise ValueError("RECEIPT_PARENT_REFUSED")
    parent = path.parent.stat()
    if parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) & 0o022:
        raise ValueError("RECEIPT_PARENT_NOT_OWNED")
    return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)


def output_digest(stream):
    stream.seek(0)
    hashed = hashlib.sha256()
    count = 0
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        hashed.update(chunk)
        count += len(chunk)
    return hashed.hexdigest(), count


def record(phase, selected, receipt, command, *, deadlines=(), timeout_seconds=3600):
    if phase not in {"source", "cold", "reader", "mapped", "context", "session"}:
        raise ValueError("PHASE_REFUSED")
    if not command or not command[0]:
        raise ValueError("COMMAND_REQUIRED")
    if not 0 < timeout_seconds <= 3600:
        raise ValueError("TIMEOUT_REFUSED")
    source_hash, source_end = selection(selected)
    limits = {"source": source_end}
    for row in deadlines:
        name, divider, value = row.partition("=")
        if not divider or name not in {"reader", "context", "session"} or name in limits:
            raise ValueError("DEADLINE_REFUSED")
        limits[name] = utc(value)
    required = {"mapped": {"reader"}, "context": {"reader"},
                "session": {"reader", "context", "session"}}.get(phase, set())
    if not required.issubset(limits):
        raise ValueError("EPHEMERAL_LEASE_MISSING")
    before_utc = dt.datetime.now(dt.timezone.utc)
    if before_utc >= min(limits.values()):
        raise ValueError("LEASE_EXPIRED_BEFORE_PHASE")
    fd = reserve_receipt(receipt)
    try:
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            before_utc = dt.datetime.now(dt.timezone.utc)
            before_mono = time.monotonic_ns()
            failure = None
            remaining = (min(limits.values()) - before_utc).total_seconds()
            if remaining <= 0:
                failure = "expired_before_spawn"
                exit_code = 125
            else:
                try:
                    outcome = subprocess.run(command, stdout=stdout, stderr=stderr,
                                             check=False, timeout=min(timeout_seconds, remaining))
                    exit_code = outcome.returncode
                except subprocess.TimeoutExpired:
                    failure = "timeout"
                    exit_code = 124
                except OSError:
                    failure = "spawn_error"
                    exit_code = 127
            after_mono = time.monotonic_ns()
            after_utc = dt.datetime.now(dt.timezone.utc)
            stdout_hash, stdout_count = output_digest(stdout)
            stderr_hash, stderr_count = output_digest(stderr)
    except BaseException:
        os.close(fd)
        raise
    elapsed = (after_mono - before_mono) / 1_000_000_000
    wall_elapsed = (after_utc - before_utc).total_seconds()
    value = {
        "schema": "cal-local-native-phase-ledger/v1",
        "phase": phase,
        "selection_sha256": source_hash,
        "command_sha256": digest(json.dumps(command, separators=(",", ":")).encode()),
        "started_utc": stamp(before_utc),
        "ended_utc": stamp(after_utc),
        "monotonic_seconds": elapsed,
        "wall_seconds": wall_elapsed,
        "clock_divergence_seconds": wall_elapsed - elapsed,
        "deadlines": {name: stamp(value) for name, value in sorted(limits.items())},
        "strictest_deadline": stamp(min(limits.values())),
        "ended_before_strictest_deadline": after_utc < min(limits.values()),
        "exit_code": exit_code,
        "failure_kind": failure,
        "stdout_sha256": stdout_hash,
        "stdout_bytes": stdout_count,
        "stderr_sha256": stderr_hash,
        "stderr_bytes": stderr_count,
    }
    raw = json.dumps(value, sort_keys=True, indent=2).encode() + b"\n"
    with os.fdopen(fd, "wb") as stream:
        if stream.write(raw) != len(raw):
            raise OSError("RECEIPT_SHORT_WRITE")
        stream.flush()
        os.fsync(stream.fileno())
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase")
    parser.add_argument("selection", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--deadline", action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    result = record(args.phase, args.selection, args.receipt, command,
                    deadlines=args.deadline)
    print(json.dumps({"phase": args.phase, "exit_code": result["exit_code"],
                      "monotonic_seconds": result["monotonic_seconds"],
                      "ended_before_strictest_deadline": result["ended_before_strictest_deadline"]},
                     sort_keys=True))
    return result["exit_code"] if result["exit_code"] != 0 else (
        0 if result["ended_before_strictest_deadline"] else 1)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
