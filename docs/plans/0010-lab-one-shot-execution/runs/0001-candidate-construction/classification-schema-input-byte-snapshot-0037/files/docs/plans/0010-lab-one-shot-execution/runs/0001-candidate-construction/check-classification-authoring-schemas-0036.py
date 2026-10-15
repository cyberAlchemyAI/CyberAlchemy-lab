"""Offline schema/AST authoring checks; creates no host, signer or Session."""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-v36'
ORIGINAL = API.parent / 'api-v35'
SCHEMAS = ROOT / 'docs/proposals/0007-lab-integrated-schema-package'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-sha256', required=True)
    args = parser.parse_args()
    source = RUN / 'classification-authoring-schema-inputs-0036.json'
    assert sha(source) == args.source_sha256
    inputs = json.loads(source.read_bytes())
    for row in inputs['files']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    spec = importlib.util.spec_from_file_location('_classification_authoring_offline_resources', SCHEMAS / 'resources.py')
    resources = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(resources)
    registry = resources.build_registry()
    auth = json.loads((API / 'authentication.schema.json').read_bytes())
    Draft202012Validator.check_schema(auth)
    validator = Draft202012Validator(auth, registry=registry, format_checker=FormatChecker())
    original = json.loads((ORIGINAL / 'authentication.schema.json').read_bytes())
    assert auth['oneOf'][:-1] == original['oneOf']
    policy_schema = auth['oneOf'][-1]
    grant = policy_schema['properties']['allowed_operations']['const']
    assert grant == ['lab.status', 'catalog.get', 'artifact.inspect', 'artifact.query',
                     'change.prepare', 'change.validate', 'operation.inspect',
                     'projection.refresh', 'classification.prepare']
    public = json.loads((API.parent / 'current-context-delivery-v8/packages/0001/host-permission-public.json').read_bytes())
    # This object tests only schema shape. It names no existing workspace and
    # is never given to ReaderChannel or any authentication/dispatch function.
    policy = {'schema_version': 'lab-local-classification-candidate-policy/v1-candidate',
              'principal_ref': 'principal:synthetic-schema-shape-only',
              'reader_public_key': public['reader_public_key'], 'host_uid': os.getuid(),
              'source_name': 'custody-participation', 'scope_refs': ['scope:synthetic-schema-only'],
              'expires_at': public['expires_at'], 'max_request_bytes': 1048576,
              'max_response_bytes': 1048576, 'max_calls': 128, 'allowed_operations': grant,
              'revoked': False, 'scope_posture': 'isolated-candidate-preparation',
              'authority_effect': 'none', 'actual_owner_outcome': None,
              'workspace': {'root': '/tmp/nonexistent-schema-shape-only', 'manifest_sha256': '0' * 64, 'max_actions': 8},
              'session_control': None, 'projection_control': None,
              'purpose': 'durable-metadata-and-exact-classification-preparation',
              'development_authorization_binding': {'ref': 'schema-shape-only', 'sha256': '0' * 64},
              'scope_control': None,
              'classification_control': {'routing_binding': {'ref': 'schema-shape-only', 'sha256': '0' * 64}}}
    checks = []

    def check(value, name):
        assert value, name
        checks.append(name)

    check(validator.is_valid(policy), 'closed classification policy schema shape')
    for label, mutate in [
        ('missing routing control', lambda row: row.pop('classification_control')),
        ('unknown policy field', lambda row: row.update(undeclared=True)),
        ('unknown routing control field', lambda row: row['classification_control'].update(undeclared=True)),
        ('owner outcome', lambda row: row.update(actual_owner_outcome='admitted')),
        ('authority effect', lambda row: row.update(authority_effect='admission')),
        ('added operation', lambda row: row['allowed_operations'].append('admission.apply')),
        ('removed operation', lambda row: row['allowed_operations'].pop()),
        ('wrong purpose', lambda row: row.update(purpose='runtime-activation')),
    ]:
        changed = copy.deepcopy(policy)
        mutate(changed)
        check(not validator.is_valid(changed), 'refuse schema shape: ' + label)
    check(auth['oneOf'][:-1] == original['oneOf'], 'all seven existing authentication variants unchanged')
    for name in ['classification_preparation.py', 'classification_fixture.py', 'test_classification_api.py',
                 'checks_classification.py', 'freeze_classification.py', 'service.py', 'auth.py']:
        ast.parse((API / name).read_bytes())
        checks.append('authored syntax: ' + name)
    cases = [node for node in ast.walk(ast.parse((API / 'test_classification_api.py').read_bytes()))
             if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
    check(len(cases) == 16, 'all sixteen authored public classification cases retained')
    for row in inputs['files']:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    result = {'schema_version': 'lab-classification-authoring-checks/v1-candidate', 'result': 'PASS',
              'source_sha256': args.source_sha256, 'checks': checks,
              'scope': 'Offline schema shape, preserved authentication branches and authored AST inventory only.',
              'actual_public_calls': 0, 'host_permissions_granted': 0, 'signers_created': 0,
              'actual_Agents_created': 0, 'Session_created': 0, 'runtime_qualified': False,
              'actual_owner_outcome': None, 'authority_effect': 'none', 'task_complete': False}
    with (RUN / 'classification-authoring-schema-checks-0036.json').open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'checks': len(checks), 'runtime_qualified': False}), flush=True)


if __name__ == '__main__':
    main()
