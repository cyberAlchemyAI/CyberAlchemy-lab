"""Run actual independent finite coverage and retained/adversarial controls."""
import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path
UNIT=Path(__file__).resolve().parent;sys.path.insert(0,str(UNIT));import replay as a


def ref(path):return {'path':path.relative_to(a.ROOT).as_posix(),'sha256':a.r.digest(path.read_bytes())}


def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
    return ref(path)


def probe(fn):
    try:fn()
    except (a.ReplayFault,a.types.SemanticFault,a.r.CaptureFault,a.c.InputError) as error:
        return {'authority_effect':'none','semantic_ready':False,'status':'unresolved-input-or-binding' if any(word in error.code for word in ['missing','stale','changed']) or isinstance(error,a.r.CaptureFault) else 'unsupported' if 'unsupported' in error.code else 'verification-failed','diagnostics':[{'code':error.code,'path':error.path}],'logical_evidence':None,'unbounded_conclusion':None}
    raise RuntimeError('Negative control unexpectedly succeeded')


def stale_source(prepared):
    spec=prepared['spec'];snapshot=json.loads((a.ROOT/spec['snapshot_ref']['path']).read_bytes())
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        for row in snapshot['captured_files']+[spec['snapshot_ref']]:
            path=root/row['path'];path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a.ROOT/row['path'],path)
        a.types.bind_sources(spec,root);source=spec['sources'][0];path=root/source['path'];path.write_bytes(path.read_bytes()+b'\n');changed=a.r.digest(path.read_bytes());result=probe(lambda:a.types.bind_sources(spec,root))
        return {**result,'fixture':'isolated copy of all201 captured source files and snapshot; changed first selected source by one newline','expected_source':source,'changed_sha256':changed,'live_source_mutated':False}


def native_exhaustion(native,coverage):
    if not native.get('exhaustion_complete') or not coverage.get('exhaustion_complete') or native['finite_scope']['rank_interval']!=coverage['range']:raise ValueError('Exhaustion interval mismatch')
    for key in ['visited','theory_models','joint_models']:
        if native['counts'][key]!=coverage['counts'][key]:raise ValueError('Exhaustion model count disagreement')
    values=[]
    for row in native['query_results']:
        count=coverage['query_counts'][row['obligation_id']]['true_models']
        if row['witness'] is None:
            expected='bounded-no-theory-model' if not coverage['counts']['theory_models'] else 'bounded-no-joint-population-model' if not coverage['counts']['joint_models'] and row['obligation_id']!='query:consistency' else 'bounded-no-witness'
            if count or row['status']!=expected or row['strength']!='bounded-exhaustion':raise ValueError('Native absence claim disagrees with independently covered range')
            values.append({'obligation_id':row['obligation_id'],'status':'independently-checked-bounded-absence','strength':'bounded-exhaustion','range':coverage['range'],'unbounded_conclusion':None})
        elif not count:raise ValueError('Witness absent from independently covered range')
    return values


def main():
    name=sys.argv[1] if len(sys.argv)>1 else 'run-001'
    if name not in ('run-001','run-002','run-003'):raise ValueError('Explicit bounded run name required')
    run=UNIT/name;run.mkdir();prepared=a.prepare();code=[ref(path) for path in [UNIT/'run_replay.py',UNIT/'replay.py',UNIT/'reference_world.py']]
    put(run/'started.json',{'authority_effect':'none','selection_ref':a.SELECTED,'implementation_bindings':prepared['runtime'],'runner_code_bindings':code,'status':'running-candidate','native_baseline':'A08 externally byte-selected retained evidence','finite_product':8640,'range_size':120,'run_name':name})
    def ranges(label,start,stop,constraints):
        reports=[];refs=[]
        for left in range(start,stop,120):
            right=min(left+120,stop);result=a.audit(left,right,constraints,prepared=prepared);path=run/'ranges'/label/(str(left).zfill(5)+'-'+str(right).zfill(5)+'.json');refs.append(put(path,result));reports.append(result)
            print(json.dumps({'scope':label,'range':[left,right],'status':result['status'],'counts':result['counts']}),flush=True)
            if result['status']!='independently-exhausted-record-range':
                put(run/'failed.json',{'status':'incomplete-independent-run','failed_range_ref':refs[-1],'preserved_ranges':refs,'authority_effect':'none'});raise RuntimeError('Independent range did not complete; preserve run and investigate')
        coverage=a.merge(reports,start,stop,constraints,prepared);coverage_ref=put(run/(label+'-coverage.json'),coverage)
        return coverage,{'coverage_ref':coverage_ref,'range_refs':refs,'constraints':constraints,'start':start,'stop':stop}
    baseline,baseline_index=ranges('baseline',0,a.w.TOTAL,[])
    native_index=json.loads((a.BASE/'units/A08/worked-controls.json').read_bytes());native_reports=[];bounded_indexes=[]
    for row in native_index['searches']:
        value=a.load_ref(row['result_ref'],{},True);checked=a.verify_native(value,row['request'],prepared);case=row['case_id']
        if value.get('exhaustion_complete'):
            request=row['request'];coverage,index=ranges(case,request.get('start',0),request.get('stop',a.w.TOTAL),request.get('constraints',[]));checked['independently_checked_absence']=native_exhaustion(value,coverage);checked['coverage_ref']=index['coverage_ref'];bounded_indexes.append({'case_id':case,**index})
        checked_ref=put(run/'native-controls'/(case+'.json'),checked);native_reports.append({'case_id':case,'native_ref':row['result_ref'],'request':row['request'],'check_ref':checked_ref})
    record_ref=native_index['record_transition_ref'];original=a.load_ref(record_ref,{});records=[];moves=[]
    for row in original['record_cases']:
        actual=a.record(row['state'],a.Control(a.f.load_limits()))
        if not a.r.same_json(actual,row['actual']):raise ValueError('Worked record denotation disagreement')
        records.append({'case_id':row['case_id'],'independent':actual})
    for row in original['transition_cases']:
        actual=a.frame(row['model']['transition'],row['model']['records'],a.Control(a.f.load_limits()))
        if actual!=row['transition_holds']:raise ValueError('Worked transition denotation disagreement')
        moves.append({'case_id':row['case_id'],'independent':actual})
    worked_ref=put(run/'record-transition-replay.json',{'authority_effect':'none','semantic_ready':False,'source_ref':record_ref,'records':records,'moves':moves})
    adversarial=[]
    def retain(case,value,expected):
        if value['status']!=expected:raise ValueError('Wrong control outcome: '+case+': '+value['status'])
        adversarial.append({'case_id':case,'result_ref':put(run/'adversarial'/(case+'.json'),value),'expected_status':expected})
        print(json.dumps({'control':case,'status':value['status']}),flush=True)
    original_selection=json.loads((a.ROOT/a.SELECTED['path']).read_bytes())
    for case,field,value,expected in [('missing-dependency-closure','require_semantic_closure',True,'unresolved-input-or-binding'),('missing-whole-translation','require_whole_translation',True,'unresolved-input-or-binding'),('unsupported-profile','selected_scope','scope:unsupported','unsupported')]:
        selected={**original_selection,field:value};selected_ref=put(run/'adversarial'/(case+'-selection.json'),selected);result=probe(lambda:a.prepare(selected_ref));retain(case,{**result,'selected_ref':selected_ref},expected)
    retain('stale-source',stale_source(prepared),'unresolved-input-or-binding')
    retain('malformed-request',a.audit(stop=3,constraints=[[]],prepared=prepared),'unsupported')
    retain('real-timeout',a.audit(stop=3,prepared=prepared,budgets={'timeout_seconds':0.000000001}),'timeout')
    calls=[0]
    def cancel():calls[0]+=1;return calls[0]>150
    retain('real-cancellation',a.audit(stop=6,prepared=prepared,cancelled=cancel),'cancelled')
    retain('configuration-limit',a.audit(stop=3,prepared=prepared,budgets={'max_interpretations':1}),'resource-limit')
    retain('step-limit',a.audit(stop=3,prepared=prepared,budgets={'max_evaluation_steps':1}),'resource-limit')
    native=json.loads((a.BASE/'units/A08/positive-search.json').read_bytes());mutated=copy.deepcopy(native);mutated['query_results'][0]['witness']['rank']=79;fixture=put(run/'adversarial/substituted-rank-native.json',mutated);retain('substituted-witness',{**probe(lambda:a.verify_native(mutated,{},prepared)),'fixture_ref':fixture},'verification-failed')
    a.verify_bindings(prepared)
    for row in code:
        if a.r.digest((a.ROOT/row['path']).read_bytes())!=row['sha256']:raise ValueError('Run/checker code changed')
    index={'schema_version':'definition-assurance-independent-pilot-run/v2-candidate','authority_effect':'none','semantic_ready':False,'status':'actual-independent-run-complete','selection_ref':a.SELECTED,'runner_code_bindings':code,'baseline':baseline_index,'native_controls':native_reports,'bounded_control_ranges':bounded_indexes,'record_transition_ref':worked_ref,'adversarial_controls':adversarial,'counts':baseline['counts'],'required_logical_queries':11,'pending_gates':11,'finite_configurations':8640,'unbounded_conclusion':None,'owner_fidelity':'pending','semantic_dependency_closure':'unresolved','whole_definition_proofs':0,'goal_status':'active','next_unit':'A10.1'}
    put(run/'run-index.json',index);print(json.dumps({'status':index['status'],'baseline_counts':baseline['counts'],'range_runs':baseline['range_runs'],'native_controls':len(native_reports),'adversarial_controls':len(adversarial),'goal_status':'active'}),flush=True)


if __name__=='__main__':main()
