"""Bind actual workflow closure, expired fixture evidence and resolver candidate."""
import hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v75'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
    parent_path=BASE/'api-v74/receipts/R03-0109.json';parent=load(parent_path)
    rows={r['path']:r for r in parent['files']}
    for r in load(API/'source-manifest.json')['files']:rows[r['path']]=r
    paths=[parent_path,API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve(),RUN/'run-API75-reference-focused-0001.py']
    outcomes={}
    for name,report_path,terminal in [('workflow_full',BASE/'api-v74/receipts/workflow-composition-full-checks-0001.json',RUN/'API74-workflow-full-terminal-0001.json'),('Machine_read',RUN/'API74-machine-read-diagnosis-0001.json',RUN/'API74-machine-read-focused-terminal-0001.json')]:
        report=load(report_path);term=load(terminal);assert term['report_binding']==bind(report_path)
        assert term['actual_exit_code']==(0 if report['result']=='PASS' else 1)
        for r in report['files']:rows[r['path']]=r
        paths.extend([report_path,terminal])
        for key in ('producer_binding','log_binding'):
            if key in term:rows[term[key]['path']]=term[key]
        outcomes[name]={'result':report['result'],'actual_cases':report['actual_cases'],'errors':report['errors'],'failures':report['failures'],'report_binding':bind(report_path),'terminal_binding':bind(terminal)}
    assert outcomes['workflow_full']['result']=='PASS' and outcomes['workflow_full']['actual_cases']==3
    focused_path=API/'receipts/carrier-reference-focused-checks-0001.json';focused=None
    if focused_path.exists():
        focused=load(focused_path)
        for r in focused['files']:rows[r['path']]=r
        paths.extend([focused_path,RUN/'API75-reference-focused-terminal-0001.json'])
        assert load(paths[-1])['report_binding']==bind(focused_path)
    for p in paths:r=bind(p);rows[r['path']]=r
    for r in rows.values():assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
    value={**parent,'result':'PASS','files':[rows[k] for k in sorted(rows)],'parent_progress_binding':bind(parent_path),'current_API_version':75,'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'API74_workflow_full_selected_qualified':True,'API74_current_Machine_read_qualified':False,'current_source_Machine_read_outcome':outcomes['Machine_read'],'current_full_workflow_outcome':outcomes['workflow_full'],
        'Machine_fixture_period_expired':True,'Machine_historical_full_suite_cause_established':False,'Machine_fixture_successor_required':True,'existing_periods_or_grants_extended':False,
        'carrier_reference_candidate_authored':True,'carrier_reference_focused_result':None if focused is None else focused['result'],'carrier_reference_current_active_process':46471 if focused is None else None,
        'generated_candidate_prepare_runtime_qualified':False,'generic_challenge_review_workflow_qualified':False,'workflow_followon_active_process':None,'workflow_focused_active_process':None,
        'remaining_obligations':['Qualify the actual independently selected API75 three-carrier reference resolver and original affected selections.','Construct and qualify a new independently bounded signed participation fixture with fresh identities, then rerun current Machine and termination checks; preserve all expired predecessors.',*parent['remaining_obligations']],
        'change':'API74 complete three-case composition suite passed nine calls. Current Machine failed during setup because the signed participation period expired. API75 declares and implements three independently selected carrier reference checks with a closed evidence schema; exact runtime outcome is recorded only when completed.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False,'claim_ceiling':'Exact source74 workflow and current fixture refusal evidence plus source75 resolver construction/available focused observations only. No complete API, current Machine, owner outcome, admission or activation.'}
    path=API/'receipts/R03-0110.json';path.parent.mkdir(exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),'carrier_reference_focused_result':value['carrier_reference_focused_result'],'goal_complete':False}),flush=True)
if __name__=='__main__':main()
