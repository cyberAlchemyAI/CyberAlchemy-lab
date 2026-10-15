"""One-use cryptographic stdio challenge from a provisioned local reader policy."""
import base64
from datetime import datetime,timezone
import os
from pathlib import Path
import secrets
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from protocol import *


def instant(text):
    value=datetime.fromisoformat(text.replace('Z','+00:00'))
    if value.tzinfo is None:raise ValueError('timezone required')
    return value.astimezone(timezone.utc)


def now():return datetime.now(timezone.utc)


class ReaderChannel:
    def __init__(self,path,expected_sha,schemas):
        self.path=Path(path);self.expected_sha=expected_sha;self.schemas=schemas;self.context=None
        self.used=False;self.host='host:R03-api:'+uuid.uuid4().hex;self.connection='connection:R03-api:'+uuid.uuid4().hex
        self.nonce=secrets.token_hex(32);self.policy=self.policy_guard()
        self.challenge={'schema_version':'lab-local-reader-challenge/v1-candidate','host_instance_ref':self.host,
            'connection_ref':self.connection,'nonce':self.nonce,'policy_sha256':expected_sha,
            'expires_at':self.policy['expires_at'],'authority_effect':'none'}
        source.require(self.schemas.valid('reader-authentication',self.challenge),'constructed challenge shape differs')
    def policy_guard(self):
        p=self.path
        source.require(p.is_file() and not p.is_symlink() and not any(a.is_symlink() for a in p.parents), 'unsafe reader policy')
        source.require(not p.is_relative_to(ROOT) and p.is_relative_to(Path('/tmp')),'independently provisioned external policy required')
        stat=p.stat();source.require(stat.st_uid==os.getuid() and stat.st_mode&0o777==0o600,'reader policy owner/mode differ')
        raw=p.read_bytes();source.require(len(raw)<=16384 and source.sha(raw)==self.expected_sha,'reader policy revoked or changed')
        value=frame_parse(raw)
        source.require(self.schemas.valid('reader-authentication',value),'reader policy schema differs')
        fields='schema_version principal_ref reader_public_key host_uid source_name scope_refs expires_at max_request_bytes max_response_bytes max_calls allowed_operations revoked scope_posture authority_effect actual_owner_outcome workspace'.split()
        source.require(set(value)==set(fields) and value['schema_version']=='lab-local-candidate-policy/v2-candidate'
            and value['scope_posture']=='isolated-candidate-preparation' and value['authority_effect']=='none'
            and value['actual_owner_outcome'] is None and value['revoked'] is False,'closed local candidate reader policy required')
        source.require(type(value['principal_ref']) is str and value['principal_ref']
            and value['host_uid']==os.getuid() and type(value['host_uid']) is int
            and isinstance(value['scope_refs'],list) and len(value['scope_refs'])==1
            and value['allowed_operations']==list(SUPPORTED),'reader authority scope differs')
        source.require(instant(value['expires_at'])>now(),'reader policy expired')
        source.require(type(value['max_request_bytes']) is int and 4096<=value['max_request_bytes']<=1024*1024
            and type(value['max_response_bytes']) is int and 4096<=value['max_response_bytes']<=4*1024*1024
            and type(value['max_calls']) is int and 1<=value['max_calls']<=256,'reader policy budget differs')
        from workspace import validate_scope
        validate_scope(value)
        source.source_selection(value['source_name'])
        Ed25519PublicKey.from_public_bytes(base64.b64decode(value['reader_public_key'],validate=True))
        return value
    def authenticate(self,raw):
        source.require(not self.used and self.context is None,'challenge already consumed')
        self.used=True;self.policy_guard();proof=frame_parse(raw)
        source.require(self.schemas.valid('reader-authentication',proof),'reader proof schema differs')
        source.require(set(proof)=={'schema_version','challenge','signature'} and proof['schema_version']=='lab-local-reader-proof/v1-candidate'
            and proof['challenge']==self.challenge,'proof is not for this host/connection/challenge')
        Ed25519PublicKey.from_public_bytes(base64.b64decode(self.policy['reader_public_key'],validate=True)).verify(
            base64.b64decode(proof['signature'],validate=True),compact(self.challenge))
        profile=source.source_selection(self.policy['source_name'])['engine_pins']['profile_sha256']
        authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        self.context={'schema_version':'lab-trusted-call-context/v1-candidate','context_ref':'context:R03-api:'+uuid.uuid4().hex,
            'host_instance_ref':self.host,'connection_ref':self.connection,'principal_ref':self.policy['principal_ref'],
            'role_assignment_bindings':[],'authority_scope':'operator-local','scope_refs':self.policy['scope_refs'],
            'source_profile_binding':{'ref':'implementation/lab-runtime/v2/profile.json','sha256':profile},
            'authentication_evidence_binding':binding('authentication:'+self.connection,raw),
            'policy_bindings':[{'ref':'policy:'+self.connection,'sha256':self.expected_sha},binding(str(authority.relative_to(ROOT)),authority.read_bytes())],
            'agent_instance_ref':None,'session_ref':None,'assignment_ref':None,'expires_at':self.policy['expires_at'],
            'limits':{'max_request_bytes':self.policy['max_request_bytes'],'max_response_bytes':self.policy['max_response_bytes'],
                'max_actions':self.policy['workspace']['max_actions'],'deadline':self.policy['expires_at']},'origin':'verified-local-adapter',
            'accept_client_supplied_authority_context':False,'private_credentials_in_context':False}
        source.require(self.schemas.valid('trusted-call-context',self.context),'constructed context shape differs')
        result={'schema_version':'lab-local-reader-authenticated/v1-candidate','context':self.context,
            'trusted_context_binding':binding(self.context['context_ref'],compact(self.context)),'authority_effect':'none'}
        source.require(self.schemas.valid('reader-authentication',result),'authenticated response shape differs')
        return result
    def guard(self):
        source.require(self.context is not None,'channel unauthenticated');self.policy_guard()
        source.require(instant(self.context['expires_at'])>now(),'channel expired')
        return self.context
    def close(self):
        self.context=None;self.nonce=None;self.challenge=None;self.used=True
