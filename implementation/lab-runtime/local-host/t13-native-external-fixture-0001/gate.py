"""Synthetic signed response over 88 exact Rust-sealed T13 fixture targets.

No actual owner, adopted representation, or authority is inferred here.
"""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[4]
DECISION_SCHEMA = ROOT / 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/decision/v2/schema.json'
DECISION_SCHEMA_SHA = 'd8858de9481049e23cd22b367b600dbeb3dc643b2d247ed91b8a6e57aff41dc9'
RESPONSE_DOMAIN = b'CAL-T13-NATIVE-SEALED-FIXTURE-RESPONSE-v1\0'
ZERO = '0' * 64


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    need(type(raw) is bytes, 'exact byte input required')
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def parse(raw):
    need(type(raw) is bytes and len(raw) <= 16 * 1024 * 1024, 'bounded original bytes required')
    def pairs(items):
        output = {}
        for key, value in items:
            need(key not in output, 'duplicate JSON key')
            output[key] = value
        return output
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'nonfinite JSON'))


def instant(raw):
    need(type(raw) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|\+00:00)', raw),
         'explicit UTC instant required')
    value = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    need(value.utcoffset().total_seconds() == 0, 'UTC instant required')
    return value


def exact_native_body(event, raw):
    need(type(event) is dict and type(raw) is bytes and raw.endswith(b'\n') and
         parse(raw) == event, 'exact Rust canonical event body differs')
    digest = event['event_digest']
    need(type(digest) is str and re.fullmatch('[a-f0-9]{64}', digest) and digest != ZERO,
         'native sealed digest required')
    token = ('"event_digest":"' + digest + '"').encode()
    need(raw.count(token) == 1 and
         sha(raw.replace(token, b'"event_digest":"' + ZERO.encode() + b'"', 1)) == digest,
         'Rust event zero-digest preimage differs')


def fixed_plan(rows, events, bodies, *, account_sha, archive_sha, native_sha):
    """Bind already returned native seal bytes to the exact 88 predecessor rows."""
    need(len(rows) == len(events) == len(bodies) == 88, 'exact 88 native targets required')
    need(all(re.fullmatch('[a-f0-9]{64}', x) for x in (account_sha, archive_sha, native_sha)),
         'selected source pins required')
    targets = []
    for position, (row, event, raw) in enumerate(zip(rows, events, bodies), 1):
        exact_native_body(event, raw)
        predecessor = row['predecessor_governance_tuple']
        state = event['complete_resulting_governance_state']
        need(set(event) == {'source_kind', 'event_family', 'event_id', 'event_digest',
                            'stream_id', 'semantic_ref', 'governance_cursor',
                            'previous_event_digest', 'complete_resulting_governance_state'}
             and row['position'] == position and row['expected_stream_version'] == 1
             and predecessor['governance_cursor'] == position
             and event['source_kind'] == 'canonical_event'
             and event['event_family'] == 'governance'
             and event['event_id'] == row['draft_event_id']
             and event['event_id'].startswith('fixture:T13:')
             and event['governance_cursor'] == row['draft_governance_cursor'] == 88 + position
             and event['stream_id'] == row['predecessor_stream_id']
             and event['previous_event_digest'] == predecessor['event_digest']
             and event['semantic_ref'] == row['semantic_tuple']
             and state['semantic_ref'] == row['semantic_tuple']
             and state['authority_effect'] == 'none'
             and state['candidate_or_maturity_status'] == 'candidate-unadmitted'
             and row['actual_owner_Decision_binding'] is None
             and row['authority_effect'] == 'none', 'sealed fixture target differs from exact inert predecessor')
        need({'source_ref': 'fixture:T13:intent:' + row['intent_binding']['sha256'],
              'relation': 'technical-predecessor-materialization',
              'operation': 'fixture-seal-only',
              'owner_route': 'fixture:T13:no-owner-decision',
              'posture': 'candidate-unadmitted-no-authority'} in state['provenance'],
             'fixture provenance absent')
        targets.append({'position': position, 'member_ref': row['member_ref'],
                        'intent_binding': copy.deepcopy(row['intent_binding']),
                        'stream_id': event['stream_id'],
                        'expected_stream_version': row['expected_stream_version'],
                        'predecessor': copy.deepcopy(predecessor),
                        'semantic_tuple': copy.deepcopy(row['semantic_tuple']),
                        'event_id': event['event_id'], 'event_digest': event['event_digest'],
                        'event_byte_sha256': sha(raw), 'event_size_bytes': len(raw)})
    need(len({x['member_ref'] for x in targets}) == 88 and
         len({x['stream_id'] for x in targets}) == 88 and
         len({x['event_byte_sha256'] for x in targets}) == 88,
         'ordered targets are not distinct')
    return {'schema_version': 'lab-T13-native-sealed-external-fixture-plan/v1',
            'fixture_only': True, 'authority_effect': 'none',
            'original_accounting_sha256': account_sha,
            'original_archive_sha256': archive_sha,
            'selected_native_executable_sha256': native_sha,
            'targets': targets}


def context(public_key_hex, now):
    need(type(public_key_hex) is str and re.fullmatch('[a-f0-9]{64}', public_key_hex),
         'ephemeral fixture public key required')
    need(type(now) is datetime and now.tzinfo is not None and now.utcoffset().total_seconds() == 0,
         'actual UTC clock required')
    return {'schema_version': 'lab-T13-native-external-fixture-context/v1',
            'fixture_only': True, 'authority_effect': 'none',
            'principal_ref': 'fixture:T13:ephemeral-owner',
            'scope_ref': 'fixture:T13:frozen-O06-native-snapshot',
            'owner_public_key_hex': public_key_hex,
            'nonce': 'fixture:T13:native-sealed-88:' + now.isoformat(),
            'decision_identity_ref': 'fixture:T13:Decision:native-sealed-88'}


def response_payload(plan, ctx, issued_at, expires_at):
    need(plan['fixture_only'] is True and plan['authority_effect'] == 'none' and len(plan['targets']) == 88,
         'fixture plan required')
    need(ctx['fixture_only'] is True and ctx['authority_effect'] == 'none' and
         ctx['principal_ref'].startswith('fixture:T13:') and ctx['scope_ref'].startswith('fixture:T13:'),
         'fixture context required')
    return {'schema_version': 'lab-T13-native-sealed-fixture-response/v1',
            'outcome': 'approve-exact-fixture-effects', 'fixture_only': True,
            'principal_ref': ctx['principal_ref'], 'scope_ref': ctx['scope_ref'],
            'nonce': ctx['nonce'], 'plan_byte_sha256': sha(encoded(plan)),
            'target_count': 88, 'issued_at': issued_at, 'expires_at': expires_at}


def verify_response(plan, ctx, raw, now):
    need(type(now) is datetime and now.tzinfo is not None and now.utcoffset().total_seconds() == 0,
         'actual UTC clock required')
    envelope = parse(raw)
    need(type(envelope) is dict and set(envelope) == {'payload', 'signature_hex'},
         'closed signed response required')
    payload = envelope['payload']
    need(type(payload) is dict and set(payload) == set(response_payload(plan, ctx, now.isoformat(), now.isoformat())),
         'closed signed response payload required')
    need(type(envelope['signature_hex']) is str and re.fullmatch('[a-f0-9]{128}', envelope['signature_hex']),
         'signature encoding differs')
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(ctx['owner_public_key_hex'])).verify(
            bytes.fromhex(envelope['signature_hex']), RESPONSE_DOMAIN + encoded(payload))
    except (InvalidSignature, ValueError) as error:
        raise ValueError('ephemeral fixture signature differs') from error
    need(payload == response_payload(plan, ctx, payload['issued_at'], payload['expires_at']) and
         instant(payload['issued_at']) <= now < instant(payload['expires_at']),
         'positive response/target/period differs')
    return payload


def decision(plan, ctx, response_raw):
    effects = ['fixture:T13:native-effect:' + target['event_digest'] for target in plan['targets']]
    return {'schema_version': 'cyberalchemy-lab-decision/v2',
            'node_id': ctx['decision_identity_ref'], 'kind': 'decision',
            'name': 'Synthetic exact native fixture response',
            'lifecycle_state': 'candidate', 'authority_effect': 'none',
            'owner_ref': ctx['principal_ref'], 'scope_ref': ctx['scope_ref'],
            'evidence_refs': ['fixture:T13:response-bytes:' + sha(response_raw)],
            'challenge_route': 'fixture:T13:challenge', 'successor_refs': [],
            'relation_refs': [{'relation_kind_ref': 'relation.declares-effect-on',
                               'direction': 'source', 'counterpart_kind': 'effect',
                               'counterpart_ref': effect} for effect in effects],
            'payload': {'decision_maker_ref': ctx['principal_ref'],
                        'subject_refs': [t['member_ref'] for t in plan['targets']],
                        'selected_outcome': 'approve-exact-fixture-effects',
                        'evidence_basis_refs': ['fixture:T13:response-bytes:' + sha(response_raw)],
                        'declared_effect_refs': effects},
            'claim_ceiling': 'Synthetic fixture only; no actual owner, adoption or authority.'}


def witness(plan, ctx, response_raw, decision_raw):
    return {'schema_version': 'lab-T13-native-sealed-external-fixture-witness/v1',
            'fixture_only': True, 'actual_adoption_authorized': False,
            'authority_effect': 'none', 'plan_byte_sha256': sha(encoded(plan)),
            'context_byte_sha256': sha(encoded(ctx)),
            'response_byte_sha256': sha(response_raw),
            'Decision_byte_sha256': sha(decision_raw),
            'event_byte_sha256': [t['event_byte_sha256'] for t in plan['targets']],
            'native_event_digests': [t['event_digest'] for t in plan['targets']],
            'expected_predecessor_digests': [t['predecessor']['event_digest'] for t in plan['targets']]}


def verify_bundle(rows, events, bodies, observed_originals, plan, ctx, response_raw,
                  decision_raw, witness_raw, now, *, expected_originals):
    fresh = fixed_plan(rows, events, bodies,
                       account_sha=plan['original_accounting_sha256'],
                       archive_sha=plan['original_archive_sha256'],
                       native_sha=plan['selected_native_executable_sha256'])
    need(fresh == plan, 'exact sealed targets changed before native effect')
    need(observed_originals == expected_originals and len(observed_originals) == 88 and all(
         old['event_digest'] == t['predecessor']['event_digest'] and
         old['event_id'] == t['predecessor']['event_id'] and
         old['governance_cursor'] == t['predecessor']['governance_cursor'] and
         old['stream_id'] == t['stream_id']
         for old, t in zip(observed_originals, plan['targets'])),
         'native observed predecessor heads differ')
    verify_response(plan, ctx, response_raw, now)
    expected_decision = decision(plan, ctx, response_raw)
    need(decision_raw == encoded(expected_decision) + b'\n',
         'deterministic external Decision bytes differ')
    schema_raw = DECISION_SCHEMA.read_bytes()
    need(sha(schema_raw) == DECISION_SCHEMA_SHA, 'original Decision schema changed')
    Draft202012Validator(parse(schema_raw)).validate(expected_decision)
    need(witness_raw == encoded(witness(plan, ctx, response_raw, decision_raw)) + b'\n',
         'exact external witness bytes differ')
    return True
