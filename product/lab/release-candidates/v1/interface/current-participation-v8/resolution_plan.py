"""Prepare an acyclic exact fixture plan while its new gate signer exists."""
import base64
import copy
import json
from datetime import datetime,timezone
from .base import *
from . import records as R, integration as I


def compact(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()


def make(store,handle,data,key,out):
    scope=data['config']['scope_ref'];head=data['head']['transaction_digest']
    original_projection_digest=handle.common.digest(data['projection'])
    workspace_ref='R03-Source6-resolution-'+data['config']['store_id']
    materials={};metadata={};objects={};source=data['projection']['subjects']
    def raw(ref):return handle.custody.original_bytes(store,ref,head)
    def header(ref):
        row=source[ref]
        return {'scope_ref':scope,'identity_ref':row['identity'],'version_ref':ref,
                'carrier_ref':row['carrier_ref'],'byte_sha256':sha(raw(ref))}
    def material(ref,value,original_bytes=None):
        selected=encoded(value) if original_bytes is None else original_bytes
        require(ref not in materials,'duplicate planned material')
        materials[ref]=selected
        return {'ref':ref,'sha256':sha(selected)}
    def object(value):
        selected=encoded(value);digest=sha(selected);objects[digest]=selected
        return {'ref':'workspace-object:'+workspace_ref+':'+digest,'sha256':digest}
    challenge=header(I.CHALLENGE+'@'+R.VERSION);contract=header(I.CONTRACT+'@'+R.VERSION)
    subject=header(R.WORK+'@'+R.VERSION);owner=header(I.OWNER+'@'+R.VERSION)
    evidence=header(I.EVIDENCE+'@'+R.VERSION)
    evidence_binding=material(evidence['version_ref'],None,raw(evidence['version_ref']))
    now=datetime.now(timezone.utc).isoformat()
    response={'schema_version':'lab-exact-challenge-response/v1-candidate','challenge':challenge,
        'challenge_contract':contract,'subject':subject,'owner_principal':owner,'response_mode':'evidence-and-revision',
        'responded_at':now,'evidence_bindings':[evidence_binding],'authority_effect':'none'}
    response_binding=material(I.RESPONSE,response)
    source_cut=cut(type('PlanView',(),{'data':data,'handle':handle})())
    routes=[];api_targets={}
    for axis in I.EFFECTS:
        prior=subject if axis=='semantic' else challenge
        body=copy.deepcopy(source[prior['version_ref']]['record'])
        if axis=='semantic':
            body['name']='Inspect exact policy custody before later independent operational acceptance'
            body['payload']['work_statement']='Preserve the authenticated Machine Actor and exact parent policy custodian when exercising the original bounded source-fact copy mechanism.'
        else:
            body['payload'].update(response_state='resolved-for-revision',resolution_decision_ref=I.DECISION+'@'+R.VERSION)
        original_bytes=encoded(body)
        target={'category':'artifact-instance','operation':'revise','version_ref':I.NEXT[axis],
            'carrier_ref':prior['carrier_ref'],'record':body,'predecessor_ref':prior['version_ref'],
            'decision_ref':'decision:'+R.PREFIX+':prospective-'+axis,'contract':None,
            'content':handle.custody.content_entry(original_bytes)}
        meta={'schema_version':'lab-candidate-target-metadata/v1-candidate','category':'artifact-instance',
              'decision_ref':target['decision_ref'],'contract':None}
        content=material('candidate:Source6:'+axis+':content',None,original_bytes)
        selected=material('candidate:Source6:'+axis+':metadata',meta)
        metadata[I.NEXT[axis]]=selected
        core={'decision_ref':target['decision_ref'],'category':target['category'],'operation':'revise',
              'version_ref':target['version_ref'],'target_digest':handle.common.digest(target)}
        core_binding=material('candidate:Source6:'+axis+':core',None,handle.common.encoded(core))
        candidate={**prior,'version_ref':target['version_ref'],'byte_sha256':sha(original_bytes),
            'candidate_contract_binding':{'ref':data['projection']['contracts'][prior['carrier_ref']]['schema_path'],
                'sha256':data['projection']['contracts'][prior['carrier_ref']]['schema_sha256']}}
        api_targets[axis]={'operation':'revise','artifact':candidate,'predecessor':prior,
            'content':{'content_ref':content['ref'],'byte_sha256':content['sha256'],'size_bytes':len(original_bytes),'media_type':'application/json'},
            'candidate_binding':selected,'requested_effect':I.EFFECT_KINDS[axis],'decision_core_binding':core_binding}
        routes.append({'axis':axis,'effect':header(I.EFFECTS[axis]+'@'+R.VERSION),
            'target_version_ref':target['version_ref'],'decision_scope':header(I.SCOPES[axis]+'@'+R.VERSION)})
        config=data['config']
        native={'schema_version':'lab-runtime-proposal/v1','proposal_id':'R03-Source6-prospective-'+axis,
            'expected_head':head,'source_snapshot_digest':config['source_snapshot_digest'],'scope_ref':scope,
            'policy_ref':config['policy_ref'],'challenge_route':config['challenge_route'],'schemas':{},'targets':[target]}
        native=handle.custody.with_originals(native,{target['version_ref']:original_bytes},{},exact_schema_bytes=True)
        _,cores=handle.operations.prepare(data['projection'],native,head,config)
        require(cores==[core],'prospective declared core differs from native calculation')
        emit(out/('resolution-native-'+axis+'.json'),native)
    rows=[]
    for index,(ref,original_bytes) in enumerate(materials.items()):
        path='inputs/input_'+str(index)+'.json';rows.append({'ref':ref,'path':path,'sha256':sha(original_bytes)})
        emit(out/('qualification-workspace/'+path),None,raw=original_bytes)
    manifest={'schema_version':'lab-owned-candidate-workspace/v1-candidate','workspace_ref':workspace_ref,
        'principal_ref':I.OWNER,'scope_refs':[scope],'materials':rows,'target_metadata':metadata,
        'authority_effect':'none','actual_owner_outcome':None}
    emit(out/'qualification-workspace/workspace.json',manifest)
    workspace_binding={'ref':'workspace:'+workspace_ref,'sha256':sha(encoded(manifest))}
    actor={'principal_ref':I.OWNER,'agent_instance_ref':None,'assignment_ref':None,'session_ref':None,'role_assignment_refs':[]}
    common={'schema_version':'lab-change-proposal/v1-candidate','actor':actor,'scope_ref':scope,'base_cut':source_cut,
        'source_profile_binding':{'ref':handle.manifest['profile_binding']['path'],'sha256':handle.manifest['profile_binding']['sha256']},
        'workspace_binding':workspace_binding,'schema_bindings':[],'connection_proposals':[],
        'evidence_bindings':[evidence_binding],'idempotency_key':'Source6:exact-controlled-resolution',
        'challenge_route':data['config']['challenge_route'],'authority_effect':'none'}
    branch_bindings={axis:object({**common,'proposal_ref':'proposal:'+R.PREFIX+':'+axis,'targets':[api_targets[axis]]}) for axis in I.EFFECTS}
    result_binding=object({**common,'proposal_ref':'proposal:'+R.PREFIX+':composed',
                          'targets':[api_targets[axis] for axis in I.EFFECTS]})
    obligations={**I.ROUTES,'response_seconds':300,'response_mode':'evidence-and-revision',
        'response_binding':response_binding,'challenger':owner,
        'accepted_evidence':[{'binding':evidence_binding,'artifact':evidence,'kind':'evidence-set'}]}
    episode_value=episode()
    payload={'schema_version':'lab-exact-challenge-resolution-gate/v1-candidate',
        'gate_ref':I.ROUTES['resolution_gate_ref'],'principal_ref':I.OWNER,'owner_route':I.ROUTES['owner_route'],
        'scope_ref':scope,'source_cut':source_cut,'challenge':challenge,'resolution_decision':header(I.DECISION+'@'+R.VERSION),
        'challenge_contract':contract,'subject':subject,'selected_outcome':I.OUTCOME,
        'semantic_proposal_binding':branch_bindings['semantic'],'governance_proposal_binding':branch_bindings['governance'],
        'evidence_bindings':[evidence_binding],'consequence_routes':routes,'response_obligations':obligations,
        'not_before':episode_value['not_before'],'expires_at':episode_value['expires_at'],
        'permitted_effects':['prepare-exact-challenge-consequences'],
        'excluded_effects':['canonical-admission','live-activation','tool-dispatch','challenged-subject-overwrite'],
        'authority_effect':'none'}
    signed={'payload':payload,'signature':base64.b64encode(key.sign(compact(payload))).decode()}
    gate_binding=object(signed)
    routing={'schema_version':'lab-challenge-resolution-routing/v1-candidate','source_cut':source_cut,'scope_ref':scope,
        'challenge_contract':contract,'subject':subject,'owner_principal':owner,
        'owner_public_key_hex':key.public_key().public_bytes_raw().hex(),'owner_gate_binding':gate_binding,
        'semantic_proposal_binding':branch_bindings['semantic'],'governance_proposal_binding':branch_bindings['governance'],
        'result_proposal_binding':result_binding,'consequence_routes':routes,'response_obligations':obligations,
        'authorization_basis_binding':{'ref':episode_value['authorization_binding']['path'],
            'sha256':episode_value['authorization_binding']['sha256']},'authority_effect':'none','actual_owner_outcome':None}
    routing_binding=object(routing)
    for digest,original_bytes in objects.items():emit(out/('qualification-workspace/objects/'+digest+'.json'),None,raw=original_bytes)
    message={'schema_version':'lab-challenge-resolution/v1-candidate','challenge':challenge,
        'resolution_decision':payload['resolution_decision'],'source_cut':source_cut,
        'evidence_bindings':[evidence_binding],'semantic_change_proposal_binding':branch_bindings['semantic'],
        'governance_change_proposal_binding':branch_bindings['governance'],'unresolved_gaps':[],'authority_effect':'none'}
    emit(out/'resolution-qualification-plan.json',{'schema_version':'lab-owned-resolution-qualification-plan/v1-candidate',
        'routing_binding':routing_binding,'workspace_binding':workspace_binding,'message':message,
        'idempotency_key':common['idempotency_key'],'principal_ref':I.OWNER,'source_cut':source_cut,
        'gate_public_key_hex':routing['owner_public_key_hex'],'development_only':True,'actual_owner_outcome':None,
        'private_keys_exported':False,'public_handler_qualified':False,'authority_effect':'none'})
    current=store.replay(require_current=True)
    require(current['head']['transaction_digest']==head
            and handle.common.digest(current['projection'])==original_projection_digest==handle.common.digest(data['projection']),
            'pure resolution plan changed signed source or projection')
    return {'message':message,'routing':routing,'gate':signed,'workspace_binding':workspace_binding}
