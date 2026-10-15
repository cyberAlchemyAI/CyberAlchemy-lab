"""Proposed, exact representation of legacy owners; grants no runtime rights."""
import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
REGISTRY = 'authority/owners/foundation-01/v1/candidates/0004-craft-identity/owners.json'
DECISION = 'docs/decisions/0029-cml07-semantic-foundation-v1/decision.json'
PRINCIPAL = 'principal:legacy-owner-vrondelli'
PRINCIPAL_REFERENCE = 'principal-reference:legacy-owner-vrondelli'
CEILING = ('Proposed representation of an exact legacy owner row. No admission, '
           'current Role Assignment, owner response, actor authentication or runtime grant.')


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def guard(pin):
    path = HERE / 'source-manifest.json'
    assert sha(path.read_bytes()) == pin, 'unselected owner representation source'
    manifest = json.loads(path.read_bytes())
    assert manifest['authority_effect'] == 'none' and manifest['actual_owner_outcome'] is None
    for row in manifest['files']:
        path = ROOT / row['path']
        assert path.is_file() and not path.is_symlink() and binding(path) == row, row['path']
    return manifest


def inputs():
    registry = json.loads((ROOT / REGISTRY).read_bytes())
    decision = json.loads((ROOT / DECISION).read_bytes())
    postimages = [r for r in decision['canonical_postimages'] if r['path'] == REGISTRY]
    assert postimages == [binding(ROOT / REGISTRY)], 'legacy registry is not the exact D29 postimage'
    assert decision['decision_id'] == 'CAL-DECISION-0029-CML07-SEMANTIC-FOUNDATION-V1'
    assert decision['admission_result']['owner_bindings_admitted'] == 4
    predecessor = registry['predecessor']
    assert binding(ROOT / predecessor['path']) == {k: predecessor[k] for k in ('path', 'sha256')}
    return registry, decision


def propose(registry, decision, proposed_at):
    """New proposed periods are explicit; absent legacy periods stay absent."""
    assert proposed_at.endswith('Z') and len(proposed_at) == 20
    person = registry['principals']
    assert len(person) == 1 and person[0]['principal_id'] == 'person:<vrondelli>'
    assert person[0]['kind'] == 'person-reference'
    rows = registry['role_assignments']
    assert len(rows) == 20
    assert len({r['assignment_id'] for r in rows}) == len(rows)
    assert len({r['role_id'] for r in rows}) == len(rows)
    assert all(r['principal_id'] == person[0]['principal_id'] and r['decision_separation'] == 'required' for r in rows)
    assert all(set(r) == {'assignment_id', 'role_id', 'principal_id', 'scope', 'decision_separation'} for r in rows)
    bodies = []
    scopes = []
    mappings = []
    p = json.loads((ROOT / 'authority/artifact-types/principal/v1/fixtures/valid/record.json').read_bytes())
    p.update(node_id=PRINCIPAL, name='Proposed legacy owner Principal', owner_ref=person[0]['principal_id'],
             scope_ref='protocol:legacy-owner-registry:' + registry['record_id'], lifecycle_state='candidate',
             evidence_refs=[REGISTRY, DECISION], relation_refs=[], successor_refs=[],
             challenge_route='protocol:owner-representation-review', claim_ceiling=CEILING)
    p['payload'].update(principal_kind='human', stable_subject_ref=person[0]['principal_id'], status='proposed',
                        recognition_boundary_refs=['protocol:legacy-owner-recognition:' + registry['record_id']],
                        registry_ref='protocol:legacy-owner-registry:' + registry['record_id'])
    p['relation_refs'] = [{'relation_kind_ref': 'relation.asserts-identity-of', 'direction': 'target',
                           'counterpart_kind': 'principal-reference', 'counterpart_ref': PRINCIPAL_REFERENCE}]
    reference = json.loads((ROOT / 'authority/artifact-types/principal-reference/v1/fixtures/valid/record.json').read_bytes())
    reference.update(node_id=PRINCIPAL_REFERENCE, name='Proposed legacy owner identity reference',
                     owner_ref=person[0]['principal_id'], scope_ref=p['scope_ref'], lifecycle_state='candidate',
                     evidence_refs=[REGISTRY, DECISION], successor_refs=[],
                     challenge_route='protocol:owner-representation-review', claim_ceiling=CEILING)
    reference['payload'].update(principal_ref=PRINCIPAL, principal_kind='human',
                                issuer_ref=p['payload']['registry_ref'], resolution_route='protocol:owner-representation-review',
                                integrity_digest='sha256:' + sha(encoded(p)), privacy_posture='owner-declared-public-repository-identity')
    reference['relation_refs'] = [{'relation_kind_ref': 'relation.asserts-identity-of', 'direction': 'source',
                                  'counterpart_kind': 'principal', 'counterpart_ref': PRINCIPAL}]
    bodies.append(('principal.json', 'principal', p))
    bodies.append(('principal-reference.json', 'principal-reference', reference))
    for index, row in enumerate(rows):
        scope = 'protocol:legacy-owner-scope:' + row['assignment_id']
        basis = 'protocol:proposed-owner-representation:' + row['assignment_id']
        role_id = 'role:' + row['role_id']
        assignment_id = 'role-assignment:legacy:' + row['assignment_id']
        role = {
            'kind': 'role', 'node_id': role_id, 'name': row['role_id'], 'status': 'candidate-unadmitted',
            'lifecycle_state': 'draft', 'scope_ref': scope, 'owner_ref': person[0]['principal_id'],
            'owner_route': 'protocol:owner-representation-review', 'purpose': row['scope'],
            'functions': [row['scope']], 'responsibility_refs': [scope], 'eligible_authority_relation_kinds': [],
            'authority_boundary': 'Exact original scope retained as prose; no permission inferred from this proposed Role.',
            'exclusions': ['No implicit Principal aliases', 'No current assignment or runtime grant', 'No owner response'],
            'challenge_route': 'protocol:owner-representation-review', 'successor_refs': [],
            'authority_effect': 'none', 'claim_ceiling': CEILING,
        }
        assignment = {
            'kind': 'role-assignment', 'node_id': assignment_id, 'status': 'candidate-unadmitted',
            'scope_ref': scope, 'owner_ref': person[0]['principal_id'], 'assignee_kind': 'person-reference',
            'assignee_ref': person[0]['principal_id'], 'role_ref': role_id, 'assignment_basis_ref': basis,
            'assignment_state': 'proposed', 'period': {'start': proposed_at, 'end': None},
            'responsibility_refs': [scope], 'authority_claim_refs': [],
            'owner_route': 'protocol:owner-representation-review', 'challenge_route': 'protocol:owner-representation-review',
            'successor_refs': [], 'authority_effect': 'none', 'claim_ceiling': CEILING,
        }
        prefix = f'{index + 1:02d}-' + row['role_id']
        bodies += [(prefix + '-role.json', 'role', role), (prefix + '-assignment.json', 'role-assignment', assignment)]
        scopes.append({'reference': scope, 'reference_class': 'protocol-scope-reference', 'original_scope_prose': row['scope'],
                       'source_selector': f'/role_assignments/{index}/scope', 'source_binding': binding(ROOT / REGISTRY),
                       'recognition_reference': p['payload']['recognition_boundary_refs'][0],
                       'registry_reference': p['payload']['registry_ref'], 'proposal_basis_reference': basis,
                       'proposal_basis_class': 'candidate-representation-proposal', 'authority_effect': 'none'})
        mappings.append({'source_selector': f'/role_assignments/{index}', 'original_row': copy.deepcopy(row),
                         'source_binding': binding(ROOT / REGISTRY), 'role_identity_mapping': {'from': row['role_id'], 'to': role_id},
                         'assignment_identity_mapping': {'from': row['assignment_id'], 'to': assignment_id},
                         'assignee_stable_subject_ref': row['principal_id'], 'proposed_principal_ref': PRINCIPAL,
                         'role_file': prefix + '-role.json', 'assignment_file': prefix + '-assignment.json',
                         'legacy_period': None, 'legacy_period_present': False,
                         'proposed_period_basis': 'New proposed representation timestamp; not a historical assignment date',
                         'decision_separation': 'required', 'current_assignment_established': False})
    plan = {'schema_version': 'lab-owner-representation-proposal/v1-candidate', 'authority_effect': 'none',
            'actual_owner_outcome': None, 'source_registry_binding': binding(ROOT / REGISTRY),
            'source_decision_binding': binding(ROOT / DECISION), 'legacy_decision_ref': decision['decision_id'],
            'legacy_scope_interpreted_as_runtime_permission': False, 'legacy_assignments_modified': False,
            'principal_identity_mapping': {'legacy_stable_subject_ref': person[0]['principal_id'], 'proposed_principal_ref': PRINCIPAL,
                                           'identity_assurance': person[0]['identity_assurance'], 'authentication_verified': False},
            'automatic_principal_aliases': [], 'source_runtime_role_assignments': 0, 'proposed_at': proposed_at,
            'proposed_roles': 20, 'proposed_role_assignments': 20, 'proposed_principals': 1, 'proposed_principal_references': 1,
            'mappings': mappings, 'protocol_scopes': scopes, 'required_governing_role_coverage_verified': False,
            'public_review_adapter_implemented': False, 'task_complete': False, 'claim_ceiling': CEILING}
    validate(bodies, plan)
    return bodies, plan


def validate(bodies, plan):
    assert len(bodies) == 42 and len({b['node_id'] for _, _, b in bodies}) == 42
    for filename, kind, body in bodies:
        assert Path(filename).name == filename and body['kind'] == kind and body['authority_effect'] == 'none'
        schema = json.loads((ROOT / f'authority/artifact-types/{kind}/v1/schema.json').read_bytes())
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(body)
    assert len(plan['mappings']) == len(plan['protocol_scopes']) == 20
    assert not plan['automatic_principal_aliases'] and not plan['legacy_scope_interpreted_as_runtime_permission']


def write_package(output, bodies, plan):
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    targets = []
    for filename, kind, body in bodies:
        raw = encoded(body)
        with (output / filename).open('xb') as f:
            f.write(raw)
        schema = ROOT / f'authority/artifact-types/{kind}/v1/schema.json'
        targets.append({'filename': filename, 'identity_ref': body['node_id'], 'carrier_ref': f'cal.artifact-type.{kind}/v1',
                        'byte_sha256': sha(raw), 'schema_binding': binding(schema), 'admission_state': 'candidate-unadmitted',
                        'proposed_effect': 'Admit exact new representation only after its own final review member succeeds',
                        'independent_decision_core_prepared': False})
    plan = {**plan, 'exact_targets': targets}
    with (output / 'proposal.json').open('xb') as f:
        f.write(encoded(plan))
    return plan
