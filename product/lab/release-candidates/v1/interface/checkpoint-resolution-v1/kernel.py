"""Verify exact selected member outcomes against independently selected keys.

Conversation/existing-authority channels require an independently recognized
channel attestation as well as original owner evidence. Caller text cannot
substitute for that channel or its current owner/role recognition.
"""
import base64
from datetime import datetime,timezone
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

CHANNELS={'owner-conversation','operator-signature','existing-exact-authority'}
def require(value,reason):
    if not value:raise ValueError(reason)
def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
    require(type(raw) is bytes,'original checkpoint bytes required')
    def pairs(items):
        result={}
        for k,v in items:require(k not in result,'duplicate checkpoint JSON key');result[k]=v
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite checkpoint JSON')))
def instant(text):
    v=datetime.fromisoformat(text.replace('Z','+00:00'));require(v.tzinfo is not None,'checkpoint timezone required');return v.astimezone(timezone.utc)
def original(binding,materials):
    raw=materials.get(binding['ref']);require(type(raw) is bytes and sha(raw)==binding['sha256'],'exact checkpoint original unavailable or changed')
    return raw
def signed_original(raw,key):
    value=parse(raw);require(set(value)=={'schema_version','payload_original_base64','signature_base64'}
        and value['schema_version']=='lab-checkpoint-signed-evidence/v1-candidate','closed original signed evidence required')
    payload=base64.b64decode(value['payload_original_base64'],validate=True)
    require(base64.b64encode(payload).decode()==value['payload_original_base64'],'signed original encoding differs')
    signature=base64.b64decode(value['signature_base64'],validate=True)
    Ed25519PublicKey.from_public_bytes(bytes.fromhex(key)).verify(signature,payload)
    return parse(payload)

def verify(message,*,materials,required_members,owner_keys,channel_key,current_cut,now,validate):
    """Pure verification: all trust inputs are supplied by the actual host.

required_members is an ordered host selection of core/Principal/role/effect
bindings. owner_keys maps that Principal/role to current externally recognized
public key and recognition evidence. channel_key is independently selected for
this exact channel. validate is the actual selected protocol-schema validator.
This function neither creates an approving outcome nor applies an effect.
"""
    require(type(now) is datetime and now.tzinfo is not None,'actual checkpoint clock required')
    require(validate('checkpoint-resolution',message),'checkpoint request schema differs')
    channel=message['authorization_channel'];require(channel in CHANNELS,'unknown authorization channel')
    review_raw=original(message['review_package_binding'],materials);review=parse(review_raw)
    require(validate('review-package',review) and review['base_cut']==current_cut,'review package schema/current cut differs')
    require(review['all_targets_materialized'] is True and review['human_checkpoint_count']==1
        and review['atomicity_requirement']=='all-or-nothing' and review['authority_effect']=='none',
        'exact single-checkpoint materialized review required')
    checkpoint_raw=original(message['checkpoint_binding'],materials)
    require(sha(checkpoint_raw)==review['checkpoint']['byte_sha256'],'review selects another exact checkpoint')
    checkpoint=parse(checkpoint_raw)
    require(checkpoint.get('kind')=='decision-checkpoint' and checkpoint['node_id']==review['checkpoint']['identity_ref']
        and checkpoint['scope_ref']==review['checkpoint']['scope_ref'] and checkpoint['authority_effect']=='none',
        'checkpoint identity/scope/body differs')
    require(checkpoint['payload']['presentation_state'] in ('pending','presented') and checkpoint['payload']['closed_at'] is None,
        'closed checkpoint cannot be resolved again as a fresh outcome')
    for binding in [review['manifest_binding'],*review['ordered_core_bindings'],*review['validation_bindings'],
        *review['example_bindings'],*review['operational_instruction_bindings']]:original(binding,materials)
    require(required_members and len(required_members)==len(message['ordered_outcomes']),'required owner outcomes missing or extra')
    unique=[];pairs=set()
    for member in required_members:
        require(set(member)=={'core_binding','owner_principal_ref','owner_role_ref','effect_binding','recognition_binding'},
            'closed independently selected required member roster required')
        pair=(member['core_binding']['ref'],member['owner_principal_ref'],member['owner_role_ref'])
        require(pair not in pairs,'duplicate member/owner/role selection');pairs.add(pair)
        if member['core_binding'] not in unique:unique.append(member['core_binding'])
        original(member['effect_binding'],materials);original(member['recognition_binding'],materials)
    require(unique==review['ordered_core_bindings'],'independent member roster/core order differs from reviewed package')
    require(set(channel_key)=={'public_key_hex','evidence_binding','not_before','expires_at','channel'}
        and channel_key['channel']==channel and instant(channel_key['not_before'])<=now<instant(channel_key['expires_at']),
        'actual current independently recognized authorization channel required')
    original(channel_key['evidence_binding'],materials)
    attestation=signed_original(original(message['channel_verification_binding'],materials),channel_key['public_key_hex'])
    expected_channel={'schema_version':'lab-checkpoint-channel-attestation/v1-candidate','authorization_channel':channel,
        'review_package_binding':message['review_package_binding'],'checkpoint_binding':message['checkpoint_binding'],
        'source_cut':current_cut,'ordered_outcomes':message['ordered_outcomes'],'resolved_at':message['resolved_at'],
        'authority_effect':'none'}
    require(attestation==expected_channel,'actual channel attestation names another response/package/cut/order')
    require(instant(message['resolved_at'])<=now,'future owner outcome cannot be recorded')
    approved=[];evidence=[message['channel_verification_binding'],channel_key['evidence_binding']]
    for member,outcome in zip(required_members,message['ordered_outcomes']):
        for key in ('core_binding','owner_principal_ref','owner_role_ref'):
            require(outcome[key]==member[key],'member/owner/role/core order or identity differs')
        owner=owner_keys.get((member['owner_principal_ref'],member['owner_role_ref']))
        require(owner is not None and set(owner)=={'public_key_hex','recognition_binding','not_before','expires_at'}
            and owner['recognition_binding']==member['recognition_binding']
            and instant(owner['not_before'])<=now<instant(owner['expires_at']),'actual owner/role recognition absent, changed or expired')
        selected=signed_original(original(outcome['authorization_evidence_binding'],materials),owner['public_key_hex'])
        expected={'schema_version':'lab-checkpoint-owner-outcome/v1-candidate','authorization_channel':channel,
            'review_package_binding':message['review_package_binding'],'checkpoint_binding':message['checkpoint_binding'],
            'source_cut':current_cut,'core_binding':member['core_binding'],'effect_binding':member['effect_binding'],
            'owner_principal_ref':member['owner_principal_ref'],'owner_role_ref':member['owner_role_ref'],
            'recognition_binding':member['recognition_binding'],'selected_outcome':outcome['selected_outcome'],
            'resolved_at':message['resolved_at'],'authority_effect':'none'}
        require(selected==expected,'actual signed outcome differs from exact member/effect/owner/channel/cut')
        approved.append(outcome['selected_outcome']=='approve-exact-effect')
        evidence.extend([outcome['authorization_evidence_binding'],member['recognition_binding'],member['effect_binding']])
    authorized=all(approved)
    require(message['all_required_members_authorized']==authorized,'caller authorization aggregate differs from actual outcomes')
    return {'schema_version':'lab-checkpoint-verification-observation/v1-candidate','review_package_binding':message['review_package_binding'],
        'checkpoint_binding':message['checkpoint_binding'],'source_cut':current_cut,'ordered_outcomes':message['ordered_outcomes'],
        'all_required_members_authorized':authorized,'evidence_bindings':evidence,'actual_effects_applied':0,'authority_effect':'none',
        'claim_ceiling':'Exact recognized channel and owner/role signatures for selected members only. Verification creates no approval, admission, activation, release or completed Work.'}
