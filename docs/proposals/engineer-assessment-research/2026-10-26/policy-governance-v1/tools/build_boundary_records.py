"""Build source-bound candidate Integration Boundary records and type request."""
from pathlib import Path
import hashlib
import json

from build_integration_records import carrier, obj, strings, write

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'model/integration'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    source = BASE / 'boundaries.json'
    rows = json.loads(source.read_text(encoding='utf-8'))['boundaries']
    assert len(rows) == len({row['id'] for row in rows}) == 6
    text = {'type': 'string', 'minLength': 1}
    props = {
        'schema_version': {'const': 'ea.integration-boundary/v1-candidate'},
        'artifact_type_ref': {'const': 'ea.artifact-type.integration-boundary/v1-candidate'},
        'record_id': text, 'version': text, 'status': {'const': 'candidate-unadmitted'},
        'authority_effect': {'const': 'none'}, 'source_ref': text,
        'source_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
        'source_index': {'type': 'integer', 'minimum': 0},
        'source_excerpt_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
        'slug': text, 'responsibility': text, 'producer': text, 'consumer': text,
        'inputs': text, 'outputs': text, 'data_classification': text, 'purpose': text,
        'interface_contract': text, 'capability_ref': text, 'invariants': strings(1),
        'failure_and_recovery': text, 'source_refs': strings(1),
        'option_review_ref': text, 'verification_contract_ref': text,
        'challenge_contract_ref': text, 'owner_ref': text, 'challenge_route': text,
        'claim_ceiling': text}
    base = ROOT / 'model/carriers/integration-boundary/v1'
    write(base / 'schema.json', {'$schema': 'https://json-schema.org/draft/2020-12/schema', **obj(list(props), props)})
    carrier('integration-boundary', 'ea.integration-boundary',
            'Preserve the stable producer-consumer responsibility, data crossing, interface, invariants and failure behavior independently of option, vendor and release selection.',
            [('cal.artifact-type.schema/v1', 'Schema constrains structural form; the boundary records responsibility, sensitive data flow and behavioral obligations for one product seam.'),
             ('cal.artifact-type.contract/v1', 'The generic Contract records parties and obligations but does not close this producer-consumer interface, custody and failure shape.'),
             ('cal.artifact-type.implementation/v1', 'Implementation records a realized capability; this boundary remains stable across candidate and successor implementations.')])
    refs = []
    for i, row in enumerate(rows):
        record = {k: v for k, v in row.items() if k not in ('id', 'option_review_id', 'verification_contract_id', 'status')}
        record.update(record_id=row['id'], version='0.1.0-candidate.1',
                      schema_version='ea.integration-boundary/v1-candidate',
                      artifact_type_ref='ea.artifact-type.integration-boundary/v1-candidate',
                      status='candidate-unadmitted', authority_effect='none',
                      source_ref='model/integration/boundaries.json', source_sha256=digest(source.read_bytes()),
                      source_index=i, source_excerpt_sha256=digest(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()),
                      option_review_ref=f'model/integration/records/{row["option_review_id"]}/record.json',
                      verification_contract_ref=f'model/integration/records/{row["verification_contract_id"]}/record.json',
                      owner_ref='role:ea-technical-owner-unassigned',
                      challenge_route='role:ea-independent-reviewer-unassigned',
                      claim_ceiling='Candidate boundary specification only; no admitted type, tested interface, selected vendor or active data flow.')
        path = BASE / 'boundaries' / row['id'] / 'record.json'
        write(path, record)
        (path.parent / 'RECORD.md').write_text('# ' + row['id'] + ': ' + row['slug'] + '\n\nCandidate boundary from [boundaries.json](../../boundaries.json). See [record.json](record.json) for its source-bound contract fields. No selected integration or observed flow.\n', encoding='utf-8')
        refs.append(str(path.relative_to(ROOT)))
    write(BASE / 'boundary-index.json', {'schema_version': 'ea.integration-boundary-index/v1',
                                        'status': 'candidate-unadmitted', 'authority_effect': 'none',
                                        'source_ref': 'model/integration/boundaries.json',
                                        'source_sha256': digest(source.read_bytes()),
                                        'count': len(refs), 'record_refs': refs})
    print('Built', len(refs), 'candidate Integration Boundary records and 1 Artifact Type Request')


if __name__ == '__main__':
    main()
