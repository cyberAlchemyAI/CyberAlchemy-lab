"""Validate proposed syntax and boundary fixtures; never claim Lean/schema or byte-parser proofs."""
from pathlib import Path
import copy
import hashlib
import json
from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def reference(token):
    return {'key': {'owner': 'fixture', 'artifact': token, 'revision': '1'}, 'digest': 'fixture-digest'}


def run():
    schemas = {name: json.loads((HERE / 'schemas' / (name + '.schema.json')).read_text())
               for name in ['resolution-binding', 'role-binding']}
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
    frame = {name: reference(name) for name in ['profile', 'subject', 'target', 'context', 'scope', 'snapshot']}
    frame.update(epoch=42, timeDomain='fixture-epoch')
    resolution = {name: reference(name) for name in ['ref', 'scope', 'intent', 'ownerDecision']}
    resolution.update(selectedSubjects=[reference('subject')], excludedSubjects=[], satisfactionTests=[])
    role = {'ref': reference('role'), 'code': 'investigation', 'subjectKind': 'project'}
    cases = []
    for name, target in [('resolution-binding', resolution), ('role-binding', role)]:
        kind = schemas[name]['properties']['kind']['const']
        base = {'schema_version': schemas[name]['properties']['schema_version']['const'],
                'binding_revision_key': reference('binding')['key'], 'kind': kind,
                'body': {'token': 'resolution:1' if name == 'resolution-binding' else 'investigation',
                         'target': target, 'frame': frame}, 'owner_review_ref': reference('review')}
        (HERE / 'schemas' / (name + '.fixture.json')).write_text(json.dumps(base, indent=2) + '\n')
        samples = [('original', base, True)]
        for field in base:
            value = copy.deepcopy(base); del value[field]; samples.append(('missing_' + field, value, False))
        mutations = [
            ('extra_outer', lambda x: x.update(extra=True)),
            ('self_embedded_bytes', lambda x: x.update(content_bytes=[1, 2])),
            ('self_digest_field', lambda x: x.update(binding_digest='not-external')),
            ('wrong_kind', lambda x: x.update(kind='another-kind')),
            ('empty_token', lambda x: x['body'].update(token='')),
            ('wrong_token_type', lambda x: x['body'].update(token=[])),
            ('extra_body', lambda x: x['body'].update(extra=True)),
            ('missing_frame_epoch', lambda x: x['body']['frame'].pop('epoch')),
            ('negative_epoch', lambda x: x['body']['frame'].update(epoch=-1)),
            ('fractional_epoch', lambda x: x['body']['frame'].update(epoch=1.5)),
            ('empty_frame_domain', lambda x: x['body']['frame'].update(timeDomain='')),
            ('missing_target_ref', lambda x: x['body']['target'].pop('ref')),
            ('extra_revision_key', lambda x: x['binding_revision_key'].update(digest='not-a-key-field')),
        ]
        for label, mutate in mutations:
            value = copy.deepcopy(base); mutate(value); samples.append((label, value, False))
        if name == 'role-binding':
            value = copy.deepcopy(base); value['body']['target']['subjectKind'] = 'other'
            samples.append(('other_kind_is_syntax_not_relation_qualification', value, True))
        else:
            value = copy.deepcopy(base); value['body']['target']['selectedSubjects'] = []
            samples.append(('empty_selection_is_syntax_not_relation_qualification', value, True))
        validator = Draft202012Validator(schemas[name])
        for label, value, expected in samples:
            actual = validator.is_valid(value)
            assert actual == expected, (name, label, actual, expected)
            cases.append({'schema': name, 'case': label, 'expected_valid': expected, 'actual_valid': actual,
                          'value_sha256': hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()})
    report = {'result': 'candidate-binding-schema-corpus-pass', 'driver': binding(Path(__file__)),
              'schemas': [binding(HERE / 'schemas' / (name + '.schema.json')) for name in schemas],
              'fixtures': [binding(HERE / 'schemas' / (name + '.fixture.json')) for name in schemas],
              'case_count': len(cases), 'cases': cases,
              'claim_scope': 'Draft202012 syntax validation only; duplicate-key byte parsing and Lean/schema correspondence not proved.',
              'schema_AST_correspondence_proved': False, 'byte_parser_proved': False,
              'authenticated_capture_proved': False, 'N03_schema_freeze': False, 'inherited_discharges': 0}
    (HERE / 'binding-schema-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'result': report['result'], 'cases': len(cases)}))


if __name__ == '__main__':
    run()
