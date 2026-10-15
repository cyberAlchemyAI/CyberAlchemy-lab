"""Task-local focused caller qualification, no live API/source replay."""
import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from datetime import datetime, timezone

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def guard():
    sources = json.loads((HERE / 'context.json').read_bytes())['selected_sources']
    for row in sources:
        if binding(ROOT / row['path'])['sha256'] != row['sha256']:
            raise AssertionError('Selected original source changed: ' + row['path'])
    return [binding(ROOT / row['path']) for row in sources]


started = datetime.now(timezone.utc).isoformat()
inputs = guard()
prior_rows=json.loads((HERE/'prior-revision-bindings.json').read_bytes())['files']
for row in prior_rows:
    assert binding(ROOT/row['path'])==row, 'Prior caller revision changed at entry'
code = [binding(HERE / name) for name in ('caller.py', 'caller_adapter.py', 'test_caller_adapter.py', 'qualify.py', 'fixtures.json')]
for row in code:
    if row['path'].endswith('.py'):
        ast.parse((ROOT / row['path']).read_bytes())
module_spec = importlib.util.spec_from_file_location('T04_focused_cases', HERE / 'test_caller_adapter.py')
module = importlib.util.module_from_spec(module_spec)
sys.modules[module_spec.name] = module
module_spec.loader.exec_module(module)
suite = unittest.defaultTestLoader.loadTestsFromModule(module)
expected = suite.countTestCases()
stream = io.StringIO()
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
log = stream.getvalue()
(HERE / 'qualification.log').write_text(log)
ended = datetime.now(timezone.utc).isoformat()
assert guard() == inputs, 'Original input drift at exit'
for row in prior_rows:
    assert binding(ROOT/row['path'])==row, 'Prior caller revision changed at exit'
assert all(binding(ROOT / row['path']) == row for row in code), 'Task code drift at exit'
residual = [p.name for p in HERE.glob('.owned-case-*')]
passed = result.wasSuccessful() and result.testsRun == expected == 31 and not result.skipped and not residual
report = {
    'schema_version': 'lab-task-caller-boundary-focused-qualification/v1-candidate',
    'task': 'T04', 'revision':'revision-0002', 'result': 'PASS' if passed else 'FAIL', 'started_at': started, 'ended_at': ended,
    'actual_command': [sys.executable, '-B', str(HERE / 'qualify.py')], 'actual_expected_exit': 0 if passed else 1,
    'interpreter': {'path': sys.executable, 'version': sys.version},
    'test_cases': result.testsRun, 'expected_cases': expected,
    'failures': [{'case': str(case), 'detail': detail} for case, detail in result.failures],
    'errors': [{'case': str(case), 'detail': detail} for case, detail in result.errors],
    'skips': result.skipped, 'syntax_checked': True,
    'original_selected_inputs_guarded_entry_exit': True, 'task_code_guarded_entry_exit': True, 'prior_revision_guarded_entry_exit': True,
    'original_source_bindings': inputs, 'executed_code_bindings': code,
    'log_binding': binding(HERE / 'qualification.log'),
    'owned_case_roots_removed': not residual, 'remaining_owned_roots': residual,
    'actual_live_API_calls': 0, 'runtime_full_history_guard_run': False,
    'native_store_or_private_live_key_access': False, 'production_or_original_callback_monkeypatches': False,
    'historical_envelopes_reauthenticated': False, 'whole_API_qualified': False,
    'actual_owner_outcome': None, 'goal_complete': False, 'authority_effect': 'none',
    'claim_ceiling': '31 focused caller policy/raw-frame-control/retained-byte/owned-journal/AST checks only. Historical missing original wire bytes are not invented. No live API16/17 authentication, expiry, runtime lifetime or full34 qualification.',
}
(HERE / 'qualification.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(log, end='')
print(json.dumps({'result': report['result'], 'cases': result.testsRun, 'report_binding': binding(HERE / 'qualification.json')}), flush=True)
raise SystemExit(0 if passed else 1)
