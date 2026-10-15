"""Complete real-filesystem fixture suite; no authenticated/public host claim."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def guard(expected):
    manifest = json.loads((HERE / 'source-manifest.json').read_bytes())
    if manifest['source_sha256'] != expected or sha(encoded(manifest['files'] + manifest['input_bindings'])) != expected:
        raise ValueError('independent publication source differs')
    for row in manifest['files'] + manifest['input_bindings']:
        path = ROOT / row['path']
        if path.is_symlink() or bind(path) != row:
            raise ValueError('publication source changed: ' + row['path'])
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    manifest = guard(args.source_sha256)
    spec = importlib.util.spec_from_file_location('_cal_publication_all_cases', HERE / 'test_publication.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.Publication)
    if suite.countTestCases() != manifest['selected_filesystem_cases']:
        raise ValueError('complete selected suite differs')
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    guard(args.source_sha256)
    good = result.wasSuccessful() and result.testsRun == manifest['selected_filesystem_cases']
    receipts = HERE / 'receipts'
    receipts.mkdir(exist_ok=False)
    path = receipts / 'actual-0001.log'
    with path.open('x') as stream:
        stream.write(log.getvalue())
    report = {'schema_version': 'lab-package-publication-checks/v1-candidate', 'result': 'PASS' if good else 'FAIL',
        'source_sha256': args.source_sha256, 'real_filesystem_fixture_cases': result.testsRun,
        'failures': len(result.failures), 'errors': len(result.errors),
        'full_selected_suite_completed': result.testsRun == manifest['selected_filesystem_cases'],
        'source_guarded_exit_completed': True, 'owned_temporary_fixture_cleanup_completed': result.wasSuccessful(),
        'fixture_posture': 'actual-owned-temporary-filesystem-with-synthetic-source-and-permission-callbacks',
        'actual_public_calls': 0, 'actual_authenticated_host_used': False, 'actual_source_admission_qualified': False,
        'public_handlers_added': 0, 'actual_target_model_qualified': False, 'whole_API_qualified': False,
        'files': [bind(path), bind(HERE / 'source-manifest.json')], 'authority_effect': 'none',
        'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False,
        'claim_ceiling': 'Complete managed filesystem fixture cases only: exact bytes, no-follow owned roots, exclusive generations, fsync marker, read-only retry, independently selected managed readback and preserved uncertainty. Synthetic callbacks do not prove authenticated permission or original source replay; no public API, semantic model, genuine pilot or admission.'}
    output = receipts / 'checks-0001.json'
    with output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': report['result'], 'cases': result.testsRun, 'failures': len(result.failures),
        'errors': len(result.errors), 'report_binding': bind(output)}), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
