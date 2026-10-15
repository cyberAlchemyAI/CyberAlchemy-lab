"""Run complete control successor against unchanged, independently pinned API44."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
API = HERE.parent / 'api-v44'
SOURCE = '9f56fbe2c874f2f9f5f7965998e033b5a51ebb75b19d5c19c3733b6b02345f0f'
PROFILE = 'afb0373d8857ae0ee11b67efd356d2652091aab8e6953fe4ddbc5deee4bd1578'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-source-sha256', required=True)
    args = parser.parse_args()
    manifest_path = HERE / 'source-manifest.json'
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == args.check_source_sha256
    selected = json.loads(manifest_path.read_bytes())
    def checks_guard():
        for row in selected['files']:
            path = ROOT / row['path']
            assert not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    checks_guard()
    name = '_cal_API44_complete_control_successor_v1'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py',
                                                submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec); sys.modules[name] = package
    spec.loader.exec_module(package)
    guard = __import__(name + '.guard', fromlist=['verify'])
    guard.verify(SOURCE)
    assert hashlib.sha256((API / 'contract-profile.json').read_bytes()).hexdigest() == PROFILE
    # Load a new test module. No original test, production function or callback
    # is patched. Relative imports select the actual unchanged API44 package.
    module_name = name + '.versioned_control_checks_v1'
    spec = importlib.util.spec_from_file_location(module_name, HERE / 'test_current_controls.py')
    module = importlib.util.module_from_spec(spec); sys.modules[module_name] = module
    spec.loader.exec_module(module); module.PROFILE = PROFILE
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.CurrentControls)
    assert suite.countTestCases() == 11
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test); cases.append({'test': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            detail = self._exc_info_to_string(error, test)
            cases.append({'test': test.id(), 'result': 'FAIL', 'detail': detail})
            self.stream.write('\n' + detail); self.stream.flush()
        def addError(self, test, error):
            super().addError(test, error)
            detail = self._exc_info_to_string(error, test)
            cases.append({'test': test.id(), 'result': 'ERROR', 'detail': detail})
            self.stream.write('\n' + detail); self.stream.flush()
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    checks_guard(); guard.verify(SOURCE)
    assert hashlib.sha256((API / 'contract-profile.json').read_bytes()).hexdigest() == PROFILE
    value = {'schema_version': 'lab-versioned-current-control-checks/v1-candidate',
             'result': 'PASS' if result.wasSuccessful() and result.testsRun == 11 else 'FAIL',
             'actual_cases': result.testsRun, 'cases': cases,
             'check_source_sha256': args.check_source_sha256,
             'API_source_sha256': SOURCE, 'API_profile_sha256': PROFILE,
             'unchanged_original_method_ASTs': 10,
             'explicit_revised_methods': ['test_03_exact_current_profile_and_protocol_controls'],
             'exact_revision': 'Declared supported-handler count15 to16; exact complete lists,34 contracts and all other checks preserved.',
             'whole_API_qualified': False, 'task_complete': False,
             'authority_effect': 'none', 'actual_owner_outcome': None}
    receipts = HERE / 'receipts'; receipts.mkdir(exist_ok=True)
    with (receipts / 'checks-0001.json').open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2); stream.write('\n')
    print(json.dumps({'result': value['result'], 'actual_cases': result.testsRun}), flush=True)
    raise SystemExit(0 if value['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
