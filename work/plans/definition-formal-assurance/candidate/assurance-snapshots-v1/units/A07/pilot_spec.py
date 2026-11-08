"""Explicit candidate record semantics for A07; no search or live authority act."""
from pathlib import Path
import copy
import json
import sys
ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path.insert(0,str(IMPL))
import contracts as c
import resolver as r
import ir

PROFILE='definition-assurance-governance-records/v2-candidate'
SOURCE_AXES=('kind','status','evidence','commitment','provenance','owner','residue')
CHANGE_AXES=SOURCE_AXES+('claims','grants','responsibilities','boundaries','role_bindings')
ADMISSION_CONTEXT={'scope':'scope:pilot-local-use','surface':'surface:pilot-rules','operation':'count-as-local-rule','effect':'permitted-local-use'}
CLAIM_FIELDS=('scope','owner_role','principal','surface','object','operation','basis','effect','challenge_route')
QUERY_FIELDS=('scope','principal','surface','object','operation','effect')
SOURCE_IDS=tuple('cal.definition.'+name for name in ['authority','authority-claim','responsibility','provenance','governance-axis-independence-invariant','authority-boundary','authority-surface'])


class SemanticFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


def exact(value,keys,code):
    if not isinstance(value,dict) or set(value)!=set(keys):raise SemanticFault(code)


def text(value):
    if not isinstance(value,str) or not value.strip() or value!=value.strip():raise SemanticFault('explicit-nonempty-identifier-required')


def sha(value):
    if not isinstance(value,str) or len(value)!=64 or any(ch not in '0123456789abcdef' for ch in value):raise SemanticFault('invalid-byte-digest')


def identifiers(values,nonempty=False):
    if not isinstance(values,list) or (nonempty and not values):raise SemanticFault('identifier-list-required')
    for value in values:text(value)
    if len(set(values))!=len(values):raise SemanticFault('duplicate-identifier')


def rows(values,identity,fields,nullable=()):
    if not isinstance(values,list):raise SemanticFault('typed-record-list-required')
    names=set()
    for row in values:
        exact(row,fields,'malformed-typed-record')
        for key in fields:
            if key in nullable and row[key] is None:continue
            text(row[key])
        if row[identity] in names:raise SemanticFault('duplicate-record-identity',row[identity])
        names.add(row[identity])


def information(value):
    exact(value,['state','value','scope_ref'],'malformed-information-state')
    state=value['state']
    if not isinstance(state,str) or state not in {'known','unknown','deferred','source-local'}:raise SemanticFault('unsupported-information-state')
    if state in {'unknown','deferred'}:
        if value['value'] is not None or value['scope_ref'] is not None:raise SemanticFault('unknown-or-deferred-is-not-known-value')
    else:
        text(value['value'])
        if state=='source-local':text(value['scope_ref'])
        elif value['scope_ref'] is not None:raise SemanticFault('unexpected-information-scope')


def provenance(value):
    exact(value,['knowledge','trail_status','steps','scope_ref'],'malformed-provenance-record');knowledge=value['knowledge'];status=value['trail_status'];steps=value['steps']
    if not isinstance(knowledge,str) or knowledge not in {'known','unknown','deferred','source-local'}:raise SemanticFault('unsupported-provenance-knowledge')
    if knowledge in {'unknown','deferred'}:
        if status!='unavailable' or steps is not None or value['scope_ref'] is not None:raise SemanticFault('unknown-provenance-is-not-empty-trail')
        return
    if knowledge=='source-local':text(value['scope_ref'])
    elif value['scope_ref'] is not None:raise SemanticFault('unexpected-provenance-scope')
    if not isinstance(status,str) or status not in {'empty','complete','incomplete'} or not isinstance(steps,list):raise SemanticFault('malformed-known-trail')
    identities=set();gaps=0
    for step in steps:
        if not isinstance(step,dict):raise SemanticFault('malformed-provenance-step')
        kind=step.get('kind')
        keys=['kind','step_id','source_ref','relation_ref','operation_ref','owner_ref','posture_ref'] if kind=='typed' else ['kind','step_id','residue_ref','owner_route'] if kind=='gap' else None
        if keys is None:raise SemanticFault('untyped-provenance-step')
        exact(step,keys,'malformed-provenance-step')
        for item in step.values():text(item)
        if step['step_id'] in identities:raise SemanticFault('duplicate-provenance-step')
        identities.add(step['step_id']);gaps+=kind=='gap'
    if status=='empty' and steps or status=='complete' and (not steps or gaps) or status=='incomplete' and (not steps or not gaps):raise SemanticFault('trail-status-does-not-match-record')


def validate_state(state):
    c.bounded_tree(state)
    exact(state,['schema_version','authority_effect','object_id','revision','context','posture','provenance','claims','grants','responsibilities','boundaries','role_bindings'],'malformed-state')
    if state['schema_version']!=PROFILE or state['authority_effect']!='none':raise SemanticFault('unsupported-state-or-authority-boundary')
    text(state['object_id']);text(state['revision']);exact(state['context'],QUERY_FIELDS,'malformed-query-context')
    for value in state['context'].values():text(value)
    if state['context']['object']!=state['object_id']:raise SemanticFault('query-subject-mismatch')
    exact(state['posture'],SOURCE_AXES,'incomplete-posture')
    for value in state['posture'].values():information(value)
    provenance(state['provenance']);p=state['provenance'];expected={'state':p['knowledge'],'value':p['trail_status'] if p['knowledge'] in {'known','source-local'} else None,'scope_ref':p['scope_ref']}
    if not r.same_json(expected,state['posture']['provenance']):raise SemanticFault('posture-provenance-record-mismatch')
    rows(state['claims'],'claim_id',('claim_id','position_kind','assignment_ref')+CLAIM_FIELDS,nullable=('assignment_ref',)+CLAIM_FIELDS)
    if any(row['position_kind'] not in {'right','responsibility'} for row in state['claims']):raise SemanticFault('unsupported-position-kind')
    rows(state['grants'],'grant_id',('grant_id','boundary_ref','role_binding_ref')+CLAIM_FIELDS)
    rows(state['responsibilities'],'assignment_id',('assignment_id','owner_role','principal','scope','object','operation','outcome','owner_route','basis','role_binding_ref'))
    rows(state['role_bindings'],'binding_id',('binding_id','principal','owner_role'))
    if not isinstance(state['boundaries'],list):raise SemanticFault('boundary-list-required')
    names=set()
    for boundary in state['boundaries']:
        exact(boundary,['boundary_id','owner_role','principal_binding','scope','allowed_objects','allowed_effects','excluded_effects','challenge_route'],'malformed-boundary')
        for key in ['boundary_id','owner_role','principal_binding','scope','challenge_route']:text(boundary[key])
        for key in ['allowed_objects','allowed_effects','excluded_effects']:identifiers(boundary[key])
        if boundary['boundary_id'] in names:raise SemanticFault('duplicate-boundary-identity')
        names.add(boundary['boundary_id'])
    return True


def matches_context(row,context):return all(row[key]==value for key,value in context.items())


def qualified_grant(grant,state):
    context=state['context']
    if not matches_context(grant,context):return False
    role=next((row for row in state['role_bindings'] if row['binding_id']==grant['role_binding_ref']),None)
    boundary=next((row for row in state['boundaries'] if row['boundary_id']==grant['boundary_ref']),None)
    if role is None or boundary is None:return False
    return role['principal']==grant['principal']==boundary['principal_binding'] and role['owner_role']==grant['owner_role']==boundary['owner_role'] and grant['scope']==boundary['scope'] and grant['object'] in boundary['allowed_objects'] and grant['effect'] in boundary['allowed_effects'] and grant['effect'] not in boundary['excluded_effects'] and grant['challenge_route']==boundary['challenge_route']


def traceable(value,scope):
    # Empty is expressible and well formed, but this selected use profile needs a trace.
    return value['knowledge'] in {'known','source-local'} and value['trail_status'] in {'complete','incomplete'} and (value['knowledge']!='source-local' or value['scope_ref']==scope)


def inspect_state(state,coupling='none'):
    validate_state(state)
    if not isinstance(coupling,str) or coupling not in {'none','admission-use-requires-trace'}:raise SemanticFault('unsupported-coupling-profile')
    if coupling=='admission-use-requires-trace' and any(state['context'][key]!=value for key,value in ADMISSION_CONTEXT.items()):raise SemanticFault('coupling-outside-selected-operation-scope')
    rights=[];duties=[];unbacked=[];explicit=[]
    qualified=[grant['grant_id'] for grant in state['grants'] if qualified_grant(grant,state)]
    assigned=[]
    for duty in state['responsibilities']:
        role=next((row for row in state['role_bindings'] if row['binding_id']==duty['role_binding_ref']),None)
        if role and role['principal']==duty['principal']==state['context']['principal'] and role['owner_role']==duty['owner_role'] and all(duty[key]==state['context'][key] for key in ['scope','object','operation']) and duty['outcome']==state['context']['effect']:assigned.append(duty['assignment_id'])
    for claim in state['claims']:
        complete=all(isinstance(claim[key],str) and claim[key].strip() for key in CLAIM_FIELDS)
        if complete:explicit.append(claim['claim_id'])
        supported=False
        if claim['position_kind']=='right' and complete:
            for grant in state['grants']:
                if grant['grant_id']==claim['assignment_ref'] and all(grant[key]==claim[key] for key in CLAIM_FIELDS) and qualified_grant(grant,state):rights.append(claim['claim_id']);supported=True;break
        elif claim['position_kind']=='responsibility' and complete:
            for duty in state['responsibilities']:
                if duty['assignment_id'] in assigned and duty['assignment_id']==claim['assignment_ref'] and claim['effect']==duty['outcome'] and claim['challenge_route']==duty['owner_route'] and all(duty[key]==claim[key] for key in ['owner_role','principal','scope','object','operation','basis']) and matches_context(claim,state['context']):duties.append(claim['claim_id']);supported=True;break
        if not supported:unbacked.append(claim['claim_id'])
    observable=traceable(state['provenance'],state['context']['scope'])
    return {'authority_effect':'none','semantic_ready':False,'authority_right_claims':rights,'responsibility_claims':duties,'qualified_right_grants':qualified,'assigned_responsibilities':assigned,'authority_positions':[{'kind':'right','assignment_id':value} for value in qualified]+[{'kind':'responsibility','assignment_id':value} for value in assigned],'explicit_claims':explicit,'unbacked_claims':unbacked,'provenance_state':state['provenance']['knowledge']+':'+state['provenance']['trail_status'],'traceable_for_selected_scope':observable,'usable_right_claims':rights if coupling=='none' or observable else [],'coupling':coupling,'root_legitimacy':'hypothetical-owner-acts-and-principal-bindings-assumed','responsibility_fulfillment':'not-assessed','claim_ceiling':'Conditional interpretation of these exact candidate records; no actual grant authority, fulfilled duty, world truth or whole-definition proof.'}


def component(state,axis):
    if axis=='provenance':return {'posture':state['posture']['provenance'],'record':state['provenance']}
    if axis in SOURCE_AXES:return state['posture'][axis]
    return state[axis]


def deltas(before,after,identity):
    left={row[identity]:row for row in before};right={row[identity]:row for row in after};result={}
    for key in set(left)|set(right):
        if not r.same_json(left.get(key),right.get(key)):result[key]=(ir.digest(left[key]) if key in left else None,ir.digest(right[key]) if key in right else None)
    return result


def verify_deltas(submitted,expected,identity):
    if not isinstance(submitted,list):raise SemanticFault('change-record-list-required')
    seen=set()
    for row in submitted:
        exact(row,[identity,'before_sha256','after_sha256','basis_ref'],'malformed-assignment-change');text(row[identity]);text(row['basis_ref'])
        for key in ['before_sha256','after_sha256']:
            if row[key] is not None:sha(row[key])
        key=row[identity]
        if key in seen:raise SemanticFault('duplicate-assignment-change')
        seen.add(key)
        if key not in expected or not r.same_json([row['before_sha256'],row['after_sha256']],list(expected[key])):raise SemanticFault('assignment-change-record-mismatch')
    if seen!=set(expected):raise SemanticFault('unrecorded-assignment-change')


def check_move(move,before,after):
    validate_state(before);validate_state(after);c.bounded_tree(move)
    exact(move,['move_id','subject_id','context','before_ref','after_ref','intended_axes','recorded_changes','grant_changes','responsibility_changes'],'malformed-move')
    text(move['move_id']);text(move['subject_id'])
    if move['subject_id']!=before['object_id'] or move['subject_id']!=after['object_id']:raise SemanticFault('move-subject-mismatch')
    if not r.same_json(move['context'],before['context']) or not r.same_json(move['context'],after['context']):raise SemanticFault('move-query-context-mismatch')
    for key,state in [('before_ref',before),('after_ref',after)]:
        exact(move[key],['revision','sha256'],'malformed-move-state-binding');sha(move[key]['sha256'])
        if move[key]['revision']!=state['revision'] or move[key]['sha256']!=ir.digest(state):raise SemanticFault('move-record-binding-mismatch',key)
    if before['revision']==after['revision']:raise SemanticFault('move-revision-not-advanced')
    identifiers(move['intended_axes'],nonempty=True)
    if not set(move['intended_axes'])<=set(CHANGE_AXES):raise SemanticFault('unknown-intended-axis')
    changed={axis for axis in CHANGE_AXES if not r.same_json(component(before,axis),component(after,axis))}
    recorded=set()
    if not isinstance(move['recorded_changes'],list):raise SemanticFault('recorded-change-list-required')
    for row in move['recorded_changes']:
        exact(row,['axis','before_sha256','after_sha256','basis_ref'],'malformed-recorded-axis-change');text(row['basis_ref']);sha(row['before_sha256']);sha(row['after_sha256']);axis=row['axis'];text(axis)
        if axis in recorded or axis not in changed:raise SemanticFault('recorded-axis-not-changed-or-duplicated')
        recorded.add(axis)
        if row['before_sha256']!=ir.digest(component(before,axis)) or row['after_sha256']!=ir.digest(component(after,axis)):raise SemanticFault('recorded-axis-binding-mismatch')
    if not set(move['intended_axes'])<=changed or not changed<=set(move['intended_axes'])|recorded:raise SemanticFault('silent-frame-change-or-unperformed-intention')
    if changed&{'boundaries','role_bindings'}:raise SemanticFault('authority-boundary-or-principal-binding-change-outside-pilot')
    verify_deltas(move['grant_changes'],deltas(before['grants'],after['grants'],'grant_id'),'grant_id')
    verify_deltas(move['responsibility_changes'],deltas(before['responsibilities'],after['responsibilities'],'assignment_id'),'assignment_id')
    return {'result':'candidate-frame-checked','changed_axes':sorted(changed),'recorded_axes':sorted(recorded),'grant_changes':len(move['grant_changes']),'responsibility_changes':len(move['responsibility_changes']),'authority_effect':'none','semantic_ready':False,'claim_ceiling':'Exact before/after candidate frame and explicitly recorded assignment deltas only; recording a change supplies no grant legitimacy or authorization to perform it.'}


def bind_sources(spec,root=ROOT):
    if not isinstance(spec,dict) or not isinstance(spec.get('sources'),list):raise SemanticFault('malformed-pilot-source-selection')
    ref=spec['snapshot_ref'];exact(ref,['path','sha256'],'malformed-pilot-snapshot-reference');sha(ref['sha256']);raw=r.read_bytes(root,ref['path'])
    if r.digest(raw)!=ref['sha256']:raise SemanticFault('stale-pilot-source-snapshot')
    snapshot=r.parse(raw,ref['path']);r.verify(snapshot,root)
    for source in spec['sources']:
        exact(source,['definition_id','version_ref','path','sha256'],'malformed-pilot-source-reference')
        for value in source.values():text(value)
        sha(source['sha256'])
    if len(spec['sources'])!=len(SOURCE_IDS) or {row['definition_id'] for row in spec['sources']}!=set(SOURCE_IDS):raise SemanticFault('pilot-source-denominator-mismatch')
    current={row['definition_id']:row for row in snapshot['current_entries']}
    for source in spec['sources']:
        if any(source[key]!=current[source['definition_id']][key] for key in ['version_ref','path','sha256']):raise SemanticFault('pilot-source-substitution')
    return {'result':'PASS','sources':len(spec['sources']),'source_capture_files':len(snapshot['captured_files']),'authority_effect':'none','source_fidelity':'pending','semantic_ready':False}
