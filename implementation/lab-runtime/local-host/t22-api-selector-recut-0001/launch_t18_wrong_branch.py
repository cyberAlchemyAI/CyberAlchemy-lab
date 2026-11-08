"""Launch a byte-captured, closed wrong-branch composite handshake probe."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
SELECTION = HERE / 'T18-WRONG-BRANCH-SELECTION-0001.json'
EXPECTED = frozenset({
    'implementation/lab-runtime/local-host/t22-api-selector-recut-0001/launch_t18_wrong_branch.py',
    'implementation/lab-runtime/local-host/t22-api-selector-recut-0001/run_api45_revision2_wrong_branch.py',
    'implementation/lab-runtime/local-host/t22-api-selector-recut-0001/API45R2-HARNESS-SELECTION-0001.json',
    'implementation/lab-runtime/local-host/t22-api-selector-recut-0001/RUN-API45R2-PAIRS-0001.json',
    'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api45-t17-0002/revision-0001/driver-selection.json',
    'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api45-t17-0002/revision-0001/drive_operator.py',
})


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(path, digest):
    path = Path(path)
    if not path.is_absolute() or not path.is_relative_to(ROOT) or any(p.is_symlink() for p in path.parents):
        raise ValueError('T18 selected origin differs')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 16 * 1024 * 1024:
            raise ValueError('T18 selected file differs')
        raw = b''
        while block := os.read(fd, 1024 * 1024):
            raw += block
        after = os.fstat(fd)
        fresh = path.lstat()
        stamp = lambda v: (v.st_dev, v.st_ino, v.st_uid, v.st_mode, v.st_size, v.st_mtime_ns, v.st_ctime_ns)
        if stamp(before) != stamp(after) or stamp(after) != stamp(fresh) or sha(raw) != digest:
            raise ValueError('T18 selected bytes changed')
        return raw
    finally:
        os.close(fd)


def verify(value, own):
    if (value['schema_version'] != 'lab-T18-api45r2-wrong-branch-selection/v1-candidate' or
            value['authority_effect'] != 'none' or len(value['files']) != len(EXPECTED)):
        raise ValueError('T18 closed selection differs')
    selected = {row['path']: row['sha256'] for row in value['files']}
    if set(selected) != EXPECTED or own.relative_to(ROOT).as_posix() not in selected:
        raise ValueError('T18 selected file set differs')
    for name, digest in selected.items():
        capture(ROOT / name, digest)
    return selected['implementation/lab-runtime/local-host/t22-api-selector-recut-0001/run_api45_revision2_wrong_branch.py']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection-sha256', required=True)
    args = parser.parse_args()
    selected_raw = capture(SELECTION, args.selection_sha256)
    selected = json.loads(selected_raw)
    own = Path(__file__).resolve()
    runner_sha = verify(selected, own)
    runner_path = HERE / 'run_api45_revision2_wrong_branch.py'
    raw = capture(runner_path, runner_sha)
    namespace = {'__name__': '_t18_selected_wrong_branch', '__file__': str(runner_path)}
    exec(compile(raw, str(runner_path), 'exec', dont_inherit=True), namespace)
    result = namespace['main']()
    if capture(SELECTION, args.selection_sha256) != selected_raw:
        raise ValueError('T18 selection changed during run')
    verify(selected, own)
    return result


if __name__ == '__main__':
    raise SystemExit(main())
