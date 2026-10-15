"""Declare execution selection and retain complete qualification before effects."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
PARENT = HERE.parent / 'current-context-delivery-v6'
MAPPED = HERE.parent / 'current-mapped-context-v3'
API = HERE.parent / 'api-v25'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load(path):
    return json.loads(path.read_bytes())


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def methods_normalized(path):
    text = path.read_text().replace('current-source-adapter-v2/reader.py#SelectedReader.open_signed', 'current-source-adapter-v3/reader.py#SelectedReader.open_signed')
    return {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(text)) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    out = HERE / 'source-manifest.json'
    execution_path = HERE / 'EXECUTION-DEPENDENCIES.json'
    context = RUN / 'context-R03-current-context-delivery-0007.json'
    assert not out.exists() and not execution_path.exists() and not context.exists()
    assert not (HERE / 'packages').exists()
    parent_source = PARENT / 'source-manifest.json'
    parent_proof = PARENT / 'receipts/qualification-0001.json'
    assert bind(parent_source)['sha256'] == 'd3ecda8d3c796e402e87efa25036ca4867534966ad4e50acb83741dc4fa9b010'
    proof = load(parent_proof)
    assert proof['result'] == 'PASS' and proof['selected_methods'] == 50
    assert proof['actual_build_exit_code'] == proof['actual_check_exit_code'] == proof['actual_audit_exit_code'] == 0
    observed_path = RUN / 'execution-dependency-observation-0002.json'
    observed = load(observed_path)
    observed_proof = RUN / 'execution-dependency-observation-proof-0002.json'
    assert load(observed_proof)['actual_terminal_exit_code'] == 0
    assert observed['result'] == 'PASS' and not observed['observed_unselected_nonbytecode_files']
    assert len(observed['actual_repository_exec_events']) == 30
    assert all(row['executed_code_matches_exact_source_compilation'] for row in observed['actual_repository_exec_events'])
    rows = {}

    def add(row):
        assert rows.get(row['path'], row) == row, row['path']
        assert bind(ROOT / row['path']) == row, row['path']
        rows[row['path']] = row

    for document in [proof, load(observed_proof), load(MAPPED / 'qualification-0001.json'), load(HERE.parent / 'current-source-adapter-v3/qualification-0001.json')]:
        for row in document['files']:
            add(row)
    inputs = [parent_source, parent_proof, observed_path, observed_proof,
              RUN / 'EXECUTION-DEPENDENCY-REVIEW-0001.md', RUN / 'authorization.json',
              RUN / 'construct-R03-current-context-0007.py', RUN / 'current-context-binding-revision-0007.json',
              MAPPED / 'qualification-0001.json', HERE.parent / 'current-source-adapter-v3/qualification-0001.json']
    for path in inputs:
        add(bind(path))
    for name in ['test_original_delivery.py', 'test_raw_delivery.py']:
        assert methods(HERE / name) == methods_normalized(PARENT / name), name
    assert sum(len(methods(HERE / name)) for name in ['test_original_delivery.py', 'test_raw_delivery.py']) == 50
    for path in HERE.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            if path.suffix == '.py':
                ast.parse(path.read_bytes())
            add(bind(path))
    execution = {}
    reasons = {}

    def select(row, reason):
        add(row)
        assert execution.get(row['path'], row) == row, row['path']
        execution[row['path']] = row
        reasons.setdefault(row['path'], [])
        if reason not in reasons[row['path']]:
            reasons[row['path']].append(reason)

    def declaration(path, reason):
        select(bind(path), reason + ': declaration bytes')
        for row in load(path)['files']:
            select(row, reason + ': declared guard input')

    declaration(MAPPED / 'source-manifest.json', 'Original mapper source guard')
    declaration(MAPPED / 'packages/0001/manifest.json', 'Exact mapped native package')
    declaration(API / 'schema-inputs.json', 'Original API schema closure')
    declaration(API / 'contract-profile.json', 'Original API profile closure')
    for key in ['original_operation_catalog_binding', 'original_schema_inputs_binding']:
        select(load(API / 'contract-profile.json')[key], 'Original API independent selection: ' + key)
    select(bind(Path('/tmp/cal-R03-mapped-native-build-0002/target/debug/lab-context-native-reader')), 'Independently selected native executable')
    for row in observed['observed_repository_read_files']:
        path = ROOT / row['path']
        if path.suffix == '.pyc':
            continue
        observed_context = HERE.parent / 'current-context-delivery-v5'
        if path.is_relative_to(observed_context):
            path = HERE / path.relative_to(observed_context)
        select(bind(path), 'Actual parent import/schema phase; corresponding successor path where applicable')
    production = ['__init__.py', 'base.py', 'build.py', 'control.py', 'generation.py',
                  'implementation-binding.json', 'lifetime-policy.json', 'run.py']
    for name in production:
        select(bind(HERE / name), 'Context production code or explicit configuration')
    for path in sorted((HERE / 'protocols').glob('*.json')):
        select(bind(path), 'Explicit Context protocol declaration')
    for kind in ['ontology-node', 'ontology-edge', 'ontology', 'ontology-cut', 'ontology-view', 'context-request', 'context-view']:
        version = 'v2' if kind == 'ontology-node' else 'v1'
        select(bind(ROOT / 'authority/artifact-types' / kind / version / 'fixtures/valid/record.json'), 'Actual generated-carrier template')
    for name in ['__init__.py', 'scope.py']:
        select(bind(HERE.parent / 'fact-read-scope-v1' / name), 'Original selected fact-scope implementation')
    selected = [execution[key] for key in sorted(execution)]
    put(execution_path, {'schema_version': 'lab-Context-execution-dependencies/v1-candidate',
                         'files': selected,
                         'external_dependency_bindings': [row for row in selected if Path(row['path']).is_absolute()],
                         'selection_reasons': {key: reasons[key] for key in sorted(reasons)},
                         'parent_qualification_binding': bind(parent_proof),
                         'observed_import_phase_binding': bind(observed_path),
                         'closure_status': 'declared-for-successor-qualification',
                         'actual_owner_outcome': None, 'authority_effect': 'none'})
    add(bind(execution_path))
    put(context, {'schema_version': 'lab-bounded-context/v1-candidate', 'task': 'R03 Context execution and qualification dependency separation',
                  'strict_coverage': 'PASS', 'blockers': [], 'source_bindings': [bind(path) for path in inputs] + [bind(execution_path), bind(HERE / 'DESIGN.md')],
                  'constraints': ['Complete immutable parent qualification retained; 49 original test method ASTs unchanged; sole reader path assertion explicitly rebound to qualified Reader3.',
                                  'Every execution input has an exact binding, explicit selecting reason and membership in full qualification.',
                                  'Original environment, source/mapper/package/schema, current permission, revocation and real clock checks remain.',
                                  'No deadline or period extension, permission cache, callback replacement, owner authority or admission.',
                                  'Declared selection is a candidate hypothesis until actual build/full50/independent audit and affected full API/lifecycle qualification.',
                                  'No file-count or component measurement proves end-to-end latency.'],
                  'authority_effect': 'none', 'actual_owner_outcome': None})
    add(bind(context))
    manifest = load(parent_source)
    manifest.update(files=[rows[key] for key in sorted(rows)],
                    external_dependency_bindings=[rows[key] for key in sorted(rows) if Path(key).is_absolute()],
                    context_binding=bind(context), execution_dependency_binding=bind(execution_path),
                    qualified_parent_Context_binding=bind(parent_proof), lifetime_policy_binding=bind(HERE / 'lifetime-policy.json'),
                    original48assertion_ASTs_preserved=False, original50assertion_ASTs_preserved=False,
                    original49assertion_ASTs_preserved=True, original50assertions_preserved_except_declared_reader_path=True,
                    reader_path_revision_binding=bind(RUN / 'current-context-binding-revision-0007.json'),
                    qualified_mapper_source_binding=bind(MAPPED / 'source-manifest.json'),
                    qualified_mapper_package_binding=bind(MAPPED / 'packages/0001/manifest.json'),
                    execution_dependency_selection_status='declared-pending-successor-qualification',
                    current_Context_successor_qualified=False, current_Agent_qualified=False, expected_tests=50,
                    actual_owner_outcome=None, authority_effect='none', task_complete=False)
    put(out, manifest)
    print(json.dumps({'result': 'FROZEN', 'source_binding': bind(out), 'execution_binding': bind(execution_path),
                      'qualification_files': len(rows), 'execution_files': len(selected),
                      'execution_bytes': sum((ROOT / row['path']).stat().st_size for row in selected),
                      'original_methods_preserved': 49, 'reader_path_assertion_rebound': 1, 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
