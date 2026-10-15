"""Unselected external-witness prototype; pure fixture lane, no native effects."""
import datetime
import hashlib
import json
import re
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

ROLE_DOMAIN = b'CAL-T13-FIXTURE-ROLE-v1\0'
RESPONSE_DOMAIN = b'CAL-T13-FIXTURE-RESPONSE-v1\0'

class Refused(ValueError):
    pass

def need(value, reason):
    if not value: raise Refused(reason)

def sha(raw):
    need(type(raw) is bytes, 'immutable bytes required')
    return hashlib.sha256(raw).hexdigest()

def parse(raw):
    need(type(raw) is bytes and len(raw) <= 16 * 1024 * 1024, 'bounded immutable JSON bytes')
    def pairs(items):
        result = {}
        for name, value in items:
            need(name not in result, 'duplicate JSON member'); result[name] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
            parse_constant=lambda _: need(False, 'nonfinite JSON'))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise Refused('invalid JSON') from error

def external_json(value):
    """NEW external domain; never used to seal a Rust native event."""
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()

def domain_hash(label, value):
    return hashlib.sha256(b'CAL-T13-EXTERNAL-PROTOTYPE-v1\0' + label.encode('ascii') + b'\0' + external_json(value)).hexdigest()

def instant(value):
    need(type(value) is str and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)', value), 'explicit UTC timestamp')
    try: result = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as error: raise Refused('invalid calendar timestamp') from error
    need(result.utcoffset() == datetime.timedelta(0), 'UTC timestamp required')
    return result

def closed(value, fields):
    need(type(value) is dict and set(value) == set(fields), 'closed fields required')

def checked(raw, expected):
    need(type(expected) is str and re.fullmatch('[a-f0-9]{64}', expected) and sha(raw) == expected,
        'independently selected byte pin differs')
    return parse(raw)

def schema_check(value, name, schema_raw, schema_pin):
    import jsonschema
    schema = checked(schema_raw, schema_pin)
    need(schema['$id'] == 'urn:cal:T13:external-witness-prototype:1', 'selected prototype schema identity')
    try: jsonschema.Draft202012Validator({'$ref': '#/$defs/' + name, '$defs': schema['$defs']}).validate(value)
    except jsonschema.ValidationError as error: raise Refused('closed prototype schema refusal') from error

def bound(binding, artifacts):
    closed(binding, ('path', 'sha256'))
    need(type(binding['path']) is str and binding['path'].startswith('fixture/T13/')
         and '..' not in binding['path'].split('/'), 'fixture public source locator only')
    need(type(artifacts) is dict and binding['path'] in artifacts, 'independently selected artifact absent')
    raw = artifacts[binding['path']]
    need(type(binding['sha256']) is str and re.fullmatch('[a-f0-9]{64}', binding['sha256'])
         and sha(raw) == binding['sha256'], 'independent artifact byte pin differs')
    return raw

def signed(envelope, domain, public_key):
    closed(envelope, ('payload', 'signature_hex'))
    need(type(public_key) is str and re.fullmatch('[a-f0-9]{64}', public_key)
         and type(envelope['signature_hex']) is str and re.fullmatch('[a-f0-9]{128}', envelope['signature_hex']), 'selected public key and signature')
    try: Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key)).verify(
        bytes.fromhex(envelope['signature_hex']), domain + external_json(envelope['payload']))
    except Exception as error: raise Refused('external signature refusal') from error
    return envelope['payload']

def native_struct_fixture(raw, target, context):
    """Original Rust STRUCTURAL fields only; ZERO is explicitly unsealed fixture."""
    event = parse(raw)
    closed(event, ('source_kind', 'event_family', 'event_id', 'event_digest', 'stream_id',
        'semantic_ref', 'governance_cursor', 'previous_event_digest', 'complete_resulting_governance_state'))
    need(event['source_kind'] == 'canonical_event' and event['event_family'] == 'governance'
         and event['event_digest'] == '0' * 64 and event['event_id'].startswith('fixture:T13:')
         and event['stream_id'] == target['expected_head']['stream_ref']
         and target['expected_head']['native_event_digest'] is None
         and event['previous_event_digest'] == '0' * 64
         and type(event['governance_cursor']) is int and event['governance_cursor'] == target['position']
         and event['semantic_ref'] == target['semantic_tuple'], 'original-field inert fixture shape differs')
    state = event['complete_resulting_governance_state']
    closed(state, ('semantic_ref', 'provenance', 'owner_route', 'candidate_or_maturity_status',
        'promotion_state_or_handle', 'authority_kind_and_posture', 'authority_effect',
        'evidence_confidence', 'commitment_confidence', 'challenge_contract', 'residue',
        'conflicts', 'drift_owner', 'invalidation_route'))
    need(state['semantic_ref'] == target['semantic_tuple'] and state['authority_effect'] == 'none'
         and state['candidate_or_maturity_status'] == 'fixture-only'
         and state['owner_route'] == context['principal_ref']
         and state['residue'] == [] and state['conflicts'] == []
         and len(state['provenance']) == 1, 'fixture governance state boundary')
    p = state['provenance'][0]
    closed(p, ('source_ref', 'relation', 'operation', 'owner_route', 'posture'))
    need(p == {'source_ref': target['authorization_intent_ref'], 'relation': 'fixture-fixed-effect',
        'operation': 'fixture-prototype-only', 'owner_route': context['principal_ref'],
        'posture': 'fixture-only-no-owner-authority'}, 'fixed stable intent provenance differs')
    closed(state['authority_kind_and_posture'], ('kind', 'posture'))
    need(state['authority_kind_and_posture'] == {'kind': 'candidate-representation',
        'posture': 'fixture-only'}, 'fixture authority posture')
    for confidence in ['evidence_confidence', 'commitment_confidence']:
        closed(state[confidence], ('scheme_ref', 'level'))
        need(state[confidence]['scheme_ref'] == 'fixture:T13:unknown-confidence'
             and state[confidence]['level'] == 'not-assessed', 'unknown confidence retained')
    challenge = state['challenge_contract']
    closed(challenge, ('challenge_response', 'valid_challenge_modes', 'contradiction_edges',
        'validation_edges', 'owner_route', 'resolution_gate', 'blocking_questions', 'challenge_residue_route'))
    need(challenge['owner_route'] == context['principal_ref']
         and challenge['valid_challenge_modes'] == ['evidence', 'contradiction', 'owner_review']
         and challenge['contradiction_edges'] == challenge['validation_edges'] == challenge['blocking_questions'] == [],
         'fixture challenge shape')
    return event

def prepare(context_raw, context_pin, plan_raw, plan_pin, artifacts, schema_raw, schema_pin, observed_heads, at=None):
    """Fix held byte inputs BEFORE response. Actual unselected lane always refuses."""
    context = checked(context_raw, context_pin)
    need(context.get('mode') == 'synthetic-fixture', 'actual adoption rule/T10/T11/current heads/eligible authority unselected')
    schema_check(context, 'context', schema_raw, schema_pin)
    need(all(context[k].startswith('fixture:T13:') for k in
        ['principal_ref', 'scope_ref', 'role_ref', 'role_issuer_ref', 'decision_identity_ref']),
        'synthetic identities cannot impersonate original governing owners')
    plan = checked(plan_raw, plan_pin); schema_check(plan, 'plan', schema_raw, schema_pin)
    now = datetime.datetime.now(datetime.timezone.utc) if at is None else at
    need(type(now) is datetime.datetime and now.utcoffset() == datetime.timedelta(0), 'aware fixture time')
    need(instant(context['valid_from']) <= now < instant(context['valid_until']), 'context interval ended')
    need(plan['context_byte_sha256'] == context_pin and plan['source_binding'] == context['source_binding']
         and plan['schema_binding'] == context['schema_binding'] and plan['materializer_binding'] == context['materializer_binding']
         and plan['scope_ref'] == context['scope_ref'], 'independent fixed source/schema/materializer/scope context differs')
    for key in ['source_binding', 'schema_binding', 'materializer_binding', 'role_evidence_binding',
                'assignment_binding', 'decision_schema_binding']:
        bound(context[key], artifacts)
    need(type(artifacts) is dict and all(type(k) is str and type(v) is bytes for k, v in artifacts.items()),
         'immutable held artifact bytes')
    role_envelope = parse(bound(context['role_evidence_binding'], artifacts))
    schema_check(role_envelope, 'role_envelope', schema_raw, schema_pin)
    role = signed(role_envelope, ROLE_DOMAIN, context['role_issuer_public_key_hex'])
    need(role['issuer_ref'] == context['role_issuer_ref'] and role['principal_ref'] == context['principal_ref']
         and role['role_ref'] == context['role_ref'] and role['assignment_binding'] == context['assignment_binding']
         and role['scope_ref'] == context['scope_ref'] and role['source_binding'] == context['source_binding']
         and role['allowed_axes'] == ['ontology_representation_adoption'], 'independent fixture role/assignment/scope/source policy differs')
    need(instant(role['valid_from']) <= now < instant(role['valid_until']), 'role interval ended')
    need(len(plan['targets']) == 88 and [t['position'] for t in plan['targets']] == list(range(1, 89))
         and all(len({t[k] for t in plan['targets']}) == 88 for k in ['member_ref', 'authorization_intent_ref'])
         and len({t['event_binding']['path'] for t in plan['targets']}) == 88
         and len({t['expected_head']['stream_ref'] for t in plan['targets']}) == 88
         and len({t['semantic_tuple']['semantic_event_id'] for t in plan['targets']}) == 88,
         'complete ordered88 independent targets required')
    need(observed_heads == [t['expected_head'] for t in plan['targets']], 'independently observed expected heads differ')
    events = []; cores = []
    for t in plan['targets']:
        need(t['member_ref'].startswith('fixture:T13:') and t['authorization_intent_ref'].startswith('fixture:T13:authorization-intent:')
             and t['native_seal_status'] == 'inert-unsealed-struct-fixture', 'synthetic fixture only; no native digest qualification')
        event_raw = bound(t['event_binding'], artifacts); native_struct_fixture(event_raw, t, context)
        events.append((t['member_ref'], event_raw))
        cores.append({'schema_version': 'lab-T13-external-fixed-effect-core/v1-prototype',
            'fixture_only': True, 'member_ref': t['member_ref'], 'event_byte_sha256': sha(event_raw),
            'source_binding': plan['source_binding'], 'schema_binding': plan['schema_binding'],
            'materializer_binding': plan['materializer_binding'], 'role_evidence_binding': context['role_evidence_binding'],
            'assignment_binding': context['assignment_binding'], 'scope_ref': plan['scope_ref'],
            'expected_head': t['expected_head'], 'semantic_tuple': t['semantic_tuple'], 'position': t['position'],
            'requested_axis': 'ontology_representation_adoption', 'authorization_intent_ref': t['authorization_intent_ref']})
    return {'context': context, 'context_raw': context_raw, 'context_pin': context_pin,
        'plan': plan, 'plan_raw': plan_raw, 'plan_pin': plan_pin, 'events': tuple(events),
        'cores': tuple(cores), 'batch_commitment': domain_hash('fixed-batch', plan),
        'core_commitment': domain_hash('ordered-fixed-cores', cores), 'role': role,
        'schema_raw': schema_raw, 'schema_pin': schema_pin,
        'artifacts': tuple(sorted(artifacts.items()))}

def response_payload(prepared, issued_at, expires_at):
    c = prepared['context']
    return {'schema_version': 'lab-T13-external-response/v1-prototype', 'fixture_only': True,
        'principal_ref': c['principal_ref'], 'scope_ref': c['scope_ref'], 'assignment_binding': c['assignment_binding'],
        'plan_byte_sha256': prepared['plan_pin'], 'batch_commitment': prepared['batch_commitment'],
        'core_commitment': prepared['core_commitment'], 'role_evidence_binding': c['role_evidence_binding'],
        'source_binding': c['source_binding'], 'nonce': c['nonce'], 'outcome': 'approve-exact-fixed-effects',
        'issued_at': issued_at, 'expires_at': expires_at}

def verify_response(prepared, response_raw, at=None):
    c = prepared['context']; now = datetime.datetime.now(datetime.timezone.utc) if at is None else at
    need(type(now) is datetime.datetime and now.utcoffset() == datetime.timedelta(0), 'aware verification time')
    # Recheck held independent context/plan/schema and EVERY body/core rather than
    # trusting mutable previously returned dictionaries. No original callbacks touched.
    need(sha(prepared['context_raw']) == prepared['context_pin'] and sha(prepared['plan_raw']) == prepared['plan_pin']
         and parse(prepared['context_raw']) == c and parse(prepared['plan_raw']) == prepared['plan'], 'held preparation context changed')
    fresh = prepare(prepared['context_raw'], prepared['context_pin'], prepared['plan_raw'], prepared['plan_pin'],
        dict(prepared['artifacts']), prepared['schema_raw'], prepared['schema_pin'],
        [t['expected_head'] for t in prepared['plan']['targets']], now)
    need(fresh == prepared, 'full held fixture source/role/body/core context changed')
    need(instant(c['valid_from']) <= now < instant(c['valid_until'])
         and instant(prepared['role']['valid_from']) <= now < instant(prepared['role']['valid_until']), 'actual verification fixture interval ended')
    need(prepared['batch_commitment'] == domain_hash('fixed-batch', prepared['plan'])
         and prepared['core_commitment'] == domain_hash('ordered-fixed-cores', list(prepared['cores'])), 'fixed batch/core changed')
    for (ref, raw), t, core in zip(prepared['events'], prepared['plan']['targets'], prepared['cores']):
        need(ref == t['member_ref'] and sha(raw) == t['event_binding']['sha256'] == core['event_byte_sha256'], 'fixed event target changed')
    envelope = parse(response_raw); schema_check(envelope, 'response_envelope', prepared['schema_raw'], prepared['schema_pin'])
    payload = signed(envelope, RESPONSE_DOMAIN, c['owner_public_key_hex'])
    need(payload == response_payload(prepared, payload['issued_at'], payload['expires_at']), 'exact positive owner/plan/core/source/scope/nonce differs')
    need(max(instant(c['valid_from']), instant(prepared['role']['valid_from'])) <= instant(payload['issued_at']) <= now < instant(payload['expires_at'])
         and instant(payload['expires_at']) <= min(instant(c['valid_until']), instant(prepared['role']['valid_until'])), 'response interval invalid')
    return payload

def decision_record(prepared, response_raw, at=None):
    """Synthetic schema-valid Decision only AFTER response; external to fixed event."""
    verify_response(prepared, response_raw, at)
    c = prepared['context']; effects = ['fixture:T13:external-core:' + domain_hash('fixed-effect-core', core) for core in prepared['cores']]
    return {'schema_version': 'cyberalchemy-lab-decision/v2', 'node_id': c['decision_identity_ref'],
        'kind': 'decision', 'name': 'Synthetic external authorization prototype', 'lifecycle_state': 'candidate',
        'authority_effect': 'none', 'owner_ref': c['principal_ref'], 'scope_ref': c['scope_ref'],
        'evidence_refs': ['fixture:T13:response-bytes:' + sha(response_raw)],
        'challenge_route': 'fixture:T13:challenge', 'successor_refs': [],
        'relation_refs': [{'relation_kind_ref': 'relation.declares-effect-on', 'direction': 'source',
            'counterpart_kind': 'effect', 'counterpart_ref': e} for e in effects],
        'payload': {'decision_maker_ref': c['principal_ref'], 'subject_refs': [t['member_ref'] for t in prepared['plan']['targets']],
            'selected_outcome': 'approve-exact-fixed-effects', 'evidence_basis_refs': ['fixture:T13:response-bytes:' + sha(response_raw)],
            'declared_effect_refs': effects},
        'claim_ceiling': 'Synthetic fixture only; no actual owner, native seal, admission, authority or original88 effect.'}

def materialize_witness(prepared, response_raw, decision_raw, decision_schema_raw, decision_schema_pin, observed_heads, at=None):
    verify_response(prepared, response_raw, at)
    need(observed_heads == [t['expected_head'] for t in prepared['plan']['targets']], 'heads changed before external witness')
    expected = decision_record(prepared, response_raw, at); decision = parse(decision_raw)
    need(decision == expected and decision_raw == external_json(expected) + b'\n',
         'deterministic external Decision bytes or response-to-fixed-cores binding differs')
    import jsonschema
    need(prepared['context']['decision_schema_binding']['sha256'] == decision_schema_pin
         and bound(prepared['context']['decision_schema_binding'], dict(prepared['artifacts'])) == decision_schema_raw,
         'independently selected original Decision schema differs')
    ds = checked(decision_schema_raw, decision_schema_pin)
    try: jsonschema.Draft202012Validator(ds).validate(decision)
    except jsonschema.ValidationError as error: raise Refused('original Decision/v2 schema refusal') from error
    # Requiring complete independent raw event bytes keeps this outside native
    # seal digest domain; response/Decision digests never modify those bytes.
    return {'schema_version': 'lab-T13-external-authorization-witness/v1-prototype',
        'fixture_only': True, 'authority_effect': 'none', 'actual_adoption_authorized': False,
        'native_seal_qualified': False, 'plan_byte_sha256': prepared['plan_pin'],
        'context_byte_sha256': prepared['context_pin'], 'batch_commitment': prepared['batch_commitment'],
        'core_commitment': prepared['core_commitment'], 'response_byte_sha256': sha(response_raw),
        'Decision_byte_sha256': sha(decision_raw), 'Decision_identity_ref': decision['node_id'],
        'owner_evidence_binding': prepared['context']['role_evidence_binding'],
        'source_binding': prepared['context']['source_binding'],
        'event_bindings': [t['event_binding'] for t in prepared['plan']['targets']],
        'expected_heads': observed_heads, 'native_event_digests': [None] * 88,
        'original_semantic_event_bytes_changed': False, 'effects_or_append_calls': 0}

def inherited_originals(account_raw, independent_account_pin):
    """All original88 remain blocked; synthetic fixtures never replace them."""
    value = checked(account_raw, independent_account_pin)
    need(value['schema_version'] == 'lab-T13-all88-native-event-accounting/v1-candidate'
         and value['authority_effect'] == 'none' and len(value['rows']) == 88, 'independent original88 account selection')
    for row in value['rows']:
        need(row['T10_dependency_complete'] is False and row['T11_dependency_complete'] is False
             and all(row[k] is None for k in ['actual_owner_Decision_binding', 'actual_owner_response',
                 'native_event_bytes', 'native_event_digest', 'stable_unsigned_core']), 'no real prerequisite/core transfer')
    return {'original_account_byte_sha256': independent_account_pin, 'original_intents': 88,
        'original_event_or_core_or_Decision_materializations': 0, 'unchanged_blockers': value['rows'],
        'unselected_external_authorization_convention': True, 'actual_adoption_ready': False,
        'authority_effect': 'none', 'task_complete': False}

def verify_witness(witness_raw, independent_witness_pin, prepared, response_raw, decision_raw,
                   decision_schema_raw, decision_schema_pin, observed_heads, at=None):
    """Whole-witness cold/pure consumer. Returns no permission or append handle."""
    value = checked(witness_raw, independent_witness_pin)
    schema_check(value, 'witness', prepared['schema_raw'], prepared['schema_pin'])
    expected = materialize_witness(prepared, response_raw, decision_raw,
        decision_schema_raw, decision_schema_pin, observed_heads, at)
    need(value == expected and witness_raw == external_json(expected) + b'\n',
         'whole exact external witness or held body dependencies differ')
    return {'technical_fixture_witness_verified': True, 'fixture_only': True,
        'authority_effect': 'none', 'actual_adoption_authorized': False,
        'native_seal_qualified': False, 'native_effects': 0}
