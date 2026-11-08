"""Reviewed, consumed-once successor Source Docker release controller.

The Source effect stays UNRUN until stage and release independent reviews pass.
Ambiguous daemon observation retains the exclusive consumed attempt.
"""
from __future__ import annotations

import argparse
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

BASE = Path("/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/context-successor-recovery-0001/tool")
RELEASE = Path(__file__).resolve().parent
STAGE = RELEASE.parent / "context-successor-stage-0001"
STAGE_REVIEW = RELEASE.parent / "CONTEXT-SUCCESSOR-STAGE-INDEPENDENT-STATIC-REVIEW-0001.md"
STAGE_EFFECT_REVIEW = RELEASE.parent / "CONTEXT-SUCCESSOR-STAGE-INDEPENDENT-EFFECT-REVIEW-0001.md"
RELEASE_REVIEW = RELEASE.parent / "CONTEXT-SUCCESSOR-SOURCE-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md"
STAGE_FREEZE_SHA = "fb957ddd0d983f87ab4ecdb769f77d8a5ead501055cad1e8b83898c39d93f617"
STAGE_STATIC_REVIEW_SHA = "6247e3e3328cf1979b2d0945678f5df2f9a8e8dd554804d1403c1cbcca8e63cf"
STAGE_EFFECT_REVIEW_SHA = "983e857cd4a7cc283c6a270e6427cd9ea238eb77dd4bac3833d3952322765e50"
STAGE_MARKER_SHA = "40739f238e27fc459a8511e2b919aa9beb057a25a8b1b2360fd2399a327a582d"
STAGE_RECEIPT_SHA = "2b0c91b8ccdad24f9cd255c32adfbd731ffbe5a09f1277f333930d8c5b4bbe96"
ATTEMPT = Path("/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/source-attempt")
ROOT = ATTEMPT / "root"
EVIDENCE = ATTEMPT / "evidence"
FAMILY = ROOT / "product/lab/release-candidates/v1/interface/docker-source-20261020-0002"
IMAGE = "sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874"
DOCKER = "/usr/bin/docker"
DOCKER_SHA = "999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00"
PYTHON_SHA = "52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41"
FREEZE_SHA = "7b4ba299155eab233fa703fcdb796fbddb06d4f7d53065223070dc5175dd2867"
NAME = "cal-source-only-20261020-0002-successor1"
MAX_STREAM = 4 * 1024 * 1024
DEADLINE = 180.0
STOP_REQUESTED = False


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def exclusive(path: Path, raw: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    try:
        view = memoryview(raw)
        while view:
            used = os.write(fd, view)
            require(used > 0, "exclusive write did not advance")
            view = view[used:]
        os.fchmod(fd, 0o600)
        os.fsync(fd)
    finally:
        os.close(fd)
    reader = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        st = os.fstat(reader)
        require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and
                stat.S_IMODE(st.st_mode) == 0o600 and
                st.st_uid == os.geteuid() and st.st_gid == os.getegid() and
                os.read(reader, len(raw) + 1) == raw,
                "exclusive evidence readback differs")
    finally:
        os.close(reader)
    dirfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)


def reviewed_stage() -> dict:
    """Require exact durable public stage, including its independent review."""
    require(sha((STAGE / "freeze.json").read_bytes()) == STAGE_FREEZE_SHA,
            "selected stage freeze changed")
    review = STAGE_REVIEW.read_bytes()
    effect_review = STAGE_EFFECT_REVIEW.read_bytes()
    require(sha(review) == STAGE_STATIC_REVIEW_SHA and
            sha(effect_review) == STAGE_EFFECT_REVIEW_SHA and
            b"Verdict: PASS" in review and STAGE_FREEZE_SHA.encode() in review and
            b"Verdict: PASS" in effect_review and
            STAGE_FREEZE_SHA.encode() in effect_review and
            STAGE_STATIC_REVIEW_SHA.encode() in effect_review,
            "selected durable stage lacks PASS review")
    stage_freeze = json.loads((STAGE / "freeze.json").read_bytes())
    for row in stage_freeze["file_bindings"]:
        path = STAGE / row["path"]
        require(path.is_file() and not path.is_symlink() and
                len(path.read_bytes()) == row["size"] and
                sha(path.read_bytes()) == row["sha256"],
                "reviewed stage member changed")
    stage_receipt_path = EVIDENCE / "stage-receipt.json"
    stage_marker_path = ATTEMPT.parent.parent / ".context-successor-20261020-0001-source-stage-consumed.json"
    for path in (stage_receipt_path, stage_marker_path):
        require(path.is_file() and not path.is_symlink() and
                stat.S_IMODE(path.stat().st_mode) == 0o600 and
                path.stat().st_uid == os.geteuid() and
                path.stat().st_gid == os.getegid(),
                "durable stage evidence mode or owner differs")
    receipt = json.loads(stage_receipt_path.read_bytes())
    marker_raw = stage_marker_path.read_bytes()
    marker = json.loads(marker_raw)
    require(sha(stage_receipt_path.read_bytes()) == STAGE_RECEIPT_SHA and
            sha(marker_raw) == STAGE_MARKER_SHA and
            receipt["schema"] == "context-successor-public-stage-receipt/v1" and
            receipt["status"] == "STAGE_ONLY_PASS" and
            receipt["files"] == 941 and
            receipt["public_cut_sha256"] == "0333193eecf462528082f79123aba15d53fc630cf21e9ae2ca39b993b30bf11b" and
            receipt["source_manifest_sha256"] == "2843a67fd28a295f5c175b8d8c2b31f701040bb8d7dedeade8d76bbdf057d1d1" and
            receipt["root"] == str(ROOT) and
            receipt["root_identity"] == [ROOT.stat().st_dev, ROOT.stat().st_ino] and
            receipt["marker_sha256"] == sha(marker_raw) and
            receipt["marker_identity"] == [stage_marker_path.stat().st_dev,
                                           stage_marker_path.stat().st_ino] and
            receipt["protected_archive_body"] == "ABSENT" and
            receipt["source_effect"] == "NOT_RUN" and
            receipt["retry_allowed"] is False and
            marker["schema"] == "context-successor-stage-intent/v1" and
            marker["status"] == "CONSUMED_NO_RETRY" and
            marker["family"] == str(ATTEMPT.parent) and
            marker["attempt"] == str(ATTEMPT),
            "durable public stage receipt or marker differs")
    return receipt


def reviewed_release() -> None:
    freeze_raw = (RELEASE / "freeze.json").read_bytes()
    freeze = json.loads(freeze_raw)
    review = RELEASE_REVIEW.read_bytes()
    require(b"Verdict: PASS" in review and sha(freeze_raw).encode() in review and
            freeze["status"] == "EFFECT_DISABLED_UNRUN_PENDING_INDEPENDENT_REVIEW" and
            freeze["stage_freeze_sha256"] == STAGE_FREEZE_SHA and
            freeze["source_effect"] == "UNRUN",
            "source release lacks matching independent PASS review")
    for row in freeze["file_bindings"]:
        path = RELEASE / row["path"]
        raw = path.read_bytes()
        require(path.is_file() and not path.is_symlink() and
                len(raw) == row["size"] and sha(raw) == row["sha256"],
                "source release member changed after review")


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
    names = {parent.as_posix() for name in files for parent in Path(name).parents
             if parent.as_posix() != "."}
    names |= {(FAMILY / part).relative_to(ROOT).as_posix()
              for part in ("packages", "receipts")}
    return names


def frozen_inputs() -> dict:
    require(Path(DOCKER).is_file() and not Path(DOCKER).is_symlink() and
            sha(Path(DOCKER).read_bytes()) == DOCKER_SHA and
            Path("/usr/bin/python3").is_file() and
            sha(Path("/usr/bin/python3").read_bytes()) == PYTHON_SHA and
            Path(sys.executable).resolve() == Path("/usr/bin/python3").resolve(),
            "selected host controller binaries changed")
    require(sha((BASE / "freeze.json").read_bytes()) == FREEZE_SHA, "0002 freeze changed")
    freeze = json.loads((BASE / "freeze.json").read_bytes())
    for row in freeze["file_bindings"]:
        path = BASE / row["path"]
        require(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row["sha256"],
                "0002 frozen member changed")
    plan = json.loads((BASE / "public-cut.json").read_bytes())
    now = dt.datetime.now(dt.timezone.utc)
    require(dt.datetime.fromisoformat(plan["not_before"]) <= now <
            dt.datetime.fromisoformat(plan["expires_at"]),
            "selected development episode is not current")
    selected = plan["public_inputs"] + plan["generated_bindings"]
    require(len(selected) == 941 and not ROOT.is_symlink(), "selected staged tree changed")
    for row in selected:
        path = ROOT / row["path"]
        require(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row["sha256"],
                "selected staged byte changed")
    actual_files, actual_dirs = tree_names(ROOT)
    selected_files = {row["path"] for row in selected}
    require(actual_files == selected_files and
            actual_dirs == expected_directories(selected_files),
            "staged file or directory inventory changed")
    return plan


def output_state(*, fresh: bool) -> dict:
    state = {}
    for name in ("packages", "receipts"):
        path = FAMILY / name
        require(path.is_dir() and not path.is_symlink(), "output root absent or symlinked")
        stat = path.stat()
        require(stat.st_uid == os.getuid() and stat.st_gid == os.getgid() and
                stat.st_mode & 0o777 == 0o700, "output owner or mode changed")
        if fresh:
            require(not list(path.iterdir()), "output root not fresh")
        state[name] = {"dev": stat.st_dev, "ino": stat.st_ino}
    return state


def docker_create_argv(label: str) -> list[str]:
    return [DOCKER, "create", "--name", NAME, "--label", "cal.source.attempt=" + label,
            "--network", "none", "--read-only", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true", "--pids-limit", "64",
            "--memory", "1g", "--cpus", "1", "--user", "1000:1000",
            "--userns", "host",
            "--mount", f"type=bind,src={ROOT},dst=/attempt/root,readonly",
            "--mount", f"type=bind,src={FAMILY / 'packages'},dst=/attempt/root/product/lab/release-candidates/v1/interface/docker-source-20261020-0002/packages",
            "--mount", f"type=bind,src={FAMILY / 'receipts'},dst=/attempt/root/product/lab/release-candidates/v1/interface/docker-source-20261020-0002/receipts",
            "--mount", f"type=bind,src={BASE},dst=/tool,readonly",
            "--tmpfs", "/attempt/tmp:rw,nosuid,nodev,size=512m,mode=1777",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=256m,mode=1777",
            IMAGE, "python", "-B", "/tool/source_once.py", "--execute-reviewed-one-shot"]


def cli(argv: list[str], *, seconds: float = 12.0) -> subprocess.CompletedProcess:
    return subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=seconds, check=False)


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


def selected_image_present() -> None:
    observed = cli([DOCKER, "image", "inspect", IMAGE])
    require(observed.returncode == 0, "selected Docker image unavailable")
    value = json.loads(observed.stdout)
    require(type(value) is list and len(value) == 1 and
            value[0].get("Id") == IMAGE,
            "selected Docker image identity differs")


def owned(info: dict, label: str, cid: str | None) -> str:
    actual = info["Id"]
    require(type(actual) is str and len(actual) == 64 and
            info["Name"] == "/" + NAME and info["Config"]["Image"] == IMAGE and
            info["Image"] == IMAGE and
            info["Config"]["Labels"].get("cal.source.attempt") == label and
            (cid is None or actual == cid), "selected Docker identity differs")
    return actual


def capture_start(cid: str, stdout_path: Path, stderr_path: Path) -> tuple[int | None, bool]:
    child = subprocess.Popen([DOCKER, "start", "-a", cid], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    selector = None
    primary = None
    cleanup_errors = []
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
        with stdout_path.open("ab", buffering=0) as out, stderr_path.open("ab", buffering=0) as err:
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
        try:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=3)
        except BaseException as error:
            cleanup_errors.append(error)
        if selector is not None:
            try:
                selector.close()
            except BaseException as error:
                cleanup_errors.append(error)
        for stream in (child.stdout, child.stderr):
            try:
                stream.close()
            except BaseException as error:
                cleanup_errors.append(error)
    if cleanup_errors:
        errors = ([primary] if primary is not None else []) + cleanup_errors
        raise BaseExceptionGroup("owned Docker client cleanup failed", errors)
    if primary is not None:
        raise primary
    return code, timed_out or overflow


def output_inventory() -> dict:
    roots = [FAMILY / "packages", FAMILY / "receipts"]
    entries = sorted(p for root in roots for p in root.rglob("*"))
    files = []
    directories = set()
    for path in entries:
        mode = path.lstat().st_mode
        require(not stat.S_ISLNK(mode) and (stat.S_ISREG(mode) or stat.S_ISDIR(mode)),
                "nonregular output entry")
        if stat.S_ISDIR(mode):
            directories.add(path.relative_to(FAMILY).as_posix())
        else:
            files.append(path)
    paths = files
    require(len(paths) <= 128, "output inventory count differs")
    total = 0
    rows = []
    for path in paths:
        size = path.stat().st_size
        total += size
        require(size <= 64 * 1024 * 1024 and total <= 256 * 1024 * 1024,
                "output inventory byte limit exceeded")
        rows.append({"path": path.relative_to(FAMILY).as_posix(),
                     "sha256": sha(path.read_bytes()), "size": size})
    manifest_path = FAMILY / "packages/0001/manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_bytes())
        members = manifest["files"]
        require(type(members) is list and len(members) <= 127 and
                all(type(row) is dict and set(row) == {"path", "sha256"} and
                    row["path"].startswith(
                        "product/lab/release-candidates/v1/interface/docker-source-20261020-0002/packages/0001/")
                    for row in members) and
                len({row["path"] for row in members}) == len(members),
                "package manifest members differ")
        package_files = {row["path"]: row["sha256"] for row in rows
                         if row["path"].startswith("packages/0001/") and
                         row["path"] != "packages/0001/manifest.json"}
        require(package_files == {row["path"].removeprefix(
                "product/lab/release-candidates/v1/interface/docker-source-20261020-0002/"): row["sha256"]
                for row in members}, "postclose package manifest closure differs")
        require({row["path"] for row in rows} ==
                set(package_files) | {"packages/0001/manifest.json"},
                "unexpected package or receipt output")
    expected_directories = {parent.as_posix() for row in rows
                            for parent in Path(row["path"]).parents
                            if parent.as_posix() not in (".", "packages", "receipts")}
    require(directories == expected_directories, "unexpected or missing output directory")
    return {"files": rows, "total_bytes": total,
            "package_manifest_present": manifest_path.is_file()}


def settle(label: str, cid: str | None, *, receipt_path: Path | None = None) -> dict:
    """Only mutate a container with the exact selected name/image/nonce/CID."""
    receipt_path = receipt_path or EVIDENCE / "source-pre-removal.json"
    info = inspected(NAME)
    if info is None:
        require(inspected(NAME) is None, "container absence not repeated")
        return {"absent": True, "daemon_exit": None, "cleanup": "already_absent",
                "forced_cleanup": True}
    actual = owned(info, label, cid)
    def receipt(value: dict) -> dict:
        return {"id": value["Id"], "name": value["Name"],
                "image_id": value["Image"],
                "attempt_label": value["Config"]["Labels"]["cal.source.attempt"],
                "status": value["State"].get("Status"),
                "running": value["State"]["Running"],
                "exit_code": value["State"].get("ExitCode")}
    daemon_exit = None
    forced = False
    if info["State"].get("Status") == "created":
        # Docker wait on an unstarted container can block. It is consumed but
        # has no source operation exit to claim.
        exclusive(receipt_path, json_bytes({"schema_version": "lab-source-docker-pre-removal/v1",
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
    exclusive(receipt_path, json_bytes({"schema_version": "lab-source-docker-pre-removal/v1",
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
    reviewed_release()
    reviewed_stage()
    require(EVIDENCE.is_dir() and not EVIDENCE.is_symlink() and
            EVIDENCE.stat().st_mode & 0o777 == 0o700, "selected evidence root differs")
    # These checks are pre-consumption. Once the O_EXCL marker exists, every
    # later failure remains consumed, including create's lost response.
    plan = frozen_inputs()
    before = output_state(fresh=True)
    attachments = {"root": (ROOT.stat().st_dev, ROOT.stat().st_ino),
                   "tool": (BASE.stat().st_dev, BASE.stat().st_ino)}
    selected_image_present()
    require(inspected(NAME) is None and inspected(NAME) is None,
            "selected container name already exists or daemon unavailable")
    require(not STOP_REQUESTED, "controller interrupted before launch")
    label = uuid.uuid4().hex
    marker = {"schema_version": "lab-source-only-consumed/v1", "container_name": NAME,
              "attempt_label": label, "image_id": IMAGE, "source_manifest_sha256": plan["source_manifest"]["sha256"],
              "state": "CONSUMED_NO_RETRY"}
    try:
        exclusive(EVIDENCE / "source-attempt-consumed.json", json_bytes(marker))
    except BaseException as error:
        raise RuntimeError("UNKNOWN_PRESERVE_NO_RETRY: Source marker claim uncertain; "
                           "retain selected attempt and Docker state") from error
    stdout_path = EVIDENCE / "source-once.stdout"
    stderr_path = EVIDENCE / "source-once.stderr"
    terminal_path = EVIDENCE / "source-once.terminal.json"
    result = {"schema_version": "lab-source-only-docker-terminal/v1",
              "attempt_label": label, "container_name": NAME,
              "operation": "UNKNOWN", "cleanup": "UNKNOWN", "overall": "UNKNOWN",
              "source_effect": "MAY_HAVE_RUN", "no_retry": True}
    cid = None
    try:
        require(not STOP_REQUESTED, "controller interrupted before Docker create")
        exclusive(stdout_path, b"")
        exclusive(stderr_path, b"")
        require(not terminal_path.exists(), "terminal path already exists")
        created = cli(docker_create_argv(label), seconds=20)
        require(created.returncode == 0 and len(created.stdout.strip()) == 64 and
                all(ch in b"0123456789abcdef" for ch in created.stdout.strip()),
                "Docker create response unavailable")
        cid = created.stdout.strip().decode()
        info = inspected(NAME)
        require(info is not None and owned(info, label, cid) == cid,
                "created Docker identity unconfirmed")
        exclusive(EVIDENCE / "source-container-id.json",
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
        settled = settle(label, cid)
        result.update(settled)
    except BaseException as error:
        result["cleanup_error_class"] = type(error).__name__
        result["cleanup_error"] = str(error)[:240]
    try:
        after = output_state(fresh=False)
        require(before == after, "selected output directory attachment changed")
        require(attachments == {"root": (ROOT.stat().st_dev, ROOT.stat().st_ino),
                                "tool": (BASE.stat().st_dev, BASE.stat().st_ino)},
                "selected input or tool attachment changed")
        frozen_inputs_post = frozen_inputs() if not (FAMILY / "packages/0001").exists() else None
        # After a package is produced the staged inventory differs only in the
        # two owned outputs; verify all 941 selected bytes independently.
        for row in plan["public_inputs"] + plan["generated_bindings"]:
            path = ROOT / row["path"]
            require(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == row["sha256"],
                    "post-close selected input differs")
        inventory = output_inventory()
        expected_names = {row["path"] for row in plan["public_inputs"] + plan["generated_bindings"]}
        family_rel = FAMILY.relative_to(ROOT)
        expected_names |= {(family_rel / row["path"]).as_posix() for row in inventory["files"]}
        actual_names, actual_dirs = tree_names(ROOT)
        require(actual_names == expected_names and
                actual_dirs == expected_directories(expected_names),
                "postclose staged tree escaped selected inputs and outputs")
        result["postclose_inputs"] = "PASS"
        result["output_attachment"] = "PASS"
        result["output_inventory"] = inventory
        del frozen_inputs_post
    except BaseException as error:
        result["postclose_error_class"] = type(error).__name__
    result["stdout_sha256"] = sha(stdout_path.read_bytes()) if stdout_path.exists() else None
    result["stderr_sha256"] = sha(stderr_path.read_bytes()) if stderr_path.exists() else None
    for path in (stdout_path, stderr_path):
        if path.exists():
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    if (not STOP_REQUESTED and result.get("absent") is True and
            result.get("forced_cleanup") is False and
            result.get("daemon_exit_consistent") is True and
            result.get("daemon_exit") == 0 and
            result.get("client_exit") == 0 and result.get("stream_or_deadline_failure") is False and
            result.get("postclose_inputs") == "PASS" and result.get("output_attachment") == "PASS"):
        try:
            lines = stdout_path.read_bytes().splitlines()
            require(len(lines) == 1 and not stderr_path.read_bytes(),
                    "single clean final Source result required")
            source = json.loads(lines[0])
            require(source["result"] == "PASS" and source["cold_replay"] == "PASS" and
                    source["signed_transactions"] == 2 and source["authored_records"] == 11 and
                    source["authored_typed_relations"] == 10 and
                    source["source_manifest_sha256"] == plan["source_manifest"]["sha256"] and
                    source["authority_effect"] == "none" and source["actual_owner_outcome"] is None and
                    sha((FAMILY / "packages/0001/manifest.json").read_bytes()) == source["package_manifest_sha256"],
                    "independent final Source result differs")
            result.update(operation="PASS", cleanup="PASS", overall="PASS",
                          source_effect="DEVELOPMENT_SOURCE_ONLY",
                          package_manifest_sha256=source["package_manifest_sha256"],
                          claim_ceiling="New disposable local Source package and signed cold replay only; no Reader/Mapper/Context or protected Source8 qualification.")
        except BaseException as error:
            result["result_error_class"] = type(error).__name__
    # The signal handler's request is sticky. Do not publish a positive result
    # after a late request during settle, postclose checks or result parsing.
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM})
    try:
        if STOP_REQUESTED or {signal.SIGINT, signal.SIGTERM} & signal.sigpending():
            result.update(operation="UNKNOWN", overall="UNKNOWN",
                          source_effect="MAY_HAVE_RUN", interrupted=True)
        exclusive(terminal_path, json_bytes(result))
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
    return result


def recover_consumed() -> dict:
    reviewed_release()
    """Cleanup-only path after controller crash; never starts Source again."""
    marker = json.loads((EVIDENCE / "source-attempt-consumed.json").read_bytes())
    require(marker["state"] == "CONSUMED_NO_RETRY" and
            marker["container_name"] == NAME and marker["image_id"] == IMAGE,
            "selected consumed marker differs")
    cid_path = EVIDENCE / "source-container-id.json"
    cid = None
    if cid_path.exists():
        identity = json.loads(cid_path.read_bytes())
        require(identity["name"] == NAME and identity["image_id"] == IMAGE and
                identity["attempt_label"] == marker["attempt_label"],
                "durable selected CID record differs")
        cid = identity["container_id"]
    terminal = EVIDENCE / "source-once.terminal.json"
    if terminal.exists():
        require(json.loads(terminal.read_bytes())["overall"] != "PASS",
                "successful consumed attempt needs no recovery")
    recovery = {"schema_version": "lab-source-only-docker-recovery/v1",
                "operation": "UNKNOWN", "no_retry": True,
                "attempt_label": marker["attempt_label"], "container_name": NAME}
    prior_path = EVIDENCE / "source-pre-removal.json"
    if prior_path.exists():
        prior_raw = prior_path.read_bytes()
        prior = json.loads(prior_raw)
        container = prior["container"]
        require(prior["schema_version"] == "lab-source-docker-pre-removal/v1" and
                container["name"] == "/" + NAME and container["image_id"] == IMAGE and
                container["attempt_label"] == marker["attempt_label"] and
                (cid is None or container["id"] == cid),
                "durable prior pre-removal receipt identity differs")
        recovery["prior_pre_removal_sha256"] = sha(prior_raw)
        recovery["prior_daemon_wait_exit"] = prior["daemon_wait_exit"]
    try:
        recovery.update(settle(marker["attempt_label"], cid,
                               receipt_path=EVIDENCE / "source-recovery-pre-removal-0001.json"))
    except Exception as error:
        recovery["cleanup_error_class"] = type(error).__name__
        recovery["cleanup_error"] = str(error)[:240]
    exclusive(EVIDENCE / "source-recovery-0001.json", json_bytes(recovery))
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
    terminal = run() if args.execute_reviewed_one_shot else recover_consumed()
    print(json.dumps(terminal, sort_keys=True))
    sys.exit(0 if terminal.get("overall") == "PASS" or
             (args.recover_consumed_cleanup and terminal.get("absent")) else 2)
