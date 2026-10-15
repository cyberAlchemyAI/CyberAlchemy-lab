"""Bind completed preparation and the exact next workflow candidate honestly."""
import hashlib, json
from pathlib import Path
RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'; API=BASE/'api-v72'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    parent_path=BASE/'api-v71/receipts/R03-0107.json'; parent=load(parent_path)
    source=load(API/'source-manifest.json'); profile=load(API/'contract-profile.json')
    assert len(profile['implemented_operations'])==21 and source['unchanged_inherited_method_count']==317
    rows={row['path']:row for row in parent['files']}
    for row in source['files']:rows[row['path']]=row
    prep_path=RUN/'API71-generated-preparation-checks-0001.json'; prep=load(prep_path)
    assert prep['result']=='PASS' and prep['actual_cases']==1 and prep['actual_public_calls']==4
    assert prep['source_sha256']==bind(BASE/'api-v71/source-manifest.json')['sha256']
    assert prep['profile_sha256']==bind(BASE/'api-v71/contract-profile.json')['sha256']
    assert prep['source_guarded_exit_completed'] and prep['owned_fixture_cleanup_completed']
    for row in prep['files']:rows[row['path']]=row
    paths=[parent_path,API/'source-manifest.json',API/'contract-profile.json',prep_path,
        RUN/'API71-generated-preparation-completed-observation-0001.json',
        RUN/'API72-freeze-terminal-0001.json',RUN/'run-API72-workflow-focused-0001.py',
        RUN/'GENERATED-CARRIER-RESOLVER-DESIGN-0001.md',Path(__file__).resolve()]
    diagnostic_path=RUN/'API50-machine-read-diagnosis-0001.json'
    diagnostic=None
    if diagnostic_path.exists():
        diagnostic=load(diagnostic_path)
        for row in diagnostic['files']:rows[row['path']]=row
        paths.append(diagnostic_path)
        terminal=RUN/'API50-machine-read-diagnosis-terminal-0001.json'
        if terminal.exists():paths.append(terminal)
    workflow_path=API/'receipts/workflow-composition-focused-checks-0001.json'
    workflow=None
    if workflow_path.exists():
        workflow=load(workflow_path)
        assert workflow['source_sha256']==bind(API/'source-manifest.json')['sha256']
        assert workflow['profile_sha256']==bind(API/'contract-profile.json')['sha256']
        for row in workflow['files']:rows[row['path']]=row
        paths.extend([workflow_path,RUN/'API72-workflow-focused-terminal-0001.json'])
        terminal=load(paths[-1]);assert terminal['report_binding']==bind(workflow_path)
        assert terminal['actual_exit_code']==(0 if workflow['result']=='PASS' else 1)
    for path in paths:
        row=bind(path);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    qualified=workflow is not None and workflow['result']=='PASS' and workflow['actual_cases']==1 and workflow['actual_public_calls']==5
    outcomes=parent['generated_workflow_outcomes']+[{'version':71,'kind':'preparation','scope':'selected',
        'result':'PASS','actual_cases':1,'actual_public_calls':4,'failures':0,'errors':0,'report_binding':bind(prep_path),
        'completed_observation_binding':bind(RUN/'API71-generated-preparation-completed-observation-0001.json')}]
    if workflow is not None:outcomes.append({'version':72,'kind':'workflow-composition','scope':'focused',
        'result':workflow['result'],'actual_cases':workflow['actual_cases'],'actual_public_calls':workflow['actual_public_calls'],
        'failures':workflow['failures'],'errors':workflow['errors'],'report_binding':bind(workflow_path),
        'terminal_binding':bind(RUN/'API72-workflow-focused-terminal-0001.json')})
    value={**parent,'result':'PASS','files':[rows[key] for key in sorted(rows)],
        'parent_progress_binding':bind(parent_path),'current_API_version':72,
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'generated_workflow_outcomes':outcomes,
        'API71_generated_preparation_selected_qualified':True,
        'generated_preparation_check_executed':True,
        'API72_independent_workflow_composition_authored':True,
        'API72_unchanged_inherited_method_count':317,
        'API72_focused_workflow_qualified':qualified,
        'generic_challenge_review_workflow_qualified':False,
        'generated_candidate_selected_full5_runtime_qualified':False,
        'generated_candidate_prepare_runtime_qualified':qualified,
        'challenge_operator_selected_full7_runtime_qualified':False,
        'Machine_read_diagnostic_executed':True,
        'Machine_read_diagnostic_result':None if diagnostic is None else diagnostic['result'],
        'Machine_read_diagnostic_active_process':37814 if diagnostic is None else None,
        'Machine_historical_full_suite_cause_established':False,
        'generated_carrier_resolver_design_binding':bind(RUN/'GENERATED-CARRIER-RESOLVER-DESIGN-0001.md'),
        'remaining_obligations':[
            'Qualify the current API72 exact composition and complete the original affected inherited regression selections.',
            'Implement and qualify separately bound typed Evidence Set and Challenge Event reference resolvers; preserve unsupported cases and owner/admission gaps.',
            'Close the original Machine diagnostic and qualify any actual repair plus the six unexecuted termination cases with fresh owned fixtures.',
            *parent['remaining_obligations']],
        'change':'Actual API71 submission/preparation/retry/inspection passed. API72 introduces independently selected complete generated/static composition and pending review without owner authority; exact runtime outcomes are recorded only when available.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'Completed source71 selected preparation and exact source72 construction/available selected runtime observations only. No full API, recognized owner outcome, canonical admission, activation or complete Lab plan.'}
    path=API/'receipts/R03-0108.json';path.parent.mkdir(exist_ok=True);emit(path,value)
    print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),
        'API71_preparation_qualified':True,'API72_focused_workflow_qualified':qualified,
        'Machine_diagnostic_result':value['Machine_read_diagnostic_result'],'goal_complete':False}),flush=True)
if __name__=='__main__':main()
