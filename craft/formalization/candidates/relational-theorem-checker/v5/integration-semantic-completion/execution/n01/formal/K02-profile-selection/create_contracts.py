"""Write separately versioned candidate schemas and an honest local API contract."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]


def binding(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def closed(properties):
    return {'type': 'object', 'properties': properties,
            'required': list(properties), 'additionalProperties': False}


def run():
    directory = HERE / 'schemas'
    directory.mkdir(exist_ok=True)
    text = {'type': 'string', 'minLength': 1}
    reference = {'$ref': '#/$defs/revisionRef'}
    definitions = {
        'revisionKey': closed({field: text for field in ['owner', 'artifact', 'revision']}),
        'revisionRef': closed({'key': {'$ref': '#/$defs/revisionKey'}, 'digest': text}),
        'frame': closed({**{field: reference for field in ['profile', 'subject', 'target', 'context', 'scope', 'snapshot']},
                         'epoch': {'type': 'integer', 'minimum': 0}, 'timeDomain': text})
    }
    postures = {'issuer': reference, 'review_posture': {'enum': ['missing', 'accepted', 'rejected']},
                'revocation_posture': {'enum': ['unknown', 'clear', 'revoked']},
                'expiry_epoch': {'type': 'integer', 'minimum': 0}}
    schemas = []
    for name, target in [('declaration', {'algorithm': text, 'encoding': text, **postures}),
                         ('selection', {'declaration_ref': reference, **postures})]:
        version = 'cyberalchemy-lab-digest-profile-' + name + '/candidate-v1'
        schema = {
            '$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': 'urn:cyberalchemy:lab:candidate:digest-profile-' + name + ':v1',
            'title': 'Candidate digest profile ' + name,
            'description': 'Decoded-value source shape only. Full byte grammar, exact frame, eligibility, digest, selected profile support and authentic ownership require separate checks.',
            '$defs': definitions,
            **closed({'schema_version': {'const': version},
                      'binding_revision_key': {'$ref': '#/$defs/revisionKey'},
                      'kind': {'const': 'digest-profile-' + name},
                      'body': closed({'token': text, 'target': closed(target), 'frame': {'$ref': '#/$defs/frame'}}),
                      'owner_review_ref': reference})
        }
        path = directory / (name + '.schema.json')
        save(path, schema)
        schemas.append(binding(path))
    save(HERE / 'candidate-api-contract.json', {
        'schema': 'relational.candidate-profile-selection-api/v1', 'task': 'N01', 'unit': 'K02-profile-selection',
        'status': 'candidate-local-Lean-api', 'schemas': schemas,
        'source_versions': {'declaration': 'cyberalchemy-lab-digest-profile-declaration/candidate-v1',
                            'selection': 'cyberalchemy-lab-digest-profile-selection/candidate-v1'},
        'supported_algorithm': 'sha256-fips1804-2015', 'supported_encoding': 'lowerhex64',
        'functions': [
            {'name': 'prepareSelectedProfile', 'namespace': 'RelationalSuccessor.CandidateProfileSelection',
             'inputs': ['bootstrap: Profile', 'limits: Limits', 'frame: Frame',
                        'declarations: List Envelope', 'selections: List Envelope'],
             'output': 'Option Stage', 'success_meaning': 'SelectedDataMeaning bootstrap limits frame declarations selections stage',
             'failure_meaning': 'No Stage satisfies SelectedDataMeaning; no reason is exposed by this Option result.',
             'effects': 'Pure; retains every source envelope in submitted order. No activation or ownership grant.'},
            {'name': 'selectProfileRows', 'inputs': ['frame: Frame', 'declarations: List Declaration', 'selections: List SelectionRecord'],
             'output': 'Option Profile', 'success_meaning': 'SelectedRowsMeaning',
             'precondition_for_source_claims': 'Typed rows alone do not establish byte capture, digest or authentic ownership.'},
            {'name': 'withSelectedOwnership', 'inputs': ['requirements: EvidenceRequirements', 'bootstrap: Profile',
                        'limits: Limits', 'declarations/selections: List Envelope', 'policies: Policies α'],
             'output': 'Policies α', 'effect': 'Replaces ownedDigestProfile with OwnedProfileMeaning; preserves parses, digest, schema and reviewed predicates.'}
        ],
        'stage_fields': ['frame', 'bootstrap', 'declarations', 'selections', 'profile'],
        'envelope_fields': ['content: List UInt8', 'byteLength: Nat', 'digestProfile: complete RevisionRef', 'digest: String'],
        'evidence_requirements': ['completeAuthenticSnapshot', 'authenticBootstrapSelection', 'issuedDeclaration',
                                  'issuedSelection', 'entitledToDeclare', 'entitledToSelect',
                                  'faithfulDeclarationReviewLifecycle', 'faithfulSelectionReviewLifecycle'],
        'evidence_contract': 'Each requirement is an independent Prop-valued obligation. No authentic provider or approval boolean is supplied. A proof of the complete owned meaning is required for the capture bridge.',
        'source_selection_policy': 'Exact full references and frames; every input is checked; conflicting same-key declarations or selection records refuse. Identical duplicates are retained. No latest/first-wins fallback.',
        'expiry_policy': 'Exclusive boundary: frame.epoch < expiry_epoch, as-of the supplied exact frame.',
        'representation_limits': ['JSON Schema validates decoded values, so it cannot retain duplicate object keys or number lexemes.',
                                  'The exact byte-record decoder must reject duplicate keys and noncanonical Nat spellings before a source claim.',
                                  'This is not an HTTP/OpenAPI endpoint, JSON serialization codec, public diagnostic API, or N03 API freeze.'],
        'profile_selection_data_exact': True, 'ownership_policy_adapter_implemented': True,
        'authentic_evidence_provider_realized': False, 'authenticated_digest_profile_selection_proved': False,
        'authenticated_capture_proved': False, 'JSON_schema_semantics_interpreter_proved': False,
        'N03_API_freeze': False, 'inherited_discharges': 0, 'authority_effect': 'none'
    })
    print({'schemas': len(schemas), 'local_functions': 3, 'authentic_evidence_provider_realized': False})


if __name__ == '__main__':
    run()
