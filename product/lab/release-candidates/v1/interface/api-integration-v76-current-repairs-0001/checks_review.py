"""Run all eleven actual-source public review adapter checks after source freeze."""
import argparse
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
    name = '_cal_api32_current_review_checks'
    spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    guard = __import__(name + '.guard', fromlist=['*'])
    guard.verify(args.source_sha256)
    module = __import__(name + '.test_review_api', fromlist=['*'])
    module.SOURCE = args.source_sha256
    module.PROFILE = args.profile_sha256
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.CurrentReview)
    assert suite.countTestCases() == 11
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
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    guard.verify(args.source_sha256)
    output = HERE / 'receipts'
    output.mkdir(mode=0o700, exist_ok=True)
    success = result.wasSuccessful() and result.testsRun == 11
    report = {'result': 'PASS' if success else 'FAIL', 'tests_run': result.testsRun,
              'expected_tests': 11, 'cases': cases, 'source_sha256': args.source_sha256,
              'profile_sha256': args.profile_sha256, 'candidate_handler_count': 14,
              'whole_API_qualified': False, 'current_owner_authority_verified': False,
              'repository_admissions_applied': 0, 'actual_owner_outcome': None,
              'authority_effect': 'none', 'task_complete': False, 'goal_complete': False}
    for filename, value in [('review-checks.json', report),
                            ('review-wire.json', {'observations': module.CurrentReview.witnesses,
                                                  'actual_owner_outcome': None, 'authority_effect': 'none'})]:
        with (output / filename).open('x') as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write('\n')
    print(json.dumps({'result': report['result'], 'tests_run': result.testsRun}), flush=True)
    raise SystemExit(0 if success else 1)

if __name__ == '__main__':
    main()
