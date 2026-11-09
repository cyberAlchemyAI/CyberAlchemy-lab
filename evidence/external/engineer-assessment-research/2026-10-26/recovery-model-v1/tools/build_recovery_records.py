"""Build source-bound recovery rules and three local Artifact Type requests.

All outputs remain project candidates. Fixtures are synthetic; no real participant
failure, upload, decision, grant or Lab admission is asserted.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

ROOT = Path(__file__).resolve().parents[1]
LAB = Path(os.environ.get('CYBERALCHEMY_LAB_ROOT', str(ROOT.parent / 'CyberAlchemy-lab')))
SOURCE = ROOT / 'model/recovery/rule-source.json'
OUT = ROOT / 'model/recovery'
CARRIERS = ROOT / 'model/carriers'
REGISTRY = LAB / 'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'


def sha(data): return hashlib.sha256(data).hexdigest()
def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def schema_field(kind, **kwargs): return {'type': kind, **kwargs}


FAMILIES = {
    'recovery-rule': {
        'meaning': 'ea.recovery-rule', 'identity': 'rule_id', 'filename': 'rule.json',
        'purpose': 'Validate one failure-class-specific administration rule with detection, preserved evidence, timer and recovery disposition, without treating it as an observed incident or active Lab policy.',
        'near': 'cal.artifact-type.policy/v2',
        'rejection': 'The selected Lab Policy is an issued governance rule set with authority scope; this is one candidate application recovery rule under an unapproved Administration Policy.',
    },
    'recovery-decision': {
        'meaning': 'ea.recovery-decision', 'identity': 'decision_id', 'filename': 'decision.json',
        'purpose': 'Validate one runtime disposition of an affected session against pinned failure evidence and recovery rule, including same-slot successor and non-scoring boundaries.',
        'near': 'cal.artifact-type.decision/v2',
        'rejection': 'The Lab Decision carrier is an authority act; this operational receipt evaluates an administration rule and cannot admit policy, authorize recruitment or replace an owner decision.',
    },
    'upload-attempt': {
        'meaning': 'ea.upload-attempt', 'identity': 'upload_attempt_id', 'filename': 'upload.json',
        'purpose': 'Validate one resumable private media transfer with part receipts, source digest, session pin and final verification state, without equating upload with accepted response.',
        'near': 'cal.artifact-type.operational-observation/v1',
        'rejection': 'An Operational Observation is an attributable datum; a resumable upload needs an idempotent transfer state machine, part lineage and completion/abort invariants.',
    },
}


def base_schema(family):
    ref = 'ea.artifact-type.' + family + '/v1-candidate'
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'title': family + ' candidate record', 'type': 'object', 'additionalProperties': False,
        'properties': {
            'schema_version': {'const': 'ea.' + family + '/v1-candidate'},
            'artifact_type_ref': {'const': ref},
            'status': {'enum': ['candidate-unadmitted', 'synthetic-fixture', 'recorded']},
            'authority_effect': {'const': 'none'},
            'claim_ceiling': schema_field('string', minLength=1),
        },
        'required': ['schema_version', 'artifact_type_ref', 'status', 'authority_effect', 'claim_ceiling'],
    }


def make_schemas():
    string = schema_field('string', minLength=1)
    nullable = {'type': ['string', 'null'], 'minLength': 1}
    rule = base_schema('recovery-rule')
    rule['properties'].update({
        'rule_id': {'pattern': '^RR-[0-9]{2}$', **string}, 'version': string,
        'policy_ref': string, 'failure_class': string,
        'phase': {'enum': ['before_start', 'recording', 'upload_pending', 'transcript_pending', 'scoring_pending', 'any_nonterminal']},
        'detection': string, 'preserve': string,
        'timer_behavior': {'enum': ['not_started', 'continues_original_deadline', 'stopped_no_extension', 'stop']},
        'default_disposition': {'enum': ['wait_same_assignment', 'continue_offline_capture', 'resume_upload', 'technical_void', 'human_review', 'withdrawn']},
        'participant_message': string, 'source_ref': {'const': 'model/recovery/rule-source.json'},
        'source_sha256': {'pattern': '^[a-f0-9]{64}$', **string},
        'source_index': schema_field('integer', minimum=0),
        'source_excerpt_sha256': {'pattern': '^[a-f0-9]{64}$', **string},
        'owner_ref': string,
    })
    rule['required'] += ['rule_id', 'version', 'policy_ref', 'failure_class', 'phase', 'detection', 'preserve', 'timer_behavior', 'default_disposition', 'participant_message', 'source_ref', 'source_sha256', 'source_index', 'source_excerpt_sha256', 'owner_ref']
    decision = base_schema('recovery-decision')
    decision['properties'].update({
        'decision_id': string, 'revision': schema_field('integer', minimum=1),
        'session_assignment_ref': string, 'case_version_ref': string, 'slot': schema_field('integer', minimum=1, maximum=3),
        'policy_ref': string, 'rule_ref': string, 'event_refs': {'type': 'array', 'minItems': 1, 'uniqueItems': True, 'items': string},
        'outcome': {'enum': ['wait_same_assignment', 'continue_offline_capture', 'resume_upload', 'technical_void', 'replace_same_slot', 'human_review', 'withdrawn']},
        'reason': string, 'timer_deadline': nullable, 'recorded_seconds_remaining': {'type': ['number', 'null'], 'minimum': 0, 'maximum': 600},
        'timing_assurance': {'enum': ['server-evidenced', 'client-only', 'unknown']},
        'analysis_posture': {'enum': ['primary-candidate', 'sensitivity-only', 'excluded']},
        'successor_assignment_ref': nullable, 'media_ref': nullable, 'actor_ref': string,
        'idempotency_key': string, 'created_at': string, 'supersedes_ref': nullable,
    })
    decision['required'] += [k for k in decision['properties'] if k not in decision['required']]
    decision['allOf'] = [{'if': {'properties': {'outcome': {'const': 'replace_same_slot'}}}, 'then': {'properties': {'successor_assignment_ref': string}}}, {'if': {'properties': {'outcome': {'enum': ['continue_offline_capture', 'resume_upload', 'wait_same_assignment']}}}, 'then': {'properties': {'successor_assignment_ref': {'type': 'null'}}}}]
    upload = base_schema('upload-attempt')
    upload['properties'].update({
        'upload_attempt_id': string, 'session_assignment_ref': string, 'case_version_ref': string,
        'storage_provider': string, 'storage_region': string, 'object_key': string, 'provider_upload_id': string,
        'state': {'enum': ['initiated', 'parts_uploading', 'awaiting_commit', 'verified', 'aborted', 'failed']},
        'declared_media_sha256': {'pattern': '^[a-f0-9]{64}$', **string},
        'declared_size_bytes': schema_field('integer', minimum=1), 'part_size_bytes': schema_field('integer', minimum=5242880),
        'confirmed_parts': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['number', 'etag', 'size_bytes'], 'properties': {'number': schema_field('integer', minimum=1), 'etag': string, 'size_bytes': schema_field('integer', minimum=1)}}},
        'upload_window_ends_at': string, 'verified_media_ref': nullable,
        'verified_sha256': {'type': ['string', 'null'], 'pattern': '^[a-f0-9]{64}$'},
        'idempotency_key': string, 'supersedes_ref': nullable,
    })
    upload['required'] += [k for k in upload['properties'] if k not in upload['required']]
    upload['allOf'] = [{'if': {'properties': {'state': {'const': 'verified'}}}, 'then': {'properties': {'verified_media_ref': string, 'verified_sha256': {'pattern': '^[a-f0-9]{64}$', **string}}}}, {'if': {'properties': {'state': {'enum': ['initiated', 'parts_uploading', 'awaiting_commit']}}}, 'then': {'properties': {'verified_media_ref': {'type': 'null'}, 'verified_sha256': {'type': 'null'}}}}]
    return {'recovery-rule': rule, 'recovery-decision': decision, 'upload-attempt': upload}


def build():
    source = json.loads(SOURCE.read_text(encoding='utf-8'))
    assert source['authority_effect'] == 'none' and len(source['rules']) == 20
    source_sha = sha(SOURCE.read_bytes())
    ids = [r['rule_id'] for r in source['rules']]
    assert ids == [f'RR-{n:02d}' for n in range(1, 21)]
    refs = []
    for i, row in enumerate(source['rules']):
        record = {
            'schema_version': 'ea.recovery-rule/v1-candidate', 'artifact_type_ref': 'ea.artifact-type.recovery-rule/v1-candidate',
            'status': 'candidate-unadmitted', 'authority_effect': 'none', 'version': '0.1.0-candidate.1',
            'policy_ref': source['policy_ref'], **row,
            'source_ref': 'model/recovery/rule-source.json', 'source_sha256': source_sha,
            'source_index': i, 'source_excerpt_sha256': sha(json.dumps(row, sort_keys=True, ensure_ascii=False).encode()),
            'owner_ref': 'role:ea-assessment-owner-unassigned',
            'claim_ceiling': 'Candidate recovery rule only; no approved administration policy or real failure disposition.',
        }
        path = OUT / 'rules' / (row['rule_id'].lower() + '.json')
        write(path, record)
        refs.append(str(path.relative_to(ROOT)))
    write(OUT / 'index.json', {'schema_version': 'ea.recovery-rule-index/v1', 'status': 'candidate-unadmitted', 'authority_effect': 'none', 'source_ref': 'model/recovery/rule-source.json', 'source_sha256': source_sha, 'count': len(refs), 'record_refs': refs})

    schemas = make_schemas()
    registry_ref = str(REGISTRY.relative_to(LAB)) + '#sha256=' + sha(REGISTRY.read_bytes())
    spec = importlib.util.spec_from_file_location('ea_artifact_surface_recovery', LAB / 'tooling/generators/artifact_surface.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    request_type = json.loads((LAB / 'authority/artifact-types/artifact-type-request/v1/artifact.json').read_text())
    for family, config in FAMILIES.items():
        base = CARRIERS / family / 'v1'
        base.mkdir(parents=True, exist_ok=True)
        write(base / 'schema.json', schemas[family])
        meaning_file = ROOT / 'model/definition-records' / family / 'definition.json'
        request = {
            'schema_version': 'cyberalchemy-lab-artifact-type-request/v1', 'request_id': 'EA-ATR-' + family.upper().replace('-', '-') + '-001',
            'version': '0.1.0-candidate.1', 'status': 'candidate-unadmitted', 'authority_effect': 'none',
            'owner_ref': 'role:ea-artifact-type-owner-unassigned',
            'proposed_semantic_kind': family, 'semantic_definition_refs': [config['meaning'] + '@0.1.0-candidate.1'],
            'validation_purpose': config['purpose'],
            'representation_proposal': {'canonical_filename': config['filename'], 'human_filename': Path(config['filename']).stem.upper() + '.md', 'projection_policy': 'generated-only'},
            'compatibility_analysis': [{'existing_type_ref': config['near'], 'rejection_reason': config['rejection']}],
            'resolution_evidence': {'registry_ref': registry_ref, 'matches': []},
            'proposed_package_home_ref': str(base.relative_to(ROOT)), 'consumed_as_subject': False,
            'expiry': {'condition': 'Resolved, rejected or superseded after exact semantic and Artifact Type owner review.', 'superseded_by': None},
            'source_direction': {'canonical': 'request.json', 'human_projection': 'REQUEST.md', 'projection_policy': 'generated-only', 'generator_ref': 'cal.generator.artifact-surface/v1'},
            'claim_ceiling': 'Candidate request only; no Lab type admission, operational decision, media receipt or participant authority.',
        }
        write(base / 'request.json', request)
        (base / 'REQUEST.md').write_text(module.render_instance(request_type, json.loads((base / 'request.json').read_text(encoding='utf-8'))), encoding='utf-8')
        descriptor = {
            'schema_version': 'ea.artifact-type-candidate/v1', 'artifact_type_ref': 'ea.artifact-type.' + family + '/v1-candidate',
            'name': family.replace('-', ' ').title(), 'status': 'candidate-unadmitted', 'authority_effect': 'none',
            'lab_carrier_target': 'cal.artifact-type.artifact-type/v3', 'lab_v3_conformance': 'not-claimed; semantic and type-owner admission bindings pending',
            'request_ref': str((base / 'request.json').relative_to(ROOT)), 'owner_ref': 'role:ea-artifact-type-owner-unassigned',
            'semantic_definition_ref': config['meaning'] + '@0.1.0-candidate.1', 'semantic_definition_sha256': sha(meaning_file.read_bytes()),
            'distinct_validation_purpose': config['purpose'],
            'instance_contract': {'canonical_filename': config['filename'], 'identity_field': config['identity'], 'closed_representation': True,
                                  'schema_ref': str((base / 'schema.json').relative_to(ROOT)), 'schema_sha256': sha((base / 'schema.json').read_bytes())},
            'typed_residue': [{'missing': 'Semantic and Artifact Type owner review plus exact Lab/v3 binding.', 'consequence': 'Local schema has no Lab type standing.'},
                              {'missing': 'Approved Administration Policy, live reference closure and failure simulation.', 'consequence': 'Structural validation cannot authorize a real retry or prove fairness.'}],
            'claim_ceiling': 'Candidate local carrier only; no Lab admission, live participant record or operational effect.',
        }
        write(base / 'artifact.json', descriptor)

    synthetic = OUT / 'synthetic'
    write(synthetic / 'recovery-decision.json', {
        'schema_version': 'ea.recovery-decision/v1-candidate', 'artifact_type_ref': 'ea.artifact-type.recovery-decision/v1-candidate',
        'status': 'synthetic-fixture', 'authority_effect': 'none', 'claim_ceiling': 'Synthetic shape witness only.',
        'decision_id': 'synthetic-rd-001', 'revision': 1, 'session_assignment_ref': 'synthetic-assignment-1',
        'case_version_ref': 'synthetic-case-v1', 'slot': 1, 'policy_ref': 'synthetic-policy-v1',
        'rule_ref': 'RR-06@0.1.0-candidate.1', 'event_refs': ['synthetic-event-1'], 'outcome': 'resume_upload',
        'reason': 'Finished local bytes and part receipts remain within upload window.', 'timer_deadline': '2026-10-26T12:10:00Z',
        'recorded_seconds_remaining': 0, 'timing_assurance': 'server-evidenced', 'analysis_posture': 'primary-candidate',
        'successor_assignment_ref': None, 'media_ref': None,
        'actor_ref': 'synthetic-recovery-worker', 'idempotency_key': 'synthetic-key-1', 'created_at': '2026-10-26T12:12:00Z', 'supersedes_ref': None,
    })
    write(synthetic / 'upload-attempt.json', {
        'schema_version': 'ea.upload-attempt/v1-candidate', 'artifact_type_ref': 'ea.artifact-type.upload-attempt/v1-candidate',
        'status': 'synthetic-fixture', 'authority_effect': 'none', 'claim_ceiling': 'Synthetic shape witness only.',
        'upload_attempt_id': 'synthetic-upload-1', 'session_assignment_ref': 'synthetic-assignment-1',
        'case_version_ref': 'synthetic-case-v1', 'storage_provider': 'synthetic-s3', 'storage_region': 'test',
        'object_key': 'synthetic/private/1', 'provider_upload_id': 'synthetic-multipart-1', 'state': 'parts_uploading',
        'declared_media_sha256': '0' * 64, 'declared_size_bytes': 10485760, 'part_size_bytes': 8388608,
        'confirmed_parts': [{'number': 1, 'etag': 'synthetic-etag', 'size_bytes': 8388608}],
        'upload_window_ends_at': '2026-10-26T13:10:00Z', 'verified_media_ref': None, 'verified_sha256': None,
        'idempotency_key': 'synthetic-upload-key-1', 'supersedes_ref': None,
    })
    print(f'Built {len(refs)} candidate recovery rules, 3 type requests and 2 synthetic shape witnesses')


if __name__ == '__main__': build()
