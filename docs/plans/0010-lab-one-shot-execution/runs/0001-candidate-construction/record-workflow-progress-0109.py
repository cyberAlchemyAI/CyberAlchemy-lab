"""Bind completed preparation and the exact next workflow candidate honestly."""
import hashlib, json
from pathlib import Path
RUN=Path(__file__).resolve().parent; ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'; API=BASE/'api-v74'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def main():
    parent_path=BASE/'api-v72/receipts/R03-0108.json'; parent=load(parent_path)
    source=load(API/'source-manifest.json'); profile=load(API/'contract-profile.json')
    assert len(profile['implemented_operations'])==21 and source['unchanged_inherited_method_count']==320
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
        RUN/'run-API74-workflow-focused-0001.py',RUN/'run-API74-after-focused-0001.py',RUN/'qualify-API74-machine-read-0001.py',RUN/'API50-machine-read-diagnosis-completed-observation-0001.json',RUN/'API72-guard-cost-measurement-0001.json',RUN/'measure-API72-guard-cost-0001.py',
        RUN/'GENERATED-CARRIER-RESOLVER-DESIGN-0001.md',Path(__file__).resolve()]
    previous_workflows=[]
    for version in (72,73):
        folder=BASE/f'api-v{version}'
        report_path=folder/'receipts/workflow-composition-focused-checks-0001.json'
        proof=load(report_path)
        assert proof['result']=='FAIL' and proof['source_sha256']==bind(folder/'source-manifest.json')['sha256']
        for row in proof['files']:rows[row['path']]=row
        paths.extend([report_path,RUN/f'API{version}-workflow-focused-terminal-0001.json'])
        previous_workflows.append({'version':version,'kind':'workflow-composition','scope':'focused',
            'result':proof['result'],'actual_cases':proof['actual_cases'],'actual_public_calls':proof['actual_public_calls'],
            'failures':proof['failures'],'errors':proof['errors'],'report_binding':bind(report_path),
            'terminal_binding':bind(paths[-1])})
    earlier_wire=load(BASE/'api-v73/receipts/workflow-composition-focused-wire-0001.json')
    prepared=[row['reply']['message'] for row in earlier_wire['observations']
              if row['call']['operation']=='change.prepare' and row['reply']['kind']=='result']
    assert len(prepared)==1 and len(prepared[0]['stable_core_bindings'])==5 and len(prepared[0]['gaps'])==4
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
        paths.extend([workflow_path,RUN/'API74-workflow-focused-terminal-0001.json'])
        terminal=load(paths[-1]);assert terminal['report_binding']==bind(workflow_path)
        assert terminal['actual_exit_code']==(0 if workflow['result']=='PASS' else 1)
    for path in paths:
        row=bind(path);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    qualified=workflow is not None and workflow['result']=='PASS' and workflow['actual_cases']==1 and workflow['actual_public_calls']==5
    outcomes=parent['generated_workflow_outcomes']+previous_workflows
    if workflow is not None:outcomes.append({'version':74,'kind':'workflow-composition','scope':'focused',
        'result':workflow['result'],'actual_cases':workflow['actual_cases'],'actual_public_calls':workflow['actual_public_calls'],
        'failures':workflow['failures'],'errors':workflow['errors'],'report_binding':bind(workflow_path),
        'terminal_binding':bind(RUN/'API74-workflow-focused-terminal-0001.json')})
    value={**parent,'result':'PASS','files':[rows[key] for key in sorted(rows)],
        'parent_progress_binding':bind(parent_path),'current_API_version':74,
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'workflow_focused_active_process':13011 if workflow is None else None,
        'workflow_followon_active_process':72154,
        'API73_composed_five_member_preparation_observed':True,
        'generated_workflow_outcomes':outcomes,
        'API71_generated_preparation_selected_qualified':True,
        'generated_preparation_check_executed':True,
        'API74_independent_workflow_composition_authored':True,
        'API74_unchanged_inherited_method_count':320,
        'API74_focused_workflow_qualified':qualified,
        'generic_challenge_review_workflow_qualified':False,
        'generated_candidate_selected_full5_runtime_qualified':False,
        'generated_candidate_prepare_runtime_qualified':qualified,
        'challenge_operator_selected_full7_runtime_qualified':False,
        'Machine_read_diagnostic_executed':True,
        'Machine_read_diagnostic_result':None if diagnostic is None else diagnostic['result'],
        'Machine_read_diagnostic_active_process':None,
        'Machine_historical_full_suite_cause_established':False,
        'generated_carrier_resolver_design_binding':bind(RUN/'GENERATED-CARRIER-RESOLVER-DESIGN-0001.md'),
        'remaining_obligations':[
            'Qualify the current API74 exact composition and complete the original affected inherited regression selections.',
            'Implement and qualify separately bound typed Evidence Set and Challenge Event reference resolvers; preserve unsupported cases and owner/admission gaps.',
            'Run the unchanged current-source Machine read selection and the six unexecuted termination cases. The original-source diagnostic expired before proof and establishes no current-source or historical full-suite cause.',
            *parent['remaining_obligations']],
        'change':'Original API50 diagnostic expired during Machine proof before any Machine reply. API72 and API73 preserved guards and refused two fixture defects; API73 observed actual five-member preparation with four retained gaps. API74 fixes the fixture protocol namespace and validates the routing schema before authentication. Current selected runtime outcomes are recorded only when completed.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False,
        'claim_ceiling':'Completed source71 selected preparation and exact source74 construction/available selected runtime observations only. No full API, recognized owner outcome, canonical admission, activation or complete Lab plan.'}
    path=API/'receipts/R03-0109.json';path.parent.mkdir(exist_ok=True);emit(path,value)
    print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),
        'API71_preparation_qualified':True,'API74_focused_workflow_qualified':qualified,
        'Machine_diagnostic_result':value['Machine_read_diagnostic_result'],'goal_complete':False}),flush=True)
if __name__=='__main__':main()
