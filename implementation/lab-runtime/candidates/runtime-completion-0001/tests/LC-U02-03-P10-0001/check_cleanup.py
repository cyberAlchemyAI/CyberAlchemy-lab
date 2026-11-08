"""Read-only accounting of the selected completed attempt; prior residue stays retained."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys

R = Path(__file__).absolute().parents[6]
E = R / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-03'
p = argparse.ArgumentParser()
p.add_argument('--work', type=Path, required=True)
p.add_argument('--label', required=True)
a = p.parse_args()
checks = 0
try:
    work = a.work.absolute()
    if work.parent != E or not work.name.startswith(('offline-build-', 'reviewer-offline-build-')):
        raise ValueError('owned work selection')
    if not a.label or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in a.label):
        raise ValueError('closed label')
    metadata = work.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid():
        raise ValueError('owned work type')
    checks += 1
    terminal_path = work / (a.label + '.json')
    fd = os.open(terminal_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > 1048576:
            raise ValueError('terminal type/bound')
        raw = stream.read(1048577)
        after = os.fstat(stream.fileno())
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        raise ValueError('terminal changed')
    terminal = json.loads(raw)
    if (terminal['returncode'] != 0 or terminal['timed_out'] or terminal['source_drift']
            or not terminal['child_reaped'] or not terminal['logs_within_accepted_bound']):
        raise ValueError('selected execution incomplete')
    checks += 1
    if terminal['environment']['TMPDIR'] != str(work / (a.label + '-scratch')):
        raise ValueError('selected exclusive scratch mismatch')
    for path in (work / (a.label + '-scratch'), work / (a.label + '-vectors')):
        before = path.lstat()
        if not stat.S_ISDIR(before.st_mode) or before.st_uid != os.getuid() or list(path.iterdir()):
            raise ValueError('selected scratch nonempty or substituted')
        after = path.lstat()
        if (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_dev, after.st_ino, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError('selected scratch changed')
        checks += 1
    print(json.dumps({'schema_version': 'lab-case-command-result/v1', 'result': 'PASS',
          'checks': checks, 'effect_state': 'none', 'cleanup': 'retained-owned'}))
except (OSError, ValueError, KeyError, TypeError):
    print(json.dumps({'schema_version': 'lab-case-command-result/v1', 'result': 'FAIL',
          'checks': checks, 'effect_state': 'none', 'cleanup': 'unknown'}))
    sys.exit(1)
