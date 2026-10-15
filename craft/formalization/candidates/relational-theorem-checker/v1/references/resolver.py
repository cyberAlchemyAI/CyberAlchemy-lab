"""Exact structural and reference checks; supplied assessments remain a trust input."""
from copy import deepcopy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'input'))
import decoder as d
s = d.s
SUPPORTED = {'relation.conforms-to', 'relation.declares-effect-on', 'relation.materializes-consequence'}


def key(ref):
    s.require(isinstance(ref, dict) and set(ref) == {'id', 'version'}, 'invalid exact reference')
    s.require(all(isinstance(v, str) and v for v in ref.values()), 'empty exact reference')
    return ref['id'], ref['version']


def from_decoder(raw):
    """Retain the definition version validated against frozen input sources."""
    value = d.decode(raw)
    normal = d.normalize(value)
    graph = deepcopy(normal['graph'])
    for edge, original in zip(graph['assertions'], value['graph']['assertions']):
        edge['kind_version'] = original['relation_kind_version']
    if 'addition' in normal:
        edge = deepcopy(normal['addition'])
        edge['kind_version'] = value['addition']['relation_kind_version']
        graph['assertions'].append(edge)
    return graph


def resolve(graph, registry):
    s.require(isinstance(graph, dict) and set(graph) in [
        {'nodes', 'assertions', 'assessments', 'admission_roots'},
        {'graph_id', 'nodes', 'assertions', 'assessments', 'admission_roots'}], 'invalid graph fields')
    s.require(all(isinstance(graph[name], list) for name in ['nodes', 'assertions', 'assessments', 'admission_roots']), 'graph collections must be lists')
    for node in graph['nodes']:
        s.require(isinstance(node, dict) and set(node) == {'ref', 'kind', 'content_identity'}, 'invalid node fields')
        s.require(isinstance(node['kind'], str), 'node type must be a string')
    for edge in graph['assertions']:
        s.require(isinstance(edge, dict) and set(edge) == {'id', 'kind', 'kind_version', 'source', 'target', 'qualifiers'}, 'invalid assertion fields')
        s.require(all(isinstance(edge[name], str) for name in ['id', 'kind', 'kind_version']), 'assertion identities must be strings')
        s.require(isinstance(edge['qualifiers'], dict), 'qualifiers must be an object')
    for assessment in graph['assessments']:
        s.require(isinstance(assessment, dict) and set(assessment) == {'ref', 'mode', 'subject', 'target', 'scope', 'role', 'output_digest', 'accepted'}, 'invalid assessment fields')
        s.require(all(isinstance(assessment[name], str) for name in ['ref', 'mode', 'scope', 'role', 'output_digest']), 'assessment fields must be strings')
    for root in graph['admission_roots']:
        s.require(isinstance(root, dict) and set(root) == {'subject', 'decision', 'authority_evidence'}, 'invalid admission root fields')
        s.require(isinstance(root['authority_evidence'], str), 'authority evidence must be a string')
    errors = []; unsupported = []; resolved = []
    def fail(code, subject, detail):
        errors.append({'code': code, 'subject': subject, 'detail': detail})
    definitions = {row['id']: row for row in registry['kinds']}
    nodes = {}
    for node in graph['nodes']:
        identity = key(node['ref'])
        if identity in nodes: fail('duplicate-node', identity, 'exact identity repeated')
        if node['kind'] not in registry['node_kinds'] or not isinstance(node['content_identity'], str) or not node['content_identity']:
            fail('invalid-node', identity, 'unknown type or empty content identity')
        nodes[identity] = node
    assessments = {}
    for assessment in graph['assessments']:
        token = assessment['ref']
        if not isinstance(token, str) or not token: fail('invalid-evidence-token', token, 'empty or non-string reference')
        if token in assessments: fail('duplicate-evidence', token, 'token repeated')
        assessments[token] = assessment
        if key(assessment['subject']) not in nodes or key(assessment['target']) not in nodes:
            fail('absent-evidence-endpoint', token, 'assessment endpoint does not resolve')
        mode = assessment['mode']
        if mode not in {'conformance', 'application-receipt'}:
            fail('wrong-evidence-type', token, 'unsupported assessment mode')
        if type(assessment['accepted']) is not bool:
            fail('invalid-evidence-posture', token, 'accepted must be Boolean')
        if mode == 'conformance' and not assessment['scope']:
            fail('empty-evidence-scope', token, 'conformance requires scope')
        if mode == 'application-receipt' and (not assessment['role'] or not assessment['output_digest']):
            fail('empty-receipt-role-or-digest', token, 'receipt requires both fields')
    seen = set()
    for edge in graph['assertions']:
        eid = edge['id']; kind = edge['kind']; qualifiers = edge['qualifiers']
        if not isinstance(eid, str) or not eid or eid in seen: fail('invalid-edge-identity', eid, 'empty or repeated identity')
        seen.add(eid)
        definition = definitions.get(kind)
        if definition is None:
            fail('unknown-relation-kind', eid, kind); continue
        if edge.get('kind_version') != definition['version']:
            fail('wrong-definition-version', eid, 'expected '+definition['version'])
        source = nodes.get(key(edge['source'])); target = nodes.get(key(edge['target']))
        if source is None or target is None:
            fail('absent-endpoint', eid, 'exact endpoint version missing'); continue
        if {'source_kind': source['kind'], 'target_kind': target['kind']} not in definition['pairs']:
            fail('undeclared-ordered-pair', eid, 'source and target type pair is absent')
        if set(qualifiers) != set(definition['fields']) or not all(isinstance(v, str) and v for v in qualifiers.values()):
            fail('invalid-qualifiers', eid, 'closed required nonempty strings expected'); continue
        if kind not in SUPPORTED:
            unsupported.append({'assertion_id': eid, 'relation_kind': kind,
                                'axes': definition['fields'], 'obligation': 'reference and normative meanings require an accepted profile'})
            continue
        if kind in {'relation.conforms-to', 'relation.declares-effect-on'}:
            field = 'exact_version_ref' if kind == 'relation.conforms-to' else 'exact_target_version_ref'
            if qualifiers[field] != edge['target']['version']:
                fail('wrong-target-version', eid, field+' must equal the literal target version')
        if kind == 'relation.declares-effect-on':
            resolved.append({'assertion_id': eid, 'meaning': 'declared effect with exact target version; no execution or authority consequence'})
            continue
        is_conformance = kind == 'relation.conforms-to'
        field = 'conformance_evidence_refs' if is_conformance else 'application_receipt_ref'
        assessment = assessments.get(qualifiers[field])
        if assessment is None:
            fail('absent-evidence', eid, field+' token does not resolve'); continue
        expected_mode = 'conformance' if is_conformance else 'application-receipt'
        if assessment['mode'] != expected_mode: fail('wrong-evidence-type', eid, expected_mode+' expected')
        if assessment['accepted'] is not True: fail('unaccepted-evidence', eid, 'assessment has not been accepted')
        if assessment['subject'] != edge['source'] or assessment['target'] != edge['target']:
            fail('wrong-evidence-endpoints', eid, 'subject and target including versions must match')
        if is_conformance:
            if assessment['scope'] != qualifiers['conformance_scope']:
                fail('wrong-evidence-scope', eid, 'assessment scope must equal qualifier scope')
        else:
            if assessment['role'] != qualifiers['consequence_role']:
                fail('wrong-evidence-role', eid, 'receipt role must equal consequence role')
            if assessment['output_digest'] != qualifiers['output_digest'] or target['content_identity'] != qualifiers['output_digest']:
                fail('wrong-output-identity', eid, 'receipt, qualifier and target identities must match')
        resolved.append({'assertion_id': eid, 'evidence_token': assessment['ref'], 'expected_mode': expected_mode})
    for root in graph['admission_roots']:
        subject = nodes.get(key(root['subject'])); decision = nodes.get(key(root['decision']))
        if subject is None or decision is None or decision['kind'] != 'decision' or not root['authority_evidence']:
            fail('invalid-supplied-admission-root', root['subject'], 'resolved subject, decision node and supplied authority evidence required')
    return {'status': 'invalid' if errors else 'unsupported' if unsupported else 'supported',
            'errors': errors, 'unsupported': unsupported, 'resolutions': resolved,
            'supplied_admission_roots': deepcopy(graph['admission_roots']),
            'derived_admission_roots': [], 'authority_effect': 'none',
            'trust_boundary': ['source interpretation', 'JSON projection', 'external assessment truth', 'supplied authority evidence truth']}


def policy(registry):
    meanings = {
        'relation.conforms-to': {'conformance_scope': 'literal scope equals conformance assessment scope',
                                'exact_version_ref': 'literal value equals target.version',
                                'conformance_evidence_refs': 'one opaque token resolves to accepted conformance assessment for exact endpoints'},
        'relation.declares-effect-on': {'effect_kind': 'nonempty declaration only',
                                     'exact_target_version_ref': 'literal value equals target.version'},
        'relation.materializes-consequence': {'application_receipt_ref': 'one opaque token resolves to accepted application-receipt assessment',
                                           'consequence_role': 'literal value equals receipt role',
                                           'output_digest': 'opaque identity equals receipt and target identity; hashing and authentic execution external'}}
    return {'schema': 'relational.reference-policy/v1', 'authority_effect': 'none',
            'normalization': 'exact literal strings; no implicit compound-reference splitting',
            'entries': [{'kind': row['id'], 'version': row['version'],
                         'axes': [{'axis': axis, 'status': 'supported' if row['id'] in meanings else 'unsupported',
                                   'meaning': meanings.get(row['id'], {}).get(axis),
                                   'unresolved_obligation': None if row['id'] in meanings else 'typed version/role/scope interpretation not established'}
                                  for axis in row['fields']]} for row in registry['kinds']],
            'stress_profiles': 'acts-for and inherits-contract have separate candidate typed profiles; legacy qualifiers are not silently decoded into them',
            'forbidden_inference': 'Qualifiers and assessments do not create admission roots or establish authentic execution.'}
