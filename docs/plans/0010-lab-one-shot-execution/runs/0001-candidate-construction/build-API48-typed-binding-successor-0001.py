"""Preserve the failed fixture and align its exact original inspector identities.

The production host, policies, public schemas and all eight assertions stay
unchanged. This corrects two independent prototype names in a test fixture.
"""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, NEW = BASE / 'api48-typed-checks-v1', BASE / 'api48-typed-checks-v2'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    assert not NEW.exists()
    source = OLD / 'source-manifest.json'
    assert bind(source)['sha256'] == '6b1198c03909390be68f35b6cbbdc39a73084ff31f6b0ca9e448ffe28adcd03c'
    original = json.loads(source.read_bytes())
    for row in original['files']:
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
    NEW.mkdir()
    for path in OLD.glob('*.py'):
        (NEW / path.name).write_bytes(path.read_bytes())
    path = NEW / 'fixture.py'
    text = path.read_text()
    old = '    inspection = copy.deepcopy(fixture.inspection)\n'
    assert text.count(old) == 1
    text = text.replace(old, old + '''    # The postimage prototype and C14 inspector used distinct fixture names.
    # Join them before any exact proposal/review/scope bytes are published.
    proposal['proposal_ref'] = inspection['proposal_ref']
    relation_target = next(t for t in proposal['targets']
                           if t['artifact']['carrier_ref'] == 'cal.artifact-type.relation-kind/v2')
    inspection['successor_version_ref'] = relation_target['artifact']['version_ref']
''')
    path.write_text(text)
    old_ast, new_ast = ast.parse((OLD / 'fixture.py').read_bytes()), ast.parse(text)
    function = next(node for node in new_ast.body if isinstance(node, ast.FunctionDef) and node.name == 'example')
    start = next(i for i, node in enumerate(function.body)
                 if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == "proposal['proposal_ref']")
    assert ast.unparse(function.body[start + 2].targets[0]) == "inspection['successor_version_ref']"
    del function.body[start:start + 3]
    assert ast.dump(old_ast, include_attributes=False) == ast.dump(new_ast, include_attributes=False)
    assert (OLD / 'test_public_typed.py').read_bytes() == (NEW / 'test_public_typed.py').read_bytes()
    path = NEW / 'checks.py'
    text = path.read_text().replace('_cal_API48_actual_typed_operation_checks_v1', '_cal_API48_actual_typed_operation_checks_v2')
    text = text.replace('_cal_API48_actual_typed_cases_v1', '_cal_API48_actual_typed_cases_v2')
    path.write_text(text)
    context = RUN / 'context-R03-API48-typed-binding-successor-0001.json'
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'task': 'R03 correct exact fixture proposal and successor identity join',
        'strict_coverage': 'PASS', 'source_bindings': [bind(source), bind(BASE / 'api-v48/source-manifest.json'),
            bind(BASE / 'typed-extension-preparation-v11/adapter.py'), bind(OLD / 'fixture.py'), bind(OLD / 'test_public_typed.py'),
            bind(RUN / 'authorization.json')],
        'write_scope': NEW.relative_to(ROOT).as_posix(),
        'constraints': ['All eight actual public assertions remain byte-identical.',
            'Production source, real policy/clock predicates and original error/uncertainty handling remain unchanged.',
            'Only proposal_ref and inspection successor_version_ref are joined before exact candidate bindings.',
            'Scope/review profiles are rebuilt from the complete corrected proposal/inspection bytes.',
            'Full successor public execution remains serialized after the same current owned run.',
            'No genuine semantic owner verdict or operational scope grant is supplied by fixtures.'],
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    checks = RUN / 'API48-typed-binding-successor-static-0001.json'
    put(checks, {'schema_version': 'lab-typed-fixture-binding-static/v1-candidate', 'result': 'PASS',
        'original_public_test_methods': 8, 'all_original_public_assertions_byte_identical': True,
        'only_fixture_AST_additions': ["proposal['proposal_ref']=inspection['proposal_ref']",
            'select exact Relation Kind target', "inspection['successor_version_ref']=relation_target['artifact']['version_ref']"],
        'every_other_fixture_AST_unchanged': True, 'production_API_source_unchanged': True,
        'actual_public_calls': 0, 'runtime_successor_qualified': False,
        'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False})
    rows = {row['path']: row for row in original['files']}
    for path in list(NEW.glob('*.py')) + [source, context, checks, Path(__file__).resolve()]:
        row = bind(path)
        rows[row['path']] = row
    for path in NEW.glob('*.py'):
        ast.parse(path.read_bytes())
    put(NEW / 'source-manifest.json', {**original, 'files': [rows[key] for key in sorted(rows)],
        'parent_check_source_binding': bind(source), 'context_binding': bind(context), 'static_checks_binding': bind(checks),
        'all_original_public_assertions_byte_identical': True, 'runtime_executed': False})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(NEW / 'source-manifest.json'),
                      'original_assertions_retained': 8, 'production_API_source_unchanged': True}), flush=True)


if __name__ == '__main__':
    main()
