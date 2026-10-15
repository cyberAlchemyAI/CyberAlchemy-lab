"""Bind current generated workflow proofs without completing R03 or the Lab plan."""
import hashlib,json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v71'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    parent_path=BASE/'api-v68/receipts/R03-0106.json';parent=load(parent_path);source=load(API/'source-manifest.json');profile=load(API/'contract-profile.json')
    assert len(profile['implemented_operations'])==21 and parent['unimplemented_public_operation_count']==13
    rows={r['path']:r for r in parent['files']}
    for row in source['files']:rows[row['path']]=row
    outcomes=[]
    for version,kind,scope,terminal_name in (
        (69,'generated','focused','API69-generated-focused-terminal-0001.json'),
        (70,'generated','focused','API70-generated-focused-terminal-0001.json'),
        (71,'generated','focused','API71-generated-focused-terminal-0001.json'),
        (71,'generated','full','API71-generated-full-terminal-0001.json'),
        (71,'challenge','full','API71-challenge-full-terminal-0001.json')):
        folder=BASE/f'api-v{version}';path=folder/f'receipts/{kind}-{scope}-checks-0001.json'
        if not path.exists():continue
        proof=load(path);terminal_path=RUN/terminal_name;terminal=load(terminal_path)
        assert proof['source_sha256']==bind(folder/'source-manifest.json')['sha256'] and proof['profile_sha256']==bind(folder/'contract-profile.json')['sha256']
        assert terminal['report_binding']==bind(path) and terminal['actual_exit_code']==(0 if proof['result']=='PASS' else 1)
        assert proof['whole_API_qualified'] is False and proof['canonical_admissions_applied']==0
        for row in proof['files']+[bind(path),bind(terminal_path)]:rows[row['path']]=row
        for key in ('producer_binding','log_binding'):
            if key in terminal:row=terminal[key];rows[row['path']]=row
        outcomes.append({'version':version,'kind':kind,'scope':scope,'result':proof['result'],'actual_cases':proof['actual_cases'],
            'actual_public_calls':proof['actual_public_calls'],'failures':proof['failures'],'errors':proof['errors'],'report_binding':bind(path),'terminal_binding':bind(terminal_path)})
    assert any(o['version']==71 for o in outcomes),'current selected actual evidence required'
    generated=next((o for o in outcomes if o['version']==71 and o['kind']=='generated' and o['scope']=='full'),None)
    challenge=next((o for o in outcomes if o['version']==71 and o['kind']=='challenge'),None)
    for path in (parent_path,API/'source-manifest.json',API/'contract-profile.json',Path(__file__).resolve(),RUN/'run-API71-generated-qualification-0001.py',RUN/'GENERATED-CONSUMER-INTEGRATION-ANALYSIS-0001.md',RUN/'CARRIER-REFERENCE-RESOLUTION-ANALYSIS-0001.md',RUN/'RUNTIME-CLOSURE-ANALYSIS-0001.md',RUN/'diagnose-API50-machine-read-0001.py',RUN/'qualify-API71-generated-preparation-0001.py',RUN/'API71-generated-qualification-driver-terminal-0001.json'):
        row=bind(path);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    remaining=[
        'Qualify original change.prepare and complete independently selected proposal.review consumption of generated challenge outputs. Current original validation preserves two unresolved carrier-specific domain reference gaps.',
        'Resolve original carrier semantic reference adapters; not-evaluable evidence does not establish semantic closure or admission readiness.',
        *parent['remaining_obligations']]
    remaining=list(dict.fromkeys(remaining))
    value={**parent,'files':[rows[k] for k in sorted(rows)],'parent_progress_binding':bind(parent_path),
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'current_API_version':71,
        'generated_consumer_integration_analysis_binding':bind(RUN/'GENERATED-CONSUMER-INTEGRATION-ANALYSIS-0001.md'),
        'carrier_reference_resolution_analysis_binding':bind(RUN/'CARRIER-REFERENCE-RESOLUTION-ANALYSIS-0001.md'),
        'runtime_closure_analysis_binding':bind(RUN/'RUNTIME-CLOSURE-ANALYSIS-0001.md'),
        'Machine_read_diagnostic_authored_binding':bind(RUN/'diagnose-API50-machine-read-0001.py'),
        'Machine_read_diagnostic_executed':False,
        'generated_preparation_check_authored_binding':bind(RUN/'qualify-API71-generated-preparation-0001.py'),
        'generated_preparation_check_executed':False,
        'generated_workflow_outcomes':outcomes,'generated_candidate_bridge_authored':True,
        'generated_candidate_selected_full5_runtime_qualified':generated is not None and generated['result']=='PASS' and generated['actual_cases']==5,
        'generated_candidate_prepare_runtime_qualified':False,'generic_challenge_review_workflow_qualified':False,
        'challenge_operator_focused_runtime_qualified':False,
        'challenge_operator_selected_full7_runtime_qualified':challenge is not None and challenge['result']=='PASS' and challenge['actual_cases']==7,
        'challenge_current_active_job_observation':None,
        'change':'API69 added an independently reconstructed completed-producer output selection for original generic validation/preparation. Its actual focused test failed by searching a check summary for details stored in bound evidence; the validator reached original four-target validation with two explicit semantic gaps. API71 preserves all production validator logic and 316 test methods, corrects that evidence assertion and the artifact-header selector, and records only its exact current selected runtime outcomes.',
        'remaining_obligations':remaining,'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'Current selected generated validation and challenge submission proof only. No qualification of generated review/preparation, whole API, actual owner authority, admission, activation or complete plan.'}
    path=API/'receipts/R03-0107.json';emit(path,value)
    print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),'generated_selected_full5_qualified':value['generated_candidate_selected_full5_runtime_qualified'],'challenge_selected_full7_qualified':value['challenge_operator_selected_full7_runtime_qualified'],'goal_complete':False}),flush=True)
if __name__=='__main__':main()
