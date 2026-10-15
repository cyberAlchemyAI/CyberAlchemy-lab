"""Freeze actual v8 host integration and explicit classification test successor."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, API = BASE / 'api-v55', BASE / 'api-v56'
CHECK = BASE / 'api56-classification-checks-v1'
COMPOSITION = BASE / 'classification-preparation-v8'
LESSON = BASE / 'lesson-host-composition-v6'


def load(path):
    return json.loads(path.read_bytes())


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def files(path):
    return sorted(p for p in path.rglob('*') if p.is_file() and not {'receipts', '__pycache__'} & set(p.parts)
                  and p.name not in ('source-manifest.json', 'contract-profile.json'))


def emit(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def tests(path):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}


def main():
    spec = importlib.util.spec_from_file_location('_cal_API56_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    parent = guard.verify('ded6259462a19cfa8da1c5e6bdb7da0e1c04ff98f137c8a3250add64a41d0674')
    inherited = []
    for path in files(OLD):
        if path.suffix == '.py':
            assert tests(path) == tests(API / path.relative_to(OLD)), path
            inherited.extend(path.relative_to(OLD).as_posix() + ':' + name for name in tests(path))
    assert len(inherited) == 293
    original = tests(API / 'test_classification_api.py')
    revised = tests(CHECK / 'test_classification_api.py')
    assert len(original) == len(revised) == 16 and set(original) == set(revised)
    changed = [n for n in original if original[n] != revised[n]]
    assert changed == ['test_09_independent_axis_is_preserved']
    assert original['test_12_wrong_original_stable_core_is_not_classified'] == revised['test_12_wrong_original_stable_core_is_not_classified']
    assert original['test_16_uncertain_core_failure_stays_pending_without_redispatch'] == revised['test_16_uncertain_core_failure_stays_pending_without_redispatch']
    for path in files(API) + files(CHECK) + files(COMPOSITION) + files(LESSON):
        if path.suffix == '.py':
            ast.parse(path.read_bytes())
    doc = API / 'CLASSIFICATION-INTEGRATION.md'
    with doc.open('x') as stream:
        stream.write('''# Classification evidence and axis qualification successor

API56 selects the authored classification-preparation-v8 composition. The earlier
v8 design records its unbound authoring stage; this document records its actual
host binding. The original v7 and failed API50 evidence remain unchanged.

A native failed validation with incomplete stable cores raises the distinct
PendingValidationRefusal. Only that explicit native outcome and existing known
RuleFailure are caught within the composition. Full original source and current
policy exit checks then run; staged native verification evidence commits outside
the pure scope. PendingValidationRefusal is rethrown after commit as an ordinary
operation error, preserving the durable pending key, indeterminate response and
recovery-required retry. No command result, classifier result or admission follows.
Unexpected errors and failed source exit checks still discard staged evidence.

The frozen API retains all 293 inherited method ASTs and 34 original contracts.
A separate bound qualification copy retains all16 classification cases. Its only
method successor corrects the independent-axis target count from five to nine and
adds exact proposal, five-domain/four-relation split, original relation signature,
endpoint and qualifier checks. The single-axis five-target check remains. Both
original bad-core/pending methods are byte-for-byte unchanged in AST form.

Actual focused and complete classification qualification remains required.
API55 expiry and affected-journey proofs belong to their exact predecessor and
do not qualify this whole successor. Nineteen handlers are authored; fifteen
operations, full package portability/export, nonempty lesson/ontology sources,
Machine write authority, genuine pilot and final S02/R08 work remain unfinished.
''')
    static = RUN / 'API56-classification-static-0001.json'
    emit(static, {'schema_version': 'lab-classification-host-static/v1-candidate', 'result': 'PASS',
        'retained_original_operation_contracts': 34, 'retained_inherited_methods': 293,
        'separate_original_classification_cases': 16, 'separate_changed_methods': changed,
        'original_bad_core_and_pending_methods_unchanged': True,
        'authored_handlers': 19, 'missing_operations': 15, 'actual_public_calls': 0,
        'actual_runtime_qualified': False, 'whole_API_qualified': False,
        'authority_effect': 'none', 'actual_owner_outcome': None, 'task_complete': False, 'goal_complete': False})
    profile = load(OLD / 'contract-profile.json')
    profile['files'] = [bind(API / (ROOT / row['path']).relative_to(OLD))
        if (ROOT / row['path']).is_relative_to(OLD) else row for row in profile['files']]
    extra = [bind(p) for p in files(API) if not (OLD / p.relative_to(API)).exists()]
    extra += [bind(p) for folder in (CHECK, COMPOSITION, LESSON) for p in files(folder)]
    extra += [bind(static), bind(RUN / 'CLASSIFICATION-GAPS-0001.md')]
    rows = {r['path']: r for r in profile['files'] + extra}
    profile['files'] = [rows[k] for k in sorted(rows)]
    profile['claim_ceiling'] = 'Nineteen authored handlers with v8 classification host binding; actual focused/full qualification pending. Separate exact axis-count successor preserves original test source. Fifteen operations and whole plan/API qualification remain incomplete.'
    emit(API / 'contract-profile.json', profile)
    rows = {r['path']: r for r in parent['files']}
    for row in extra:
        rows[row['path']] = row
    for path in files(API) + files(CHECK) + files(COMPOSITION) + files(LESSON) + [OLD / 'source-manifest.json',
            API / 'contract-profile.json', Path(__file__).resolve(), RUN / 'author-API56-classification-0001.py',
            RUN / 'API55-expiry2-terminal-0001.json',
            BASE / 'api55-session-checks-v1/receipts/checks-0001.json',
            BASE / 'api55-session-checks-v1/receipts/actual-0001.log',
            BASE / 'api55-session-checks-v1/receipts/wire-0001.json']:
        row = bind(path)
        rows[row['path']] = row
    for row in rows.values():
        assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], row['path']
    emit(API / 'source-manifest.json', {**parent, 'files': [rows[k] for k in sorted(rows)],
        'parent_source_binding': bind(OLD / 'source-manifest.json'), 'retained_inherited_methods': inherited,
        'unchanged_inherited_method_count': 293, 'whole_API_qualified': False,
        'original_expiry_runtime_qualified': False, 'classification_actual_runtime_qualified': False,
        'task_complete': False, 'goal_complete': False})
    selection = [bind(p) for p in files(CHECK)] + [bind(API / 'source-manifest.json'),
        bind(API / 'contract-profile.json'), bind(API / 'test_classification_api.py'),
        bind(static), bind(RUN / 'CLASSIFICATION-GAPS-0001.md')]
    emit(CHECK / 'source-manifest.json', {'schema_version': 'lab-separate-classification-check-source/v1-candidate',
        'files': selection, 'original_classification_methods': 16, 'changed_methods': changed,
        'actual_runtime_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None})
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(API / 'source-manifest.json'),
        'profile_binding': bind(API / 'contract-profile.json'), 'check_source_binding': bind(CHECK / 'source-manifest.json'),
        'retained_original_methods': 293, 'separate_retained_cases': 16,
        'changed_methods': changed, 'actual_runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
