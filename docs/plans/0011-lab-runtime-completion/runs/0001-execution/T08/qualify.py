"""Real owned T08 focused qualification, ordered reader then graph checkpoints."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[6]
HERE = Path(__file__).resolve().parent
COMPONENT = ROOT/'product/lab/release-candidates/v1/interface/release-proof-inputs-v1-completion-0001'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(): return datetime.now(timezone.utc).isoformat()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-manifest-sha256', required=True)
    parser.add_argument('--attempt', required=True)
    args = parser.parse_args()
    if not args.attempt.isdigit(): raise ValueError('numeric exclusive attempt required')
    manifest_path = HERE/'qualification-inputs.json'
    if sha(manifest_path) != args.input_manifest_sha256: raise ValueError('independent input manifest differs')
    inputs = json.loads(manifest_path.read_text())
    def guard():
        if sha(manifest_path) != args.input_manifest_sha256: raise ValueError('input manifest changed')
        for row in inputs['files']:
            p = ROOT/row['path']
            if p.is_symlink() or sha(p) != row['sha256']: raise ValueError('qualified source changed: '+row['path'])
    guard()
    versions = {'python': sys.version.split()[0],
        'jsonschema': importlib.metadata.version('jsonschema'),
        'cryptography': importlib.metadata.version('cryptography')}
    if versions != {'python': '3.14.4', 'jsonschema': '4.23.0', 'cryptography': '46.0.5'}:
        raise ValueError('independently selected R02 environment differs')
    events_path = HERE/('attempt-'+args.attempt+'.events.jsonl')
    report_path = HERE/('attempt-'+args.attempt+'.json')
    if report_path.exists(): raise ValueError('attempt report exists')
    events = events_path.open('x'); cases = []; started = stamp(); begin = time.monotonic()
    def event(value):
        events.write(json.dumps(dict(at=stamp(), **value), sort_keys=True)+'\n'); events.flush()
    event({'phase': 'entry', 'source_binding': args.input_manifest_sha256, 'environment': versions})
    spec = importlib.util.spec_from_file_location('_cal_T08_tests', COMPONENT/'test_inputs.py')
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    method_ast = {}
    tree = ast.parse((COMPONENT/'test_inputs.py').read_text())
    for cls in tree.body:
        if isinstance(cls, ast.ClassDef):
            for fn in cls.body:
                if isinstance(fn, ast.FunctionDef) and fn.name.startswith('test_'):
                    method_ast[cls.name+'.'+fn.name] = hashlib.sha256(ast.dump(fn, include_attributes=False).encode()).hexdigest()
    class Observed(unittest.TextTestResult):
        def startTest(self, test):
            self.case_started = time.monotonic(); self.case_utc = stamp()
            event({'phase': 'case-start', 'case': test.id()}); super().startTest(test)
        def record(self, test, result, detail=None):
            identity = type(test).__name__+'.'+test._testMethodName
            row = {'case': identity, 'result': result, 'actual_started_at': self.case_utc,
                'finished_at': stamp(), 'duration_seconds': time.monotonic()-self.case_started,
                'method_AST_sha256': method_ast[identity]}
            if detail: row['detail'] = detail
            cases.append(row); event(dict(phase='case-terminal', **row))
        def addSuccess(self, test): super().addSuccess(test); self.record(test, 'PASS')
        def addFailure(self, test, err):
            super().addFailure(test, err); self.record(test, 'FAIL', self._exc_info_to_string(err, test))
        def addError(self, test, err):
            super().addError(test, err); self.record(test, 'ERROR', self._exc_info_to_string(err, test))
    reader_suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.ReaderCases)
    graph_suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.GraphCases)
    reader_count = reader_suite.countTestCases(); graph_count = graph_suite.countTestCases()
    reader_result = unittest.TextTestRunner(verbosity=2, resultclass=Observed).run(reader_suite)
    event({'phase': 'checkpoint-reader', 'result': 'PASS' if reader_result.wasSuccessful() else 'FAIL', 'cases': reader_result.testsRun})
    graph_result = None
    if reader_result.wasSuccessful():
        graph_result = unittest.TextTestRunner(verbosity=2, resultclass=Observed).run(graph_suite)
        event({'phase': 'checkpoint-graph', 'result': 'PASS' if graph_result.wasSuccessful() else 'FAIL', 'cases': graph_result.testsRun})
    exit_error = None
    try: guard()
    except Exception as exc: exit_error = str(exc)
    cleanup = not list(HERE.glob('owned-reader-*')) and not list(HERE.glob('owned-graph-*'))
    passed = (reader_result.wasSuccessful() and graph_result is not None and graph_result.wasSuccessful()
              and exit_error is None and cleanup and len(cases) == reader_count+graph_count)
    report = {'schema_version': 'lab-T08-focused-qualification/v1-candidate',
        'result': 'PASS-FOCUSED-CANDIDATE' if passed else 'FAIL', 'started_at': started,
        'finished_at': stamp(), 'duration_seconds': time.monotonic()-begin,
        'input_manifest_binding': {'path': str(manifest_path.relative_to(ROOT)), 'sha256': args.input_manifest_sha256},
        'environment': versions, 'reader_cases_expected': reader_count, 'graph_cases_expected': graph_count,
        'cases': cases, 'entry_guard_passed': True, 'exit_guard_error': exit_error,
        'owned_scratch_removed': cleanup, 'private_key_files_written': False,
        'full_size_table_is_technical_fixture': True, 'production_host_inputs_accessed': False,
        'original_API16_full_history_guard_performed': False,
        'original_public_schema_and_role_bytes_selected': True,
        'ordinary_Vault_limit_changed': False, 'original_v1_readers_or_graphs_changed': False,
        'actual_owner_outcome': None, 'whole_API_qualified': False, 'canonical_admissions': 0,
        'runtime_activations': 0, 'authority_effect': 'none', 'task_complete': False,
        'claim_ceiling': 'New protected reader and explicitly selected original-schema graph technical fixtures only; production full closure/custody/eligibility and shared API integration still required.'}
    event({'phase': 'terminal', 'result': report['result'], 'owned_scratch_removed': cleanup,
           'full_component_input_exit_guard_passed': exit_error is None})
    events.close()
    report['events_binding'] = {'path': str(events_path.relative_to(ROOT)), 'sha256': sha(events_path)}
    with report_path.open('x') as f: json.dump(report, f, indent=2); f.write('\n')
    print(json.dumps({'result': report['result'], 'cases': len(cases),
                      'report_sha256': sha(report_path), 'owned_scratch_removed': cleanup}), flush=True)
    return 0 if passed else 1

if __name__ == '__main__': raise SystemExit(main())
