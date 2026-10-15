"""Generate exact JSON-AST fixtures while retaining object order and duplicate keys.

The generator/byte parser are not formally verified. Concrete schema comparisons
are independent controls, not universal source refinement or authenticity.
"""
from copy import deepcopy
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
SCHEMA = ROOT / 'authority/artifact-types/intent-resolution/v1/schema.json'
FIXTURE = ROOT / 'authority/artifact-types/intent-resolution/v1/fixtures/valid/record.json'


class ObjectPairs(list):
    pass


class NumberToken(str):
    pass


class DuplicateKey(ValueError):
    pass


def binding(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def quote(value):
    return json.dumps(value, ensure_ascii=False)


def render(value):
    if isinstance(value, ObjectPairs):
        return 'Value.object [' + ', '.join('(' + quote(key) + ', ' + render(item) + ')'
                                          for key, item in value) + ']'
    if isinstance(value, NumberToken):
        return 'Value.number ' + quote(str(value))
    if value is None:
        return 'Value.null'
    if isinstance(value, bool):
        return 'Value.boolean ' + str(value).lower()
    if isinstance(value, str):
        return 'Value.string ' + quote(value)
    if isinstance(value, list):
        return 'Value.array [' + ', '.join(render(item) for item in value) + ']'
    raise TypeError(type(value))


def as_schema_value(value):
    if isinstance(value, ObjectPairs):
        result = {}
        for key, item in value:
            if key in result:
                raise DuplicateKey(key)
            result[key] = as_schema_value(item)
        return result
    if isinstance(value, NumberToken):
        return json.loads(str(value))
    if isinstance(value, list):
        return [as_schema_value(item) for item in value]
    return value


def get(obj, key):
    return next(value for name, value in obj if name == key)


def replace(obj, key, value):
    for index, (name, _) in enumerate(obj):
        if name == key:
            obj[index] = (key, value)
            return
    raise KeyError(key)


def remove(obj, key):
    obj[:] = [(name, value) for name, value in obj if name != key]


def typed_record(raw):
    def strings(values):
        return '[' + ', '.join(quote(item) for item in values) + ']'
    def payload(value):
        return '{ ' + ', '.join(key + ' := ' +
            (strings(item) if isinstance(item, list) else quote(item))
            for key, item in value.items()) + ' }'
    def relation(value):
        return '{ ' + ', '.join(key + ' := ' + quote(item) for key, item in value.items()) + ' }'
    fields = []
    for key, value in raw.items():
        if key == 'payload':
            encoded = payload(value)
        elif key == 'relation_refs':
            encoded = '[' + ', '.join(relation(item) for item in value) + ']'
        elif isinstance(value, list):
            encoded = strings(value)
        else:
            encoded = quote(value)
        fields.append(key + ' := ' + encoded)
    return '{ ' + ', '.join(fields) + ' }'


def reverse_objects(value):
    if isinstance(value, ObjectPairs):
        return ObjectPairs((key, reverse_objects(item)) for key, item in reversed(value))
    if isinstance(value, list):
        return [reverse_objects(item) for item in value]
    return value


def run():
    schema = json.loads(SCHEMA.read_text())
    validator = Draft202012Validator(schema)
    source = json.loads(FIXTURE.read_text(), object_pairs_hook=ObjectPairs,
                        parse_int=NumberToken, parse_float=NumberToken)
    original = as_schema_value(source)
    validator.validate(original)
    assert set(original) == set(schema['required']) and len(schema['required']) == 14
    assert len(schema['properties']['payload']['required']) == 5
    assert len(schema['properties']['relation_refs']['items']['required']) == 4
    cases = []

    def add(name, changed, expected):
        try:
            raw = as_schema_value(changed)
            actual = validator.is_valid(raw)
            method = 'Draft202012Validator'
        except DuplicateKey:
            raw = None
            actual = False
            method = 'candidate-profile-retained-duplicate-key-rejection'
        assert actual == expected, name
        cases.append({'name': name, 'ast': changed, 'expected': actual,
                      'comparison_method': method, 'typed_record': raw if actual else None})

    add('original_source', deepcopy(source), True)
    add('all_unique_objects_reordered', reverse_objects(source), True)
    for location, keys in [('outer', schema['required']),
            ('payload', schema['properties']['payload']['required']),
            ('reference', schema['properties']['relation_refs']['items']['required'])]:
        def select(ast, location=location):
            if location == 'outer':
                return ast
            if location == 'payload':
                return get(ast, 'payload')
            return get(ast, 'relation_refs')[0]
        for key in keys:
            changed = deepcopy(source);remove(select(changed), key)
            add(location + '_missing_' + key, changed, False)
            changed = deepcopy(source);replace(select(changed), key, NumberToken('0'))
            add(location + '_wrong_type_' + key, changed, False)
        changed = deepcopy(source);select(changed).append(('unexpected', 'value'))
        add(location + '_extra_key', changed, False)
        for suffix in ['identical', 'conflicting']:
            changed = deepcopy(source);obj = select(changed);key = keys[0]
            obj.append((key, deepcopy(get(obj, key)) if suffix == 'identical' else 'different'))
            add(location + '_duplicate_' + suffix, changed, False)

    for field in ['evidence_refs', 'successor_refs', 'relation_refs',
                  'selected_subject_refs', 'satisfaction_test_refs', 'excluded_subject_refs']:
        def select_array(ast, field=field):
            return ast if field in ['evidence_refs', 'successor_refs', 'relation_refs'] else get(ast, 'payload')
        for position in ['head', 'tail']:
            changed = deepcopy(source);obj = select_array(changed);items = get(obj, field)
            if not items:
                items.append('candidate:synthetic-successor')
            items.insert(0 if position == 'head' else len(items), None)
            add(field + '_invalid_' + position, changed, False)

    for name, value in [('null', None), ('boolean', True), ('number', NumberToken('0')),
                        ('string', 'object-required'), ('array', [])]:
        add('wrong_top_' + name, value, False)

    changed = deepcopy(source);get(get(changed, 'payload'), 'selected_subject_refs').reverse()
    add('selected_array_order_preserved', changed, True)
    changed = deepcopy(source);get(changed, 'relation_refs').append(deepcopy(get(changed, 'relation_refs')[0]))
    add('duplicate_relation_items_preserved', changed, True)
    changed = deepcopy(source);replace(changed, 'evidence_refs', [])
    add('empty_evidence_shape_valid', changed, True)
    changed = deepcopy(source);replace(changed, 'owner_ref', 'unverified-label')
    add('owner_label_does_not_authenticate', changed, True)
    changed = deepcopy(source);replace(changed, 'lifecycle_state', 'retired')
    add('retired_label_shape_valid', changed, True)
    changed = deepcopy(source);replace(get(changed, 'payload'), 'satisfaction_test_refs', [])
    add('empty_tests_do_not_create_satisfaction', changed, True)
    changed = deepcopy(source);replace(get(changed, 'payload'), 'excluded_subject_refs',
                                       [get(get(changed, 'payload'), 'selected_subject_refs')[0]])
    add('selection_exclusion_overlap_shape_valid', changed, True)
    changed = deepcopy(source);replace(get(changed, 'relation_refs')[0], 'relation_kind_ref', 'relation.successor-of')
    add('unjoined_relation_enums_shape_valid', changed, True)

    # Key-only AST identity is retained in the case literals, not collapsed maps.
    fixture_lines = ['import JsonEncoding', '', 'set_option autoImplicit false', '',
        'namespace RelationalSuccessor.CandidateJsonSource.Examples',
        'open RelationalSuccessor.CandidateJsonSource',
        'open RelationalSuccessor.CandidateIntentRecordShape', '',
        'def sourceAst : Value := ' + render(source),
        'def sourceRecord : RawRecord := ' + typed_record(original), '',
        'end RelationalSuccessor.CandidateJsonSource.Examples', '']
    (HERE / 'JsonFixture.lean').write_text('\n'.join(fixture_lines))
    modules = []
    for offset in range(0, len(cases), 6):
        number = offset // 6 + 1
        name = 'JsonControls' + str(number)
        modules.append(name)
        chunk = cases[offset:offset + 6]
        lines = ['import JsonFixture', '', 'set_option autoImplicit false', '',
            'namespace RelationalSuccessor.CandidateJsonSource.Examples',
            'open RelationalSuccessor.CandidateJsonSource',
            'open RelationalSuccessor.CandidateIntentRecordShape', '']
        for case in chunk:
            lines += ['def ast_' + case['name'] + ' : Value := ' + render(case['ast'])]
            expected = 'some (' + typed_record(case['typed_record']) + ')' if case['expected'] else 'none'
            lines += ['theorem ' + case['name'] + ' : decodeRecord ast_' + case['name'] +
                      ' = ' + expected + ' := by decide', '']
        lines += ['#print axioms ' + case['name'] for case in chunk]
        lines += ['end RelationalSuccessor.CandidateJsonSource.Examples', '']
        (HERE / (name + '.lean')).write_text('\n'.join(lines))
    report_cases = [{'name': case['name'], 'expected': case['expected'],
                     'comparison_method': case['comparison_method'],
                     'ast_expression_sha256': hashlib.sha256(render(case['ast']).encode()).hexdigest()}
                    for case in cases]
    report = {'task': 'N01', 'unit': 'K02-json', 'schema': binding(SCHEMA),
        'fixture': binding(FIXTURE), 'generator': binding(Path(__file__)),
        'generated_fixture': binding(HERE / 'JsonFixture.lean'),
        'generated_controls': [binding(HERE / (name + '.lean')) for name in modules],
        'comparison_engine': {'package': 'jsonschema', 'version': version('jsonschema'),
                              'validator': 'Draft202012Validator'},
        'object_entry_policy': 'Retain entries and reject identical or conflicting duplicate keys before lookup',
        'candidate_parser_profile_owner_accepted': False,
        'original_outer_fields': [key for key, _ in source],
        'controls': report_cases, 'control_count': len(cases),
        'generator_translation_proved': False, 'byte_parser_proved': False,
        'source_authenticity_established': False, 'inherited_discharges': 0}
    (HERE / 'source-capture.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'controls': len(cases), 'control_modules': modules,
                      'retained_duplicate_key_controls': sum('duplicate_' in case['name']
                          and 'items' not in case['name'] for case in cases)}))


if __name__ == '__main__':
    run()
