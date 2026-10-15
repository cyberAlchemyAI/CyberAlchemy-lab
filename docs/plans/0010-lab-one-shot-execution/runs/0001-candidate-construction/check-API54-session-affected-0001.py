"""Seven unchanged original Session cases against the frozen successor."""
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v54'
SOURCE = 'c5706f746f40228b5fae94803c5d3eab6ac8297f184bfb0d14293ddd9986a15b'
PROFILE = '56f341937c0e51664f174ff207528e41df8c92e208bb28e5661b10197cd4038d'
CASES = ['test_01_actual_private_memory_erased', 'test_03_seven_exact_candidate_connections',
         'test_05_same_key_no_second_creation', 'test_24_captured_source_corruption_disposes_on_inspection',
         'test_25_close_does_not_require_current_Project_State', 'test_26_private_policy_revocation_disposes',
         'test_29_source_and_period_unchanged']


def main():
    spec = importlib.util.spec_from_file_location('_cal_API54_affected_guard', API / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(SOURCE)
    name = '_cal_API54_affected_actual'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    P = importlib.import_module(name + '.protocol')
    assert P.source.sha((API / 'contract-profile.json').read_bytes()) == PROFILE
    tests = importlib.import_module(name + '.test_custody_sessions')
    tests.PROFILE = PROFILE
    suite = unittest.TestSuite([tests.Sessions(case) for case in CASES])
    assert suite.countTestCases() == 7
    log = RUN / 'API54-session-affected7-0001.log'
    with log.open('x') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    guard.verify(SOURCE)
    wire = RUN / 'API54-session-affected7-wire-0001.json'
    with wire.open('x') as stream:
        json.dump(tests.Sessions.events, stream, indent=2, sort_keys=True)
        stream.write('\n')
    def bind(path):
        return {'path': path.relative_to(ROOT).as_posix(), 'sha256': P.source.sha(path.read_bytes())}
    good = result.wasSuccessful() and result.testsRun == 7
    report = {'schema_version': 'lab-original-affected-Session-checks/v1-candidate', 'result': 'PASS' if good else 'FAIL',
        'source_sha256': SOURCE, 'profile_sha256': PROFILE, 'selected_original_methods': CASES,
        'actual_cases': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'original_test_methods_unchanged': True, 'original_source_callbacks_unchanged': True,
        'full_selected_suite_completed': result.testsRun == 7,
        'source_guarded_exit_completed': good, 'owned_fixture_cleanup_completed': good,
        'full_regression_qualified': False, 'whole_API_qualified': False,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'files': [bind(log), bind(wire), bind(API / 'source-manifest.json'), bind(API / 'contract-profile.json'),
                  bind(API / 'test_custody_sessions.py'), bind(Path(__file__).resolve())],
        'claim_ceiling': 'Seven selected unchanged original Session cases only: RAM erasure, seven connections, exact retry, corrupted source disposal, close with invalidated Project State, policy revocation and original absolute period. No new grant, full API regression, admission or complete plan.'}
    output = RUN / 'API54-session-affected7-report-0001.json'
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'actual_cases': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors), 'report_binding': bind(output)}), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
