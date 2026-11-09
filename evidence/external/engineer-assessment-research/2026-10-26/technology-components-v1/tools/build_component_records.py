"""Build candidate technology identities and empty integration-binding carrier."""
from pathlib import Path
import hashlib
import json

from build_integration_records import carrier, obj, strings, write

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'model/integration'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    source = BASE / 'components.json'
    rows = json.loads(source.read_text(encoding='utf-8'))['components']
    assert len(rows) == 24 and len({x['id'] for x in rows}) == 24
    text = {'type': 'string', 'minLength': 1}
    maybe = {'type': ['string', 'null']}
    common = {'record_id': text, 'version': text, 'status': {'const': 'candidate-unadmitted'},
              'authority_effect': {'const': 'none'}, 'source_ref': text,
              'source_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
              'source_index': {'type': 'integer', 'minimum': 0},
              'source_excerpt_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
              'owner_ref': text, 'challenge_route': text, 'claim_ceiling': text}
    component_props = dict(common, **{
        'schema_version': {'const': 'ea.technology-component/v1-candidate'},
        'artifact_type_ref': {'const': 'ea.artifact-type.technology-component/v1-candidate'},
        'name': text, 'component_kind': text, 'boundary_refs': strings(),
        'source_refs': strings(1), 'selection_posture': {'const': 'candidate-only'},
        'version_pin': {'type': 'null'}, 'license_or_terms_ref': {'type': 'null'},
        'publisher_or_maintainer_ref': {'type': 'null'}, 'upstream_identity_ref': {'type': 'null'},
        'lifecycle_status': {'const': 'unverified'},
        'legal_processor_ref': {'type': 'null'}, 'operating_owner_ref': {'type': 'null'},
        'data_exposure': text, 'unresolved': strings(1)})
    binding_props = {
        'schema_version': {'const': 'ea.integration-binding/v1-candidate'},
        'artifact_type_ref': {'const': 'ea.artifact-type.integration-binding/v1-candidate'},
        'record_id': text, 'version': text, 'status': {'enum': ['candidate-unadmitted', 'selected-pending-activation', 'active', 'retired']},
        'authority_effect': {'const': 'none'}, 'boundary_ref': text, 'environment_ref': text,
        'component_refs': strings(1), 'version_pins': {'type': 'object', 'additionalProperties': text},
        'configuration_digest': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
        'adapter_contract_ref': text, 'data_route_ref': text, 'owner_decision_ref': text,
        'verification_result_refs': strings(1), 'privacy_approval_ref': text,
        'operating_owner_ref': text, 'rollback_ref': text, 'release_ref': text,
        'challenge_route': text, 'claim_ceiling': text}
    for family, props in [('technology-component', component_props), ('integration-binding', binding_props)]:
        write(ROOT / 'model/carriers' / family / 'v1/schema.json',
              {'$schema': 'https://json-schema.org/draft/2020-12/schema', **obj(list(props), props)})
    carrier('technology-component', 'ea.technology-component',
            'Track one named external service, library, SDK, browser capability or tool with identity, selection posture, version, terms, data exposure and open review.',
            [('cal.artifact-type.tool/v1', 'Tool is an invocable Lab Agent Action resource with a versioned input/output contract; a browser API, SDK or managed processor candidate is not necessarily that Agent Tool.'),
             ('cal.artifact-type.implementation/v1', 'Implementation records a realized capability and execution entrypoint; a shortlist component can exist before any build or selection.')])
    carrier('integration-binding', 'ea.integration-binding',
            'Pin an owner-selected integration to exact component versions, configuration, environment, data route, verification, approval and rollback for one release.',
            [('cal.artifact-type.implementation/v1', 'Lab Implementation/v1 relates a realized capability to schemas and entrypoints but does not close dependency versions, processor route, release, approval and rollback as one product deployment binding.'),
             ('cal.artifact-type.decision/v2', 'Decision selects with authority; this carrier records the exact resulting deployment binding and its lifecycle.')])
    refs = []
    for i, row in enumerate(rows):
        record = dict(row, record_id=row['id'], version='0.1.0-candidate.1',
                      schema_version='ea.technology-component/v1-candidate',
                      artifact_type_ref='ea.artifact-type.technology-component/v1-candidate',
                      status='candidate-unadmitted', authority_effect='none',
                      source_ref='model/integration/components.json', source_sha256=digest(source.read_bytes()),
                      source_index=i, source_excerpt_sha256=digest(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()),
                      owner_ref='role:ea-technical-owner-unassigned',
                      challenge_route='role:ea-independent-reviewer-unassigned',
                      claim_ceiling='Candidate technology identity only; no version selected, license cleared, processor approved, package installed or binding deployed.')
        record.pop('id')
        path = BASE / 'components' / row['id'] / 'record.json'
        write(path, record)
        (path.parent / 'RECORD.md').write_text('# ' + row['name'] + '\n\nCandidate component from [components.json](../../components.json). See [record.json](record.json) for source-pinned fields. No selected version or deployment.\n', encoding='utf-8')
        refs.append(str(path.relative_to(ROOT)))
    write(BASE / 'component-index.json', {'schema_version': 'ea.technology-component-index/v1',
                                         'status': 'candidate-unadmitted', 'authority_effect': 'none',
                                         'source_ref': 'model/integration/components.json',
                                         'source_sha256': digest(source.read_bytes()),
                                         'count': len(refs), 'record_refs': refs,
                                         'binding_refs': []})
    print('Built', len(refs), 'candidate component records and 2 Artifact Type Requests; no binding instance')


if __name__ == '__main__':
    main()
