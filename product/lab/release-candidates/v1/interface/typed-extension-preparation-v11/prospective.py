"""Resolve prospective carriers from exact proposal bodies and separate contracts.

These are candidate-for-R08 facts only. Full original custody preparation and the
host's independent source/Actor/permission checks remain required. This module
cannot turn a proposed descriptor into an admitted endpoint or writable pair.
"""
import copy
from pathlib import PurePosixPath
from jsonschema import Draft202012Validator
from . import adapter as A

CONTRACT_FIELDS = set('semantic_kind schema_path schema_sha256 schema_selector instance_discriminator identity_field allowed_relation_kinds relation_roles'.split())
SLOT_FIELDS = set('artifact_type_ref semantic_kind semantic_definition_refs schema_path schema_selector schema_sha256 distinct_validation_purpose'.split())


def resolve_prospective_carriers(selection, inspection, proposal, *,
                                 read_material, independently_selected_schema_paths):
    """Resolve every unknown exact endpoint ref; no caller effective-state labels.

    Metadata and schema bindings belong to the exact type target and its stable
    core. The original backend must subsequently validate that complete core,
    Definition closure and proposed transaction. Missing directional roles are a
    malformed prospective contract, rather than a request to revise a current one.
    """
    future = copy.deepcopy(selection)
    unknown = sorted({pair[direction + '_contract_ref'] for pair in inspection['allowed_endpoint_pairs']
                      for direction in ('source', 'target')
                      if pair[direction + '_contract_ref'] not in selection['endpoints']})
    schemas = {}
    for binding in proposal['schema_bindings']:
        A.require(binding['ref'] in independently_selected_schema_paths,
                  'prospective schema lacks independent destination selection')
        raw = read_material(binding)
        A.require(type(raw) is bytes and A.sha(raw) == binding['sha256'],
                  'prospective schema original bytes differ')
        path = independently_selected_schema_paths[binding['ref']]
        p = PurePosixPath(path)
        A.require(type(path) is str and p.as_posix() == path and path.startswith('runtime/schemas/')
                  and path.endswith('.json') and '..' not in p.parts and path not in schemas,
                  'prospective schema destination is unsafe or ambiguous')
        schema = A.parse(raw); Draft202012Validator.check_schema(schema)
        schemas[path] = (schema, binding, raw)
    proofs = []
    for ref in unknown:
        targets = [t for t in proposal['targets'] if t['operation'] in ('admit', 'revise')
                   and t['artifact']['version_ref'] == ref
                   and t['artifact']['carrier_ref'] == 'cal.artifact-type.artifact-type/v3']
        A.require(len(targets) == 1, 'prospective exact registered-type target missing or ambiguous')
        target = targets[0]; header = A.public_header(target['artifact']); content = target['content']
        raw = read_material({'ref': content['content_ref'], 'sha256': content['byte_sha256']})
        A.require(type(raw) is bytes and A.sha(raw) == content['byte_sha256'] == header['byte_sha256']
                  and len(raw) == content['size_bytes'] and content['media_type'] == 'application/json',
                  'prospective descriptor exact content/header bytes differ')
        body = A.parse(raw)
        A.require(set(body) == SLOT_FIELDS and body['artifact_type_ref'] == ref
                  and ref.rsplit('/', 1)[0] == header['identity_ref']
                  and header['scope_ref'] == proposal['scope_ref'],
                  'prospective registered slot identity or scope differs')
        if target['operation'] == 'admit':
            A.require(target['predecessor'] is None and not any(
                old.rsplit('/', 1)[0] == header['identity_ref'] for old in selection['endpoints']),
                'prospective admit shadows a current carrier family')
        else:
            predecessor = target['predecessor']
            if predecessor is not None:
                A.public_header(predecessor)
            A.require(predecessor is not None and predecessor['version_ref'] in selection['endpoints']
                      and predecessor['identity_ref'] == header['identity_ref']
                      and predecessor['version_ref'].rsplit('/', 1)[0] == header['identity_ref']
                      and predecessor['scope_ref'] == header['scope_ref'],
                      'prospective revision lacks its exact independently selected predecessor')
            # A captured predecessor may use the earlier registration carrier.
            # Its exact original carrier/byte identity is checked against the
            # independent projection by the complete backend preparation.
        meta_raw = read_material(target['candidate_binding'])
        A.require(type(meta_raw) is bytes and A.sha(meta_raw) == target['candidate_binding']['sha256'],
                  'prospective metadata original bytes differ')
        meta = A.parse(meta_raw)
        A.require(set(meta) == {'schema_version', 'category', 'decision_ref', 'contract'}
                  and meta['schema_version'] == 'lab-candidate-target-metadata/v1-candidate'
                  and meta['category'] == 'artifact-type' and type(meta['decision_ref']) is str
                  and bool(meta['decision_ref']), 'prospective closed independent type metadata required')
        contract = meta['contract']
        A.require(type(contract) is dict and set(contract) == CONTRACT_FIELDS,
                  'prospective separate schema/role contract must be closed')
        A.require(all(body[k] == contract[k] for k in ('semantic_kind', 'schema_path', 'schema_sha256', 'schema_selector')),
                  'prospective descriptor and separate contract differ')
        A.require(contract['schema_selector'] is None and contract['schema_path'] in schemas,
                  'prospective carrier needs an exact complete proposed schema')
        schema, binding, schema_raw = schemas[contract['schema_path']]
        A.require(A.sha(schema_raw) == contract['schema_sha256'], 'prospective schema identity differs')
        slot = selection['schemas']['cal.artifact-type.artifact-type/v3']['properties']['registered_types']['items']
        A.require(Draft202012Validator(slot).is_valid(body), 'prospective original registration slot refused')
        descriptor = {**body, 'instance_contract': {'identity_field': contract['identity_field'],
                         'instance_discriminator': copy.deepcopy(contract['instance_discriminator'])},
                      'allowed_relation_kinds': copy.deepcopy(contract['allowed_relation_kinds']),
                      'relation_roles': copy.deepcopy(contract['relation_roles'])}
        A.require(type(descriptor['allowed_relation_kinds']) is list and type(descriptor['relation_roles']) is list,
                  'prospective closed role lists required')
        future['endpoints'][ref] = {'kind': contract['semantic_kind'], 'scope': 'carrier',
                                   'effective_state': 'candidate-for-R08', 'evidence_binding': copy.deepcopy(binding)}
        future['descriptors'][ref] = descriptor
        future['schemas'][ref] = schema
        future['materials'][binding['ref']] = schema_raw
        proofs.append({'artifact': header, 'candidate_binding': copy.deepcopy(target['candidate_binding']),
                       'schema_binding': copy.deepcopy(binding), 'decision_core_binding': copy.deepcopy(target['decision_core_binding']),
                       'effective_state': 'candidate-for-R08', 'full_original_backend_checks_required': True})
    # A candidate's own endpoint role grammar must already be explicit for review.
    # Full target/contract/core validation remains the unchanged backend's job.
    from .source_selection import _role_allows
    for pair in inspection['allowed_endpoint_pairs']:
        for direction, counterpart in [('source', 'target'), ('target', 'source')]:
            ref = pair[direction + '_contract_ref']
            if ref in unknown:
                A.require(future['endpoints'][ref]['kind'] == pair[direction + '_kind'],
                          'prospective endpoint semantic kind differs')
                A.require(_role_allows(future['descriptors'][ref], inspection['relation_kind_ref'],
                                      direction, pair[counterpart + '_kind']),
                          'prospective exact directional role is undeclared')
    return future, {'schema_version': 'lab-prospective-endpoint-selection/v1-candidate',
                    'pending_endpoint_admission_refs': unknown, 'candidate_bindings': proofs,
                    'globally_available_pairs_added': 0, 'actual_transactions_written': 0,
                    'live_currentness_established': False, 'actual_owner_outcome': None,
                    'public_handler_qualified': False, 'authority_effect': 'none'}
