"""Independent record/projection replay with exact byte-selected finite scope."""
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from time import monotonic
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parent.parent;IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
sys.path[:0]=[str(UNIT),str(IMPL),str(BASE/'units/A07')]
import contracts as c
import resolver as r
import ir
import obligations as o
import verifier as e
import pilot_spec as types
from providers import finite as f
import reference_world as w
loader=importlib.util.spec_from_file_location('A09_provider_under_test',IMPL/'pilot-v2.py');provider=importlib.util.module_from_spec(loader);loader.loader.exec_module(provider)
SELECTED={'path':(UNIT/'selection.json').relative_to(ROOT).as_posix(),'sha256':'c52c58699b03404b6e4a61b351720ffdc69925125a3762298a3769739ce7e18c'}
OWNERS={'Traceable':'provenance','Position':'authority','Right':'authority','Duty':'responsibility','BackedRight':'authority-claim'}
FIELDS=('scope','owner_role','principal','surface','object','operation','basis','effect','challenge_route')
ALL_AXES=w.AXES+('claims','grants','responsibilities','boundaries','role_bindings')
CONSTRAINTS={'trace-implies-position','no-position','some-position','no-trace','no-right','no-duty','some-right','some-duty'}


class ReplayFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


class Stop(ReplayFault):pass


def exact(value,keys,code):
    if not isinstance(value,dict) or set(value)!=set(keys):raise ReplayFault(code)


class Control:
    def __init__(self,limits,cancelled=None):self.limits=limits;self.cancelled=cancelled;self.steps=0;self.deadline=monotonic()+limits['timeout_seconds']
    def poll(self):
        if self.cancelled and self.cancelled():raise Stop('cancelled')
        if monotonic()>=self.deadline:raise Stop('timeout')
    def tick(self):
        self.poll()
        if self.steps>=self.limits['max_evaluation_steps']:raise Stop('evaluation-step-limit')
        self.steps+=1


def equal(left,right,control):control.tick();return r.same_json(left,right)


def record(state,control):
    control.poll();types.validate_state(state);q=state['context']
    if any(q[key]!=value for key,value in w.CONTEXT.items()):raise ReplayFault('unsupported-record-context')
    permits=[];duties=[]
    for grant in state['grants']:
        for role in state['role_bindings']:
            if not equal(role['binding_id'],grant['role_binding_ref'],control):continue
            for boundary in state['boundaries']:
                control.tick()
                if boundary['boundary_id']!=grant['boundary_ref']:continue
                matching=all(equal(grant[key],value,control) for key,value in q.items())
                ownership=equal(role['principal'],grant['principal'],control) and equal(boundary['principal_binding'],grant['principal'],control) and equal(role['owner_role'],grant['owner_role'],control) and equal(boundary['owner_role'],grant['owner_role'],control)
                bounded=equal(boundary['scope'],grant['scope'],control) and grant['object'] in boundary['allowed_objects'] and grant['effect'] in boundary['allowed_effects'] and grant['effect'] not in boundary['excluded_effects'] and equal(boundary['challenge_route'],grant['challenge_route'],control)
                if matching and ownership and bounded:permits.append(grant)
    for assignment in state['responsibilities']:
        for role in state['role_bindings']:
            control.tick()
            if role['binding_id']!=assignment['role_binding_ref']:continue
            if all(equal(assignment[key],q[key],control) for key in ('principal','scope','object','operation')) and equal(assignment['outcome'],q['effect'],control) and equal(role['principal'],assignment['principal'],control) and equal(role['owner_role'],assignment['owner_role'],control):duties.append(assignment)
    supported=[];unbacked=[];incomplete=[]
    for claim in state['claims']:
        control.tick();complete=all(isinstance(claim[key],str) for key in FIELDS)
        if not complete:incomplete.append(claim['claim_id'])
        if claim['position_kind']!='right':continue
        holds=complete and any(equal(claim['assignment_ref'],grant['grant_id'],control) and all(equal(claim[key],grant[key],control) for key in FIELDS) for grant in permits)
        (supported if holds else unbacked).append(claim['claim_id'])
    lineage=state['provenance'];control.tick()
    # Shape checking already ensures nonempty qualified trails and routed gaps.
    traced=lineage['steps'] is not None and len(lineage['steps'])>0 and lineage['knowledge'] in ('known','source-local') and (lineage['knowledge']!='source-local' or equal(lineage['scope_ref'],q['scope'],control))
    ids={row['grant_id'] for row in permits};referenced={row['assignment_ref'] for row in state['claims'] if row['position_kind']=='right'}
    return {'Traceable':bool(traced),'Position':bool(permits or duties),'Right':bool(permits),'Duty':bool(duties),'BackedRight':bool(supported),'right_grants':sorted(ids),'assigned_duties':sorted(row['assignment_id'] for row in duties),'backed_claims':supported,'unbacked_claims':unbacked,'incomplete_claims':incomplete,'unclaimed_right_grants':sorted(ids-referenced)}


def component(state,axis):
    if axis=='provenance':return [state['posture']['provenance'],state['provenance']]
    if axis in w.AXES:return state['posture'][axis]
    return state[axis]


def delta(before,after,identity):
    left={row[identity]:row for row in before};right={row[identity]:row for row in after};changes={}
    for key in left.keys()|right.keys():
        if not r.same_json(left.get(key),right.get(key)):changes[key]=[ir.digest(left[key]) if key in left else None,ir.digest(right[key]) if key in right else None]
    return changes


def frame(transition,records,control):
    exact(transition,['before','after','move'],'malformed-transition');before=transition['before'];after=transition['after'];m=transition['move'];types.validate_state(before);types.validate_state(after)
    exact(m,['move_id','subject_id','context','before_ref','after_ref','intended_axes','recorded_changes','grant_changes','responsibility_changes'],'malformed-move');types.text(m['move_id']);types.text(m['subject_id'])
    if not any(equal(after,state,control) for state in records):return False
    if not (m['subject_id']==before['object_id']==after['object_id']) or not equal(before['context'],m['context'],control) or not equal(after['context'],m['context'],control):return False
    for ref,state in [(m['before_ref'],before),(m['after_ref'],after)]:
        exact(ref,['revision','sha256'],'malformed-snapshot-ref');types.sha(ref['sha256']);types.text(ref['revision'])
        if not equal(ref,{'revision':state['revision'],'sha256':ir.digest(state)},control):return False
    if before['revision']==after['revision']:return False
    types.identifiers(m['intended_axes'],nonempty=True)
    if any(axis not in ALL_AXES for axis in m['intended_axes']):return False
    changed={axis for axis in ALL_AXES if not equal(component(before,axis),component(after,axis),control)}
    if changed & {'boundaries','role_bindings'}:return False
    recorded={}
    if not isinstance(m['recorded_changes'],list):raise ReplayFault('malformed-recorded-changes')
    for row in m['recorded_changes']:
        exact(row,['axis','before_sha256','after_sha256','basis_ref'],'malformed-recorded-change');types.text(row['axis']);types.text(row['basis_ref']);types.sha(row['before_sha256']);types.sha(row['after_sha256']);axis=row['axis']
        if axis in recorded or axis not in changed:return False
        # The sealed change-component digest uses its declared object representation.
        before_component={'posture':before['posture']['provenance'],'record':before['provenance']} if axis=='provenance' else component(before,axis)
        after_component={'posture':after['posture']['provenance'],'record':after['provenance']} if axis=='provenance' else component(after,axis)
        if not equal([row['before_sha256'],row['after_sha256']],[ir.digest(before_component),ir.digest(after_component)],control):return False
        recorded[axis]=row
    intended=set(m['intended_axes'])
    if not intended<=changed or not changed<=intended|set(recorded):return False
    for pool,identity,rows in [('grants','grant_id',m['grant_changes']),('responsibilities','assignment_id',m['responsibility_changes'])]:
        expected=delta(before[pool],after[pool],identity);submitted={}
        if not isinstance(rows,list):raise ReplayFault('malformed-assignment-deltas')
        for row in rows:
            exact(row,[identity,'before_sha256','after_sha256','basis_ref'],'malformed-assignment-delta');types.text(row[identity]);types.text(row['basis_ref'])
            for key in ('before_sha256','after_sha256'):
                if row[key] is not None:types.sha(row[key])
            if row[identity] in submitted:return False
            submitted[row[identity]]=[row['before_sha256'],row['after_sha256']]
        if not equal(expected,submitted,control):return False
    return True


class Denotation(e.Denotation):
    def __init__(self,declarations,model,control):self.control=control;super().__init__(declarations,model)
    def tick(self):self.control.tick();super().tick()


def assess(world,prepared,control,constraints=()):
    c.bounded_tree(world);exact(world,['records','transition'],'malformed-record-world')
    if not isinstance(world['records'],list) or len(world['records'])!=2 or any(not isinstance(row,dict) for row in world['records']) or tuple(row.get('object_id') for row in world['records'])!=w.SUBJECTS:raise ReplayFault('exact-carrier-required')
    values=[record(state,control) for state in world['records']]
    if not frame(world['transition'],world['records'],control):return {'status':'record-frame-counterexample','values':values,'theory':False,'populations':False,'queries':{}}
    for constraint in constraints:
        control.tick();active={key:any(row[key] for row in values) for key in OWNERS}
        holds={'trace-implies-position':all(not row['Traceable'] or row['Position'] for row in values),'no-position':not active['Position'],'some-position':active['Position'],'no-trace':not active['Traceable'],'no-right':not active['Right'],'no-duty':not active['Duty'],'some-right':active['Right'],'some-duty':active['Duty']}[constraint]
        if not holds:return {'status':'record-constraint-counterexample','values':values,'theory':False,'populations':False,'queries':{}}
    mapping=prepared['mapping'];model={'domains':{mapping['Record']:list(w.SUBJECTS)},'constants':{},'functions':{},'predicates':{mapping[key]:[[identity] for identity,row in zip(w.SUBJECTS,values) if row[key]] for key in OWNERS}}
    evaluator=Denotation(prepared['declarations'],model,control)
    T=all(evaluator.truth(node) for node in prepared['T'])
    if not T:return {'status':'projection-theory-counterexample','values':values,'theory':False,'populations':False,'queries':{}}
    joint=all(evaluator.truth(node) for node in prepared['I']);queries={}
    for key,node in prepared['Q'].items():
        if key=='query:consistency' or joint:queries[key]=evaluator.truth(node)
    return {'status':'candidate-model-assessed','values':values,'theory':True,'populations':joint,'queries':queries,'projection_model':model}


def load_ref(ref,captured,parse=True):
    exact(ref,['path','sha256'],'malformed-selected-reference');types.sha(ref['sha256']);raw=r.read_bytes(ROOT,ref['path'])
    if r.digest(raw)!=ref['sha256']:raise ReplayFault('stale-selected-input',ref['path'])
    if ref['path'] in captured and captured[ref['path']]!=raw:raise ReplayFault('input-read-race')
    captured[ref['path']]=raw
    return r.parse(raw,ref['path']) if parse else raw


def runtime():
    return f.current_bindings()+[{'path':path.relative_to(ROOT).as_posix(),'sha256':r.digest(path.read_bytes())} for path in [IMPL/'pilot-v2.py',IMPL/'verifier.py',IMPL/'obligations.py',IMPL/'relation-policy.py',BASE/'units/A07/pilot_spec.py',UNIT/'replay.py',UNIT/'reference_world.py']]


def prepare(selection_ref=SELECTED,live_source_root=ROOT):
    captured={};selection=load_ref(selection_ref,captured)
    exact(selection,['schema_version','authority_effect','context_ref','upstream_manifest_ref','upstream_receipt_ref','projection_ref','provider_ref','semantics_ref','source_spec_ref','require_whole_translation','require_semantic_closure','selected_scope'],'malformed-independent-selection')
    if selection['schema_version']!='definition-assurance-record-verification-selection/v2-candidate' or selection['authority_effect']!='none' or selection['selected_scope']!='scope:governance-record-projection-v2':raise ReplayFault('unsupported-record-verification-profile')
    if type(selection['require_whole_translation']) is not bool or type(selection['require_semantic_closure']) is not bool:raise ReplayFault('malformed-scope-requirement')
    context=load_ref(selection['context_ref'],captured)
    for row in context['sources']:load_ref({key:row[key] for key in ('path','sha256')},captured,False)
    manifest=load_ref(selection['upstream_manifest_ref'],captured)
    if manifest['authority_effect']!='none' or len(manifest['files'])!=362:raise ReplayFault('upstream-manifest-denominator-substitution')
    known={row['path']:row['sha256'] for row in manifest['files']}
    if len(known)!=len(manifest['files']):raise ReplayFault('duplicate-upstream-path')
    for row in manifest['files']:
        if r.digest(r.read_bytes(ROOT,row['path']))!=row['sha256']:raise ReplayFault('stale-upstream-delivery',row['path'])
    for key in ['upstream_receipt_ref','projection_ref','provider_ref','semantics_ref','source_spec_ref']:
        if known.get(selection[key]['path'])!=selection[key]['sha256']:raise ReplayFault('independent-input-selection-substitution',key)
    receipt=load_ref(selection['upstream_receipt_ref'],captured)
    for row in receipt['inputs']+receipt['outputs']:load_ref(row,captured,False)
    config=load_ref(selection['projection_ref'],captured);spec=load_ref(selection['source_spec_ref'],captured);types.bind_sources(spec,live_source_root)
    if not r.same_json(config['sources'],spec['sources']) or config['authority_effect']!='none' or config['semantic_ready'] is not False or config['source_spec_ref']!=selection['source_spec_ref'] or config['semantics_contract_ref']!=selection['semantics_ref']:raise ReplayFault('projection-source-or-boundary-substitution')
    inputs=[load_ref(row,captured) for row in config['input_ir_refs']]
    if len(inputs)!=7 or sorted(row['source']['definition_id'] for row in inputs)!=sorted(row['definition_id'] for row in spec['sources']):raise ReplayFault('missing-selected-projection-input')
    if selection['require_semantic_closure']:raise ReplayFault('missing-semantic-dependency-closure')
    if selection['require_whole_translation'] and any(row['source_fidelity']!='accepted' or any(clause['disposition']!='interpreted' for clause in row['clauses']) for row in inputs):raise ReplayFault('missing-whole-definition-translation')
    for row in config['alignment_refs']:load_ref(row,captured)
    subject=load_ref(config['subject_ref'],captured);ir.verify_composed(subject,inputs,config['alignment_refs'],ROOT)
    theory=load_ref(config['theory_ref'],captured);relations=load_ref(config['relations_ref'],captured);populations=load_ref(config['populations_ref'],captured);endpoints=load_ref(config['endpoint_bindings_ref'],captured);required=o.generate(theory,relations,populations,endpoints,ROOT);o.compare_required(required,load_ref(config['required_set_ref'],captured))
    if theory['scope']!=selection['selected_scope'] or not r.same_json(theory['sources'],spec['sources']):raise ReplayFault('theory-source-scope-substitution')
    source_by_id={row['definition_id']:row for row in spec['sources']};renaming=[]
    for local,owner in {**OWNERS,'Record':'provenance'}.items():
        source=source_by_id['cal.definition.'+owner];original=ir.qualified(source,theory['scope'],local);canonical=subject.get('sort_alignment',{}).get(original,original);renaming.append({'local_symbol_id':local,'canonical_id':canonical,'source':source})
    mapping=e.signature_map(theory,subject,inputs,renaming,endpoints)
    if not r.same_json(mapping,config['symbol_mapping']):raise ReplayFault('nominal-symbol-substitution')
    declarations=subject['declarations'];sorts={row['symbol_id']:row['symbol_id'] for row in declarations if row['kind']=='sort'};symbols={row['symbol_id']:row for row in declarations if row['kind']!='sort'}
    def formula(node):return ir.formula(e.renamed(node,mapping),sorts,symbols)
    T=[formula(node) for node in theory['statements']];Q={row['obligation_id']:formula(row['statement']) for row in required['logical_manifest']['obligations']};I=[Q[row['obligation_id']] for row in required['logical_manifest']['obligations'] if row['obligation_id'].startswith('population:')]
    native_paths={selection['projection_ref']['path']};native_context_ref=next(row for row in receipt['outputs'] if row['path'].endswith('/A08/context.json'));native_context=load_ref(native_context_ref,captured);native_paths.add(native_context_ref['path'])
    for row in native_context['sources']:native_paths.add(row['path'])
    source_receipt_path=next(row['path'] for row in native_context['sources'] if row['path'].endswith('/A07/receipt.json'));source_receipt=r.parse(captured[source_receipt_path],source_receipt_path)
    for row in source_receipt['outputs']:load_ref(row,captured,False);native_paths.add(row['path'])
    for key in ['source_spec_ref','subject_ref','semantics_contract_ref','theory_ref','relations_ref','populations_ref','endpoint_bindings_ref','required_set_ref']:native_paths.add(config[key]['path'])
    for key in ['input_ir_refs','alignment_refs']:native_paths.update(row['path'] for row in config[key])
    native_input_hash=ir.digest({path:r.digest(captured[path]) for path in native_paths})
    selected_runtime=runtime();native_runtime=f.current_bindings()+[selection['provider_ref']]
    return {'selection':selection,'selection_ref':dict(selection_ref),'live_source_root':live_source_root,'spec':spec,'config':config,'captured':captured,'mapping':mapping,'declarations':declarations,'T':T,'I':I,'Q':Q,'required':required,'runtime':selected_runtime,'native_runtime':native_runtime,'native_input_hash':native_input_hash,'provider_prepared':{'config':config,'typed':{'declarations':declarations,'T':T,'I':I,'Q':Q}}}


def verify_bindings(prepared):
    for path,raw in prepared['captured'].items():
        if r.read_bytes(ROOT,path)!=raw:raise ReplayFault('input-changed-during-replay',path)
    types.bind_sources(prepared['spec'],prepared['live_source_root'])
    if not r.same_json(runtime(),prepared['runtime']):raise ReplayFault('runtime-or-checker-changed-during-replay')


def request(constraints,start,stop):
    c.bounded_tree({'constraints':constraints,'start':start,'stop':stop})
    if not isinstance(constraints,list) or any(not isinstance(value,str) for value in constraints) or len(set(constraints))!=len(constraints) or set(constraints)-CONSTRAINTS:raise ReplayFault('unsupported-record-constraint')
    if type(start) is not int or type(stop) is not int or not 0<=start<stop<=w.TOTAL:raise ReplayFault('invalid-exact-rank-interval')


def audit(start=0,stop=w.TOTAL,constraints=None,prepared=None,budgets=None,cancelled=None):
    constraints=[] if constraints is None else constraints;control=None;limits=None;valid=False;complete=False;epoch=None;counts={'visited':0,'theory_models':0,'joint_models':0};queries={};chain=hashlib.sha256();diagnostics=[];currentness='not-verified'
    base={'schema_version':'definition-assurance-record-range-audit/v2-candidate','authority_effect':'none','semantic_ready':False,'unbounded_conclusion':None,'source_fidelity':'pending','semantic_dependency_closure':'unresolved','mechanized_proof':False}
    def result(status):
        value={**base,'status':status,'exhaustion_complete':complete,'required_denominator_status':'resolved' if epoch else 'unresolved-no-evidence-emitted','range':[start,stop] if valid else None,'counts':{**counts,'evaluation_steps':control.steps if control else 0},'query_counts':queries,'diagnostics':diagnostics,'coverage_chain_sha256':chain.hexdigest(),'input_epoch':epoch,'source_runtime_currentness':currentness,'limits':limits,'claim_ceiling':'Independent finite record/AST values and implementation agreement in this exact interval; no source-owner fidelity or unbounded theorem.'}
        if limits and len(ir.canonical(value))>limits['max_output_bytes']:return {**base,'status':'resource-limit','exhaustion_complete':False,'range':value['range'],'counts':value['counts'],'query_counts':{key:{'true_models':None,'first_rank':None} for key in queries},'diagnostics':[{'code':'output-byte-limit'}],'input_epoch':epoch,'required_denominator_status':value['required_denominator_status']}
        return value
    def invalidate_queries():return {key:{'true_models':None,'first_rank':None} for key in queries}
    try:
        limits=f.load_limits(budgets);control=Control(limits,cancelled);request(constraints,start,stop);valid=True
        if limits['max_domain_cardinality']<2:raise ReplayFault('exact-carrier-exceeds-budget')
        control.poll();prepared=prepare() if prepared is None else prepared;control.poll()
        epoch={'selection_ref':prepared['selection_ref'],'required_set_sha256':prepared['required']['required_set_sha256'],'constraints_sha256':ir.digest(constraints),'runtime_sha256':ir.digest(prepared['runtime']),'inputs_sha256':ir.digest({path:r.digest(raw) for path,raw in prepared['captured'].items()})}
        queries={key:{'true_models':0,'first_rank':None} for key in prepared['Q']}
        for rank in range(start,stop):
            control.poll()
            if counts['visited']>=limits['max_interpretations']:raise Stop('configuration-limit')
            world=w.world(rank);generated=provider.point(rank)
            if not equal(world,generated,control):raise ReplayFault('configuration-enumeration-disagreement',str(rank))
            actual=assess(world,prepared,control,constraints);observed=provider.assess(generated,prepared['provider_prepared'],control,constraints)
            if not equal(actual,observed,control):raise ReplayFault('record-or-logical-denotation-disagreement',str(rank))
            counts['visited']+=1;counts['theory_models']+=actual['theory'];counts['joint_models']+=actual['populations']
            for key,truth in actual['queries'].items():
                if truth:
                    queries[key]['true_models']+=1
                    if queries[key]['first_rank'] is None:queries[key]['first_rank']=rank
            chain.update(ir.canonical({'rank':rank,'world_sha256':ir.digest(world),'reference':actual})+b'\n')
        verify_bindings(prepared);currentness='verified-at-final-read';control.poll();complete=True
        return result('independently-exhausted-record-range')
    except Stop as error:
        diagnostics=[{'code':error.code}]
        if prepared:
            try:verify_bindings(prepared);currentness='verified-at-final-read'
            except (ReplayFault,types.SemanticFault,r.CaptureFault,f.ProviderFault,OSError) as stale:
                queries=invalidate_queries();diagnostics=[{'code':getattr(stale,'code',type(stale).__name__)}];currentness='failed-final-read';return result('unresolved-input-or-binding')
        return result(error.code if error.code in {'timeout','cancelled'} else 'resource-limit')
    except (ReplayFault,types.SemanticFault,r.CaptureFault,e.VerificationFault,ir.IRFault,o.ObligationFault,o.p.PolicyFault,c.InputError,f.ProviderFault) as error:
        queries=invalidate_queries();diagnostics=[{'code':error.code,'path':error.path}]
        return result('unresolved-input-or-binding' if any(word in error.code for word in ('missing','stale','changed')) or isinstance(error,r.CaptureFault) else 'unsupported' if 'unsupported' in error.code else 'verification-failed')
    except (OSError,KeyError,ValueError,TypeError,AttributeError,IndexError,MemoryError,RecursionError) as error:
        queries=invalidate_queries();diagnostics=[{'code':type(error).__name__}];return result('verifier-error')


def merge(reports,start=0,stop=w.TOTAL,constraints=None,prepared=None):
    """Validate aggregation metadata; range truth still needs actual replay."""
    constraints=[] if constraints is None else constraints
    prepared=prepare() if prepared is None else prepared
    expected_epoch={'selection_ref':prepared['selection_ref'],'required_set_sha256':prepared['required']['required_set_sha256'],'constraints_sha256':ir.digest(constraints),'runtime_sha256':ir.digest(prepared['runtime']),'inputs_sha256':ir.digest({path:r.digest(raw) for path,raw in prepared['captured'].items()})}
    request([],start,stop)
    if not isinstance(reports,list) or not reports:raise ReplayFault('missing-range-evidence')
    rows=sorted(reports,key=lambda row:row['range'][0] if isinstance(row.get('range'),list) else -1);cursor=start;epoch=rows[0].get('input_epoch');total={'visited':0,'theory_models':0,'joint_models':0,'evaluation_steps':0};queries={}
    for row in rows:
        if row.get('schema_version')!='definition-assurance-record-range-audit/v2-candidate' or row.get('authority_effect')!='none' or row.get('semantic_ready') is not False or row.get('unbounded_conclusion') is not None or row.get('status')!='independently-exhausted-record-range' or row.get('exhaustion_complete') is not True or row.get('source_runtime_currentness')!='verified-at-final-read':raise ReplayFault('incomplete-or-invalid-range-evidence')
        interval=row.get('range')
        if not isinstance(interval,list) or len(interval)!=2 or any(type(value) is not int for value in interval) or interval[0]!=cursor or not cursor<interval[1]<=stop:raise ReplayFault('range-gap-overlap-or-outside-scope')
        if not r.same_json(expected_epoch,row['input_epoch']) or not r.same_json(epoch,row['input_epoch']):raise ReplayFault('mixed-range-input-epochs')
        if set(row['query_counts'])!=set(prepared['Q']):raise ReplayFault('range-query-denominator-substitution')
        types.sha(row['coverage_chain_sha256'])
        if row['counts']['visited']!=interval[1]-interval[0] or any(type(value) is not int or value<0 for value in row['counts'].values()):raise ReplayFault('range-count-substitution')
        if not (row['counts']['joint_models']<=row['counts']['theory_models']<=row['counts']['visited']):raise ReplayFault('range-count-substitution')
        if queries and set(queries)!=set(row['query_counts']):raise ReplayFault('range-query-denominator-substitution')
        for key,value in row['query_counts'].items():
            if type(value['true_models']) is not int or not 0<=value['true_models']<=row['counts']['theory_models']:raise ReplayFault('range-query-count-substitution')
            rank=value['first_rank']
            if (value['true_models']==0)!=(rank is None) or rank is not None and (type(rank) is not int or not interval[0]<=rank<interval[1]):raise ReplayFault('range-first-witness-substitution')
            target=queries.setdefault(key,{'true_models':0,'first_rank':None});target['true_models']+=value['true_models']
            if target['first_rank'] is None:target['first_rank']=rank
        for key in total:total[key]+=row['counts'][key]
        cursor=interval[1]
    if cursor!=stop:raise ReplayFault('range-cover-incomplete')
    return {'schema_version':'definition-assurance-record-coverage/v2-candidate','authority_effect':'none','semantic_ready':False,'status':'aggregate-of-independent-finite-range-audits','range':[start,stop],'exhaustion_complete':True,'input_epoch':epoch,'counts':total,'query_counts':queries,'range_runs':len(rows),'unbounded_conclusion':None,'claim_ceiling':'Gap-free finite aggregation, conditional on actual byte-bound range execution/replay. Aggregation is not a kernel proof; per-run caps are not a single-run budget claim.'}


def verify_native(native,request_data,prepared):
    c.bounded_tree(native);constraints=request_data.get('constraints',[]);start=request_data.get('start',0);stop=request_data.get('stop',w.TOTAL);mode=request_data.get('mode','first-evidence');request(constraints,start,stop)
    if native.get('schema_version')!='definition-assurance-governance-search/v2-candidate' or native.get('authority_effect')!='none' or native.get('semantic_ready') is not False or native.get('unbounded_conclusion') is not None or native.get('source_fidelity')!='pending':raise ReplayFault('native-claim-boundary-substitution')
    if native.get('required_denominator_status')=='unresolved-no-evidence-emitted':
        if native.get('status') not in ('timeout','cancelled') or native.get('query_results') or native.get('input_bindings') is not None:raise ReplayFault('unresolved-native-denominator-substitution')
        return {'status':'checked-no-evidence-control','native_status':native['status'],'queries':[],'semantic_ready':False,'authority_effect':'none'}
    rows=native.get('query_results')
    if not isinstance(rows,list) or len(rows)!=len(prepared['Q']) or {row['obligation_id'] for row in rows}!=set(prepared['Q']):raise ReplayFault('native-required-denominator-substitution')
    expected={'required_set_sha256':prepared['required']['required_set_sha256'],'constraints_sha256':ir.digest(constraints),'projection_inputs_sha256':prepared['native_input_hash'],'request_sha256':ir.digest({'constraints':constraints,'mode':mode,'start':start,'stop':stop}),'implementation_sha256':ir.digest(prepared['native_runtime'])}
    if not r.same_json(expected,native.get('input_bindings')):raise ReplayFault('native-input-binding-substitution')
    if 'implementation_bindings' in native and not r.same_json(native['implementation_bindings'],prepared['native_runtime']):raise ReplayFault('native-provider-runtime-substitution')
    control=Control(f.load_limits());results=[]
    for row in rows:
        witness=row.get('witness')
        if witness is None:
            if row.get('strength') not in ('none','bounded-exhaustion'):raise ReplayFault('native-uncheckable-strength')
            results.append({'obligation_id':row['obligation_id'],'status':'finite-exhaustion-needs-independent-range-evidence' if row.get('strength')=='bounded-exhaustion' else 'checked-no-model-evidence','strength':'none'})
            continue
        if row.get('status')!='witness-found' or row.get('strength')!='model-witness':raise ReplayFault('native-witness-strength-substitution')
        exact(witness,['rank','model','model_sha256','projection_model','projection_model_sha256'],'malformed-native-witness')
        rank=witness['rank']
        if type(rank) is not int or not start<=rank<stop or not r.same_json(w.world(rank),witness['model']) or ir.digest(witness['model'])!=witness['model_sha256']:raise ReplayFault('native-witness-rank-or-byte-substitution')
        actual=assess(witness['model'],prepared,control,constraints)
        if not actual['theory'] or actual['queries'].get(row['obligation_id']) is not True:raise ReplayFault('native-witness-fails-independent-query')
        if not r.same_json(actual['projection_model'],witness['projection_model']) or ir.digest(witness['projection_model'])!=witness['projection_model_sha256']:raise ReplayFault('native-projection-model-substitution')
        results.append({'obligation_id':row['obligation_id'],'status':'independently-checked-record-model-witness','strength':'model-witness','rank':rank,'model_sha256':witness['model_sha256'],'projection_model_sha256':witness['projection_model_sha256'],'mechanized_proof':False})
    verify_bindings(prepared)
    return {'status':'independently-checked-native-record-evidence','native_status':native['status'],'authority_effect':'none','semantic_ready':False,'queries':results,'steps':control.steps,'unbounded_conclusion':None}
