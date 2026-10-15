"""Run the complete frozen pure evidence-buffer suite."""
import argparse
import hashlib
import importlib.util
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
    path = HERE / 'source-manifest.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == args.source_sha256
    selected = json.loads(path.read_bytes())
    def guard():
        for row in selected['files']:
            source = ROOT / row['path']
            assert not source.is_symlink() and not any(p.is_symlink() for p in source.parents)
            assert hashlib.sha256(source.read_bytes()).hexdigest() == row['sha256']
    guard()
    name = '_cal_staged_evidence_checks_v1'
    spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py',
                                                submodule_search_locations=[str(HERE)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package; spec.loader.exec_module(package)
    module = __import__(name + '.test_buffer', fromlist=['BufferTests'])
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.BufferTests)
    assert suite.countTestCases() == 22
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    guard()
    value = {'schema_version': 'lab-staged-evidence-checks/v1-candidate',
             'result': 'PASS' if result.wasSuccessful() and result.testsRun == 22 else 'FAIL',
             'actual_cases': result.testsRun, 'failures': len(result.failures),
             'errors': len(result.errors), 'source_sha256': args.source_sha256,
             'actual_public_calls': 0, 'authenticated_host_qualified': False,
             'authority_effect': 'none', 'actual_owner_outcome': None,
             'claim_ceiling': 'Pure bounded staging only; synthetic validator and writer callbacks grant no host or operation qualification.'}
    receipts = HERE / 'receipts'; receipts.mkdir(exist_ok=True)
    with (receipts / 'checks-0001.json').open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2); stream.write('\n')
    print(json.dumps(value), flush=True)
    raise SystemExit(0 if value['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
