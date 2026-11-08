"""Run the frozen successor's six actual termination-policy cases."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('_cal_termination_guard', HERE / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(args.source_sha256)
    assert hashlib.sha256((HERE / 'contract-profile.json').read_bytes()).hexdigest() == args.profile_sha256
    name = '_cal_api34_termination_boundaries'
    spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    checks = __import__(name + '.test_termination_boundaries', fromlist=['*'])
    checks.PROFILE = args.profile_sha256
    cases = []

    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})

        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'test': test.id(), 'result': 'FAIL', 'detail': self._exc_info_to_string(error, test)})

        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'test': test.id(), 'result': 'ERROR', 'detail': self._exc_info_to_string(error, test)})

    suite = unittest.defaultTestLoader.loadTestsFromModule(checks)
    assert suite.countTestCases() == 6
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    guard.verify(args.source_sha256)
    success = result.wasSuccessful() and result.testsRun == 6
    output = HERE / 'receipts'
    output.mkdir(mode=0o700, exist_ok=True)
    report = {'schema_version': 'lab-Session-termination-boundary-checks/v1-candidate',
              'result': 'PASS' if success else 'FAIL', 'tests_run': result.testsRun,
              'expected_tests': 6, 'cases': cases, 'events': checks.TerminationBoundaries.events,
              'source_sha256': args.source_sha256, 'profile_sha256': args.profile_sha256,
              'permissions_cached': False, 'clock_replaced': False, 'source_callbacks_replaced': False,
              'current_Agent_qualified': False, 'whole_API_qualified': False,
              'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False}
    with (output / 'termination-boundary-checks.json').open('x') as stream:
        json.dump(report, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'tests_run': result.testsRun}), flush=True)
    raise SystemExit(0 if success else 1)


if __name__ == '__main__':
    main()

