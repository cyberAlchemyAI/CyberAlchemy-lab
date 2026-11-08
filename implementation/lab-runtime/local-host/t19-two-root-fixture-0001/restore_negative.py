"""Exercise failed restore through the real extractor and compare whole trees."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import sys
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNNER_SHA = "fbf381eb77465f2d3a2bc8b54037aabbcdb1350ab40a496fbcbf71abccee679a"
RUN_RESULT_SHA = "877d357909e1a967a280241fcb705450ff0585178993a8cc1c955e9d21bfc4fd"
ARCHIVE_SHA = "020f2755bd2687003f15d93a49a1e3bd6a49d838e3efe1398d6731881edce448"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(value: bool, reason: str) -> None:
    if not value:
        raise ValueError(reason)


def selected_runner():
    path = HERE / "run.py"
    need(stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink(), "runner path changed")
    raw = path.read_bytes()
    need(sha(raw) == RUNNER_SHA, "runner bytes changed")
    spec = importlib.util.spec_from_loader("_cal_t19_first_runner", loader=None)
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(path)
    sys.modules[spec.name] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    need(sha(path.read_bytes()) == RUNNER_SHA, "runner changed during import")
    return module


def tree(root: Path) -> dict[str, str]:
    rows = {}
    for path in sorted(root.rglob("*")):
        mode = path.lstat().st_mode
        need(not stat.S_ISLNK(mode), "installed tree contains link")
        name = path.relative_to(root).as_posix()
        if stat.S_ISREG(mode):
            rows[name] = sha(path.read_bytes())
        elif stat.S_ISDIR(mode):
            rows[name + "/"] = "directory"
        else:
            raise ValueError("installed tree contains nonregular path")
    return rows


def run() -> dict:
    runner = selected_runner()
    first_raw = (HERE / "RUN-0001.json").read_bytes()
    need(sha(first_raw) == RUN_RESULT_SHA, "first terminal run changed")
    first = json.loads(first_raw)
    need(first["fixture_install_restore_passed"] is True and
         len(first["fresh_install_runs"]) == 2 and
         all(row["passed"] for row in first["fresh_install_runs"]) and
         first["restore_run"]["passed"] is True and
         first["installed_api40_service"] is False,
         "first bounded Docker result differs")
    package = runner.package_module()
    body = package.build()
    need(sha(body) == ARCHIVE_SHA, "selected archive changed")
    with tempfile.TemporaryDirectory(prefix="cal-t19-restore-negative-") as name:
        parent = Path(name)
        installed = parent / "installed"
        installed.mkdir(mode=0o700)
        installed_result = package.extract_verified(body, installed)
        need(installed_result["archive_sha256"] == ARCHIVE_SHA and
             installed_result["extracted_fixture_context_verified"] is True,
             "initial extraction differs")
        before = tree(installed)
        need(len(before) > 800, "whole installed-tree inventory missing")
        corrupted = body[:-1] + bytes([body[-1] ^ 1])
        need(sha(corrupted) != ARCHIVE_SHA, "corrupt control ineffective")
        try:
            package.extract_verified(corrupted, installed)
        except (ValueError, KeyError, OSError, AssertionError, zipfile.BadZipFile):
            pass
        else:
            raise ValueError("corrupt archive restore accepted")
        need(tree(installed) == before, "corrupt restore changed installed tree")
        try:
            package.extract_verified(body, installed)
        except ValueError as exc:
            need("nonempty or unsafe extraction root" in str(exc),
                 "occupied restore refused for a different reason")
        else:
            raise ValueError("occupied root overwritten")
        need(tree(installed) == before, "occupied restore changed installed tree")
        restored = parent / "restored"
        restored.mkdir(mode=0o700)
        restored_result = package.extract_verified(body, restored)
        need(restored_result["archive_sha256"] == ARCHIVE_SHA and
             tree(restored) == before, "clean restore bytes differ")
        result = {"schema_version": "lab-t19-restore-negative/v1",
                  "prior_six_journey_result_sha256": RUN_RESULT_SHA,
                  "archive_sha256": ARCHIVE_SHA,
                  "installed_tree_entries": len(before),
                  "installed_tree_digest": sha(json.dumps(before, sort_keys=True,
                                                       separators=(",", ":")).encode()),
                  "corrupt_archive_refused_by_extractor": True,
                  "occupied_root_refused_by_extractor": True,
                  "whole_tree_unchanged_after_refusals": True,
                  "clean_restore_whole_tree_equal": True,
                  "installed_api40_service": False,
                  "full_T19_complete": False,
                  "authority_effect": "none",
                  "runner_sha256": sha(Path(__file__).read_bytes())}
    result["owned_roots_removed"] = not parent.exists()
    need(result["owned_roots_removed"], "owned restore roots survived")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
