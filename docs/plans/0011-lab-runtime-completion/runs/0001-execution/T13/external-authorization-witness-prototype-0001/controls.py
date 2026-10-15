"""Owned 88-target synthetic fixtures. No actual owner/native/lease/state effects."""
import argparse
import ast
import base64
import copy
import datetime
import hashlib
import json
import os
import sys
import types
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).absolute().parent
INSTALL = ROOT / 'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--code-sha256', required=True)
    parser.add_argument('--schema-sha256', required=True); args = parser.parse_args()
    assert Path(sys.executable) == INSTALL / 'bin/python'
    sys.path.insert(0, str(INSTALL / 'deps'))
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    checks = []; fd_start = len(os.listdir('/proc/self/fd'))
    def check(name, value):
        if not value: raise AssertionError(name)
        checks.append(name)
    raw = (HERE / 'witness.py').read_bytes(); check('independent own code pin', hashlib.sha256(raw).hexdigest() == args.code_sha256)
    W = types.ModuleType('_cal_T13_owned_external_witness_fixture'); W.__file__ = str(HERE / 'witness.py')
    exec(compile(raw, W.__file__, 'exec', dont_inherit=True), W.__dict__)
    schema_raw = (HERE / 'protocol.schema.json').read_bytes(); check('independent own schema pin', W.sha(schema_raw) == args.schema_sha256)
    # Ephemeral OWNED INERT fixture signing keys, never serialized or retained.
    role_key = Ed25519PrivateKey.generate(); owner_key = Ed25519PrivateKey.generate(); other_key = Ed25519PrivateKey.generate()
    pub = lambda key: key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
    now = datetime.datetime.now(datetime.timezone.utc); start = (now - datetime.timedelta(minutes=1)).isoformat(); end = (now + datetime.timedelta(minutes=10)).isoformat()
    artifacts = {}
    def add(name, raw):
        path = 'fixture/T13/' + name; artifacts[path] = raw
        return {'path': path, 'sha256': W.sha(raw)}
    source = add('source.json', W.external_json({'fixture_only': True, 'source': 'owned-inert-source', 'actual_currentness': False}))
    native = (ROOT / 'implementation/lab-ontology/candidates/v1/adapters/native/src/lib.rs').read_bytes()
    native_schema = add('native-struct-source.rs', native)
    materializer = add('materializer.py', raw)
    assignment = add('assignment.json', W.external_json({'fixture_only': True, 'synthetic_assignment': 'owned-1', 'actual_governing_RoleAssignment': False}))
    decision_schema_raw = (ROOT / 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/decision/v2/schema.json').read_bytes()
    decision_schema = add('decision-schema.json', decision_schema_raw)
    role_payload = {'schema_version': 'lab-T13-fixture-role-evidence/v1-prototype', 'fixture_only': True,
        'issuer_ref': 'fixture:T13:role-issuer', 'principal_ref': 'fixture:T13:principal', 'role_ref': 'fixture:T13:owner-role',
        'assignment_binding': assignment, 'scope_ref': 'fixture:T13:scope', 'source_binding': source,
        'allowed_axes': ['ontology_representation_adoption'], 'valid_from': start, 'valid_until': end}
    role_envelope = {'payload': role_payload, 'signature_hex': role_key.sign(W.ROLE_DOMAIN + W.external_json(role_payload)).hex()}
    role_binding = add('role-evidence.json', W.external_json(role_envelope))
    context = {'schema_version': 'lab-T13-external-fixture-context/v1-prototype', 'mode': 'synthetic-fixture',
        'fixture_only': True, 'authority_effect': 'none', 'principal_ref': 'fixture:T13:principal', 'scope_ref': 'fixture:T13:scope',
        'role_ref': 'fixture:T13:owner-role', 'role_issuer_ref': 'fixture:T13:role-issuer', 'role_issuer_public_key_hex': pub(role_key),
        'owner_public_key_hex': pub(owner_key), 'nonce': 'fixture:T13:nonce-1', 'decision_identity_ref': 'fixture:T13:Decision',
        'valid_from': start, 'valid_until': end, 'source_binding': source, 'schema_binding': native_schema,
        'materializer_binding': materializer, 'role_evidence_binding': role_binding, 'assignment_binding': assignment,
        'decision_schema_binding': decision_schema}
    context_raw = W.external_json(context); context_pin = W.sha(context_raw); targets = []
    for index in range(1, 89):
        semantic = {'semantic_event_id': 'fixture:T13:semantic:' + str(index), 'semantic_event_digest': '0' * 64, 'semantic_cursor': index}
        head = {'stream_ref': 'fixture:T13:stream:' + str(index), 'stream_version': 0,
            'head_record_byte_sha256': W.sha(W.external_json({'fixture_only': True, 'inert_head': index})), 'native_event_digest': None}
        intent = 'fixture:T13:authorization-intent:' + str(index)
        state = {'semantic_ref': semantic,
            'provenance': [{'source_ref': intent, 'relation': 'fixture-fixed-effect', 'operation': 'fixture-prototype-only',
                'owner_route': context['principal_ref'], 'posture': 'fixture-only-no-owner-authority'}],
            'owner_route': context['principal_ref'], 'candidate_or_maturity_status': 'fixture-only',
            'promotion_state_or_handle': 'not-promoted', 'authority_kind_and_posture': {'kind': 'candidate-representation', 'posture': 'fixture-only'},
            'authority_effect': 'none', 'evidence_confidence': {'scheme_ref': 'fixture:T13:unknown-confidence', 'level': 'not-assessed'},
            'commitment_confidence': {'scheme_ref': 'fixture:T13:unknown-confidence', 'level': 'not-assessed'},
            'challenge_contract': {'challenge_response': 'Owned inert fixture review only', 'valid_challenge_modes': ['evidence', 'contradiction', 'owner_review'],
                'contradiction_edges': [], 'validation_edges': [], 'owner_route': context['principal_ref'], 'resolution_gate': 'fixture:T13:gate',
                'blocking_questions': [], 'challenge_residue_route': 'fixture:T13:residue'},
            'residue': [], 'conflicts': [], 'drift_owner': 'fixture:T13:drift', 'invalidation_route': 'fixture:T13:invalidate'}
        # Explicit unsealed original-struct-shaped inert bytes. ZERO markers are
        # NOT native event hashes; no native seal/currentness is claimed.
        event = {'source_kind': 'canonical_event', 'event_family': 'governance', 'event_id': 'fixture:T13:event:' + str(index),
            'event_digest': '0' * 64, 'stream_id': head['stream_ref'], 'semantic_ref': semantic,
            'governance_cursor': index, 'previous_event_digest': '0' * 64, 'complete_resulting_governance_state': state}
        targets.append({'position': index, 'member_ref': 'fixture:T13:member:' + str(index), 'event_binding': add('event-' + str(index) + '.json', W.external_json(event)),
            'expected_head': head, 'semantic_tuple': semantic, 'authorization_intent_ref': intent, 'native_seal_status': 'inert-unsealed-struct-fixture'})
    plan = {'schema_version': 'lab-T13-external-fixed-plan/v1-prototype', 'fixture_only': True, 'authority_effect': 'none',
        'context_byte_sha256': context_pin, 'scope_ref': context['scope_ref'], 'source_binding': source,
        'schema_binding': native_schema, 'materializer_binding': materializer, 'targets': targets}
    plan_raw = W.external_json(plan); plan_pin = W.sha(plan_raw); heads = [t['expected_head'] for t in targets]
    def prepare(craw=context_raw, cpin=context_pin, praw=plan_raw, ppin=plan_pin, art=artifacts, obs=heads, time=now):
        return W.prepare(craw, cpin, praw, ppin, art, schema_raw, args.schema_sha256, obs, time)
    prepared = prepare(); check('complete held88 fixed byte/core inputs', len(prepared['events']) == len(prepared['cores']) == 88)
    def response(payload=None, key=owner_key, domain=W.RESPONSE_DOMAIN):
        payload = W.response_payload(prepared, now.isoformat(), (now + datetime.timedelta(minutes=5)).isoformat()) if payload is None else payload
        return W.external_json({'payload': payload, 'signature_hex': key.sign(domain + W.external_json(payload)).hex()})
    response_raw = response(); decision = W.decision_record(prepared, response_raw, now); decision_raw = W.external_json(decision) + b'\n'
    before_events = prepared['events']; witness = W.materialize_witness(prepared, response_raw, decision_raw, decision_schema_raw, decision_schema['sha256'], heads, now)
    witness_raw = W.external_json(witness) + b'\n'; verified = W.verify_witness(witness_raw, W.sha(witness_raw), prepared, response_raw, decision_raw, decision_schema_raw, decision_schema['sha256'], heads, now)
    check('whole external witness verified no authority/effects/native seal', verified['technical_fixture_witness_verified'] is True and verified['actual_adoption_authorized'] is False and verified['native_seal_qualified'] is False)
    check('response/Decision never mutate held88 event preimages', prepared['events'] == before_events and all(W.sha(raw) == t['event_binding']['sha256'] for (_, raw), t in zip(before_events, targets)))
    check('original Decision/v2 schema selected external bytes', decision_schema['sha256'] == W.sha(decision_schema_raw))
    for i, core in enumerate(prepared['cores']):
        check('88 distinct fixed core:' + str(i + 1), core['position'] == i + 1 and core['event_byte_sha256'] == targets[i]['event_binding']['sha256'])
    def refuse(name, call):
        try: call()
        except (W.Refused, KeyError, ValueError, TypeError): check(name, True)
        else: raise AssertionError(name)
    refuse('independent context pin drift', lambda: prepare(cpin='f' * 64))
    refuse('independent plan pin drift', lambda: prepare(ppin='f' * 64))
    refuse('source body changed', lambda: prepare(art={**artifacts, source['path']: b'{}'}))
    refuse('materializer code changed', lambda: prepare(art={**artifacts, materializer['path']: b'changed'}))
    refuse('assignment bytes changed', lambda: prepare(art={**artifacts, assignment['path']: b'{}'}))
    refuse('role envelope body changed', lambda: prepare(art={**artifacts, role_binding['path']: b'{}'}))
    changed_heads = copy.deepcopy(heads); changed_heads[0]['head_record_byte_sha256'] = 'f' * 64
    refuse('fresh heads changed', lambda: prepare(obs=changed_heads))
    refuse('heads changed after response', lambda: W.materialize_witness(prepared, response_raw, decision_raw, decision_schema_raw, decision_schema['sha256'], changed_heads, now))
    changed = copy.deepcopy(plan); changed['targets'].reverse()
    refuse('batch ordering changed', lambda: prepare(praw=W.external_json(changed), ppin=W.sha(W.external_json(changed))))
    changed = copy.deepcopy(plan); changed['targets'].pop()
    refuse('one of88 omitted', lambda: prepare(praw=W.external_json(changed), ppin=W.sha(W.external_json(changed))))
    changed = copy.deepcopy(plan); changed['targets'][1]['member_ref'] = changed['targets'][0]['member_ref']
    refuse('duplicate independent member', lambda: prepare(praw=W.external_json(changed), ppin=W.sha(W.external_json(changed))))
    changed = copy.deepcopy(plan); changed['new_field'] = True
    refuse('unknown plan fields', lambda: prepare(praw=W.external_json(changed), ppin=W.sha(W.external_json(changed))))
    changed = copy.deepcopy(context); changed['mode'] = 'unselected-actual'
    refuse('actual lane unknown rule/authority/heads refuses', lambda: prepare(craw=W.external_json(changed), cpin=W.sha(W.external_json(changed))))
    changed = copy.deepcopy(context); changed['principal_ref'] = 'principal:repository-owner'
    refuse('synthetic lane cannot impersonate original principal', lambda: prepare(craw=W.external_json(changed), cpin=W.sha(W.external_json(changed))))
    changed = copy.deepcopy(context); changed['valid_until'] = '2026-02-30T00:00:00Z'
    refuse('invalid calendar time fails closed', lambda: prepare(craw=W.external_json(changed), cpin=W.sha(W.external_json(changed))))
    refuse('expired context/role', lambda: prepare(time=now + datetime.timedelta(minutes=20)))
    payload = json.loads(response_raw)['payload']
    for field, altered in [('principal_ref', 'fixture:T13:wrong-owner'), ('scope_ref', 'fixture:T13:wrong-scope'),
        ('nonce', 'fixture:T13:wrong-nonce'), ('plan_byte_sha256', 'f' * 64), ('core_commitment', 'f' * 64),
        ('batch_commitment', 'f' * 64), ('outcome', 'revise')]:
        bad = copy.deepcopy(payload); bad[field] = altered
        refuse('valid signature wrong selected ' + field, lambda bad=bad: W.verify_response(prepared, response(bad), now))
    bad = copy.deepcopy(payload); bad['source_binding'] = {**source, 'sha256': 'f' * 64}
    refuse('signed wrong source', lambda: W.verify_response(prepared, response(bad), now))
    bad = copy.deepcopy(payload); bad['issued_at'] = (now - datetime.timedelta(minutes=2)).isoformat()
    refuse('response before role/context interval', lambda: W.verify_response(prepared, response(bad), now))
    bad = copy.deepcopy(payload); bad['expires_at'] = (now - datetime.timedelta(seconds=1)).isoformat()
    refuse('response expired', lambda: W.verify_response(prepared, response(bad), now))
    bad = copy.deepcopy(payload); bad['expires_at'] = (now + datetime.timedelta(hours=1)).isoformat()
    refuse('response extends role/context period', lambda: W.verify_response(prepared, response(bad), now))
    bad = copy.deepcopy(payload); bad['unexpected'] = 'inert'
    refuse('unknown signed response fields', lambda: W.verify_response(prepared, response(bad), now))
    refuse('wrong owner signing key', lambda: W.verify_response(prepared, response(key=other_key), now))
    refuse('role/response signature domain substitution', lambda: W.verify_response(prepared, response(domain=W.ROLE_DOMAIN), now))
    bad = copy.deepcopy(prepared); bad['cores'] = bad['cores'][:-1]
    bad['core_commitment'] = W.domain_hash('ordered-fixed-cores', list(bad['cores']))
    refuse('prepared core truncation/recommit cannot bypass fresh88 reconstruction', lambda: W.verify_response(bad, response_raw, now))
    bad = copy.deepcopy(prepared); bad['role']['valid_until'] = (now + datetime.timedelta(days=1)).isoformat()
    refuse('cached role interval cannot renew', lambda: W.verify_response(bad, response_raw, now))
    bad = copy.deepcopy(decision); bad['payload']['declared_effect_refs'][0] = 'fixture:T13:wrong-core'
    refuse('Decision-to-fixed-core binding changed', lambda: W.materialize_witness(prepared, response_raw, W.external_json(bad) + b'\n', decision_schema_raw, decision_schema['sha256'], heads, now))
    refuse('Decision lexical bytes changed', lambda: W.materialize_witness(prepared, response_raw, json.dumps(decision, indent=4).encode(), decision_schema_raw, decision_schema['sha256'], heads, now))
    bad = copy.deepcopy(witness); bad['actual_adoption_authorized'] = True; bad_raw = W.external_json(bad) + b'\n'
    refuse('whole witness cannot grant actual permission', lambda: W.verify_witness(bad_raw, W.sha(bad_raw), prepared, response_raw, decision_raw, decision_schema_raw, decision_schema['sha256'], heads, now))
    refuse('independent witness bytes pin changed', lambda: W.verify_witness(witness_raw, 'f' * 64, prepared, response_raw, decision_raw, decision_schema_raw, decision_schema['sha256'], heads, now))
    original_path = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T13/native-event-closure-preparation-0001/ACCOUNTING-88.json'
    original_raw = original_path.read_bytes(); original_pin = 'c783761f5180365cbec59ef8ab654cb3d9bb3376e408eee37f06216ccaf46f1d'
    inherited = W.inherited_originals(original_raw, original_pin)
    for row in inherited['unchanged_blockers']:
        check('88 originals still independently blocked:' + row['member_ref'], row['native_event_bytes'] is None and row['stable_unsigned_core'] is None and row['actual_owner_Decision_binding'] is None and row['T10_dependency_complete'] is False and row['T11_dependency_complete'] is False)
    check('SHA byte/external core domains distinct and native hashes unknown', W.sha(plan_raw) != W.domain_hash('fixed-batch', plan)
        and all(d is None for d in witness['native_event_digests']))
    check('no Python native event seal invoked', 'seal_governance_event(' not in raw.decode())
    check('FD zero', len(os.listdir('/proc/self/fd')) == fd_start)
    # Public fixture bytes/signatures only, no private key serialization. Exact
    # program/native sources are references; fixture event/state data are owned.
    public_fixture = {'fixture_only': True, 'authority_effect': 'none', 'context_raw_base64': base64.b64encode(context_raw).decode(),
        'plan_raw_base64': base64.b64encode(plan_raw).decode(), 'response_raw_base64': base64.b64encode(response_raw).decode(),
        'Decision_raw_base64': base64.b64encode(decision_raw).decode(), 'witness_raw_base64': base64.b64encode(witness_raw).decode(),
        'public_artifacts': {path: base64.b64encode(data).decode() for path, data in artifacts.items()
            if path not in {materializer['path'], native_schema['path'], decision_schema['path']}},
        'public_code_source_refs': {'materializer': {'path': str((HERE / 'witness.py').relative_to(ROOT)), 'sha256': W.sha(raw)},
            'native': {'path': 'implementation/lab-ontology/candidates/v1/adapters/native/src/lib.rs', 'sha256': W.sha(native)},
            'Decision_schema': {'path': 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/decision/v2/schema.json', 'sha256': W.sha(decision_schema_raw)}},
        'private_keys_exported': False, 'native_event_seal_or_currentness_qualified': False, 'native_effects': 0}
    report = {'schema_version': 'lab-T13-external-witness-prototype-controls/v1-candidate', 'result': 'PASS',
        'check_count': len(checks), 'checks': checks, 'code_sha256': args.code_sha256, 'schema_sha256': args.schema_sha256,
        'fixture_targets': 88, 'original_intents_blocked': 88, 'FD_delta': 0,
        'owned_ephemeral_fixture_signing_only': True, 'private_keys_exported': False,
        'original_native_Store_Reader_lease_or_shared_calls': False, 'native_seal_qualified': False,
        'actual_owner_or_adoption_qualified': False, 'authority_effect': 'none', 'task_complete': False}
    for name, value in [('FIXTURE-PUBLIC-INPUTS.json', public_fixture), ('CONTROLS.json', report)]:
        with (HERE / name).open('x') as stream: stream.write(json.dumps(value, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'checks'}))

if __name__ == '__main__': main()
