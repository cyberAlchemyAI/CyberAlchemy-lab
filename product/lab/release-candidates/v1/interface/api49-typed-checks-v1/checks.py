"""Run all ten actual authenticated operator typed cases from pinned sources."""
import argparse
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
API = HERE.parent / 'api-v49'
SOURCE = '70a59c0f1c5cd96bedd523a024827a41e2b8f54f3ca0f6a685599ff4d6fe14aa'
PROFILE = '4ce85f563320da3b97d95b5f598053b2e2ec88f44bc1ec7e281c2aa22b4073c5'


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-source-sha256', required=True)
    args = parser.parse_args()
    manifest = HERE / 'source-manifest.json'
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == args.check_source_sha256
    selected = json.loads(manifest.read_bytes())
    def guard():
        for row in selected['files']:
            path = ROOT / row['path']
            assert path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    guard()
    name = '_cal_API49_actual_typed_operation_checks_v1'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    check_name = '_cal_API49_actual_typed_cases_v1'
    spec = importlib.util.spec_from_file_location(check_name, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[check_name] = package
    spec.loader.exec_module(package)
    tests = importlib.import_module(check_name + '.test_public_typed')
    tests.API, tests.SOURCE, tests.PROFILE = name, SOURCE, PROFILE
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            detail = self._exc_info_to_string(error, test)
            cases.append({'test': test.id(), 'result': 'FAIL', 'detail': detail})
            self.stream.write('\n' + detail)
            self.stream.flush()
        def addError(self, test, error):
            super().addError(test, error)
            detail = self._exc_info_to_string(error, test)
            cases.append({'test': test.id(), 'result': 'ERROR', 'detail': detail})
            self.stream.write('\n' + detail)
            self.stream.flush()
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    assert suite.countTestCases() == 10
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    guard()
    receipts = HERE / 'receipts'
    receipts.mkdir(exist_ok=True)
    report = {'schema_version': 'lab-public-typed-operation-checks/v1-candidate',
        'result': 'PASS' if result.wasSuccessful() and result.testsRun == 10 else 'FAIL',
        'actual_cases': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'cases': cases, 'source_sha256': SOURCE, 'profile_sha256': PROFILE,
        'check_source_sha256': args.check_source_sha256,
        'original_reader_guarded_exit_completed': getattr(tests.PublicTypedChecks, 'original_reader_guarded_exit_completed', False),
        'actual_public_calls': len(getattr(tests.PublicTypedChecks, 'observations', [])),
        'all_target_changes_synthetic': True, 'genuine_semantic_review_provided': False,
        'assigned_Agent_qualified': False, 'actual_runtime_grant': False, 'whole_API_qualified': False,
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False}
    put(receipts / 'checks-0001.json', report)
    put(receipts / 'wire-0001.json', getattr(tests.PublicTypedChecks, 'observations', []))
    print(json.dumps({'result': report['result'], 'actual_cases': result.testsRun,
                      'original_reader_guarded_exit_completed': report['original_reader_guarded_exit_completed']}), flush=True)
    raise SystemExit(0 if report['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
