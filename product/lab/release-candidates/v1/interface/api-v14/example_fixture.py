"""Real selected Work candidate; exact original bytes and independent target cores."""
import copy
from .fixtures import *
from .handlers import cut

def materials_for(view,*,operation='admit',record_override=None,carrier_override=None):
    subjects=[s for s in view.subjects.values() if s['kind']=='work' and s['effective_state'] in ('admitted-current','local-admitted-current')]
    source.require(subjects,'selected exact Work source missing');prior=subjects[0]
    from .artifact_model import artifact_ref,carrier
    record=copy.deepcopy(prior['record']);identity='work:R03-exact-candidate-example'
    original_carrier=carrier(view,prior);identity_field=view.data['projection']['contracts'][original_carrier]['artifact'].get('instance_contract',{}).get('identity_field') or 'node_id'
    if operation=='admit':record[identity_field]=identity
    else:identity=prior['identity']
    record['name']='Inspect a complete candidate before its final owner decision'
    record['payload']['completion_state']='candidate-prepared'
    record['payload']['work_statement']='Prepare exact target/core/schema evidence and inspect unresolved references before the final owner checkpoint.'
    if 'scope_ref' in record:record['scope_ref']=view.data['config']['scope_ref']
    if record_override is not None:record=record_override
    version=identity+'@R03-preparation-1' if operation!='withdraw' else prior['version_ref']
    selected_carrier=carrier_override or carrier(view,prior)
    target={'category':'artifact-instance','operation':operation,'version_ref':version,'carrier_ref':selected_carrier,
        'record':record if operation!='withdraw' else None,'predecessor_ref':prior['version_ref'] if operation!='admit' else None,
        'decision_ref':'decision:R03-candidate-'+operation,'contract':None}
    core={'decision_ref':target['decision_ref'],'category':target['category'],'operation':operation,'version_ref':version,'target_digest':view.handle.common.digest(target)}
    metadata={'schema_version':'lab-candidate-target-metadata/v1-candidate','category':target['category'],'decision_ref':target['decision_ref'],'contract':None}
    # Whitespace in original material deliberately differs from JCS/control encoding.
    raw=(json.dumps(record,indent=3,ensure_ascii=False)+'\n').encode();metaraw=source.encoded(metadata);coreraw=view.handle.common.encoded(core)
    materials={'candidate:work-content':raw,'candidate:work-metadata':metaraw,'candidate:work-core':coreraw}
    selected={'ref':'candidate:work-metadata','sha256':source.sha(metaraw)}
    config=view.data['config'];contract=view.data['projection']['contracts'][selected_carrier]
    h={'scope_ref':config['scope_ref'],'identity_ref':identity,'version_ref':version,'carrier_ref':selected_carrier,'byte_sha256':source.sha(raw),
        'candidate_contract_binding':{'ref':contract['schema_path'],'sha256':contract['schema_sha256']}}
    if operation=='withdraw':h=artifact_ref(view,prior)
    api_target={'operation':operation,'artifact':h,'predecessor':artifact_ref(view,prior) if operation!='admit' else None,
        'content':{'content_ref':'candidate:work-content','byte_sha256':source.sha(raw),'size_bytes':len(raw),'media_type':'application/json'} if operation!='withdraw' else None,
        'candidate_binding':selected if operation!='withdraw' else None,'requested_effect':operation+' one exact Work revision after final owner authorization',
        'decision_core_binding':{'ref':'candidate:work-core','sha256':source.sha(coreraw)}}
    return materials,{version:selected},api_target

def candidate_call(service,target,operation='change.prepare',key='fixture:prepare'):
    context=service.channel.context;view=service.handlers.view
    c=call(context,'lab.status',cut(view));c['operation']=operation;c['idempotency_key']=key
    actor=c['message']['actor']
    c['message']={'schema_version':'lab-change-proposal/v1-candidate','proposal_ref':'proposal:R03-exact-work-candidate','actor':actor,
        'scope_ref':view.data['config']['scope_ref'],'base_cut':cut(view),
        'source_profile_binding':{'ref':view.handle.manifest['profile_binding']['path'],'sha256':view.handle.manifest['profile_binding']['sha256']},
        'workspace_binding':service.vault.control_binding,'targets':[copy.deepcopy(target)],'schema_bindings':[],'connection_proposals':[],
        'evidence_bindings':[],'idempotency_key':'fixture:prepare','challenge_route':view.data['config']['challenge_route'],'authority_effect':'none'}
    return c
