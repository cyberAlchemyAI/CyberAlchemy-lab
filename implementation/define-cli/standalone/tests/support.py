"""Portable qualification helpers. Imports installed Define, never its source tree."""
import base64
import copy
import json
from pathlib import Path
import unittest

from define_core import call
from define_core.contracts import check
from define_core.exact import binding, decode, encode, sha
from define_core.example import example_members
from define_core.prepare import local_ref


def b64(members):
    return {path: base64.b64encode(raw).decode('ascii') for path, raw in members.items()}


def raw_members(members):
    return {path: base64.b64decode(raw, validate=True) for path, raw in members.items()}


def base():
    members = example_members()
    request = decode(members.pop('request.json'))
    return request, members


def refresh(request):
    meanings = [h['payload']['working_meaning'] for h in request['handling'] if h['disposition'] == 'propose' or
                (h['disposition'] == 'specialize' and h['payload']['mode'] == 'meaning-change')]
    for app in request['applications']:
        ref = app['meaning_ref']
        if ref['kind'] == 'embedded':
            i = next(i for i, m in enumerate(meanings) if m['meaning_id'] == ref['entry_id'])
            app['meaning_ref'] = local_ref(request['request_id'], request['request_revision'], 'working-meaning', i, meanings[i])
    for h in request['handling']:
        if h['disposition'] == 'specialize' and h['payload']['mode'] == 'application':
            app = next(a for a in request['applications'] if a['application_id'] == h['payload']['application_id'])
            h['payload']['parent_ref'] = copy.deepcopy(app['meaning_ref'])
    for assessment in request['assessments']:
        i = next(i for i, a in enumerate(request['applications']) if a['application_id'] == assessment['application_ref']['entry_id'])
        assessment['application_ref'] = local_ref(request['request_id'], request['request_revision'], 'application', i, request['applications'][i])
    return request


def no_sources():
    request, _ = base()
    h = copy.deepcopy(request['handling'][1]);h['payload']['working_meaning']['lineage'] = []
    request['required_concepts'] = [request['required_concepts'][1]]
    request['handling'] = [h]
    request['source_bindings'] = [];request['evidence_bindings'] = []
    request['applications'] = [];request['assessments'] = []
    return request, {}


def add_source(request, inputs, path, raw):
    b = binding(raw, path)
    request['source_bindings'].append(b);inputs[path] = raw
    return b


def external_application():
    request, inputs = base()
    meaning = copy.deepcopy(request['handling'][1]['payload']['working_meaning'])
    source = {'definition_id': 'example:export-complete', 'version': '1', 'statement': meaning['statement'], 'parameters': meaning['parameters']}
    add_source(request, inputs, 'complete.json', encode(source))
    ref = {'kind': 'external', 'input_id': 'complete.json', 'identity': source['definition_id'], 'revision': source['version'],
           'carrier_ref': 'example.meaning/v1', 'selector': '', 'sha256': sha(encode(source))}
    request['handling'][1] = {'concept_id': 'complete-export', 'disposition': 'reuse', 'payload': {'meaning_ref': ref, 'applicability': 'Exact local source only.'}}
    app = request['applications'][0];app['meaning_ref'] = copy.deepcopy(ref)
    app['parameter_contract_ref'] = 'parameters:' + ref['identity'] + '@' + ref['revision']
    refresh(request)
    return request, inputs


def materialization():
    request, inputs = base()
    meaning = request['handling'][1]['payload']['working_meaning']
    descriptor = call({'api_version': 'define.api/v1', 'id': 'carrier', 'operation': 'schema', 'params': {'kind': 'definition-carrier'}})['data']
    body = json.loads((Path(__file__).parent/'fixtures/definition.json').read_bytes())
    body['voices']['scientific_formal']['normative_statement'] = meaning['statement']
    body['voices']['scientific_formal']['notation'] = [{'symbol': p['name'], 'meaning': p['interpretation']} for p in meaning['parameters']]
    body['boundaries'] = meaning['boundaries'];body['scope']['applicability'] = meaning['scope']
    body['schema_digest'] = descriptor['schema_binding']['sha256']
    body['source_direction']['generator_sha256'] = descriptor['generator_binding']['sha256']
    body_binding = add_source(request, inputs, 'candidate-definition.json', encode(body))
    from define_core.materialize import leaves
    lineage = {'schema_version': 'cal.define.field-lineage/v1', 'authored_by': 'example:test-author',
               'fields': [{'target_selector': s, 'source_binding': body_binding, 'source_selector': s} for s in leaves(body)],
               'claim_ceiling': 'Synthetic authored attribution only, no independent fidelity acceptance.', 'authority_effect': 'none'}
    lineage_binding = add_source(request, inputs, 'candidate-lineage.json', encode(lineage))
    request['materialization_selection'] = [{'meaning_ref': copy.deepcopy(request['applications'][0]['meaning_ref']),
        'purpose': 'Candidate materialization qualification', 'authority_scope': body['scope']['authority_scope_ref'],
        'owner_route': 'example:unqualified-route', 'identity_intention': 'new-identity', 'parent_ref': None,
        'definition_binding': body_binding, 'field_lineage_binding': lineage_binding}]
    return request, inputs


class Case(unittest.TestCase):
    def invoke(self, operation, params=None, identity='test'):
        result = call({'api_version': 'define.api/v1', 'id': identity, 'operation': operation, 'params': params or {}})
        check(result, 'api-result')
        self.assertEqual(result['authority_effect'], 'none')
        return result

    def ok(self, result):
        self.assertIn(result['outcome'], ('prepared', 'prepared-with-gaps', 'ready', 'not-evaluable'), result)
        return result['data']

    def refused(self, result, code=None):
        self.assertIn(result['outcome'], ('invalid-input', 'blocked', 'unsupported'), {'outcome':result['outcome'], 'diagnostics':result['diagnostics']})
        self.assertIsNone(result['data'])
        if code:self.assertEqual(result['diagnostics'][0]['code'], code)
        return result

    def captured(self, request=None, inputs=None, **kwargs):
        if request is None:request, inputs = base()
        params = {'request_utf8': encode(request).decode(), 'inputs': b64(inputs), 'permit_retention': True, 'captured_at': '2026-10-15T00:00:00+00:00', **kwargs}
        return self.ok(self.invoke('capture', params))

    def prepared(self, request=None, inputs=None, captured=None):
        if request is None:request, inputs = base()
        captured = self.captured(request, inputs) if captured is None else captured
        return self.invoke('prepare', {'request_utf8': encode(request).decode(), 'capture_utf8': captured['capture_utf8'], 'inputs': captured['inputs']})

    def package(self, request=None, inputs=None):
        return self.ok(self.prepared(request, inputs))
