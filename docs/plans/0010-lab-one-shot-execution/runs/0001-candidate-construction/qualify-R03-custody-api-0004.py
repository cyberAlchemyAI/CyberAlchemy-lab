"""Close qualification only from actual terminal suites and frozen observations."""
import argparse,ast,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-v20'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    p=argparse.ArgumentParser();p.add_argument('--observation-sha256',required=True);p.add_argument('--terminal-sha256',required=True);p.add_argument('--predecessor-terminal-sha256',required=True);a=p.parse_args()
    source=HERE/'custody-api-audit-source-0004.json';m=load(source);obs_path=HERE/'custody-api-independent-observations-0004.json';obs=load(obs_path)
    assert bind(obs_path)['sha256']==a.observation_sha256 and obs['result']=='PASS' and obs['source_binding']==bind(source) and not obs['full_suite_qualification']
    ot=HERE/'custody-api-observation-terminal-0004.json';observed_terminal=load(ot)
    assert observed_terminal['exit_code']==0 and observed_terminal['result']=='PASS' and observed_terminal['source_binding']==bind(source) and observed_terminal['observation_binding']==bind(obs_path)
    t=HERE/'custody-api-terminal-0004.json';terminal=load(t);assert bind(t)['sha256']==a.terminal_sha256 and terminal['exit_code']==0
    previous=API.parent/'api-v19';pt=HERE/'custody-api-terminal-0003.json';pred=load(pt);assert bind(pt)['sha256']==a.predecessor_terminal_sha256 and pred['exit_code'] in [0,1]
    for root,value,count in [(API,terminal,146),(previous,pred,129)]:
        for field,local in [('source_binding','source-manifest.json'),('profile_binding','contract-profile.json'),('checks_binding','receipts/checks.json'),('log_binding','checks-0001.log'),('wire_observations_binding','receipts/wire-observations.json')]:assert value[field]==bind(root/local),field
        tests=load(root/'receipts/checks.json');assert tests['tests_run']==tests['expected_tests']==count and len(tests['cases'])==len({r['test'] for r in tests['cases']})==count
        assert (value['exit_code']==0)==(tests['result']=='PASS')
    tests=load(API/'receipts/checks.json');assert tests['result']=='PASS' and all(r['result']=='PASS' for r in tests['cases']) and tests['source_sha256']==m['api_source_binding']['sha256'] and tests['profile_sha256']==m['api_profile_binding']['sha256']
    for name in ['test_preparation.py','test_preparation_corrected.py','run_session_checks.py','test_custody_sessions.py','test_custody_api.py']:assert methods(API/name)==methods(previous/name)
    assert len(methods(API/'test_guarded_reads.py'))==17
    wire=load(API/'receipts/wire-observations.json')
    for module in ['_cal_api_v20_checks.run_session_checks','_cal_api_v20_checks.test_custody_sessions']:
        operations={r['reply']['operation'] for r in wire[module] if r['reply']['kind']=='result'};assert len(operations)==12
    rows={r['path']:r for r in m['files']}
    for r in rows.values():assert bind(ROOT/r['path'])==r,r['path']
    for root in [API,previous]:
        for name in ['source-manifest.json','contract-profile.json','receipts/checks.json','checks-0001.log','receipts/wire-observations.json']:
            b=bind(root/name);assert rows.get(b['path'],b)==b;rows[b['path']]=b
    for path in [source,obs_path,ot,t,pt]:b=bind(path);rows[b['path']]=b
    receipt={'schema_version':'lab-R03-original-source-API-integration-partial-proof/v1-candidate','result':'PASS','files':sorted(rows.values(),key=lambda r:r['path']),'checked_at':datetime.now(timezone.utc).isoformat(),'parent_receipt_binding':m['parent_receipt_binding'],'selected_API_source_binding':m['api_source_binding'],'selected_API_profile_binding':m['api_profile_binding'],'independent_observation_binding':bind(obs_path),'independent_observation_terminal_binding':bind(ot),'actual_full_suite_terminal_binding':bind(t),'actual_predecessor_terminal_binding':bind(pt),'parent_files_retained':obs['parent_files_retained'],'audit_checks':obs['checks'],'selected_methods':146,'original_methods_retained':129,'additional_guard_methods':17,'raw_original_artifact_bodies':23,'current_closed_original_typed_connections':10,'complete_SQL_original_body_custody_verified':True,'actual_legacy_and_original_Session_journeys_verified':True,'actual_public_api_operations':12,'remaining_original_api_operations':22,'original_public_api_operations':34,'closed_plan_criteria':35,'total_plan_criteria':46,'repository_admissions_applied':0,'private_keys_exported':False,'Session_memory_rehydrated':False,'authority_effect':'none','actual_owner_outcome':None,'human_pilot_outcome':None,'task_complete':False,'goal_complete':False,'remaining_obligations':m['remaining_obligations'],'claim_ceiling':'Historical owned observations and complete suite qualification for twelve candidate APIs. No current participation grant or owner authority inferred after expiry. Remaining22APIs/full46criteria/actualR04/S02/R08 outcomes remain.'}
    out=API/'receipts/R03-0022.json';out.open('x').write(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':'PASS','files':len(rows),'methods':146,'receipt_binding':bind(out)}))
if __name__=='__main__':main()
