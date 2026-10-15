"""Bind exact completed classification and pending-inspection observations."""
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v57'
CHECK=BASE/'api57-classification-checks-v2'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def terminal(name,session,initial,final,exit_code,report,log,wire):
    observed=load(report)
    path=RUN/name
    emit(path,{'schema_version':'lab-actual-tool-terminal/v1-candidate','session_id':session,
        'initial_chunk_id':initial,'final_chunk_id':final,'actual_exit_code':exit_code,
        'result':observed['result'],'actual_cases':observed['actual_cases'],
        'errors':observed['errors'],'failures':observed['failures'],
        'actual_public_calls':len(load(wire)),
        'source_guarded_exit_completed':observed['source_guarded_exit_completed'],
        'owned_fixture_cleanup_completed':observed['owned_fixture_cleanup_completed'],
        'report_binding':bind(report),'log_binding':bind(log),'wire_binding':bind(wire),
        'whole_API_qualified':False,'authority_effect':'none','task_complete':False,'goal_complete':False})
    return path

def main():
    parent_path=BASE/'api-v56/receipts/R03-0099.json';parent=load(parent_path)
    historical=BASE/'api56-classification-checks-v1/receipts'
    pending=CHECK/'receipts'
    failed=BASE/'api57-classification-checks-v1/receipts'
    historic_report=load(historical/'full-0001.json')
    current_report=load(pending/'pending-0001.json')
    for report,count in ((historic_report,16),(current_report,1)):
        assert report['result']=='PASS' and report['actual_cases']==count
        assert report['errors']==report['failures']==0
        assert report['source_guarded_exit_completed'] and report['owned_fixture_cleanup_completed']
        assert report['original_test_file_unchanged'] and not report['whole_API_qualified']
    assert len(load(historical/'full-wire-0001.json'))==20
    wire=load(pending/'pending-wire-0001.json');assert len(wire)==4
    assert wire[0]['reply']['message']['code']=='indeterminate'
    inspected=wire[1]['reply']['message']
    assert wire[1]['reply']['kind']=='result' and inspected['posture']=='indeterminate'
    assert inspected['result_binding'] is None and inspected['reconciliation_required'] and not inspected['retry_allowed']
    assert len(inspected['effect_evidence_bindings'])>1
    assert wire[2]['reply']['message']['code']=='recovery-required'
    assert wire[3]['reply']['message']['code']=='integrity-failed'
    full_terminal=terminal('API56-classification-full16-terminal-0001.json',82302,'552acc','9d4e16',0,
        historical/'full-0001.json',historical/'full-0001.log',historical/'full-wire-0001.json')
    pending_terminal=terminal('API57-pending-evidence-terminal-0002.json',63123,'e37a47','e573ed',0,
        pending/'pending-0001.json',pending/'pending-0001.log',pending/'pending-wire-0001.json')
    failed_terminal=terminal('API57-pending-evidence-failed-terminal-0001.json',53244,'a7784f','c7226e',1,
        failed/'pending-0001.json',failed/'pending-0001.log',failed/'pending-wire-0001.json')
    freeze_terminal=RUN/'API57-freeze-terminal-0002.json'
    emit(freeze_terminal,{'schema_version':'lab-actual-tool-terminal/v1-candidate','session_id':35087,
        'initial_chunk_id':'f9e846','final_chunk_id':'80d65d','actual_exit_code':0,'result':'FROZEN',
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'check_source_binding':bind(BASE/'api57-classification-checks-v1/source-manifest.json'),
        'runtime_checks_executed':False,'authority_effect':'none','task_complete':False,'goal_complete':False})
    rows={row['path']:row for row in parent['files']}
    for row in load(API/'source-manifest.json')['files']+current_report['files']+historic_report['files']:
        rows[row['path']]=row
    paths=[parent_path,full_terminal,pending_terminal,failed_terminal,freeze_terminal,
        historical/'full-0001.json',pending/'pending-0001.json',failed/'pending-0001.json',
        failed/'pending-0001.log',failed/'pending-wire-0001.json',API/'source-manifest.json',API/'contract-profile.json',
        CHECK/'source-manifest.json',RUN/'API57-freeze-failed-terminal-0001.json',
        RUN/'finish-API57-freeze-0002.py',RUN/'ARE-CONTINUATION-R03-0100.json',Path(__file__).resolve()]
    for path in paths:
        row=bind(path);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    profile=load(API/'contract-profile.json');assert len(profile['implemented_operations'])==19
    value={**parent,'files':[rows[k] for k in sorted(rows)],'parent_progress_binding':bind(parent_path),
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'implemented_operations':profile['implemented_operations'],
        'change':'API57 records an exact principal/claim-bound pending native evidence observation after full source exit. Actual inspection exposes the retained failed report, null result, indeterminate state and mandatory reconciliation; exact retry refuses redispatch, and claim-binding tamper is refused. One case/four authenticated calls PASS. API56 full16/20 calls separately completed PASS. Initial freeze path handling and added test request-budget errors are retained as failed attempts. Full API57 classification17 is running. All34 contracts remain in scope,19 handlers authored/15 missing; no complete API, task, goal or admission.',
        'pending_native_evidence_checks_binding':bind(pending/'pending-0001.json'),
        'pending_native_evidence_terminal_binding':bind(pending_terminal),
        'pending_native_evidence_actual_cases':1,'pending_native_evidence_actual_public_calls':4,
        'pending_native_evidence_runtime_qualified':True,
        'pending_native_evidence_qualification_scope':'Only one exact authenticated pending-inspection/retry/tamper case/four calls against API57.',
        'historical_API56_classification_full16_binding':bind(historical/'full-0001.json'),
        'historical_API56_classification_full16_terminal_binding':bind(full_terminal),
        'historical_API56_classification_full16_qualified':True,
        'historical_API56_classification_full16_actual_cases':16,
        'historical_API56_classification_full16_actual_public_calls':20,
        'classification_v8_runtime_qualification_scope':'All16 separately versioned classification cases/20 authenticated calls against historical exact API56; no transfer to API57.',
        'classification_full16_qualified':False,'current_API57_classification_full17_qualified':False,
        'current_API57_whole_suite_qualified':False,'failed_pending_test_terminal_binding':bind(failed_terminal),
        'authored_handlers':19,'implemented_public_handlers':19,'unimplemented_public_operation_count':15,
        'remaining_obligations':[
            'Finish the same API57 classification full17 job, session7381 initial8e742c; exact pending case alone does not qualify all classification behavior or the whole API.',
            'Finish the same original API50 remaining240 driver/session67314; preserve original deadlines, failed scopes and exact source identity.',
            'Implement all15 remaining public operations, general foreign/admitted package authority/carrier coverage and portable export with full dependency/privacy proof.',
            'Complete nonempty Lesson/Context/Ontology sources, actual Machine write authority, internal/specialized authority resolution, genuine R05 participant evidence, R06/R07 and all-member S02. Sole actual R08 precedes separately authorized A01-A04.'],
        'claim_ceiling':'One API57 pending native evidence case/four calls, plus completed exact predecessor API56 full16/20 calls. Full current17 and other API journeys remain unfinished. All15 missing operations and full46 task plan remain outstanding; no genuine pilot, owner outcome, admission, activation or completed goal.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    path=API/'receipts/R03-0100.json';path.parent.mkdir(exist_ok=True);emit(path,value)
    print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),
        'current_pending_cases':1,'current_pending_calls':4,'historical_full_classification_cases':16,
        'authored_handlers':19,'missing_operations':15,'task_complete':False,'goal_complete':False}),flush=True)

if __name__=='__main__':main()
