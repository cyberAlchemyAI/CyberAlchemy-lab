"""Hypothetical states and byte-bound moves for candidate review."""
import copy
import pilot_spec as p


def info(value=None,state='known',scope=None):return {'state':state,'value':value,'scope_ref':scope}


def base_state(mode='unknown'):
    context={'scope':'scope:pilot-local-use','principal':'principal:hypothetical-reviewer','surface':'surface:pilot-rules','object':'artifact:import-review','operation':'count-as-local-rule','effect':'permitted-local-use'}
    value={'knowledge':'unknown','trail_status':'unavailable','steps':None,'scope_ref':None}
    state={'schema_version':p.PROFILE,'authority_effect':'none','object_id':context['object'],'revision':'state:before','context':context,'posture':{key:info(value) for key,value in zip(p.SOURCE_AXES,['rule','candidate','unassessed','proposed',None,'role:rule-owner','none'])},'provenance':value,'claims':[],'grants':[],'responsibilities':[],'role_bindings':[{'binding_id':'binding:rule-owner','principal':context['principal'],'owner_role':'role:rule-owner'}],'boundaries':[{'boundary_id':'boundary:rule-owner','owner_role':'role:rule-owner','principal_binding':context['principal'],'scope':context['scope'],'allowed_objects':[context['object']],'allowed_effects':[context['effect']],'excluded_effects':[],'challenge_route':'role:rule-challenge'}]}
    set_provenance(state,mode);return state


def set_provenance(state,mode):
    step={'kind':'typed','step_id':'step:import','source_ref':'source:hypothetical-rule-v1','relation_ref':'relation.derived-from','operation_ref':'operation.import-for-review','owner_ref':'role:source-owner','posture_ref':'posture:source-local'}
    gap={'kind':'gap','step_id':'step:missing','residue_ref':'residue:hypothetical-import-gap','owner_route':'role:lineage-reviewer'}
    choices={'unknown':{'knowledge':'unknown','trail_status':'unavailable','steps':None,'scope_ref':None},'deferred':{'knowledge':'deferred','trail_status':'unavailable','steps':None,'scope_ref':None},'empty':{'knowledge':'known','trail_status':'empty','steps':[],'scope_ref':None},'complete':{'knowledge':'known','trail_status':'complete','steps':[step],'scope_ref':None},'incomplete':{'knowledge':'known','trail_status':'incomplete','steps':[step,gap],'scope_ref':None},'source-local':{'knowledge':'source-local','trail_status':'complete','steps':[step],'scope_ref':state['context']['scope']}}
    state['provenance']=copy.deepcopy(choices[mode]);value=state['provenance'];state['posture']['provenance']=info(value['trail_status'] if value['knowledge'] in {'known','source-local'} else None,value['knowledge'],value['scope_ref'])


def right(state,grant=True,claim=True):
    fields={**state['context'],'owner_role':'role:rule-owner','basis':'decision:hypothetical-owner-act','challenge_route':'role:rule-challenge'}
    if grant:state['grants'].append({'grant_id':'grant:local-use',**fields,'boundary_ref':'boundary:rule-owner','role_binding_ref':'binding:rule-owner'})
    if claim:state['claims'].append({'claim_id':'claim:local-use','position_kind':'right','assignment_ref':'grant:local-use',**fields})
    return state


def responsibility(state,claim=True):
    context=state['context'];duty={'assignment_id':'duty:route-review','owner_role':'role:rule-owner','principal':context['principal'],'scope':context['scope'],'object':context['object'],'operation':context['operation'],'outcome':context['effect'],'owner_route':'role:rule-challenge','basis':'decision:hypothetical-duty-assignment','role_binding_ref':'binding:rule-owner'}
    state['responsibilities'].append(duty)
    if claim:state['claims'].append({'claim_id':'claim:duty','position_kind':'responsibility','assignment_ref':duty['assignment_id'],**context,'owner_role':duty['owner_role'],'basis':duty['basis'],'challenge_route':duty['owner_route']})
    return state


def move(before,after,intended=('provenance',),recorded=()):
    def assignments(left,right,identity):return [{identity:key,'before_sha256':value[0],'after_sha256':value[1],'basis_ref':'decision:hypothetical-explicit-assignment-change'} for key,value in sorted(p.deltas(left,right,identity).items())]
    return {'move_id':'move:hypothetical-transition','subject_id':before['object_id'],'context':copy.deepcopy(before['context']),'before_ref':{'revision':before['revision'],'sha256':p.ir.digest(before)},'after_ref':{'revision':after['revision'],'sha256':p.ir.digest(after)},'intended_axes':list(intended),'recorded_changes':[{'axis':axis,'before_sha256':p.ir.digest(p.component(before,axis)),'after_sha256':p.ir.digest(p.component(after,axis)),'basis_ref':'decision:hypothetical-explicit-coupling'} for axis in recorded],'grant_changes':assignments(before['grants'],after['grants'],'grant_id'),'responsibility_changes':assignments(before['responsibilities'],after['responsibilities'],'assignment_id')}


def worked():
    states=[]
    for mode in ['empty','unknown','deferred','complete','incomplete','source-local']:
        state=base_state(mode);states.append({'case_id':'provenance-'+mode,'scenario':'Hypothetical imported rule with '+mode+' origin information; neither source recording nor uncertainty grants a permission.','state':state,'actual':p.inspect_state(state,'admission-use-requires-trace')})
    for identity,state,scenario in [('ungranted-explicit-claim',right(base_state('complete'),grant=False),'An imported rule carries a complete local-use assertion; the owner has issued no grant.'),('unclaimed-qualified-grant',right(base_state('complete'),claim=False),'A hypothetical owner grant exists independently of any separate assertion record.'),('granted-right-with-unknown-origin',right(base_state('unknown')),'A hypothetical qualified permission exists; admission-use trace review is still unavailable.'),('responsibility-without-permission',responsibility(base_state('complete')),'A reviewer is assigned an obligation to route an outcome and has no permit grant for causing it.'),('granted-right-with-routed-gap',right(base_state('incomplete')),'A named owner act and correctly routed missing lineage segment coexist in the selected candidate scope.')]:states.append({'case_id':identity,'scenario':scenario,'state':state,'actual':p.inspect_state(state,'admission-use-requires-trace')})
    before=right(base_state());after=copy.deepcopy(before);after['revision']='state:after';set_provenance(after,'complete');transition=move(before,after)
    return {'source_scope':'Hypothetical named objects, actors, decisions and assignments; no actual owner acts or duty fulfillment asserted.','authority_effect':'none','states':states,'moves':[{'case_id':'provenance-only-exact-state-transition','before':before,'after':after,'move':transition,'actual':p.check_move(transition,before,after)}]}
