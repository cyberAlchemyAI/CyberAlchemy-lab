"""Cold causal tests for the exact selected preclaim trace points."""
from __future__ import annotations

from contextlib import redirect_stderr
from datetime import datetime, timedelta, timezone
import importlib
import io
import json
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[4]
PACKAGE = 'api-integration-v33-t03-one-lesson-native-v4-preclaim-diagnostic-0003'
S = importlib.import_module(PACKAGE + '.service')


def run_case(point):
    context = {'limits':{'max_request_bytes':100000,'max_actions':1,
                         'max_response_bytes':100000,
                         'deadline':(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat()},
               'context_ref':'context:test','principal_ref':'principal:test',
               'agent_instance_ref':'agent:test','assignment_ref':'assignment:test',
               'session_ref':'session:test','role_assignment_bindings':[]}
    def guard():
        if point=='pre-context':raise RuntimeError('controlled channel refusal')
        return context
    channel = SimpleNamespace(guard=guard,connection='test-channel',
                              policy={'allowed_operations':['lesson.apply'],'max_calls':8})
    schemas = SimpleNamespace(operations=['lesson.apply'],
                              valid=lambda *_:True,guard=lambda:None,
                              profile_binding={'ref':'profile:test','sha256':'0'*64})
    host = object.__new__(S.Service)
    host.channel=channel;host.schemas=schemas;host.seen=set();host.code_files={}
    host.sessions=None;host.borrowed_custody=False
    def lookup(*_):
        if point=='lookup':raise LookupError('controlled lookup negative')
        return None,None
    host.vault=SimpleNamespace(lookup=lookup,
                               claim=lambda *_args,**_kwargs:(_ for _ in ()).throw(RuntimeError('claim must not run')))
    def builder(*_):
        if point=='builder':raise RuntimeError('controlled builder negative')
        raise RuntimeError('builder must not run')
    host.select_application=builder
    host.error=lambda _call,_raw,_inner,error:{'kind':'error','code':error.code,'message':error.message}
    call={'schema_version':'lab-api-call/v2-candidate','operation':'lesson.apply',
          'call_id':'T03-'+point,'message':{},'deadline':
          (datetime.now(timezone.utc)+timedelta(minutes=(-1 if point=='expiry' else 5))).isoformat(),
          'expected_contract_profile_binding':schemas.profile_binding,
          'caller_context_ref':context['context_ref'],'max_response_bytes':8192,
          'idempotency_key':'key:'+point,'expected_source_cut':{}}
    raw=json.dumps(call,sort_keys=True,separators=(',',':')).encode()
    original=S.jcs.fingerprint
    if point=='jcs':
        S.jcs.fingerprint=lambda *_:(_ for _ in ()).throw(RuntimeError('controlled JCS negative'))
    elif point in ('lookup','builder'):
        S.jcs.fingerprint=lambda *_:'controlled-fingerprint'
    captured=io.StringIO()
    try:
        with redirect_stderr(captured):reply=host._call(raw)
    finally:
        S.jcs.fingerprint=original
    rows=[json.loads(line) for line in captured.getvalue().splitlines()]
    if point=='pre-context':
        if rows or reply.get('code')!='unauthenticated-channel' or host.seen:
            raise ValueError('pre-context refusal altered public transport or made a claim')
        return {'case':point,'public_code':reply['code'],'stages':[],
                'exception_text_not_emitted':True}
    if not rows or any(row['kind']!='T03-preclaim-stage' for row in rows):
        raise ValueError('bounded stage telemetry missing or malformed')
    stages=[row['stage'] for row in rows]
    expected={'jcs':['before-schemas-guard','before-jcs'],
              'lookup':['before-schemas-guard','before-jcs','before-lookup','before-lookup'],
              'builder':['before-schemas-guard','before-jcs','before-lookup','after-lookup','before-builder','before-builder'],
              'expiry':['before-schemas-guard']}[point]
    if stages != expected:
        raise ValueError('wrong causal stage sequence for '+point+': '+repr(stages)+' '+repr(rows[-1])+' '+repr(reply))
    expected_code={'expiry':'deadline-exceeded','jcs':'invalid-contract'}.get(point,'integrity-failed')
    if reply['code'] != expected_code:
        raise ValueError('wrong public code for '+point+': '+repr(reply))
    if point in ('lookup','builder'):
        last=rows[-1]
        if last.get('exception_class') not in ('RuntimeError','LookupError') or not isinstance(last.get('exception_text_sha256'),str):
            raise ValueError('bounded generic origin missing')
        if 'controlled' in captured.getvalue():
            raise ValueError('private exception text escaped diagnostic')
    if host.seen != {'T03-'+point}:
        raise ValueError('unexpected call ID state')
    return {'case':point,'public_code':reply['code'],'stages':stages,
            'exception_text_not_emitted':'controlled' not in captured.getvalue()}


if __name__=='__main__':
    print(json.dumps({'results':[run_case(point) for point in ('pre-context','jcs','lookup','builder','expiry')]},sort_keys=True))
