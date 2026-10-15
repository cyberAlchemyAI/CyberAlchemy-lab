"""Preserve every source field and compare concrete typed-shape controls to JSON Schema.

This translation is not a verified JSON parser or proof of source authenticity.
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


def binding(path):
    return {'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def text(value):
    return json.dumps(value, ensure_ascii=False)


def string_list(values):
    return '[' + ', '.join(text(value) for value in values) + ']'


def payload(value):
    return '{ ' + ', '.join(key + ' := ' +
        (string_list(value[key]) if isinstance(value[key], list) else text(value[key]))
        for key in ['intent_ref', 'owner_decision_ref', 'selected_subject_refs',
                    'satisfaction_test_refs', 'excluded_subject_refs']) + ' }'


def relation(value):
    return '{ ' + ', '.join(key + ' := ' + text(value[key]) for key in
        ['relation_kind_ref', 'direction', 'counterpart_kind', 'counterpart_ref']) + ' }'


def run():
    schema = json.loads(SCHEMA.read_text())
    fixture = json.loads(FIXTURE.read_text())
    validator = Draft202012Validator(schema)
    validator.validate(fixture)
    assert len(schema['required']) == 14
    assert set(fixture) == set(schema['required']) == set(schema['properties'])
    assert set(fixture['payload']) == set(schema['properties']['payload']['required'])
    assert len(schema['properties']['payload']['required']) == 5
    assert schema['additionalProperties'] is False
    assert schema['properties']['payload']['additionalProperties'] is False
    assert schema['properties']['relation_refs']['items']['additionalProperties'] is False
    lines = ['import IntentRecordShape', '', 'set_option autoImplicit false', '',
             'namespace RelationalSuccessor.CandidateIntentRecordShape.Examples',
             'open RelationalSuccessor.CandidateIntentRecordShape', '',
             'def sourceFixture : RawRecord where']
    for key in schema['required']:
        value = fixture[key]
        if key == 'payload':
            rendered = payload(value)
        elif key == 'relation_refs':
            rendered = '[' + ', '.join(relation(item) for item in value) + ']'
        elif isinstance(value, list):
            rendered = string_list(value)
        else:
            rendered = text(value)
        lines.append('  ' + key + ' := ' + rendered)
    lines += ['', 'end RelationalSuccessor.CandidateIntentRecordShape.Examples', '']
    (HERE / 'OuterFixture.lean').write_text('\n'.join(lines))

    controls = []

    def add(label, change, lean, expected):
        changed = deepcopy(fixture)
        change(changed)
        actual = validator.is_valid(changed)
        assert actual == expected, label
        controls.append({'name': label, 'lean': lean, 'expected': actual,
                         'source_record': changed})

    add('original_source_shape', lambda d: None, 'sourceFixture', True)
    for key, invalid in [('schema_version', 'wrong-schema'), ('node_id', ''),
            ('kind', 'decision'), ('name', ''), ('lifecycle_state', 'unknown'),
            ('authority_effect', 'grant'), ('owner_ref', ''), ('scope_ref', ''),
            ('challenge_route', ''), ('claim_ceiling', '')]:
        add('invalid_' + key, lambda d, k=key, v=invalid: d.__setitem__(k, v),
            '{ sourceFixture with ' + key + ' := ' + text(invalid) + ' }', False)
    for key in ['evidence_refs', 'successor_refs']:
        for suffix, values in [('empty_member', ['']), ('duplicates', ['x', 'x'])]:
            add(key + '_' + suffix, lambda d, k=key, v=values: d.__setitem__(k, v),
                '{ sourceFixture with ' + key + ' := ' + string_list(values) + ' }', False)
    add('empty_relation_list', lambda d: d.__setitem__('relation_refs', []),
        '{ sourceFixture with relation_refs := [] }', False)
    for key, invalid in [('relation_kind_ref', 'relation.addresses-intent'),
            ('direction', 'both'), ('counterpart_kind', 'project'), ('counterpart_ref', '')]:
        item = deepcopy(fixture['relation_refs'][0]); item[key] = invalid
        add('invalid_relation_' + key,
            lambda d, v=item: d.__setitem__('relation_refs', [v]),
            '{ sourceFixture with relation_refs := [' + relation(item) + '] }', False)
    for key in ['intent_ref', 'owner_decision_ref']:
        add('empty_payload_' + key,
            lambda d, k=key: d['payload'].__setitem__(k, ''),
            '{ sourceFixture with payload := { sourceFixture.payload with ' + key + ' := "" } }', False)
    for key in ['selected_subject_refs', 'satisfaction_test_refs', 'excluded_subject_refs']:
        for suffix, values in [('empty_member', ['']), ('duplicates', ['x', 'x'])]:
            add(key + '_' + suffix,
                lambda d, k=key, v=values: d['payload'].__setitem__(k, v),
                '{ sourceFixture with payload := { sourceFixture.payload with ' + key +
                ' := ' + string_list(values) + ' } }', False)
    add('empty_evidence_is_shape_valid', lambda d: d.__setitem__('evidence_refs', []),
        '{ sourceFixture with evidence_refs := [] }', True)
    add('retired_is_shape_valid', lambda d: d.__setitem__('lifecycle_state', 'retired'),
        '{ sourceFixture with lifecycle_state := "retired" }', True)
    add('owner_label_alone_is_shape_valid', lambda d: d.__setitem__('owner_ref', 'unverified-label'),
        '{ sourceFixture with owner_ref := "unverified-label" }', True)
    empty_payload = deepcopy(fixture['payload'])
    for key in ['selected_subject_refs', 'satisfaction_test_refs', 'excluded_subject_refs']:
        empty_payload[key] = []
    add('empty_payload_lists_are_shape_valid', lambda d: d.__setitem__('payload', empty_payload),
        '{ sourceFixture with payload := ' + payload(empty_payload) + ' }', True)
    overlap = deepcopy(fixture['payload']);overlap['excluded_subject_refs'] = [overlap['selected_subject_refs'][0]]
    add('selected_excluded_overlap_is_shape_valid', lambda d: d.__setitem__('payload', overlap),
        '{ sourceFixture with payload := ' + payload(overlap) + ' }', True)
    mixed = deepcopy(fixture['relation_refs'][0]);mixed['relation_kind_ref'] = 'relation.successor-of'
    add('unjoined_relation_enums_are_shape_valid', lambda d: d.__setitem__('relation_refs', [mixed]),
        '{ sourceFixture with relation_refs := [' + relation(mixed) + '] }', True)
    alias_tokens = [fixture['payload']['selected_subject_refs'][0], 'alias:project-subject']
    add('distinct_selected_alias_tokens_are_shape_valid',
        lambda d: d['payload'].__setitem__('selected_subject_refs', alias_tokens),
        '{ sourceFixture with payload := { sourceFixture.payload with selected_subject_refs := ' +
        string_list(alias_tokens) + ' } }', True)

    modules = []
    for offset in range(0, len(controls), 6):
        number = offset // 6 + 1
        chunk = controls[offset:offset + 6]
        name = 'OuterControls' + str(number)
        modules.append(name)
        lines = ['import OuterFixture', '', 'set_option autoImplicit false', '',
            'namespace RelationalSuccessor.CandidateIntentRecordShape.Examples',
            'open RelationalSuccessor.CandidateIntentRecordShape', '']
        for control in chunk:
            lines += ['theorem ' + control['name'] + ' : recordShapeCheck ' +
                '(' + control['lean'] + ') = ' + str(control['expected']).lower() + ' := by decide', '']
        lines += ['#print axioms ' + control['name'] for control in chunk]
        lines += ['end RelationalSuccessor.CandidateIntentRecordShape.Examples', '']
        (HERE / (name + '.lean')).write_text('\n'.join(lines))

    # These cases cannot be expressed by the complete typed carrier. They remain
    # explicitly unproved adapter obligations rather than fabricated Lean cases.
    parser_shape_probes = []
    for key in schema['required']:
        changed = deepcopy(fixture); del changed[key]
        assert not validator.is_valid(changed)
        parser_shape_probes.append({'case': 'missing-' + key, 'schema_valid': False,
                                   'typed_carrier_represents_case': False})
    extra = deepcopy(fixture);extra['unexpected'] = 'value'
    assert not validator.is_valid(extra)
    parser_shape_probes.append({'case': 'extra-outer-field', 'schema_valid': False,
                               'typed_carrier_represents_case': False})
    report = {'task': 'N01', 'unit': 'K02-outer', 'schema': binding(SCHEMA),
        'shape_probe_engine': {'package': 'jsonschema', 'version': version('jsonschema'),
                               'validator': 'Draft202012Validator'},
        'fixture': binding(FIXTURE), 'generator': binding(Path(__file__)),
        'generated_fixture': binding(HERE / 'OuterFixture.lean'),
        'generated_controls': [binding(HERE / (name + '.lean')) for name in modules],
        'required_outer_fields': schema['required'], 'outer_field_count': 14,
        'typed_shape_controls': controls, 'typed_shape_control_count': len(controls),
        'unrepresented_parser_shape_probes': parser_shape_probes,
        'translation_proved': False, 'JSON_parser_proved': False,
        'source_authenticity_established': False, 'inherited_discharges': 0}
    (HERE / 'source-capture.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'outer_fields': 14, 'typed_controls': len(controls),
                      'parser_probes_not_formalized': len(parser_shape_probes),
                      'control_modules': modules}))


if __name__ == '__main__':
    run()
