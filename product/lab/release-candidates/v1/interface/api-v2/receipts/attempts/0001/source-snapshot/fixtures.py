"""Explicit isolated fixture reader provisioner; never a canonical owner grant."""
import base64
from datetime import timedelta
import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from auth import *


def provision(root,source_name='engineering'):
    root=Path(root)
    source.require(root.is_dir() and not any(root.iterdir()) and root.is_relative_to(Path('/tmp'))
        and not root.is_relative_to(ROOT) and not root.is_symlink(),'fresh explicitly owned fixture root required')
    key=Ed25519PrivateKey.generate();public=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    private=key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
    descriptor=os.open(root/'reader.pem',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(descriptor,'wb') as stream:stream.write(private)
    profile=source.parse(source.original({'path':'implementation/lab-runtime/v2/profile.json','sha256':source.PINS.profile_sha256}))
    policy={'schema_version':'lab-local-reader-policy/v1-candidate','principal_ref':'principal:R03-api-fixture-reader',
        'reader_public_key':base64.b64encode(public).decode(),'host_uid':os.getuid(),'source_name':source_name,
        'scope_refs':[profile['project_ref']],'expires_at':(now()+timedelta(minutes=30)).isoformat(),
        'max_request_bytes':65536,'max_response_bytes':1048576,'max_calls':128,'read_operations':list(SUPPORTED),
        'revoked':False,'scope_posture':'isolated-candidate-reader','authority_effect':'none','actual_owner_outcome':None}
    raw=compact(policy);descriptor=os.open(root/'reader-policy.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(descriptor,'wb') as stream:stream.write(raw)
    return key,root/'reader-policy.json',source.sha(raw)


def proof(key,challenge):
    return compact({'schema_version':'lab-local-reader-proof/v1-candidate','challenge':challenge,
        'signature':base64.b64encode(key.sign(compact(challenge))).decode()})


def call(context,operation,selected_cut=None,**changes):
    deadline=(now()+timedelta(minutes=10)).isoformat()
    actor={k:context[k] for k in ('principal_ref','agent_instance_ref','assignment_ref','session_ref')}
    actor['role_assignment_refs']=context['role_assignment_bindings']
    message={'schema_version':'lab-lab-status-request/v1-candidate' if operation=='lab.status' else 'lab-catalog-request/v1-candidate',
        'request_ref':'request:R03-api:'+uuid.uuid4().hex,'actor':actor,'source_cut':selected_cut,
        'budget':{'max_actions':0,'max_input_bytes':65536,'max_output_bytes':1048576,'deadline':deadline},'authority_effect':'none'}
    if operation=='lab.status':message['scope_refs']=context['scope_refs']
    elif operation=='catalog.get':message.update(carrier_refs=[],include_relations=True,limit=20,page_cursor=None)
    elif operation=='artifact.inspect':message.update(schema_version='lab-artifact-inspect-request/v1-candidate',artifact=None,include=['body','contract','gaps'])
    elif operation=='artifact.query':message.update(schema_version='lab-artifact-query/v1-candidate',scope_refs=context['scope_refs'],
        carrier_refs=['cal.artifact-type.definition/v2'],identity_refs=[],relation_kind_refs=[],max_depth=0,limit=20,
        page_cursor=None,freshness_requirement='current',query_basis='canonical')
    else:raise ValueError('fixture operation not selected')
    message.update(changes)
    return {'schema_version':'lab-api-call/v1-candidate','call_id':'call:R03-api:'+uuid.uuid4().hex,
        'operation':operation,'caller_context_ref':context['context_ref'],'expected_source_cut':selected_cut,
        'deadline':deadline,'max_response_bytes':1048576,'idempotency_key':None,'message':message}
