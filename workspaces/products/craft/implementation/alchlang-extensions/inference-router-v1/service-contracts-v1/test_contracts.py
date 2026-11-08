import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource
from validate import BASE, validate_service, trace_stream

VALUE = json.loads((BASE / 'service.example.json').read_text())
STATE = json.loads((BASE / 'stream-state.json').read_text())
ROOT = next(p for p in BASE.parents if (p / 'agent-routing/routes.json').exists())
DS = ROOT / 'craft/projects/domainspec-v2'


class Contracts(unittest.TestCase):
    def reject(self, change, code=None):
        candidate = copy.deepcopy(VALUE)
        change(candidate)
        with self.assertRaises((ValueError, ValidationError)) as result:
            validate_service(candidate)
        if code:
            self.assertIn(code, str(result.exception))

    def test_candidate_and_stateless_service(self):
        validate_service(VALUE)
        pure = copy.deepcopy(VALUE)
        pure['functions'] = [pure['functions'][0]]
        pure.update(service_id='catalog-only', routes=[pure['routes'][0]], query_iterations=[], dependencies=[], custody=None)
        validate_service(pure)

    def test_no_inline_code_secrets_or_client_destination(self):
        for key in ['code', 'secret', 'url', 'shell', 'tenant_id']:
            self.reject(lambda x: x.update({key: 'injected'}))
        self.reject(lambda x: x['routes'][0].update(source='execute arbitrary source'))

    def test_unique_and_resolved_routes(self):
        self.reject(lambda x: x['routes'].append(dict(x['routes'][0], id='other')), 'DUPLICATE_ROUTE')
        self.reject(lambda x: x['routes'][0].update(function_ref='unknown'), 'UNRESOLVED_ROUTE_FUNCTION')
        self.reject(lambda x: x['routes'][0].update(error_policy_ref='unknown'), 'UNRESOLVED_ERROR_POLICY')

    def test_get_cannot_execute_operation_or_read_body(self):
        self.reject(lambda x: x['routes'][0].update(function_ref='inference'), 'GET_REQUIRES_QUERY')
        self.reject(lambda x: x['routes'][0].update(input='json'))

    def test_iteration_is_bounded_and_pure(self):
        self.reject(lambda x: x['query_iterations'][0].update(item_query_ref='inference'), 'ITERATION_REQUIRES_PURE_QUERY_AND_MAPPING')
        self.reject(lambda x: x['query_iterations'][0].update(max_items=101))
        self.reject(lambda x: x['query_iterations'][0].update(concurrency=2))
        self.reject(lambda x: x['query_iterations'][0].update(partial_result='return'))

    def test_declared_effects_cannot_hide_inside_pure_functions(self):
        self.reject(lambda x: x['functions'][4].update(dependencies=['http-invocation-v1']), 'PURE_FUNCTION_EFFECT_FORBIDDEN')

    def test_iteration_reference_and_type_closure(self):
        self.reject(lambda x: x['query_iterations'][0].update(item_query_ref='unknown'), 'UNRESOLVED_ITERATION_FUNCTION')
        self.reject(lambda x: x['functions'][4].update(output_type='Alias'), 'ITERATION_SOURCE_REQUIRES_LIST')
        self.reject(lambda x: x['functions'][6].update(output_type='WrongInput'), 'ITERATION_INPUT_TYPE_MISMATCH')

    def test_no_hidden_retry_and_nested_budget_escalation(self):
        self.reject(lambda x: x['limits'].update(max_attempts=2))
        self.reject(lambda x: x['limits'].update(response_bytes=1000), 'ITERATION_EXCEEDS_SERVICE_LIMIT')
        self.reject(lambda x: x['limits'].update(deadline_ms=0))

    def test_stream_and_custody_require_declared_dependencies(self):
        self.reject(lambda x: x['dependencies'].remove('response-stream-v1'), 'STREAM_DEPENDENCY_REQUIRED')
        self.reject(lambda x: x['dependencies'].remove('request-custody-v1'), 'CUSTODY_DEPENDENCY_REQUIRED')
        self.reject(lambda x: x['custody'].update(stream_replay=True))
        self.reject(lambda x: x['custody'].update(storage='cross-host'))

    def test_errors_cannot_expose_exception_messages(self):
        self.reject(lambda x: x['error_policy'].update(envelope='exception-message'))
        self.reject(lambda x: x['error_policy'].update(unknown_status=200))
        self.reject(lambda x: x['error_policy']['mappings'].append(x['error_policy']['mappings'][0]), 'DUPLICATE_ERROR_CODE')

    def test_stream_valid_traces(self):
        for events, expected in [(['start', 'delta', 'delta', 'complete'], 'completed'), (['start', 'fail'], 'failed'), (['cancel'], 'cancelled'), (['fail'], 'failed')]:
            self.assertEqual(trace_stream(STATE, events), expected)

    def test_stream_invalid_traces(self):
        for events in [['delta'], ['complete'], ['start', 'complete', 'delta'], ['start', 'fail', 'complete'], ['cancel', 'start'], ['start', 'start']]:
            with self.assertRaisesRegex(ValueError, 'INVALID_TRANSITION'):
                trace_stream(STATE, events)

    def test_dependencies_conform_to_existing_domainspec_d45_schema(self):
        folder = DS / 'impl/system-integration/contracts'
        schemas = [json.loads((folder / name).read_text()) for name in ['dependency-contract-v1.schema.json', 'integration-reference-v1.schema.json']]
        registry = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in schemas)
        validator = Draft202012Validator(schemas[0], registry=registry)
        for contract in json.loads((BASE / 'dependency-contracts.json').read_text())['contracts']:
            validator.validate(contract)
            mutant = dict(contract, concern='Port')
            with self.assertRaises(ValidationError):
                validator.validate(mutant)


if __name__ == '__main__':
    unittest.main()
