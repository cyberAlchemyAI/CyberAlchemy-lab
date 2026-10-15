"""Recognize an independently selected exact signed resolution authorization.

An admitted Decision body does not supply permission. The selected host policy
must independently bind the signer, gate and scope. Public fields cannot add
them. This verifier neither signs nor resolves a challenge or admits anything.
"""
import base64
from datetime import datetime,timezone
import hashlib
import json

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

FIELDS=frozenset({'schema_version','gate_ref','principal_ref','owner_route','scope_ref',
    'source_cut','challenge','resolution_decision','challenge_contract','subject',
    'selected_outcome','semantic_proposal_binding','governance_proposal_binding',
    'evidence_bindings','consequence_routes','response_obligations','not_before','expires_at','permitted_effects','excluded_effects',
    'authority_effect'})


def require(value,reason):
    if not value:raise ValueError(reason)


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def instant(value):
    require(type(value) is str,'explicit instant required')
    result=datetime.fromisoformat(value.replace('Z','+00:00'))
    require(result.tzinfo is not None,'gate instant must identify timezone')
    return result.astimezone(timezone.utc)


def verify(envelope,*,selected_public_key_hex,recognized_principal,selected_gate_ref,
           owner_route,scope_ref,source_cut,challenge,resolution_decision,challenge_contract,
           subject,selected_outcome,semantic_proposal_binding,governance_proposal_binding,
           evidence_bindings,consequence_routes,response_obligations,principal_record,policy_expires_at,now):
    """All selection parameters originate in the independently verified host.

The actual caller passes the real current UTC clock; this module does not extend
or create any period. The current source Principal recognizes only the exact
public key digest independently selected in the private host grant.
"""
    require(type(envelope) is dict and set(envelope)=={'payload','signature'},'closed signed owner gate required')
    payload=envelope['payload']
    require(type(payload) is dict and set(payload)==FIELDS,'closed owner gate payload required')
    require(type(selected_public_key_hex) is str and len(selected_public_key_hex)==64,
            'independent Ed25519 signer selection required')
    public=bytes.fromhex(selected_public_key_hex)
    require(len(public)==32,'independent public key width differs')
    require(principal_record['kind']=='principal' and principal_record['node_id']==recognized_principal
            and principal_record['scope_ref']==scope_ref and principal_record['payload']['status']=='active'
            and principal_record['payload']['stable_subject_ref']=='ed25519-public-key-sha256:'+hashlib.sha256(public).hexdigest(),
            'selected signer not recognized by exact current Principal')
    Ed25519PublicKey.from_public_bytes(public).verify(base64.b64decode(envelope['signature'],validate=True),encoded(payload))
    expected={'schema_version':'lab-exact-challenge-resolution-gate/v1-candidate',
              'gate_ref':selected_gate_ref,'principal_ref':recognized_principal,'owner_route':owner_route,
              'scope_ref':scope_ref,'source_cut':source_cut,'challenge':challenge,
              'resolution_decision':resolution_decision,'challenge_contract':challenge_contract,
              'subject':subject,'selected_outcome':selected_outcome,
              'semantic_proposal_binding':semantic_proposal_binding,
              'governance_proposal_binding':governance_proposal_binding,
              'evidence_bindings':evidence_bindings,'consequence_routes':consequence_routes,
              'response_obligations':response_obligations,'not_before':payload['not_before'],
              'expires_at':payload['expires_at'],'permitted_effects':['prepare-exact-challenge-consequences'],
              'excluded_effects':['canonical-admission','live-activation','tool-dispatch','challenged-subject-overwrite'],
              'authority_effect':'none'}
    require(payload==expected,'signed owner gate does not bind these exact selected consequences')
    require(type(now) is datetime and now.tzinfo is not None,'actual current clock required')
    require(instant(payload['not_before'])<=now<instant(payload['expires_at'])<=instant(policy_expires_at),
            'owner gate expired, not effective or outside independent policy interval')
    return payload
