"""Project the public Source Docker tool to the fresh identity, without running it."""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'source-only-docker-0002'
TARGET = HERE / 'tool'
OLD_ROLE = 'docker-source-20261020-0001'
NEW_ROLE = 'docker-source-20261020-0002'
OLD_ID = 'R03-docker-source-20261020-0001'
NEW_ID = 'R03-docker-source-20261020-0002'
EXPECTED = {'preflight.py': (1, 0), 'source_once.py': (3, 3)}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def project():
    result = {}
    for name, counts in EXPECTED.items():
        raw = (BASE / name).read_bytes()
        text = raw.decode('utf-8')
        if (text.count(OLD_ROLE), text.count(OLD_ID)) != counts:
            raise ValueError('Source tool projection span differs: ' + name)
        projected = text.replace(OLD_ID, NEW_ID).replace(OLD_ROLE, NEW_ROLE).encode('utf-8')
        for level in (0, 2):
            compile(projected, '/tool/' + name, 'exec', optimize=level)
        result[name] = projected
    result['public-cut.json'] = (HERE / 'public-cut.json').read_bytes()
    result['capture-closure.json'] = (BASE / 'capture-closure.json').read_bytes()
    return result


def materialize():
    result = project()
    if TARGET.exists():
        raise ValueError('public tool projection already exists')
    TARGET.mkdir(mode=0o700)
    for name, raw in sorted(result.items()):
        (TARGET / name).write_bytes(raw)
    return {name: sha(raw) for name, raw in sorted(result.items())}


if __name__ == '__main__':
    import json, sys
    if sys.argv[1:] == ['--materialize-public']:
        print(json.dumps(materialize(), sort_keys=True))
    elif not sys.argv[1:]:
        print(json.dumps({name: sha(raw) for name, raw in sorted(project().items())},
                         sort_keys=True))
    else:
        raise SystemExit('only --materialize-public is supported')
