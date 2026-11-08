"""New owned candidate snapshots over exact retained native contest evidence.

An old signed capsule proves historical fixture response lineage only. A fresh,
independently selected metadata grant and Source guard authorize this factory.
The Decision/v2 is a new derived record, never a relabeled native Decision/v1.
"""
import base64
import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
NATIVE=Path.home()/'.local/share/cyberalchemy-lab/t22-native-agent-diagnostics/91755e756e7543e6a42e664fafa744b2'
RESOLVED=Path.home()/'.local/share/cyberalchemy-lab/t22-fixture-resolution-diagnostics/16e331f232bf44f68cf669d159bd2649'
PUBLIC=ROOT/'implementation/lab-runtime/local-host/t22-native-agent-contest-0001'
PINS={'native-candidate':('candidate.json','71be1ed90197329e7405bd3ad709721a440d8617b19076edc396f3bd4767d9e8'),
      'native-request':('request.json','b8bce552c5a1866a652543885bf523a7774f5cda8959f13586356ace3ab380b6'),
      'signed-capsule':('source-capsule.json','4299492e2870824db450d2c78ec00b47242d14af5d5df234007488f2e696dda1'),
      'native-proposal':('native-proposal.json','9f9ee6b7ad10e0558fb39a2c5770680396c71f57f9d60d768f229b50b43818fc'),
      'submission-receipt':('LIVE-NATIVE-AGENT-COLD-API71-0001.json','ac9bb4baa9a295cab8b6cbbb80a2ed16b350c36786677c602350f5dc25284cf4'),
      'submission-observation':('NATIVE-AGENT-COLD-CALL-API71-0002.json','acbacb89c0c69adc3fd02c1d29a3208cc30c1ee37b9fffda7eeb31c49aac7970'),
      'resolution-receipt':('LIVE-NATIVE-FIXTURE-RESOLUTION-API73-0002.json','844957985468e691789a957053b2d60fbeab82ec229072ec1063417816e9e5d2')}
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def instant(v):
    d=datetime.fromisoformat(v.replace('Z','+00:00'));need(d.tzinfo is not None,'aware UTC required');return d
def schema(kind,version):
    folder=ROOT/'authority/artifact-types'/kind/version
    if kind=='decision' and version=='v2':folder=ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/decision/v2'
    return folder
def selected_originals():
    originals={}
    for label,(name,digest) in PINS.items():
        parent=PUBLIC if label in ('submission-receipt','submission-observation','resolution-receipt') else (NATIVE if label in ('native-candidate','native-request') else RESOLVED)
        path=parent/name
        raw=path.read_bytes();need(sha(raw)==digest,'independent actual original changed: '+label);originals[label]=raw
    return originals
def historical(originals):
    need(set(originals)==set(PINS),'closed actual native input set required')
    for label,raw in originals.items():need(sha(raw)==PINS[label][1],'independent actual original changed: '+label)
    original=json.loads(originals['native-candidate']);request=json.loads(originals['native-request']);capsule=json.loads(originals['signed-capsule']);proposal=json.loads(originals['native-proposal'])
    payload=capsule['envelope']['payload'];public=bytes.fromhex(capsule['issuer_public_hex'])
    submitted=json.loads(originals['submission-receipt']);observed=json.loads(originals['submission-observation']);resolved=json.loads(originals['resolution-receipt'])
    need(submitted['result']=='PASS' and submitted['challenge_submitted'] is True and submitted['challenge_resolved'] is False
         and submitted['owner_decision'] is None and payload['native_submission_sha256']==sha(enc(submitted))
         and payload['native_call_observation_sha256']==sha(enc(observed))
         and submitted['source_cut']==observed['source_cut']==request['source_cut']
         and submitted['challenge_response_sha256']==observed['reply_sha256'] and observed['reply_kind']=='result',
         'actual successful native submission/observation closure differs')
    need(resolved['result']=='PASS' and resolved['fixture_source_sha256']==sha(originals['signed-capsule'])
         and resolved['native_proposal_sha256']==sha(originals['native-proposal'])
         and resolved['candidate_response_state']=='deferred' and resolved['actual_owner_outcome'] is None,
         'actual native resolution terminal evidence differs')
    Ed25519PublicKey.from_public_bytes(public).verify(base64.b64decode(capsule['envelope']['signature'],validate=True),enc(payload))
    need(payload['member_sha256s']=={k:sha(enc(v)) for k,v in capsule['members'].items()},'historical signed member closure changed')
    need(payload['response_sha256']==sha(enc(capsule['response'])) and payload['original_challenge_sha256']==sha(originals['native-candidate'])
         and base64.b64decode(capsule['original_challenge_base64'],validate=True)==originals['native-candidate']
         and enc(capsule['original_request'])==originals['native-request'],'historical original/request/response lineage differs')
    need(capsule['response']['selected_fixture_outcome']=='defer' and capsule['response']['actual_owner_outcome'] is None
         and payload['selected_fixture_outcome']=='defer' and payload['actual_owner_outcome'] is None,'historical fixture outcome differs')
    target=proposal['targets'][0]
    need(len(proposal['targets'])==1 and target['predecessor']['byte_sha256']==sha(originals['native-candidate'])
         and target['artifact']['byte_sha256']==sha(enc(capsule['members']['challenge-event']))
         and capsule['members']['challenge-event']['payload']['response_state']=='deferred','actual native defer proposal differs')
    need(instant(original['payload']['submitted_at'])<=instant(capsule['response']['responded_at'])<=datetime.now(timezone.utc),
         'historical response is future or precedes actual submission')
    return original,request,capsule,proposal
def derive(*,originals,contract_raw,grant,host_guard,run_ref):
    """Construct fresh local metadata outputs under an independent current grant."""
    host_guard();original,request,capsule,proposal=historical(originals)
    now=datetime.now(timezone.utc)
    need(grant['authority_effect']=='none' and grant['actual_owner_outcome'] is None and grant['revoked'] is False
         and grant['source_cut']==request['source_cut'] and grant['scope_ref']==original['scope_ref']
         and grant['run_ref']==run_ref and grant['permitted_effects']==['candidate-workflow-transition']
         and 'role:accountable-owner' in grant['actor_role_refs']
         and instant(grant['not_before'])<=now<instant(grant['expires_at']), 'fresh independently selected fixture metadata owner grant required')
    need(sha(contract_raw)==request['challenge_contract']['byte_sha256'],'current actual Contract original differs')
    contract=json.loads(contract_raw)
    need(contract['node_id']==request['challenge_contract']['identity_ref'] and original['payload']['ground'] in contract['payload']['grounds']
         and 'agent-instance' in contract['payload']['eligible_challenger_kinds'] and 'work' in contract['payload']['challengeable_subject_kinds']
         and capsule['response']['response_mode'] in contract['payload']['response_modes'],
         'actual Contract does not cover retained native challenge')
    seed=sha(enc({'run':run_ref,'originals':{k:sha(v) for k,v in originals.items()},'grant':grant}))[:24]
    decision_id='decision:owned-native-contest:'+seed;decision_ref=decision_id+'@derived-v2.1'
    effect_id='effect:owned-native-contest:'+seed;effect_ref=effect_id+'@derived.1'
    evidence='native-contest-historical-proof:'+sha(originals['signed-capsule'])
    records={};headers={};raws={};scope=original['scope_ref'];principal=grant['principal_ref']
    def put(label,body,kind,version,ref):
        folder=schema(kind,version);Draft202012Validator(json.loads((folder/'schema.json').read_bytes())).validate(body)
        raw=enc(body);header={'scope_ref':scope,'identity_ref':body['node_id'],'version_ref':ref,'carrier_ref':'cal.artifact-type.'+kind+'/'+version,'byte_sha256':sha(raw)}
        records[label]=body;headers[label]=header;raws[ref]=raw
    for phase,state in [('eligible','eligible'),('responded','responded'),('resolved','deferred')]:
        body=copy.deepcopy(original);body['name']='Owned retained native contest '+phase;body['owner_ref']=principal
        body['claim_ceiling']='New private fixture metadata snapshot over retained actual native evidence. No current Agent capability, actual owner outcome, Source admission or accepted/rejected contest outcome.'
        body['evidence_refs']=[*body['evidence_refs'],evidence]
        body['payload']['response_state']=state
        if phase!='eligible':body['payload']['evidence_refs']=[*body['payload']['evidence_refs'],'response:local-fixture:'+sha(enc(capsule['response']))]
        if phase=='resolved':body['payload'].update(resolution_decision_ref=decision_ref,residue_refs=['residue:local-fixture-contest-awaiting-real-owner'])
        put(phase,body,'challenge-event','v1',body['node_id']+'@owned-'+phase+'.'+seed)
    decision=json.loads((schema('decision','v2')/'fixtures/valid/record.json').read_bytes())
    decision.update(node_id=decision_id,name='Derived retained native fixture defer Decision/v2',owner_ref=principal,scope_ref=scope,
      lifecycle_state='candidate',evidence_refs=[evidence],successor_refs=[],claim_ceiling='New Decision/v2 factory output under current fixture metadata owner grant, not native Decision/v1 relabel or actual owner decision.')
    decision['payload'].update(decision_maker_ref=principal,subject_refs=[headers['resolved']['version_ref']],
      selected_outcome='defer local fixture contest; retain unresolved residue',declared_effect_refs=[effect_ref],evidence_basis_refs=[evidence])
    decision['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'source','counterpart_kind':'effect','counterpart_ref':effect_ref}]
    put('decision',decision,'decision','v2',decision_ref)
    effect=json.loads((schema('effect','v1')/'fixtures/valid/record.json').read_bytes())
    effect.update(node_id=effect_id,name='Owned fixture deferred snapshot effect',owner_ref=principal,scope_ref=scope,lifecycle_state='candidate',evidence_refs=[evidence],successor_refs=[],
      claim_ceiling='Private coordination declaration only; performs no Source revision or admission.')
    effect['payload'].update(effect_kind='revise',subject_ref=headers['resolved']['version_ref'],intended_state='deferred-fixture-metadata',effective_when='Only scoped owned workflow commit; actual owner outcome remains absent.',verification_refs=[evidence])
    effect['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'target','counterpart_kind':'decision','counterpart_ref':decision_ref}]
    put('effect',effect,'effect','v1',effect_ref)
    host_guard()
    provenance={'schema_version':'lab-owned-native-contest-factory/v1','observed_at':now.isoformat(),'source_cut':grant['source_cut'],'scope_ref':scope,'coordinating_principal':principal,
      'run_ref':run_ref,'input_bindings':{k:sha(v) for k,v in originals.items()},'current_contract_sha256':sha(contract_raw),'current_metadata_grant_sha256':sha(enc(grant)),
      'factory_code_sha256':sha(Path(__file__).read_bytes()),'outputs':headers,'private_effect':headers['effect'],
      'historical_signature_valid':True,'historical_capsule_period_is_not_current_permission':True,
      'old_native_decision_schema':capsule['members']['decision']['schema_version'],'new_decision_schema':decision['schema_version'],
      'new_decision_is_distinct_record':decision['node_id']!=capsule['members']['decision']['node_id'],'selected_fixture_outcome':'defer','actual_owner_outcome':None,
      'fixture_owner_obligation':'Exact current authenticated fixture metadata-owner grant, retaining signed historical defer; not real Vlad/repository-owner authority.',
      'canonical_admissions':0,'authority_effect':'none'}
    return headers,raws,provenance
