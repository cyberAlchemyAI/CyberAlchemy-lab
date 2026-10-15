"""Complete selected actual import suite, preserving clocks and original guards."""
import argparse
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
API = HERE.parent / 'api-v53'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--profile-sha256', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('_cal_API53_package_guard', API / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(args.source_sha256)
    name = '_cal_API53_package_actual'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    P = importlib.import_module(name + '.protocol')
    assert P.source.sha((API / 'contract-profile.json').read_bytes()) == args.profile_sha256
    spec = importlib.util.spec_from_file_location('_cal_API53_package_cases', HERE / 'test_host.py')
    tests = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = tests
    spec.loader.exec_module(tests)
    tests.PACKAGE, tests.PROFILE = name, args.profile_sha256
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(tests.PackageChecks)
    assert suite.countTestCases() == 3
    output = HERE / 'receipts'
    output.mkdir(exist_ok=False)
    log = output / 'actual-0001.log'
    with log.open('x') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    guard.verify(args.source_sha256)
    wire = output / 'wire-0001.json'
    with wire.open('x') as stream:
        json.dump(tests.PackageChecks.events, stream, indent=2, sort_keys=True)
        stream.write('\n')
    def bind(path):
        return {'path': path.relative_to(ROOT).as_posix(), 'sha256': P.source.sha(path.read_bytes())}
    good = result.wasSuccessful() and result.testsRun == 3 and tests.PackageChecks.positive_import_completed
    report = {'schema_version': 'lab-package-import-public-checks/v1-candidate', 'result': 'PASS' if good else 'FAIL',
        'source_sha256': args.source_sha256, 'profile_sha256': args.profile_sha256,
        'actual_cases': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'actual_public_calls': len(tests.PackageChecks.events), 'actual_authenticated_host_used': bool(tests.PackageChecks.events),
        'actual_import_positive_completed': tests.PackageChecks.positive_import_completed,
        'source_guarded_exit_completed': tests.PackageChecks.source_exit_completed,
        'owned_fixture_cleanup_completed': tests.PackageChecks.owned_cleanup_completed,
        'full_selected_suite_completed': result.testsRun == 3, 'actual_public_export_qualified': False,
        'source_package_posture': 'owned-controlled-candidate-same-target-cut',
        'source_publication_permission_fixture_only': True, 'general_foreign_source_import_qualified': False,
        'source_admission_qualified': False, 'canonical_admissions_applied': 0,
        'whole_API_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None,
        'task_complete': False, 'goal_complete': False,
        'files': [bind(log), bind(wire), bind(API / 'source-manifest.json'), bind(API / 'contract-profile.json')],
        'claim_ceiling': 'Three selected actual operator import cases only: independently selected managed candidate package, actual original signed target replay, original native source/target proposal checks, complete selected accounting, strict controls, durable journal and read-only retry. The publication grant is synthetic fixture permission. No public export, general foreign/admitted-source import, canonical admission, genuine pilot, whole API or completed plan.'}
    path = output / 'checks-0001.json'
    with path.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'actual_cases': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors), 'actual_public_calls': len(tests.PackageChecks.events),
        'report_binding': bind(path), 'goal_complete': False}), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
