"""Observe owned fixture cleanup; retain selected build/evidence for review."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

T = Path(__file__).absolute().parent
R = T.parents[5]
E = R / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-02'
PREFIX = E.parent / 'LC-U01-02/python-bytecode-cache-disabled-0002'
fd = os.open(PREFIX, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
with os.fdopen(fd, 'rb') as stream:
    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode) or hashlib.sha256(stream.read(59)).hexdigest() != 'a5712f1655f68e6f8fe7cacbfb454dc0be0cd1ad8f22f1788fbad7b8adafae29':
        raise ValueError('cache prefix guard')
if os.environ.get('PYTHONPYCACHEPREFIX') != str(PREFIX) or not sys.flags.no_site or not sys.dont_write_bytecode:
    raise ValueError('guarded Python required')
clean = not any(E.glob('offline-build-*/tmp/member-fixture-*')) and not any(E.glob('reviewer-offline-build-*/tmp/member-fixture-*')) and not any(E.glob('owned-input-negative-*')) and not any(T.rglob('__pycache__'))
print(json.dumps({'schema_version': 'lab-case-command-result/v1', 'result': 'PASS' if clean else 'FAIL',
    'checks': 2, 'effect_state': 'owned-inert', 'cleanup': 'retained-owned'}))
raise SystemExit(0 if clean else 1)
