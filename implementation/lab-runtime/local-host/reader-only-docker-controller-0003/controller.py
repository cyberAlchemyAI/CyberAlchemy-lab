"""External, consumed-once Reader Docker controller candidate. Never import Reader here.

This candidate is effect-disabled; no Reader or Docker effect has been run. A missing or ambiguous
daemon observation is UNKNOWN and leaves the exclusive attempt consumed.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, ExitStack
import datetime as dt
import hashlib
import json
import os
import re
import selectors
import signal
import stat
import subprocess
import sys
import time
import uuid
from pathlib import Path

BASE = Path("/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/fresh-reader-docker-0004")
ATTEMPT = Path("/tmp/cal-reader-only-dev-20261020-0001-exact1")
ROOT = ATTEMPT / "root"
EVIDENCE = ATTEMPT / "evidence"
SOURCE = "product/lab/release-candidates/v1/interface/docker-source-20261020-0001"
READER = "product/lab/release-candidates/v1/interface/docker-reader-20261020-0001"
OUT = ATTEMPT / "reader-output"
IMAGE = "sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874"
DOCKER = "/usr/bin/docker"
DOCKER_SHA = "999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00"
PYTHON_SHA = "52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41"
FREEZE_SHA = "d50c94ebfe3d3777040ca353032a7943a263d2cfc82ecd26ac454e080ac5bdeb"
SELECTION_SHA = "073bc2938e30d6d108ed8b22205eed551d3879c1eab4379d0200c4e9f2d90b22"
READER_SHA = "4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251"
EFFECT_ENABLED = False
NAME = "cal-reader-only-20261020-0001-controller-0003"
MAX_STREAM = 4 * 1024 * 1024
MAX_CLI = 1024 * 1024
MAX_RECEIPT = 1024 * 1024
DEADLINE = 180.0
STOP_REQUESTED = False
HELD_EVIDENCE = None
HELD_OUTPUT = None
LOG_IDENTITIES = {}
HELD_MOUNTS = []


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def same_inode(a: os.stat_result, b: os.stat_result) -> bool:
    return (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)


def check_chain(chain: list[tuple[Path, int]]) -> None:
    for path, fd in chain:
        named = path.lstat()
        held = os.fstat(fd)
        require(stat.S_ISDIR(named.st_mode) and same_inode(named, held),
                "held directory attachment changed")


@contextmanager
def held_directory(path: Path):
    """Hold every absolute ancestor without following directory symlinks."""
    require(path.is_absolute() and ".." not in path.parts, "unsafe held directory path")
    chain = []
    primary = None
    try:
        fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        chain.append((Path("/"), fd))
        current = Path("/")
        for component in path.parts[1:]:
            fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                         dir_fd=chain[-1][1])
            current = current / component
            chain.append((current, fd))
        check_chain(chain)
        yield chain
        check_chain(chain)
    except BaseException as error:
        primary = error
        raise
    finally:
        failures = []
        for name, fd in reversed(chain):
            try:
                os.close(fd)
            except BaseException as error:
                failures.append((str(name), fd, error))
        if failures:
            if primary is not None:
                prior = getattr(primary, "secondary_close_errors", [])
                primary.secondary_close_errors = prior + failures
                primary.add_note("held directory close failure; custody is UNKNOWN")
            else:
                group = BaseExceptionGroup("held directory close failure; custody is UNKNOWN",
                                           [row[2] for row in failures])
                group.close_failures = failures
                raise group


def cleanup_owned_client(child, selector, primary):
    """Try every owned-client teardown step; never replace a primary failure."""
    failures = []

    def attempt(label, action):
        try:
            return action(), True
        except BaseException as error:
            failures.append((label, error))
            return None, False

    status, known = attempt("poll", child.poll)
    if not known or status is None:
        attempt("terminate", child.terminate)
        try:
            child.wait(timeout=3)
        except BaseException as error:
            failures.append(("wait_after_terminate", error))
            attempt("kill", child.kill)
            attempt("wait_after_kill", lambda: child.wait(timeout=3))
    if selector is not None:
        attempt("selector_close", selector.close)
    for label, stream in (("stdout_close", child.stdout), ("stderr_close", child.stderr)):
        if stream is not None:
            attempt(label, stream.close)
    if failures:
        if primary is not None:
            prior = getattr(primary, "secondary_cleanup_errors", [])
            primary.secondary_cleanup_errors = prior + failures
            primary.add_note("owned client cleanup failure; client state is UNKNOWN")
        else:
            group = BaseExceptionGroup("owned client cleanup failed; client state is UNKNOWN",
                                       [error for _, error in failures])
            group.cleanup_failures = failures
            return group
    return primary


def selected_chain(path: Path):
    if path == EVIDENCE and HELD_EVIDENCE is not None:
        return HELD_EVIDENCE
    if path == OUT and HELD_OUTPUT is not None:
        return HELD_OUTPUT
    return None


def exclusive(path: Path, raw: bytes, *, commit_check=None) -> tuple[int, int]:
    held = selected_chain(path.parent)
    if held is None:
        with held_directory(path.parent) as chain:
            return _exclusive_held(path.name, raw, chain, commit_check=commit_check)
    return _exclusive_held(path.name, raw, held, commit_check=commit_check)


def _exclusive_held(name: str, raw: bytes, chain: list[tuple[Path, int]],
                    *, commit_check=None) -> tuple[int, int]:
    check_chain(chain)
    parent_fd = chain[-1][1]
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                 0o600, dir_fd=parent_fd)
    with os.fdopen(fd, "wb") as stream:
        payload = commit_check() if commit_check is not None else raw
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
        if commit_check is not None:
            # STOP and expiry are sticky. A change during file or parent fsync
            # rewrites the same newly created leaf to UNKNOWN before return.
            for _ in range(3):
                next_payload = commit_check()
                if next_payload != payload:
                    stream.seek(0)
                    stream.truncate(0)
                    stream.write(next_payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                    payload = next_payload
                os.fsync(parent_fd)
            last = commit_check()
            if last != payload:
                stream.seek(0)
                stream.truncate(0)
                stream.write(last)
                stream.flush()
                os.fsync(stream.fileno())
                os.fsync(parent_fd)
                payload = last
            require(commit_check() == payload, "terminal commit changed after bounded checks")
        identity = os.fstat(stream.fileno())
    if commit_check is None:
        os.fsync(parent_fd)
    named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    require(stat.S_ISREG(named.st_mode) and same_inode(named, identity) and
            named.st_uid == os.getuid() and named.st_mode & 0o777 == 0o600,
            "exclusive evidence leaf attachment changed")
    check_chain(chain)
    return named.st_dev, named.st_ino


def bounded_read(path: Path, limit: int, *, expected: tuple[int, int] | None = None) -> bytes:
    held = selected_chain(path.parent)
    if held is None:
        with held_directory(path.parent) as chain:
            return _bounded_read_held(path.name, limit, chain, expected=expected)
    return _bounded_read_held(path.name, limit, held, expected=expected)


def _bounded_read_held(name: str, limit: int, chain: list[tuple[Path, int]],
                       *, expected: tuple[int, int] | None = None) -> bytes:
    check_chain(chain)
    parent_fd = chain[-1][1]
    fd = os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                 dir_fd=parent_fd)
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid() and
                before.st_size <= limit and
                (expected is None or (before.st_dev, before.st_ino) == expected),
                "bounded evidence leaf differs")
        raw = os.read(fd, limit + 1)
        after = os.fstat(fd)
        named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        require(len(raw) <= limit and before.st_size == len(raw) and
                same_inode(before, after) and same_inode(before, named) and
                stat.S_ISREG(named.st_mode) and
                (expected is None or (named.st_dev, named.st_ino) == expected),
                "bounded evidence leaf changed or overflowed")
        check_chain(chain)
        return raw
    finally:
        os.close(fd)


def tree_names(root: Path) -> tuple[set[str], set[str]]:
    files, directories = set(), set()
    for path in root.rglob("*"):
        mode = path.lstat().st_mode
        require(stat.S_ISREG(mode) or stat.S_ISDIR(mode),
                "nonregular staged tree entry")
        name = path.relative_to(root).as_posix()
        (files if stat.S_ISREG(mode) else directories).add(name)
    return files, directories


def expected_directories(files: set[str]) -> set[str]:
    return {parent.as_posix() for name in files for parent in Path(name).parents
            if parent.as_posix() != "."} | {SOURCE + "/receipts"}


def period_current(period: dict) -> None:
    now = dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(period["not_before"])
    end = dt.datetime.fromisoformat(period["expires_at"])
    require(start.tzinfo is not None and end.tzinfo is not None and
            start <= now < end and end - start == dt.timedelta(hours=24),
            "selected Source period is not current")


def frozen_inputs() -> dict:
    require(os.getuid() == 1000 and os.getgid() == 1000 and
            BASE.is_dir() and not BASE.is_symlink() and
            ROOT.is_dir() and not ROOT.is_symlink(),
            "selected Reader UID or mount root changed")
    require(Path(DOCKER).is_file() and not Path(DOCKER).is_symlink() and
            sha(Path(DOCKER).read_bytes()) == DOCKER_SHA and
            Path("/usr/bin/python3").is_file() and
            sha(Path("/usr/bin/python3").read_bytes()) == PYTHON_SHA and
            Path(sys.executable).resolve() == Path("/usr/bin/python3").resolve(),
            "selected host controller binaries changed")
    freeze_raw = (BASE / "freeze.json").read_bytes()
    require(sha(freeze_raw) == FREEZE_SHA, "Reader 0004 freeze changed")
    freeze = json.loads(freeze_raw)
    tool_prefix = BASE.relative_to(Path("/home/vlad_/projects/CyberAlchemy-lab")).as_posix() + "/"
    bound_tool_names = {row["path"][len(tool_prefix):] for row in freeze["file_bindings"]
                        if row["path"].startswith(tool_prefix)} | {"freeze.json"}
    actual_tool_files, actual_tool_dirs = tree_names(BASE)
    expected_tool_dirs = {parent.as_posix() for name in bound_tool_names
                          for parent in Path(name).parents if parent.as_posix() != "."}
    require(actual_tool_files == bound_tool_names and actual_tool_dirs == expected_tool_dirs,
            "Reader tool mount inventory changed")
    for row in freeze["file_bindings"]:
        path = Path("/home/vlad_/projects/CyberAlchemy-lab") / row["path"]
        require(path.is_file() and not path.is_symlink() and
                sha(path.read_bytes()) == row["sha256"], "Reader frozen member changed")
    selection_raw = (BASE / "selection.json").read_bytes()
    require(sha(selection_raw) == SELECTION_SHA, "Reader selection changed")
    selection = json.loads(selection_raw)
    require(selection["effect"] == "NOT_RUN" and
            selection["reader_manifest_binding"] ==
            {"path": READER + "/source-manifest.json", "sha256": READER_SHA},
            "Reader selection differs")
    source_raw = (ROOT / SOURCE / "source-manifest.json").read_bytes()
    package_raw = (ROOT / SOURCE / "packages/0001/manifest.json").read_bytes()
    reader_raw = (ROOT / READER / "source-manifest.json").read_bytes()
    require(sha(source_raw) == selection["source_manifest_binding"]["sha256"] and
            sha(package_raw) == selection["source_package_binding"]["sha256"] and
            sha(reader_raw) == READER_SHA, "selected Source/Reader manifest changed")
    source, package, reader = map(json.loads, (source_raw, package_raw, reader_raw))
    require(package["source_manifest_binding"] == selection["source_manifest_binding"] and
            reader["producer_source_binding"] == selection["source_manifest_binding"] and
            reader["producer_package_binding"] == selection["source_package_binding"],
            "selected producer/Reader join changed")
    period_raw = (ROOT / SOURCE / "packages/0001/period.json").read_bytes()
    period = json.loads(period_raw)
    period_current(period)
    require(period["expires_at"] == selection["episode_expires_at"] and
            package["period_binding"]["sha256"] == sha(period_raw),
            "selected participation period changed")
    expected_raw = (ROOT / SOURCE / "packages/0001/expected-replay.json").read_bytes()
    expected = json.loads(expected_raw)
    require(expected["expected_head"] == selection["expected_head"] and
            package["expected_replay_binding"]["sha256"] == sha(expected_raw),
            "selected signed cut changed")
    rows = reader["files"] + package["files"] + [
        {"path": READER + "/source-manifest.json", "sha256": READER_SHA},
        {"path": SOURCE + "/packages/0001/manifest.json",
         "sha256": selection["source_package_binding"]["sha256"]}]
    names = [row["path"] for row in rows]
    require(len(names) == 986 and len(set(names)) == 986 and not ROOT.is_symlink(),
            "Reader stage selection is not exact 986 files")
    actual_files, actual_dirs = tree_names(ROOT)
    require(actual_files == set(names) and actual_dirs == expected_directories(set(names)),
            "Reader stage inventory changed")
    for row in rows:
        path = ROOT / row["path"]
        require(path.is_file() and not path.is_symlink() and
                sha(path.read_bytes()) == row["sha256"], "Reader stage selected byte changed")
    return {"selection": selection, "rows": rows,
            "reader_manifest_sha256": READER_SHA,
            "source_package_manifest_sha256": selection["source_package_binding"]["sha256"]}


def output_state(*, fresh: bool) -> dict:
    chain = selected_chain(OUT)
    if chain is None:
        with held_directory(OUT) as local:
            return _output_state_held(local, fresh=fresh)
    return _output_state_held(chain, fresh=fresh)


def _output_state_held(chain: list[tuple[Path, int]], *, fresh: bool) -> dict:
    check_chain(chain)
    st = os.fstat(chain[-1][1])
    require(st.st_uid == os.getuid() and st.st_gid == os.getgid() and
            st.st_mode & 0o777 == 0o700, "Reader output owner or mode changed")
    if fresh:
        require(not os.listdir(chain[-1][1]), "Reader output root not fresh")
    return {"dev": st.st_dev, "ino": st.st_ino}


def docker_create_argv(label: str) -> list[str]:
    return [DOCKER, "create", "--name", NAME, "--label", "cal.reader.attempt=" + label,
            "--network", "none", "--read-only", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true", "--pids-limit", "64",
            "--memory", "1g", "--cpus", "1", "--user", "1000:1000",
            "--mount", f"type=bind,src={ROOT},dst=/attempt/root,readonly",
            "--mount", f"type=bind,src={OUT},dst=/attempt/reader-output",
            "--mount", f"type=bind,src={BASE},dst=/tool,readonly",
            "--tmpfs", "/attempt/tmp:rw,nosuid,nodev,size=512m,mode=1777",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m,mode=1777",
            IMAGE, "python", "-B", "/tool/reader_once.py", "--execute-reviewed-one-shot"]


def cli(argv: list[str], *, seconds: float = 12.0) -> subprocess.CompletedProcess:
    """Stream and cap every Docker CLI response, including inspect diagnostics."""
    child = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.DEVNULL)
    selector = None
    primary = None
    outputs = {child.stdout: bytearray(), child.stderr: bytearray()}
    code = None
    deadline = time.monotonic() + seconds
    try:
        selector = selectors.DefaultSelector()
        for stream in outputs:
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ)
        while selector.get_map() and time.monotonic() < deadline:
            for key, _ in selector.select(timeout=min(0.25, max(0, deadline-time.monotonic()))):
                data = os.read(key.fileobj.fileno(), 65536)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                require(len(outputs[key.fileobj]) + len(data) <= MAX_CLI,
                        "Docker CLI stream exceeds bound")
                outputs[key.fileobj].extend(data)
        require(not selector.get_map(), "Docker CLI stream deadline exceeded")
        code = child.wait(timeout=max(0, deadline-time.monotonic()))
    except BaseException as error:
        primary = error
    finally:
        primary = cleanup_owned_client(child, selector, primary)
    if primary is not None:
        if isinstance(primary, ValueError) and "deadline" in str(primary):
            timeout = subprocess.TimeoutExpired(argv, seconds)
            if hasattr(primary, "secondary_cleanup_errors"):
                timeout.secondary_cleanup_errors = primary.secondary_cleanup_errors
            raise timeout from primary
        raise primary
    return subprocess.CompletedProcess(argv, code, bytes(outputs[child.stdout]),
                                    bytes(outputs[child.stderr]))


def inspected(name: str) -> dict | None:
    proc = cli([DOCKER, "inspect", name])
    if proc.returncode != 0:
        # The pinned Docker CLI emits [] plus a lowercase error line for an
        # absent object. Accept only that full selected-name diagnostic (or
        # its case/whitespace variant), never a transport error containing the
        # same phrase as a substring. Callers repeat the absence observation.
        diagnostic = proc.stderr.strip(b" \t\r\n")
        # Case-insensitive matching applies only to Docker's human diagnostic
        # prefix. The selected object-name bytes are compared exactly.
        exact = (rb"(?i:error[ \t]*:[ \t]*no[ \t]+such[ \t]+"
                 rb"(?:object|container)[ \t]*:)[ \t]*" + re.escape(name.encode("ascii")))
        require(proc.returncode == 1 and proc.stdout.strip() in (b"", b"[]") and
                re.fullmatch(exact, diagnostic) is not None,
                "Docker inspect failure is ambiguous")
        return None
    value = json.loads(proc.stdout)
    require(type(value) is list and len(value) == 1, "Docker inspect shape differs")
    return value[0]


def owned(info: dict, label: str, cid: str | None) -> str:
    actual = info["Id"]
    require(type(actual) is str and len(actual) == 64 and
            info["Name"] == "/" + NAME and info["Config"]["Image"] == IMAGE and
            info["Image"] == IMAGE and
            info["Config"]["Labels"].get("cal.reader.attempt") == label and
            (cid is None or actual == cid), "selected Docker identity differs")
    return actual


@contextmanager
def open_log_append(path: Path):
    held = selected_chain(path.parent)
    if held is None:
        with held_directory(path.parent) as chain:
            with _open_log_held(path.name, chain) as stream:
                yield stream
    else:
        with _open_log_held(path.name, held) as stream:
            yield stream


@contextmanager
def _open_log_held(name: str, chain: list[tuple[Path, int]]):
    check_chain(chain)
    parent_fd = chain[-1][1]
    fd = os.open(name, os.O_WRONLY | os.O_APPEND | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC,
                 dir_fd=parent_fd)
    try:
        held = os.fstat(fd)
        named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        require(stat.S_ISREG(held.st_mode) and same_inode(held, named) and
                held.st_uid == os.getuid() and held.st_mode & 0o777 == 0o600 and
                (name not in LOG_IDENTITIES or
                 (held.st_dev, held.st_ino) == LOG_IDENTITIES[name]),
                "selected log leaf attachment changed")
        with os.fdopen(fd, "ab", buffering=0, closefd=False) as stream:
            yield stream
            stream.flush()
            os.fsync(fd)
        named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        require(same_inode(held, named), "selected log leaf changed during capture")
        check_chain(chain)
    finally:
        os.close(fd)


def capture_start(cid: str, stdout_path: Path, stderr_path: Path) -> tuple[int | None, bool]:
    child = subprocess.Popen([DOCKER, "start", "-a", cid], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    selector = None
    primary = None
    code = None
    overflow = False
    timed_out = False
    try:
        limits = {child.stdout: 0, child.stderr: 0}
        selector = selectors.DefaultSelector()
        for stream in limits:
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ)
        deadline = time.monotonic() + DEADLINE
        with open_log_append(stdout_path) as out, open_log_append(stderr_path) as err:
            targets = {child.stdout: out, child.stderr: err}
            while selector.get_map() and time.monotonic() < deadline and not STOP_REQUESTED:
                for key, _ in selector.select(timeout=min(0.25, max(0, deadline - time.monotonic()))):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    used = limits[key.fileobj]
                    take = max(0, min(len(data), MAX_STREAM - used))
                    if take:
                        targets[key.fileobj].write(data[:take])
                    limits[key.fileobj] = used + take
                    overflow |= take < len(data)
            timed_out = STOP_REQUESTED or (time.monotonic() >= deadline and
                                           (selector.get_map() or child.poll() is None))
        if not timed_out and child.poll() is not None:
            code = child.wait(timeout=3)
        else:
            timed_out = True
    except BaseException as error:
        primary = error
    finally:
        primary = cleanup_owned_client(child, selector, primary)
    if primary is not None:
        raise primary
    return code, timed_out or overflow


def output_inventory() -> dict:
    chain = selected_chain(OUT)
    if chain is None:
        with held_directory(OUT) as local:
            return _output_inventory_held(local)
    return _output_inventory_held(chain)


def _output_inventory_held(chain: list[tuple[Path, int]]) -> dict:
    check_chain(chain)
    entries = os.listdir(chain[-1][1])
    require(entries == ["receipt.json"],
            "Reader output must be one regular receipt")
    raw = bounded_read(OUT / "receipt.json", MAX_RECEIPT)
    return {"files": [{"path": "receipt.json", "sha256": sha(raw), "size": len(raw)}],
            "total_bytes": len(raw)}


def settle(label: str, cid: str | None, *, receipt_path: Path | None = None) -> dict:
    """Only mutate a container with the exact selected name/image/nonce/CID."""
    receipt_path = receipt_path or EVIDENCE / "reader-pre-removal.json"
    info = inspected(NAME)
    if info is None:
        require(inspected(NAME) is None, "container absence not repeated")
        return {"absent": True, "daemon_exit": None, "cleanup": "already_absent",
                "forced_cleanup": True}
    actual = owned(info, label, cid)
    def receipt(value: dict) -> dict:
        return {"id": value["Id"], "name": value["Name"],
                "image_id": value["Image"],
                "attempt_label": value["Config"]["Labels"]["cal.reader.attempt"],
                "status": value["State"].get("Status"),
                "running": value["State"]["Running"],
                "exit_code": value["State"].get("ExitCode")}
    daemon_exit = None
    forced = False
    if info["State"].get("Status") == "created":
        # Docker wait on an unstarted container can block. It is consumed but
        # has no Reader operation exit to claim.
        exclusive(receipt_path, json_bytes({"schema_version": "lab-reader-docker-pre-removal/v1",
                                            "container": receipt(info), "daemon_wait_exit": None,
                                            "reason": "created_unstarted"}))
        removed = cli([DOCKER, "rm", actual], seconds=8)
        require(removed.returncode == 0 and inspected(NAME) is None and inspected(NAME) is None,
                "never-started owned container removal unconfirmed")
        return {"absent": True, "daemon_exit": None, "cleanup": "removed_unstarted",
                "forced_cleanup": True, "pre_removal_inspect": receipt(info)}
    if info["State"]["Running"]:
        forced = True
        try:
            cli([DOCKER, "stop", "--time", "5", actual], seconds=8)
        except (OSError, subprocess.TimeoutExpired):
            pass
        info = inspected(NAME)
        require(info is not None and owned(info, label, actual) == actual,
                "owned container identity lost after stop")
        if info["State"]["Running"]:
            try:
                cli([DOCKER, "kill", actual], seconds=8)
            except (OSError, subprocess.TimeoutExpired):
                pass
    info = inspected(NAME)
    require(info is not None and owned(info, label, actual) == actual and
            info["State"]["Running"] is False, "owned container still running")
    pre_removal = receipt(info)
    try:
        waited = cli([DOCKER, "wait", actual], seconds=8)
        if waited.returncode == 0 and waited.stdout.strip().isdigit():
            daemon_exit = int(waited.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        pass
    exclusive(receipt_path, json_bytes({"schema_version": "lab-reader-docker-pre-removal/v1",
                                        "container": pre_removal,
                                        "daemon_wait_exit": daemon_exit,
                                        "reason": "settled_after_start"}))
    removed = cli([DOCKER, "rm", actual], seconds=8)
    require(removed.returncode == 0, "owned container removal unconfirmed")
    require(inspected(NAME) is None and inspected(NAME) is None,
            "owned container post-close absence unconfirmed")
    return {"absent": True, "daemon_exit": daemon_exit, "cleanup": "removed",
            "forced_cleanup": forced, "pre_removal_inspect": pre_removal,
            "daemon_exit_consistent": daemon_exit is not None and
                                      pre_removal["exit_code"] == daemon_exit}


def run() -> dict:
    require(EFFECT_ENABLED, "Reader controller effect disabled pending independent review and release")
    global HELD_EVIDENCE, HELD_OUTPUT, HELD_MOUNTS, LOG_IDENTITIES
    with ExitStack() as stack:
        HELD_EVIDENCE = stack.enter_context(held_directory(EVIDENCE))
        HELD_OUTPUT = stack.enter_context(held_directory(OUT))
        HELD_MOUNTS = [stack.enter_context(held_directory(ROOT)),
                       stack.enter_context(held_directory(BASE))]
        try:
            return _run_held()
        finally:
            HELD_EVIDENCE = None
            HELD_OUTPUT = None
            HELD_MOUNTS = []
            LOG_IDENTITIES = {}


def _run_held() -> dict:
    require(EFFECT_ENABLED, "Reader controller effect disabled pending independent review and release")
    require(ATTEMPT.is_dir() and not ATTEMPT.is_symlink() and
            ATTEMPT.stat().st_uid == os.getuid() and
            ATTEMPT.stat().st_gid == os.getgid() and
            ATTEMPT.stat().st_mode & 0o777 == 0o700,
            "selected Reader attempt root differs")
    require(EVIDENCE.is_dir() and not EVIDENCE.is_symlink() and
            EVIDENCE.stat().st_mode & 0o777 == 0o700, "Reader evidence root differs")
    plan = frozen_inputs()
    before = output_state(fresh=True)
    attachments = {"root": (ROOT.stat().st_dev, ROOT.stat().st_ino),
                   "tool": (BASE.stat().st_dev, BASE.stat().st_ino)}
    require(inspected(NAME) is None and inspected(NAME) is None,
            "selected Reader container exists or daemon unavailable")
    require(not STOP_REQUESTED, "controller interrupted before launch")
    label = uuid.uuid4().hex
    marker = {"schema_version": "lab-reader-only-consumed/v1", "container_name": NAME,
              "attempt_label": label, "image_id": IMAGE,
              "reader_manifest_sha256": READER_SHA, "state": "CONSUMED_NO_RETRY"}
    exclusive(EVIDENCE / "reader-attempt-consumed.json", json_bytes(marker))
    stdout_path = EVIDENCE / "reader-once.stdout"
    stderr_path = EVIDENCE / "reader-once.stderr"
    terminal_path = EVIDENCE / "reader-once.terminal.json"
    result = {"schema_version": "lab-reader-only-docker-terminal/v1",
              "attempt_label": label, "container_name": NAME,
              "operation": "UNKNOWN", "cleanup": "UNKNOWN", "overall": "UNKNOWN",
              "reader_effect": "MAY_HAVE_RUN", "no_retry": True}
    cid = None
    try:
        require(not STOP_REQUESTED, "controller interrupted before Docker create")
        LOG_IDENTITIES[stdout_path.name] = exclusive(stdout_path, b"")
        LOG_IDENTITIES[stderr_path.name] = exclusive(stderr_path, b"")
        require(not terminal_path.exists(), "Reader terminal path already exists")
        for chain in HELD_MOUNTS:
            check_chain(chain)
        created = cli(docker_create_argv(label), seconds=20)
        for chain in HELD_MOUNTS:
            check_chain(chain)
        require(created.returncode == 0 and len(created.stdout.strip()) == 64 and
                all(ch in b"0123456789abcdef" for ch in created.stdout.strip()),
                "Docker create response unavailable")
        cid = created.stdout.strip().decode()
        info = inspected(NAME)
        require(info is not None and owned(info, label, cid) == cid,
                "created Reader Docker identity unconfirmed")
        exclusive(EVIDENCE / "reader-container-id.json",
                  json_bytes({"container_id": cid, "name": NAME,
                              "attempt_label": label, "image_id": IMAGE}))
        require(not STOP_REQUESTED, "controller interrupted before Docker start")
        child_exit, timeout_or_overflow = capture_start(cid, stdout_path, stderr_path)
        result.update(container_id=cid, client_exit=child_exit,
                      stream_or_deadline_failure=timeout_or_overflow)
    except BaseException as error:
        result["controller_error_class"] = type(error).__name__
        result["controller_error"] = str(error)[:240]
    try:
        result.update(settle(label, cid))
    except BaseException as error:
        result["cleanup_error_class"] = type(error).__name__
        result["cleanup_error"] = str(error)[:240]
    try:
        require(before == output_state(fresh=False), "Reader output attachment changed")
        require(attachments == {"root": (ROOT.stat().st_dev, ROOT.stat().st_ino),
                                "tool": (BASE.stat().st_dev, BASE.stat().st_ino)},
                "Reader input or tool attachment changed")
        post = frozen_inputs()
        require(post == plan, "Reader selected postclose inputs changed")
        result["output_inventory"] = output_inventory()
        result["postclose_inputs"] = "PASS"
        result["output_attachment"] = "PASS"
    except BaseException as error:
        result["postclose_error_class"] = type(error).__name__
    stdout_raw = stderr_raw = None
    try:
        stdout_raw = bounded_read(stdout_path, MAX_STREAM,
                                  expected=LOG_IDENTITIES.get(stdout_path.name))
        stderr_raw = bounded_read(stderr_path, MAX_STREAM,
                                  expected=LOG_IDENTITIES.get(stderr_path.name))
        result["stdout_sha256"] = sha(stdout_raw)
        result["stderr_sha256"] = sha(stderr_raw)
    except BaseException as error:
        result["log_error_class"] = type(error).__name__
        result["stdout_sha256"] = None
        result["stderr_sha256"] = None
    if (stdout_raw is not None and stderr_raw is not None and
            not STOP_REQUESTED and result.get("absent") is True and
            result.get("forced_cleanup") is False and
            result.get("daemon_exit_consistent") is True and
            result.get("daemon_exit") == 0 and result.get("client_exit") == 0 and
            result.get("stream_or_deadline_failure") is False and
            result.get("postclose_inputs") == "PASS" and
            result.get("output_attachment") == "PASS"):
        try:
            lines = stdout_raw.splitlines()
            require(len(lines) == 1 and not stderr_raw,
                    "single clean Reader result required")
            reported = json.loads(lines[0])
            require(reported == {"result": "PASS_READER_PRIVATE",
                                 "receipt_sha256": result["output_inventory"]["files"][0]["sha256"],
                                 "reader_manifest_sha256": READER_SHA,
                                 "source_package_manifest_sha256": plan["source_package_manifest_sha256"]},
                    "Reader result and receipt differ")
            receipt = json.loads(bounded_read(OUT / "receipt.json", MAX_RECEIPT))
            require(receipt["schema_version"] == "lab-disposable-reader-receipt/v1-private" and
                    receipt["reader_manifest_sha256"] == READER_SHA and
                    receipt["source_package_manifest_sha256"] == plan["source_package_manifest_sha256"] and
                    receipt["expected_head"] == plan["selection"]["expected_head"] and
                    receipt["authority_effect"] == "none" and
                    receipt["actual_owner_outcome"] is None,
                    "selected Reader receipt differs")
            period_current(json.loads(bounded_read(ROOT / SOURCE / "packages/0001/period.json", 4096)))
            result.update(operation="PASS", cleanup="PASS", overall="PASS",
                          reader_effect="DISPOSABLE_READER_DIAGNOSTIC",
                          receipt_sha256=reported["receipt_sha256"],
                          claim_ceiling="Disposable exact-pinned Source cold-open and fresh Reader diagnostic only; no protected Source8 qualification.")
        except BaseException as error:
            result["result_error_class"] = type(error).__name__
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
    try:
        def terminal_bytes() -> bytes:
            interrupted = STOP_REQUESTED or bool({signal.SIGINT, signal.SIGTERM} & signal.sigpending())
            expired = False
            if result.get("overall") == "PASS":
                try:
                    period_current(json.loads(bounded_read(
                        ROOT / SOURCE / "packages/0001/period.json", 4096)))
                except BaseException:
                    expired = True
            if interrupted or expired:
                result.update(operation="UNKNOWN", overall="UNKNOWN",
                              reader_effect="MAY_HAVE_RUN")
                if interrupted:
                    result["interrupted"] = True
                if expired:
                    result["period_expired_at_commit"] = True
            return json_bytes(result)
        exclusive(terminal_path, terminal_bytes(), commit_check=terminal_bytes)
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
    return result


def recover_consumed() -> dict:
    """Cleanup-only path after controller crash; never starts Reader again."""
    require(EFFECT_ENABLED, "Reader controller effect disabled pending independent review and release")
    global HELD_EVIDENCE
    with held_directory(EVIDENCE) as chain:
        HELD_EVIDENCE = chain
        try:
            return _recover_held()
        finally:
            HELD_EVIDENCE = None


def _recover_held() -> dict:
    marker = json.loads(bounded_read(EVIDENCE / "reader-attempt-consumed.json", 4096))
    require(marker["state"] == "CONSUMED_NO_RETRY" and
            marker["container_name"] == NAME and marker["image_id"] == IMAGE and
            marker["reader_manifest_sha256"] == READER_SHA,
            "selected consumed marker differs")
    cid_path = EVIDENCE / "reader-container-id.json"
    cid = None
    if cid_path.exists():
        identity = json.loads(bounded_read(cid_path, 4096))
        require(identity["name"] == NAME and identity["image_id"] == IMAGE and
                identity["attempt_label"] == marker["attempt_label"],
                "durable selected CID record differs")
        cid = identity["container_id"]
    terminal = EVIDENCE / "reader-once.terminal.json"
    if terminal.exists():
        require(json.loads(bounded_read(terminal, 1024 * 1024))["overall"] != "PASS",
                "successful consumed attempt needs no recovery")
    recovery = {"schema_version": "lab-reader-only-docker-recovery/v1",
                "operation": "UNKNOWN", "no_retry": True,
                "attempt_label": marker["attempt_label"], "container_name": NAME}
    prior_path = EVIDENCE / "reader-pre-removal.json"
    if prior_path.exists():
        prior_raw = bounded_read(prior_path, 1024 * 1024)
        prior = json.loads(prior_raw)
        container = prior["container"]
        require(prior["schema_version"] == "lab-reader-docker-pre-removal/v1" and
                container["name"] == "/" + NAME and container["image_id"] == IMAGE and
                container["attempt_label"] == marker["attempt_label"] and
                (cid is None or container["id"] == cid),
                "durable prior pre-removal receipt identity differs")
        recovery["prior_pre_removal_sha256"] = sha(prior_raw)
        recovery["prior_daemon_wait_exit"] = prior["daemon_wait_exit"]
    try:
        recovery.update(settle(marker["attempt_label"], cid,
                               receipt_path=EVIDENCE / "reader-recovery-pre-removal-0001.json"))
    except Exception as error:
        recovery["cleanup_error_class"] = type(error).__name__
        recovery["cleanup_error"] = str(error)[:240]
    exclusive(EVIDENCE / "reader-recovery-0001.json", json_bytes(recovery))
    return recovery


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--execute-reviewed-one-shot", action="store_true")
    group.add_argument("--recover-consumed-cleanup", action="store_true")
    args = parser.parse_args()
    def request_stop(_signum, _frame):
        global STOP_REQUESTED
        STOP_REQUESTED = True
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    require(EFFECT_ENABLED, "Reader controller effect disabled pending independent review and release")
    terminal = run() if args.execute_reviewed_one_shot else recover_consumed()
    print(json.dumps(terminal, sort_keys=True))
    sys.exit(0 if terminal.get("overall") == "PASS" or
             (args.recover_consumed_cleanup and terminal.get("absent")) else 2)
