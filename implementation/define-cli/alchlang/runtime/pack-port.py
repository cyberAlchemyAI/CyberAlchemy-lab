"""Explicit data/byte port to the unchanged standalone Define v3 implementation."""
import json
import base64
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'standalone'))
from define_core import call
from define_core.exact import decode, tree

NUMERIC = {'bytes', 'revision', 'request_revision', 'pack_revision'}
JSON_FIELDS = {'value_schema', 'bindings'}

def protocol(value, key=None):
    if key in JSON_FIELDS:
        return decode(value.encode("utf-8"))
    if key in NUMERIC:
        return int(value)
    if isinstance(value, list):
        return [protocol(item) for item in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {'tag', 'fields'} and value['tag'] in ('External', 'Embedded'):
        return protocol(value['fields']['value'])
    return {({'identity_ref': 'identity', 'context_description': 'context'}.get(name, name)): (item if name == 'revision' and value.get('kind') == 'external' else protocol(item, name)) for name, item in value.items()}

def request(document):
    result = protocol({key: value for key, value in document.items() if key != 'handling'})
    for name in ('predecessor_package_binding', 'language_evidence_binding', 'field_supplement_binding'):
        if result.get(name) is None:
            result.pop(name, None)
    result['handling'] = []
    for handling in document['handling']:
        tag = handling['tag']
        payload = protocol(handling['fields']['value'])
        concept = payload.pop('concept_id')
        disposition = {'Reuse': 'reuse', 'Propose': 'propose', 'Open': 'open',
                       'ApplyParameters': 'specialize', 'ChangeMeaning': 'specialize'}[tag]
        if tag in ('ApplyParameters', 'ChangeMeaning'):
            payload['mode'] = 'application' if tag == 'ApplyParameters' else 'meaning-change'
        result['handling'].append({'concept_id': concept, 'disposition': disposition, 'payload': payload})
    return result

def typed(value, key=None, plain_reference=False):
    if key in JSON_FIELDS:
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    if key in NUMERIC:
        return str(value)
    if isinstance(value, list):
        return [typed(item) for item in value]
    if not isinstance(value, dict):
        return value
    converted = {({'identity': 'identity_ref', 'context': 'context_description'}.get(name, name)): typed(item, name)
                 for name, item in value.items()}
    if value.get('kind') in ('external', 'embedded') and not plain_reference:
        return {'tag': value['kind'].title(), 'fields': {'value': converted}}
    return converted

def imported(document, project, work, context):
    # The source request is schema checked before any conversion. Unsupported
    # limits fail in AlchLang rather than truncating a caller's collections.
    tree(document)
    schema = invoke('schema', {'kind': 'request'})
    from jsonschema import Draft202012Validator
    Draft202012Validator(schema['data']['schema']).validate(document)
    scope = {key: document[key] for key in ('goal', 'originating_intent', 'context', 'consumer', 'intended_use')}
    scope.update(project=project, work=work)
    lineage = {key: typed(document.get(key)) for key in
               ('predecessor_package_binding', 'language_evidence_binding', 'field_supplement_binding')}
    seed = {'session_id': document['request_id'], 'request_revision': str(document['request_revision']),
            'request_lineage': lineage, 'scope': typed(scope), 'validation_scope': typed(document['validation_scope'])}
    payloads = [{'tag': 'Initialize', 'fields': {'value': {key: value for key, value in seed.items() if key != 'session_id'}}},
                {'tag': 'SetContext', 'fields': {'value': context}}]
    def add(tag, value):
        payloads.append({'tag': tag, 'fields': {'value': value}})
    for value in document['required_concepts']:
        add('RequireConcept', typed(value))
    for field, tag in [('source_bindings', 'BindSource'), ('evidence_bindings', 'BindEvidence')]:
        for value in document[field]:
            add(tag, typed(value))
    for handling in document['handling']:
        payload = handling['payload']
        disposition = handling['disposition']
        tag = {'reuse': 'Reuse', 'propose': 'Propose', 'open': 'Open',
               'specialize': 'ApplyParameters' if payload.get('mode') == 'application' else 'ChangeMeaning'}[disposition]
        value = typed({key: item for key, item in payload.items() if key != 'mode'})
        value['concept_id'] = handling['concept_id']
        if tag == 'Reuse':
            value['meaning_ref'] = typed(payload['meaning_ref'], plain_reference=True)
        add('HandleMeaning', {'tag': tag, 'fields': {'value': value}})
    for field, tag in [('applications', 'PutApplication'), ('assessments', 'PutAssessment')]:
        for value in document[field]:
            add(tag, typed(value))
    for selection in document['materialization_selection']:
        value = typed(selection)
        value['meaning_ref'] = typed(selection['meaning_ref'], plain_reference=True)
        value['parent_ref'] = typed(selection['parent_ref'], plain_reference=True)
        add('SelectMaterialization', value)
    return {'seed': seed, 'payloads': payloads}

def invoke(operation, params):
    return call({'api_version': 'define.api/v1', 'id': 'define-alch', 'operation': operation, 'params': params})

def main():
    data = json.load(sys.stdin)
    if data['operation'] == 'decode-json':
        print(json.dumps({'document': decode(base64.b64decode(data['bytes_base64'], validate=True))}))
    elif data['operation'] == 'translate':
        result = request(data['request'])
        schema = invoke('schema', {'kind': 'request'})
        assert schema['outcome'] == 'prepared', schema
        from jsonschema import Draft202012Validator
        Draft202012Validator(schema['data']['schema']).validate(result)
        print(json.dumps({'request': result}))
    elif data['operation'] == 'import-request':
        print(json.dumps(imported(data['request'] if 'request' in data else decode(base64.b64decode(data['request_base64'], validate=True)), data['project'], data['work'], data['context'])))
    else:
        print(json.dumps(invoke(data['operation'], data['params'])))

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'outcome': 'refused', 'diagnostic': getattr(error, 'code', 'invalid-protocol-translation'), 'authority_effect': 'none'}))
        sys.exit(2)
