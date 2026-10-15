"""Run all frozen pure package cases; never claim actual host qualification."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('_cal_package_transfer_all_cases', HERE / 'test_transfer.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    engine = module.T.Transfer(args.source_sha256)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.Packages)
    manifest = json.loads((HERE / 'source-manifest.json').read_bytes())
    assert suite.countTestCases() == manifest['selected_pure_cases']
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    engine.guard()
    receipts = HERE / 'receipts'
    receipts.mkdir(exist_ok=False)
    actual_log = receipts / 'actual-0001.log'
    with actual_log.open('x') as stream:
        stream.write(log.getvalue())
    def bind(path):
        return {'path': path.relative_to(ROOT).as_posix(), 'sha256': module.T.sha(path.read_bytes())}
    good = result.wasSuccessful() and result.testsRun == manifest['selected_pure_cases']
    report = {'schema_version': 'lab-package-transfer-pure-checks/v1-candidate',
        'result': 'PASS' if good else 'FAIL', 'source_sha256': args.source_sha256,
        'pure_cases': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'full_selected_suite_completed': result.testsRun == manifest['selected_pure_cases'],
        'source_guarded_exit_completed': True, 'fixture_posture': 'synthetic-pure-values-only',
        'actual_public_calls': 0, 'actual_authenticated_host_used': False,
        'actual_source_admission_qualified': False, 'actual_target_model_qualified': False,
        'public_handlers_added': 0, 'whole_API_qualified': False, 'authority_effect': 'none',
        'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'files': [bind(actual_log), bind(HERE / 'source-manifest.json')],
        'claim_ceiling': 'Complete frozen pure dependency closure, exact-byte archive verification and source import accounting only. No authenticated transport, semantic target validation, managed publication, genuine pilot, admission or complete API.'}
    output = receipts / 'checks-0001.json'
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'pure_cases': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors), 'report_binding': bind(output)}), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
