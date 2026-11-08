"""Copy the exact pinned public native runtime into a disjoint clean install."""

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SUPPORT = ROOT / "product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001"
SELECTION = ROOT / "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json"
ORIGINAL = SUPPORT / "installations/0004"
sys.path.insert(0, str(SUPPORT))
import closure  # noqa: E402


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def install(destination):
    destination = Path(destination)
    parent = destination.parent
    require(destination.is_absolute() and not destination.exists() and not destination.is_symlink() and
            parent.is_dir() and not parent.is_symlink() and
            not destination.resolve().is_relative_to(ROOT.resolve()), "CLEAN_INSTALL_ORIGIN_REFUSED")
    meta = parent.stat()
    require(meta.st_uid == os.getuid() and stat.S_IMODE(meta.st_mode) == 0o700,
            "CLEAN_INSTALL_PARENT_OWNER_MODE_REFUSED")
    selected, raw_selection = closure.load_selection(SELECTION, sha(SELECTION.read_bytes()))
    expected = closure.installed_files(selected)
    require(len(expected) == 1010, "CLEAN_INSTALL_SELECTION_COUNT_REFUSED")
    destination.mkdir(mode=0o700)
    for relative, row in sorted(expected.items()):
        source = ORIGINAL / relative
        require(source.is_file() and not source.is_symlink() and
                not any(p.is_symlink() for p in source.parents),
                "CLEAN_INSTALL_INPUT_ORIGIN_REFUSED " + relative)
        raw = source.read_bytes()
        require(sha(raw) == row["sha256"] and len(raw) == row["size_bytes"] and
                stat.S_IMODE(source.stat().st_mode) == row["mode"],
                "CLEAN_INSTALL_INPUT_BYTES_REFUSED " + relative)
        target = destination / relative
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, row["mode"])
        with os.fdopen(fd, "wb") as stream:
            require(stream.write(raw) == len(raw), "CLEAN_INSTALL_SHORT_WRITE")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(target, row["mode"])
    original_receipt = ORIGINAL / "installation.json"
    original_raw = original_receipt.read_bytes()
    observed = destination.stat()
    identity = [observed.st_dev, observed.st_ino, observed.st_uid, stat.S_IMODE(observed.st_mode)]
    receipt = {"schema": "cal-clean-installed-native-runtime/v1", "identity": identity,
               "selection_sha256": sha(raw_selection), "file_count": len(expected),
               "original_installation_receipt": {
                   "path": original_receipt.relative_to(ROOT).as_posix(),
                   "sha256": sha(original_raw)},
               "reason": "Exact copied public payload excludes unselected generated pycache files."}
    raw = json.dumps(receipt, sort_keys=True, indent=2).encode() + b"\n"
    path = destination / "installation.json"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        require(stream.write(raw) == len(raw), "CLEAN_INSTALL_RECEIPT_SHORT_WRITE")
        stream.flush()
        os.fsync(stream.fileno())
    closure.verify_installed(destination, selected)
    return {"destination": str(destination), "identity": identity,
            "receipt_sha256": sha(raw), "files": len(expected)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(install(args.destination), sort_keys=True))
