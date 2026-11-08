"""Build and verify an independently signed *local fixture* resolution source.

This extends an observed native Agent submission with a fixture response,
Decision/Effect/DecisionScope and candidate challenge successor. It cannot
admit records, create an actual owner outcome, or satisfy a source-current API
resolution by itself. Bytes and signing keys stay outside the repository.
"""
from __future__ import annotations
import base64
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import jsonschema

ROOT = Path(__file__).resolve().parents[4]
API_SOURCE = 'a38d44c85102b527ad681600b9b585914ac548659aba833b28915c59435fa47c'
ORIGINAL_CANDIDATE_SHA = '4a1a12597dd15b838bf28db0dfaf8ff48a42048f314859883473e2c53b69ab34'
ORIGINAL_SOURCE_CUT_SHA = 'be6891b44f1d31c35db9151829688323e9d7572a8e9bf4917a51e884b77d7475'
KINDS = ('principal','principal-reference','decision','effect','decision-scope','authority-claim','challenge-event')

def canon(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()

def sha(raw): return hashlib.sha256(raw).hexdigest()

def need(ok,reason):
    if not ok: raise ValueError(reason)

def instant(raw):
    value=datetime.fromisoformat(raw.replace('Z','+00:00'))
    need(value.tzinfo is not None and value.utcoffset().total_seconds()==0,'UTC instant required')
    return value

def frame(raw):
    def pairs(rows):
        out={}
        for k,v in rows:
            need(k not in out,'duplicate source field')
            out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs)

def schema(kind):
    path=ROOT/'authority/artifact-types'/kind/'v1/schema.json'
    return json.loads(path.read_bytes())

def validate(kind,body):
    jsonschema.Draft202012Validator(schema(kind)).validate(body)

def fixture(kind):
    return json.loads((ROOT/'authority/artifact-types'/kind/'v1/fixtures/valid/record.json').read_bytes())

def build(*,submission,observation,candidate_raw,request,now,period_end,signing_key=None,fixture_principal_ref=None):
    """Use exact successful native evidence; generated ownership is fixture-only."""
    need(sha(canon(submission))=='2f358e462cace64bf08f0899d0087826087e71f7fbe924f47be0858d3570073b'
         and sha(canon(observation))=='dede7abdfb0af369761b1bcb8febeab098b9a1e6aa86f2a064e8eb7bd4bcccfe',
         'selected native observation bytes changed')
    need(submission['result']=='PASS' and submission['challenge_submitted'] is True
         and submission['challenge_resolved'] is False and submission['owner_decision'] is None
         and submission['authority_effect']=='none','observed unresolved native submission required')
    need(submission['api_source_binding']['sha256']==API_SOURCE
         and observation['api_source_sha256']==API_SOURCE,'selected native API differs')
    need(observation['reply_kind']=='result' and observation['reply_sha256']==submission['challenge_response_sha256']
         and observation['source_cut']==submission['source_cut']==request['source_cut'],'submission source/reply differs')
    need(sha(candidate_raw)==ORIGINAL_CANDIDATE_SHA and sha(canon(submission['source_cut']))==ORIGINAL_SOURCE_CUT_SHA,
         'independently selected native candidate/source cut differs')
    event=frame(candidate_raw);validate('challenge-event',event)
    need(request['challenge_candidate_binding']['sha256']==sha(candidate_raw)
         and request['actor']['agent_instance_ref']==submission['agent_instance_ref']==event['payload']['challenger_ref']
         and event['payload']['subject_version_ref']==request['subject']['version_ref']
         and event['payload']['challenge_contract_ref']==request['challenge_contract']['version_ref']
         and event['payload']['response_state']=='open' and event['payload']['resolution_decision_ref']=='none',
         'exact submitted candidate/Actor/subject/Contract required')
    need(type(now) is datetime and now.tzinfo is not None and now.utcoffset().total_seconds()==0
         and instant(event['payload']['submitted_at'])<=now<instant(period_end),'current bounded fixture clock required')
    seed=uuid.uuid4().hex
    principal_ref=fixture_principal_ref or 'principal:local-fixture-contest-owner:'+seed
    principal_reference_ref='principal-reference:local-fixture-contest-owner:'+seed
    claim_ref='authority-claim:local-fixture-contest-only:'+seed
    decision_ref='decision:local-fixture-contest-defer:'+seed
    effect_ref='effect:local-fixture-contest-candidate:'+seed
    scope_ref='decision-scope:local-fixture-contest-candidate:'+seed
    key=signing_key or Ed25519PrivateKey.generate()
    public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    scope=event['scope_ref']
    evidence=[{'ref':'native-submission:'+submission['challenge_proposal_ref'],'sha256':sha(canon(submission))},
              {'ref':'native-call-observation','sha256':sha(canon(observation))},
              {'ref':'submitted-challenge-original','sha256':sha(candidate_raw)}]
    response={'schema_version':'lab-local-Agent-challenge-response/v1-fixture',
              'challenge_original_sha256':sha(candidate_raw),
              'challenge_ref':event['node_id'], 'subject':request['subject'],
              'challenge_contract':request['challenge_contract'],
              'challenger_kind':'agent-instance','challenger_ref':submission['agent_instance_ref'],
              'responding_fixture_principal':principal_ref,'response_mode':'owner-review',
              'responded_at':now.isoformat(),'evidence_bindings':evidence,
              'selected_fixture_outcome':'defer','actual_owner_outcome':None,'authority_effect':'none'}
    response_ref='response:local-fixture:'+sha(canon(response))
    def common(kind,identity):
        body=fixture(kind)
        body.update(node_id=identity,owner_ref=principal_ref,scope_ref=scope,
                    name='Local fixture '+kind+' for deferred Agent contest',
                    evidence_refs=[item['ref'] for item in evidence]+[response_ref],
                    relation_refs=[],successor_refs=[],lifecycle_state='candidate',
                    claim_ceiling='Synthetic local fixture consequence only. No actual owner outcome, source admission or activation.')
        return body
    principal=common('principal',principal_ref)
    principal['payload'].update(principal_kind='isolated-fixture-operator',
        stable_subject_ref='ed25519-public-key-sha256:'+sha(public),
        registry_ref='registry:local-fixture-contest-owner',
        recognition_boundary_refs=['boundary:local-fixture-contest-only'],status='active')
    def relation(kind,direction,counterpart_kind,ref):
        return {'relation_kind_ref':kind,'direction':direction,'counterpart_kind':counterpart_kind,'counterpart_ref':ref}
    principal['relation_refs']=[relation('relation.asserts-identity-of','target','principal-reference',principal_reference_ref)]
    principal_reference=common('principal-reference',principal_reference_ref)
    principal_reference['payload'].update(principal_ref=principal_ref,principal_kind='isolated-fixture-operator',
        issuer_ref=principal_ref,resolution_route='route:local-fixture-signed-source',
        integrity_digest='ed25519-public-key-sha256:'+sha(public),privacy_posture='Synthetic fixture public key only')
    principal_reference['relation_refs']=[relation('relation.asserts-identity-of','source','principal',principal_ref)]
    decision=common('decision',decision_ref)
    decision['payload'].update(decision_maker_ref=principal_ref,subject_refs=[event['node_id']],
        selected_outcome='defer local fixture contest; retain unresolved residue',
        evidence_basis_refs=[item['ref'] for item in evidence]+[response_ref],declared_effect_refs=[effect_ref])
    decision['relation_refs']=[relation('relation.declares-effect-on','source','effect',effect_ref)]
    successor=copy.deepcopy(event)
    successor['successor_refs']=[]
    successor['evidence_refs']=list(event['evidence_refs'])+[response_ref]
    successor['payload'].update(response_state='responded',resolution_decision_ref=decision_ref,
        residue_refs=list(event['payload']['residue_refs'])+['residue:local-fixture-contest-awaiting-real-owner'])
    successor['claim_ceiling']='Locally signed deferred fixture successor. Original native candidate bytes retained separately; no actual owner decision.'
    effect=common('effect',effect_ref)
    effect['payload'].update(effect_kind='revise',subject_ref=event['node_id'],intended_state='candidate',
        effective_when='explicit local fixture resolution only; original source remains unchanged',
        verification_refs=[response_ref])
    effect['relation_refs']=[relation('relation.declares-effect-on','target','decision',decision_ref)]
    decision_scope=common('decision-scope',scope_ref)
    decision_scope['payload'].update(subject_refs=[event['node_id']],subject_kind_refs=['challenge-event'],
        permitted_effects=['revise'],excluded_effects=['canonical-admission','live-activation','work-completion','real-owner-decision'])
    decision_scope['relation_refs']=[relation('relation.scopes-authority-over','target','authority-claim',claim_ref)]
    authority_claim=common('authority-claim',claim_ref)
    authority_claim['payload'].update(claimant_ref=principal_ref,decision_scope_ref=scope_ref,
        authority_basis_refs=['fixture-signed-source:'+sha(canon(submission))],
        claimed_permissions=['prepare-local-fixture-challenge-successor'],
        limitations=['candidate-only','no-actual-owner-decision','no-repository-admission','no-activation'])
    authority_claim['relation_refs']=[relation('relation.scopes-authority-over','source','decision-scope',scope_ref)]
    bodies={'principal':principal,'principal-reference':principal_reference,'decision':decision,
        'effect':effect,'decision-scope':decision_scope,'authority-claim':authority_claim,'challenge-event':successor}
    for kind,body in bodies.items(): validate(kind,body)
    payload={'schema_version':'lab-local-Agent-contest-resolution-source/v1-fixture',
             'scope_ref':scope,'source_cut':submission['source_cut'],
             'native_api_source_sha256':API_SOURCE,
             'native_submission_sha256':sha(canon(submission)),
             'native_call_observation_sha256':sha(canon(observation)),
             'original_challenge_sha256':sha(candidate_raw),
             'response_sha256':sha(canon(response)),
             'member_sha256s':{kind:sha(canon(body)) for kind,body in bodies.items()},
             'fixture_principal_ref':principal_ref,'selected_fixture_outcome':'defer',
             'not_before':now.isoformat(),'expires_at':min(now+timedelta(hours=1),instant(period_end)).isoformat(),
             'actual_owner_outcome':None,'authority_effect':'none'}
    envelope={'payload':payload,'signature':base64.b64encode(key.sign(canon(payload))).decode()}
    del key
    source={'envelope':envelope,'issuer_public_hex':public.hex(),
            'original_challenge_base64':base64.b64encode(candidate_raw).decode(),
            'response':response,'members':bodies}
    verify(source,selected_public_hex=public.hex(),selected_submission_sha256=sha(canon(submission)),
           selected_source_cut=submission['source_cut'],now=now)
    return source

def verify(source,*,selected_public_hex,selected_submission_sha256,selected_source_cut,now):
    need(type(source) is dict and set(source)=={'envelope','issuer_public_hex','original_challenge_base64','response','members'},'closed fixture source required')
    need(source['issuer_public_hex']==selected_public_hex,'independently selected fixture signer differs')
    envelope=source['envelope'];need(set(envelope)=={'payload','signature'},'closed signed payload required')
    public=bytes.fromhex(selected_public_hex)
    Ed25519PublicKey.from_public_bytes(public).verify(base64.b64decode(envelope['signature'],validate=True),canon(envelope['payload']))
    p=envelope['payload']
    need(p['schema_version']=='lab-local-Agent-contest-resolution-source/v1-fixture'
         and p['scope_ref']==source['members']['challenge-event']['scope_ref']
         and p['native_submission_sha256']==selected_submission_sha256
         and p['source_cut']==selected_source_cut and p['native_api_source_sha256']==API_SOURCE
         and p['selected_fixture_outcome']=='defer' and p['actual_owner_outcome'] is None and p['authority_effect']=='none',
         'fixture source scope/lineage/outcome differs')
    need(instant(p['not_before'])<=now<instant(p['expires_at']),'fixture source expired or future')
    need(set(source['members'])==set(KINDS),'exact fixture member closure required')
    need(p['member_sha256s']=={kind:sha(canon(body)) for kind,body in source['members'].items()},'fixture member bytes changed')
    for kind,body in source['members'].items():
        validate(kind,body)
        need(body['scope_ref']==p['scope_ref'] and body['authority_effect']=='none' and body['lifecycle_state']=='candidate',
             'fixture member escapes scope or candidate state')
    original=base64.b64decode(source['original_challenge_base64'],validate=True)
    need(sha(original)==p['original_challenge_sha256']==ORIGINAL_CANDIDATE_SHA
         and sha(canon(selected_source_cut))==ORIGINAL_SOURCE_CUT_SHA,'native original/source cut changed')
    need(sha(canon(source['response']))==p['response_sha256'],'fixture response changed')
    original_body=frame(original);validate('challenge-event',original_body)
    response=source['response'];members=source['members'];owner=members['principal']
    need(original_body['scope_ref']==p['scope_ref']
         and response['subject']['identity_ref']==original_body['payload']['subject_ref']
         and response['subject']['version_ref']==original_body['payload']['subject_version_ref']
         and response['challenge_contract']['version_ref']==original_body['payload']['challenge_contract_ref'],
         'fixture response changed original source subject/Contract')
    need(owner['node_id']==p['fixture_principal_ref']
         and owner['payload']['stable_subject_ref']=='ed25519-public-key-sha256:'+sha(public)
         and response['responding_fixture_principal']==owner['node_id']
         and response['challenger_kind']=='agent-instance'
         and response['challenger_ref']==original_body['payload']['challenger_ref']
         and response['challenge_original_sha256']==sha(original)
         and response['selected_fixture_outcome']=='defer'
         and response['actual_owner_outcome'] is None and response['authority_effect']=='none',
         'fixture Agent/owner/response lineage differs')
    need(instant(original_body['payload']['submitted_at'])<=instant(response['responded_at'])<=now,'response clock differs')
    decision=members['decision'];effect=members['effect'];scope=members['decision-scope'];successor=members['challenge-event']
    need(decision['payload']['selected_outcome']=='defer local fixture contest; retain unresolved residue'
         and scope['payload']['excluded_effects']==['canonical-admission','live-activation','work-completion','real-owner-decision']
         and decision['payload']['decision_maker_ref']==owner['node_id']
         and decision['payload']['declared_effect_refs']==[effect['node_id']]
         and decision['payload']['subject_refs']==[original_body['node_id']]
         and effect['payload']['subject_ref']==original_body['node_id']
         and effect['payload']['effect_kind']=='revise' and effect['payload']['intended_state']=='candidate'
         and scope['payload']['subject_refs']==[original_body['node_id']]
         and scope['payload']['permitted_effects']==['revise']
         and successor['node_id']==original_body['node_id']
         and successor['payload']['resolution_decision_ref']==decision['node_id']
         and successor['payload']['response_state']=='responded'
         and successor['payload']['subject_version_ref']==original_body['payload']['subject_version_ref'],
         'fixture Decision/Effect/scope/successor differs')
    expected_successor=copy.deepcopy(original_body)
    expected_successor['successor_refs']=[]
    response_ref='response:local-fixture:'+sha(canon(response))
    expected_successor['evidence_refs']=list(original_body['evidence_refs'])+[response_ref]
    expected_successor['payload'].update(response_state='responded',resolution_decision_ref=decision['node_id'],
        residue_refs=list(original_body['payload']['residue_refs'])+['residue:local-fixture-contest-awaiting-real-owner'])
    expected_successor['claim_ceiling']='Locally signed deferred fixture successor. Original native candidate bytes retained separately; no actual owner decision.'
    need(successor==expected_successor,'fixture successor changed original candidate semantics')
    return True
