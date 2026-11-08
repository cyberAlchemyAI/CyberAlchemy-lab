"""Separate current-Source8 Machine replay linked to the frozen API33 whole run."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
from unittest.mock import patch
import unittest


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v41-current-source8-0001'
API_SOURCE_SHA = '69c872681c53ff02ba5d38ef0f80d866d75f0b9e8c6b6d5d214b9adc2ba70961'
API_PROFILE_SHA = '18ed4a8a577679211ee5f530ea8148fc18cb0dd0a29ef16de73d6ea761eb9860'
MACHINE_METHOD_AST_SHA = 'ee77f861acde636814133cdaaba3905e86570f6802dff2049d38be793a760bb2'
V4 = ROOT / 'implementation/lab-runtime/local-host/source8-api30-rebind-0004/working/whole-classes-result-0001.json'
V4_SOURCE_SHA = 'e400703a2ace9ea1899d7abf15023632a83235e1e15f5459970b1ed8d12a37dd'
V4_API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-current-0001'
V4_CLASSES = {'test_custody_sessions': ('Sessions', 34),
              'run_session_checks': ('Sessions', 34),
              'test_current_controls': ('CurrentControls', 11),
              'test_termination_boundaries': ('TerminationBoundaries', 6),
              'test_machine_transport': ('MachineTransport', 14)}
V4_MODULE = '_cal_api30_current_source8_successor_0001'
V4_MACHINE_ID = V4_MODULE + '.test_machine_transport.MachineTransport.test_02_all_seven_public_read_operations_with_actual_Actor'
V4_HARNESS = {
    'implementation/lab-runtime/local-host/source8-api30-rebind-0004/run_whole.py': '03ef57c50c519375e99e656fcf885135f63f5b941ea295032ad6af8e3e170f0b',
    'implementation/lab-runtime/local-host/source8-api30-rebind-0004/timer_test.py': '787a94892aa60386ae18acc2c8d8112339f348c50b130c3c1dcf22e06dc5c6a1',
    'implementation/lab-runtime/local-host/source8-api30-rebind-0001/prepare_successor.py': '643bebfb0d9817ca5944d86a9a07172c4554d4c2ff2e7c4e1995e3c185a9f473',
    'implementation/lab-runtime/local-host/source8-api30-rebind-0001/test_prepare_successor.py': 'aeac98a34b17125f32f18fcdb773b0d915e50987d31349056183eea890c1f88a',
}
FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8'
FAMILY_SOURCE_SHA = '501e59318f2e0f504c4bd9cbf2c364e9901712cef33d785d67dd0a7107fa6a27'
FAMILY_CONTEXT_SHA = '9a7baaf2453bed90a67b7145dd02c21f6e72150759885358e18f643f34899ddd'
OLD_SOURCE = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/fresh-legacy-current-runtime-preparation-0009/instances/legacy-source8-20261018-b/source'
OLD_SOURCE_SHA = '270afe48263bd84ed76f542e196cdccbf922c0b4a90276098fb9fe513906f889'
OLD_PACKAGE_SHA = 'e46218f4e8e784d511c1cc1644853006b726a2114474323fa18122c8496f232f'
OLD_PERIOD_SHA = '4ce3a3c7a6a0a21c8ebb5720392faad0055f89b35de1e319d56a2e9cc40c8200'
MODULE = '_cal_api41_current_source8_machine_replay_0001'
METHOD = 'test_02_all_seven_public_read_operations_with_actual_Actor'
READER_ORIGIN_REFUSAL = 'actual independently selected Source8 reader code origin differs'


def sha(path: Path) -> str:
    if not path.is_relative_to(ROOT) or any(p.is_symlink() for p in (path, *path.parents) if p == ROOT or ROOT in p.parents):
        raise ValueError('selected input path has unselected origin: ' + str(path))
    if path.is_symlink() or not path.is_file():
        raise ValueError('selected input is missing or linked: ' + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(path: Path, expected: str) -> bytes:
    if not path.is_relative_to(ROOT) or any(p.is_symlink() for p in (path, *path.parents) if p == ROOT or ROOT in p.parents):
        raise ValueError('selected input path has unselected origin: ' + str(path))
    if path.is_symlink() or not path.is_file():
        raise ValueError('selected input is missing or linked: ' + str(path))
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('selected input bytes differ: ' + str(path))
    return raw


def verify_selected_code_rows() -> dict[str, tuple[Path, bytes]]:
    manifest = json.loads(exact(API / 'source-manifest.json', API_SOURCE_SHA))
    rows = manifest.get('files')
    if type(rows) is not list or len(rows) != 207:
        raise ValueError('API41 source-code row count differs')
    paths = [row.get('path') for row in rows]
    if (len(set(paths)) != len(paths)
            or any(type(path) is not str or Path(path).is_absolute() or '..' in Path(path).parts for path in paths)
            or {str((API / name).relative_to(ROOT)) for name in ('__init__.py', 'guard.py', 'source_bridge.py',
                                                                   'test_custody_sessions.py', 'test_machine_transport.py')} - set(paths)):
        raise ValueError('selected API41 executable code closure differs')
    code = {}
    prefix = str(API.relative_to(ROOT)) + '/'
    for row in rows:
        path = ROOT / row['path']
        raw = exact(path, row['sha256'])
        if row['path'].startswith(prefix) and path.suffix == '.py':
            name = path.name
            if name in code:
                raise ValueError('duplicate selected API41 Python module name')
            code[name] = (path, raw)
    if '__init__.py' not in code or 'guard.py' not in code or 'protocol.py' not in code:
        raise ValueError('selected API41 bootstrap code is missing')
    return code


class PinnedAPIFinder(MetaPathFinder, Loader):
    """Load API41 package modules from verified captured bytes, never reopen paths."""
    def __init__(self, name: str, code: dict[str, tuple[Path, bytes]]):
        self.name = name
        self.code = code

    def find_spec(self, fullname, path=None, target=None):
        if fullname != self.name and not fullname.startswith(self.name + '.'):
            return None
        leaf = '__init__.py' if fullname == self.name else fullname[len(self.name) + 1:] + '.py'
        if leaf not in self.code:
            raise ImportError('unselected API41 package module: ' + fullname)
        file, _ = self.code[leaf]
        is_package = fullname == self.name
        spec = ModuleSpec(fullname, self, origin=str(file), is_package=is_package)
        if is_package:
            spec.submodule_search_locations = [str(API)]
        return spec

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        leaf = '__init__.py' if module.__name__ == self.name else module.__name__[len(self.name) + 1:] + '.py'
        file, raw = self.code[leaf]
        module.__file__ = str(file)
        exec(compile(raw, str(file), 'exec'), module.__dict__)


def method_ast_sha() -> str:
    tree = ast.parse((API / 'test_machine_transport.py').read_text())
    classes = [item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == 'MachineTransport']
    if len(classes) != 1:
        raise ValueError('selected Machine class differs')
    methods = [item for item in classes[0].body if isinstance(item, ast.FunctionDef) and item.name == METHOD]
    if len(methods) != 1:
        raise ValueError('seven-operation Machine method differs')
    return hashlib.sha256(ast.dump(methods[0], include_attributes=False).encode()).hexdigest()


def expected_v4_ids() -> list[str]:
    exact(V4_API / 'source-manifest.json', V4_SOURCE_SHA)
    manifest = json.loads((V4_API / 'source-manifest.json').read_bytes())
    rows = {row['path']: row['sha256'] for row in manifest['files']}
    expected = []
    for filename, (class_name, count) in V4_CLASSES.items():
        path = V4_API / (filename + '.py')
        if rows.get(path.relative_to(ROOT).as_posix()) != sha(path):
            raise ValueError('frozen API33 selected test bytes differ')
        tree = ast.parse(path.read_text())
        classes = [item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == class_name]
        if len(classes) != 1:
            raise ValueError('frozen API33 test class differs')
        methods = sorted(item.name for item in classes[0].body
                         if isinstance(item, ast.FunctionDef) and item.name.startswith('test'))
        if len(methods) != count or len(set(methods)) != count:
            raise ValueError('frozen API33 test method inventory differs')
        expected.extend(V4_MODULE + '.' + filename + '.' + class_name + '.' + method
                        for method in methods)
    return expected


def prior_99(expected_result_sha: str) -> dict:
    if re.fullmatch('[0-9a-f]{64}', expected_result_sha) is None or sha(V4) != expected_result_sha:
        raise ValueError('externally reviewed frozen v4 result digest differs')
    value = json.loads(V4.read_bytes())
    ids = value.get('selected_case_ids')
    cases = value.get('case_rows')
    expected = expected_v4_ids()
    harness = value.get('harness_bindings')
    if (type(harness) is not list or len(harness) != len(V4_HARNESS)
            or {item.get('path'): item.get('sha256') for item in harness} != V4_HARNESS
            or any(sha(ROOT / path) != digest for path, digest in V4_HARNESS.items())):
        raise ValueError('frozen v4 runner/timer selection differs')
    appended_rows = value.get('current_source8_machine_case_rows')
    appended_errors = value.get('current_source8_machine_errors')
    appended_failures = value.get('current_source8_machine_failures')
    if value.get('result') == 'PASS':
        appended_exact = (appended_rows is not None and len(appended_rows) == 1
                          and appended_rows[0].get('test_id') == V4_MACHINE_ID
                          and appended_rows[0].get('result') == 'PASS'
                          and appended_errors == [] and appended_failures == [])
    else:
        expected_setup = 'setUpClass (' + V4_MODULE + '.test_machine_transport.MachineTransport)'
        appended_exact = (appended_failures == [] and type(appended_errors) is list
                          and len(appended_errors) == 1 and type(appended_errors[0]) is list
                          and len(appended_errors[0]) == 2
                          and appended_errors[0][0] in (V4_MACHINE_ID, expected_setup)
                          and 'CurrentFixtureReader' in appended_errors[0][1]
                          and type(appended_rows) is list
                          and (appended_rows == [] or (len(appended_rows) == 1
                              and appended_rows[0].get('test_id') == V4_MACHINE_ID
                              and appended_rows[0].get('result') == 'ERROR')))
    if (value.get('successor_manifest_sha256') != V4_SOURCE_SHA
            or value.get('tests_run') != 99
            or value.get('exact_whole_class_coverage') is not True
            or value.get('expired_original_negative_passed') is not True
            or value.get('current_legacy_machine_context_get_passed') is not True
            or value.get('wrong_origin_old_source_refused') is not True
            or value.get('harness_unchanged_during_run') is not True
            or value.get('source_unchanged_during_run') is not True
            or value.get('t06_operator_unchanged_during_run') is not True
            or value.get('stable_native_executable_unchanged_during_run') is not True
            or type(ids) is not list or ids != expected
            or type(cases) is not list or len(cases) != 99
            or [row.get('test_id') for row in cases] != expected
            or any(row.get('result') != 'PASS' for row in cases)
            or value.get('class_case_counts') != {name: row[1] for name, row in V4_CLASSES.items()}
            or value.get('errors') != [] or value.get('failures') != []
            or value.get('result') not in ('PASS', 'FAIL')
            or (value['result'] == 'PASS') != (value.get('current_source8_machine_context_get_passed') is True)
            or not appended_exact):
        raise ValueError('frozen API33 whole-case evidence is not 99 exact PASS cases')
    return {'path': V4.relative_to(ROOT).as_posix(), 'sha256': sha(V4),
            'source_manifest_sha256': V4_SOURCE_SHA, 'case_count': 99,
            'combined_v4_result': value.get('result'),
            'combined_v4_current_source8_machine_passed': value.get('current_source8_machine_context_get_passed')}


def selected_api():
    code = verify_selected_code_rows()
    exact(API / 'contract-profile.json', API_PROFILE_SHA)
    exact(FAMILY / 'source/source-manifest.json', FAMILY_SOURCE_SHA)
    exact(FAMILY / 'context/source-manifest.json', FAMILY_CONTEXT_SHA)
    if method_ast_sha() != MACHINE_METHOD_AST_SHA:
        raise ValueError('selected Machine test method changed')
    if any(name == MODULE or name.startswith(MODULE + '.') for name in sys.modules):
        raise ValueError('API41 Machine package was already loaded before selected code verification')
    finder = PinnedAPIFinder(MODULE, code)
    sys.meta_path.insert(0, finder)
    importlib.import_module(MODULE)
    guard = importlib.import_module(MODULE + '.guard')
    guard.verify(API_SOURCE_SHA)
    return importlib.import_module(MODULE + '.protocol').source


class OneResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.case = None
        self.start = None

    def startTest(self, test):
        super().startTest(test)
        self.start = time.monotonic()
        self.case = {'id': test.id(), 'started_at_utc': datetime.now(timezone.utc).isoformat(), 'result': 'RUNNING'}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.case['result'] = 'PASS'

    def addError(self, test, error):
        super().addError(test, error)
        if self.case is not None:
            self.case['result'] = 'ERROR'

    def addFailure(self, test, error):
        super().addFailure(test, error)
        if self.case is not None:
            self.case['result'] = 'FAIL'

    def stopTest(self, test):
        self.case['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
        self.case['monotonic_elapsed_seconds'] = round(time.monotonic() - self.start, 3)
        channel = getattr(test, 'channel', None)
        resource = getattr(test, 'resource', None)
        delivery = getattr(test, 'delivery_result', None)
        self.case['observed_expiry'] = {
            'reader_policy': channel.policy.get('expires_at') if channel is not None else None,
            'reader_context': channel.context.get('expires_at') if channel is not None else None,
            'context_delivery': delivery.get('expires_at') if isinstance(delivery, dict) else None,
            'session': resource.expires.isoformat() if resource is not None else None,
        }
        super().stopTest(test)


def write_result_once(output: dict, path: Path) -> None:
    parent = path.parent
    parent.mkdir(mode=0o700, exist_ok=True)
    raw = (json.dumps(output, indent=2, sort_keys=True) + '\n').encode()
    directory_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        info = os.fstat(directory_fd)
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o700):
            raise ValueError('Machine result directory is not owner-private and exact')
        fd = os.open(path.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=directory_fd)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def exact_reader_origin_refusal(callback) -> bool:
    try:
        callback()
    except ValueError as error:
        if str(error) != READER_ORIGIN_REFUSAL:
            raise
        return True
    raise ValueError('wrong Reader origin was accepted')


def run(expected_result_sha: str) -> dict:
    if os.environ.get('PYTHONDONTWRITEBYTECODE') != '1':
        raise ValueError('selected Python must not create unpinned bytecode')
    runner_sha = sha(Path(__file__))
    prior = prior_99(expected_result_sha)
    source = selected_api()
    old_period_path = OLD_SOURCE / 'packages/0001/period.json'
    exact(OLD_SOURCE / 'source-manifest.json', OLD_SOURCE_SHA)
    exact(OLD_SOURCE / 'packages/0001/manifest.json', OLD_PACKAGE_SHA)
    exact(old_period_path, OLD_PERIOD_SHA)
    old_period = json.loads(old_period_path.read_bytes())
    if datetime.fromisoformat(old_period['expires_at']) >= datetime.now(timezone.utc):
        raise ValueError('old source period has not yet expired')
    with source.replay_source(source.CURRENT_SOURCE8_NAME) as view:
        if not source.current_source8_view(view):
            raise ValueError('current Source8 view is not selected')
        reader = view.source8_context_producer.reader
        reader_module = sys.modules[type(reader).__module__]
        if source.reader_factory(view)() is not reader:
            raise ValueError('current reader factory did not select actual reader')
        with patch.object(reader_module, 'SelectedReader', object):
            wrong_class_refused = exact_reader_origin_refusal(lambda: source.reader_factory(view))
        with patch.object(reader_module, '__file__', '/tmp/unselected-current-reader.py'):
            wrong_origin_refused = exact_reader_origin_refusal(lambda: source.reader_factory(view))
        if source.reader_factory(view)() is not reader:
            raise ValueError('actual reader not restored after negative probes')
        try:
            reader.package(OLD_SOURCE_SHA, OLD_PACKAGE_SHA)
        except ValueError as error:
            if str(error) != 'independently selected new source/package differs':
                raise
            old_source_pin_refused = True
        else:
            raise ValueError('old expired source was accepted by current reader')
    session = __import__(MODULE + '.test_custody_sessions', fromlist=['Sessions'])
    machine = __import__(MODULE + '.test_machine_transport', fromlist=['MachineTransport'])
    current = __import__(MODULE + '.current_context_sessions', fromlist=['D', 'R'])
    session.PROFILE = API_PROFILE_SHA
    machine.PROFILE = API_PROFILE_SHA
    originals = (session.PUBLIC_SOURCE_NAME, session.D, session.R, machine.D)
    try:
        session.PUBLIC_SOURCE_NAME = source.CURRENT_SOURCE8_NAME
        session.D = current.D
        session.R = current.R
        machine.D = current.D
        selected = machine.MachineTransport(METHOD)
        expected_id = MODULE + '.test_machine_transport.MachineTransport.' + METHOD
        if selected.id() != expected_id:
            raise ValueError('selected Machine test identity differs')
        result = unittest.TextTestRunner(verbosity=2, resultclass=OneResult, failfast=True).run(unittest.TestSuite([selected]))
    finally:
        session.PUBLIC_SOURCE_NAME, session.D, session.R, machine.D = originals
    guard = __import__(MODULE + '.guard', fromlist=['verify'])
    guard.verify(API_SOURCE_SHA)
    verify_selected_code_rows()
    exact(API / 'source-manifest.json', API_SOURCE_SHA)
    exact(API / 'contract-profile.json', API_PROFILE_SHA)
    exact(FAMILY / 'source/source-manifest.json', FAMILY_SOURCE_SHA)
    exact(FAMILY / 'context/source-manifest.json', FAMILY_CONTEXT_SHA)
    output = {
        'schema': 'cal-API41-current-Source8-Machine-replay/v1',
        'result': 'PASS' if result.wasSuccessful() and result.testsRun == 1 and result.case and result.case['result'] == 'PASS' else 'FAIL',
        'api_source_manifest_sha256': API_SOURCE_SHA,
        'api_profile_sha256': API_PROFILE_SHA,
        'source8_family_source_manifest_sha256': FAMILY_SOURCE_SHA,
        'source8_family_context_manifest_sha256': FAMILY_CONTEXT_SHA,
        'prior_api33_99_case_result_binding': prior,
        'selected_method_ast_sha256': MACHINE_METHOD_AST_SHA,
        'test': result.case,
        'tests_run': result.testsRun,
        'errors': [(case.id(), error[-1500:]) for case, error in result.errors],
        'failures': [(case.id(), error[-1500:]) for case, error in result.failures],
        'wrong_reader_class_refused': wrong_class_refused,
        'wrong_reader_origin_refused': wrong_origin_refused,
        'old_source_pin_refused': old_source_pin_refused,
        'historical_source_period_expired': True,
        'expired_old_source_period_binding': {
            'path': old_period_path.relative_to(ROOT).as_posix(),
            'sha256': OLD_PERIOD_SHA,
            'expires_at': old_period['expires_at'],
        },
        'historical_source_binding': {'path': (OLD_SOURCE / 'source-manifest.json').relative_to(ROOT).as_posix(),
                                      'sha256': OLD_SOURCE_SHA},
        'historical_package_binding': {'path': (OLD_SOURCE / 'packages/0001/manifest.json').relative_to(ROOT).as_posix(),
                                       'sha256': OLD_PACKAGE_SHA},
        'authority_effect': 'none',
        'actual_owner_outcome': None,
        'claim_ceiling': 'One actual current Source8 Machine seven-read case linked to independently reviewed 99 API33 Session/Custody cases; no admission, contest outcome, publication, or historical Source5 qualification.',
        'runner_sha256': runner_sha,
        'runner_unchanged_during_run': sha(Path(__file__)) == runner_sha,
        'v4_result_unchanged_during_run': sha(V4) == prior['sha256'],
    }
    if not output['runner_unchanged_during_run'] or not output['v4_result_unchanged_during_run']:
        output['result'] = 'FAIL'
    path = HERE / 'working/current-source8-machine-result-0001.json'
    write_result_once(output, path)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--v4-result-sha256', required=True)
    value = run(parser.parse_args().v4_result_sha256)
    print(json.dumps({'result': value['result'], 'tests_run': value['tests_run']}))
    raise SystemExit(0 if value['result'] == 'PASS' else 1)
