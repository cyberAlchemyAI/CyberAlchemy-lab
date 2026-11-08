"""Capture a bounded, no-replace receipt for the disposable WSL cgroup oracle."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid


SCRIPT = Path(__file__).absolute().with_name("contained_descendant_oracle_v2.py")
SYSTEMD_RUN = "/usr/bin/systemd-run"
PYTHON = "/usr/bin/python3"


def main():
    fault = len(sys.argv) == 3 and sys.argv[2] == "--fault-before-migration"
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and not fault):
        raise SystemExit("usage: run_contained_descendant_oracle_v2.py NEW-RECEIPT.json [--fault-before-migration]")
    target = Path(sys.argv[1]).absolute()
    if target.exists() or target.is_symlink():
        raise RuntimeError("receipt path already exists")
    if not target.parent.is_dir() or target.parent.is_symlink():
        raise RuntimeError("receipt parent must exist and be regular directory")
    if SCRIPT.is_symlink() or not SCRIPT.is_file():
        raise RuntimeError("oracle source must be a regular file")
    source = SCRIPT.read_bytes()
    unit = "cal-lcu0302-oracle-" + time.strftime("%Y%m%d", time.gmtime()) + "-" + uuid.uuid4().hex[:8] + ".scope"
    scope = Path("/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/app.slice") / unit
    if scope.exists():
        raise RuntimeError("scope name collision")
    argv = [SYSTEMD_RUN, "--user", "--scope", "--collect", "--quiet",
            "--property=Delegate=yes", "--property=RuntimeMaxSec=20s",
            "--unit=" + unit.removesuffix(".scope"), PYTHON, "-B", "-S", str(SCRIPT), unit]
    if fault:
        argv.append("--fault-before-migration")
    started = time.monotonic()
    try:
        run = subprocess.run(argv, capture_output=True, timeout=25, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("scope runner exceeded 25 seconds; inspect selected scope") from exc
    elapsed_ms = round((time.monotonic() - started) * 1000)
    if len(run.stdout) > 8192 or len(run.stderr) > 8192:
        raise RuntimeError("unbounded oracle output")
    if run.returncode != 0 or run.stderr or run.stdout.count(b"\n") != 1:
        raise RuntimeError("oracle failed; no PASS receipt written")
    observation = json.loads(run.stdout)
    if fault:
        if (observation.get("schema_version") != "lab-lcu0302-disposable-cgroup-fault/v2"
                or observation.get("result") != "EXPECTED_FAULT_CLEANUP_PASS"
                or observation.get("child_reaped_eof_exit_91") is not True
                or observation.get("attempt_removed") is not True
                or observation.get("broker_removed") is not True
                or elapsed_ms >= 5000):
            raise RuntimeError("fault cleanup failed or reached outer watchdog")
    elif (observation.get("schema_version") != "lab-lcu0302-disposable-cgroup-oracle/v2"
          or observation.get("result") != "PASS" or observation.get("claim") != "disposable user-scope cgroup mechanism only"
          or observation.get("before", {}).get("root") != str(scope)
          or observation.get("after", {}).get("attempt_removed") is not True
          or observation.get("after", {}).get("broker_removed") is not True):
        raise RuntimeError("oracle output did not satisfy expected contract")
    deadline = time.monotonic() + 5
    while scope.exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    if scope.exists():
        raise RuntimeError("delegated scope remains after run")
    if SCRIPT.read_bytes() != source:
        raise RuntimeError("oracle source changed during run")
    receipt = {
        "schema_version": "lab-lcu0302-disposable-cgroup-receipt/v2",
        "claim_ceiling": "Actual disposable same-UID user-scope cgroup mechanism only; not dedicated-worker custody, protected host admission, historical-family release, or LC-U03-02 acceptance.",
        "mode": "fault-before-migration" if fault else "normal",
        "elapsed_ms": elapsed_ms,
        "oracle_sha256": hashlib.sha256(source).hexdigest(),
        "oracle_size_bytes": len(source),
        "invocation": argv,
        "exit_code": run.returncode,
        "stderr_bytes": len(run.stderr),
        "stdout_sha256": hashlib.sha256(run.stdout).hexdigest(),
        "observation": observation,
        "post_scope_absent": True,
    }
    encoded = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(encoded)
            out.flush()
            os.fsync(out.fileno())
    finally:
        parent_fd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    print(json.dumps({"result": "EXPECTED_FAULT_CLEANUP_PASS" if fault else "PASS", "receipt": str(target), "sha256": hashlib.sha256(encoded).hexdigest(),
                      "post_scope_absent": True}, sort_keys=True))


if __name__ == "__main__":
    main()
