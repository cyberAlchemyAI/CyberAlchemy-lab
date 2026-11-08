"""Static Source controller projection for the persistent successor.

The projected file unconditionally refuses both effect entrypoints. It is a
review target, not a dispatched Docker controller.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'source-only-docker-0006/controller.py'
TARGET = HERE / 'source_controller.py'
TOOL = HERE / 'tool'
ATTEMPT = ('/home/vlad_/.local/state/cyberalchemy-lab/'
           'context-successor-20261020-0001/source-attempt')
NAME = 'cal-source-only-20261020-0002-successor1'
OLD_TOOL = '/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/source-only-docker-0002'
OLD_ATTEMPT = '/tmp/cal-source-only-dev-20261020-0001-exact1'
OLD_NAME = 'cal-source-only-20261020-0001-0006'
OLD_FREEZE = '68bb30c1969fb07909f58d87907f821a6bdc59a5ba659a831bc2424dae6f381d'
OLD_ROLE = 'docker-source-20261020-0001'
NEW_ROLE = 'docker-source-20261020-0002'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def project():
    raw = BASE.read_bytes()
    text = raw.decode('utf-8')
    new_freeze = sha((TOOL / 'freeze.json').read_bytes())
    replacements = (
        (OLD_TOOL, str(TOOL), 1),
        (OLD_ATTEMPT, ATTEMPT, 1),
        (OLD_NAME, NAME, 1),
        (OLD_FREEZE, new_freeze, 1),
        (OLD_ROLE, NEW_ROLE, 5),
    )
    for old, new, count in replacements:
        if text.count(old) != count or old == new:
            raise ValueError('Source controller projection span differs: ' + old)
        text = text.replace(old, new)
    for needle in ('def run() -> dict:\n', 'def recover_consumed() -> dict:\n'):
        if text.count(needle) != 1:
            raise ValueError('Source effect entrypoint span differs')
        text = text.replace(needle, needle +
                            '    raise RuntimeError("EFFECT_DISABLED_PENDING_SUCCESSOR_REVIEW")\n', 1)
    projected = text.encode('utf-8')
    for level in (0, 2):
        compile(projected, str(TARGET), 'exec', optimize=level)
    return projected


def materialize():
    raw = project()
    if TARGET.exists():
        raise ValueError('projected controller already exists')
    TARGET.write_bytes(raw)
    return sha(raw)


if __name__ == '__main__':
    import json, sys
    if sys.argv[1:] == ['--materialize-public']:
        result = {'status': 'EFFECT_DISABLED_CONTROLLER_MATERIALIZED',
                  'sha256': materialize()}
    elif not sys.argv[1:]:
        result = {'status': 'EFFECT_DISABLED_CONTROLLER_PROJECTION',
                  'sha256': sha(project())}
    else:
        raise SystemExit('only --materialize-public is supported')
    print(json.dumps(result, sort_keys=True))
