"""Bind actual owner-join proofs and preserve the original qualification ceiling."""
import hashlib
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v59'
def load(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def emit(p,v):
    with p.open('x') as stream:json.dump(v,stream,indent=2,sort_keys=True);stream.write('\n')
def terminal(version,session,initial,final,code):
    report=BASE/f'checkpoint-owner-verification-v{version}/receipts/checks-0001.json';proof=load(report)
    path=RUN/f'checkpoint-owner-v{version}-terminal-0001.json'
    emit(path,{'schema_version':'lab-actual-tool-terminal/v1-candidate','session_id':session,
        'initial_chunk_id':initial,'final_chunk_id':final,'actual_exit_code':code,
        'result':proof['result'],'actual_cases':proof['actual_cases'],'failures':proof['failures'],'errors':proof['errors'],
        'report_binding':bind(report),'source_guarded_exit_completed':proof['source_guarded_exit_completed'],
        'authority_effect':'none','task_complete':False,'goal_complete':False})
    return path
def main():
    parent_path=API/'receipts/R03-0103.json';parent=load(parent_path)
    proofs=[load(BASE/f'checkpoint-owner-verification-v{v}/receipts/checks-0001.json') for v in (1,2,3)]
    assert proofs[0]['result']=='FAIL' and proofs[0]['actual_cases']==38 and proofs[0]['errors']==5 and proofs[0]['failures']==0
    assert proofs[1]['result']=='PASS' and proofs[1]['actual_cases']==43 and proofs[1]['errors']==proofs[1]['failures']==0
    assert proofs[2]['result']=='PASS' and proofs[2]['actual_cases']==49 and proofs[2]['errors']==proofs[2]['failures']==0
    for p in proofs:
        assert p['source_guarded_exit_completed'] and not p['public_checkpoint_handler_qualified'] and not p['live_authority_verified']
    terminals=[terminal(1,59455,'069a25','d9f53f',1),terminal(2,None,'def9c1','def9c1',0),terminal(3,41499,'7863e7','82cfde',0)]
    rows={r['path']:r for r in parent['files']}
    for version,proof in zip((1,2,3),proofs):
        folder=BASE/f'checkpoint-owner-verification-v{version}';source=load(folder/'source-manifest.json')
        for row in source['files']+source['input_bindings']+proof['files']:rows[row['path']]=row
        for p in (folder/'source-manifest.json',folder/'receipts/checks-0001.json'):
            row=bind(p);rows[row['path']]=row
    for p in [parent_path,Path(__file__).resolve(),*terminals]:
        row=bind(p);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    value={**parent,'files':[rows[k] for k in sorted(rows)],'parent_progress_binding':bind(parent_path),
        'checkpoint_owner_join_source_binding':bind(BASE/'checkpoint-owner-verification-v3/source-manifest.json'),
        'checkpoint_owner_join_checks_binding':bind(BASE/'checkpoint-owner-verification-v3/receipts/checks-0001.json'),
        'checkpoint_owner_join_terminal_bindings':[bind(p) for p in terminals],
        'checkpoint_owner_join_cases_passed':49,'checkpoint_owner_join_synthetic_scope_qualified':True,
        'checkpoint_owner_join_native_positive_journey_qualified':False,'checkpoint_owner_live_authority_qualified':False,
        'checkpoint_owner_storage_and_assignment_domains_separate':True,
        'change':'Added independently provisioned private owner/key selection, actual API59 source resolver and five original-schema owner authority joins. Current v3 passed49 selected synthetic join/actual private-file checks. v1 failed38/5errors on malformed fixture/unresolved Source Cut schema; original failed proof retained. v2 passed43 after retaining mandatory limitations/exclusions and using original storage Source Cut schema. v3 separates storage header scope from assignment/target domain; all43 prior test bodies unchanged plus six domain cases. Claim/assignment basis Decisions and semantic limitations remain unresolved and live authority is explicitly false. No public checkpoint handler or actual owner outcome is qualified.',
        'remaining_obligations':[
            'Resolve original assignment/claim basis Decisions and semantic limitations with independent admitted provenance; verify successful actual native Principal/Role/Scope sources; compose selected owner/core/target policy with exact checkpoint rules. Only an independently verified actual authorization channel may establish owner responses.',
            'Complete checkpoint public host policy/protocol integration, durable recording, original Validation Reports, exact retries/recovery and actual authenticated handler journeys. Operator signatures alone do not establish human identity; conversation/existing-authority need their original provenance adapters.',
            *parent['remaining_obligations'][1:]],
        'claim_ceiling':'Selected API59 full14 export evidence and49 synthetic original-schema authority join/actual private-file custody checks only. Native positive owner journey, live authority, public checkpoint handler, actual R08 outcome, canonical admission and complete plan remain unqualified.',
        'whole_API_qualified':False,'task_complete':False,'goal_complete':False}
    path=API/'receipts/R03-0104.json';emit(path,value)
    print(json.dumps({'result':'PASS','progress_binding':bind(path),'bound_files':len(rows),
        'owner_join_cases_passed':49,'authored_handlers':20,'missing_operations':14,'goal_complete':False}),flush=True)
if __name__=='__main__':main()
