"""External, consumed-once local Reader Docker release. Never import Reader here.

This disjoint candidate is effect-enabled only for its exact one-shot command after independent
review. An ambiguous daemon observation is UNKNOWN and leaves the exclusive attempt consumed.
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

BASE = Path("/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/reader-only-unified-0006")
STAGE = Path("/tmp/cal-reader-stage-20261020-0001-0008")
ATTEMPT = Path("/tmp/cal-reader-only-dev-20261020-0001-unified6")
ROOT = STAGE / "root"
EVIDENCE = ATTEMPT / "evidence"
SOURCE = "product/lab/release-candidates/v1/interface/docker-source-20261020-0001"
READER = "product/lab/release-candidates/v1/interface/docker-reader-20261020-0001"
OUT = ATTEMPT / "reader-output"
IMAGE = "sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874"
DOCKER = "/usr/bin/docker"
DOCKER_SHA = "999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00"
PYTHON_SHA = "52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41"
ENTRYPOINT_SHA = "84e7ae107b44ac383f1776c8d949a6f91316a7609c49fd649297fceb5bc8c0c3"
SELECTION_SHA = "073bc2938e30d6d108ed8b22205eed551d3879c1eab4379d0200c4e9f2d90b22"
READER_SHA = "4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251"
EFFECT_ENABLED = True
NAME = "cal-reader-only-20261020-0001-unified-0006"
STAGE_FREEZE_SHA = "7baa002724d031a1225e73518dee282caf3f9d26a914bdc306788c3873917606"
STAGE_TERMINAL_SHA = "bd45626107f1754b9d108e138fdf3a85dc3b4ed0ffa00cfb1fc304f7974093cd"
STAGE_CONSUMED_SHA = "b9f58618fd1a994e4127c6a50991bbc88bc7b2e40d7cedf96c17cd4155623c7e"
STAGE_REVIEW_ONE_SHA = "9caf8e442bf9e4c82680ebf343710a7304f36f55e950e4461aaf845697ffa417"
STAGE_REVIEW_TWO_SHA = "244e75313d32488848e6452ebb9f7f6c7948cc0fd9e1b20fdc47cd31e9e41e15"
ENTRY_FREEZE_SHA = "eef4d78b91748aa8df27d09157a7962e2920167cdca1700da73e28d726a3029e"
ENTRY_REVIEW_SHA = "b8b535b6c07eb5e0717989d25c495c2c9d76e368a1c1e632b32b4424c6cc47d8"
MOUNT_AUDIT_SHA = "e6b2670afb53a815436f54b5fe9c13d0110ee3938092c40da76de05421231d16"
CONTROLLER_FREEZE_SHA = "cb14a96bcd17b833cc5139af3aa5fb0e8bbe9ae9c33e8129603f0eb9ac80806d"
READER_ROLE_FREEZE_SHA = "28d97810e1c3ac77aceee504a49a4e3e0c57fe08c520053b1c46b62c61e326a1"
UNIFIED_0001_FREEZE_SHA = "8b88e8cb60ce118d6822e929de57430a434a5cf1555e2e5df5da8e0e6e74d1b5"
UNIFIED_0001_REVIEW_SHA = "ae3c467890bcfd40b827fd66e414370e34017634c4d8a4f774141cc3ea488999"
UNIFIED_0001_REVIEW_TWO_SHA = "29e3a362729eae63eaae4cd38ffeb2551be164983314b0e08256004e7d7bc809"
UNIFIED_0002_FREEZE_SHA = "807249fa418e2990fe31bdd693fbe32660089d26f3b30f445670f34483284f4b"
UNIFIED_0002_REVIEW_ONE_SHA = "229c2413050e0328346b3d40b514938d4c79b710aaec86f5ef0102d1777fb199"
UNIFIED_0002_REVIEW_TWO_SHA = "cd3e55a537dd8fe1536a9f7ff23a0a08868c0bf6d2007c48f5462febff28496c"
STAGE_PLAN_SHA = "82ddcf898953881d49cfb1b99ba0b91f4f9c7393cfde5ae3bb9549b5a769e524"
MAX_STREAM = 4 * 1024 * 1024
MAX_CLI = 1024 * 1024
MAX_RECEIPT = 1024 * 1024
MAX_STAGE_FILE = 512 * 1024 * 1024
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


def verify_stage_metadata(root: Path, plan: dict[str, dict],
                          expected_dirs: set[str]) -> None:
    """Recheck stage 0008's selected owner, modes, links, bytes and attachment."""
    with held_directory(root) as root_chain:
        info = os.fstat(root_chain[-1][1])
        require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
                info.st_gid == os.getgid() and stat.S_IMODE(info.st_mode) == 0o755,
                "stage root owner or mode changed")
        files, directories = tree_names(root)
        require(files == set(plan) and directories == expected_dirs,
                "stage inventory changed")
        for name, row in sorted(plan.items()):
            path = root / name
            mode = int(row["target_mode"], 8)
            require(mode in (0o444, 0o600), "stage selected mode differs")
            with held_directory(path.parent) as chain:
                parent = chain[-1][1]
                before = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
                require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and
                        before.st_uid == os.getuid() and before.st_gid == os.getgid() and
                        stat.S_IMODE(before.st_mode) == mode and
                        before.st_size <= MAX_STAGE_FILE,
                        "stage file owner, mode or link changed: " + name)
                fd = os.open(path.name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW |
                             os.O_CLOEXEC, dir_fd=parent)
                try:
                    held = os.fstat(fd)
                    identity = lambda st: (st.st_dev, st.st_ino, st.st_mode,
                                           st.st_uid, st.st_gid, st.st_nlink,
                                           st.st_size, st.st_mtime_ns, st.st_ctime_ns)
                    require(identity(before) == identity(held),
                            "stage leaf changed before read: " + name)
                    digest = hashlib.sha256()
                    count = 0
                    while True:
                        chunk = os.read(fd, 1024 * 1024)
                        if not chunk:
                            break
                        count += len(chunk)
                        require(count <= MAX_STAGE_FILE, "stage file exceeds bound")
                        digest.update(chunk)
                    named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
                    require(count == before.st_size and digest.hexdigest() == row["sha256"] and
                            identity(before) == identity(os.fstat(fd)) == identity(named),
                            "stage file bytes or attachment changed: " + name)
                finally:
                    os.close(fd)
        for name in sorted(expected_dirs):
            private = name == SOURCE + "/receipts" or name.startswith(SOURCE + "/packages")
            with held_directory(root / name) as chain:
                directory = os.fstat(chain[-1][1])
                require(stat.S_ISDIR(directory.st_mode) and
                        directory.st_uid == os.getuid() and
                        directory.st_gid == os.getgid() and
                        stat.S_IMODE(directory.st_mode) == (0o700 if private else 0o755),
                        "stage directory owner or mode changed: " + name)


def period_current(period: dict) -> None:
    now = dt.datetime.now(dt.timezone.utc)
    start = dt.datetime.fromisoformat(period["not_before"])
    end = dt.datetime.fromisoformat(period["expires_at"])
    require(start.tzinfo is not None and end.tzinfo is not None and
            start <= now < end and end - start == dt.timedelta(hours=24),
            "selected Source period is not current")


def stage_provenance() -> None:
    """Bind the observed stage, never treat that observation as continuing custody."""
    host = Path("/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host")
    bindings = (
        (host / "fresh-reader-docker-0008/freeze.json", STAGE_FREEZE_SHA),
        (STAGE / "evidence/stage-terminal.json", STAGE_TERMINAL_SHA),
        (STAGE / "consumed.json", STAGE_CONSUMED_SHA),
        (host / "FRESH-READER-DOCKER-INDEPENDENT-EFFECT-REVIEW-0008.md", STAGE_REVIEW_ONE_SHA),
        (host / "independent-reader-stage-effect-review-0008/review.json", STAGE_REVIEW_TWO_SHA),
        (host / "reader-only-entrypoint-0004/freeze.json", ENTRY_FREEZE_SHA),
        (host / "READER-ONLY-ENTRYPOINT-INDEPENDENT-STATIC-REVIEW-0004.md", ENTRY_REVIEW_SHA),
        (host / "READER-DOCKER-MOUNT-TOPOLOGY-AUDIT-20261020-0001.md", MOUNT_AUDIT_SHA),
        (host / "reader-only-docker-controller-0003/freeze.json", CONTROLLER_FREEZE_SHA),
        (host / "fresh-reader-docker-0005/freeze.json", READER_ROLE_FREEZE_SHA),
        (host / "reader-only-unified-0001/freeze.json", UNIFIED_0001_FREEZE_SHA),
        (host / "independent-reader-unified-review-0001/review.json", UNIFIED_0001_REVIEW_SHA),
        (host / "READER-ONLY-UNIFIED-INDEPENDENT-STATIC-REVIEW-0001.md", UNIFIED_0001_REVIEW_TWO_SHA),
        (host / "reader-only-unified-0002/freeze.json", UNIFIED_0002_FREEZE_SHA),
        (host / "independent-reader-unified-review-0002/review.json", UNIFIED_0002_REVIEW_ONE_SHA),
        (host / "READER-ONLY-UNIFIED-INDEPENDENT-STATIC-REVIEW-0002.md", UNIFIED_0002_REVIEW_TWO_SHA),
    )
    for path, expected in bindings:
        require(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == expected,
                "selected Reader predecessor or independent review changed")
    stage = json.loads((STAGE / "evidence/stage-terminal.json").read_bytes())
    require(stage["overall"] == "OBSERVED_STAGE_ONLY" and
            stage["reader_effect"] == "NOT_RUN" and stage["input_files"] == 986 and
            stage["selection_sha256"] == SELECTION_SHA and
            stage["reader_manifest_sha256"] == READER_SHA and
            stage["source_package_sha256"] ==
            "f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b",
            "selected stage observation differs")
    stage_unknown_absent(STAGE)
    require(STAGE.is_dir() and not STAGE.is_symlink() and
            STAGE.stat().st_uid == os.getuid() and STAGE.stat().st_mode & 0o777 == 0o700,
            "selected stage attachment differs")


def stage_unknown_absent(stage: Path) -> None:
    """Stage 0008 writes UNKNOWN at the attempt root, outside evidence/."""
    for path in (stage / "stage-unknown.json", stage / "evidence/stage-unknown.json"):
        try:
            path.lstat()
        except FileNotFoundError:
            continue
        raise ValueError("stage UNKNOWN supersedes neutral receipt")


def frozen_inputs() -> dict:
    stage_provenance()
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
    freeze = json.loads(freeze_raw)
    require(freeze["schema_version"] == "lab-reader-only-unified-freeze/v6-enabled" and
            freeze["stage_freeze_sha256"] == STAGE_FREEZE_SHA and
            freeze["reader_entrypoint_sha256"] == ENTRYPOINT_SHA and
            freeze["selection_sha256"] == SELECTION_SHA and
            freeze["effect"] == "NOT_RUN" and freeze["release_enabled"] is True and
            freeze["selected_attempt"] == str(ATTEMPT) and
            freeze["container_name"] == NAME and freeze["image_id"] == IMAGE,
            "unified Reader tool freeze differs")
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
    stage_plan_raw = (BASE / "stage-plan.json").read_bytes()
    require(sha(stage_plan_raw) == STAGE_PLAN_SHA, "Reader stage plan changed")
    stage_plan = json.loads(stage_plan_raw)
    stage_rows = stage_plan["files"]
    require(stage_plan["schema_version"] == "lab-reader-stage-copy-plan/v1-inert" and
            stage_plan["effect"] == "NOT_RUN" and
            stage_plan["archive_body_opened"] is False and
            stage_plan["selection_sha256"] == SELECTION_SHA and
            len(stage_rows) == 986 and
            [(row["path"], row["sha256"]) for row in stage_rows] ==
            sorted((row["path"], row["sha256"]) for row in rows),
            "Reader stage plan selection differs")
    verify_stage_metadata(ROOT, {row["path"]: row for row in stage_rows},
                          expected_directories(set(names)))
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
    selected = os.fstat(HELD_MOUNTS[0][-1][1]) if HELD_MOUNTS else ROOT.stat()
    return [DOCKER, "create", "--name", NAME, "--label", "cal.reader.attempt=" + label,
            "--network", "none", "--read-only", "--cap-drop", "ALL",
            "--ipc", "private",
            "--security-opt", "no-new-privileges:true", "--pids-limit", "1",
            "--memory", "1g", "--cpus", "1", "--user", "1000:1000",
            "--env", f"CAL_READER_STAGE_ID={selected.st_dev}:{selected.st_ino}",
            "--mount", f"type=bind,src={ROOT},dst=/attempt/root,readonly",
            "--mount", f"type=bind,src={OUT},dst=/attempt/reader-output",
            "--mount", f"type=bind,src={BASE},dst=/tool,readonly",
            "--tmpfs", "/attempt/tmp:rw,nosuid,nodev,size=512m,mode=0700,uid=1000,gid=1000",
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
        # A failed create still needs its bounded partial response. Keep it on
        # the exception for the create-only recorder, never in the terminal.
        primary.bounded_stdout = bytes(outputs[child.stdout])
        primary.bounded_stderr = bytes(outputs[child.stderr])
        primary.child_returncode = code
        if isinstance(primary, ValueError) and "deadline" in str(primary):
            timeout = subprocess.TimeoutExpired(argv, seconds)
            if hasattr(primary, "secondary_cleanup_errors"):
                timeout.secondary_cleanup_errors = primary.secondary_cleanup_errors
            timeout.bounded_stdout = primary.bounded_stdout
            timeout.bounded_stderr = primary.bounded_stderr
            timeout.child_returncode = code
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


def create_diagnostic(raw: bytes) -> str:
    """Allowlist a diagnostic category; never retain arbitrary daemon text."""
    value = raw.decode("utf-8", "replace").strip().lower()
    if not value:
        return "EMPTY"
    if "invalid mount config" in value:
        return "INVALID_MOUNT_CONFIG"
    if "no such image" in value or "unable to find image" in value:
        return "IMAGE_UNAVAILABLE"
    if "conflict. the container name" in value:
        return "NAME_CONFLICT"
    if "cannot connect to the docker daemon" in value:
        return "DAEMON_UNAVAILABLE"
    return "OTHER_REDACTED"


def record_create_response(label: str, argv: list[str], proc=None, error=None) -> dict:
    """Durable no-replace create outcome before CID parsing or daemon action."""
    stdout = proc.stdout if proc is not None else getattr(error, "bounded_stdout", b"")
    stderr = proc.stderr if proc is not None else getattr(error, "bounded_stderr", b"")
    require(type(stdout) is bytes and type(stderr) is bytes and
            len(stdout) <= MAX_CLI and len(stderr) <= MAX_CLI,
            "create response stream differs")
    code = proc.returncode if proc is not None else getattr(error, "child_returncode", None)
    candidate = stdout.strip()
    response = {
        "schema_version": "lab-reader-docker-create-response/v1",
        "container_name": NAME, "attempt_label": label, "image_id": IMAGE,
        "argv_sha256": sha(json_bytes(argv)), "returncode": code,
        "error_class": type(error).__name__ if error is not None else None,
        "stdout_size": len(stdout), "stdout_sha256": sha(stdout),
        "stderr_size": len(stderr), "stderr_sha256": sha(stderr),
        "stderr_diagnostic": create_diagnostic(stderr),
        "stdout_cid": candidate.decode("ascii") if len(candidate) == 64 and
                      all(ch in b"0123456789abcdef" for ch in candidate) else None,
    }
    exclusive(EVIDENCE / "reader-create-response.json", json_bytes(response))
    return response


def observe_created(label: str) -> dict:
    """Persist exact-name daemon observation before any start or cleanup."""
    try:
        info = inspected(NAME)
    except BaseException as error:
        result = {"schema_version": "lab-reader-docker-create-observation/v1",
                  "state": "INSPECT_UNKNOWN", "error_class": type(error).__name__}
        exclusive(EVIDENCE / "reader-create-observation.json", json_bytes(result))
        raise
    result = {"schema_version": "lab-reader-docker-create-observation/v1",
              "state": "ABSENT" if info is None else "PRESENT"}
    if info is not None:
        try:
            actual = owned(info, label, None)
            result.update(identity="MATCH", container_id=actual,
                          daemon_status=info["State"].get("Status"),
                          running=info["State"].get("Running"))
        except BaseException as error:
            result.update(identity="DIFFERS", error_class=type(error).__name__)
    exclusive(EVIDENCE / "reader-create-observation.json", json_bytes(result))
    return result


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
    candidate = None
    with ExitStack() as stack:
        HELD_EVIDENCE = stack.enter_context(held_directory(EVIDENCE))
        HELD_OUTPUT = stack.enter_context(held_directory(OUT))
        HELD_MOUNTS = [stack.enter_context(held_directory(ROOT)),
                       stack.enter_context(held_directory(BASE))]
        try:
            candidate = _run_held()
        finally:
            HELD_EVIDENCE = None
            HELD_OUTPUT = None
            HELD_MOUNTS = []
            LOG_IDENTITIES = {}
    # The provisional result is never authoritative. ExitStack has checked
    # attachment and completed every selected input/output/evidence close.
    return finalize_closed(candidate)


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
    create_recorded = False
    create_observed = False
    try:
        require(not STOP_REQUESTED, "controller interrupted before Docker create")
        LOG_IDENTITIES[stdout_path.name] = exclusive(stdout_path, b"")
        LOG_IDENTITIES[stderr_path.name] = exclusive(stderr_path, b"")
        require(not terminal_path.exists(), "Reader terminal path already exists")
        for chain in HELD_MOUNTS:
            check_chain(chain)
        create_argv = docker_create_argv(label)
        try:
            created = cli(create_argv, seconds=20)
        except BaseException as create_error:
            record_create_response(label, create_argv, error=create_error)
            create_recorded = True
            observe_created(label)
            create_observed = True
            raise
        response = record_create_response(label, create_argv, proc=created)
        create_recorded = True
        observation = observe_created(label)
        create_observed = True
        for chain in HELD_MOUNTS:
            check_chain(chain)
        require(created.returncode == 0 and response["stdout_cid"] is not None,
                "Docker create response unavailable")
        cid = response["stdout_cid"]
        require(observation.get("state") == "PRESENT" and
                observation.get("identity") == "MATCH" and
                observation.get("container_id") == cid and
                observation.get("daemon_status") == "created" and
                observation.get("running") is False,
                "created Reader Docker observation unconfirmed")
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
    if create_recorded and create_observed:
        try:
            result.update(settle(label, cid))
        except BaseException as error:
            result["cleanup_error_class"] = type(error).__name__
            result["cleanup_error"] = str(error)[:240]
    else:
        result["cleanup"] = "NOT_ATTEMPTED_WITHOUT_CREATE_OBSERVATION"
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
        def provisional_bytes() -> bytes:
            terminal_bytes()
            provisional = dict(result)
            provisional["candidate_overall"] = provisional["overall"]
            provisional["overall"] = "UNKNOWN"
            provisional["finalization"] = "PENDING_OUTER_CLOSES"
            return json_bytes(provisional)
        exclusive(terminal_path, provisional_bytes(), commit_check=provisional_bytes)
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
    return result


def finalize_closed(candidate: dict | None) -> dict:
    """Publish a final disposition only after every operation-held FD closes."""
    require(candidate is not None, "Reader provisional result unavailable")
    provisional_path = EVIDENCE / "reader-once.terminal.json"
    provisional_raw = bounded_read(provisional_path, MAX_RECEIPT)
    provisional = json.loads(provisional_raw)
    require(provisional["overall"] == "UNKNOWN" and
            provisional["candidate_overall"] == candidate["overall"] and
            provisional["attempt_label"] == candidate["attempt_label"] and
            provisional["finalization"] == "PENDING_OUTER_CLOSES",
            "Reader provisional result differs")
    final = dict(candidate)
    final.update(schema_version="lab-reader-only-docker-final/v1",
                 finalization="CLOSED_AND_COMMITTED",
                 provisional_sha256=sha(provisional_raw))
    def final_bytes() -> bytes:
        interrupted = STOP_REQUESTED or bool({signal.SIGINT, signal.SIGTERM} & signal.sigpending())
        expired = False
        if final.get("overall") == "PASS":
            try:
                period_current(json.loads(bounded_read(
                    ROOT / SOURCE / "packages/0001/period.json", 4096)))
            except BaseException:
                expired = True
        if interrupted or expired:
            final.update(operation="UNKNOWN", overall="UNKNOWN",
                         reader_effect="MAY_HAVE_RUN")
            if interrupted:
                final["interrupted"] = True
            if expired:
                final["period_expired_at_commit"] = True
        return json_bytes(final)
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
    try:
        exclusive(EVIDENCE / "reader-once.final.json", final_bytes(),
                  commit_check=final_bytes)
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
    # All final-file handles, parent handles and signal-mask restoration have
    # completed. A disagreement or failed read leaves the marker missing.
    require(bounded_read(EVIDENCE / "reader-once.final.json", MAX_RECEIPT) == final_bytes(),
            "Reader final disposition changed before marker")
    # mkdir is the last effect. It holds no FD that could fail during a later
    # close. A missing marker leaves even a written PASS file UNKNOWN.
    os.mkdir(EVIDENCE / "reader-once.finalized", mode=0o700)
    return final


def preflight() -> dict:
    """Read-only same-state check; no Docker or Reader call."""
    require(not ATTEMPT.exists() and not ATTEMPT.is_symlink(),
            "selected one-shot Reader attempt is not fresh")
    plan = frozen_inputs()
    require(len(plan["rows"]) == 986, "Reader staged selection differs")
    statvfs = os.statvfs("/tmp")
    available = statvfs.f_bavail * statvfs.f_frsize
    require(available >= 512 * 1024 * 1024,
            "selected host temporary filesystem lacks predispatch headroom")
    return {"schema_version": "lab-reader-only-unified-preflight/v1",
            "status": "PASS_INERT", "effect": "NOT_RUN", "attempt_fresh": True,
            "stage_freeze_sha256": STAGE_FREEZE_SHA,
            "stage_terminal_sha256": STAGE_TERMINAL_SHA,
            "selection_sha256": SELECTION_SHA,
            "reader_manifest_sha256": READER_SHA,
            "selected_files": len(plan["rows"]),
            "host_tmp_available_bytes": available,
            "claim_ceiling": "Current disposable Reader input checks only; no Docker Reader effect or protected Source8 qualification."}


def prepare_attempt() -> None:
    """No-replace local one-shot output/evidence; a partial tree is consumed."""
    require(EFFECT_ENABLED, "Reader effect disabled pending independent review and release")
    ATTEMPT.mkdir(mode=0o700, exist_ok=False)
    for path in (EVIDENCE, OUT):
        path.mkdir(mode=0o700, exist_ok=False)
    for path in (ATTEMPT, EVIDENCE, OUT):
        st = path.lstat()
        require(stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid() and
                st.st_gid == os.getgid() and st.st_mode & 0o777 == 0o700,
                "selected Reader output or evidence root differs")
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


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
    final_path = EVIDENCE / "reader-once.final.json"
    marker_path = EVIDENCE / "reader-once.finalized"
    finalization = "MISSING_OR_FAILED"
    try:
        mark = marker_path.lstat()
    except FileNotFoundError:
        pass
    else:
        require(stat.S_ISDIR(mark.st_mode) and mark.st_uid == os.getuid() and
                mark.st_gid == os.getgid() and stat.S_IMODE(mark.st_mode) == 0o700 and
                not list(marker_path.iterdir()),
                "Reader finalization marker custody differs")
        try:
            final = json.loads(bounded_read(final_path, MAX_RECEIPT))
            provisional_raw = bounded_read(EVIDENCE / "reader-once.terminal.json", MAX_RECEIPT)
            provisional = json.loads(provisional_raw)
            require(final["schema_version"] == "lab-reader-only-docker-final/v1" and
                    final["finalization"] == "CLOSED_AND_COMMITTED" and
                    final["attempt_label"] == marker["attempt_label"] and
                    final["container_name"] == NAME and
                    final["provisional_sha256"] == sha(provisional_raw) and
                    provisional["overall"] == "UNKNOWN" and
                    provisional["candidate_overall"] in ("PASS", "UNKNOWN"),
                    "Reader final disposition differs")
        except Exception:
            finalization = "INVALID_UNKNOWN"
        else:
            finalization = "CLOSED_AND_COMMITTED"
            require(final["overall"] != "PASS",
                    "successful consumed attempt needs no recovery")
    recovery = {"schema_version": "lab-reader-only-docker-recovery/v1",
                "operation": "UNKNOWN", "no_retry": True,
                "attempt_label": marker["attempt_label"], "container_name": NAME,
                "finalization": finalization}
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
    group.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    def request_stop(_signum, _frame):
        global STOP_REQUESTED
        STOP_REQUESTED = True
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    if args.preflight:
        terminal = preflight()
        print(json.dumps(terminal, sort_keys=True))
        sys.exit(0)
    require(EFFECT_ENABLED, "Reader controller effect disabled pending independent review and release")
    if args.execute_reviewed_one_shot:
        prepare_attempt()
        terminal = run()
    else:
        terminal = recover_consumed()
    print(json.dumps(terminal, sort_keys=True))
    sys.exit(0 if terminal.get("overall") == "PASS" or
             (args.recover_consumed_cleanup and terminal.get("absent")) else 2)
