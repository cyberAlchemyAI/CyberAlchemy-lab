"""Verify selected run bytes and rerun every claimed finite configuration."""
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;sys.path.insert(0,str(UNIT));import replay as a
import run_replay as h


def load(ref):return a.load_ref(ref,{})


def verify(index_ref,fresh_ranges=True):
    index=load(index_ref);prepared=a.prepare()
    if index['schema_version']!='definition-assurance-independent-pilot-run/v2-candidate' or index['authority_effect']!='none' or index['semantic_ready'] is not False or index['status']!='actual-independent-run-complete' or index['selection_ref']!=a.SELECTED:raise ValueError('Invalid run authority/input boundary')
    for row in index['runner_code_bindings']:a.load_ref(row,{},False)
    range_runs=0;range_points=0
    def coverage(selected):
        nonlocal range_runs,range_points
        rows=[]
        for ref in selected['range_refs']:
            row=load(ref);rows.append(row)
            if fresh_ranges:
                fresh=a.audit(row['range'][0],row['range'][1],selected['constraints'],prepared=prepared)
                if not a.r.same_json(fresh,row):raise ValueError('Fresh configuration replay mismatch: '+ref['path']+' '+fresh['status'])
            range_runs+=1;range_points+=row['counts']['visited']
            if fresh_ranges and range_runs%12==0:print(json.dumps({'verification':'fresh-range-replay','range_runs':range_runs,'configurations':range_points}),flush=True)
        actual=a.merge(rows,selected['start'],selected['stop'],selected['constraints'],prepared)
        if not a.r.same_json(actual,load(selected['coverage_ref'])):raise ValueError('Coverage aggregation differs from selected bytes')
        return actual
    baseline=coverage(index['baseline'])
    if baseline['range']!=[0,8640] or baseline['counts']['visited']!=8640 or baseline['counts']['theory_models']!=5760 or baseline['counts']['joint_models']!=1296 or baseline['range_runs']!=72:raise ValueError('Finite product/inhabitation denominator mismatch')
    bounded={row['case_id']:coverage(row) for row in index['bounded_control_ranges']}
    native_checks={}
    for row in index['native_controls']:
        native=load(row['native_ref']);actual=a.verify_native(native,row['request'],prepared)
        if native.get('exhaustion_complete'):
            actual['independently_checked_absence']=h.native_exhaustion(native,bounded[row['case_id']]);actual['coverage_ref']=next(item['coverage_ref'] for item in index['bounded_control_ranges'] if item['case_id']==row['case_id'])
        if not a.r.same_json(actual,load(row['check_ref'])):raise ValueError('Native evidence replay mismatch')
        native_checks[row['case_id']]=actual
    record=load(index['record_transition_ref']);source=load(record['source_ref'])
    expected_records=[{'case_id':row['case_id'],'independent':a.record(row['state'],a.Control(a.f.load_limits()))} for row in source['record_cases']]
    expected_moves=[{'case_id':row['case_id'],'independent':a.frame(row['model']['transition'],row['model']['records'],a.Control(a.f.load_limits()))} for row in source['transition_cases']]
    if not a.r.same_json(record['records'],expected_records) or not a.r.same_json(record['moves'],expected_moves):raise ValueError('Worked denotation replay mismatch')
    for row in index['adversarial_controls']:
        stored=load(row['result_ref']);case=row['case_id']
        if case in ['missing-dependency-closure','missing-whole-translation','unsupported-profile']:actual={**h.probe(lambda:a.prepare(stored['selected_ref'])),'selected_ref':stored['selected_ref']}
        elif case=='stale-source':actual=h.stale_source(prepared)
        elif case=='malformed-request':actual=a.audit(stop=3,constraints=[[]],prepared=prepared)
        elif case=='real-timeout':actual=a.audit(stop=3,prepared=prepared,budgets={'timeout_seconds':0.000000001})
        elif case=='real-cancellation':
            calls=[0]
            def cancel():calls[0]+=1;return calls[0]>150
            actual=a.audit(stop=6,prepared=prepared,cancelled=cancel)
        elif case=='configuration-limit':actual=a.audit(stop=3,prepared=prepared,budgets={'max_interpretations':1})
        elif case=='step-limit':actual=a.audit(stop=3,prepared=prepared,budgets={'max_evaluation_steps':1})
        elif case=='substituted-witness':actual={**h.probe(lambda:a.verify_native(load(stored['fixture_ref']),{},prepared)),'fixture_ref':stored['fixture_ref']}
        else:raise ValueError('Unknown independent control')
        if not a.r.same_json(stored,actual) or actual['status']!=row['expected_status']:raise ValueError('Independent adversarial control replay mismatch: '+case)
    a.verify_bindings(prepared)
    return {'authority_effect':'none','semantic_ready':False,'status':'PASS','verification_scope':'Externally byte-selected actual range output, exact gap-free aggregation, native record/model/AST evidence and adversarial controls; all ranges freshly rerun.' if fresh_ranges else 'Byte-selected aggregate and native/adversarial rechecks; full ranges not rerun in this invocation.','baseline_configurations':8640,'baseline_theory_models':5760,'baseline_joint_models':1296,'range_runs':range_runs,'range_configurations':range_points,'fresh_range_replay':fresh_ranges,'checked_existential_witnesses':len([row for row in native_checks['positive']['queries'] if row['strength']=='model-witness']),'native_controls':len(native_checks),'adversarial_controls':len(index['adversarial_controls']),'record_cases':len(expected_records),'transition_cases':len(expected_moves),'source_binding':a.types.bind_sources(prepared['spec'],a.ROOT),'source_fidelity':'pending','semantic_dependency_closure':'unresolved','unbounded_conclusion':None,'whole_definition_proofs':0,'goal_status':'active','next_unit':'A10.1'}


if __name__=='__main__':
    path=UNIT/(sys.argv[1] if len(sys.argv)>1 else 'run-001')/'run-index.json'
    print(json.dumps(verify(h.ref(path)),indent=2,sort_keys=True))
