"""Record exact authored export integration and completed selected journeys."""
import argparse
import hashlib
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v58';CHECK=BASE/'api58-export-checks-v2'
def load(path):return json.loads(path.read_bytes())
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def emit(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def terminal(name,session,initial,final,exit_code,report,log,wire):
    observed=load(report);path=RUN/name
    emit(path,{'schema_version':'lab-actual-tool-terminal/v1-candidate','session_id':session,
        'initial_chunk_id':initial,'final_chunk_id':final,'actual_exit_code':exit_code,
        'result':observed['result'],'actual_cases':observed['actual_cases'],
        'errors':observed['errors'],'failures':observed['failures'],'actual_public_calls':len(load(wire)),
        'source_guarded_exit_completed':observed['source_guarded_exit_completed'],
        'owned_fixture_cleanup_completed':observed['owned_fixture_cleanup_completed'],
        'report_binding':bind(report),'log_binding':bind(log),'wire_binding':bind(wire),
        'whole_API_qualified':False,'authority_effect':'none','task_complete':False,'goal_complete':False})
    return path
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--focused-final-chunk',required=True);args=parser.parse_args()
    parent_path=BASE/'api-v57/receipts/R03-0100.json';parent=load(parent_path)
    historical=BASE/'api57-classification-checks-v2/receipts'
    focused_path=CHECK/'receipts/package-export-focused-0001.json';focused=load(focused_path)
    full=load(historical/'full-0001.json')
    for proof,expected in ((focused,3),(full,17)):
        assert proof['result']=='PASS' and proof['actual_cases']==expected
        assert proof['errors']==proof['failures']==0 and proof['source_guarded_exit_completed'] and proof['owned_fixture_cleanup_completed']
    wire=load(CHECK/'receipts/package-export-focused-wire-0001.json')
    assert len(wire)==4 and all(row['reply']['kind']=='result' and row['reply']['message']['posture']=='published' for row in wire)
    assert wire[2]['reply']['message']==wire[3]['reply']['message']
    assert len(load(historical/'full-wire-0001.json'))==24
    full_terminal=terminal('API57-classification-full17-terminal-0001.json',7381,'8e742c','feb4e2',0,
        historical/'full-0001.json',historical/'full-0001.log',historical/'full-wire-0001.json')
    focused_terminal=terminal('API58-package-export-focused-terminal-0002.json',59531,'fdd76d',args.focused_final_chunk,0,
        focused_path,CHECK/'receipts/package-export-focused-0001.log',CHECK/'receipts/package-export-focused-wire-0001.json')
    failed=API/'receipts'
    failed_terminal=terminal('API58-package-export-failed-terminal-0001.json',43272,'a6c532','022e91',1,
        failed/'package-export-focused-0001.json',failed/'package-export-focused-0001.log',failed/'package-export-focused-wire-0001.json')
    freeze_terminal=RUN/'API58-freeze-terminal-0001.json'
    emit(freeze_terminal,{'schema_version':'lab-actual-tool-terminal/v1-candidate','session_id':94484,
        'initial_chunk_id':'d97ebc','final_chunk_id':'c4a20b','actual_exit_code':0,'result':'FROZEN',
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'runtime_checks_executed':False,'authority_effect':'none','task_complete':False,'goal_complete':False})
    rows={row['path']:row for row in parent['files']}
    for row in load(API/'source-manifest.json')['files']+focused['files']+full['files']+load(CHECK/'source-manifest.json')['files']:
        rows[row['path']]=row
    paths=[parent_path,full_terminal,focused_terminal,failed_terminal,freeze_terminal,
        historical/'full-0001.json',focused_path,failed/'package-export-focused-0001.json',
        failed/'package-export-focused-0001.log',failed/'package-export-focused-wire-0001.json',
        RUN/'API58-export-proposal-diagnostic-0001.json',RUN/'diagnose-API58-export-proposal-0001.py',
        API/'source-manifest.json',API/'contract-profile.json',CHECK/'source-manifest.json',Path(__file__).resolve()]
    for path in paths:
        row=bind(path);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    profile=load(API/'contract-profile.json');assert len(profile['implemented_operations'])==20
    catalog=load(ROOT/profile['original_operation_catalog_binding']['path'])
    missing=[row['operation'] for row in catalog['operations'] if row['operation'] not in profile['implemented_operations']]
    assert len(missing)==14 and len(catalog['operations'])==34
    value={**parent,'files':[rows[k] for k in sorted(rows)],'parent_progress_binding':bind(parent_path),
        'source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'implemented_operations':profile['implemented_operations'],'authored_handlers':20,'implemented_public_handlers':20,
        'unimplemented_public_operation_count':14,'unimplemented_public_operations':missing,
        'change':'API58 adds original package.export with independently selected host policy, complete original material graph, native candidate validation, retained signed archive/profile basis, privacy/encoding/budget checks and actual source/current permission guarded managed publication. Three selected cases/four authenticated calls PASS: controlled native Work candidate, current signed-source Work and read-only exact retry. The initial fixture incorrectly removed required Work membership and failed two cases; its failed report and native validation diagnostic remain. A separate bound fixture successor restores original membership with all12 test bodies unchanged. API57 full17/24 calls separately completed PASS. Full export12 and current inherited journeys remain required;14 operations and whole plan are unfinished.',
        'package_export_checks_binding':bind(focused_path),'package_export_terminal_binding':bind(focused_terminal),
        'package_export_actual_cases':3,'package_export_actual_public_calls':4,'package_export_runtime_qualified':True,
        'package_export_runtime_qualification_scope':'Three selected authenticated Work-root journeys only: exact validated controlled candidate, current signed-source root with original basis and read-only retry. JSON sources; no broad carrier/source-authority or foreign import claim.',
        'package_export_full12_qualified':False,'current_API58_whole_suite_qualified':False,
        'historical_API57_full_classification_binding':bind(historical/'full-0001.json'),
        'historical_API57_full_classification_terminal_binding':bind(full_terminal),
        'historical_API57_full_classification_qualified':True,'historical_API57_full_classification_actual_cases':17,
        'historical_API57_full_classification_actual_public_calls':24,
        'pending_native_evidence_runtime_qualified':False,
        'pending_native_evidence_qualification_scope':'Qualified for exact API57 only; no transfer to API58.',
        'package_export_failed_attempt_terminal_binding':bind(failed_terminal),
        'remaining_obligations':[
            'Complete all12 exact API58 export checks and every required current inherited journey; focused Work-root export proof does not qualify all carriers, sources or the whole API.',
            'Finish the same original API50 remaining240 scheduler/session67314 without altering original clocks or failed evidence.',
            'Implement all14 remaining public operations and close general foreign/admitted-source import, source authority/reference adapters and non-JSON material privacy/encoding obligations.',
            'Complete nonempty Lesson/Context/Ontology sources, actual Machine write authority and internal/specialized authority resolution, genuine R05 participant evidence, R06/R07 and all-member S02. Sole actual R08 precedes separately authorized A01-A04.'],
        'claim_ceiling':'Three selected exact API58 Work-root export cases/four calls only. API57 full17/24 calls belongs to its predecessor. Export12, other current journeys, general carrier/authority closure, all14 missing operations, genuine pilot and final review/application remain unfinished. No owner outcome, canonical admission, activation or completed plan.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    path=API/'receipts/R03-0101.json';emit(path,value)
    print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),
        'export_actual_cases':3,'export_actual_public_calls':4,'historical_full_classification_cases':17,
        'authored_handlers':20,'missing_operations':14,'task_complete':False,'goal_complete':False}),flush=True)
if __name__=='__main__':main()
