"""Independent construction of the exact A08 declared finite product."""
import copy
from math import prod
import ir

SUBJECTS=('artifact:import-review','artifact:local-rule')
AXES=('kind','status','evidence','commitment','provenance','owner','residue')
PATHS=('complete','unknown','empty','deferred','incomplete','source-local')
CLAIMS=('none','right','incomplete-right','responsibility','both')
MOVES=('provenance-only','silent-status','explicit-status')
RADICES=(6,6,2,2,2,2,5,3);TOTAL=prod(RADICES)
CONTEXT={'scope':'scope:pilot-local-use','surface':'surface:pilot-rules','operation':'count-as-local-rule','effect':'permitted-local-use'}


def information(value,state='known',scope=None):return {'state':state,'value':value,'scope_ref':scope}


def state(index,path,permit,duty,claims,status='candidate',revision=None):
    object_id=SUBJECTS[index];q={**CONTEXT,'principal':'principal:hypothetical-reviewer','object':object_id}
    if path in ('unknown','deferred'):knowledge=path;trail_status='unavailable';steps=None;scope=None
    else:
        knowledge='source-local' if path=='source-local' else 'known';trail_status='complete' if path=='source-local' else path;scope=q['scope'] if path=='source-local' else None
        step={'kind':'typed','step_id':'step:'+object_id,'source_ref':'source:hypothetical-rule-v1','relation_ref':'relation.derived-from','operation_ref':'operation.import-for-review','owner_ref':'role:source-owner','posture_ref':'posture:source-local'}
        steps=[] if path=='empty' else [step]
        if path=='incomplete':steps.append({'kind':'gap','step_id':'gap:'+object_id,'residue_ref':'residue:hypothetical-import-gap','owner_route':'role:lineage-reviewer'})
    provenance={'knowledge':knowledge,'trail_status':trail_status,'steps':steps,'scope_ref':scope}
    posture={key:information(value) for key,value in {'kind':'rule','status':status,'evidence':'unassessed','commitment':'proposed','owner':'role:rule-owner','residue':'none'}.items()}
    posture['provenance']=information(trail_status if steps is not None else None,knowledge,scope)
    fields={**q,'owner_role':'role:rule-owner','basis':'decision:hypothetical-owner-act','challenge_route':'role:rule-challenge'}
    grants=[{'grant_id':'grant:'+str(index),**fields,'boundary_ref':'boundary:rule-owner','role_binding_ref':'binding:rule-owner'}] if permit else []
    assignments=[{'assignment_id':'duty:'+str(index),'owner_role':fields['owner_role'],'principal':q['principal'],'scope':q['scope'],'object':object_id,'operation':q['operation'],'outcome':q['effect'],'owner_route':'role:rule-challenge','basis':fields['basis'],'role_binding_ref':'binding:rule-owner'}] if duty else []
    asserted=[]
    if claims in ('right','incomplete-right','both'):
        claim={'claim_id':'claim:right:'+str(index),'position_kind':'right','assignment_ref':'grant:'+str(index),**fields}
        if claims=='incomplete-right' and index==0:claim['scope']=None
        asserted.append(claim)
    if claims in ('responsibility','both'):asserted.append({'claim_id':'claim:duty:'+str(index),'position_kind':'responsibility','assignment_ref':'duty:'+str(index),**fields})
    return {'schema_version':'definition-assurance-governance-records/v2-candidate','authority_effect':'none','object_id':object_id,'revision':revision or 'state:after:'+str(index),'context':q,'posture':posture,'provenance':provenance,'claims':asserted,'grants':grants,'responsibilities':assignments,'boundaries':[{'boundary_id':'boundary:rule-owner','owner_role':'role:rule-owner','principal_binding':q['principal'],'scope':q['scope'],'allowed_objects':list(SUBJECTS),'allowed_effects':[q['effect']],'excluded_effects':[],'challenge_route':'role:rule-challenge'}],'role_bindings':[{'binding_id':'binding:rule-owner','principal':q['principal'],'owner_role':'role:rule-owner'}]}


def coordinates(rank):
    if type(rank) is not int or not 0<=rank<TOTAL:raise ValueError('Invalid exact finite rank')
    return tuple((rank//prod(RADICES[i+1:]))%radix for i,radix in enumerate(RADICES))


def world(rank):
    a,b,g0,g1,d0,d1,c,m=coordinates(rank);claim=CLAIMS[c];move_kind=MOVES[m]
    after=state(0,PATHS[a],g0,d0,claim,status='candidate' if m==0 else 'reviewed')
    other=state(1,PATHS[b],g1,d1,claim)
    before=state(0,'empty' if PATHS[a]=='unknown' else 'unknown',g0,d0,claim,revision='state:before:0')
    recorded=[] if m!=2 else [{'axis':'status','before_sha256':ir.digest(before['posture']['status']),'after_sha256':ir.digest(after['posture']['status']),'basis_ref':'decision:hypothetical-explicit-coupling'}]
    move={'move_id':'move:'+move_kind,'subject_id':SUBJECTS[0],'context':copy.deepcopy(after['context']),'before_ref':{'revision':before['revision'],'sha256':ir.digest(before)},'after_ref':{'revision':after['revision'],'sha256':ir.digest(after)},'intended_axes':['provenance'],'recorded_changes':recorded,'grant_changes':[],'responsibility_changes':[]}
    return {'records':[after,other],'transition':{'before':before,'after':copy.deepcopy(after),'move':move}}
