"""Record the actual lookup repair and preserve the failed predecessor suite."""
import argparse
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v59';CHECK=BASE/'api59-export-checks-v1'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def terminal(name,session,initial,final,exit_code,report):
    v=load(report);p=RUN/name
    emit(p,{'schema_version':'lab-actual-tool-terminal/v1-candidate','session_id':session,
        'initial_chunk_id':initial,'final_chunk_id':final,'actual_exit_code':exit_code,
        'result':v['result'],'actual_cases':v['actual_cases'],'actual_public_calls':v['actual_public_calls'],
        'failures':v['failures'],'errors':v['errors'],'report_binding':bind(report),
        'source_guarded_exit_completed':v['source_guarded_exit_completed'],
        'owned_fixture_cleanup_completed':v['owned_fixture_cleanup_completed'],
        'whole_API_qualified':False,'authority_effect':'none','task_complete':False,'goal_complete':False})
    return p
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--focused-final-chunk',required=True)
    parser.add_argument('--failed-full-final-chunk',required=True);args=parser.parse_args()
    parent_path=BASE/'api-v58/receipts/R03-0101.json';parent=load(parent_path)
    focused_path=CHECK/'receipts/package-export-focused-0001.json';focused=load(focused_path)
    failed_path=BASE/'api58-export-checks-v2/receipts/package-export-full-0001.json';failed=load(failed_path)
    assert focused['result']=='PASS' and focused['actual_cases']==4 and focused['actual_public_calls']==5
    assert focused['failures']==focused['errors']==0 and focused['source_guarded_exit_completed'] and focused['owned_fixture_cleanup_completed']
    assert failed['result']=='FAIL' and failed['actual_cases']==12 and failed['failures']==2 and failed['errors']==0
    assert {r['test'].split('.')[-1] for r in failed['cases'] if r['result']=='FAIL'}=={
        'test_05_caller_cannot_replace_selected_privacy_review','test_06_caller_cannot_omit_dependency_closure'}
    completed=RUN/'API50-exports134-terminal-0002.json';old=load(completed)
    assert old['actual_exit_code']==0 and old['actual_cases']==134 and old['failures']==old['errors']==0
    ft=terminal('API59-readonly-lookup-focused-terminal-0001.json',23997,'b1c271',args.focused_final_chunk,0,focused_path)
    bt=terminal('API58-package-export-full12-failed-terminal-0001.json',42741,'c5e851',args.failed_full_final_chunk,1,failed_path)
    freeze=RUN/'API59-freeze-terminal-0001.json'
    emit(freeze,{'schema_version':'lab-actual-tool-terminal/v1-candidate','session_id':84174,
        'initial_chunk_id':'3fff5d','final_chunk_id':'350614','actual_exit_code':0,'result':'FROZEN',
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'runtime_checks_executed':False,'authority_effect':'none','task_complete':False,'goal_complete':False})
    rows={r['path']:r for r in parent['files']}
    for row in load(API/'source-manifest.json')['files']+load(CHECK/'source-manifest.json')['files']+focused['files']+failed['files']:
        rows[row['path']]=row
    for p in (parent_path,focused_path,failed_path,completed,ROOT/old['report_binding']['path'],ROOT/old['log_binding']['path'],
        ft,bt,freeze,API/'source-manifest.json',API/'contract-profile.json',CHECK/'source-manifest.json',Path(__file__).resolve()):
        row=bind(p);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    profile=load(API/'contract-profile.json');assert len(profile['implemented_operations'])==20
    value={**parent,'files':[rows[k] for k in sorted(rows)],'parent_progress_binding':bind(parent_path),
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'readonly_lookup_checks_binding':bind(focused_path),'readonly_lookup_terminal_binding':bind(ft),
        'readonly_lookup_runtime_qualified':True,'readonly_lookup_actual_cases':4,'readonly_lookup_actual_public_calls':5,
        'readonly_lookup_qualification_scope':'Two unchanged original refusal cases plus actual unknown-operation inspection and missing-lock retry on a published Work candidate. Every rejected/inspection/retry request preserves owned file bytes.',
        'historical_API58_export_full12_result':'FAIL','historical_API58_export_full12_checks_binding':bind(failed_path),
        'historical_API58_export_full12_terminal_binding':bind(bt),'historical_API58_export_full12_failures':2,
        'historical_API50_exports134_terminal_binding':bind(completed),'historical_API50_exports134_qualified':True,
        'API50_completed_selected_cases':346,'API50_completed_selected_cases_passed':342,
        'API50_completed_selected_cases_failed':3,'API50_completed_selected_cases_errors':1,'API50_remaining_selected_cases':106,
        'package_export_runtime_qualified':False,'package_export_runtime_qualification_scope':'Historical selected API58 proof only. API59 full14, including all12 unchanged export cases, remains required.',
        'current_API59_whole_suite_qualified':False,'package_export_full14_qualified':False,
        'implemented_operations':profile['implemented_operations'],'authored_handlers':20,'unimplemented_public_operation_count':14,
        'change':'API59 repairs the observed lock-file write during read-only lookup before rejected export preflight. Empty journal inspection writes nothing; existing journal inspection opens its lock without creation; a nonempty journal without its lock is refused without recreation. The authoritative claim still creates its original exclusive lock and rechecks the fingerprint before dispatch. Four actual cases/five calls PASS. All305 inherited methods and all12 original export tests are unchanged. API58 full12 failed exactly two file-equality assertions; its evidence remains. Original API50 exports134 separately completed PASS. Fourteen operations and the complete plan remain unfinished.',
        'remaining_obligations':[
            'Complete all14 exact API59 checks, including twelve unchanged export cases, and every required current inherited journey. Selected lookup proof does not qualify the whole API or general carrier/source closure.',
            'Finish the same original API50 remaining106 scheduler/session67314 without changing clocks or failed evidence; metadata86, machine14 and termination6 remain.',
            'Implement all14 remaining public operations; close general foreign/admitted-source import, carrier/reference/authority adapters and non-JSON privacy/encoding.',
            'Complete nonempty Lesson/Context/Ontology, actual Machine write authority, genuine R05 participant evidence, R06/R07 and all-member S02. Sole actual R08 precedes separately authorized A01-A04.'],
        'claim_ceiling':'Four actual API59 lookup/refusal/recovery cases/five calls only. API58 failed full12 and historical API50 exports134 evidence remain exact predecessors. All14 current export cases, inherited journeys, missing operations, genuine pilot, owner review and application remain unfinished.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    p=API/'receipts/R03-0102.json';p.parent.mkdir(exist_ok=True);emit(p,value)
    print(json.dumps({'result':'PASS','progress_binding':bind(p),'bound_files':len(rows),
        'actual_lookup_cases':4,'actual_public_calls':5,'authored_handlers':20,'missing_operations':14,
        'task_complete':False,'goal_complete':False}),flush=True)
if __name__=='__main__':main()
