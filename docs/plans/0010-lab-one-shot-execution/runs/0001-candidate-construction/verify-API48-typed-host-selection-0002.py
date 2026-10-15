"""Complete pure inventory checks and exact offline policy/routing shape checks.

All fixtures here are explicitly shape-only. No public operation or grant exists.
"""
import copy
import hashlib
import importlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator, FormatChecker

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
API, HOST = BASE / 'api-v48', BASE / 'typed-host-composition-v3'
SOURCE = 'a7329574c52004e476fd822da9177375a484ffc380e27c84f437ffc8f66d08e6'
PROFILE = '080eaba1d670b1f660073a0554a601b3ee4eabd3be60d47dbe427df4ea4229f9'
HOST_SOURCE = 'f722728cdc57263944e5f7db65dd0b91d3e7f464f15c10297bb517b964db4a20'


def bind(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def package(name, path):
    spec = importlib.util.spec_from_file_location(name, path / '__init__.py', submodule_search_locations=[str(path)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)


def main():
    package('_cal_API48_typed_selection_API', API)
    guard = importlib.import_module('_cal_API48_typed_selection_API.guard')
    guard.verify(SOURCE)
    P = importlib.import_module('_cal_API48_typed_selection_API.protocol')
    schemas = P.Schemas(PROFILE)
    assert bind(HOST / 'source-manifest.json')['sha256'] == HOST_SOURCE
    package('_cal_API48_typed_selection_host_v3', HOST)
    tests = importlib.import_module('_cal_API48_typed_selection_host_v3.test_selection')
    prep = importlib.import_module('_cal_API48_typed_selection_host_v3.preparation')
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    assert suite.countTestCases() == 25
    cases = []
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            cases.append({'case': test.id(), 'result': 'PASS'})
        def addFailure(self, test, error):
            super().addFailure(test, error)
            cases.append({'case': test.id(), 'result': 'FAIL', 'detail': self._exc_info_to_string(error, test)})
        def addError(self, test, error):
            super().addError(test, error)
            cases.append({'case': test.id(), 'result': 'ERROR', 'detail': self._exc_info_to_string(error, test)})
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    assert result.wasSuccessful() and result.testsRun == 25
    helper_modules = prep.helpers()
    assert len(helper_modules) == 4
    cases.append({'case': 'exact complete helper source/proof including external migration pins', 'result': 'PASS'})
    b = {'ref': 'fixture:shape-only-no-permission', 'sha256': P.source.sha(b'{}')}
    cut = json.loads((RUN / 'typed-actual-source-comparison-0010.json').read_bytes())['selected_source_cut']
    route = {'schema_version': 'lab-typed-preparation-routing/v3-candidate',
        'scope_ref': 'project:shape-only-no-permission', 'source_cut': cut,
        'proposal_binding': b, 'inspection_binding': b, 'helper_source_binding': b, 'helper_proof_binding': b,
        'catalog_profile_binding': b, 'catalog_review_binding': b, 'catalog_snapshot_digest': 'a' * 64,
        'representation_profile_binding': b, 'canonical_writable_authority_ref': 'cal.artifact-type.typed-relation/v3',
        'schema_destinations': [{'schema_binding': b, 'runtime_schema_path': 'runtime/schemas/candidate.json'}],
        'scope_preparation_profile_binding': None, 'record_basis': 'complete-current-and-exact-prospective-postimage',
        'actual_owner_outcome': None, 'authority_effect': 'none'}
    route_validator = Draft202012Validator(json.loads((HOST / 'routing.schema.json').read_bytes()),
                                           registry=schemas.registry, format_checker=FormatChecker())
    def check(name, validator, value, expected):
        actual = validator.is_valid(value)
        assert actual is expected, (name, list(validator.iter_errors(value)))
        cases.append({'case': name, 'result': 'PASS', 'expected_shape_valid': expected})
    check('closed typed route', route_validator, route, True)
    for key, value in [('actor', {}), ('actual_runtime_grant', True), ('runtime_admission_authorized', True)]:
        invalid = copy.deepcopy(route)
        invalid[key] = value
        check('route refuses undeclared ' + key, route_validator, invalid, False)
    invalid = copy.deepcopy(route)
    invalid['schema_destinations'] *= 2
    check('route refuses duplicate destination row', route_validator, invalid, False)
    invalid = copy.deepcopy(route)
    invalid.pop('helper_proof_binding')
    check('route requires independent helper proof', route_validator, invalid, False)
    parent = json.loads((BASE / 'api-v47/authentication.schema.json').read_bytes())
    current = json.loads((API / 'authentication.schema.json').read_bytes())
    assert current['oneOf'][:-1] == parent['oneOf']
    cases.append({'case': 'all nine original authentication variants identical', 'result': 'PASS'})
    branch = current['oneOf'][-1]
    policy_validator = Draft202012Validator(branch, registry=schemas.registry, format_checker=FormatChecker())
    # Construct shape only from exact declared constants; public key and path
    # are placeholders and are never supplied to ReaderChannel.
    policy = {'schema_version': branch['properties']['schema_version']['const'],
        'principal_ref': 'principal:shape-only-no-permission', 'reader_public_key': 'A' * 43 + '=',
        'host_uid': 1000, 'source_name': 'custody-participation', 'scope_refs': ['project:shape-only-no-permission'],
        'expires_at': '2030-01-01T00:00:00+00:00', 'max_request_bytes': 1048576,
        'max_response_bytes': 1048576, 'max_calls': 1, 'allowed_operations': list(P.TYPED_SUPPORTED),
        'revoked': False, 'scope_posture': 'isolated-candidate-preparation', 'authority_effect': 'none',
        'actual_owner_outcome': None, 'workspace': {'root': '/tmp/shape-only-does-not-exist',
        'manifest_sha256': 'a' * 64, 'max_actions': 1}, 'session_control': None,
        'projection_control': None, 'purpose': 'durable-metadata-and-exact-typed-extension-preparation',
        'development_authorization_binding': {'ref': 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json', 'sha256': '4d3c34a7f19b4b47892b3fbf5673544b36b0517e516961adcc77722f5d08e906'}, 'scope_control': None, 'typed_control': {'routing_binding': b}}
    check('closed typed policy shape', policy_validator, policy, True)
    for key, value in [('session_memory', {'fabricated': True}), ('actual_runtime_grant', True), ('agent_instance_ref', 'fabricated')]:
        invalid = copy.deepcopy(policy)
        invalid[key] = value
        check('typed policy refuses undeclared ' + key, policy_validator, invalid, False)
    for label, action in [
        ('owner outcome', lambda value: value.update(actual_owner_outcome='admitted')),
        ('wildcard operation', lambda value: value['allowed_operations'].append('*')),
        ('missing route', lambda value: value.pop('typed_control')),
        ('route extra grant', lambda value: value['typed_control'].update(actual_runtime_grant=True)),
    ]:
        invalid = copy.deepcopy(policy)
        action(invalid)
        check('typed policy refuses ' + label, policy_validator, invalid, False)
    assert len(P.SUPPORTED) == 17 and schemas.profile['implemented_operations'] == list(P.SUPPORTED)
    assert len(schemas.operations) == 34
    cases.append({'case': 'seventeen declared handlers and all thirty-four original contracts', 'result': 'PASS'})
    guard.verify(SOURCE)
    rows = {row['path']: row for row in json.loads((API / 'source-manifest.json').read_bytes())['files']}
    for path in [API / 'source-manifest.json', Path(__file__).resolve()]:
        row = bind(path)
        rows[row['path']] = row
    value = {'schema_version': 'lab-typed-host-selection-checks/v1-candidate', 'result': 'PASS',
        'actual_cases': len(cases), 'pure_inventory_methods': 25, 'cases': cases,
        'API_source_binding': bind(API / 'source-manifest.json'), 'host_source_binding': bind(HOST / 'source-manifest.json'),
        'files': [rows[k] for k in sorted(rows)], 'actual_public_calls': 0, 'shape_only_policy_fixture': True,
        'public_typed_qualified': False, 'assigned_Agent_qualified': False, 'actual_runtime_grant': False,
        'task_complete': False, 'actual_owner_outcome': None, 'authority_effect': 'none',
        'claim_ceiling': 'Pure schema inventory, helper byte selection and offline policy/routing shape only; authenticated public execution and original full suites remain unqualified.'}
    with (RUN / 'API48-typed-host-selection-checks-0002.json').open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'result': 'PASS', 'actual_cases': len(cases), 'actual_public_calls': 0}), flush=True)


if __name__ == '__main__':
    main()
