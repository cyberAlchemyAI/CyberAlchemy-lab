"""Disjoint continuation after the frozen 68/68 Session PASS and case69 refusal.

The historical Source5 constructor refuses at its selected environment guard.
The selected policy's independent period guard is exercised separately with
source preflight disabled; this never claims a new grant was made.
"""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
PREV = HERE.with_name('source8-api30-rebind-0004')
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-current-0001'
OLD_RESULT = PREV / 'working/whole-classes-result-0001.json'
OLD_SHA = '90c3c6ca270031930351485ff9a70660240d55b2186393abe46c32f55d26427f'
API_SHA = 'e400703a2ace9ea1899d7abf15023632a83235e1e15f5459970b1ed8d12a37dd'
PROFILE_SHA = 'c86a04159a99d607f15f42078ae64b108ef5007e121f830d54174f0167b8813a'
OLD_RUNNER_SHA = '03ef57c50c519375e99e656fcf885135f63f5b941ea295032ad6af8e3e170f0b'
ORIGINAL_CONTROL_SHA = 'b9222c75c10c41410643a25a3bd5a5c29de8727943d09f8ddc96145b71dc0e0a'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select():
    if (sha(OLD_RESULT), sha(API / 'source-manifest.json'), sha(API / 'contract-profile.json'),
            sha(PREV / 'run_whole.py')) != (OLD_SHA, API_SHA, PROFILE_SHA, OLD_RUNNER_SHA):
        raise ValueError('frozen T02 predecessor selection differs')
    old = json.loads(OLD_RESULT.read_bytes())
    first = old['selected_case_ids'][:68]
    rows = old['case_rows']
    if (old['tests_run'] != 69 or len(rows) != 69 or
            [row['test_id'] for row in rows[:68]] != first or
            any(row['result'] != 'PASS' for row in rows[:68]) or
            rows[68]['test_id'] != old['selected_case_ids'][68] or rows[68]['result'] != 'FAIL' or
            'selected R02 participation environment differs' not in old['failures'][0][1] or
            not all(old[k] for k in ('source_unchanged_during_run', 'harness_unchanged_during_run',
                                     't06_operator_unchanged_during_run',
                                     'stable_native_executable_unchanged_during_run'))):
        raise ValueError('frozen 68-case predecessor evidence differs')
    manifest = json.loads((API / 'source-manifest.json').read_bytes())
    for row in manifest['files']:
        path = ROOT / row['path']
        if not path.is_file() or path.is_symlink() or sha(path) != row['sha256']:
            raise ValueError('current API33 selected code byte differs')
    name = '_cal_api30_current_source8_successor_0001'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py',
                                                 submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    return name, old, manifest


class Outcome(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = []
        self._start = {}

    def startTest(self, test):
        super().startTest(test)
        self._start[test.id()] = (datetime.now(timezone.utc).isoformat(), time.monotonic())

    def stopTest(self, test):
        at, stamp = self._start.pop(test.id())
        status = 'FAIL' if any(case.id() == test.id() for case, _ in self.failures) else (
            'ERROR' if any(case.id() == test.id() for case, _ in self.errors) else 'PASS')
        self.rows.append({'test_id': test.id(), 'result': status, 'started_at_utc': at,
                          'completed_at_utc': datetime.now(timezone.utc).isoformat(),
                          'monotonic_elapsed_seconds': round(time.monotonic() - stamp, 3)})
        super().stopTest(test)


def successor_control(original, module):
    from pathlib import Path
    import tempfile
    from datetime import datetime, timezone

    def test_01_expired_legacy_source_refuses_new_session_grant(self):
        auth = __import__(module.__package__ + '.auth', fromlist=['ReaderChannel'])
        fixtures = __import__(module.__package__ + '.fixtures', fromlist=['provision'])
        protocol = __import__(module.__package__ + '.protocol', fromlist=['source'])
        ReaderChannel, provision, source = auth.ReaderChannel, fixtures.provision, protocol.source
        period = API.parent / 'session-participation-v2/packages/0001/period.json'
        period_raw = period.read_bytes()
        old = source.parse(period_raw)
        self.assertGreaterEqual(datetime.now(timezone.utc),
                                datetime.fromisoformat(old['expires_at'].replace('Z', '+00:00')))
        with tempfile.TemporaryDirectory(prefix='cal-R03-expired-source-refusal-v2-') as tmp:
            root = Path(tmp)
            root.chmod(0o700)
            key, path, pin = provision(root, 'fresh-participation',
                                       principal='principal:R03-fresh-reader')
            with self.assertRaisesRegex(ValueError, '^selected R02 participation environment differs$'):
                ReaderChannel(path, pin, self.schemas)
            selected = object.__new__(ReaderChannel)
            selected.path, selected.expected_sha, selected.schemas = path, pin, self.schemas
            with self.assertRaisesRegex(ValueError,
                    '^historical fresh source host window exceeds retained absolute Assignment interval$'):
                selected.policy_guard(check_source=False)
            key = None
        self.assertFalse(root.exists())

    cls = type(original.__name__, (original,),
               {'test_01_expired_legacy_source_refuses_new_session_grant':
                test_01_expired_legacy_source_refuses_new_session_grant})
    cls.__module__ = module.__name__
    cls.__qualname__ = original.__qualname__
    return cls


def main():
    name, old, manifest = select()
    selected_ids = old['selected_case_ids'][68:]
    suite = unittest.TestSuite()
    groups = (('test_current_controls', 'CurrentControls'),
              ('test_termination_boundaries', 'TerminationBoundaries'),
              ('test_machine_transport', 'MachineTransport'))
    for filename, classname in groups:
        module = __import__(name + '.' + filename, fromlist=[classname])
        module.PROFILE = PROFILE_SHA
        cls = getattr(module, classname)
        if filename == 'test_current_controls':
            methods = unittest.defaultTestLoader.getTestCaseNames(cls)
            digest = hashlib.sha256(json.dumps(methods, separators=(',', ':')).encode()).hexdigest()
            if len(methods) != 11 or digest != ORIGINAL_CONTROL_SHA:
                raise ValueError('original CurrentControls method inventory differs')
            cls = successor_control(cls, module)
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    all_cases = list(suite)
    if len(all_cases) != 31 or [case.id() for case in all_cases] != selected_ids:
        raise ValueError('T02 remainder is not exact selected 31-case suffix')
    started = datetime.now(timezone.utc).isoformat()
    result = unittest.TextTestRunner(verbosity=2, failfast=True, resultclass=Outcome).run(suite)
    verdict = {'result': 'PASS' if result.wasSuccessful() and result.testsRun == 31 else 'FAIL',
               'predecessor_result_sha256': OLD_SHA, 'source_manifest_sha256': API_SHA,
               'profile_sha256': PROFILE_SHA, 'selected_case_ids': selected_ids,
               'started_at_utc': started, 'completed_at_utc': datetime.now(timezone.utc).isoformat(),
               'tests_run': result.testsRun, 'case_rows': result.rows,
               'failures': [(case.id(), text[-1600:]) for case, text in result.failures],
               'errors': [(case.id(), text[-1600:]) for case, text in result.errors],
               'expired_original_claim': 'constructor refuses at historical environment; exact policy period guard separately refuses expired Assignment with source preflight disabled',
               'source_unchanged_during_run': sha(API / 'source-manifest.json') == API_SHA and all(
                   sha(ROOT / row['path']) == row['sha256'] for row in manifest['files']),
               'runner_sha256': sha(Path(__file__).resolve())}
    out = HERE / 'working'
    out.mkdir(mode=0o700, exist_ok=True)
    target = out / 'remainder-result-0001.json'
    if target.exists():
        raise ValueError('versioned remainder result already exists')
    target.write_text(json.dumps(verdict, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'result': verdict['result'], 'tests_run': result.testsRun,
                      'failures': len(result.failures), 'errors': len(result.errors)}))


if __name__ == '__main__':
    main()
