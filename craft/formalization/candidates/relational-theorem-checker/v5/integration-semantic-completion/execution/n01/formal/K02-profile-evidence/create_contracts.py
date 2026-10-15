"""Candidate authority snapshot shape, local API, and exact obligation mapping."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, data): path.write_text(json.dumps(data, indent=2) + '\n')
def closed(properties): return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}
def array(item): return {'type': 'array', 'items': item}


def run():
    definitions = json.loads((HERE.parent / 'K02-profile-selection/schemas/declaration.schema.json').read_text())['$defs']
    ref = {'$ref': '#/$defs/revisionRef'}
    text = {'type': 'string', 'minLength': 1}
    target = closed({
        'trust_root': ref, 'bootstrap': closed({'ref': ref, 'algorithm': text, 'encoding': text}),
        'declaration_manifest': array(ref), 'selection_manifest': array(ref),
        'issuances': array(closed({'source_ref': ref, 'source_kind': text, 'issuer': ref, 'owner_review_ref': ref,
                                   'source_bytes': array({'type': 'integer', 'minimum': 0, 'maximum': 255})})),
        'entitlements': array(closed({'ref': ref, 'principal': ref, 'actions': array({'enum': ['declare', 'select']}), 'scope': ref})),
        'reviews': array(closed({'ref': ref, 'source_ref': ref, 'decision': {'enum': ['missing', 'accepted', 'rejected']},
                                'revocation': {'enum': ['unknown', 'clear', 'revoked']}, 'expiry_epoch': {'type': 'integer', 'minimum': 0}}))
    })
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
              '$id': 'urn:cyberalchemy:lab:candidate:profile-authority-snapshot:v1', '$defs': definitions,
              'description': 'Candidate decoded-value evidence shape. Exact byte capture, reference/frame/root joins, non-equivocation and authentic/admissible snapshot evidence remain separate checks.',
              **closed({'schema_version': {'const': 'cyberalchemy-lab-profile-authority-snapshot/candidate-v1'},
                        'binding_revision_key': {'$ref': '#/$defs/revisionKey'}, 'kind': {'const': 'profile-authority-snapshot'},
                        'body': closed({'token': text, 'target': target, 'frame': {'$ref': '#/$defs/frame'}}), 'owner_review_ref': ref})}
    schema_path = HERE / 'authority-snapshot.schema.json'; save(schema_path, schema)
    save(HERE / 'candidate-api-contract.json', {
        'schema': 'relational.candidate-authority-evidence-api/v1', 'task': 'N01', 'unit': 'K02-profile-evidence',
        'status': 'candidate-local-Lean-api', 'source_schema': binding(schema_path),
        'numeric_representation_correction': binding(HERE / 'NUMERIC-REPRESENTATION-CORRECTION.md'),
        'functions': [
            {'name': 'prepareAuthority', 'inputs': ['bootstrap: Profile', 'budget: Nat', 'frame: Frame',
                'expectedTrustRoot: RevisionRef', 'expectedAuthority: RevisionRef', 'capture: Envelope'],
             'output': 'Option CapturedAuthority', 'success': 'AuthorityDataMeaning',
             'effects': 'Pure capture/header/coherence preparation; no root authenticity or ownership grant.'},
            {'name': 'prepareProfileEvidence', 'inputs': ['bootstrap: Profile', 'limits: Limits', 'frame: Frame',
                'expectedTrustRoot: RevisionRef', 'expectedAuthority: RevisionRef', 'authorityCapture: Envelope',
                'declarations/selections: List Envelope'], 'output': 'Option EvidenceStage',
             'success': 'PreparedEvidenceMeaning', 'failure': 'No stage satisfies that independent data meaning; Option exposes no public cause.'},
            {'name': 'interpretedRequirements', 'inputs': ['rootPolicy: RootPolicy', 'bootstrap: Profile', 'limits: Limits',
                'expectedTrustRoot/Authority: RevisionRef', 'authorityCapture: Envelope', 'authority: CapturedAuthority'],
             'output': 'EvidenceRequirements', 'effects': 'Eight concrete exact interpretations, each requiring TrustedAuthorityMeaning and an actual authoritative-snapshot boundary.'}
        ],
        'namespace': 'RelationalSuccessor.CandidateProfileEvidence',
        'evidence_stage_fields': ['profile: previous Stage', 'authority: CapturedAuthority'],
        'snapshot_fields': ['trustRoot', 'bootstrap', 'ordered declaration manifest', 'ordered selection manifest', 'issuances', 'entitlements', 'reviews'],
        'issuance_byte_policy': 'Complete original UInt8 content is compared to exact Nat values, with a global 0..255 guard. No modulo conversion or hash-only matching.',
        'grant_policy': 'One exact grant may permit declare and select. Every required principal/action/scope join is exact.',
        'review_policy': 'One complete owner-review reference may cover multiple sources. Conflicting full references at one review key or assertions at one review/source key pair refuse, including unused facts.',
        'trust_boundary': 'RootPolicy.authoritativeSnapshot must establish authenticity, completeness and admissibility of this exact original snapshot under an independently selected root/frame. No real provider is supplied.',
        'budget_policy': 'Existing total/count bounds cover declaration/selection inputs. The authority capture has the configured per-capture bound. A combined authority-plus-input total/count guard and measured runtime profile remain pending.',
        'representation_limits': ['Schema validates decoded values; duplicate keys and numeric lexemes require the exact raw-byte decoder.',
                                  'Source/root references and approval/revocation labels cannot establish authentic authority.',
                                  'No HTTP API, public diagnostic classification or N03 freeze is implemented.'],
        'eight_evidence_requirements_interpreted': True, 'real_authoritative_snapshot_provider': False,
        'authenticated_capture_proved': False, 'JSON_schema_semantics_interpreter_proved': False,
        'N03_API_freeze': False, 'inherited_discharges': 0, 'authority_effect': 'none'
    })
    mappings = [
        ('snapshot byte/record/header/coherence interpretation', 'AuthorityPreparation.lean', ['authority_preparation_exact']),
        ('complete profile-plus-evidence interpretation', 'AuthorityPreparation.lean', ['profile_evidence_preparation_exact', 'profile_evidence_none_exact']),
        ('exact original source byte and evidence joins', 'AuthorityChecks.lean', ['issuance_exact', 'entitlement_exact', 'review_check_exact', 'evidence_rows_exact', 'exact_issuance_preserves_original_bytes']),
        ('original source envelope retention', 'AuthorityPreparation.lean', ['prepared_evidence_retains_inputs']),
        ('actual root boundary and conditional ownership', 'AuthorityOwnership.lean', ['prepared_evidence_and_authentic_boundary_construct_ownership', 'ownership_requires_actual_snapshot_boundary', 'absent_boundary_blocks_owned_profile']),
        ('conditional complete capture bridge', 'AuthorityOwnership.lean', ['complete_capture_from_interpreted_evidence'])
    ]
    rows = []
    for contract, stem, names in mappings:
        assert set(names) <= set(re.findall(r'^theorem (\w+)', (HERE / stem).read_text(), re.M))
        rows.append({'contract': contract, 'source': binding(HERE / stem),
                     'theorem_targets': ['RelationalSuccessor.CandidateProfileEvidence.' + name for name in names],
                     'inherited_discharges': 0})
    for contract in ['real authoritative-snapshot provider', 'Schema semantics and full nineteen-policy K02 realization',
                     'public diagnostics', 'combined-resource guards and measured operational profile', 'independent closure checking', 'whole-theory/inherited-ID closure']:
        rows.append({'contract': contract, 'status': 'not-established', 'inherited_discharges': 0})
    save(HERE / 'refinement-matrix.json', {'task': 'N01', 'unit': 'K02-profile-evidence', 'rows': rows,
                                         'inherited_discharges': 0, 'authority_effect': 'none'})
    print({'candidate_schemas': 1, 'local_functions': 3, 'refinement_rows': len(rows)})


if __name__ == '__main__': run()
