"""Aggregate only completed actual worker reports for all original methods."""
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v96'
PLAN=RUN/'API96-class-worker-plan-0140.json'
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    assert binding(PLAN)['sha256']=='bb222638d482c7ddff50f571e25cd249f11eb25064f83e4ee60da55ba59a375f'
    plan=json.loads(PLAN.read_bytes())
    paths=[RUN/'API96-sequential-first-class-0140.json',*[RUN/f'API96-worker-{i}-0140.json' for i in range(8)]]
    missing=[p.name for p in paths if not p.exists()]
    if missing:
        print(json.dumps({'result':'PENDING','missing_reports':missing}));return 2
    cases=[];problems=[]
    for i,p in enumerate(paths):
        report=json.loads(p.read_bytes())
        expected=plan['sequential_first_class'] if i==0 else plan['workers'][str(i-1)]
        assert set(report['selected_methods'])==set(expected)
        assert report['actual_methods']==len(expected)
        assert report['authority_effect']=='none' and report['actual_owner_outcome'] is None
        for row in report['files']:
            assert binding(ROOT/row['path'])==row,'report source changed: '+row['path']
        if i==0:assert report['independent_source_guard_after_process_exit']
        else:
            assert report['source_guarded_exit_completed']
            assert report['worker_plan_binding']==binding(PLAN)
            assert report['files'][0]==binding(API/'source-manifest.json')
            assert report['files'][1]==binding(API/'contract-profile.json')
        actual=[]
        for case in report['cases']:
            test=case['test'].split('.',1)[1]
            module,cls,method=test.split('.')
            ident=module+'.py:'+cls+'.'+method
            actual.append(ident);cases.append({**case,'declared_method':ident,'worker_report_binding':binding(p)})
        assert set(actual)==set(expected) and len(actual)==len(set(actual))
        if report['result']!='PASS' or any(c['result']!='PASS' for c in report['cases']):problems.append(p.name)
    assert len(cases)==323 and {c['declared_method'] for c in cases}==set(plan['all_declared_methods'])
    spec=importlib.util.spec_from_file_location('_API96_aggregate_original_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard);guard.verify(plan['source_sha256'])
    assert binding(API/'source-manifest.json')['sha256']==plan['source_sha256']
    assert binding(API/'contract-profile.json')['sha256']==plan['profile_sha256']
    value={'schema_version':'lab-actual-declared-api-worker-qualification/v1-candidate','result':'FAIL' if problems else 'PASS',
           'actual_methods':323,'cases':cases,'failed_worker_reports':problems,
           'selected_methods':plan['all_declared_methods'],'original_clocks_or_callbacks_changed':False,
           'source_guarded_exit_completed':True,'files':[binding(p) for p in [PLAN,*paths,API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve()]],
           'task_complete':False,'goal_complete':False,'authority_effect':'none','actual_owner_outcome':None,
           'claim_ceiling':'All 323 original declared API96 methods only. No successor API qualification, missing handler, human usefulness, owner admission or whole Lab completion inferred.'}
    out=RUN/'API96-all-workers-0140.json'
    with out.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':value['result'],'actual_methods':323,'report_binding':binding(out)}));return 1 if problems else 0
if __name__=='__main__':raise SystemExit(main())
