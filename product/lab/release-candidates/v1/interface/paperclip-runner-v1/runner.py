"""One pinned, nonce-authenticated read episode suitable for Paperclip process.

Paperclip's environment and task identifiers are correlation data, never Lab
permission. No Paperclip API is called and no Lab candidate mutation is enabled.
"""
import argparse
import base64
from datetime import datetime,timezone,timedelta
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import selectors
import stat
import subprocess
import sys
import time
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
READS={'lab.status','catalog.get','artifact.inspect','artifact.query'}
FIELDS={
    'lab.status':set(),
    'catalog.get':{'carrier_refs','include_relations','limit','page_cursor'},
    'artifact.inspect':{'artifact','include'},
    'artifact.query':{'carrier_refs','identity_refs','relation_kind_refs','max_depth','limit','page_cursor','freshness_requirement','query_basis'},
}
def require(value,reason):
    if not value:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def parse(raw):
    def pairs(items):
        out={}
        for k,v in items:require(k not in out,'duplicate input key');out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def selected_file(path,pin,*,private=False):
    path=Path(path)
    require(path.is_absolute() and path.resolve()==path and '..' not in path.parts
        and not path.is_symlink() and not any(p.is_symlink() for p in path.parents),'unsafe selected path')
    st=path.stat();require(stat.S_ISREG(st.st_mode) and st.st_size<=4*1024*1024,'bounded regular selected file required')
    if private:require(path.is_relative_to(Path('/tmp')) and not path.is_relative_to(ROOT)
        and st.st_uid==os.getuid() and st.st_mode&0o777==0o600,'private test-owned credential/policy custody required')
    raw=path.read_bytes();require(sha(raw)==pin,'independently selected file pin differs')
    return raw
def validate_plan(plan):
    require(type(plan) is dict and set(plan)=={'schema_version','steps'}
        and plan['schema_version']=='lab-paperclip-read-plan/v1-candidate'
        and type(plan['steps']) is list and 1<=len(plan['steps'])<=16,'closed bounded read plan required')
    for row in plan['steps']:
        require(type(row) is dict and set(row)=={'operation','selectors'} and row['operation'] in READS
            and type(row['selectors']) is dict and set(row['selectors'])<=FIELDS[row['operation']],
            'only exact read operations and declared selectors are supported')
    return plan

class Child:
    def __init__(self,args,deadline):
        self.deadline=deadline;self.pending=bytearray();self.closed=False
        # Paperclip's bearer credential is never forwarded to the Lab process.
        env={k:v for k,v in os.environ.items() if not k.startswith('PAPERCLIP_')
            and k not in ('PYTHONPATH','PYTHONSTARTUP','PYTHONINSPECT')}
        self.process=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env)
        self.selector=selectors.DefaultSelector();self.selector.register(self.process.stdout,selectors.EVENT_READ)
    def receive(self):
        while True:
            if b'\n' in self.pending:
                line,_,rest=self.pending.partition(b'\n');self.pending=bytearray(rest)
                require(len(line)<=4*1024*1024,'child response byte budget exceeded')
                return parse(bytes(line))
            remaining=self.deadline-time.monotonic();require(remaining>0,'Lab read episode timed out')
            require(self.selector.select(min(remaining,1)) or self.process.poll() is None,'Lab exited before response')
            ready=self.selector.select(0)
            if not ready:continue
            raw=os.read(self.process.stdout.fileno(),65536);require(raw,'Lab response stream ended')
            self.pending.extend(raw);require(len(self.pending)<=4*1024*1024+1,'child frame exceeds byte budget')
    def send(self,value):
        require(time.monotonic()<self.deadline,'episode expired before request')
        self.process.stdin.write(encoded(value)+b'\n');self.process.stdin.flush()
    def close(self):
        if self.closed:return
        self.closed=True
        try:
            self.process.stdin.close()
            try:self.process.wait(timeout=max(.1,min(5,self.deadline-time.monotonic())))
            except subprocess.TimeoutExpired:
                self.process.terminate()
                try:self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=3)
        finally:self.selector.close();self.process.stdout.close()

def build_call(protocol,schemas,context,operation,cut,selected,deadline):
    actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
    actor['role_assignment_refs']=context['role_assignment_bindings']
    budget={'max_actions':0,'max_input_bytes':context['limits']['max_request_bytes'],
        'max_output_bytes':context['limits']['max_response_bytes'],'deadline':deadline}
    message={'schema_version':'lab-lab-status-request/v1-candidate','request_ref':'request:paperclip:'+uuid.uuid4().hex,
        'actor':actor,'source_cut':cut,'budget':budget,'authority_effect':'none'}
    if operation=='lab.status':message['scope_refs']=context['scope_refs']
    elif operation=='catalog.get':message.update(schema_version='lab-catalog-request/v1-candidate',carrier_refs=[],include_relations=True,limit=20,page_cursor=None)
    elif operation=='artifact.inspect':message.update(schema_version='lab-artifact-inspect-request/v1-candidate',artifact=None,include=['contract','gaps'])
    else:message.update(schema_version='lab-artifact-query/v1-candidate',scope_refs=context['scope_refs'],carrier_refs=[],identity_refs=[],relation_kind_refs=[],
        max_depth=0,limit=20,page_cursor=None,freshness_requirement='current',query_basis='canonical')
    message.update(selected)
    call={'schema_version':'lab-api-call/v2-candidate','expected_contract_profile_binding':schemas.profile_binding,
        'call_id':'call:paperclip:'+uuid.uuid4().hex,'operation':operation,'caller_context_ref':context['context_ref'],
        'expected_source_cut':cut,'deadline':deadline,'max_response_bytes':context['limits']['max_response_bytes'],
        'idempotency_key':None,'message':message}
    require(schemas.valid('api-call',call),'read selectors do not conform to the selected wire contract')
    require(len(encoded(call))<=context['limits']['max_request_bytes'],'read request exceeds selected input budget')
    return call

def run(args):
    started=datetime.now(timezone.utc);deadline=time.monotonic()+args.timeout_seconds
    root=Path(args.api_root);require(root.resolve()==root and root.parent==HERE.parent,'selected sibling candidate API required')
    manifest=parse(selected_file(root/'source-manifest.json',args.source_sha256))
    entries={row['path']:row for row in manifest['files']}
    require(len(entries)==len(manifest['files']),'ambiguous API source file selection')
    # Verify the bootstrap modules before executing their Python code. The
    # selected original guard then checks its complete transitive source closure.
    for filename in ('__init__.py','guard.py'):
        path=root/filename;row=entries.get(path.relative_to(ROOT).as_posix())
        require(row is not None,'API bootstrap module is outside its selected source manifest')
        selected_file(path,row['sha256'])
    name='_cal_paperclip_selected_'+root.name.replace('-','_')
    spec=importlib.util.spec_from_file_location(name,root/'__init__.py',submodule_search_locations=[str(root)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    G=__import__(name+'.guard',fromlist=['verify']);G.verify(args.source_sha256)
    P=__import__(name+'.protocol',fromlist=['Schemas']);schemas=P.Schemas(args.profile_sha256)
    privacy=__import__(name+'.workspace',fromlist=['privacy']).privacy
    policy=parse(selected_file(args.policy,args.policy_sha256,private=True))
    key=serialization.load_pem_private_key(selected_file(args.reader_key,args.reader_key_sha256,private=True),password=None)
    require(isinstance(key,Ed25519PrivateKey),'selected Ed25519 reader credential required')
    public=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    require(base64.b64decode(policy['reader_public_key'],validate=True)==public,'selected credential is not the independently provisioned reader')
    plan=validate_plan(parse(selected_file(args.plan,args.plan_sha256)))
    privacy(plan)
    require(all(step['operation'] in policy['allowed_operations'] for step in plan['steps']),'read operation outside the selected policy')
    clock_end=started+timedelta(seconds=args.timeout_seconds)
    policy_end=datetime.fromisoformat(policy['expires_at'].replace('Z','+00:00'));require(policy_end.tzinfo is not None,'policy timezone required')
    clock_end=min(clock_end,policy_end);require(clock_end>datetime.now(timezone.utc),'selected reader grant expired')
    command=[sys.executable,'-I','-B',str(root/'serve.py'),'--source-sha256',args.source_sha256,'--policy',args.policy,
        '--policy-sha256',args.policy_sha256,'--protocol-profile-sha256',args.profile_sha256]
    require(time.monotonic()<deadline,'episode expired during source/configuration preflight')
    child=Child(command,deadline);observed=[];cut=None
    try:
        challenge=child.receive();require(schemas.valid('reader-authentication',challenge)
            and challenge.get('schema_version')=='lab-local-reader-challenge/v1-candidate'
            and challenge['policy_sha256']==args.policy_sha256,'actual Lab challenge differs')
        child.send({'schema_version':'lab-local-reader-proof/v1-candidate','challenge':challenge,
            'signature':base64.b64encode(key.sign(encoded(challenge))).decode()});key=None
        authenticated=child.receive();require(schemas.valid('reader-authentication',authenticated)
            and authenticated.get('schema_version')=='lab-local-reader-authenticated/v1-candidate','actual Lab authentication refused')
        context=authenticated['context'];require(context['principal_ref']==policy['principal_ref']
            and context['scope_refs']==policy['scope_refs'] and context['accept_client_supplied_authority_context'] is False
            and authenticated['trusted_context_binding']==P.binding(context['context_ref'],encoded(context)),
            'authenticated reader identity/scope/context differs')
        steps=[{'operation':'lab.status','selectors':{}},*plan['steps']]
        for step in steps:
            call=build_call(P,schemas,context,step['operation'],cut,step['selectors'],clock_end.isoformat());raw=encoded(call)
            child.send(call);reply=child.receive();privacy(reply)
            require(schemas.valid('api-reply',reply) and reply['call_id']==call['call_id'] and reply['operation']==call['operation']
                and reply['request_binding']['sha256']==sha(raw) and reply['contract_profile_binding']==schemas.profile_binding
                and reply['trusted_context_binding']==authenticated['trusted_context_binding'],'exact read reply binding differs')
            require(reply['kind']=='result','Lab returned a domain refusal')
            if cut is None:cut=reply['message']['source_cut']
            require(reply['message']['source_cut']==cut,'read reply moved from selected source cut')
            observed.append({'operation':call['operation'],'call_binding':{'ref':call['call_id'],'sha256':sha(raw)},'reply':reply})
    finally:key=None;child.close()
    require(child.process.returncode==0,'Lab process did not close cleanly')
    G.verify(args.source_sha256)
    result={'schema_version':'lab-paperclip-read-episode/v1-candidate','result':'PASS','source_cut':cut,'calls':observed,
        'started_at':started.isoformat(),'finished_at':datetime.now(timezone.utc).isoformat(),
        'Paperclip_API_called':False,'Paperclip_assignment_grants_Lab_authority':False,'private_keys_exported':False,
        'Lab_mutations_requested':0,'human_pilot_usefulness':None,'authority_effect':'none',
        'claim_ceiling':'Exact authenticated local candidate reads and clean process exit only. No Paperclip server integration, Agent Work satisfaction, human usefulness, admission or complete Lab qualification.'}
    privacy(result);return result

def main():
    p=argparse.ArgumentParser(description='Pinned local candidate Lab reads for Paperclip process adapter.')
    for name in ('api-root','source-sha256','profile-sha256','policy','policy-sha256','reader-key','reader-key-sha256','plan','plan-sha256'):p.add_argument('--'+name,required=True)
    p.add_argument('--timeout-seconds',type=int,default=900);a=p.parse_args();require(1<=a.timeout_seconds<=900,'bounded episode timeout required')
    try:
        result=run(a);print(json.dumps(result,sort_keys=True,allow_nan=False));return 0
    except Exception as error:
        # Error values can contain private input: expose only the safe class.
        print(json.dumps({'schema_version':'lab-paperclip-runner-refusal/v1-candidate','result':'FAIL',
            'error_class':type(error).__name__,'human_pilot_usefulness':None,'authority_effect':'none',
            'claim_ceiling':'Episode failed or incomplete; no successful Lab/Paperclip operation asserted.'}));return 1
if __name__=='__main__':raise SystemExit(main())
