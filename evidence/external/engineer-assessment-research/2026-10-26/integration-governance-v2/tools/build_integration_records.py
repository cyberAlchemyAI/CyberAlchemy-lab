"""Build source-bound candidate integration reviews and verification contracts."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'CyberAlchemy-lab'
BASE = ROOT / 'model/integration'
REGISTRY = LAB / 'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'
REQUEST_SCHEMA = LAB / 'authority/artifact-types/artifact-type-request/v1/schema.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def strings(min_items=0):
    return {'type': 'array', 'items': {'type': 'string', 'minLength': 1}, 'minItems': min_items}


def obj(required, properties):
    return {'type': 'object', 'additionalProperties': False, 'required': required, 'properties': properties}


def carrier(family, definition_id, purpose, alternatives):
    c = ROOT / 'model/carriers' / family / 'v1'
    schema_ref = str((c / 'schema.json').relative_to(ROOT))
    registry_ref = str(REGISTRY.relative_to(LAB)) + '#sha256=' + sha(REGISTRY.read_bytes())
    definition_ref = f'{definition_id}@0.1.0-candidate.1'
    request = {
        'schema_version': 'cyberalchemy-lab-artifact-type-request/v1',
        'request_id': f'EA-ATR-{family.upper().replace("-", "-")}-001',
        'version': '0.1.0-candidate.1', 'status': 'candidate-unadmitted',
        'authority_effect': 'none', 'owner_ref': 'role:ea-artifact-type-owner-unassigned',
        'proposed_semantic_kind': family, 'proposed_package_home_ref': str(c.relative_to(ROOT)),
        'resolution_evidence': {'registry_ref': registry_ref, 'matches': []},
        'compatibility_analysis': [{'existing_type_ref': x, 'rejection_reason': why} for x, why in alternatives],
        'semantic_definition_refs': [definition_ref],
        'representation_proposal': {'canonical_filename': 'record.json', 'human_filename': 'RECORD.md', 'projection_policy': 'generated-only'},
        'validation_purpose': purpose, 'consumed_as_subject': False,
        'expiry': {'condition': 'Resolved, rejected or superseded by exact Artifact Type owner review.', 'superseded_by': None},
        'source_direction': {'canonical': 'request.json', 'human_projection': 'REQUEST.md', 'projection_policy': 'generated-only', 'generator_ref': 'cal.generator.artifact-surface/v1'},
        'claim_ceiling': 'Candidate request only; no Lab type admission, implementation choice, participant collection or release.'
    }
    write(c / 'request.json', request)
    (c / 'REQUEST.md').write_text('# ' + family.replace('-', ' ').title() + ' request\n\nGenerated from [request.json](request.json). Candidate only; no authority effect.\n', encoding='utf-8')
    definition_path = ROOT / 'model/definition-records' / definition_id.removeprefix('ea.') / 'definition.json'
    descriptor = {
        'schema_version': 'ea.artifact-type-candidate/v1',
        'artifact_type_ref': f'ea.artifact-type.{family}/v1-candidate',
        'semantic_definition_ref': definition_ref,
        'semantic_definition_sha256': sha(definition_path.read_bytes()),
        'status': 'candidate-unadmitted', 'authority_effect': 'none',
        'owner_ref': 'role:ea-artifact-type-owner-unassigned',
        'request_ref': str((c / 'request.json').relative_to(ROOT)),
        'instance_contract': {'canonical_filename': 'record.json', 'human_filename': 'RECORD.md', 'identity_field': 'record_id', 'schema_ref': schema_ref, 'schema_sha256': sha((c / 'schema.json').read_bytes()), 'closed_representation': True},
        'distinct_validation_purpose': purpose,
        'lab_v3_conformance': 'not-claimed; semantic and type-owner admission bindings pending',
        'claim_ceiling': 'Candidate local carrier only; no selected implementation, Lab type admission or verified run.'
    }
    write(c / 'artifact.json', descriptor)
    return c


def main():
    choices = json.loads((BASE / 'choices.json').read_text(encoding='utf-8'))['choices']
    contracts = json.loads((BASE / 'contracts.json').read_text(encoding='utf-8'))['contracts']
    assert len(choices) == len(contracts) == 6
    ids = {x['id'] for x in choices}
    assert ids == {x['option_review_id'] for x in contracts}
    assert {x['contract_id'] for x in choices} == {x['id'] for x in contracts}
    text = {'type': 'string', 'minLength': 1}
    option = obj(['id', 'name', 'why', 'benefits', 'tradeoffs', 'failure_modes', 'source_refs', 'dependencies', 'evidence_maturity', 'disposition'], {
        'id': text, 'name': text, 'why': text, 'benefits': strings(1), 'tradeoffs': strings(1),
        'failure_modes': strings(1), 'source_refs': strings(1), 'dependencies': strings(1),
        'evidence_maturity': text, 'disposition': text})
    check = obj(['id', 'stimulus', 'acceptance'], {'id': text, 'stimulus': text, 'acceptance': text})
    common = {'record_id': text, 'version': text, 'status': {'const': 'candidate-unadmitted'},
              'authority_effect': {'const': 'none'}, 'source_ref': text,
              'source_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
              'source_index': {'type': 'integer', 'minimum': 0},
              'source_excerpt_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
              'owner_ref': text, 'challenge_route': text, 'claim_ceiling': text}
    review_props = dict(common, **{
        'schema_version': {'const': 'ea.integration-option-review/v1-candidate'},
        'artifact_type_ref': {'const': 'ea.artifact-type.integration-option-review/v1-candidate'},
        'boundary': text, 'problem': text, 'requirement_refs': strings(1),
        'options': {'type': 'array', 'items': option, 'minItems': 2},
        'provisional_preference': text, 'rationale': text, 'unresolved_assumptions': strings(1),
        'decision_constraints': strings(1), 'revisit_triggers': strings(1),
        'rejected_alternatives': strings(),
        'verification_contract_ref': text, 'owner_decision_ref': {'type': 'null'}})
    contract_props = dict(common, **{
        'schema_version': {'const': 'ea.integration-verification-contract/v1-candidate'},
        'artifact_type_ref': {'const': 'ea.artifact-type.integration-verification-contract/v1-candidate'},
        'option_review_ref': text, 'objective': text, 'environment': text,
        'checks': {'type': 'array', 'items': check, 'minItems': 1},
        'failure_route': text, 'evidence_requirements': strings(1),
        'rejection_gates': strings(1), 'threshold_registration': text,
        'run_refs': {'type': 'array', 'maxItems': 0},
        'result_refs': {'type': 'array', 'maxItems': 0}})
    review_carrier = ROOT / 'model/carriers/integration-option-review/v1'
    contract_carrier = ROOT / 'model/carriers/integration-verification-contract/v1'
    write(review_carrier / 'schema.json', {'$schema': 'https://json-schema.org/draft/2020-12/schema', **obj(list(review_props), review_props)})
    write(contract_carrier / 'schema.json', {'$schema': 'https://json-schema.org/draft/2020-12/schema', **obj(list(contract_props), contract_props)})
    carrier('integration-option-review', 'ea.integration-option-review',
            'Preserve one integration boundary’s alternatives, why, trade-offs, failure modes, source evidence and provisional preference before any owner choice.',
            [('cal.artifact-type.decision/v1', 'A Decision is an attributable authority selection; these are pre-decision option comparisons with no selected effect.'),
             ('cal.artifact-type.evaluation/v1', 'Evaluation records check outcomes against a profile; this review retains competing options and untested assumptions before a run.')])
    carrier('integration-verification-contract', 'ea.integration-verification-contract',
            'Specify one integration option review’s executable checks, acceptance gates, failure route and evidence needed before selection.',
            [('cal.artifact-type.contract/v1', 'The generic Contract carrier preserves obligation references but not closed test stimulus, environment and acceptance checks for one integration boundary.'),
             ('cal.artifact-type.challenge-contract/v1', 'Challenge Contract governs contesting subjects, challengers and resolution; it is not a technical spike or acceptance test contract.'),
             ('cal.artifact-type.experiment-design/v1', 'Experiment Design is for a research study; the immediate synthetic engineering spike does not itself recruit participants or test a scientific claim.')])
    refs = []
    for family, rows, source in [('integration-option-review', choices, BASE / 'choices.json'),
                                 ('integration-verification-contract', contracts, BASE / 'contracts.json')]:
        source_ref = str(source.relative_to(ROOT)); source_hash = sha(source.read_bytes())
        for i, row in enumerate(rows):
            rid = row['id']; path = BASE / 'records' / rid / 'record.json'
            shared = {'record_id': rid, 'version': '0.1.0-candidate.1', 'status': 'candidate-unadmitted',
                      'authority_effect': 'none', 'source_ref': source_ref, 'source_sha256': source_hash,
                      'source_index': i, 'source_excerpt_sha256': sha(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()),
                      'owner_ref': 'role:ea-technical-owner-unassigned',
                      'challenge_route': row.get('challenge_route', 'role:ea-independent-reviewer-unassigned'),
                      'claim_ceiling': 'Candidate design record only; no executed check, selected integration, participant-data permission or release.'}
            if family == 'integration-option-review':
                record = dict(shared, schema_version='ea.integration-option-review/v1-candidate',
                              artifact_type_ref='ea.artifact-type.integration-option-review/v1-candidate',
                              boundary=row['boundary'], problem=row['problem'], requirement_refs=row['requirement_refs'],
                              options=row['options'], provisional_preference=row['provisional_preference'],
                              rationale=row['rationale'], unresolved_assumptions=row['unresolved_assumptions'],
                              decision_constraints=row['decision_constraints'], revisit_triggers=row['revisit_triggers'],
                              rejected_alternatives=row['rejected_alternatives'],
                              verification_contract_ref=f'model/integration/records/{row["contract_id"]}/record.json',
                              owner_decision_ref=None)
            else:
                record = dict(shared, schema_version='ea.integration-verification-contract/v1-candidate',
                              artifact_type_ref='ea.artifact-type.integration-verification-contract/v1-candidate',
                              option_review_ref=f'model/integration/records/{row["option_review_id"]}/record.json',
                              objective=row['objective'], environment=row['environment'], checks=row['checks'],
                              failure_route=row['failure_route'], evidence_requirements=row['evidence_requirements'],
                              rejection_gates=row['rejection_gates'], threshold_registration=row['threshold_registration'],
                              run_refs=[], result_refs=[])
            write(path, record)
            (path.parent / 'RECORD.md').write_text('# ' + rid + '\n\nGenerated candidate record from [' + source.name + '](../../' + source.name + '). See [record.json](record.json) for the closed fields. No owner Decision or test run exists.\n', encoding='utf-8')
            refs.append(str(path.relative_to(ROOT)))
    write(BASE / 'index.json', {'schema_version': 'ea.integration-record-index/v1', 'status': 'candidate-unadmitted',
                                'authority_effect': 'none', 'count': len(refs), 'record_refs': refs,
                                'source_refs': ['model/integration/choices.json', 'model/integration/contracts.json']})
    print('Built', len(refs), 'candidate integration records and 2 Artifact Type Requests')


if __name__ == '__main__':
    main()
