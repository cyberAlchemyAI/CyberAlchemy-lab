"""Exclusive successor for actual parent-channel composition and closed-peer errors."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, API = BASE / 'api-v51', BASE / 'api-v52'
HOST_OLD, HOST = BASE / 'lesson-host-composition-v1', BASE / 'lesson-host-composition-v2'
CHECK_OLD, CHECK = BASE / 'api51-lesson-checks-v1', BASE / 'api52-lesson-checks-v1'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def files(root):
    return sorted(p for p in root.rglob('*') if p.is_file()
                  and not {'receipts', '__pycache__'} & set(p.parts)
                  and p.name not in ('source-manifest.json', 'contract-profile.json'))


def copy_new(old, new):
    new.mkdir(exist_ok=False)
    for path in files(old):
        target = new / path.relative_to(old)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write(path.read_bytes())


def replace(path, old, new):
    text = path.read_text()
    assert text.count(old) == 1, (path, old)
    path.write_text(text.replace(old, new))


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    report = CHECK_OLD / 'receipts/checks-0001.json'
    failed = load(report)
    assert bind(report)['sha256'] == '655df97397aea62eaae0a1876a7752243ba86ac8ac8d2e80ec2f6b11b75e0685'
    assert failed['result'] == 'FAIL' and failed['errors'] == 3 and failed['actual_cases'] == 3
    terminal = RUN / 'API51-lesson3-terminal-0001.json'
    emit(terminal, {'schema_version': 'lab-actual-tool-terminal/v1-candidate',
        'session_id': 18103, 'initial_chunk_id': '2ba6a0', 'final_chunk_id': '9e5e9e',
        'actual_exit_code': 1, 'result': 'FAIL', 'actual_cases': 3, 'failures': 0, 'errors': 3,
        'full_selected_suite_completed': True, 'source_guarded_exit_completed': True,
        'report_binding': bind(report), 'log_binding': bind(CHECK_OLD / 'receipts/actual-0001.log'),
        'wire_binding': bind(CHECK_OLD / 'receipts/wire-0001.json'),
        'authority_effect': 'none', 'task_complete': False, 'goal_complete': False})
    spec = importlib.util.spec_from_file_location('_API52_predecessor_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('7444cec4a6d58c5cb851b876de79d4c52c2d392c55b53e64e1eb214788b2cf3c')
    copy_new(OLD, API)
    copy_new(HOST_OLD, HOST)
    copy_new(CHECK_OLD, CHECK)
    replace(HOST / 'host.py', "'api-v51/service.py'", "'api-v52/service.py'")
    replace(HOST / 'host.py', '                bridge = self.host.sessions.bridge',
        "                bridge = self.parent.sessions.bridge\n"
        "                require(bridge.channel is self.parent.channel and self.resource.bridge is bridge,\n"
        "                        'live Session parent reader channel differs')")
    replace(HOST / 'host.py', '                    evaluated = self.calculate(message, request, outer)',
        '                    self.peer.guard()\n                    evaluated = self.calculate(message, request, outer)')
    replace(API / 'lesson_selection.py', "'lesson-host-composition-v1'", "'lesson-host-composition-v2'")
    replace(API / 'lesson_selection.py', "+'_lesson_host_v1'", "+'_lesson_host_v2'")
    replace(API / 'machine_transport.py', '    def call(self, raw):\n        self.guard()',
        "    def call(self, raw):\n        try:\n            self.guard()\n        except Exception:\n"
        "            return importlib.import_module(self.Service.__module__).transport('unauthenticated-channel', raw)")
    replace(API / 'service.py', '        context=self.channel.context\n        value=',
        "        context=self.channel.context\n        if context is None:return transport('unauthenticated-channel',raw,call['call_id'])\n        value=")
    replace(CHECK / 'checks.py', "API=HERE.parent/'api-v51'", "API=HERE.parent/'api-v52'")
    for path in (CHECK / 'checks.py', CHECK / 'test_host.py'):
        path.write_text(path.read_text().replace('_cal_API51', '_cal_API52').replace('cal-API51-owned-lesson-', 'cal-API52-owned-lesson-'))
    assert methods(CHECK_OLD / 'test_host.py') == methods(CHECK / 'test_host.py'), 'three regression assertions changed'
    retained = []
    for path in files(OLD):
        if path.suffix == '.py':
            assert methods(path) == methods(API / path.relative_to(OLD)), path
            retained += [str(path.relative_to(OLD)) + ':' + name for name in methods(path)]
    assert len(retained) == 293
    for path in files(API) + files(HOST) + files(CHECK):
        if path.suffix == '.py':
            ast.parse(path.read_bytes())
    (HOST / 'README.md').write_text('''# Lesson host composition v2 candidate

The actual live Session was opened through its parent ReaderChannel. Register
that exact parent bridge with the unchanged fact-read kernel. The authenticated
Machine peer and live resource are still checked inside and outside the scope;
the parent policy is reread by the original channel guard. No source callback,
registry, permission, deadline or Session object is replaced.

Disposed or revoked peers return the original unauthenticated transport error.
The reply path cannot construct a trusted result from a cleared channel context.
The three original lesson assertions and all 293 inherited methods are retained.
API51's three errors and actual exit 1 are preserved. API52 has no runtime
qualification until its own exact frozen source checks finish successfully.
The signed source is still empty of Lessons; nonempty qualification remains.
''')
    static = RUN / 'API52-lesson-host-repair-static-0001.json'
    emit(static, {'schema_version': 'lab-lesson-host-repair-static/v1-candidate', 'result': 'PASS',
        'retained_inherited_methods': 293, 'retained_lesson_regression_methods': 3,
        'parent_channel_scope_selected': True, 'original_fact_scope_kernels_unchanged': True,
        'original_clocks_and_callbacks_unchanged': True, 'authored_handlers': 18, 'missing_operations': 16,
        'failed_predecessor_terminal_binding': bind(terminal), 'actual_public_calls': 0,
        'runtime_qualified': False, 'authority_effect': 'none', 'task_complete': False})
    profile = load(OLD / 'contract-profile.json')
    profile['files'] = [bind(API / (ROOT / row['path']).relative_to(OLD))
        if (ROOT / row['path']).is_relative_to(OLD) else row for row in profile['files']]
    profile['files'] += [bind(p) for p in files(HOST) + files(CHECK)] + [bind(static)]
    profile['claim_ceiling'] = 'Eighteen authored handlers; API51 failure preserved; parent channel repair authored. API52 runtime and nonempty Lesson qualification pending.'
    emit(API / 'contract-profile.json', profile)
    rows = {row['path']: row for row in parent['files']}
    for path in files(API) + files(HOST) + files(CHECK) + [OLD / 'source-manifest.json',
            API / 'contract-profile.json', report, terminal, static, Path(__file__).resolve()]:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    emit(API / 'source-manifest.json', {**parent, 'files': [rows[k] for k in sorted(rows)],
        'parent_source_binding': bind(OLD / 'source-manifest.json'),
        'retained_inherited_methods': retained, 'unchanged_inherited_method_count': 293,
        'failed_predecessor_terminal_binding': bind(terminal), 'whole_API_qualified': False,
        'current_Agent_qualified': False, 'lesson_nonempty_signed_source_qualified': False,
        'task_complete': False, 'goal_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
        'profile_binding': bind(API / 'contract-profile.json'), 'retained_original_methods': 293,
        'retained_lesson_regression_methods': 3, 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
