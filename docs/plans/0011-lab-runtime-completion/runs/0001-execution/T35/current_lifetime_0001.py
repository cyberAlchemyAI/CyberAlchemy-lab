"""Observe one real current Source8 Session; never replace clocks or callbacks.

The profiler records function identities, counts and durations only. It never
reads arguments, private signers, frame locals, Session notes or source bodies.
This diagnostic measures context/open/Machine/selection/inspect/close. Full
application/assessment and qualification are separate, mandatory obligations.
"""
import argparse
import copy
import cProfile
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import uuid

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
API = ROOT/'product/lab/release-candidates/v1/interface/api-integration-v17'
PROVIDER = API.parent/'source8-session-runtime-v1-action-0148'
FAMILY = API.parent/'current-session-fixtures-v1-completion-0001/instances/diagnostic-0004'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def install(name, path):
    spec = importlib.util.spec_from_file_location(name, path/'__init__.py',
        submodule_search_locations=[str(path)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    return lambda stem: importlib.import_module(name+'.'+stem)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--output-prefix', required=True)
    args = parser.parse_args()
    assert len(args.source) == len(args.profile) == 64
    assert args.output_prefix.replace('-', '').isalnum()
    report = RUN/'T35'/(args.output_prefix+'.json')
    events = RUN/'T35'/(args.output_prefix+'.events.jsonl')
    assert not report.exists() and not events.exists()
    lock = os.open(RUN/'lease-sensitive-runtime.lock', os.O_RDWR|os.O_NOFOLLOW)
    phases = []
    replies = []
    state = {}
    failure = None
    entry = exit_guard = disposed = explicit_close = False
    cleanup_observation = {}
    callbacks = None
    root = None

    def expiry():
        out = {'observed_at': now()}
        if 'source_period' in state:
            out['source_period'] = state['source_period']
        if 'channel' in state:
            out['reader_policy_expires_at'] = state['channel'].policy['expires_at']
        resource = state.get('resource')
        if resource is not None:
            out['Session_expires_at'] = resource.expires.isoformat()
            out['Session_seconds_remaining'] = (resource.expires-datetime.now(timezone.utc)).total_seconds()
            out['Session_closed'] = resource.closed
        return out

    def event(value):
        raw = json.dumps({'at': now(), **value}, sort_keys=True)+'\n'
        with events.open('a') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        print(raw.strip(), flush=True)

    def stage(label, callback):
        event({'phase': label, 'state': 'starting', 'expiry': expiry()})
        profiler = cProfile.Profile()
        started = time.monotonic()
        cpu = time.process_time()
        profiler.enable()
        failed = False
        try:
            return callback()
        except BaseException:
            failed = True
            raise
        finally:
            profiler.disable()
            elapsed = time.monotonic()-started
            cpu_seconds = time.process_time()-cpu
            calls = []
            for stat in profiler.getstats():
                code = stat.code
                if not hasattr(code, 'co_filename'):
                    continue
                path = Path(code.co_filename)
                if not path.is_relative_to(ROOT/'product/lab/release-candidates/v1/interface'):
                    continue
                calls.append({'path': str(path.relative_to(ROOT)),
                    'function': code.co_name, 'line': code.co_firstlineno,
                    'calls': stat.callcount, 'recursive_calls': stat.reccallcount,
                    'inclusive_seconds': stat.totaltime, 'exclusive_seconds': stat.inlinetime})
            calls.sort(key=lambda row: (-row['exclusive_seconds'], row['path'], row['line']))
            row = {'phase': label, 'elapsed_seconds': elapsed,
                'CPU_seconds': cpu_seconds, 'failed': failed,
                'trusted_function_rows': calls, 'expiry': expiry()}
            phases.append(row)
            event({k: v for k, v in row.items() if k != 'trusted_function_rows'} | {'state': 'completed'})

    try:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        load = install('_root_T35_current_lifetime_0001', API)
        G = load('guard')
        stage('full-current-entry-guard', lambda: G.verify(args.source))
        entry = True
        P = load('protocol')
        A = load('auth')
        F = load('fixtures')
        S = load('service')
        I = load('integration_dispatch')
        MT = load('machine_transport')
        HP = install('_root_T35_original_source8_provider_0001', PROVIDER)('provider')
        M = HP.modules(S.__package__)
        D = P.source.current_session_fixture_delivery()
        assert P.source.CURRENT_SOURCE8_NAME == 'completion-current-participation:diagnostic-0004'
        period = D.load(D.reader.HERE/'packages/0001/period.json')
        state['source_period'] = {k: period[k] for k in ('not_before', 'expires_at')}
        with ExitStack() as stack:
            selected = stage('independent-current-signed-source',
                lambda: stack.enter_context(D.reader.open_signed(D.SOURCE_PIN, D.SOURCE_PACKAGE)))
            view = selected.view
            view.custody_signed_sources = selected
            view.integrated_reader = D.reader
            view.source8_context_producer = D
            schemas = stage('actual-current-Schemas', lambda: P.Schemas(args.profile))
            materials, plan = stage('original-provider-lesson-materials', lambda: HP.lesson_materials(M, D, selected))
            root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-T35-current-lifetime-')))
            root.chmod(0o700)
            key, policy, pin = stage('independent-current-reader-provision',
                lambda: HP.provision(M, root, D, selected, P.source.CURRENT_SOURCE8_NAME, materials))
            channel = stage('actual-reader-construction', lambda: A.ReaderChannel(policy, pin, schemas))
            state['channel'] = channel
            stack.callback(channel.close)
            stage('actual-reader-nonce-authentication', lambda: channel.authenticate(F.proof(key, channel.challenge)))
            key = None
            host = stage('actual-current-Service', lambda: S.Service(view, channel, schemas))
            stack.callback(host.close)
            dispatcher = I.IntegrationService(host)
            stack.callback(dispatcher.close)
            query = stage('original-parent-query-preparation', lambda: D.query(selected, host.sessions.bridge))

            def call(service, surface, operation, message, operation_key=None):
                request = HP.call(M, service, operation, message, key=operation_key)
                raw = P.compact(request)
                reply = surface.call(raw)
                replies.append({'operation': operation, 'request_byte_sha256': sha(raw),
                    'reply_sha256': sha(P.compact(reply)), 'kind': reply.get('kind'),
                    'code': reply.get('code'),
                    'message_code': reply.get('message', {}).get('code') if type(reply.get('message')) is dict else None,
                    'expiry': expiry()})
                # Refusal is retained before domain payload access; no blind retry.
                assert reply.get('kind') == 'result' and type(reply.get('message')) is dict, 'primary-domain-refusal'
                return reply['message']

            delivery = stage('actual-parent-context-get', lambda: call(host, dispatcher, 'context.get', query))
            ref = lambda identity: copy.deepcopy(selected.sources.resolve(identity+'@'+D.records.VERSION)[0].artifact)
            budget = copy.deepcopy(query['budget'])
            budget['max_actions'] = 1
            runtime = importlib.import_module(type(host.sessions).__module__)
            opening = {'schema_version': 'lab-agent-session-open/v1-candidate',
                'request_ref': 'request:T35-open:'+uuid.uuid4().hex,
                'actor': host.sessions.bridge.actor(), 'assignment': ref(D.records.ASSIGNMENT),
                'profile': ref(D.records.PROFILE), 'implementation': ref(D.records.IMPLEMENTATION),
                'capabilities': [ref(D.records.CAPABILITY)],
                'context_delivery_binding': P.binding('context-delivery:'+delivery['context_view']['version_ref'], P.compact(delivery)),
                'authority_envelope_binding': runtime.stable_policy(channel),
                'source_cut': selected.source_cut, 'budget': budget,
                'memory_policy': {'persistence_allowed': False, 'expires_with_session': True}, 'authority_effect': 'none'}
            opened = stage('actual-Session-open', lambda: call(host, dispatcher, 'session.open', opening, 'T35:open:'+uuid.uuid4().hex))
            sid = opened['session_ref']
            state['resource'] = host.sessions.live[sid]
            scope = D.FACT_SCOPE
            state['scope'] = scope
            callbacks = (selected.guard, selected.sources.current_guard, D.verify_source, D.generate,
                channel.guard, channel.policy_guard, channel.termination_guard,
                scope.policy_scope, scope.parent_guard, scope.package_guard)
            source_binding = {'path': str((API/'source-manifest.json').relative_to(ROOT)),
                'sha256': sha((API/'source-manifest.json').read_bytes())}
            assert source_binding['sha256'] == args.source
            machine = stage('actual-Machine-select', lambda: MT.select(host, sid, source_binding))
            state['machine'] = machine
            stack.callback(machine.close)
            proof = stage('actual-Machine-proof', machine.proof)
            stage('actual-Machine-authentication', lambda: machine.authenticate(proof))
            proof = None
            machine_surface = I.IntegrationService(machine.service)
            stack.callback(machine_surface.close)
            query = stage('original-Machine-query-preparation', lambda: D.query(selected, machine.service.sessions.bridge))
            selection = stage('actual-Machine-lesson-select', lambda: call(machine.service, machine_surface, 'lesson.select', query))
            assert len(selection['items']) == len(plan['lessons'])
            assert len([row for row in selection['items'] if row['posture'] == 'selected']) == 1
            inspection = {'schema_version': 'lab-session-inspect-request/v1-candidate',
                'request_ref': 'request:T35-inspect:'+uuid.uuid4().hex,
                'actor': host.sessions.bridge.actor(), 'session_ref': sid, 'budget': budget, 'authority_effect': 'none'}
            inspected = stage('actual-parent-Session-inspect', lambda: call(host, dispatcher, 'session.inspect', inspection))
            closing = {'schema_version': 'lab-agent-session-close/v1-candidate',
                'request_ref': 'request:T35-close:'+uuid.uuid4().hex, 'session_ref': sid,
                'agent_instance_ref': opened['agent_instance_ref'],
                'expected_session_binding': inspected['last_receipt_binding'],
                'requested_at': A.now().isoformat(), 'reason': 'completed',
                'eligible_audit_bindings': [], 'authority_effect': 'none'}
            stage('actual-parent-Session-close', lambda: call(host, dispatcher, 'session.close', closing, 'T35:close:'+uuid.uuid4().hex))
            explicit_close = True
            disposed = state['resource'].closed and machine.closed and machine._private_key is None and machine.context is None
            assert disposed and scope.active_scope() is None
            assert callbacks == (selected.guard, selected.sources.current_guard, D.verify_source, D.generate,
                channel.guard, channel.policy_guard, channel.termination_guard,
                scope.policy_scope, scope.parent_guard, scope.package_guard)
        state.pop('channel', None)
    except BaseException as error:
        failure = {'exception_class': type(error).__name__, 'frames': []}
        tb = error.__traceback__
        while tb:
            path = Path(tb.tb_frame.f_code.co_filename)
            if path.is_relative_to(ROOT):
                failure['frames'].append({'path': str(path.relative_to(ROOT)),
                    'function': tb.tb_frame.f_code.co_name, 'line': tb.tb_lineno})
            tb = tb.tb_next
    finally:
        # ExitStack has already run original cleanup callbacks on both success
        # and refusal. Observe only disposal booleans, never RAM/key contents.
        resource = state.get('resource')
        machine = state.get('machine')
        scope = state.get('scope')
        try:
            cleanup_observation = {
                'resource_created': resource is not None,
                'resource_closed': resource is not None and resource.closed,
                'memory_empty': resource is not None and len(resource.memory) == 0,
                'delivery_cleared': resource is not None and resource.delivery is None,
                'machine_created': machine is not None,
                'machine_closed': machine is not None and machine.closed,
                'machine_signer_cleared': machine is not None and machine._private_key is None,
                'machine_context_cleared': machine is not None and machine.context is None,
                'source_scope_absent': scope is None or scope.active_scope() is None}
        except BaseException as error:
            cleanup_observation = {'observation_failure_class': type(error).__name__}
        if entry:
            try:
                stage('full-current-exit-guard', lambda: G.verify(args.source))
                exit_guard = True
            except BaseException as error:
                failure = failure or {'exception_class': type(error).__name__, 'frames': []}
        fcntl.flock(lock, fcntl.LOCK_UN)
        os.close(lock)
    value = {'schema_version': 'lab-current-Source8-lifetime-measurement/v1-candidate',
        'result': 'MEASURED-PASS' if failure is None and disposed and exit_guard else 'MEASURED-REFUSAL-OR-INCOMPLETE',
        'source_sha256': args.source, 'profile_sha256': args.profile,
        'phase_timings': phases, 'sanitized_replies': replies, 'failure': failure,
        'full_current_entry_exit_guard': entry and exit_guard,
        'actual_Machine_and_Session_disposal': disposed,
        'explicit_Session_close_completed': explicit_close,
        'post_ExitStack_disposal_observation': cleanup_observation,
        'owned_fixture_cleanup': root is not None and not root.exists(),
        'production_callbacks_or_clocks_replaced': False, 'private_values_inspected_or_recorded': False,
        'application_assessment_executed': False, 'historical_physical_closure': 'REFUSED',
        'whole_API_qualified': False, 'task_complete': False, 'authority_effect': 'none'}
    with report.open('x') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')
    event({'phase': 'terminal', 'result': value['result'], 'failure_class': None if failure is None else failure['exception_class']})
    return 0 if value['result'] == 'MEASURED-PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
