"""Run original expiry assertions against the exact selected successor."""
import argparse
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
API = HERE.parent / 'api-v55'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('_cal_API55_expiry_guard', API / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(args.source_sha256)
    name = '_cal_API55_expiry_actual'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    P = importlib.import_module(name + '.protocol')
    assert P.source.sha((API / 'contract-profile.json').read_bytes()) == args.profile_sha256
    modules = [importlib.import_module(name + '.' + m) for m in ['run_session_checks', 'test_custody_sessions']]
    for module in modules:
        module.PROFILE = args.profile_sha256
    case = 'test_27_actual_expiry_timer_disposes'
    suite = unittest.TestSuite([module.Sessions(case) for module in modules])
    assert suite.countTestCases() == 2
    output = HERE / 'receipts'
    output.mkdir(exist_ok=False)
    log = output / 'actual-0001.log'
    with log.open('x') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    guard.verify(args.source_sha256)
    wire = output / 'wire-0001.json'
    with wire.open('x') as stream:
        json.dump([event for module in modules for event in module.Sessions.events], stream, indent=2, sort_keys=True)
        stream.write('\n')
    def bind(path):
        return {'path': path.relative_to(ROOT).as_posix(), 'sha256': P.source.sha(path.read_bytes())}
    good = result.wasSuccessful() and result.testsRun == 2
    report = {'schema_version': 'lab-original-expiry-checks/v1-candidate', 'result': 'PASS' if good else 'FAIL',
        'source_sha256': args.source_sha256, 'profile_sha256': args.profile_sha256,
        'actual_cases': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'original_70_second_deadlines_unchanged': True, 'original_90_second_waits_unchanged': True,
        'original_test_methods_unchanged': True, 'original_source_callbacks_unchanged': True,
        'full_selected_suite_completed': result.testsRun == 2,
        'source_guarded_exit_completed': good, 'owned_fixture_cleanup_completed': good,
        'full_regression_qualified': False, 'whole_API_qualified': False,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'files': [bind(log), bind(wire), bind(API / 'source-manifest.json'), bind(API / 'contract-profile.json')],
        'claim_ceiling': 'Two unchanged original real-clock expiry tests only. Actual authenticated host and original source callbacks; no profiler, mock clock, deadline extension or admission. Complete API regression and plan remain unfinished.'}
    path = output / 'checks-0001.json'
    with path.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'actual_cases': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors), 'report_binding': bind(path)}), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
