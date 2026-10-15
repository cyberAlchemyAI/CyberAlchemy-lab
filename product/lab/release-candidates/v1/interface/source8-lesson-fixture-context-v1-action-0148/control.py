"""Separately provisioned current host permission and one-use transport authentication."""
from pathlib import Path
import sys
from .base import HERE,ROOT,sha,encoded,load,require,binding,original,reader,records,API,MAPPED,API_PROFILE_PIN,preflight,FACT_SCOPE
import json,os,copy,secrets,uuid,base64
from datetime import datetime,timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
EL=reader.adapter.eligibility
AUTH=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
AUTH_SHA='4d3c34a7f19b4b47892b3fbf5673544b36b0517e516961adcc77722f5d08e906'

def now():return datetime.now(timezone.utc)
def stamp(v):return v.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def wire(value):return API.compact(value)
def bind(ref,raw):return {'ref':ref,'sha256':sha(raw)}

def verify_source(pin):
    return preflight(pin)

class HostChannel:
    """Private host policy and real cryptographic proof; no caller supplied grants."""
    def __init__(self,path,policy_sha,source_pin,source,schemas):
        self.path=Path(path);self.policy_sha=policy_sha;self.source_pin=source_pin;self.source=source;self.schemas=schemas
        self.closed=False;self.used=False;self.context=None;self.policy=self.policy_guard()
        self.connection='connection:R03-context:'+uuid.uuid4().hex;self.host='host:R03-context:'+uuid.uuid4().hex
        self.challenge={'schema_version':'lab-context-host-challenge/v1-candidate','host_instance_ref':self.host,
            'connection_ref':self.connection,'nonce':secrets.token_hex(32),'policy_sha256':policy_sha,
            'expires_at':self.policy['expires_at'],'authority_effect':'none'}
    def policy_guard(self):
        require(not self.closed,'closed host channel');FACT_SCOPE.package_guard(self.source,verify_source,self.source_pin);FACT_SCOPE.parent_guard(self.source)
        p=self.path;require(p.is_absolute() and p.is_relative_to(Path('/tmp')) and not p.is_relative_to(ROOT)
            and p.resolve()==p and not p.is_symlink() and not any(a.is_symlink() for a in p.parents),'private external host policy required')
        st=p.stat();require(st.st_uid==os.getuid() and st.st_mode&0o777==0o600 and p.stat().st_size<=16384,'host policy custody invalid')
        raw=p.read_bytes();require(sha(raw)==self.policy_sha,'host permission revoked or changed');v=EL.parse(raw)
        require(set(v)==set('schema_version host_uid principal_ref scope_ref reader_public_key not_before expires_at max_input_bytes max_output_bytes max_session_seconds period_binding allowed_operations authority_effect actual_owner_outcome'.split()),'closed host policy required')
        require(v['schema_version']=='lab-context-host-policy/v1-candidate' and v['host_uid']==os.getuid()
            and v['principal_ref']==records.PRINCIPAL and v['scope_ref']==self.source.sources.scope_ref
            and v['allowed_operations']==['context.get','session.open'] and v['authority_effect']=='none' and v['actual_owner_outcome'] is None,'host permission scope/posture differs')
        require(EL.instant(v['not_before'])<=now()<EL.instant(v['expires_at']),'host permission expired or not yet effective')
        require(v['period_binding']==binding(reader.HERE/'packages/0001/period.json'),'independent absolute Assignment period differs')
        for key,maximum in [('max_input_bytes',1048576),('max_output_bytes',4194304),('max_session_seconds',3600)]:
            require(type(v[key]) is int and 1<=v[key]<=maximum,'host budget invalid')
        Ed25519PublicKey.from_public_bytes(base64.b64decode(v['reader_public_key'],validate=True))
        return v
    def authenticate(self,proof_raw):
        require(not self.used and self.context is None,'authentication challenge already consumed');self.used=True;self.policy_guard()
        proof=EL.parse(proof_raw);require(set(proof)=={'challenge','signature'} and proof['challenge']==self.challenge,'proof names another challenge')
        Ed25519PublicKey.from_public_bytes(base64.b64decode(self.policy['reader_public_key'],validate=True)).verify(
            base64.b64decode(proof['signature'],validate=True),wire(self.challenge))
        profile=self.source.view.handle.manifest['profile_binding']
        self.context={'schema_version':'lab-trusted-call-context/v1-candidate','context_ref':'context:R03-delivery:'+uuid.uuid4().hex,
            'host_instance_ref':self.host,'connection_ref':self.connection,'principal_ref':records.PRINCIPAL,
            'role_assignment_bindings':[],'authority_scope':'operator-local','scope_refs':[self.policy['scope_ref']],
            'source_profile_binding':{'ref':profile['path'],'sha256':profile['sha256']},
            'authentication_evidence_binding':bind('authentication:'+self.connection,proof_raw),
            'policy_bindings':[bind('host-policy:'+self.connection,self.path.read_bytes()),bind(AUTH.relative_to(ROOT).as_posix(),AUTH.read_bytes())],
            'agent_instance_ref':None,'session_ref':None,'assignment_ref':None,'expires_at':self.policy['expires_at'],
            'limits':{'max_request_bytes':self.policy['max_input_bytes'],'max_response_bytes':self.policy['max_output_bytes'],
                'max_actions':1,'deadline':self.policy['expires_at']},'origin':'verified-local-adapter',
            'accept_client_supplied_authority_context':False,'private_credentials_in_context':False}
        require(self.schemas.valid('trusted-call-context',self.context),'original trusted context schema rejected constructed host context')
        return copy.deepcopy(self.context)
    def guard(self):
        require(self.context is not None and not self.closed,'host channel unauthenticated or closed');self.policy_guard()
        require(EL.instant(self.context['expires_at'])>now(),'host channel expired');return copy.deepcopy(self.context)
    def actor(self):
        c=self.guard();return {'principal_ref':c['principal_ref'],'role_assignment_refs':c['role_assignment_bindings'],
            'agent_instance_ref':None,'session_ref':None,'assignment_ref':None}
    def permission(self):
        self.guard();v=self.policy;p=load(reader.HERE/'packages/0001/period.json')
        protocols={}
        for f in (HERE/'protocols').glob('*.json'):
            body=load(f);protocols[body['reference']]={'kind':body['kind'],'binding':{'ref':f.relative_to(ROOT).as_posix(),'sha256':sha(f.read_bytes())}}
        implementation=load(HERE/'implementation-binding.json')
        return EL.SessionPermission(records.PRINCIPAL,v['scope_ref'],frozenset(v['allowed_operations']),v['not_before'],v['expires_at'],
            {p['period_ref']:[p['not_before'],p['expires_at']]},frozenset([records.POLICY]),frozenset(),frozenset(),
            (bind('host-policy:'+self.connection,self.path.read_bytes()),bind(AUTH.relative_to(ROOT).as_posix(),AUTH.read_bytes())),
            1,v['max_input_bytes'],v['max_output_bytes'],v['max_session_seconds'],
            {records.IMPLEMENTATION+'@'+records.VERSION:{'entrypoint_ref':implementation['entrypoint_ref'],
                'environment_contract_ref':implementation['environment_contract_ref'],
                'evidence_binding':{'ref':(HERE/'implementation-binding.json').relative_to(ROOT).as_posix(),'sha256':sha((HERE/'implementation-binding.json').read_bytes())}}},protocols)
    def permission_guard(self,value):
        return value==self.permission()
    def close(self):self.closed=True;self.context=None;self.challenge=None;self.used=True
