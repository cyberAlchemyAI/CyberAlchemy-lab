"""Real controlled retained-builder episode and separately scoped test-only Decision."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence.service import *
from failures.service import FailureService
from challenges.service import ChallengeService, ControlledGate


def declarations(e, challenge):
    """Host fixture owner creates exact local gate outside challenge request bytes."""
    c = challenge.current_ref
    effect = e.put(e.make('effect', 'contest-disposition', {'effect_kind': 'challenge-disposition',
        'subject_ref': c, 'intended_state': 'resolved-for-revision', 'effective_when': 'exact-current-W05-controlled-host-gate',
        'verification_refs': [challenge.response_ref, e.subject_ref]}))
    scope = e.put(e.make('decision-scope', 'contest-only', {'subject_kind_refs': ['challenge-event'], 'subject_refs': [c],
        'permitted_effects': ['challenge-disposition'],
        'excluded_effects': ['challenged-subject-mutation', 'canonical-admission', 'live-activation']}))
    boundary = e.put(e.make('authority-claim', 'controlled-contest-claim', {
        'authority_basis_refs': [e.host.grant.evidence_ref], 'claimant_ref': e.host.ref('principal'),
        'claimed_permissions': ['challenge-disposition'], 'decision_scope_ref': scope,
        'limitations': ['fixture-only', 'no-challenged-subject-mutation', 'no-canonical-admission', 'no-live-activation']}))
    e.edge('claim-scope', 'relation.scopes-authority-over', boundary, scope,
        {'authority_role': 'controlled-fixture-contest-only', 'scope_ref': scope})
    decision = e.put(e.make('decision', 'local-fixture-disposition', {'decision_maker_ref': e.host.ref('principal'),
        'subject_refs': [c], 'selected_outcome': 'fixture-accept-contest-for-revision',
        'evidence_basis_refs': [challenge.response_ref], 'declared_effect_refs': [effect]}))
    e.edge('decision-effect', 'relation.declares-effect-on', decision, effect,
        {'effect_kind': 'challenge-disposition', 'exact_target_version_ref': effect})
    original = encoded({'fixture_only': True, 'actual_owner_outcome': None, 'challenge_ref': c,
        'subject_ref': e.subject_ref, 'decision_ref': decision, 'effect_ref': effect, 'decision_scope_ref': scope,
        'claim_ref': boundary,
        'response_ref': challenge.response_ref, 'fixture_outcome': 'fixture-accept-contest-for-revision'})
    e.blob('host-fixture-gate.json', original)
    e.host.fixture_gate = ControlledGate('protocol:W05-exact-fixture-gate@1', e.host.session.session_ref,
        e.host.status['head'], SCOPE, c, e.records[c][1], e.subject_ref, e.records[e.subject_ref][1],
        decision, e.records[decision][1], effect, e.records[effect][1], scope, e.records[scope][1], boundary, e.records[boundary][1],
        e.host.now[0]+120, 'fixture-accept-contest-for-revision', original, byte_sha(original))
    return decision, effect, scope


def prepare_episode(output, *, finish=True):
    f = host_fixture()
    e = EvidenceService(output, f)
    manifest = e.observe()
    failures = FailureService(e)
    refs, edges = failures.materialize(manifest)
    contract = e.put(e.make('challenge-contract', 'controlled-builder-contest', {
        'policy_ref': 'protocol:W05-controlled-contest-policy@1', 'challengeable_subject_kinds': ['implementation'],
        'eligible_challenger_kinds': ['principal'], 'grounds': ['schema-contract-conflict'],
        'required_evidence_kinds': ['evidence-set'], 'response_modes': ['evidence', 'owner-review'],
        'owner_route': 'protocol:W05-fixture-principal-route', 'resolution_gate_ref': 'protocol:W05-exact-fixture-gate@1',
        'response_period': 'protocol:W05-300-second-response@1', 'unresolved_residue_route': 'protocol:W05-old-revision-review-pending'}))
    refs['challenge_contract'] = contract
    f.fixture_gate = None
    c = ChallengeService(e, contract, gate_reader=lambda: f.fixture_gate)
    submitted = c.submit(refs['historical'], f.ref('principal'), 'schema-contract-conflict', [refs['evidence']])
    refs['challenge_submitted'] = submitted
    edges.append(e.edge('contest-subject', 'relation.challenges', submitted, refs['historical'],
        {'challenge_contract_ref': contract, 'challenge_mode': 'schema-contract-conflict', 'challenged_version_ref': refs['historical']}))
    edges.append(e.edge('contest-contract', 'relation.governed-by', submitted, contract, {'governance_role': 'exact-contest-contract'}))
    c.eligible()
    if finish:
        c.respond('evidence', [refs['evidence']])
        decision, effect, scope = declarations(e, c)
        refs.update(decision=decision, effect=effect, decision_scope=scope)
        refs['challenge_resolved'] = c.resolve(decision, effect, scope)
        finalize(e, refs, c)
    return e, failures, refs, c


def finalize(e, refs, challenge):
    e.check()
    # Every generated carrier and connection is selected by an original-byte binding.
    records = []
    for key, (p, digest) in e.records.items():
        v = e.get(key)
        if e.record_roles[key] == 'output':
            for hint in v['relation_refs']:
                counterpart = e.get(hint['counterpart_ref'], hint['counterpart_kind'])
                source, target = (key, hint['counterpart_ref']) if hint['direction'] == 'source' else (hint['counterpart_ref'], key)
                source_kind, target_kind = (v['kind'], counterpart['kind']) if hint['direction'] == 'source' else (counterpart['kind'], v['kind'])
                matches = [x for x in upstream.read(upstream.PAIRS)['exact_pairs'] if
                    (x['relation_kind_ref'], x['source_kind'], x['target_kind']) ==
                    (hint['relation_kind_ref'], source_kind, target_kind)]
                require(len(matches) == 1, 'candidate inline selection has an undeclared ordered pair')
        records.append({'version_ref': key, 'kind': v['kind'], 'path': p.name, 'sha256': digest, 'role': e.record_roles[key]})
    blobs = [{'ref': key, 'path': p.name, 'sha256': sha} for key, (p, sha) in e.blobs.items()]
    for key in e.blobs:
        e.original(key)
    index = {'schema_version': 'lab-W05-controlled-episode/v1-candidate', 'authority_effect': 'none', 'controlled': True,
        'actual_owner_outcome': None, 'canonical_effects_applied': 0, 'challenge_state': challenge.state,
        'records': records, 'original_evidence': blobs, 'selected_refs': refs,
        'source_bindings': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha} for p, sha in e.sources.items()],
        'claim_ceiling': 'Actual controlled historical source replay and local fixture contest disposition only; original source unchanged, cause open, no production Incident or R08 owner outcome.'}
    path = e.output/'episode-index.json'
    with path.open('xb') as stream:
        stream.write(encoded(index))
    return path


def cold_verify(path, independent_sha):
    """Observational fresh-process reconstruction; never resumes a pending action."""
    path = Path(path)
    raw = path.read_bytes()
    require(byte_sha(raw) == independent_sha, 'independent episode index pin differs')
    index = parse(raw)
    require(index['controlled'] and index['actual_owner_outcome'] is None and index['canonical_effects_applied'] == 0, 'episode authority ceiling differs')
    for row in index['source_bindings']:
        require(byte_sha((ROOT/row['path']).read_bytes()) == row['sha256'], 'cold source drift')
    records = {}
    for row in index['records']:
        require(Path(row['path']).name == row['path'], 'cold record path outside scope')
        p = path.parent/row['path']
        require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == row['sha256'], 'cold original record drift')
        value = parse(p.read_bytes()); validate(value, row['kind'])
        require(row['version_ref'].startswith(value['node_id']+'@'), 'cold exact record identity differs')
        require(value['authority_effect'] == 'none' and (row['role'] == 'input' or value.get('lifecycle_state') == 'candidate'), 'cold candidate posture differs')
        require(row['version_ref'] not in records, 'cold duplicate exact revision')
        records[row['version_ref']] = value
    for row in index['original_evidence']:
        require(Path(row['path']).name == row['path'], 'cold evidence path outside scope')
        p = path.parent/row['path']
        require(p.is_file() and not p.is_symlink() and byte_sha(p.read_bytes()) == row['sha256'], 'cold original evidence drift')
    for value in records.values():
        if value['kind'] == 'typed-relation':
            p = value['payload']
            upstream.typed('cold-check', p['relation_kind_ref'], p['source']['version_ref'], p['target']['version_ref'], records, p['qualifiers'])
    refs = index['selected_refs']
    resolved = records[refs['challenge_resolved']]['payload']
    require(resolved['resolution_decision_ref'] == refs['decision'] and resolved['subject_version_ref'] == refs['historical'], 'cold challenge disposition differs')
    require(records[refs['cause']]['payload']['disposition'] == 'open', 'cold unverified cause asserted')
    return {'result': 'PASS', 'records': len(records), 'relations': sum(v['kind'] == 'typed-relation' for v in records.values()),
        'controlled': True, 'actual_owner_outcome': None, 'retry_dispatched': False}


if __name__ == '__main__':
    if sys.argv[1] == '--cold':
        print(encoded(cold_verify(sys.argv[2], sys.argv[3])).decode(), end='')
    else:
        e, _, refs, c = prepare_episode(sys.argv[1])
        print(encoded({'result': 'PASS', 'records': len(e.records), 'state': c.state, 'actual_owner_outcome': None}).decode(), end='')
        e.host.session.close()
