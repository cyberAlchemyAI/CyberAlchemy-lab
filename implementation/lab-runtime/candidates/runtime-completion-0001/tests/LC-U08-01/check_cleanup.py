"""Read-only owned scratch checks; evidence/build artifacts remain retained."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys

R = Path(__file__).absolute().parents[6]
E = R / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U08-01'
p = argparse.ArgumentParser()
p.add_argument('--work', type=Path, required=True)
a = p.parse_args()
work = a.work.absolute()
checks = 0
try:
    if work.parent != E or not work.name.startswith(('offline-build-', 'reviewer-offline-build-')):
        raise ValueError('owned build root')
    root_stat = work.lstat()
    if not stat.S_ISDIR(root_stat.st_mode) or root_stat.st_uid != os.getuid():
        raise ValueError('owned build directory identity')
    checks += 1
    scratch = work / 'tmp'
    before = scratch.lstat()
    if not stat.S_ISDIR(before.st_mode) or before.st_uid != os.getuid() or list(scratch.iterdir()):
        raise ValueError('remaining or substituted fixture scratch')
    after = scratch.lstat()
    if (before.st_dev, before.st_ino, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_mtime_ns):
        raise ValueError('scratch changed')
    checks += 1
    if any(entry.name.startswith('c01-fixture-') for entry in E.iterdir()):
        raise ValueError('remaining canonical-contract scratch')
    checks += 1
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS','checks':checks,'effect_state':'none','cleanup':'retained-owned'}))
except (OSError, ValueError):
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'FAIL','checks':checks,'effect_state':'none','cleanup':'unknown'}))
    sys.exit(1)
