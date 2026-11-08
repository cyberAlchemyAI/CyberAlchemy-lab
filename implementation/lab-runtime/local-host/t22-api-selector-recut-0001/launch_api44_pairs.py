"""Execute the API44 runner from independently selected captured source bytes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
SELECTION = HERE / 'API44-HARNESS-SELECTION-0001.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(path, digest):
    path = Path(path)
    if (not path.is_absolute() or not path.is_relative_to(ROOT) or path.is_symlink() or
            any(parent.is_symlink() for parent in path.parents)):
        raise ValueError('selected harness origin differs')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 16 * 1024 * 1024:
            raise ValueError('selected harness file differs')
        chunks = []
        while block := os.read(fd, 1024 * 1024):
            chunks.append(block)
        raw = b''.join(chunks)
        after = os.fstat(fd)
        fresh = path.lstat()
        stamp = lambda value: (value.st_dev, value.st_ino, value.st_uid, value.st_mode,
                               value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if stamp(before) != stamp(after) or stamp(after) != stamp(fresh) or sha(raw) != digest:
            raise ValueError('selected harness bytes changed')
        return raw
    finally:
        os.close(fd)


def verify(selection, own_path):
    if (selection['schema_version'] != 'lab-T17-api44-harness-selection/v1-candidate' or
            selection['authority_effect'] != 'none' or len(selection['files']) != 8):
        raise ValueError('closed API44 harness selection differs')
    selected = {row['path']: row['sha256'] for row in selection['files']}
    if len(selected) != 8:
        raise ValueError('duplicate API44 harness row')
    own_name = own_path.relative_to(ROOT).as_posix()
    runner = HERE / 'run_api44_pairs.py'
    runner_name = runner.relative_to(ROOT).as_posix()
    if own_name not in selected or runner_name not in selected:
        raise ValueError('launcher or runner absent from selection')
    for name, digest in selected.items():
        path = Path(name)
        if path.is_absolute() or '..' in path.parts:
            raise ValueError('nonrelative harness selection row')
        capture(ROOT / path, digest)
    return selected[runner_name]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection-sha256', required=True)
    args = parser.parse_args()
    selected_raw = capture(SELECTION, args.selection_sha256)
    selection = json.loads(selected_raw)
    own = Path(__file__).resolve()
    runner_sha = verify(selection, own)
    runner = HERE / 'run_api44_pairs.py'
    runner_raw = capture(runner, runner_sha)
    namespace = {'__name__': '_cal_api44_captured_pairs_runner', '__file__': str(runner)}
    exec(compile(runner_raw, str(runner), 'exec', dont_inherit=True), namespace)
    code = namespace['main']()
    if capture(SELECTION, args.selection_sha256) != selected_raw:
        raise ValueError('harness release pin changed during run')
    verify(selection, own)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
