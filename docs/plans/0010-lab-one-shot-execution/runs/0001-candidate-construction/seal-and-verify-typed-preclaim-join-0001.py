"""Seal and run every retained selection and added preclaim identity check."""
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
PACKAGE = ROOT / 'product/lab/release-candidates/v1/interface/typed-host-composition-v4'


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    unsealed = RUN / 'typed-preclaim-join-unsealed-inventory-0001.json'
    document = json.loads(unsealed.read_bytes())
    manifest = PACKAGE / 'source-manifest.json'
    assert not manifest.exists()
    inputs = document['input_bindings'] + [binding(unsealed), binding(Path(__file__).resolve())]
    source = {**document['parent'], 'schema_version': 'lab-typed-host-composition-source/v4-candidate',
        'files': [binding(path) for path in sorted(PACKAGE.glob('*')) if path.is_file()],
        'input_bindings': inputs, 'context_binding': document['context_binding'],
        'static_binding': document['static_binding'], 'preclaim_identity_join_authored': True,
        'public_handler_qualified': False, 'task_complete': False}
    def guard():
        for row in source['files'] + source['input_bindings']:
            path = ROOT / row['path']
            assert path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents)
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    guard()
    emit(manifest, source)
    name = '_cal_typed_preclaim_join_full_selection_v4'
    spec = importlib.util.spec_from_file_location(name, PACKAGE / '__init__.py', submodule_search_locations=[str(PACKAGE)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    modules = [importlib.import_module(name + '.' + suffix) for suffix in ('test_selection', 'test_inspection_join')]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(module) for module in modules)
    assert suite.countTestCases() == 41
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'test': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'test': test.id(), 'result': 'FAIL', 'detail': self._exc_info_to_string(error, test)})
        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'test': test.id(), 'result': 'ERROR', 'detail': self._exc_info_to_string(error, test)})
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    guard()
    report = {'schema_version': 'lab-typed-preclaim-join-checks/v1-candidate',
        'result': 'PASS' if result.wasSuccessful() and result.testsRun == 41 else 'FAIL',
        'actual_cases': result.testsRun, 'retained_inventory_cases': 25, 'new_preclaim_cases': 16,
        'failures': len(result.failures), 'errors': len(result.errors), 'cases': cases,
        'source_binding': binding(manifest), 'script_binding': binding(Path(__file__).resolve()),
        'actual_public_calls': 0, 'runtime_qualified': False, 'actual_runtime_grant': False,
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False}
    emit(RUN / 'typed-preclaim-join-checks-0001.json', report)
    print(json.dumps({'result': report['result'], 'actual_cases': result.testsRun,
                      'source_binding': binding(manifest)}), flush=True)
    raise SystemExit(0 if report['result'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
