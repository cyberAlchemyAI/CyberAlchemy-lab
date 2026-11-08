"""Fresh-process whole-class inherited regression worker for selected API53 bytes."""

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
import json
import os
from pathlib import Path
import re
import stat
import sys
import traceback
import unittest

sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v53-t16-challenge-source-0001'
INVENTORY = ROOT / 'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
INVENTORY_SHA = 'bd83d446316e30a912616eb55552ae2935305b206c6400c8e067501f0912f3f3'
SOURCE_SHA = '7944431236ce9437516104b33ed04024994e0d9d45a2c2152eacf71612fd09ff'
PROFILE_SHA = '7480e7bf7d848a16d50bf7f56d6c4a24bd6175b0fa61d35fa796f9bf76c99f7d'
PACKAGE = '_cal_t16_api53_serial'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def exact(path, expected=None):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('selected path is not absolute and closed')
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
                raise ValueError('selected file is not regular')
            blocks = []
            while block := os.read(fd, 1024 * 1024):
                blocks.append(block)
            after = os.fstat(fd)
            attached = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
            stamp = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
            if stamp(before) != stamp(after) or stamp(after) != stamp(attached):
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
            raise ImportError('unselected API53 module: ' + fullname)
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
    if len(manifest['files']) != 210:
        raise ValueError('API53 manifest row count differs')
    prefix = API.relative_to(ROOT).as_posix() + '/'
    code = {}
    for row in manifest['files']:
        if row['path'].startswith(prefix) and row['path'].endswith('.py'):
            leaf = row['path'][len(prefix):]
            if '/' in leaf or leaf in code:
                raise ValueError('API53 module inventory differs')
            file = API / leaf
            code[leaf] = (file, exact(file, row['sha256']))
    if len(code) != 145 or not {'__init__.py', 'guard.py', 'protocol.py'} <= set(code):
        raise ValueError('selected executable closure differs')
    exact(API / 'contract-profile.json', PROFILE_SHA)
    return code


def terminalize(expected, observed, fixture_errors, tests_run, failure, at_utc):
    """Represent every selected ID, without calling an unrun method executed."""
    got = [row['id'] for row in observed]
    if len(got) != len(set(got)) or set(got) - set(expected):
        raise ValueError('actual case ID set differs')
    missing = set(expected) - set(got)
    cause = ('SETUP-ERROR' if fixture_errors and tests_run == 0 else
             'FIXTURE-INTERRUPTED' if fixture_errors else
             'WORKER-INTERRUPTED' if failure else 'NOT-RUN')
    by_id = {row['id']: row for row in observed}
    for identity in missing:
        by_id[identity] = {'id': identity, 'result': cause, 'executed': False,
                           'started_at_utc': None, 'ended_at_utc': at_utc}
    rows = [by_id[identity] for identity in expected]
    exact = len(rows) == len(set(row['id'] for row in rows)) == len(expected)
    executed = exact and tests_run == len(expected) and all(row['executed'] for row in rows)
    return rows, exact, executed


def run(bucket, runner_sha, run_id):
    if sha(exact(Path(__file__).absolute())) != runner_sha:
        raise ValueError('runner selected digest differs')
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,31}', run_id):
        raise ValueError('closed run identity required')
    inventory = json.loads(exact(INVENTORY, INVENTORY_SHA))
    if bucket not in inventory['buckets']:
        raise ValueError('unknown exact class bucket')
    expected = inventory['buckets'][bucket]
    safe = bucket.replace(':', '-').replace('.', '-')
    work = HERE / 'working' / run_id
    work.mkdir(mode=0o700, parents=True, exist_ok=True)
    if work.is_symlink() or not work.is_dir():
        raise ValueError('unsafe owned worker result directory')
    result_path = work / (safe + '-RESULT.json')
    events_path = work / (safe + '-EVENTS.jsonl')
    if result_path.exists() or events_path.exists():
        raise ValueError('bucket result already exists')
    os.umask(0o077)
    events_fd = os.open(events_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    events_stream = os.fdopen(events_fd, 'w')
    def event(value):
        events_stream.write(json.dumps({'at_utc': now(), **value}, sort_keys=True) + '\n')
        events_stream.flush(); os.fsync(events_stream.fileno())
    event({'phase': 'start', 'bucket': bucket, 'pid': os.getpid(), 'expected_count': len(expected)})
    cases = []; fixture_errors = []; entry = False; exit_guard = False; failure = None; tests_run = 0
    start = now()
    try:
        code = capture()
        if any(name == PACKAGE or name.startswith(PACKAGE + '.') for name in sys.modules):
            raise ValueError('ambient selected package present')
        finder = PinnedAPI(code); sys.meta_path.insert(0, finder)
        __import__(PACKAGE)
        guard = __import__(PACKAGE + '.guard', fromlist=['verify'])
        guard.verify(SOURCE_SHA)
        entry = True
        event({'phase': 'entry-guard-pass', 'captured_api_modules': len(code)})
        protocol = __import__(PACKAGE + '.protocol', fromlist=['Schemas'])
        protocol.Schemas(PROFILE_SHA)
        classes = {item.rsplit('.', 1)[0] for item in expected}
        if len(classes) != 1:
            raise ValueError('bucket must be exactly one whole class')
        name = next(iter(classes))
        filename, classname = name.split(':', 1)
        selected = __import__(PACKAGE + '.' + Path(filename).stem, fromlist=['*'])
        cls = getattr(selected, classname)
        if not issubclass(cls, unittest.TestCase):
            raise ValueError('selected class is not unittest.TestCase')
        helper = __import__(PACKAGE + '.export_test_base', fromlist=['*'])
        fixtures = [selected, helper]
        if filename == 'test_machine_transport.py':
            fixtures.append(__import__(PACKAGE + '.test_custody_sessions', fromlist=['*']))
        for fixture in fixtures:
            fixture.SOURCE = SOURCE_SHA
            fixture.PROFILE = PROFILE_SHA
        suite = unittest.TestSuite()
        identities = {}
        for ident in expected:
            method = ident.rsplit('.', 1)[1]
            test = cls(method)
            identities[test.id()] = ident
            suite.addTest(test)
        if len(identities) != len(expected) or suite.countTestCases() != len(expected):
            raise ValueError('selected whole-class count differs')
        class Result(unittest.TextTestResult):
            active = {}
            def startTest(self, test):
                super().startTest(test)
                row = {'id': identities[test.id()], 'result': 'PASS',
                       'executed': True, 'started_at_utc': now()}
                self.active[test.id()] = row
                event({'phase': 'case-start', 'id': row['id']})
            def _bad(self, test, err, result):
                row = self.active.get(test.id())
                value = {'result': result, 'detail': self._exc_info_to_string(err, test)}
                if row is None: fixture_errors.append({'fixture': test.id(), **value})
                else: row.update(value)
            def addFailure(self, test, err):
                super().addFailure(test, err); self._bad(test, err, 'FAIL')
            def addError(self, test, err):
                super().addError(test, err); self._bad(test, err, 'ERROR')
            def addSkip(self, test, reason):
                super().addSkip(test, reason)
                row = self.active.get(test.id())
                if row is None: fixture_errors.append({'fixture': test.id(), 'result': 'SKIP', 'detail': reason})
                else: row.update(result='SKIP', detail=reason)
            def addExpectedFailure(self, test, err):
                super().addExpectedFailure(test, err); self._bad(test, err, 'EXPECTED-FAILURE')
            def addUnexpectedSuccess(self, test):
                super().addUnexpectedSuccess(test)
                self.active[test.id()].update(result='UNEXPECTED-SUCCESS')
            def addSubTest(self, test, subtest, err):
                super().addSubTest(test, subtest, err)
                if err is not None: self._bad(test, err, 'SUBTEST-FAIL')
            def stopTest(self, test):
                row = self.active.pop(test.id())
                row['ended_at_utc'] = now()
                cases.append(row)
                event({'phase': 'case-terminal', **row})
                super().stopTest(test)
        result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
        tests_run = result.testsRun
    except BaseException:
        failure = traceback.format_exc()
        event({'phase': 'worker-exception', 'detail': failure})
    finally:
        try:
            if entry:
                guard.verify(SOURCE_SHA)
                exact(INVENTORY, INVENTORY_SHA)
                exact(API / 'source-manifest.json', SOURCE_SHA)
                exact(API / 'contract-profile.json', PROFILE_SHA)
                for filename, raw in code.values(): exact(filename, sha(raw))
                loaded = set(finder.loaded)
                for name in sys.modules:
                    if name.startswith(PACKAGE + '.'):
                        leaf = name[len(PACKAGE) + 1:] + '.py'
                        if leaf not in loaded or leaf not in code:
                            raise ValueError('selected API module escaped captured loader')
                exit_guard = True
        except BaseException:
            failure = (failure or '') + '\nEXIT GUARD:\n' + traceback.format_exc()
    try:
        completed, exact_cases, all_executed = terminalize(
            expected, cases, fixture_errors, tests_run, failure, now())
    except BaseException:
        failure = (failure or '') + '\nTERMINAL ROWS:\n' + traceback.format_exc()
        completed = cases
        exact_cases = all_executed = False
    for row in completed:
        if not row['executed']:
            event({'phase': 'case-unexecuted-terminal', **row})
    cases = completed
    passed = (entry and exit_guard and failure is None and not fixture_errors and all_executed
              and all(row['result'] == 'PASS' for row in cases))
    event({'phase': 'worker-terminal', 'result': 'PASS' if passed else 'FAIL', 'tests_run': tests_run})
    events_stream.close()
    value = {
        'schema_version': 'lab-t16-api53-serial-bucket/v1', 'result': 'PASS' if passed else 'FAIL',
        'bucket': bucket, 'selected_ids': expected, 'cases': cases, 'fixture_errors': fixture_errors,
        'run_id': run_id,
        'tests_run': tests_run, 'exact_case_set': exact_cases, 'all_methods_executed': all_executed,
        'entry_guard_passed': entry,
        'exit_guard_passed': exit_guard, 'execution_error': failure,
        'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
        'inventory_sha256': INVENTORY_SHA, 'runner_sha256': runner_sha,
        'events_sha256': sha(exact(events_path)),
        'started_at_utc': start, 'ended_at_utc': now(),
        'fresh_process_pid': os.getpid(), 'provisional_current_cut': True,
        't15_final_freeze_selected': False, 't16_full_qualification': False,
        'authority_effect': 'none',
    }
    result_fd = os.open(result_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(result_fd, 'w') as stream:
        json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')
        stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'result': value['result'], 'bucket': bucket, 'tests_run': tests_run,
                      'result_sha256': sha(exact(result_path))}), flush=True)
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--runner-sha256', required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    expected = args.runner_sha256
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError('external runner byte selection absent')
    return run(args.bucket, expected, args.run_id)


if __name__ == '__main__':
    raise SystemExit(main())
