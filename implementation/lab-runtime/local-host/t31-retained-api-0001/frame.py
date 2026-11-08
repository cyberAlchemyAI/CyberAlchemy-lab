"""Private candidate coordination over exact current Source Work/Goal inputs.

No original Work, Goal, source cut, or current source edge is rewritten. New
IR/Decision/Effect declarations authorize only this owned metadata Run.
"""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator

def need(value,message):
    if not value:raise ValueError(message)
def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def construct(*,root,inputs,source_cut,principal,run_ref):
    root=Path(root);need(set(inputs)=={'intent','work','goal','coordination','goal_project','project'},'exact current Source coordination input set required')
    records={};headers={}
    for key,(header,raw) in inputs.items():
        need(type(raw)is bytes and sha(raw)==header['byte_sha256'],'exact current Source input original/header differs')
        body=json.loads(raw)
        identity=next((body[name] for name in ('node_id','goal_id','coordination_context_id','project_id') if name in body),None)
        need(identity==header['identity_ref'] and header['version_ref'].startswith(identity+'@')
             and len(header['version_ref'])>len(identity)+1,'exact Source input identity/header differs')
        if 'version' in body:need(header['version_ref']==identity+'@'+body['version'],'exact Source input version/header differs')
        headers[key]=copy.deepcopy(header);records[key]=body
    scope=headers['project']['identity_ref'];work=records['work'];coord=records['coordination'];edge=records['goal_project']
    need(all(header['scope_ref']==scope for header in headers.values()),'exact Source input scope differs')
    need(headers['project']['scope_ref']==scope and work['payload']['project_ref']==coord['project_ref']==scope
         and coord['goal_ref']==headers['goal']['version_ref'] and coord['goal_ref'] in work['payload']['goal_refs'],
         'actual current Work/Goal/Coordination Project meaning differs')
    need(edge['payload']['relation_kind_ref']=='relation.member-of'
         and edge['payload']['source']['version_ref']==headers['goal']['version_ref']
         and edge['payload']['target']['version_ref']==headers['project']['version_ref'],
         'actual current Goal/Project relationship differs')
    seed=sha(enc({'run_ref':run_ref,'source_cut':source_cut,'inputs':headers}))[:24]
    refs={k:k+':current-private-workflow:'+seed+'@candidate.1' for k in ('intent-resolution','decision','effect','declared-effect')}
    bodies={};schemas={}
    for label,kind,version in [('intent-resolution','intent-resolution','v1'),('decision','decision','v2'),('effect','effect','v1'),('declared-effect','typed-relation','v3')]:
        folder=root/'authority/artifact-types'/kind/version
        if not (folder/'schema.json').is_file():folder=root/'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors'/kind/version
        body=json.loads((folder/'fixtures/valid/record.json').read_bytes());body.update(node_id=refs[label].rsplit('@',1)[0],owner_ref=principal,scope_ref=scope,
            lifecycle_state='candidate',successor_refs=[],relation_refs=[],evidence_refs=['current-source-input-observation:'+seed],
            claim_ceiling='Private owned workflow coordination over exact current Source originals only. No Source admission, original Work completion or actual owner outcome.')
        bodies[label]=body;schemas[label]=(kind,version,json.loads((folder/'schema.json').read_bytes()))
    bodies['intent-resolution']['payload'].update(intent_ref=headers['intent']['version_ref'],selected_subject_refs=[headers[k]['version_ref'] for k in ('work','goal','coordination')],
        excluded_subject_refs=['canonical-admission','live-store-mutation','external-effects'],owner_decision_ref=refs['decision'],satisfaction_test_refs=['private-owned-workflow:'+run_ref])
    bodies['decision']['payload'].update(decision_maker_ref=principal,subject_refs=[refs['intent-resolution']],selected_outcome='Coordinate exact local candidate workflow evidence only.',
        declared_effect_refs=[refs['effect']],evidence_basis_refs=['current-source-input-observation:'+seed])
    bodies['effect']['payload'].update(effect_kind='lifecycle-transition',subject_ref=refs['intent-resolution'],intended_state='owned-coordination-current',
        effective_when='Exact independently current Reader metadata grant and private workflow profile validate.',verification_refs=['private-owned-workflow:'+run_ref])
    bodies['intent-resolution']['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'target','counterpart_kind':'decision','counterpart_ref':refs['decision']}]
    bodies['decision']['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'source','counterpart_kind':'intent-resolution','counterpart_ref':refs['intent-resolution']}]
    bodies['effect']['relation_refs']=[{'relation_kind_ref':'relation.declares-effect-on','direction':'target','counterpart_kind':'decision','counterpart_ref':refs['decision']}]
    bodies['declared-effect']['payload'].update(relation_kind_ref='relation.declares-effect-on',
        source={'kind':'decision','ref':bodies['decision']['node_id'],'version_ref':refs['decision']},
        target={'kind':'intent-resolution','ref':bodies['intent-resolution']['node_id'],'version_ref':refs['intent-resolution']},
        qualifiers={'effect_kind':'lifecycle-transition','exact_target_version_ref':refs['intent-resolution']},relation_evidence_refs=['current-source-input-observation:'+seed])
    outputs={};raws={}
    for label,body in bodies.items():
        kind,version,schema=schemas[label];Draft202012Validator(schema).validate(body);raw=enc(body)
        outputs[label]={'scope_ref':scope,'identity_ref':body['node_id'],'version_ref':refs[label],'carrier_ref':'cal.artifact-type.'+kind+'/'+version,'byte_sha256':sha(raw)};raws[refs[label]]=raw
    capsule={'schema_version':'lab-private-current-Source-workflow-frame/v1','source_cut':copy.deepcopy(source_cut),'principal_ref':principal,'run_ref':run_ref,
        'scope_ref':scope,'source_headers':headers,'private_artifacts':outputs,'private_records':bodies,
        'original_Work_Goal_or_Source_bytes_rewritten':False,'Source_graph_effect':'none','actual_owner_outcome':None,'authority_effect':'none'}
    return capsule,raws
