"""Exact separate classification successor with all sixteen original cases."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
API = HERE.parent / 'api-v57'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    parser.add_argument('--check-source-sha256', required=True)
    parser.add_argument('--suite', choices=['focused', 'full', 'pending'], required=True)
    args = parser.parse_args()
    selected_path = HERE / 'source-manifest.json'
    assert sha(selected_path) == args.check_source_sha256
    selected = json.loads(selected_path.read_bytes())
    def check_source():
        assert sha(selected_path) == args.check_source_sha256
        for row in selected['files']:
            path = ROOT / row['path']
            assert path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
            assert sha(path) == row['sha256'], row['path']
    check_source()
    name = '_cal_API57_classification_' + args.suite
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    guard = __import__(name + '.guard', fromlist=['verify'])
    guard.verify(args.source_sha256)
    assert sha(API / 'contract-profile.json') == args.profile_sha256
    spec = importlib.util.spec_from_file_location(name + '.versioned_classification', HERE / 'test_classification_api.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.SOURCE, module.PROFILE = args.source_sha256, args.profile_sha256
    if args.suite == 'pending':
        suite=unittest.TestSuite([module.ClassificationAPI('test_17_pending_native_evidence_is_inspectable_and_tamper_refused')])
        expected=1
    elif args.suite == 'focused':
        names = ['test_09_independent_axis_is_preserved', 'test_12_wrong_original_stable_core_is_not_classified',
                 'test_16_uncertain_core_failure_stays_pending_without_redispatch']
        suite = unittest.TestSuite(module.ClassificationAPI(n) for n in names)
        expected = 3
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.ClassificationAPI)
        expected = 17
    assert suite.countTestCases() == expected
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
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
    receipts = HERE / 'receipts'
    receipts.mkdir(exist_ok=True)
    log = receipts / (args.suite + '-0001.log')
    with log.open('x') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(suite)
    check_source(); guard.verify(args.source_sha256)
    assert sha(API / 'contract-profile.json') == args.profile_sha256
    wire = receipts / (args.suite + '-wire-0001.json')
    with wire.open('x') as stream:
        json.dump(module.ClassificationAPI.observations, stream, indent=2, sort_keys=True)
        stream.write('\n')
    def bind(path):
        return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}
    good = result.wasSuccessful() and result.testsRun == expected
    report = {'schema_version': 'lab-separate-classification-checks/v1-candidate',
        'result': 'PASS' if good else 'FAIL', 'suite': args.suite,
        'actual_cases': result.testsRun, 'expected_cases': expected, 'cases': cases,
        'errors': len(result.errors), 'failures': len(result.failures),
        'source_sha256': args.source_sha256, 'profile_sha256': args.profile_sha256,
        'check_source_sha256': args.check_source_sha256,
        'full_selected_suite_completed': result.testsRun == expected,
        'source_guarded_exit_completed': good, 'owned_fixture_cleanup_completed': good,
        'original_test_file_unchanged': True, 'original_cases_retained': 16,
        'only_test_method_successor': 'Independent-axis targets5 to9 plus exact proposal, five domain/four relation targets and original signature/endpoint/qualifier checks. Other15 method ASTs unchanged; one added case exercises pending evidence inspection, retry and tamper refusal.',
        'canonical_admissions_applied': 0, 'whole_API_qualified': False,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'files': [bind(log), bind(wire), bind(selected_path), bind(API / 'source-manifest.json'),
                  bind(API / 'contract-profile.json')],
        'claim_ceiling': 'Only the selected exact authenticated candidate classification cases. Full original source exit and owned cleanup are required for PASS. Native validation evidence may persist while a bad-core command remains pending, without classification, command result, owner outcome or admission. No other API journey or complete plan is qualified.'}
    output = receipts / (args.suite + '-0001.json')
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'suite': args.suite, 'actual_cases': result.testsRun,
        'errors': len(result.errors), 'failures': len(result.failures), 'report_binding': bind(output)}), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
