"""Observe the original Machine guard with owned fixtures; no callback replacement."""
import argparse
import copy
from contextlib import ExitStack
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[6]
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v16'
OUTPUT = Path(__file__).resolve().parent
SOURCE = '8ac40a51e23b8e528178807792b8ae477aa9c46cd50d92a5b1522c82945413c7'
PROFILE = '8cc29da16d3881d8816cdc45c55358d9229fcaf226d1b9a757402ebc8675d18c'
WATCH = {API / 'legacy_context_sessions.py', ROOT / 'product/lab/release-candidates/v1/interface/machine-context-scope-v1/generation.py', API / 'machine_context_scope.py'}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def stamp():
    return datetime.now(timezone.utc).isoformat()

def bind(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-prefix', required=True)
    args=parser.parse_args()
    assert args.output_prefix.replace('-','').isalnum()
    events=OUTPUT/(args.output_prefix+'.events.jsonl')
    report=OUTPUT/(args.output_prefix+'.json')
    assert not events.exists() and not report.exists()
    traces=[]; phases=[]; observation={}; cleanup=False; failure=None; source_verified=False
    def event(value):
        with events.open('a') as stream:
            stream.write(json.dumps({'at':stamp(),**value},sort_keys=True)+'\n');stream.flush();os.fsync(stream.fileno())
    def stage(name, fn):
        start=time.monotonic();event({'phase':name,'state':'starting'})
        value=fn();duration=time.monotonic()-start
        phases.append({'phase':name,'seconds':duration});event({'phase':name,'state':'completed','seconds':duration})
        return value
    watch_names={str(x) for x in WATCH}
    def trace_raise(code, offset, exception):
        if code.co_filename not in watch_names:return
        line=next((line for begin,end,line in code.co_lines() if begin<=offset<end),code.co_firstlineno)
        row={'path':str(Path(code.co_filename).relative_to(ROOT)),'function':code.co_name,'line':line,'exception_class':type(exception).__name__,'at':stamp()}
        if len(traces)<128:traces.append(row)
    def reply_summary(reply):
        return {k:copy.deepcopy(reply[k]) for k in ('schema_version','kind','operation','code','effect_may_have_started','recovery_policy','request_binding','handler_binding') if k in reply} | {'message_code':reply.get('message',{}).get('code') if isinstance(reply.get('message'),dict) else None,'reply_sha256':sha(json.dumps(reply,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())}
    lock=OUTPUT.parent/'lease-sensitive-runtime.lock'
    fd=os.open(lock,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        name='_cal_completion_T01_actual_API16'
        spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
        package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
        def load(stem):return __import__(name+'.'+stem,fromlist=['*'])
        G=load('guard'); P=load('protocol'); A=load('auth'); F=load('example_fixture'); S=load('service'); MT=load('machine_transport'); LR=load('legacy_context_sessions'); HR=load('handlers'); PR=load('projection_refresh'); LS=load('legacy_fixture_selection')
        assert sha((API/'contract-profile.json').read_bytes())==PROFILE
        original_callbacks=(MT.select, MT.MachinePeer.proof, MT.MachinePeer.authenticate, LR.ContextSessions.view_get, LR.MachineContextSessions.view_get)
        stage('full-parent-entry-guard',lambda:G.verify(SOURCE));source_verified=True
        with ExitStack() as stack:
            view=stage('independent-legacy-replay',lambda:stack.enter_context(P.source.replay_source(LS.PUBLIC_SOURCE_NAME)))
            schemas=stage('actual-schema-profile',lambda:P.Schemas(PROFILE))
            materials,metadata,target=stage('owned-fixture-materials',lambda:F.materials_for(view))
            root=Path(stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-completion-T01-machine-')));root.chmod(0o700)
            key,policy,pin=stage('fresh-owned-reader-provision',lambda:F.provision(root,LS.PUBLIC_SOURCE_NAME,materials,metadata,principal=LR.R.PRINCIPAL,projection_control=PR.control(view)))
            channel=stage('original-reader-channel',lambda:A.ReaderChannel(policy,pin,schemas));stack.callback(channel.close)
            authenticated=stage('original-reader-authentication',lambda:channel.authenticate(F.proof(key,channel.challenge)))
            trusted=authenticated['context']
            key=None
            host=stage('original-base-service',lambda:S.Service(view,channel,schemas));stack.callback(host.close)
            current=HR.cut(view);selected=view.custody_signed_sources
            query=LR.D.query(selected,host.sessions.bridge);query['budget'].update(max_input_bytes=65536,max_output_bytes=1048576)
            request=F.call(trusted,'lab.status',current);request.update(operation='context.get',message=query)
            delivery=stage('original-parent-context-get',lambda:host.call(P.compact(request)))
            event({'phase':'parent-public-reply','observation':reply_summary(delivery)})
            assert delivery.get('kind')=='result','original parent Context refused'
            ref=lambda ident:copy.deepcopy(selected.sources.resolve(ident+'@'+LR.R.VERSION)[0].artifact)
            request=F.call(trusted,'lab.status',current);budget=request['message']['budget'];budget['max_actions']=1
            request.update(operation='session.open',idempotency_key='T01-machine-session',message={'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:T01-session-open','actor':request['message']['actor'],'assignment':ref(LR.R.ASSIGNMENT),'profile':ref(LR.R.PROFILE),'implementation':ref(LR.R.IMPLEMENTATION),'capabilities':[ref(LR.R.CAPABILITY)],'context_delivery_binding':P.binding('context-delivery:'+delivery['message']['context_view']['version_ref'],P.compact(delivery['message'])),'authority_envelope_binding':LR.stable_policy(channel),'source_cut':copy.deepcopy(current),'budget':budget,'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'})
            opened=stage('original-session-open',lambda:host.call(P.compact(request)))
            event({'phase':'session-public-reply','observation':reply_summary(opened)})
            assert opened.get('kind')=='result' and opened['message']['posture']=='active','original Session refused'
            sid=opened['message']['session_ref']
            peer=stage('original-machine-select',lambda:MT.select(host,sid,bind(API/'source-manifest.json')));stack.callback(peer.close)
            proof=stage('original-machine-proof',peer.proof)
            context=stage('original-machine-authentication',lambda:peer.authenticate(proof));proof=None
            observation.update(actual_runtime_class=type(peer.service.sessions).__name__,actual_runtime_module=type(peer.service.sessions).__module__,actual_session_expires_at=context['expires_at'])
            query=LR.D.query(selected,peer.service.sessions.bridge);query['budget'].update(max_input_bytes=65536,max_output_bytes=1048576)
            request=F.call(context,'lab.status',current);request.update(operation='context.get',message=query)
            # The interpreter observer captures only exception type/source/function/line;
            # it never reads exception values, signer/RAM/notes or frame locals.
            sys.monitoring.use_tool_id(5,'T01-sanitized-exceptions-only')
            sys.monitoring.register_callback(5,sys.monitoring.events.RAISE,trace_raise)
            sys.monitoring.register_callback(5,sys.monitoring.events.PY_UNWIND,trace_raise)
            sys.monitoring.set_events(5,sys.monitoring.events.RAISE|sys.monitoring.events.PY_UNWIND)
            try:reply=stage('actual-machine-context-get',lambda:peer.call(P.compact(request)))
            finally:
                sys.monitoring.set_events(5,0);sys.monitoring.free_tool_id(5)
            observation['actual_reply']=reply_summary(reply)
            event({'phase':'actual-Machine-public-reply','observation':observation['actual_reply'],'throwing_frames':traces})
            assert original_callbacks==(MT.select,MT.MachinePeer.proof,MT.MachinePeer.authenticate,LR.ContextSessions.view_get,LR.MachineContextSessions.view_get),'original callback identity changed'
            observation['original_callbacks_retained']=True
        cleanup=not root.exists()
        stage('full-parent-exit-guard',lambda:G.verify(SOURCE))
    except BaseException as exc:
        failure={'exception_class':type(exc).__name__,'frames':[]}
        tb=exc.__traceback__
        while tb is not None:
            path=Path(tb.tb_frame.f_code.co_filename)
            if path.is_relative_to(ROOT):failure['frames'].append({'path':str(path.relative_to(ROOT)),'function':tb.tb_frame.f_code.co_name,'line':tb.tb_lineno})
            tb=tb.tb_next
        event({'phase':'diagnostic-error','failure':failure})
    finally:
        sys.settrace(None);fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
        if 'root' in locals():cleanup=not root.exists()
    result='CAUSAL-INTEGRITY-REFUSAL-OBSERVED' if failure is None and observation.get('actual_reply',{}).get('message_code')=='integrity-failed' and any(x['path'].endswith('machine-context-scope-v1/generation.py') and x['function']=='selected' and x['exception_class']=='ValueError' for x in traces) else 'INCOMPLETE'
    value={'schema_version':'lab-Machine-causal-diagnostic/v1-candidate','result':result,'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'diagnostic_binding':bind(Path(__file__).resolve()),'phase_timings':phases,'observation':observation,'throwing_frames':traces,'failure':failure,'owned_scratch_cleanup':cleanup,'parent_entry_guard_passed':source_verified,'production_callbacks_replaced':False,'clocks_changed':False,'private_values_inspected':False,'original_API_receipts_written':False,'whole_API_qualified':False,'authority_effect':'none','goal_complete':False}
    event({'phase':'terminal','result':result,'owned_scratch_cleanup':cleanup})
    value['events_binding']=bind(events)
    with report.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'result':result,'report':str(report),'failure':failure},sort_keys=True),flush=True)
    return 0 if result=='CAUSAL-INTEGRITY-REFUSAL-OBSERVED' else 1

if __name__=='__main__':raise SystemExit(main())
