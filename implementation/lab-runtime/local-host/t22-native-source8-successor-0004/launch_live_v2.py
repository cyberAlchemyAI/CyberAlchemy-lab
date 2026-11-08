"""Load the preselected T22 runner and chain helpers from held exact bytes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SELECTION = HERE / 'RUNNER-SELECTION-0001.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def held(path, expected):
    if path.is_symlink() or any(parent.is_symlink() for parent in path.parents):
        raise ValueError('selected T22 runner path linked')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('selected T22 runner path not regular')
        size = os.fstat(fd).st_size
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(size + 1)
        if len(raw) != size:
            raise ValueError('selected T22 runner/helper length changed')
    finally:
        os.close(fd)
    if sha(raw) != expected:
        raise ValueError('selected T22 runner/helper bytes changed')
    return raw


def run():
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise ValueError('invoke with python3 -I -B')
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--runner-selection-sha256', required=True)
    selected, _ = parser.parse_known_args()
    selected_raw = held(SELECTION, selected.runner_selection_sha256)
    selection = json.loads(selected_raw)
    if selection['schema_version'] != 'lab-T22-native-session-runner-selection/v1':
        raise ValueError('selected T22 runner protocol differs')
    paths = {}
    for role in ('launch', 'runner', 'verify_work', 'seal_chain'):
        path = ROOT / selection[role + '_path']
        if path.parent != HERE:
            raise ValueError('selected T22 runner/helper outside owned package')
        paths[role] = (path, held(path, selection[role + '_sha256']))
    if paths['launch'][0] != Path(__file__).resolve():
        raise ValueError('selected T22 launcher identity differs')
    for role in ('verify_work', 'seal_chain'):
        path, raw = paths[role]
        module = types.ModuleType(role)
        module.__file__ = str(path)
        sys.modules[role] = module
        exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    path, raw = paths['runner']
    scope = {'__name__': '__main__', '__file__': str(path), '__package__': None,
             '_HELD_RUNNER_SELECTION': selected_raw}
    exec(compile(raw, str(path), 'exec', dont_inherit=True), scope)


if __name__ == '__main__':
    run()
