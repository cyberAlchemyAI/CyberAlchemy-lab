"""Retain every corrected public assertion and add two preclaim refusal cases."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, NEW = BASE / 'api48-typed-checks-v2', BASE / 'api49-typed-checks-v1'
API = BASE / 'api-v49'
SOURCE = '70a59c0f1c5cd96bedd523a024827a41e2b8f54f3ca0f6a685599ff4d6fe14aa'
PROFILE = '4ce85f563320da3b97d95b5f598053b2e2ec88f44bc1ec7e281c2aa22b4073c5'


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def methods(path):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    assert not NEW.exists()
    parent = json.loads((OLD / 'source-manifest.json').read_bytes())
    assert binding(OLD / 'source-manifest.json')['sha256'] == 'f0077decf35c6c8f94e15023ed4f310f0f0e18a9607992d1cacffee6133c6190'
    assert binding(API / 'source-manifest.json')['sha256'] == SOURCE
    assert binding(API / 'contract-profile.json')['sha256'] == PROFILE
    for row in parent['files']:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    NEW.mkdir()
    for path in OLD.glob('*.py'):
        (NEW / path.name).write_bytes(path.read_bytes())
    path = NEW / 'fixture.py'
    text = path.read_text().replace("assert mode in ('exact', 'bad-core', 'bad-review', 'duplicate-path')",
        "assert mode in ('exact', 'bad-core', 'bad-review', 'duplicate-path', 'mismatched-proposal', 'mismatched-successor')")
    anchor = '    metadata = {}\n'
    assert text.count(anchor) == 1
    text = text.replace(anchor, '''    if mode == 'mismatched-proposal':
        inspection['proposal_ref'] = 'fixture:deliberately-different-proposal'
    elif mode == 'mismatched-successor':
        inspection['successor_version_ref'] = 'fixture:deliberately-different-successor'
    metadata = {}
''')
    assert text.count('lab-typed-preparation-routing/v3-candidate') == 1
    text = text.replace('lab-typed-preparation-routing/v3-candidate', 'lab-typed-preparation-routing/v4-candidate')
    path.write_text(text)
    path = NEW / 'test_public_typed.py'
    with path.open('a') as stream:
        stream.write('''

    def test_09_mismatched_inspection_proposal_refused_before_claim(self):
        host, call, _ = self.example(mode='mismatched-proposal')
        before = self.journal(host)
        reply = self.invoke(host, call)
        self.assertEqual(reply['message']['code'], 'invalid-contract', reply)
        self.assertEqual(self.journal(host), before)
        self.assertLess(self.Auth.now(), self.Auth.instant(call['deadline']))

    def test_10_mismatched_inspection_successor_refused_before_claim(self):
        host, call, _ = self.example(mode='mismatched-successor')
        before = self.journal(host)
        reply = self.invoke(host, call)
        self.assertEqual(reply['message']['code'], 'invalid-contract', reply)
        self.assertEqual(self.journal(host), before)
        self.assertLess(self.Auth.now(), self.Auth.instant(call['deadline']))
''')
    old_methods, new_methods = methods(OLD / 'test_public_typed.py'), methods(path)
    assert len(old_methods) == 8 and len(new_methods) == 10
    assert all(new_methods[name] == value for name, value in old_methods.items())
    path = NEW / 'checks.py'
    text = path.read_text()
    text = text.replace("API = HERE.parent / 'api-v48'", "API = HERE.parent / 'api-v49'")
    text = text.replace('a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6', SOURCE)
    text = text.replace('080eaba1d670b1f660073a0554a601b3ee4eabd3be60d47dbe427df4ea4229f9', PROFILE)
    text = text.replace('_cal_API48_actual_typed_operation_checks_v2', '_cal_API49_actual_typed_operation_checks_v1')
    text = text.replace('_cal_API48_actual_typed_cases_v2', '_cal_API49_actual_typed_cases_v1')
    text = text.replace('suite.countTestCases() == 8', 'suite.countTestCases() == 10')
    text = text.replace('result.testsRun == 8', 'result.testsRun == 10')
    text = text.replace('all eight actual', 'all ten actual')
    path.write_text(text)
    context = RUN / 'context-R03-API49-public-typed-0001.json'
    emit(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'strict_coverage': 'PASS',
        'task': 'R03 full authenticated typed successor with preclaim identity refusal',
        'source_bindings': [binding(API / 'source-manifest.json'), binding(OLD / 'source-manifest.json'),
                           binding(RUN / 'authorization.json'), binding(RUN / 'API48-typed-binding-join-checks-0001.json')],
        'write_scope': NEW.relative_to(ROOT).as_posix(),
        'constraints': ['All eight original public method ASTs retained; two exact preclaim refusal cases added.',
            'Keep actual ReaderChannel, real policy bytes/clocks, original900-second bound and source/custody exit checks.',
            'No original production function or callback patched.',
            'Every candidate target remains synthetic; no genuine semantic owner verdict or operational scope grant.',
            'Run serially after the same current API48 driver completes all selected original suites.'],
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    rows = {row['path']: row for row in parent['files']}
    for row in json.loads((API / 'source-manifest.json').read_bytes())['files']:
        rows[row['path']] = row
    for path in list(NEW.glob('*.py')) + [OLD / 'source-manifest.json', API / 'source-manifest.json',
        API / 'contract-profile.json', context, Path(__file__).resolve()]:
        if path.suffix == '.py':
            ast.parse(path.read_bytes())
        row = binding(path)
        rows[row['path']] = row
    emit(NEW / 'source-manifest.json', {**parent, 'files': [rows[key] for key in sorted(rows)],
        'source_binding': binding(API / 'source-manifest.json'), 'parent_check_source_binding': binding(OLD / 'source-manifest.json'),
        'context_binding': binding(context), 'retained_original_method_count': 8, 'added_preclaim_cases': 2,
        'expected_actual_public_cases': 10, 'runtime_executed': False, 'task_complete': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': binding(NEW / 'source-manifest.json'),
                      'retained_public_methods': 8, 'added_preclaim_cases': 2, 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
