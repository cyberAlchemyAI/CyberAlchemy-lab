#!/usr/bin/env python3
"""Run an exact current Source8 Context/Session API batch in an owned workspace."""
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
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-0004'
API_MANIFEST_SHA = '822bef0481a1ce2e050be1324a1059e9bd3f018b96fb290fb10776fbc648bc64'
PROFILE_SHA = '0d0fa9fd9f461a7e9c2f3775b397051d1518f23005a75483a8bf6143eaa7e02b'
FAMILY = 'legacy-local-d95e3b741ca86f02'
SOURCE = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances' / FAMILY / 'source'
SOURCE_MANIFEST_SHA = 'fa55046b2d5ff60713500c5466fd356552fa75ceec53fe53635a81e141798019'
PERIOD_SHA = '7409f858261a79bd249c76d63c9c47686f99efff9d5db9448fd1aff3ce7d4683'


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


def utc(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def select():
    need(sha((API / 'source-manifest.json').read_bytes()) == API_MANIFEST_SHA,
         'selected API source manifest changed')
    need(sha((API / 'contract-profile.json').read_bytes()) == PROFILE_SHA,
         'selected API contract profile changed')
    need(sha((SOURCE / 'source-manifest.json').read_bytes()) == SOURCE_MANIFEST_SHA,
         'selected signed Source manifest changed')
    period_path = SOURCE / 'packages/0001/period.json'
    need(sha(period_path.read_bytes()) == PERIOD_SHA, 'selected Source period changed')
    period = json.loads(period_path.read_bytes())
    need(utc(period['not_before']) <= datetime.now(timezone.utc) < utc(period['expires_at']),
         'selected Source period is not current')
    return period


def journal_bytes(root):
    if not root.exists():
        return {}
    return {p.relative_to(root).as_posix(): sha(p.read_bytes()) for p in root.rglob('*') if p.is_file()}


def run():
    started = datetime.now(timezone.utc)
    start_ns = time.monotonic_ns()
    period = select()
    name = '_cal_t17_d95_session_api33'
    loaded(name, API / '__init__.py', package=True)
    source = __import__(name + '.source_bridge', fromlist=['replay_source'])
    protocol = __import__(name + '.protocol', fromlist=['Schemas'])
    fixtures = __import__(name + '.fixtures', fromlist=['provision'])
    auth = __import__(name + '.auth', fromlist=['ReaderChannel'])
    service_module = __import__(name + '.service', fromlist=['Service'])
    handlers = __import__(name + '.handlers', fromlist=['cut'])
    source_end = utc(period['expires_at'])
    events = []
    with ExitStack() as stack:
        view = stack.enter_context(source.replay_source(source.CURRENT_SOURCE8_NAME))
        need(source.current_source8_view(view), 'actual current Source8 view refused')
        temp = tempfile.TemporaryDirectory(prefix='cal-t17-d95-session-', dir='/tmp')
        temp_root = Path(stack.enter_context(temp))
        temp_root.chmod(0o700)
        schemas = protocol.Schemas(PROFILE_SHA)
        key, policy_path, _ = fixtures.provision(temp_root, source.CURRENT_SOURCE8_NAME,
                                                 principal=period['principal_ref'])
        policy = protocol.frame_parse(policy_path.read_bytes())
        need(policy['session_control']['period_binding']['sha256'] == PERIOD_SHA,
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
        reader_end = utc(authenticated['expires_at'])
        service = service_module.Service(view, channel, schemas)
        stack.callback(service.close)
        need(type(service.sessions).__name__ == 'ContextSessions',
             'actual current Source8 Session host absent')
        source_cut = handlers.cut(view)

        def invoke(request, *, expected='result'):
            raw = protocol.compact(request)
            call_start = datetime.now(timezone.utc).isoformat()
            call_start_ns = time.monotonic_ns()
            reply = service.call(raw)
            elapsed = (time.monotonic_ns() - call_start_ns) / 1e9
            if reply['kind'] != expected:
                print('T17 Session diagnostic: ' + json.dumps({'operation': request['operation'],
                      'reply_kind': reply['kind'],
                      'error_code': reply.get('message', {}).get('code'),
                      'error_message': reply.get('message', {}).get('message'),
                      'reader_lease_expires_at': authenticated['expires_at']}, sort_keys=True), file=sys.stderr)
            need(schemas.valid('api-reply', reply) and
                 reply['request_binding']['sha256'] == sha(raw) and reply['kind'] == expected,
                 'actual ' + request['operation'] + ' reply differs')
            events.append({'operation': request['operation'], 'request_sha256': sha(raw),
                           'reply_sha256': sha(protocol.compact(reply)), 'reply_kind': reply['kind'],
                           'error_code': reply['message'].get('code') if expected == 'error' else None,
                           'started_at_utc': call_start, 'monotonic_elapsed_seconds': elapsed})
            return reply

        session_module = __import__(name + '.current_context_sessions', fromlist=['D'])
        D, R = session_module.D, session_module.R
        context_message = D.query(view.custody_signed_sources, service.sessions.bridge)
        context_message['budget'].update(max_input_bytes=65536, max_output_bytes=1048576)
        context_request = fixtures.call(authenticated, 'lab.status', source_cut)
        context_request.update(operation='context.get', message=context_message)
        delivery = invoke(context_request)['message']
        print('T17 d95 batch: context.get PASS', file=sys.stderr)
        need(delivery['posture'] == 'ready' and delivery['source_cut'] == source_cut and
             utc(delivery['expires_at']) > datetime.now(timezone.utc),
             'actual current Context delivery not ready')
        delivery_binding = protocol.binding('context-delivery:' + delivery['context_view']['version_ref'],
                                             protocol.compact(delivery))
        proof = service.sessions.delivery(delivery_binding)
        need(proof['verified_original_binding'] == delivery_binding and
             proof['authenticated_principal_ref'] == authenticated['principal_ref'],
             'selected delivery proof origin differs')
        proof = None
        print('T17 d95 batch: delivery proof PASS', file=sys.stderr)

        ref = lambda identity: view.custody_signed_sources.sources.resolve(identity + '@' + R.VERSION)[0].artifact
        opening = fixtures.call(authenticated, 'lab.status', source_cut)
        actor = opening['message']['actor']
        budget = opening['message']['budget']
        budget['max_actions'] = 1
        opening.update(operation='session.open', idempotency_key='open:' + uuid.uuid4().hex,
                       message={'schema_version': 'lab-agent-session-open/v1-candidate',
                                'request_ref': 'request:T17-session-open:' + uuid.uuid4().hex,
                                'actor': actor, 'assignment': ref(R.ASSIGNMENT),
                                'profile': ref(R.PROFILE), 'implementation': ref(R.IMPLEMENTATION),
                                'capabilities': [ref(R.CAPABILITY)],
                                'context_delivery_binding': delivery_binding,
                                'authority_envelope_binding': session_module.stable_policy(channel),
                                'source_cut': source_cut, 'budget': budget,
                                'memory_policy': {'persistence_allowed': False, 'expires_with_session': True},
                                'authority_effect': 'none'})
        expired_request = json.loads(json.dumps(opening))
        expired_request['call_id'] = 'call:T17-expired:' + uuid.uuid4().hex
        expired_request['idempotency_key'] = 'open:expired:' + uuid.uuid4().hex
        expired_request['message']['request_ref'] = 'request:T17-expired:' + uuid.uuid4().hex
        expired_request['message']['budget']['deadline'] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        before = len(service.sessions.live)
        journal = service.vault.root / 'journal'
        before_journal = journal_bytes(journal)
        expiry = invoke(expired_request, expected='error')
        after_journal = journal_bytes(journal)
        need(len(service.sessions.live) == before and before_journal == after_journal and
             expiry['operation'] == 'session.open' and expiry['message']['code'] == 'deadline-exceeded',
             'expired Session request changed live resource count')
        expiry = None
        print('T17 d95 batch: deadline refusal PASS', file=sys.stderr)
        wrong_actor = json.loads(json.dumps(opening))
        wrong_actor['call_id'] = 'call:T17-wrong-actor:' + uuid.uuid4().hex
        wrong_actor['idempotency_key'] = 'open:wrong-actor:' + uuid.uuid4().hex
        wrong_actor['message']['request_ref'] = 'request:T17-wrong-actor:' + uuid.uuid4().hex
        wrong_actor['message']['actor']['principal_ref'] = 'principal:foreign-t17'
        need(schemas.valid('api-call', wrong_actor), 'wrong-Actor negative is not schema valid')
        before_journal = journal_bytes(journal)
        wrong_actor_reply = invoke(wrong_actor, expected='error')
        need(wrong_actor_reply['message']['code'] == 'unauthorized' and
             journal_bytes(journal) == before_journal and len(service.sessions.live) == before,
             'wrong Actor reached an owned Session or journal effect')
        print('T17 d95 batch: wrong Actor refusal PASS', file=sys.stderr)
        opened = invoke(opening)['message']
        sid = opened['session_ref']
        need(opened['posture'] == 'active' and sid in service.sessions.live,
             'actual Session resource not opened')
        resource = service.sessions.live[sid]
        session_end = utc(opened['expires_at'])
        need(resource.expires == session_end and session_end <= reader_end and session_end <= source_end,
             'actual Session lease origin differs')
        guard_ok = resource.guard()
        need(guard_ok is True, 'actual live Session guard did not pass')
        row = service.sessions.selected(sid)
        closing = fixtures.call(authenticated, 'lab.status', source_cut)
        closing.update(operation='session.close', idempotency_key='close:' + uuid.uuid4().hex,
                       message={'schema_version': 'lab-agent-session-close/v1-candidate',
                                'request_ref': 'request:T17-session-close:' + uuid.uuid4().hex,
                                'session_ref': sid, 'agent_instance_ref': opened['agent_instance_ref'],
                                'expected_session_binding': row['session_state_binding'],
                                'requested_at': datetime.now(timezone.utc).isoformat(),
                                'reason': 'completed', 'eligible_audit_bindings': [],
                                'authority_effect': 'none'})
        wrong_agent = json.loads(json.dumps(closing))
        wrong_agent['call_id'] = 'call:T17-wrong-agent:' + uuid.uuid4().hex
        wrong_agent['idempotency_key'] = 'close:wrong-agent:' + uuid.uuid4().hex
        wrong_agent['message']['request_ref'] = 'request:T17-wrong-agent:' + uuid.uuid4().hex
        wrong_agent['message']['agent_instance_ref'] = 'agent-instance:foreign-t17'
        need(schemas.valid('api-call', wrong_agent), 'wrong-Agent negative is not schema valid')
        before_journal = journal_bytes(journal)
        wrong_agent_reply = invoke(wrong_agent, expected='error')
        need(wrong_agent_reply['message']['code'] == 'conflict' and
             journal_bytes(journal) == before_journal and sid in service.sessions.live,
             'wrong Agent changed a live Session or journal')
        print('T17 d95 batch: wrong Agent refusal PASS', file=sys.stderr)
        closed = invoke(closing)['message']
        need(closed['discarded_memory'] is True and sid not in service.sessions.live and
             resource.closed and resource.memory == [] and resource.delivery is None,
             'actual Session memory disposal not observed')
        result = {'schema_version': 'lab-T17-d95-session-batch/v1',
                  'selected_source_manifest_sha256': SOURCE_MANIFEST_SHA,
                  'selected_api_source_manifest_sha256': API_MANIFEST_SHA,
                  'selected_contract_profile_sha256': PROFILE_SHA,
                  'selected_source_period_sha256': PERIOD_SHA,
                  'source_period_expires_at': period['expires_at'],
                  'reader_lease_expires_at': authenticated['expires_at'],
                  'session_lease_expires_at': opened['expires_at'],
                  'context_delivery_sha256': delivery_binding['sha256'],
                  'session_ref_sha256': sha(sid.encode()),
                  'expired_request_refused_without_live_resource': True,
                  'wrong_actor_refused_without_effect': True,
                  'wrong_agent_refused_without_effect': True,
                  'session_opened_and_guarded': True,
                  'session_closed_and_memory_disposed': True,
                  'calls': events,
                  'authority_effect': 'none',
                  'claim_ceiling': 'One current d95 Source8 Context delivery and native session.open/session.close in a private temporary workspace, with three preclaim causal refusals. This covers two T17 operations on one exact API/source cut, not all 34 operations, a Machine phase, or full T35 qualification.'}
    need(not temp_root.exists(), 'private Session workspace survived cleanup')
    result['owned_temporary_fixture_removed'] = True
    result['started_at_utc'] = started.isoformat()
    result['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['monotonic_elapsed_seconds'] = (time.monotonic_ns() - start_ns) / 1e9
    result['runner_sha256'] = sha(Path(__file__).read_bytes())
    return result


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
