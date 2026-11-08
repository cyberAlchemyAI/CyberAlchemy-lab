"""Build candidate policy clauses, one retention schedule and Lab Policy/v2 records."""
from pathlib import Path
import hashlib
import json

from build_integration_records import carrier, obj, strings, write

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent / 'CyberAlchemy-lab'
BASE = ROOT / 'model/policies'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    clause_source = BASE / 'clauses.json'
    policy_source = BASE / 'policy-set.json'
    retention_source = BASE / 'retention-source.json'
    assistance_source = BASE / 'assistance-source.json'
    clauses = json.loads(clause_source.read_text(encoding='utf-8'))['clauses']
    policies = json.loads(policy_source.read_text(encoding='utf-8'))['policies']
    retention = json.loads(retention_source.read_text(encoding='utf-8'))
    assistance = json.loads(assistance_source.read_text(encoding='utf-8'))
    assert len(clauses) == 46 and len(policies) == 14 and len(retention['entries']) == 10 and len(assistance['rows']) == 24
    text = {'type': 'string', 'minLength': 1}
    common = {'record_id': text, 'version': text, 'status': {'const': 'candidate-unadmitted'},
              'authority_effect': {'const': 'none'}, 'source_ref': text,
              'source_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
              'source_index': {'type': 'integer', 'minimum': 0},
              'source_excerpt_sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'},
              'owner_ref': text, 'challenge_route': text, 'claim_ceiling': text}
    clause_props = dict(common, **{
        'schema_version': {'const': 'ea.policy-clause/v1-candidate'},
        'artifact_type_ref': {'const': 'ea.artifact-type.policy-clause/v1-candidate'},
        'policy_ref': text, 'condition': text,
        'effect': {'enum': ['require', 'prohibit', 'permit', 'hold']},
        'statement': text, 'enforcement_point': text, 'required_evidence': text,
        'exception_route': text, 'owner_role': text, 'source_refs': strings(1),
        'open_parameters': strings()})
    entry = obj(['id', 'data_class', 'purpose', 'start_trigger', 'duration_value', 'duration_unit',
                 'deletion_route', 'derivative_lineage', 'exception_route', 'owner_role', 'source_refs', 'status'], {
        'id': text, 'data_class': text, 'purpose': text, 'start_trigger': text,
        'duration_value': {'type': 'null'}, 'duration_unit': {'type': 'null'},
        'deletion_route': text, 'derivative_lineage': text, 'exception_route': text,
        'owner_role': text, 'source_refs': strings(1), 'status': {'const': 'candidate-unapproved'}})
    retention_props = dict(common, **{
        'schema_version': {'const': 'ea.retention-schedule/v1-candidate'},
        'artifact_type_ref': {'const': 'ea.artifact-type.retention-schedule/v1-candidate'},
        'policy_ref': text, 'jurisdiction': {'type': 'null'},
        'controller_ref': {'type': 'null'}, 'approval_ref': {'type': 'null'},
        'entries': {'type': 'array', 'items': entry, 'minItems': 1}})
    assistance_row = obj(['id', 'session', 'resource', 'phase', 'baseline_state', 'reason',
                          'research_override', 'violation_handling', 'accessibility_protection'], {
        'id': text, 'session': {'type': 'integer', 'minimum': 1, 'maximum': 3},
        'resource': text, 'phase': {'enum': ['before-case', 'timed-answer']},
        'baseline_state': {'enum': ['candidate-permit', 'candidate-prohibit']},
        'reason': text, 'research_override': {'type': ['string', 'null']},
        'violation_handling': text, 'accessibility_protection': {'type': 'boolean'}})
    assistance_props = dict(common, **{
        'schema_version': {'const': 'ea.assistance-matrix/v1-candidate'},
        'artifact_type_ref': {'const': 'ea.artifact-type.assistance-matrix/v1-candidate'},
        'policy_ref': text, 'administration_policy_ref': text,
        'notice_requirement': text, 'pre_exposure_note': text,
        'rows': {'type': 'array', 'items': assistance_row, 'minItems': 1},
        'owner_role': text, 'approval_ref': {'type': 'null'}})
    for family, props in [('policy-clause', clause_props), ('retention-schedule', retention_props),
                          ('assistance-matrix', assistance_props)]:
        write(ROOT / 'model/carriers' / family / 'v1/schema.json',
              {'$schema': 'https://json-schema.org/draft/2020-12/schema', **obj(list(props), props)})
    carrier('policy-clause', 'ea.policy-clause',
            'Carry one source-bound normative product rule with condition, required/prohibited action, evidence, enforcement, exception, owner and open parameters.',
            [('cal.artifact-type.policy/v2', 'Policy/v2 carries the versioned policy and rule references; this record is one inspectable rule, not the issuing policy.'),
             ('ea.artifact-type.recovery-rule/v1-candidate', 'A Recovery Rule governs a specific session failure; general research, privacy, scoring and assistance clauses need wider scope.')])
    carrier('retention-schedule', 'ea.retention-schedule',
            'Carry one data-class and purpose retention matrix with start trigger, duration, lineage, deletion route and exceptions before collection.',
            [('cal.artifact-type.policy/v2', 'Policy/v2 can issue the retention obligation but its generic rule references do not close the per-data-class clock, derivative and deletion matrix.'),
             ('ea.artifact-type.policy-clause/v1-candidate', 'One clause cannot represent the full data-class schedule and shared controller/jurisdiction decision.')])
    carrier('assistance-matrix', 'ea.assistance-matrix',
            'Carry participant-visible per-session preparation and timed-answer tool/help allowances with research-arm and accessibility distinctions.',
            [('cal.artifact-type.policy/v2', 'Policy/v2 carries issued rule references, but the participant-facing per-session and per-resource allowance matrix needs a closed operational representation.'),
             ('ea.artifact-type.administration-policy/v1-candidate', 'Administration Policy covers timing, reveals and recovery; this matrix pins the exact help-resource allowances and disclosure shown to participants.')])
    clause_refs = []
    for i, row in enumerate(clauses):
        record = {k: v for k, v in row.items() if k not in ('id', 'policy_id', 'status')}
        record.update(record_id=row['id'], version='0.1.0-candidate.1',
                      schema_version='ea.policy-clause/v1-candidate',
                      artifact_type_ref='ea.artifact-type.policy-clause/v1-candidate',
                      status='candidate-unadmitted', authority_effect='none',
                      source_ref='model/policies/clauses.json', source_sha256=digest(clause_source.read_bytes()),
                      source_index=i, source_excerpt_sha256=digest(json.dumps(row, ensure_ascii=False, sort_keys=True).encode()),
                      policy_ref=f'model/policies/records/{row["policy_id"]}/policy.json',
                      owner_ref='role:ea-' + row['owner_role'].replace('_', '-') + '-unassigned',
                      challenge_route='role:ea-independent-reviewer-unassigned',
                      claim_ceiling='Candidate policy clause only; no issued policy, operational enforcement, approval or compliance result.')
        path = BASE / 'clauses' / row['id'] / 'record.json'
        write(path, record)
        (path.parent / 'RECORD.md').write_text('# ' + row['id'] + '\n\nSource-bound candidate clause from [clauses.json](../../clauses.json). See [record.json](record.json). No policy effect.\n', encoding='utf-8')
        clause_refs.append(str(path.relative_to(ROOT)))
    retention_record = {k: v for k, v in retention.items() if k not in ('schema_version', 'schedule_id', 'status', 'authority_effect', 'policy_id')}
    retention_record.update(record_id=retention['schedule_id'], version='0.1.0-candidate.1',
                            schema_version='ea.retention-schedule/v1-candidate',
                            artifact_type_ref='ea.artifact-type.retention-schedule/v1-candidate',
                            status='candidate-unadmitted', authority_effect='none',
                            source_ref='model/policies/retention-source.json',
                            source_sha256=digest(retention_source.read_bytes()), source_index=0,
                            source_excerpt_sha256=digest(json.dumps(retention, ensure_ascii=False, sort_keys=True).encode()),
                            policy_ref='model/policies/records/POL-02/policy.json',
                            owner_ref='role:ea-privacy-owner-unassigned',
                            challenge_route='role:ea-independent-reviewer-unassigned',
                            claim_ceiling='Draft schedule with all durations, jurisdiction and controller unresolved; no participant-data retention authorization or deletion result.')
    retention_path = BASE / 'retention-schedule.json'
    write(retention_path, retention_record)
    assistance_record = {k: v for k, v in assistance.items() if k not in ('schema_version', 'matrix_id', 'status', 'authority_effect', 'policy_id')}
    assistance_record.update(record_id=assistance['matrix_id'], version='0.1.0-candidate.1',
                             schema_version='ea.assistance-matrix/v1-candidate',
                             artifact_type_ref='ea.artifact-type.assistance-matrix/v1-candidate',
                             status='candidate-unadmitted', authority_effect='none',
                             source_ref='model/policies/assistance-source.json',
                             source_sha256=digest(assistance_source.read_bytes()), source_index=0,
                             source_excerpt_sha256=digest(json.dumps(assistance, ensure_ascii=False, sort_keys=True).encode()),
                             policy_ref='model/policies/records/POL-03/policy.json',
                             owner_ref='role:ea-assessment-owner-unassigned',
                             challenge_route='role:ea-independent-reviewer-unassigned',
                             claim_ceiling='Participant-facing draft matrix only; no issued allowance, monitored participant or assistance finding.')
    assistance_path = BASE / 'assistance-matrix.json'
    write(assistance_path, assistance_record)
    policy_refs = []
    for i, row in enumerate(policies):
        path = BASE / 'records' / row['id'] / 'policy.json'
        ref = str(path.relative_to(ROOT))
        record = {
            'schema_version': 'cyberalchemy-lab-policy/v2',
            'node_id': 'policy:ea:' + row['id'].lower(), 'kind': 'policy',
            'name': row['title'], 'lifecycle_state': 'candidate', 'authority_effect': 'none',
            'owner_ref': 'role:ea-' + row['owner_role'].replace('_', '-') + '-unassigned',
            'scope_ref': 'scope:ea-product-research-candidate', 'evidence_refs': [],
            'challenge_route': 'role:ea-independent-reviewer-unassigned', 'successor_refs': [],
            'relation_refs': [{'relation_kind_ref': 'relation.governed-by', 'direction': 'source',
                               'counterpart_kind': 'context', 'counterpart_ref': 'model/AUTHORITY.md'}],
            'payload': {'issuer_ref': 'role:ea-' + row['owner_role'].replace('_', '-') + '-unassigned',
                        'governed_scope_ref': row['scope'],
                        'rule_refs': [f'model/policies/clauses/{rid}/record.json' for rid in row['clause_ids']],
                        'exception_route': row['exception_route'],
                        'effective_period': row['effective_period']},
            'claim_ceiling': 'Candidate Lab Policy/v2 shape only; owner, jurisdiction, values and issue Decision remain open. No active operational rule.'}
        write(path, record)
        (path.parent / 'POLICY.md').write_text('# ' + row['title'] + '\n\nCandidate Lab Policy/v2 from [policy-set.json](../../policy-set.json). See [policy.json](policy.json) and its rule refs. No issued effect.\n', encoding='utf-8')
        policy_refs.append(ref)
    write(BASE / 'index.json', {'schema_version': 'ea.policy-record-index/v1',
                               'status': 'candidate-unissued', 'authority_effect': 'none',
                               'clause_source_ref': 'model/policies/clauses.json',
                               'clause_source_sha256': digest(clause_source.read_bytes()),
                               'policy_source_ref': 'model/policies/policy-set.json',
                               'policy_source_sha256': digest(policy_source.read_bytes()),
                               'retention_source_ref': 'model/policies/retention-source.json',
                               'retention_source_sha256': digest(retention_source.read_bytes()),
                               'assistance_source_ref': 'model/policies/assistance-source.json',
                               'assistance_source_sha256': digest(assistance_source.read_bytes()),
                               'clause_count': len(clause_refs), 'clause_refs': clause_refs,
                               'policy_count': len(policy_refs), 'policy_refs': policy_refs,
                               'retention_ref': str(retention_path.relative_to(ROOT)),
                               'assistance_ref': str(assistance_path.relative_to(ROOT))})
    print('Built', len(policy_refs), 'Lab Policy/v2 candidates,', len(clause_refs), 'clauses, one retention schedule and one assistance matrix')


if __name__ == '__main__':
    main()
