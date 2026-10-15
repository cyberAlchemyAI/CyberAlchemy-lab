"""Finite record-profile search; no whole-definition or unbounded proof claim."""
import copy
import json
import sys
from functools import lru_cache
from pathlib import Path
from time import monotonic
import contracts as c
import resolver as r
import ir
import semantics as s
import obligations as o
from providers import finite as f
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
UNIT=BASE/'units/A08';sys.path.insert(0,str(BASE/'units/A07'))
import pilot_spec as p

SCHEMA='definition-assurance-governance-search/v2-candidate'
SUBJECTS=('artifact:import-review','artifact:local-rule')
PATHS=('complete','unknown','empty','deferred','incomplete','source-local')
CLAIMS=('none','right','incomplete-right','responsibility','both')
MOVES=('provenance-only','silent-status','explicit-status')
RADICES=(6,6,2,2,2,2,5,3)
TOTAL=8640
CONSTRAINTS={'trace-implies-position','no-position','some-position','no-trace','no-right','no-duty','some-right','some-duty'}
SCOPE='scope:governance-record-projection-v2'
OWNERS={'Traceable':'provenance','Position':'authority','Right':'authority','Duty':'responsibility','BackedRight':'authority-claim'}


class PilotFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


class Stop(PilotFault):pass


class Control:
    def __init__(self,limits,cancelled=None):
        self.limits=limits;self.cancelled=cancelled;self.deadline=monotonic()+limits['timeout_seconds'];self.steps=0
    def poll(self):
        if self.cancelled is not None and self.cancelled():raise Stop('cancelled')
        if monotonic()>=self.deadline:raise Stop('timeout')
    def tick(self):
        self.poll()
        if self.steps>=self.limits['max_evaluation_steps']:raise Stop('evaluation-step-limit')
        self.steps+=1


def same(left,right,control):control.tick();return r.same_json(left,right)


def record_values(state,control):
    """Independent predicate implementation; A07 is used only for closed typing."""
    control.poll();p.validate_state(state);control.poll();context=state['context']
    if any(context[key]!=value for key,value in p.ADMISSION_CONTEXT.items()):raise PilotFault('record-outside-selected-context')
    role_table={row['binding_id']:row for row in state['role_bindings']};boundary_table={row['boundary_id']:row for row in state['boundaries']};rights=set();duties=set();backed=[];unbacked=[];incomplete=[]
    for grant in state['grants']:
        control.tick();role=role_table.get(grant['role_binding_ref']);boundary=boundary_table.get(grant['boundary_ref'])
        if role is None or boundary is None:continue
        matching=all(same(grant[key],value,control) for key,value in context.items())
        qualified=matching and same(role['principal'],grant['principal'],control) and same(boundary['principal_binding'],grant['principal'],control) and same(role['owner_role'],grant['owner_role'],control) and same(boundary['owner_role'],grant['owner_role'],control) and same(boundary['scope'],grant['scope'],control) and grant['object'] in boundary['allowed_objects'] and grant['effect'] in boundary['allowed_effects'] and grant['effect'] not in boundary['excluded_effects'] and same(boundary['challenge_route'],grant['challenge_route'],control)
        if qualified:rights.add(grant['grant_id'])
    for duty in state['responsibilities']:
        control.tick();role=role_table.get(duty['role_binding_ref'])
        if role is not None and same(role['principal'],duty['principal'],control) and same(role['owner_role'],duty['owner_role'],control) and all(same(duty[key],context[key],control) for key in ['principal','scope','object','operation']) and same(duty['outcome'],context['effect'],control):duties.add(duty['assignment_id'])
    grants={row['grant_id']:row for row in state['grants']}
    for claim in state['claims']:
        control.tick();complete=all(claim[key] is not None for key in p.CLAIM_FIELDS)
        if not complete:incomplete.append(claim['claim_id'])
        grant=grants.get(claim['assignment_ref']);holds=claim['position_kind']=='right' and complete and claim['assignment_ref'] in rights and all(same(claim[key],grant[key],control) for key in p.CLAIM_FIELDS)
        if holds:backed.append(claim['claim_id'])
        elif claim['position_kind']=='right':unbacked.append(claim['claim_id'])
    prov=state['provenance'];control.tick();trace=prov['knowledge'] in {'known','source-local'} and prov['trail_status'] in {'complete','incomplete'} and (prov['knowledge']!='source-local' or same(prov['scope_ref'],context['scope'],control))
    return {'Traceable':trace,'Position':bool(rights or duties),'Right':bool(rights),'Duty':bool(duties),'BackedRight':bool(backed),'right_grants':sorted(rights),'assigned_duties':sorted(duties),'backed_claims':backed,'unbacked_claims':unbacked,'incomplete_claims':incomplete,'unclaimed_right_grants':sorted(rights-{claim['assignment_ref'] for claim in state['claims'] if claim['position_kind']=='right'})}


def change_components(state):return {**state['posture'],'provenance':{'posture':state['posture']['provenance'],'record':state['provenance']},**{key:state[key] for key in p.CHANGE_AXES if key not in p.SOURCE_AXES}}


def delta_records(left,right,identity):
    a={row[identity]:row for row in left};b={row[identity]:row for row in right}
    return {key:(ir.digest(a[key]) if key in a else None,ir.digest(b[key]) if key in b else None) for key in set(a)|set(b) if not r.same_json(a.get(key),b.get(key))}


def transition_holds(transition,records,control):
    """Separate exact binding/frame check; no calls to A07 check_move."""
    control.poll();p.exact(transition,['before','after','move'],'malformed-transition');before=transition['before'];after=transition['after'];move=transition['move'];p.validate_state(before);p.validate_state(after)
    p.exact(move,['move_id','subject_id','context','before_ref','after_ref','intended_axes','recorded_changes','grant_changes','responsibility_changes'],'malformed-move')
    if not any(same(after,state,control) for state in records):return False
    if not same(move['subject_id'],before['object_id'],control) or not same(move['subject_id'],after['object_id'],control) or not same(move['context'],before['context'],control) or not same(move['context'],after['context'],control):return False
    for key,state in [('before_ref',before),('after_ref',after)]:
        p.exact(move[key],['revision','sha256'],'malformed-state-reference')
        if not same(move[key],{'revision':state['revision'],'sha256':ir.digest(state)},control):return False
    if same(before['revision'],after['revision'],control):return False
    p.identifiers(move['intended_axes'],nonempty=True)
    if not set(move['intended_axes'])<=set(p.CHANGE_AXES):return False
    old=change_components(before);new=change_components(after);changed={key for key in old if not same(old[key],new[key],control)};recorded=set()
    if not isinstance(move['recorded_changes'],list):raise PilotFault('malformed-recorded-changes')
    for row in move['recorded_changes']:
        p.exact(row,['axis','before_sha256','after_sha256','basis_ref'],'malformed-recorded-change');p.text(row['axis']);p.text(row['basis_ref']);key=row['axis']
        if key in recorded or key not in changed or not same([row['before_sha256'],row['after_sha256']],[ir.digest(old[key]),ir.digest(new[key])],control):return False
        recorded.add(key)
    if not set(move['intended_axes'])<=changed or not changed<=set(move['intended_axes'])|recorded or changed&{'boundaries','role_bindings'}:return False
    for key,identity in [('grants','grant_id'),('responsibilities','assignment_id')]:
        expected=delta_records(before[key],after[key],identity);seen=set();submitted=move['grant_changes' if key=='grants' else 'responsibility_changes']
        if not isinstance(submitted,list):raise PilotFault('malformed-assignment-changes')
        for row in submitted:
            p.exact(row,[identity,'before_sha256','after_sha256','basis_ref'],'malformed-assignment-change');p.text(row[identity]);p.text(row['basis_ref']);identity_value=row[identity]
            if identity_value in seen or identity_value not in expected or not same([row['before_sha256'],row['after_sha256']],list(expected[identity_value]),control):return False
            seen.add(identity_value)
        if seen!=set(expected):return False
    control.poll();return True


def info(value=None,state='known',scope=None):return {'state':state,'value':value,'scope_ref':scope}


def trail(state,mode):
    typed={'kind':'typed','step_id':'step:'+state['object_id'],'source_ref':'source:hypothetical-rule-v1','relation_ref':'relation.derived-from','operation_ref':'operation.import-for-review','owner_ref':'role:source-owner','posture_ref':'posture:source-local'}
    gap={'kind':'gap','step_id':'gap:'+state['object_id'],'residue_ref':'residue:hypothetical-import-gap','owner_route':'role:lineage-reviewer'}
    known=mode not in {'unknown','deferred'};knowledge='known' if mode in {'empty','complete','incomplete'} else mode
    state['provenance']={'knowledge':knowledge,'trail_status':mode if mode in {'empty','complete','incomplete'} else 'complete' if mode=='source-local' else 'unavailable','steps':[] if mode=='empty' else [typed,gap] if mode=='incomplete' else [typed] if known else None,'scope_ref':state['context']['scope'] if mode=='source-local' else None}
    v=state['provenance'];state['posture']['provenance']=info(v['trail_status'] if known else None,knowledge,v['scope_ref'])


def make_state(index,path,permit,duty,claim_mode):
    identity=SUBJECTS[index];context={**p.ADMISSION_CONTEXT,'principal':'principal:hypothetical-reviewer','object':identity}
    state={'schema_version':p.PROFILE,'authority_effect':'none','object_id':identity,'revision':'state:after:'+str(index),'context':context,'posture':{key:info(value) for key,value in zip(p.SOURCE_AXES,['rule','candidate','unassessed','proposed',None,'role:rule-owner','none'])},'provenance':None,'claims':[],'grants':[],'responsibilities':[],'role_bindings':[{'binding_id':'binding:rule-owner','principal':context['principal'],'owner_role':'role:rule-owner'}],'boundaries':[{'boundary_id':'boundary:rule-owner','owner_role':'role:rule-owner','principal_binding':context['principal'],'scope':context['scope'],'allowed_objects':list(SUBJECTS),'allowed_effects':[context['effect']],'excluded_effects':[],'challenge_route':'role:rule-challenge'}]}
    trail(state,path);fields={**context,'owner_role':'role:rule-owner','basis':'decision:hypothetical-owner-act','challenge_route':'role:rule-challenge'};grant_id='grant:'+str(index);duty_id='duty:'+str(index)
    if permit:state['grants']=[{'grant_id':grant_id,**fields,'boundary_ref':'boundary:rule-owner','role_binding_ref':'binding:rule-owner'}]
    if duty:state['responsibilities']=[{'assignment_id':duty_id,'owner_role':fields['owner_role'],'principal':fields['principal'],'scope':fields['scope'],'object':identity,'operation':fields['operation'],'outcome':fields['effect'],'owner_route':fields['challenge_route'],'basis':fields['basis'],'role_binding_ref':'binding:rule-owner'}]
    if claim_mode in {'right','incomplete-right','both'}:
        claim={'claim_id':'claim:right:'+str(index),'position_kind':'right','assignment_ref':grant_id,**fields}
        if claim_mode=='incomplete-right' and index==0:claim['scope']=None
        state['claims'].append(claim)
    if claim_mode in {'responsibility','both'}:state['claims'].append({'claim_id':'claim:duty:'+str(index),'position_kind':'responsibility','assignment_ref':duty_id,**fields})
    return state


def point(rank):
    if type(rank) is not int or not 0<=rank<TOTAL:raise PilotFault('invalid-configuration-rank')
    remaining=rank;digits=[]
    for radix in reversed(RADICES):remaining,digit=divmod(remaining,radix);digits.append(digit)
    a,b,g0,g1,d0,d1,claim,move=list(reversed(digits));records=[make_state(0,PATHS[a],bool(g0),bool(d0),CLAIMS[claim]),make_state(1,PATHS[b],bool(g1),bool(d1),CLAIMS[claim])]
    after=records[0];before=copy.deepcopy(after);before['revision']='state:before:0';trail(before,'empty' if PATHS[a]=='unknown' else 'unknown')
    recorded=[]
    if MOVES[move]!='provenance-only':after['posture']['status']=info('reviewed')
    if MOVES[move]=='explicit-status':recorded=[{'axis':'status','before_sha256':ir.digest(before['posture']['status']),'after_sha256':ir.digest(after['posture']['status']),'basis_ref':'decision:hypothetical-explicit-coupling'}]
    transition={'before':before,'after':copy.deepcopy(after),'move':{'move_id':'move:'+MOVES[move],'subject_id':after['object_id'],'context':copy.deepcopy(after['context']),'before_ref':{'revision':before['revision'],'sha256':ir.digest(before)},'after_ref':{'revision':after['revision'],'sha256':ir.digest(after)},'intended_axes':['provenance'],'recorded_changes':recorded,'grant_changes':[],'responsibility_changes':[]}}
    return {'records':records,'transition':transition}


def renamed(node,mapping):
    if isinstance(node,list):return [renamed(value,mapping) for value in node]
    if not isinstance(node,dict):return node
    result={key:renamed(value,mapping) for key,value in node.items()}
    if node.get('op') in {'pred','const','fn'}:result['name']=mapping[node['name']]
    if node.get('op') in {'forall','exists'}:result['sort']=mapping[node['sort']]
    return result


def capture_ref(ref,captured):
    p.exact(ref,['path','sha256'],'malformed-projection-reference');raw=r.read_bytes(ROOT,ref['path'])
    if r.digest(raw)!=ref['sha256']:raise PilotFault('stale-projection-artifact',ref['path'])
    if ref['path'] in captured and captured[ref['path']]!=raw:raise PilotFault('projection-read-race')
    captured[ref['path']]=raw;return raw


def read_ref(ref,captured):return r.parse(capture_ref(ref,captured),ref['path'])


@lru_cache(maxsize=2)
def typed_projection(encoded):
    value=json.loads(encoded);config=value['config'];inputs=value['inputs'];subject=value['subject'];ir.verify_composed(subject,inputs,config['alignment_refs'],ROOT)
    sources={source['definition_id']:source for source in config['sources']}
    if value['theory']['scope']!=SCOPE or len(inputs)!=7 or sorted([row['source']['definition_id'] for row in inputs])!=sorted(sources):raise PilotFault('projection-source-or-scope-denominator-substitution')
    for row in inputs:
        core=row['input_core'];owned=[key for key,owner in OWNERS.items() if core['source']['definition_id']=='cal.definition.'+owner]
        declarations=[{'kind':'sort','symbol_id':'Record','scope':SCOPE,'domain_policy':'nonempty'}]+[{'kind':'predicate','symbol_id':key,'scope':SCOPE,'argument_sorts':['Record']} for key in owned]
        if not r.same_json(core['source'],sources[core['source']['definition_id']]) or not r.same_json(core['declarations'],declarations) or core['scope']!=SCOPE or core['depends_on'] or core['assumptions'] or core['populations'] or core['relations'] or core['source_fidelity']!='pending' or core['semantic_status']!='candidate' or core['logic_features']!=['first-order']:raise PilotFault('unsupported-record-projection-IR')
        if len(core['clauses'])!=1 or core['clauses'][0]['formal_statement'] is not None or core['clauses'][0]['disposition']!='deferred':raise PilotFault('unsupported-record-projection-lowering')
    expected={key:ir.qualified(sources['cal.definition.'+owner],SCOPE,key) for key,owner in OWNERS.items()}
    expected['Record']=subject['sort_alignment'][ir.qualified(next(source for source in config['sources'] if source['definition_id']=='cal.definition.provenance'),value['theory']['scope'],'Record')]
    if not r.same_json(expected,config['symbol_mapping']):raise PilotFault('projection-nominal-identity-substitution')
    declarations=subject['declarations'];sorts={row['symbol_id']:row['symbol_id'] for row in declarations if row['kind']=='sort'};symbols={row['symbol_id']:row for row in declarations if row['kind']!='sort'}
    T=[ir.formula(node,sorts,symbols) for node in renamed(value['theory']['statements'],expected)]
    obligations=value['required']['logical_manifest']['obligations'];I=[ir.formula(renamed(row['statement'],expected),sorts,symbols) for row in obligations if row['obligation_id'].startswith('population:')];Q={row['obligation_id']:ir.formula(renamed(row['statement'],expected),sorts,symbols) for row in obligations}
    return {'declarations':declarations,'T':T,'I':I,'Q':Q}


def prepare():
    captured={};path=UNIT/'projection.json';config=read_ref({'path':path.relative_to(ROOT).as_posix(),'sha256':r.digest(path.read_bytes())},captured)
    if config.get('schema_version')!='definition-assurance-record-projection/v2-candidate' or config.get('authority_effect')!='none' or config.get('semantic_ready') is not False:raise PilotFault('unsupported-projection-profile')
    p.exact(config,['schema_version','authority_effect','semantic_ready','source_spec_ref','subject_ref','input_ir_refs','alignment_refs','theory_ref','relations_ref','populations_ref','endpoint_bindings_ref','required_set_ref','symbol_mapping','sources','semantics_contract_ref','claim_ceiling'],'malformed-projection-profile')
    context=r.parse((UNIT/'context.json').read_bytes(),'context')
    captured[(UNIT/'context.json').relative_to(ROOT).as_posix()]=(UNIT/'context.json').read_bytes()
    for ref in context['sources']:capture_ref({key:ref[key] for key in ['path','sha256']},captured)
    receipt=r.parse((BASE/'units/A07/receipt.json').read_bytes(),'A07-receipt')
    for ref in receipt['outputs']:capture_ref(ref,captured)
    spec=read_ref(config['source_spec_ref'],captured);p.bind_sources(spec,ROOT)
    selected={row['path']:row['sha256'] for row in context['sources']}
    for key in ['source_spec_ref','semantics_contract_ref']:
        if selected.get(config[key]['path'])!=config[key]['sha256']:raise PilotFault('projection-upstream-binding-substitution')
    if not r.same_json(config['sources'],spec['sources']):raise PilotFault('projection-source-selection-substitution')
    subject=read_ref(config['subject_ref'],captured);inputs=[read_ref(ref,captured) for ref in config['input_ir_refs']]
    for ref in config['alignment_refs']:read_ref(ref,captured)
    capture_ref(config['semantics_contract_ref'],captured)
    theory=read_ref(config['theory_ref'],captured);relations=read_ref(config['relations_ref'],captured);populations=read_ref(config['populations_ref'],captured);bindings=read_ref(config['endpoint_bindings_ref'],captured);submitted=read_ref(config['required_set_ref'],captured)
    required=o.generate(theory,relations,populations,bindings,ROOT);o.compare_required(required,submitted)
    if not r.same_json(theory['sources'],spec['sources']):raise PilotFault('projection-theory-source-substitution')
    pred=o.p.pred;quant=o.p.quant
    source_ids={row['definition_id']:row for row in spec['sources']}
    expected_bindings={name:{'source':source_ids['cal.definition.'+owner],'scope':SCOPE,'predicate':name,'carrier':'Record'} for name,owner in OWNERS.items()}
    if not r.same_json(bindings,expected_bindings):raise PilotFault('projection-endpoint-owner-substitution')
    expected_theory={'theory_id':'T_RECORD_PROJECTION_V2','sources':spec['sources'],'declarations':[{'kind':'sort','symbol_id':'Record','scope':SCOPE,'domain_policy':'nonempty'}]+[{'kind':'predicate','symbol_id':name,'scope':SCOPE,'argument_sorts':['Record']} for name in OWNERS],'statements':[quant('forall','Record',{'op':'iff','left':pred('Position'),'right':{'op':'or','args':[pred('Right'),pred('Duty')]}}),quant('forall','Record',{'op':'implies','left':pred('BackedRight'),'right':pred('Right')})],'assumption_set_id':'CTX_RECORDS_HYPOTHETICAL_V2','scope':SCOPE,'change_class':'initial','prior_theory_ref':None}
    if not r.same_json(theory,expected_theory):raise PilotFault('unsupported-record-projection-theory')
    if len(populations)!=5 or {row['predicate_ref'] for row in populations}!=set(OWNERS) or any(row['requirement']!='required' or not r.same_json(row['statement'],quant('exists','Record',pred(row['predicate_ref']))) for row in populations):raise PilotFault('projection-population-policy-substitution')
    if len(relations)!=2 or {row['bindings']['right']['predicate'] for row in relations}!={'Position','BackedRight'} or any(row['bindings']['left']['predicate']!='Traceable' or row['distinction']!='permitted' or row['proper'] is not False or row['forbidden'] or row['relation']['relation_class']!='overlap-distinct' or row['relation']['direction']!='forward' or row['relation']['minimum_strength']!='model-witness' for row in relations):raise PilotFault('projection-relation-policy-substitution')
    typed=typed_projection(ir.canonical({'config':config,'subject':subject,'inputs':inputs,'theory':theory,'required':required}).decode())
    runtime=f.current_bindings()+[{'path':Path(__file__).relative_to(ROOT).as_posix(),'sha256':r.digest(Path(__file__).read_bytes())}]
    return {'config':config,'spec':spec,'subject':subject,'inputs':inputs,'theory':theory,'required':required,'typed':typed,'captured':captured,'runtime':runtime}


def verify_bindings(prepared):
    for path,raw in prepared['captured'].items():
        if r.read_bytes(ROOT,path)!=raw:raise PilotFault('input-changed-during-record-search',path)
    p.bind_sources(prepared['spec'],ROOT)
    runtime=f.current_bindings()+[{'path':Path(__file__).relative_to(ROOT).as_posix(),'sha256':r.digest(Path(__file__).read_bytes())}]
    if not r.same_json(runtime,prepared['runtime']):raise PilotFault('runtime-or-checker-changed-during-search')


class Evaluator(s.Evaluator):
    def __init__(self,structure,control):super().__init__(structure);self.control=control
    def tick(self):self.control.tick();super().tick()


def assess(model,prepared,control,constraints=()):
    c.bounded_tree(model);p.exact(model,['records','transition'],'malformed-record-model')
    if not isinstance(model['records'],list) or len(model['records'])!=2 or [state.get('object_id') if isinstance(state,dict) else None for state in model['records']]!=list(SUBJECTS):raise PilotFault('exact-record-carrier-required')
    values=[record_values(state,control) for state in model['records']]
    if not transition_holds(model['transition'],model['records'],control):return {'status':'record-frame-counterexample','values':values,'theory':False,'populations':False,'queries':{}}
    for constraint in constraints:
        control.tick();position=any(value['Position'] for value in values);right=any(value['Right'] for value in values);duty=any(value['Duty'] for value in values);trace=any(value['Traceable'] for value in values)
        allowed={'trace-implies-position':all(not value['Traceable'] or value['Position'] for value in values),'no-position':not position,'some-position':position,'no-trace':not trace,'no-right':not right,'no-duty':not duty,'some-right':right,'some-duty':duty}[constraint]
        if not allowed:return {'status':'record-constraint-counterexample','values':values,'theory':False,'populations':False,'queries':{}}
    mapping=prepared['config']['symbol_mapping'];projection={'domains':{mapping['Record']:list(SUBJECTS)},'constants':{},'functions':{},'predicates':{mapping[name]:[[state['object_id']] for state,value in zip(model['records'],values) if value[name]] for name in ['Traceable','Position','Right','Duty','BackedRight']}}
    structure=s.validate_model(prepared['typed']['declarations'],projection);evaluator=Evaluator(structure,control)
    T=all(evaluator.holds(node) for node in prepared['typed']['T'])
    if not T:return {'status':'projection-theory-counterexample','values':values,'theory':False,'populations':False,'queries':{}}
    I=all(evaluator.holds(node) for node in prepared['typed']['I']);results={}
    for key,node in prepared['typed']['Q'].items():
        if key=='query:consistency' or I:results[key]=evaluator.holds(node)
    return {'status':'candidate-model-assessed','values':values,'theory':True,'populations':I,'queries':results,'projection_model':projection}


def validate_request(constraints,mode,start,stop):
    c.bounded_tree({'constraints':constraints,'mode':mode,'start':start,'stop':stop})
    if not isinstance(constraints,list) or any(not isinstance(value,str) for value in constraints) or len(set(constraints))!=len(constraints) or set(constraints)-CONSTRAINTS:raise PilotFault('unsupported-or-duplicate-record-constraint')
    if not isinstance(mode,str) or mode not in {'first-evidence','exhaustive'}:raise PilotFault('unsupported-search-mode')
    if type(start) is not int or type(stop) is not int or not 0<=start<stop<=TOTAL:raise PilotFault('invalid-exact-rank-range')


def search(constraints=None,mode='first-evidence',start=0,stop=TOTAL,budgets=None,cancelled=None):
    constraints=[] if constraints is None else constraints
    prepared=None;control=None;limits=None;rows=[];counts={'visited':0,'theory_models':0,'joint_models':0}
    complete=False;request_valid=False;currentness='not-verified'
    base={'schema_version':SCHEMA,'authority_effect':'none','semantic_ready':False,'source_fidelity':'pending','semantic_closure':'unresolved','unbounded_conclusion':None}
    def finish(status,diagnostics=()):
        for row in rows:
            if row['status']=='not-found':
                row['status']='bounded-no-theory-model' if complete and not counts['theory_models'] else 'bounded-no-joint-population-model' if complete and not counts['joint_models'] and row['obligation_id']!='query:consistency' else 'bounded-no-witness' if complete else 'unknown-incomplete-search'
                row['strength']='bounded-exhaustion' if complete else 'none'
        bindings={'required_set_sha256':prepared['required']['required_set_sha256'],'constraints_sha256':ir.digest(constraints),'projection_inputs_sha256':ir.digest({path:r.digest(raw) for path,raw in prepared['captured'].items()}),'request_sha256':ir.digest({'constraints':constraints,'mode':mode,'start':start,'stop':stop}),'implementation_sha256':ir.digest(prepared['runtime'])} if prepared else None
        value={**base,'status':status,'exhaustion_complete':complete,'source_runtime_currentness':currentness,'required_denominator_status':'resolved' if prepared else 'unresolved-no-evidence-emitted','counts':{**counts,'evaluation_steps':control.steps if control else 0},'query_results':rows,'diagnostics':list(diagnostics),'limits':limits,'finite_scope':{'radices':list(RADICES),'full_configurations':TOTAL,'rank_interval':[start,stop] if request_valid else None,'range_meaning':'Exact configuration ranks, not unrestricted domains or arbitrary records.'},'input_bindings':bindings,'implementation_bindings':prepared['runtime'] if prepared else None,'pending_gates':prepared['required']['administrative_and_semantic_gates'] if prepared else [],'claim_ceiling':'Conditional finite candidate record/projection evidence only. A checked witness is existential; bounded range exhaustion is not an unbounded theorem, source-owner fidelity or semantic admission.'}
        if limits and len(ir.canonical(value))>limits['max_output_bytes']:
            compact=[{'obligation_id':row['obligation_id'],'status':'unknown-output-limit','strength':'none','witness':None} for row in rows]
            return {**base,'status':'resource-limit','exhaustion_complete':False,'source_runtime_currentness':currentness,'required_denominator_status':value['required_denominator_status'],'counts':value['counts'],'query_results':compact,'diagnostics':[{'code':'output-byte-limit'}],'input_bindings':bindings,'pending_gate_ids':[row['gate_id'] for row in value['pending_gates']]}
        return value
    def invalidate(status):
        for row in rows:row.update(status=status,strength='none',witness=None)
    try:
        limits=f.load_limits(budgets)
        if limits['max_output_bytes']<8192:raise PilotFault('output-budget-below-required-control-envelope')
        if limits['max_domain_cardinality']<len(SUBJECTS):raise PilotFault('selected-carrier-exceeds-domain-budget')
        control=Control(limits,cancelled);validate_request(constraints,mode,start,stop);request_valid=True
        control.poll();prepared=prepare()
        rows=[{'obligation_id':row['obligation_id'],'statement_sha256':ir.digest(row['statement']),'status':'not-found','strength':'none','minimum_strength':row['minimum_strength'],'witness':None} for row in prepared['required']['logical_manifest']['obligations']]
        by_id={row['obligation_id']:row for row in rows};control.poll()
        for rank in range(start,stop):
            control.poll()
            if counts['visited']>=limits['max_interpretations']:raise Stop('configuration-limit')
            model=point(rank);control.poll();counts['visited']+=1;actual=assess(model,prepared,control,constraints)
            if actual['theory']:
                counts['theory_models']+=1;counts['joint_models']+=actual['populations']
                for key,truth in actual['queries'].items():
                    if truth and by_id[key]['witness'] is None:by_id[key].update(status='witness-found',strength='model-witness',witness={'rank':rank,'model':model,'model_sha256':ir.digest(model),'projection_model':actual['projection_model'],'projection_model_sha256':ir.digest(actual['projection_model'])})
                if mode=='first-evidence' and all(row['witness'] is not None for row in rows):break
        else:complete=True
        verify_bindings(prepared);currentness='verified-at-final-read'
        control.poll();return finish('bounded-checked' if complete else 'witnesses-found')
    except Stop as error:
        complete=False
        # Partial witnesses need the same final byte/currentness checks.
        if prepared:
            try:verify_bindings(prepared);currentness='verified-at-final-read'
            except (PilotFault,p.SemanticFault,r.CaptureFault,f.ProviderFault,OSError,ValueError,KeyError,TypeError) as stale:
                currentness='failed-final-read';invalidate('unresolved-input-or-binding')
                return finish('unresolved-input-or-binding',[{'code':getattr(stale,'code',type(stale).__name__)}])
        return finish(error.code if error.code in {'timeout','cancelled'} else 'resource-limit',[{'code':error.code}])
    except (PilotFault,p.SemanticFault,r.CaptureFault,o.ObligationFault,o.p.PolicyFault,ir.IRFault,c.InputError,f.ProviderFault,s.ModelFault) as error:
        complete=False;invalidate('unresolved-input-or-binding')
        return finish('unresolved-input-or-binding' if isinstance(error,r.CaptureFault) or 'stale' in error.code or 'changed' in error.code else 'unsupported' if 'unsupported' in error.code else 'malformed',[{'code':error.code,'path':error.path}])
    except (OSError,ImportError,AttributeError,KeyError,TypeError,ValueError,IndexError,MemoryError,RecursionError) as error:
        complete=False;invalidate('provider-error')
        return finish('provider-error',[{'code':type(error).__name__}])
