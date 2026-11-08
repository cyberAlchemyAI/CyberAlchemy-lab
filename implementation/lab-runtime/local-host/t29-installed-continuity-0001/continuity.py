"""Disposable installed-fixture continuity, consumption, and generation rollback."""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HOST = ROOT / "implementation/lab-runtime/local-host"
PIN = {
    "source-manifest.json": "1e00e6fd7f1baf7f8cfcd0c0ae7c11ab66649e05cc9575705bee968117ae0346",
    "package-release.json": "a8cfacd9e15b65184c1b87a284a699475850b8a783a354102301f50ccbe9cb3e",
    "package_runtime.py": "a617eead84b5b802e2f6c9ab983a24fc28ac8ea7551df8d5d57cc54fd3adfdcb",
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def checked(path: Path, expected: str) -> bytes:
    """Reject symlink ancestors and recheck the held regular file."""
    path = Path(path)
    for parent in (path, *path.parents):
        if parent == ROOT.parent:
            break
        state = parent.lstat()
        require(not stat.S_ISLNK(state.st_mode), "linked selected path")
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "unsafe selected file")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        held = os.fstat(fd)
        require((held.st_dev, held.st_ino) == (before.st_dev, before.st_ino), "selected file replaced")
        raw = b""
        while True:
            part = os.read(fd, 1 << 20)
            if not part:
                break
            raw += part
        after = os.fstat(fd)
        require((held.st_size, held.st_mtime_ns, held.st_ctime_ns) ==
                (after.st_size, after.st_mtime_ns, after.st_ctime_ns), "selected file changed")
    finally:
        os.close(fd)
    require(sha(raw) == expected, "selected file digest changed: " + path.name)
    return raw


def selected() -> dict:
    raw = {name: checked(HOST / name, digest) for name, digest in PIN.items()}
    manifest = json.loads(raw["source-manifest.json"])
    release = json.loads(raw["package-release.json"])
    require(release == {"schema": "lab-local-package-release/v1",
                        "source_manifest_sha256": PIN["source-manifest.json"],
                        "build_inputs": manifest["build_inputs"]}, "release binding changed")
    require(manifest["builder_sha256"] == PIN["package_runtime.py"] and
            len(manifest["materials"]) == 698 and len(manifest["runtime_code"]) == 3,
            "fixture selection changed")
    return manifest


def child(argv: list[str], cwd: Path, *, expect: int = 0) -> dict:
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                            timeout=180, check=False, env={"PATH": os.environ.get("PATH", ""),
                                                            "HOME": str(cwd), "PYTHONDONTWRITEBYTECODE": "1"})
    require(result.returncode == expect, "child refusal: " + result.stderr[-500:])
    return json.loads(result.stdout if expect == 0 else result.stderr)


def validate_consumer(proposal: dict, applied: dict, packet: dict, status: dict) -> dict:
    target = proposal["targets"][0]["version_ref"]
    context = packet["context_packet"]
    require(packet["session_disposition"] == "closed-after-export", "session not closed")
    require(context["head"] == applied["transaction_digest"] == status["head"], "consumer HEAD changed")
    require(context["agent_session"]["payload"]["input_refs"][0] == target,
            "consumer used different Work version")
    require(context["context_view"]["source_epoch"] == status["head"], "consumer source epoch changed")
    require(context["project_state"]["node_id"] == status["current_project_state"]["node_id"],
            "consumer Project State changed")
    require(context["authority_effect"] == "none" and not context["short_memory_persisted"],
            "consumer claim changed")
    view = context["context_view"]
    lease = (datetime.fromisoformat(view["expires_at"].replace("Z", "+00:00")) -
             datetime.fromisoformat(view["generated_at"].replace("Z", "+00:00"))).total_seconds()
    require(119 <= lease <= 121, "Session lease is not bounded to 120 seconds")
    return {"work_version": target, "head": status["head"],
            "context_view": context["context_view"]["node_id"],
            "project_state": context["project_state"]["node_id"],
            "bounded_input_consumed": True, "session_lease_seconds": lease,
            "consumption_kind": "source-bound context packet read and checked; no subsequent action",
            "session_closed": True}


def run() -> dict:
    manifest = selected()
    with tempfile.TemporaryDirectory(prefix="cal-t29-continuity-") as directory:
        owned = Path(directory)
        stage = owned / "installed"
        stage.mkdir()
        workspace = stage / "workspace"
        source = HOST / "package_runtime.py"
        builder_bytes = checked(source, PIN["package_runtime.py"])
        # The stage child compiles the selected bytes passed on stdin. A
        # verify-then-path-import would reopen mutable source during startup.
        loader = ("import sys; p=sys.argv[1]; sys.argv=[p,*sys.argv[2:]]; "
                  "exec(compile(sys.stdin.buffer.read(),p,'exec'),"
                  "{'__name__':'__main__','__file__':p})")
        staged = subprocess.run([sys.executable, "-I", "-B", "-c", loader,
                                 str(source), "--context", str(stage)],
                                input=builder_bytes, cwd=ROOT, capture_output=True,
                                timeout=180, check=False)
        require(staged.returncode == 0, "fixture stage refused: " + staged.stderr[-500:].decode(errors="replace"))
        for name, digest in PIN.items():
            checked(HOST / name, digest)
        verifier = workspace / "implementation/lab-runtime/local-host/verify_package.py"
        check = subprocess.run([sys.executable, "-I", "-B", str(verifier), "--verify-context", str(stage)],
                               cwd=workspace, capture_output=True, text=True, timeout=180, check=False)
        require(check.returncode == 0, "installed fixture verification refused: " + check.stderr[-500:])
        for name, digest in manifest["runtime_code"].items():
            require(sha((workspace / name).read_bytes()) == digest, "installed executable changed")

        cli = workspace / "implementation/lab-runtime/v1/lab.py"
        state = owned / "state"
        state.mkdir(mode=0o700)
        store = state / "active-store"
        key = state / "owner.pem"
        pub = state / "owner.pub"
        proposal_file = state / "proposal.json"
        approval_file = state / "approval.json"
        process_count = 0
        def call(*args: str, store_path: Path = store, expect: int = 0) -> dict:
            nonlocal process_count
            process_count += 1
            # -s retains the installed script directory for its lab_runtime
            # package while excluding the user site and inherited PYTHONPATH.
            return child([sys.executable, "-s", "-B", str(cli), "--repo", str(workspace),
                          "--store", str(store_path), *map(str, args)], workspace, expect=expect)

        call("keygen", "--private", key, "--public", pub)
        initial = call("init", "--id", "t29-local-continuity", "--owner",
                       "principal:t29-local-fixture", "--public-key", pub)
        require(initial["sequence"] == 0 and not initial["recovery_required"], "genesis not clean")
        genesis = state / "genesis-copy"
        shutil.copytree(store, genesis, symlinks=False)
        require(call("verify", store_path=genesis)["transactions_replayed"] == 1,
                "saved genesis did not replay")
        call("example", "--id", "t29-local-work", "--out", proposal_file)
        proposal = json.loads(proposal_file.read_bytes())
        review = call("review", proposal_file)
        require(review["target_count"] == 1 and review["approval_required"], "Work review changed")
        call("authorize", proposal_file, "--private-key", key, "--out", approval_file)
        approval = json.loads(approval_file.read_bytes())
        altered = copy.deepcopy(proposal)
        altered["targets"][0]["record"]["name"] = "Changed after signature"
        changed = state / "changed-proposal.json"
        changed.write_text(json.dumps(altered))
        refusal = call("apply", changed, approval_file, expect=2)
        require(refusal["result"] == "BLOCKED" and
                refusal["error"] == "approval does not bind exact proposal, authority, scope and HEAD" and
                call("status")["head"] == initial["head"],
                "changed signed output altered HEAD")
        applied = call("apply", proposal_file, approval_file)
        status = call("status")
        replay = call("verify")
        require(status["sequence"] == 1 and status["head"] == applied["transaction_digest"]
                and replay["head"] == status["head"] and replay["transactions_replayed"] == 2,
                "restart replay lost admission")
        target = proposal["targets"][0]["version_ref"]
        packet = call("session", target, "--ttl", "120", "--context-only")
        consumed = validate_consumer(proposal, applied, packet, status)
        sentinel = state / "foreign-sentinel"
        sentinel.write_bytes(b"foreign-owned-residue\n")
        candidate = state / "retained-candidate"
        require(not candidate.exists() and genesis.is_dir() and store.is_dir(), "rollback target unsafe")
        store.rename(candidate)
        try:
            genesis.rename(store)
        except OSError:
            candidate.rename(store)
            raise
        restored = call("verify")
        restored_status = call("status")
        retained = call("verify", store_path=candidate)
        require(restored_status["sequence"] == 0 and restored_status["head"] == initial["head"]
                and restored["transactions_replayed"] == 1 and retained["head"] == applied["transaction_digest"]
                and retained["transactions_replayed"] == 2 and sentinel.read_bytes() == b"foreign-owned-residue\n",
                "generation rollback failed")
        outcome = {"schema_version": "lab-t29-installed-continuity/v1", "result": "PASS",
                   "fixture_manifest_sha256": PIN["source-manifest.json"],
                   "fixture_release_sha256": PIN["package-release.json"],
                   "installed_fixture_verified": True, "fresh_process_operations": process_count,
                   "signed_local_work_sequence": status["sequence"],
                   "signed_local_work_head": status["head"],
                   "changed_signed_proposal_refused": True, "fresh_restart_replay": True,
                   "consumption": consumed, "rolled_back_head": restored_status["head"],
                   "retained_candidate_replay_before_cleanup": True,
                   "foreign_residue_preserved": True, "original_admitted_operation": False,
                   "api40_installed_replay": False, "repository_authority_effect": "none",
                   "external_effects": 0, "local_t29_check_passed": True,
                   "original_scope_complete": False, "task_complete": False}
    require(not owned.exists(), "owned temp root remains")
    outcome["owned_temp_root_removed"] = True
    return outcome


if __name__ == "__main__":
    try:
        print(json.dumps(run(), sort_keys=True, indent=2))
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print("T29_REFUSED:" + str(error), file=sys.stderr)
        raise SystemExit(1)
