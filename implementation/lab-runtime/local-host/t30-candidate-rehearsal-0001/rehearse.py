"""Disposable T25 candidate import and fresh-process cold replay rehearsal."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import types

ROOT = Path(__file__).resolve().parents[4]
TASK = Path(__file__).resolve().parent
SOURCES = {
    "t25_package": (ROOT / "implementation/lab-runtime/local-host/t25-local-candidate-0001/package.py",
                    "891bc19939b719728039447519f0d127805dbca360df533f2459201b42efb4d7"),
    "t26_decision": (ROOT / "implementation/lab-runtime/local-host/t26-local-decision-state-0001/decision_state.py",
                     "9736123d3a5ca8d0ebc0d020426ae45514be91a27046ac4b6b4ffbceba8b7309"),
    "t27_import": (ROOT / "implementation/lab-runtime/local-host/t27-local-import-0001/local_import.py",
                   "24cb9ef326a841c995ac55d7df265a953557938f2e32596014900fd6bdcdf8b7"),
}
ARCHIVE_SHA = "020f2755bd2687003f15d93a49a1e3bd6a49d838e3efe1398d6731881edce448"
COLD_BOOTSTRAP = (
    "import hashlib,sys\n"
    "expected=sys.argv.pop(1)\n"
    "filename=sys.argv.pop(1)\n"
    "raw=sys.stdin.buffer.read()\n"
    "if hashlib.sha256(raw).hexdigest()!=expected: raise SystemExit('cold runner bytes differ')\n"
    "scope={'__name__':'__main__','__file__':filename}\n"
    "exec(compile(raw,filename,'exec'),scope)\n"
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_selected(name: str):
    path, expected = SOURCES[name]
    for ancestor in (path, *path.parents):
        if ancestor == ROOT.parent:
            break
        if ancestor.is_symlink():
            raise ValueError("selected source linked")
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("selected source nonregular")
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise ValueError("selected source changed")
    module = types.ModuleType("t30_selected_" + name)
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    if sha(path.read_bytes()) != expected:
        raise ValueError("selected source changed after load")
    return module


def selected_modules():
    return load_selected("t25_package"), load_selected("t26_decision"), load_selected("t27_import")


def cold_read(root: Path, expected_archive_sha: str):
    package, _, imported = selected_modules()
    reader = imported.LocalImporter(root)
    try:
        head, head_sha = reader.read_head()
        if head["sequence"] != 1 or head["bundle_digest"] != expected_archive_sha:
            raise ValueError("cold committed HEAD differs")
        body = imported._regular_at(reader._bundles_fd, f"{expected_archive_sha}.bin")
        if sha(body) != expected_archive_sha:
            raise ValueError("cold committed archive changed")
        replay = package.replay(body)
        if replay["archive_sha256"] != expected_archive_sha or replay["replayed_additions"] != 799:
            raise ValueError("cold candidate replay differs")
        return {"cold_head_sha256": head_sha, "cold_archive_sha256": sha(body),
                "cold_replayed_additions": replay["replayed_additions"]}
    finally:
        reader.close()


def run():
    package, decisions, imported = selected_modules()
    body = package.build()
    if sha(body) != ARCHIVE_SHA or package.replay(body)["task_complete"] is not False:
        raise ValueError("selected local candidate differs")
    with tempfile.TemporaryDirectory(prefix="cal-T30-candidate-") as name:
        parent = Path(name)
        store = parent / "store"
        store.mkdir(mode=0o700)
        foreign = parent / "foreign.bin"
        foreign.write_bytes(b"unrelated-sentinel")
        operator = imported.LocalImporter(store)
        try:
            _, before = operator.read_head()
            target = decisions.Target.from_bytes(member="fixture:whole-T25-candidate",
                                                 scope="local-import", base_digest=before,
                                                 bundle_digest=ARCHIVE_SHA, body=body)
            state = decisions.DecisionState()
            try:
                operator.import_decided_bundle(target=target, decision_state=state,
                                               body=body, expected_head_digest=before)
            except imported.ImportError as exc:
                if "not approved" not in str(exc):
                    raise
            else:
                raise ValueError("unapproved candidate was imported")
            if operator.read_head()[1] != before or list(operator.bundles.iterdir()):
                raise ValueError("unapproved candidate changed store")
            choice = decisions.Event("fixture:T30:approve-exact-local-candidate", target, "approve")
            if state.apply(choice, body=body) != "approved":
                raise ValueError("local fixture decision did not project")
            committed = operator.import_decided_bundle(target=target, decision_state=state,
                                                        body=body, expected_head_digest=before)
            if committed != {"idempotent": False, "head_digest": operator.read_head()[1],
                             "sequence": 1}:
                raise ValueError("local committed import differs")
            retry = operator.import_decided_bundle(target=target, decision_state=state,
                                                    body=body, expected_head_digest=before)
            if retry != {"idempotent": True, "head_digest": committed["head_digest"],
                          "sequence": 1}:
                raise ValueError("exact candidate retry differs")
            try:
                operator.import_decided_bundle(target=target, decision_state=state,
                                               body=body + b"x", expected_head_digest=before)
            except (imported.ImportError, decisions.DecisionError):
                pass
            else:
                raise ValueError("changed candidate bytes imported")
            operator.close()
            runner_path = TASK / "rehearse.py"
            if not stat.S_ISREG(runner_path.lstat().st_mode) or any(
                    p.is_symlink() for p in (runner_path, *runner_path.parents)):
                raise ValueError("cold runner path unsafe")
            runner_raw = runner_path.read_bytes()
            runner_sha = sha(runner_raw)
            child = subprocess.run([sys.executable, "-I", "-B", "-c", COLD_BOOTSTRAP,
                                    runner_sha, str(runner_path), "--cold-root", str(store),
                                    "--archive-sha", ARCHIVE_SHA, "--self-sha", runner_sha],
                                   input=runner_raw, cwd=ROOT, capture_output=True, timeout=180,
                                   env={"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"})
            if child.returncode != 0:
                raise ValueError("fresh-process cold replay refused")
            if not stat.S_ISREG(runner_path.lstat().st_mode) or sha(runner_path.read_bytes()) != runner_sha:
                raise ValueError("cold runner path changed")
            cold = json.loads(child.stdout)
            if cold["cold_head_sha256"] != committed["head_digest"]:
                raise ValueError("fresh-process HEAD differs")
            release = parent / "release"
            release.mkdir(mode=0o700)
            extraction = package.extract_verified(body, release)
            if (extraction["archive_sha256"] != ARCHIVE_SHA or
                    extraction["extracted_fixture_context_verified"] is not True or
                    extraction["installed_api40_replay"] is not False):
                raise ValueError("clean candidate fixture extraction differs")
            if foreign.read_bytes() != b"unrelated-sentinel":
                raise ValueError("foreign sentinel changed")
            return {"schema_version": "lab-t30-local-candidate-rehearsal/v1",
                    "archive_sha256": ARCHIVE_SHA, "initial_head_sha256": before,
                    "committed_head_sha256": committed["head_digest"],
                    "fresh_process_replay": cold,
                    "unapproved_refused": True, "changed_bytes_refused": True,
                    "exact_retry_idempotent": True, "foreign_sentinel_preserved": True,
                    "clean_fixture_extract_verified": True,
                    "fixture_decision_only": True, "authority_effect": "none",
                    "installed_api40_replay": False, "docker_startup_from_candidate": False,
                    "full_t30_release": False}
        finally:
            operator.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cold-root", type=Path)
    parser.add_argument("--archive-sha")
    parser.add_argument("--self-sha")
    args = parser.parse_args()
    if args.cold_root is not None:
        if (args.archive_sha != ARCHIVE_SHA or
                args.self_sha != sha((TASK / "rehearse.py").read_bytes())):
            raise ValueError("cold runner selection differs")
        print(json.dumps(cold_read(args.cold_root, args.archive_sha), sort_keys=True))
    elif args.archive_sha is None and args.self_sha is None:
        print(json.dumps(run(), sort_keys=True, indent=2))
    else:
        parser.error("cold root required with explicit archive and runner pins")


if __name__ == "__main__":
    main()
