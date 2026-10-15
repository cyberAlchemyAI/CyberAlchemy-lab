import argparse
import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
def verify(pin):
    raw = (HERE / 'source-manifest.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == pin
    source = json.loads(raw)
    for row in source['files']:
        path = ROOT / row['path']
        assert path.is_file() and not any(p.is_symlink() for p in (path, *path.parents))
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], row['path']
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    verify(args.source_sha256)
    name = '_cal_file_materialization_checks'
    spec = importlib.util.spec_from_file_location(name, HERE / '__init__.py', submodule_search_locations=[str(HERE)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    tests = __import__(name + '.test_exports', fromlist=['*'])
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, t):
            super().addSuccess(t)
            cases.append({'test': t.id(), 'result': 'PASS'})
        def addFailure(self, t, error):
            super().addFailure(t, error)
            cases.append({'test': t.id(), 'result': 'FAIL', 'detail': self._exc_info_to_string(error, t)})
        def addError(self, t, error):
            super().addError(t, error)
            cases.append({'test': t.id(), 'result': 'ERROR', 'detail': self._exc_info_to_string(error, t)})
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    assert suite.countTestCases() == 24
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    verify(args.source_sha256)
    receipts = HERE / 'receipts'
    receipts.mkdir(mode=0o700, exist_ok=True)
    value = {'result': 'PASS' if result.wasSuccessful() and result.testsRun == 24 else 'FAIL', 'tests_run': result.testsRun, 'expected_tests': 24, 'cases': cases, 'source_sha256': args.source_sha256, 'observations': tests.Exports.observations, 'public_api_qualification': False, 'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False}
    with (receipts / 'checks-0001.json').open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    raise SystemExit(0 if value['result'] == 'PASS' else 1)
if __name__ == '__main__':
    main()
