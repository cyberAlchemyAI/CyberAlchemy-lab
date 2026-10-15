"""Resolve complete catalog and carrier impacts from an independently pinned cut.

This module does not authenticate a host or select its live cut. Public integration
must supply a verified current snapshot, compare it with the selected projection,
validate all prospective cores/schemas, and retain its original policy guards.
"""
import base64
import copy
import importlib

from . import adapter as A


def select_bound_catalog(snapshot, *, expected_profile_sha256,
                         expected_snapshot_digest, evidence_bytes):
    inspector = A.kernel()
    sources = importlib.import_module(inspector.__package__ + '.sources')
    sources.verify_snapshot(snapshot, expected_profile_sha256=expected_profile_sha256)
    A.require(snapshot['snapshot_digest'] == expected_snapshot_digest,
              'independent semantic snapshot pin differs')
    materials = dict(evidence_bytes)
    for ref, encoded in snapshot['byte_contents'].items():
        raw = base64.b64decode(encoded, validate=True)
        A.require(ref not in materials or materials[ref] == raw,
                  'candidate evidence cannot shadow canonical bytes')
        materials[ref] = raw
    relations = {}
    for ref, body in snapshot['relation_contracts'].items():
        matches = [s for s in snapshot['subjects'].values()
                   if s['category'] == 'relation-kind'
                   and s['identity'] == ref and s['effective_state'] == 'admitted-current']
        A.require(len(matches) == 1 and matches[0]['record'] == body,
                  'complete current Relation Kind inventory is ambiguous or differs')
        selected = matches[0]
        binding = {'ref': selected['source']['path'], 'sha256': selected['source']['sha256']}
        A.require(binding['ref'] in materials and A.sha(materials[binding['ref']]) == binding['sha256']
                  and A.parse(materials[binding['ref']]) == body,
                  'Relation Kind predecessor original bytes differ')
        p = body['payload']
        relations[ref] = {'version_ref': selected['version_ref'],
                          'effective_state': 'admitted-current',
                          'unique_question': p['unique_question'], 'axis_ref': p['axis_id'],
                          'allowed_endpoint_pairs': [(x['source_kind'], x['target_kind'])
                                                     for x in p['allowed_endpoint_pairs']],
                          'qualifier_contract': copy.deepcopy(p['qualifier_contract']),
                          'signature_binding': binding}
    endpoints, descriptors, schemas = {}, {}, {}
    for ref, contract in snapshot['contracts'].items():
        if contract['lifecycle_state'] != 'admitted-current':
            continue
        path = contract['schema_path']
        A.require(path in materials and A.sha(materials[path]) == contract['schema_sha256'],
                  'current carrier schema original bytes differ')
        descriptor = contract['artifact']
        A.require(descriptor['artifact_type_ref'] == ref
                  and descriptor['schema_digest'] == contract['schema_sha256'],
                  'current carrier descriptor/schema selection differs')
        descriptors[ref] = copy.deepcopy(descriptor)
        schemas[ref] = A.parse(materials[path])
        endpoints[ref] = {'kind': contract['semantic_kind'], 'scope': 'carrier',
                          'effective_state': 'admitted-current',
                          'evidence_binding': {'ref': path, 'sha256': contract['schema_sha256']}}
    A.require('cal.artifact-type.typed-relation/v3' in endpoints,
              'exact current canonical Typed Relation/v3 carrier unavailable')
    return {'relations': relations, 'endpoints': endpoints, 'descriptors': descriptors,
            'schemas': schemas, 'materials': materials,
            'snapshot_digest': expected_snapshot_digest,
            'effective_state_scope': snapshot['effective_state_scope'],
            'live_currentness_established': False, 'authority_effect': 'none'}


def _role_allows(descriptor, relation, direction, counterpart):
    A.require(type(descriptor.get('allowed_relation_kinds')) is list
              and type(descriptor.get('relation_roles')) is list,
              'carrier has no declared endpoint role grammar')
    return relation in descriptor['allowed_relation_kinds'] and any(
        row['relation_kind_ref'] == relation and row['direction'] == direction
        and counterpart in row['counterpart_kinds'] for row in descriptor['relation_roles'])


def _canonical_allows(schema, inspection, materials):
    """Read the exact declared generic carrier grammar; no wildcard inference."""
    relation = inspection['relation_kind_ref']
    props = schema.get('properties', {}).get('payload', {}).get('properties', {})
    A.require(type(props.get('relation_kind_ref', {}).get('enum')) is list,
              'canonical carrier has no closed Relation Kind discriminator')
    if relation not in props['relation_kind_ref']['enum']:
        return False
    rules = [row for row in schema.get('allOf', [])
             if row.get('if', {}).get('properties', {}).get('payload', {}).get('properties', {})
             .get('relation_kind_ref', {}).get('const') == relation]
    A.require(len(rules) == 1, 'canonical exact relation branch missing or ambiguous')
    branch = rules[0]['then']['properties']['payload']
    declared = set()
    for pair in branch['oneOf']:
        p = pair['properties']
        declared.add((p['source']['properties']['kind']['const'],
                      p['target']['properties']['kind']['const']))
    prior = branch['properties']['qualifiers']
    inspector = A.kernel()
    for pair in inspection['allowed_endpoint_pairs']:
        if (pair['source_kind'], pair['target_kind']) not in declared:
            return False
        b = pair['qualifier_schema_binding']
        A.require(b['ref'] in materials and A.sha(materials[b['ref']]) == b['sha256'],
                  'exact candidate qualifier domain unavailable')
        domain = A.parse(materials[b['ref']])
        closed = inspector.check_closed_domain(domain)
        combined = copy.deepcopy(domain)
        combined.setdefault('allOf', []).append(prior)
        try:
            accepted = inspector.check_closed_domain(combined)
        except inspector.RuntimeFault:
            return False
        if accepted['allowed_values'] != closed['allowed_values']:
            return False
    return True


def assess_carrier_impacts(selection, inspection):
    """Inspect every declared ordered endpoint role and generic carrier schema."""
    relation = inspection['relation_kind_ref']
    old = selection['relations'].get(relation)
    pairs = inspection['allowed_endpoint_pairs']
    keys = {(p['source_kind'], p['target_kind']) for p in pairs}
    A.require(len(keys) == len(pairs) and all('*' not in key for key in keys),
              'exact unique ordered pairs required')
    if old is not None:
        A.require(set(old['allowed_endpoint_pairs']) <= keys,
                  'extension cannot remove predecessor ordered pairs')
    impacts = set()
    reasons = []
    for pair in pairs:
        A.require(pair['canonical_authority'] == 'typed-relation'
                  and pair['projection_binding'] is None,
                  'specialized authority requires its own independently bound impact resolver')
        for direction, counterpart in [('source', 'target'), ('target', 'source')]:
            ref = pair[direction + '_contract_ref']
            A.require(ref in selection['endpoints'],
                      'endpoint requires an independently validated prospective carrier resolver')
            A.require(selection['endpoints'][ref]['kind'] == pair[direction + '_kind'],
                      'exact endpoint carrier kind differs')
            if not _role_allows(selection['descriptors'][ref], relation,
                                direction, pair[counterpart + '_kind']):
                impacts.add(ref)
                reasons.append({'carrier_ref': ref, 'reason': 'ordered endpoint role is undeclared',
                                'direction': direction, 'counterpart_kind': pair[counterpart + '_kind']})
    canonical = 'cal.artifact-type.typed-relation/v3'
    if not _canonical_allows(selection['schemas'][canonical], inspection, selection['materials']):
        impacts.add(canonical)
        reasons.append({'carrier_ref': canonical, 'reason': 'exact pair/qualifier schema requires a successor'})
    return {'required_current_carrier_refs': sorted(impacts), 'impact_reasons': reasons,
            'complete_current_carrier_inventory_count': len(selection['endpoints']),
            'globally_available_pairs_added': 0, 'authority_effect': 'none',
            'unsupported_resolvers': ['specialized-authority', 'new-prospective-endpoint']}


def resolve_impacted_successors(impact, proposal, read_material):
    """Require one exact explicit successor target for each affected carrier."""
    selected = []
    for ref in impact['required_current_carrier_refs']:
        identity = ref.rsplit('/', 1)[0]
        matches = [t for t in proposal['targets'] if t['operation'] == 'revise'
                   and t['artifact']['identity_ref'] == identity
                   and t['artifact']['carrier_ref'] == 'cal.artifact-type.artifact-type/v3'
                   and t['predecessor'] is not None and t['predecessor']['version_ref'] == ref]
        A.require(len(matches) == 1, 'complete affected carrier successor missing or ambiguous')
        target = matches[0]
        raw = read_material({'ref': target['content']['content_ref'],
                             'sha256': target['content']['byte_sha256']})
        A.require(type(raw) is bytes and A.sha(raw) == target['artifact']['byte_sha256']
                  == target['content']['byte_sha256'] and len(raw) == target['content']['size_bytes'],
                  'affected carrier successor exact bytes differ')
        body = A.parse(raw)
        A.require(body['artifact_type_id'] == identity
                  and body['artifact_type_ref'] == target['artifact']['version_ref']
                  and body['artifact_type_ref'] != ref,
                  'affected carrier successor identity or revision differs')
        selected.append(A.public_header(target['artifact']))
    return selected
