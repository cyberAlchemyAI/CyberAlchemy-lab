"""Install and restore the exact local fixture package in two fresh roots.

This is a bounded fixture exercise. It does not install the API40 Service.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
T30 = ROOT / "implementation/lab-runtime/local-host/t30-candidate-rehearsal-0001"
REHEARSE_SHA = "791ebdb89dbc9de84196581df9eaa087dc9f2b456800822e26c085af0963a56f"
ARCHIVE_SHA = "020f2755bd2687003f15d93a49a1e3bd6a49d838e3efe1398d6731881edce448"
CHAIN_MARKER = "local Source → Reader → Mapper → Context fixture: PASS".encode()
WORK_MARKER = b"local Work journey: PASS"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def package_module():
    path = T30 / "rehearse.py"
    raw = path.read_bytes()
    need(sha(raw) == REHEARSE_SHA and path.is_file() and not path.is_symlink(),
         "selected local package loader differs")
    spec = importlib.util.spec_from_file_location("_cal_t19_rehearse", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    need(sha(path.read_bytes()) == REHEARSE_SHA, "selected loader changed during import")
    package, _, _ = module.selected_modules()
    return package


def run_command(args: list[str], env: dict[str, str] | None = None,
                marker: bytes | None = None, timeout: int = 1800) -> dict:
    started = time.monotonic()
    process = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, timeout=timeout)
    return {"exit_code": process.returncode,
            "marker_seen": marker is None or marker in process.stdout,
            "stdout_sha256": sha(process.stdout), "stderr_sha256": sha(process.stderr),
            "elapsed_seconds": round(time.monotonic() - started, 3)}


def resources(project: str, image: str) -> dict:
    def names(args):
        return sorted(subprocess.run(args, capture_output=True, check=True).stdout.decode().splitlines())
    return {"containers": names(["docker", "ps", "-aq", "--filter", f"label=com.docker.compose.project={project}"]),
            "volumes": names(["docker", "volume", "ls", "-q", "--filter", f"label=com.docker.compose.project={project}"]),
            "networks": names(["docker", "network", "ls", "-q", "--filter", f"label=com.docker.compose.project={project}"]),
            "image_present": subprocess.run(["docker", "image", "inspect", image], capture_output=True).returncode == 0}


def exercise(root: Path, label: str) -> dict:
    token = uuid.uuid4().hex
    project = "cal-t19-" + token[:20]
    image = "cyberalchemy-lab-t19:local-" + token
    context = root / "fixture"
    env = dict(os.environ, LAB_LOCAL_BUILD_CONTEXT=str(context), LAB_LOCAL_IMAGE=image)
    prefix = ["docker", "compose", "-p", project, "-f", str(context / "compose.yaml")]
    empty = {"containers": [], "volumes": [], "networks": [], "image_present": False}
    before = resources(project, image)
    need(before == empty, "fresh Docker identity is occupied")
    stages = []
    cleanup = []
    try:
        for args, marker in ((prefix + ["build", "--no-cache", "lab-fixture"], None),
                             (prefix + ["run", "--rm", "--no-deps", "--pull", "never", "chain-fixture"], CHAIN_MARKER),
                             (prefix + ["run", "--rm", "--no-deps", "--pull", "never", "lab-fixture"], WORK_MARKER)):
            row = run_command(args, env, marker)
            stages.append(row)
            if row["exit_code"] != 0 or not row["marker_seen"]:
                break
    finally:
        cleanup.append(run_command(prefix + ["down", "-v", "--remove-orphans"], env, timeout=180))
        cleanup.append(run_command(["docker", "image", "rm", "--", image], timeout=180))
    after = resources(project, image)
    return {"label": label, "project": project, "image": image,
            "stages": stages, "cleanup": cleanup, "before": before, "after": after,
            "passed": len(stages) == 3 and all(s["exit_code"] == 0 and s["marker_seen"] for s in stages)
                      and all(s["exit_code"] == 0 for s in cleanup) and after == empty}


def run() -> dict:
    package = package_module()
    body = package.build()
    need(sha(body) == ARCHIVE_SHA, "selected candidate archive differs")
    with tempfile.TemporaryDirectory(prefix="cal-t19-two-root-") as name:
        parent = Path(name)
        roots = [parent / "install-a", parent / "install-b"]
        installs = []
        for root in roots:
            root.mkdir(mode=0o700)
            result = package.extract_verified(body, root)
            need(result["archive_sha256"] == ARCHIVE_SHA and
                 result["extracted_fixture_context_verified"] is True,
                 "fresh extraction differs")
            installs.append({"root_name": root.name, "replayed_additions": result["replayed_additions"],
                             "fixture_context_verified": True})
        need(roots[0].samefile(roots[1]) is False, "install roots overlap")
        foreign = parent / "foreign.txt"
        foreign.write_text("unrelated-t19-sentinel\n")
        foreign_sha = sha(foreign.read_bytes())
        # A changed archive refuses before touching the existing installation.
        corrupted = body[:-1] + bytes([body[-1] ^ 1])
        need(sha(corrupted) != ARCHIVE_SHA, "corrupt archive control ineffective")
        before = sha((roots[0] / "fixture/package-manifest.json").read_bytes())
        try:
            package.replay(corrupted)
        except (ValueError, KeyError, OSError, AssertionError, zipfile.BadZipFile):
            pass
        else:
            raise ValueError("corrupt restore archive was accepted")
        need(sha((roots[0] / "fixture/package-manifest.json").read_bytes()) == before,
             "failed restore changed installed bytes")
        executions = [exercise(root, root.name) for root in roots]
        need(all(row["passed"] for row in executions), "one fresh installed fixture did not start")
        # Restore into a third empty root from the same pinned archive. The old
        # installation stays available until the new extraction has verified.
        restored = parent / "restored"
        restored.mkdir(mode=0o700)
        restored_result = package.extract_verified(body, restored)
        need(restored_result["archive_sha256"] == ARCHIVE_SHA and
             restored_result["replayed_additions"] == installs[0]["replayed_additions"],
             "restored archive replay differs")
        restore_run = exercise(restored, "restored")
        need(restore_run["passed"] and sha(foreign.read_bytes()) == foreign_sha,
             "restore/rollback disturbed the fixture or foreign sibling")
        result = {"schema_version": "lab-t19-two-root-fixture/v1", "archive_sha256": ARCHIVE_SHA,
                  "installations": installs, "fresh_install_runs": executions,
                  "failed_restore_refused_without_change": True,
                  "restore_run": restore_run, "foreign_sibling_unchanged": True,
                  "fixture_install_restore_passed": True,
                  "installed_api40_service": False, "full_T19_complete": False,
                  "authority_effect": "none", "runner_sha256": sha(Path(__file__).read_bytes())}
    result["owned_roots_removed"] = not parent.exists()
    need(result["owned_roots_removed"], "owned install roots survived cleanup")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
