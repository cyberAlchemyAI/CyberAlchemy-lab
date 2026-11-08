"""Run all public classification cases only after exact source/profile freeze."""
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
    name = '_cal_api36_classification_checks'
    spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    guard = __import__(name + '.guard', fromlist=['verify'])
    manifest = guard.verify(args.source_sha256)
    assert manifest['freeze_precedes_new_owned_fixture_effects']
    profile_path = HERE / 'contract-profile.json'
    assert hashlib.sha256(profile_path.read_bytes()).hexdigest() == args.profile_sha256
    module = __import__(name + '.test_classification_api', fromlist=['ClassificationAPI'])
    module.SOURCE = args.source_sha256
    module.PROFILE = args.profile_sha256
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.ClassificationAPI)
    assert suite.countTestCases() == 16
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
    assert hashlib.sha256(profile_path.read_bytes()).hexdigest() == args.profile_sha256
    receipts = HERE / 'receipts'
    receipts.mkdir(exist_ok=True)
    value = {'schema_version': 'lab-public-classification-checks/v1-candidate',
             'result': 'PASS' if result.wasSuccessful() and result.testsRun == 16 else 'FAIL',
             'tests_run': result.testsRun, 'expected_tests': 16, 'cases': cases,
             'source_sha256': args.source_sha256, 'profile_sha256': args.profile_sha256,
             'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False}
    with (receipts / 'classification-checks.json').open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    with (receipts / 'classification-wire.json').open('x') as stream:
        json.dump({'actual_public_calls': module.ClassificationAPI.observations,
                   'actual_owner_outcome': None, 'authority_effect': 'none'}, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': value['result'], 'tests_run': result.testsRun}), flush=True)
    raise SystemExit(0 if value['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
