"""ISB-02 candidate contract validation only. No service execution. See README.md."""
from pathlib import Path
import json
from jsonschema import Draft202012Validator

BASE = Path(__file__).resolve().parent
SCHEMA = json.loads((BASE / 'service.schema.json').read_text())
Draft202012Validator.check_schema(SCHEMA)


def validate_service(value):
    Draft202012Validator(SCHEMA).validate(value)
    def unique(rows, key, label):
        values = [key(row) for row in rows]
        if len(set(values)) != len(values):
            raise ValueError('DUPLICATE_' + label)
    unique(value['functions'], lambda row: row['id'], 'FUNCTION')
    unique(value['routes'], lambda row: row['id'], 'ROUTE_ID')
    unique(value['routes'], lambda row: (row['method'], row['path']), 'ROUTE')
    unique(value['query_iterations'], lambda row: row['id'], 'ITERATION')
    unique(value['error_policy']['mappings'], lambda row: row['code'], 'ERROR_CODE')
    funcs = {row['id']: row for row in value['functions']}
    for route in value['routes']:
        if route['function_ref'] not in funcs:
            raise ValueError('UNRESOLVED_ROUTE_FUNCTION')
        if route['error_policy_ref'] != value['error_policy']['id']:
            raise ValueError('UNRESOLVED_ERROR_POLICY')
        if route['method'] == 'GET' and funcs[route['function_ref']]['kind'] != 'query':
            raise ValueError('GET_REQUIRES_QUERY')
        if route['response'] == 'json-or-sse' and 'response-stream-v1' not in value['dependencies']:
            raise ValueError('STREAM_DEPENDENCY_REQUIRED')
    for iteration in value['query_iterations']:
        selected = []
        for field, kind in [('source_query_ref', 'query'), ('item_query_ref', 'query'), ('input_mapping_ref', 'mapping')]:
            function = funcs.get(iteration[field])
            if function is None:
                raise ValueError('UNRESOLVED_ITERATION_FUNCTION')
            if function['kind'] != kind:
                raise ValueError('ITERATION_REQUIRES_PURE_QUERY_AND_MAPPING')
            selected.append(function)
        source, item, mapping = selected
        if not source['output_type'].endswith('[]'):
            raise ValueError('ITERATION_SOURCE_REQUIRES_LIST')
        if mapping['output_type'] != item['input_type']:
            raise ValueError('ITERATION_INPUT_TYPE_MISMATCH')
        if iteration['max_output_bytes'] > value['limits']['response_bytes']:
            raise ValueError('ITERATION_EXCEEDS_SERVICE_LIMIT')
    if value['limits']['event_bytes'] > value['limits']['response_bytes']:
        raise ValueError('EVENT_EXCEEDS_RESPONSE_LIMIT')
    if value['custody'] is not None and value['custody']['dependency_ref'] not in value['dependencies']:
        raise ValueError('CUSTODY_DEPENDENCY_REQUIRED')
    for function in value['functions']:
        if not set(function['dependencies']) <= set(value['dependencies']):
            raise ValueError('FUNCTION_DEPENDENCY_UNDECLARED')
        if function['kind'] in ['query', 'mapping'] and function['dependencies']:
            raise ValueError('PURE_FUNCTION_EFFECT_FORBIDDEN')
    return value


def trace_stream(contract, events):
    """Evaluate the declared transition table as a specification witness, not I/O."""
    state = contract['initial']
    for event in events:
        choices = [row for row in contract['transitions'] if row['from'] == state and row['event'] == event]
        if state in contract['terminal'] or len(choices) != 1:
            raise ValueError('INVALID_TRANSITION')
        state = choices[0]['to']
    return state


if __name__ == '__main__':
    validate_service(json.loads((BASE / 'service.example.json').read_text()))
    print('PASS: candidate service contract; compilation and runtime execution remain later units.')
