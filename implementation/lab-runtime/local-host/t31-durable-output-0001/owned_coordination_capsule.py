"""Schema-validated private coordination facts over actual native source inputs.

These are scoped local fixture candidates. They are never Source admissions,
real owner outcomes, or permission to continue a closed runtime Session.
"""
import base64,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def fixture(kind,version='v1'):
    if kind=='decision' and version=='v2':folder=ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/decision/v2'
    elif kind=='typed-relation' and version=='v3':folder=ROOT/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3'
    else:folder=ROOT/'authority/artifact-types'/kind/version
    return json.loads((folder/'fixtures/valid/record.json').read_bytes()),folder/'schema.json'
def build(emission,*,run_ref,principal_ref,scope_ref):
    from jsonschema import Draft202012Validator
    need(emission['scope_ref']==scope_ref and emission['principal_ref']==principal_ref
         and emission['WorkflowRun_committed'] is False,'actual native producer scope/Principal required')
    inputs={row['origin']['semantic_kind']:row for row in emission['coordination_inputs']}
    need(set(inputs)=={'intent','work','goal','coordination-context','agent-assignment','context-request'},'exact native coordination input set required')
    bodies={}
    for kind,row in inputs.items():
        raw=base64.b64decode(row['private_original_base64'],validate=True)
        need(sha(raw)==row['sha256']==row['artifact']['byte_sha256'] and row['artifact']['scope_ref']==scope_ref,'native input original/header differs')
        bodies[kind]=json.loads(raw)
    work,goal,coord,assignment=(bodies[k] for k in ('work','goal','coordination-context','agent-assignment'))
    need(coord['project_ref']==scope_ref and coord['goal_ref']==inputs['goal']['artifact']['version_ref']
         and coord['goal_ref'] in work['payload']['goal_refs']
         and assignment['payload']['work_ref']==inputs['work']['artifact']['version_ref']
         and assignment['payload']['intent_ref']==inputs['intent']['artifact']['version_ref'],
         'actual native Work/Goal/Intent/Assignment coordination does not close')
    seed=sha(encoded({'run':run_ref,'emission':emission}))[:20]
    ids={k:k+':owned-fixture:'+seed for k in ('intent-resolution','decision','effect','delegation','typed-relation')}
    refs={k:v+'@owned-coordination.1' for k,v in ids.items()}
    result={};schemas={}
    for kind,version in [('intent-resolution','v1'),('decision','v2'),('effect','v1'),('delegation','v1'),('typed-relation','v3')]:
        body,schema=fixture(kind,version);body.update(node_id=ids[kind],owner_ref=principal_ref,scope_ref=scope_ref,
          lifecycle_state='candidate',relation_refs=[],successor_refs=[],evidence_refs=['native-first-emitter:'+sha(encoded(emission))],
          claim_ceiling='Owned fixture workflow coordination only; not Source-current, canonical admission, actual owner outcome, runtime continuation or Work completion.')
        result[kind]=body;schemas[kind]=(version,schema)
    result['intent-resolution']['payload'].update(intent_ref=inputs['intent']['artifact']['version_ref'],
      selected_subject_refs=[inputs[k]['artifact']['version_ref'] for k in ('work','goal','coordination-context')],
      excluded_subject_refs=[],owner_decision_ref=refs['decision'],satisfaction_test_refs=['owned-workflow:'+run_ref])
    result['decision']['payload'].update(decision_maker_ref=principal_ref,subject_refs=[refs['intent-resolution']],
      selected_outcome='Coordinate exact private fixture WorkflowRun; no admission or Work completion.',
      declared_effect_refs=[refs['effect']],evidence_basis_refs=['native-first-emitter:'+sha(encoded(emission))])
    result['effect']['payload'].update(effect_kind='lifecycle-transition',subject_ref=refs['intent-resolution'],
      intended_state='owned-coordination-current',effective_when='Independently current owned workflow grant and exact native provenance validate.',
      verification_refs=['owned-workflow:'+run_ref])
    # The authenticated Reader operator coordinates the retained observations.
    # This private delegation authorizes that fixture metadata role only.
    result['delegation']['payload'].update(delegator_principal_ref=principal_ref,eligible_agent_ref=principal_ref,
      scope_refs=[scope_ref],allowed_action_kinds=['candidate-workflow-transition'],policy_refs=['owned-workflow:'+run_ref],
      effective_period='owned-workflow:'+run_ref,approval_gate_refs=[],redelegation_allowed=False,revocation_state='not-revoked')
    result['delegation']['claim_ceiling']+=' Eligible actor is the authenticated Reader operator in this private profile; it confers no runtime Machine capability.'
    result['typed-relation']['payload'].update(relation_kind_ref='relation.declares-effect-on',
      source={'kind':'decision','ref':ids['decision'],'version_ref':refs['decision']},
      target={'kind':'intent-resolution','ref':ids['intent-resolution'],'version_ref':refs['intent-resolution']},
      qualifiers={'effect_kind':'lifecycle-transition','exact_target_version_ref':refs['intent-resolution']},relation_evidence_refs=['owned-workflow:'+run_ref])
    result['intent-resolution']['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'target',
      'counterpart_kind':'decision','counterpart_ref':refs['decision']}]
    result['decision']['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'source',
      'counterpart_kind':'intent-resolution','counterpart_ref':refs['intent-resolution']}]
    for kind in ('effect','delegation'):
        result[kind]['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'target',
          'counterpart_kind':'decision','counterpart_ref':refs['decision']}]
    artifacts={};raws={}
    for kind,body in result.items():
        version,schema=schemas[kind];Draft202012Validator(json.loads(schema.read_bytes())).validate(body)
        raw=encoded(body);raws[refs[kind]]=raw;artifacts[kind]={'scope_ref':scope_ref,'identity_ref':ids[kind],
          'version_ref':refs[kind],'carrier_ref':'cal.artifact-type.'+kind+'/'+version,'byte_sha256':sha(raw)}
    need(result['intent-resolution']['payload']['owner_decision_ref']==artifacts['decision']['version_ref']
         and result['decision']['payload']['subject_refs']==[artifacts['intent-resolution']['version_ref']]
         and result['decision']['payload']['declared_effect_refs']==[artifacts['effect']['version_ref']]
         and result['effect']['payload']['subject_ref']==artifacts['intent-resolution']['version_ref'],
         'private coordination IR/Decision/Effect semantics differ')
    capsule={'schema_version':'lab-private-owned-coordination-capsule/v1-fixture','run_ref':run_ref,
      'scope_ref':scope_ref,'principal_ref':principal_ref,'source_cut':emission['source_cut'],
      'native_producer_receipt_sha256':sha(encoded(emission)),'inputs':inputs,'artifacts':artifacts,
      'records':result,'schema_bindings':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())} for _,p in schemas.values()],
      'authority_effect':'none','actual_owner_outcome':None}
    return capsule,raws
