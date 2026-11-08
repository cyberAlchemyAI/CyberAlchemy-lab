#!/usr/bin/env python3
"""Observed current Source8 Context and Session phases in one owned workspace."""
from __future__ import annotations

from contextlib import ExitStack
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ONE_CALL = ROOT / 'implementation/lab-runtime/local-host/t35-current-call-integration-0001'
RUNNER_SHA = '08608a2301d62683f7ef78a838feb5beb5a5c4a7d2fe0d41dbe0286960ff6735'
RESULT_SHA = '3c21f463ca2df4468fad226ca49d8eab5af5deb1139c980296a9cef7b34a48e0'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def loaded(name, path, *, package=False):
    spec = importlib.util.spec_from_file_location(
        name, path, submodule_search_locations=[str(path.parent)] if package else None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def select():
    need(sha((ONE_CALL / 'run.py').read_bytes()) == RUNNER_SHA and
         sha((ONE_CALL / 'RESULT.json').read_bytes()) == RESULT_SHA,
         'reviewed T35 one-call predecessor changed')
    prior = loaded('_cal_t35_session_predecessor', ONE_CALL / 'run.py')
    prior.verify_result(json.loads((ONE_CALL / 'RESULT.json').read_bytes()))
    prior.API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-t35-session-preflight-0002'
    prior.OBSERVER = ('implementation/lab-runtime/local-host/t35-phase-observer-session-preflight-0002/observe.py',
                      'c1b0bf5ef6e1181dc0d6f5f9c97d28d9ece71d4bd84ac5effce82a739f267547')
    prior.SELECTION = ('implementation/lab-runtime/local-host/t35-phase-observer-session-preflight-0002/selected-boundaries.json',
                       '83239f99116e2fe02142534a3c14e5d57d1946be0d2e9cabce000b2249a335f6')
    prior.API_MANIFEST = ('product/lab/release-candidates/v1/interface/api-integration-v33-t35-session-preflight-0002/source-manifest.json',
                          '094d456fb4cddca37a83b03f1562b26afc3527d98d4bede752a69a0f63b7884f')
    prior.PROFILE = ('product/lab/release-candidates/v1/interface/api-integration-v33-t35-session-preflight-0002/contract-profile.json',
                     '9c93a9ef6a0a90b3aaadc6da6207c8fd8e0d706d83e69958e4750d72374b4637')
    period = prior.preflight()
    observer = loaded('_cal_t35_session_observer', ROOT / prior.OBSERVER[0])
    selected = observer.verify_boundary_selection(ROOT / prior.SELECTION[0], prior.SELECTION[1], ROOT)
    return prior, period, observer, selected


def run():
    started = datetime.now(timezone.utc)
    start_ns = time.monotonic_ns()
    prior, period, observer, selected = select()
    name = '_cal_t35_session_current_source8_api33'
    loaded(name, prior.API / '__init__.py', package=True)
    source = __import__(name + '.source_bridge', fromlist=['replay_source'])
    protocol = __import__(name + '.protocol', fromlist=['Schemas'])
    fixtures = __import__(name + '.fixtures', fromlist=['provision'])
    auth = __import__(name + '.auth', fromlist=['ReaderChannel'])
    service_module = __import__(name + '.service', fromlist=['Service'])
    handlers = __import__(name + '.handlers', fromlist=['cut'])
    source_end = prior.utc(period['expires_at'])
    events = []
    with ExitStack() as stack:
        view = stack.enter_context(source.replay_source(source.CURRENT_SOURCE8_NAME))
        need(source.current_source8_view(view), 'actual current Source8 view refused')
        temp = tempfile.TemporaryDirectory(prefix='cal-t35-current-session-', dir='/tmp')
        temp_root = Path(stack.enter_context(temp))
        temp_root.chmod(0o700)
        schemas = protocol.Schemas(prior.PROFILE[1])
        key, policy_path, _ = fixtures.provision(temp_root, source.CURRENT_SOURCE8_NAME,
                                                 principal=period['principal_ref'])
        policy = protocol.frame_parse(policy_path.read_bytes())
        need(policy['session_control']['period_binding']['sha256'] == prior.SOURCE_PERIOD[1],
             'Session permission period differs')
        policy['source8_control'] = {**source.source8_bindings(source.CURRENT_SOURCE8_NAME),
                                     'application_journal_scope': None}
        policy_raw = protocol.compact(policy)
        policy_path.write_bytes(policy_raw)
        channel = auth.ReaderChannel(policy_path, sha(policy_raw), schemas)
        authentication = channel.authenticate(fixtures.proof(key, channel.challenge))
        authenticated = authentication['context']
        key = None
        need(authenticated == channel.context and
             authentication['trusted_context_binding']['sha256'] == sha(protocol.compact(authenticated)),
             'authenticated Reader context differs')
        reader_end = prior.utc(authenticated['expires_at'])
        service = service_module.Service(view, channel, schemas)
        stack.callback(service.close)
        need(type(service.sessions).__name__ == 'ContextSessions',
             'actual current Source8 Session host absent')
        ledger = observer.BoundaryLedger('T35-current-Source8-Session-phases-0001', source_end, selected)
        source_cut = handlers.cut(view)

        def invoke(request, *, expected='result'):
            raw = protocol.compact(request)
            reply = ledger.callback(selected['Service.call'], service.call, service.call, reader_end, raw)
            if reply['kind'] != expected:
                print('T35 Session diagnostic: ' + json.dumps({'operation': request['operation'],
                      'reply_kind': reply['kind'],
                      'error_code': reply.get('message', {}).get('code'),
                      'reader_lease_expires_at': authenticated['expires_at']}, sort_keys=True), file=sys.stderr)
            need(schemas.valid('api-reply', reply) and
                 reply['request_binding']['sha256'] == sha(raw) and reply['kind'] == expected,
                 'actual ' + request['operation'] + ' reply differs')
            events.append({'operation': request['operation'], 'request_sha256': sha(raw),
                           'reply_sha256': sha(protocol.compact(reply)), 'reply_kind': reply['kind']})
            return reply

        session_module = __import__(name + '.current_context_sessions', fromlist=['D'])
        D, R = session_module.D, session_module.R
        context_message = D.query(view.custody_signed_sources, service.sessions.bridge)
        context_message['budget'].update(max_input_bytes=65536, max_output_bytes=1048576)
        context_request = fixtures.call(authenticated, 'lab.status', source_cut)
        context_request.update(operation='context.get', message=context_message)
        delivery = invoke(context_request)['message']
        print('T35 Session phase: context.get PASS', file=sys.stderr)
        need(delivery['posture'] == 'ready' and delivery['source_cut'] == source_cut and
             prior.utc(delivery['expires_at']) > datetime.now(timezone.utc),
             'actual current Context delivery not ready')
        delivery_binding = protocol.binding('context-delivery:' + delivery['context_view']['version_ref'],
                                             protocol.compact(delivery))
        proof = ledger.callback(selected['ContextSessions.delivery'], service.sessions.delivery,
                                service.sessions.delivery, reader_end, delivery_binding)
        need(proof['verified_original_binding'] == delivery_binding and
             proof['authenticated_principal_ref'] == authenticated['principal_ref'],
             'selected delivery proof origin differs')
        proof = None
        print('T35 Session phase: delivery proof PASS', file=sys.stderr)

        ref = lambda identity: view.custody_signed_sources.sources.resolve(identity + '@' + R.VERSION)[0].artifact
        opening = fixtures.call(authenticated, 'lab.status', source_cut)
        actor = opening['message']['actor']
        budget = opening['message']['budget']
        budget['max_actions'] = 1
        opening.update(operation='session.open', idempotency_key='open:' + uuid.uuid4().hex,
                       message={'schema_version': 'lab-agent-session-open/v1-candidate',
                                'request_ref': 'request:T35-session-open:' + uuid.uuid4().hex,
                                'actor': actor, 'assignment': ref(R.ASSIGNMENT),
                                'profile': ref(R.PROFILE), 'implementation': ref(R.IMPLEMENTATION),
                                'capabilities': [ref(R.CAPABILITY)],
                                'context_delivery_binding': delivery_binding,
                                'authority_envelope_binding': session_module.stable_policy(channel),
                                'source_cut': source_cut, 'budget': budget,
                                'memory_policy': {'persistence_allowed': False, 'expires_with_session': True},
                                'authority_effect': 'none'})
        expired_request = json.loads(json.dumps(opening))
        expired_request['call_id'] = 'call:T35-expired:' + uuid.uuid4().hex
        expired_request['idempotency_key'] = 'open:expired:' + uuid.uuid4().hex
        expired_request['message']['request_ref'] = 'request:T35-expired:' + uuid.uuid4().hex
        expired_request['message']['budget']['deadline'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        before = len(service.sessions.live)
        journal = service.vault.root / 'journal'
        before_journal = {p.relative_to(journal).as_posix() for p in journal.rglob('*') if p.is_file()}
        expiry = invoke(expired_request, expected='error')
        after_journal = {p.relative_to(journal).as_posix() for p in journal.rglob('*') if p.is_file()}
        need(len(service.sessions.live) == before and before_journal == after_journal and
             expiry['operation'] == 'session.open' and expiry['message']['code'] == 'deadline-exceeded',
             'expired Session request changed live resource count')
        expiry = None
        print('T35 Session phase: deadline refusal PASS', file=sys.stderr)
        before_claim_journal = {p.relative_to(journal).as_posix(): sha(p.read_bytes())
                                for p in journal.rglob('*') if p.is_file()}
        claim_calls = []
        original_claim = service.vault.claim
        def forbidden_claim(*args, **kwargs):
            claim_calls.append(True)
            raise RuntimeError('vault.claim reached despite missing native contract')
        service.vault.claim = forbidden_claim
        try:
            refused = invoke(opening, expected='error')
        finally:
            service.vault.claim = original_claim
        after_claim_journal = {p.relative_to(journal).as_posix(): sha(p.read_bytes())
                               for p in journal.rglob('*') if p.is_file()}
        need(refused['message']['code'] == 'unresolved-reference' and
             refused['message']['retry_policy'] == 'no-retry' and
             claim_calls == [] and before_claim_journal == after_claim_journal and
             len(service.sessions.live) == 0,
             'missing native v4 contract did not refuse before claim with no journal effect')
        result = {'schema_version': 'lab-T35-current-source8-session-preclaim-refusal/v1',
                  'predecessor_one_call_sha256': RESULT_SHA,
                  'selected_source_manifest_sha256': prior.SOURCE_MANIFEST[1],
                  'selected_api_source_manifest_sha256': prior.API_MANIFEST[1],
                  'selected_boundary_selection_sha256': prior.SELECTION[1],
                  'source_period_expires_at': period['expires_at'],
                  'reader_lease_expires_at': authenticated['expires_at'],
                  'context_delivery_sha256': delivery_binding['sha256'],
                  'expired_request_refused_without_live_or_journal_effect': True,
                  'missing_native_contract_error_code': refused['message']['code'],
                  'missing_native_contract_refused_before_claim': True,
                  'vault_claim_calls_for_missing_contract': len(claim_calls),
                  'owned_journal_unchanged_for_missing_contract': before_claim_journal == after_claim_journal,
                  'calls': events, 'observation': ledger.result(),
                  'authority_effect': 'none',
                  'claim_ceiling': 'One current Source8 Context delivery and two causal preclaim Session-open refusals in an owned temporary workspace. No positive Session, Machine phase, private body, global phase total, or full T35 qualification.'}
    need(not temp_root.exists(), 'private Session workspace survived cleanup')
    result['owned_temporary_fixture_removed'] = True
    result['started_at_utc'] = started.isoformat()
    result['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['monotonic_elapsed_seconds'] = (time.monotonic_ns() - start_ns) / 1e9
    result['runner_sha256'] = sha(Path(__file__).read_bytes())
    return result


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
