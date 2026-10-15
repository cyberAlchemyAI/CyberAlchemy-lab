"""UNRUN: pure candidate boundary and owned inert output controls only."""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import uuid
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).resolve().parent

def load(path):
    name='_cal_T06_control_'+uuid.uuid4().hex
    module=types.ModuleType(name);module.__file__=str(ROOT/path);module.CAPTURED_COMPONENTS=CAPTURED_COMPONENTS;sys.modules[name]=module
    exec(compile(CAPTURED_COMPONENTS[path],module.__file__,'exec'),module.__dict__)
    return module

def main(argv=None):
    parser=argparse.ArgumentParser();parser.parse_args(argv)
    H=load((HERE/'harness.py').relative_to(ROOT).as_posix())
    B=load('docs/plans/0011-lab-runtime-completion/runs/0001-execution/T04/revision-0002/caller_adapter.py')
    controls=[]
    def good(name,operation):operation();controls.append({'control':name,'result':'PASS'})
    def bad(name,operation):
        try:operation()
        except (ValueError,KeyError,TypeError,FileNotFoundError,OSError):controls.append({'control':name,'result':'PASS-refusal'});return
        raise AssertionError(name)
    class FixtureSchemas:
        profile_binding={'ref':'fixture:profile','sha256':'0'*64}
        def valid(self,name,value):
            # Deliberately local shape fixture, not the full original registry.
            return (name=='api-reply' and value.get('schema_version')=='lab-api-reply/v2-candidate') or (name=='transport-error' and value.get('schema_version')=='lab-api-transport-error/v1-candidate')
    S=FixtureSchemas();context={'context_ref':'fixture:context'}
    chosen={'handler_bindings':{'base_catalog':{'path':'fixture/catalog.py','sha256':'1'*64},'base_inspect':{'path':'fixture/inspect.py','sha256':'2'*64}}}
    call={'call_id':'fixture:call','operation':'operation.inspect'}
    raw=b' \t{"fixture": true} \r'
    reply={'schema_version':'lab-api-reply/v2-candidate','kind':'error','call_id':call['call_id'],'operation':call['operation'],
           'contract_profile_binding':S.profile_binding,'request_binding':{'ref':'fixture:call','sha256':sha256(raw).hexdigest()},
           'trusted_context_binding':{'ref':context['context_ref'],'sha256':sha256(H.compact(context)).hexdigest()},
           'handler_binding':{'ref':'fixture/inspect.py','sha256':'2'*64},
           'message':{'schema_version':'lab-error-result/v1-candidate','code':'not-found','retry_policy':'no-retry','authority_effect':'none'}}
    def check(r=None,rbytes=raw,c=None,ctx=None):return H.reply_check(reply if r is None else r,rbytes,call if c is None else c,'base',context if ctx is None else ctx,S,chosen,'not-found',B)
    good('held raw request and context and original handler selection',lambda:check())
    bad('whitespace bytes cannot be canonicalized',lambda:check(rbytes=b'{"fixture":true}'))
    for name,change in [
        ('handler origin',lambda r:r['handler_binding'].update(ref='fixture/foreign.py')),
        ('handler digest',lambda r:r['handler_binding'].update(sha256='3'*64)),
        ('context digest',lambda r:r['trusted_context_binding'].update(sha256='4'*64)),
        ('context ref',lambda r:r['trusted_context_binding'].update(ref='fixture:foreign')),
        ('request digest',lambda r:r['request_binding'].update(sha256='5'*64)),
        ('call id',lambda r:r.update(call_id='fixture:other')),
        ('operation',lambda r:r.update(operation='catalog.get')),
        ('profile',lambda r:r.update(contract_profile_binding={'ref':'fixture:other','sha256':'6'*64})),
        ('unknown envelope',lambda r:r.update(kind='unknown')),
        ('invalid original envelope version',lambda r:r.update(schema_version='unknown')),
        ('retry forbidden',lambda r:r['message'].update(retry_policy='reconcile-first')),
        ('different domain refusal',lambda r:r['message'].update(code='unauthorized'))]:
        r=deepcopy(reply);change(r);bad('refuse '+name,lambda r=r:check(r))
    transport={'schema_version':'lab-api-transport-error/v1-candidate','code':'unauthenticated-channel','effect_may_have_started':False,'recovery_policy':'no-retry','authority_effect':'none'}
    bad('classify transport before missing domain payload',lambda:check(transport))
    bad('Root template cannot activate',lambda:H.selection_check({'status':None}))
    bad('closed public capture rejects extra fields',lambda:H.public_exact({'path':'x','sha256':'0'*64,'extra':1}))
    bad('public capture rejects traversal',lambda:H.public_exact({'path':'../x','sha256':'0'*64}))
    original=CAPTURED_COMPONENTS[(HERE.parent/'maintained-operator-qualification-0001'/'original-driver3-preimage.py').relative_to(ROOT).as_posix()]
    good('exact original driver preimage',lambda:H.need(sha256(original).hexdigest()=='1bfe17cbb51fe4369c67888986b7a86f308178ebba963bf2bad78adb5ab5feca','preimage'))
    before=len(os.listdir('/proc/self/fd'))
    with tempfile.TemporaryDirectory(prefix='cal-T06-pure-output-') as tmp:
        parent=Path(tmp);O=H.Output(parent,'fresh')
        try:
            O.append({'inert':'first'});O.report({'inert':'report'})
            controls.append({'control':'anchored sanitized event and exclusive report writes','result':'PASS'})
            bad('report no replacement',lambda:O.report({'inert':'competing'}))
            os.rename(parent/'observations',parent/'retained');os.mkdir(parent/'observations',0o700)
            bad('late output ancestor replacement refused',lambda:O.append({'inert':'never-written'}))
            H.need(not list((parent/'observations').iterdir()),'unselected replacement received bytes')
        finally:O.close()
    H.need(before==len(os.listdir('/proc/self/fd')),'own output descriptors leaked')
    controls.append({'control':'own descriptor cleanup','result':'PASS'})
    wire_results=load((HERE/'wire_controls.py').relative_to(ROOT).as_posix()).check(H)
    controls.extend(wire_results)
    print(json.dumps({'result':'PASS-pure-fixture-only','controls':controls,'full_original_schema_validation':False,
                      'native_or_lease_calls':0,'authority_effect':'none','task_complete':False},sort_keys=True))
    return 0
