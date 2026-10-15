"""Check full failure fixture authoring without creating a host or signer."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from jsonschema import Draft202012Validator

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
INTERFACE = ROOT / 'product/lab/release-candidates/v1/interface'
API = INTERFACE / 'api-v39'
PARENT = INTERFACE / 'api-v38'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def put(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')


def methods(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}


def main():
    rows = {}; cases = []
    def add(path):
        row = bind(path); assert rows.get(row['path'], row) == row
        rows[row['path']] = row
    def check(name, condition):
        assert condition, name
        cases.append({'case': name, 'result': 'PASS'})
    name = '_cal_API39_fixture_schema_authoring_final'
    spec = importlib.util.spec_from_file_location(name, API / '__init__.py', submodule_search_locations=[str(API)])
    package = importlib.util.module_from_spec(spec); sys.modules[name] = package; spec.loader.exec_module(package)
    fixture = __import__(name + '.failure_fixture', fromlist=['failure_bodies'])
    mapper = INTERFACE / 'current-mapped-context-v3/packages/0001/mapping.json'
    mapping = json.loads(mapper.read_bytes())
    header = next(row['artifact'] for row in mapping['rows'] if row['artifact']['identity_ref'] == 'product:cyberalchemy-lab')
    registry = ROOT / 'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
    catalog = json.loads(registry.read_bytes())['admitted_contracts']
    for mode in ['single', 'threshold-met', 'threshold-missed', 'threshold-unknown',
                 'unknown-rule', 'invalid-schema', 'bad-core', 'independent-recovery', 'conflict']:
        nodes, edges, _ = fixture.failure_bodies(header['scope_ref'], header, mode)
        by_identity = {body['node_id']: body for body in nodes}
        for body in nodes:
            carrier = 'cal.artifact-type.' + body['kind'] + '/v1'
            entry = next(row for row in catalog if row['artifact_type_ref'] == carrier)
            schema = ROOT / entry['schema_path']; add(schema); add(schema.parent / 'fixtures/valid/record.json')
            check(mode + ': ' + body['kind'] + ' original schema',
                  Draft202012Validator(json.loads(schema.read_bytes())).is_valid(body)
                  == (not (mode == 'invalid-schema' and body['kind'] == 'failure-assessment')))
        for left, right, kind, qualifiers in edges:
            check(mode + ': ' + kind + ' distinct selected endpoints',
                  left is by_identity[left['node_id']] and right is by_identity[right['node_id']])
            path = ROOT / 'authority/relation-kinds/candidates/0007-governance-transaction-extension/instances/relation-kinds' / (kind.split('.')[-1] + '.json')
            if not path.exists():
                path = ROOT / 'authority/relation-kinds/candidates/0006-definition-complete-instances/instances/relation-kinds' / path.name
            add(path); signature = json.loads(path.read_bytes())['payload']
            check(mode + ': ' + kind + ' original endpoint pair',
                  {'source_kind': left['kind'], 'target_kind': right['kind']} in signature['allowed_endpoint_pairs'])
            contract = signature['qualifier_contract']
            check(mode + ': ' + kind + ' closed qualifiers',
                  set(qualifiers) == set(contract['required_axes'])
                  and all(Draft202012Validator(contract['properties'][key]).is_valid(value) for key, value in qualifiers.items()))
    nodes, edges, _ = fixture.failure_bodies(header['scope_ref'], header, 'single')
    check('Baseline8 nodes and5 distinct Typed Relations', len(nodes) == 8 and len(edges) == 5)
    check('All18 public failure cases authored', len(methods(API / 'test_failure_api.py')) == 18)
    retained = 0
    for path in PARENT.rglob('*.py'):
        if 'receipts' in path.parts or '__pycache__' in path.parts: continue
        check('Inherited method ASTs retained ' + path.name, methods(path) == methods(API / path.relative_to(PARENT)))
        retained += len(methods(path))
    check('All275 inherited obligations retained', retained == 275)
    check('Original policy source guard executes once', (API / 'auth.py').read_text().count('        borrowed=FACT_SCOPE.policy_scope(self)') == 1)
    for filename in ['api-call.schema.json', 'api-reply.schema.json']:
        check('Original34-operation ' + filename + ' unchanged',
              (API / 'schemas' / filename).read_bytes() == (PARENT / 'schemas' / filename).read_bytes())
    for directory in [API, INTERFACE / 'failure-preparation-v1', INTERFACE / 'classification-preparation-v4']:
        for path in directory.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                if path.suffix == '.py': ast.parse(path.read_bytes())
                add(path)
    for path in [registry, mapper, INTERFACE / 'failure-assessment-rules-v8/receipts/proof-0001.json', Path(__file__).resolve()]: add(path)
    inputs = RUN / 'API39-failure-fixture-authoring-inputs-0002.json'
    put(inputs, {'files': [rows[key] for key in sorted(rows)], 'authority_effect': 'none', 'actual_runtime_fixtures': 0})
    for row in rows.values(): assert bind(ROOT / row['path']) == row
    report = RUN / 'API39-failure-fixture-authoring-checks-0002.json'
    put(report, {'result': 'PASS', 'actual_checks': len(cases), 'checks': cases, 'input_binding': bind(inputs),
                 'fixture_schema_examples_are_synthetic': True, 'retained_inherited_methods': 275,
                 'new_public_case_count': 18, 'actual_public_calls': 0, 'actual_runtime_fixtures': 0,
                 'source_frozen': False, 'runtime_qualified': False, 'authority_effect': 'none'})
    print(json.dumps({'result': 'PASS', 'checks': len(cases), 'new_public_cases': 18, 'inputs': bind(inputs)}), flush=True)


if __name__ == '__main__': main()
