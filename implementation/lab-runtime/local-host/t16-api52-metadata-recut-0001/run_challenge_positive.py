"""Byte-backed focused inherited-fixture replay for the API52 candidate."""

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
import json
import os
from pathlib import Path
import stat
import sys
import traceback
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v52-t16-metadata-current-0001'
SOURCE_SHA = '060b501c32bb9cc3292f0e2a3124a89770ab5f69c6a749a823c466660dc96020'
PROFILE_SHA = '5da736d675d92e9fc72b1a197eea27d449610b2be8c621075aec81380fcb9c12'
INVENTORY = ROOT / 'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
INVENTORY_SHA = 'bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3'
PACKAGE = '_cal_t16_api52_focused'
CASES = {
    'challenge-positive': ('test_challenge_api.py', 'CurrentChallenge',
                           'test_01_actual_challenge_proposal_preserves_exact_revision_and_original_bytes'),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def exact(path, expected=None):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('absolute closed selected path required')
    handles = []
    try:
        parent = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        handles.append(parent)
        for part in path.parts[1:-1]:
            parent = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            handles.append(parent)
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise ValueError('selected regular file required')
            blocks = []
            while block := os.read(fd, 1024 * 1024):
                blocks.append(block)
            after = os.fstat(fd)
            named = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
            if stamp(before) != stamp(after) or stamp(after) != stamp(named):
                raise ValueError('selected file changed during capture')
            raw = b''.join(blocks)
            if expected is not None and sha(raw) != expected:
                raise ValueError('selected file digest differs: ' + str(path))
            return raw
        finally:
            os.close(fd)
    finally:
        for handle in reversed(handles):
            os.close(handle)


class PinnedAPI(MetaPathFinder, Loader):
    def __init__(self, code):
        self.code = code
        self.loaded = []

    def find_spec(self, fullname, path=None, target=None):
        if fullname != PACKAGE and not fullname.startswith(PACKAGE + '.'):
            return None
        leaf = '__init__.py' if fullname == PACKAGE else fullname[len(PACKAGE) + 1:] + '.py'
        if leaf not in self.code:
            raise ImportError('unselected API52 module: ' + fullname)
        filename, _ = self.code[leaf]
        spec = ModuleSpec(fullname, self, origin=str(filename), is_package=fullname == PACKAGE)
        if fullname == PACKAGE:
            spec.submodule_search_locations = [str(API)]
        return spec

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        leaf = '__init__.py' if module.__name__ == PACKAGE else module.__name__[len(PACKAGE) + 1:] + '.py'
        filename, raw = self.code[leaf]
        module.__file__ = str(filename)
        exec(compile(raw, str(filename), 'exec', dont_inherit=True), module.__dict__)
        self.loaded.append(leaf)


def capture():
    manifest = json.loads(exact(API / 'source-manifest.json', SOURCE_SHA))
    if len(manifest['files']) != 208:
        raise ValueError('API52 source row count differs')
    prefix = API.relative_to(ROOT).as_posix() + '/'
    code = {}
    for row in manifest['files']:
        if row['path'].startswith(prefix) and row['path'].endswith('.py'):
            leaf = row['path'][len(prefix):]
            if '/' in leaf or leaf in code:
                raise ValueError('API52 module inventory differs')
            file = API / leaf
            code[leaf] = (file, exact(file, row['sha256']))
    if len(code) != 145 or not {'__init__.py', 'guard.py', 'protocol.py'} <= set(code):
        raise ValueError('selected executable closure differs')
    exact(API / 'contract-profile.json', PROFILE_SHA)
    exact(INVENTORY, INVENTORY_SHA)
    return manifest, code


def run(key, runner_sha):
    if key not in CASES:
        raise ValueError('unselected focused case')
    if sha(exact(Path(__file__).absolute())) != runner_sha:
        raise ValueError('focused runner digest differs')
    os.umask(0o077)
    out = HERE / 'working' / (key + '-RESULT.json')
    out.parent.mkdir(mode=0o700, exist_ok=True)
    if out.exists():
        raise ValueError('focused result already exists')
    selected_id = ':'.join(CASES[key][:2]) + '.' + CASES[key][2]
    inventory = json.loads(exact(INVENTORY, INVENTORY_SHA))
    if sum(selected_id in ids for ids in inventory['buckets'].values()) != 1:
        raise ValueError('focused test ID is not unique in inherited 345 inventory')
    started = utc()
    entry = exit_guard = source_unchanged = False
    failure = None
    result = None
    finder = None
    try:
        manifest, code = capture()
        if any(name == PACKAGE or name.startswith(PACKAGE + '.') for name in sys.modules):
            raise ValueError('ambient selected package present')
        finder = PinnedAPI(code)
        sys.meta_path.insert(0, finder)
        __import__(PACKAGE)
        guard = __import__(PACKAGE + '.guard', fromlist=['verify'])
        guard.verify(SOURCE_SHA)
        entry = True
        protocol = __import__(PACKAGE + '.protocol', fromlist=['Schemas'])
        protocol.Schemas(PROFILE_SHA)
        filename, classname, method = CASES[key]
        module = __import__(PACKAGE + '.' + Path(filename).stem, fromlist=['*'])
        module.SOURCE = SOURCE_SHA
        module.PROFILE = PROFILE_SHA
        cls = getattr(module, classname)
        suite = unittest.TestSuite([cls(method)])
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    except BaseException:
        failure = traceback.format_exc()
    finally:
        try:
            if entry:
                guard.verify(SOURCE_SHA)
                exit_guard = True
            manifest2, code2 = capture()
            source_unchanged = manifest2 == manifest and code2 == code
            if finder is not None:
                unexpected = [name for name in sys.modules if name == PACKAGE or name.startswith(PACKAGE + '.')
                              if name != PACKAGE and name[len(PACKAGE) + 1:] + '.py' not in finder.loaded]
                if unexpected:
                    raise ValueError('loaded API52 module escaped captured loader')
        except BaseException:
            failure = (failure or '') + traceback.format_exc()
    status = ('PASS' if failure is None and result is not None and result.testsRun == 1
              and result.wasSuccessful() and entry and exit_guard and source_unchanged else 'REFUSED')
    receipt = {
        'schema_version': 'lab-T16-API52-focused-inherited-fixture/v1',
        'selected_case_id': selected_id,
        'started_at_utc': started, 'ended_at_utc': utc(),
        'source_manifest_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
        'inventory_sha256': INVENTORY_SHA, 'runner_sha256': runner_sha,
        'entry_guard_pass': entry, 'exit_guard_pass': exit_guard,
        'source_unchanged_during_run': source_unchanged,
        'tests_run': None if result is None else result.testsRun,
        'failures': [] if result is None else [detail for _, detail in result.failures],
        'errors': [] if result is None else [detail for _, detail in result.errors],
        'skipped': [] if result is None else result.skipped,
        'failure': failure, 'status': status,
        'claim_ceiling': 'One focused inherited method only; not T15 or 345-method T16 qualification.',
    }
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(receipt, stream, sort_keys=True, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'status': status, 'case': selected_id, 'result': str(out)}, sort_keys=True))
    return status == 'PASS'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=tuple(CASES), required=True)
    parser.add_argument('--runner-sha256', required=True)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case, args.runner_sha256) else 1)
