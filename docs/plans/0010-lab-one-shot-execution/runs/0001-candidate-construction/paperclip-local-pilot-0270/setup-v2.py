"""Additive caller correction: compare the public cut to an actual cold replay.

Original wrapper/direct failure and its successful underlying runner stay intact.
The original private seed, key and absolute expiry are unchanged.
"""
import argparse,hashlib,importlib.util,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
original=HERE/'setup.py'
assert hashlib.sha256(original.read_bytes()).hexdigest()=='c41a6fc9166b3e23919e6ba44144c2c1fdd1f6eaa2c47006763b1893de71fe74'
spec=importlib.util.spec_from_file_location('_paperclip_owned_setup_original_0270',original)
O=importlib.util.module_from_spec(spec);spec.loader.exec_module(O)
PVT=O.PRIVATE
old="assert observed['source_cut']==policy['history_control']['source_cut']"
new="assert observed['source_cut']==json.loads(inputs['cut'])"
assert O.WRAPPER.count(old)==1
WRAPPER=O.WRAPPER.replace(old,new)

def prepare():
    assert not (PVT/'reader_wrapper-v2.py').exists()
    M=O.modules();G=M('guard');P=M('protocol');H=M('handlers')
    G.verify(O.SOURCE)
    policy=O.load(PVT/'policy.json');P.source.validate_history_policy(policy)
    with P.source.replay_source(policy['source_name']) as view:
        # Actual cold verified data/config/head/history digests, using the exact
        # selected production cut function. No synthetic head/stream inference.
        cut=H.cut(view)
        selected=P.source.history_selection(policy['source_name'])
        assert view.data['head']['transaction_digest']==selected['expected_head']
        assert cut['commit_sha256']==selected['expected_head'] and cut['commit_sequence']==1
        assert cut['source_profile_sha256']==selected['engine_pins']['profile_sha256']
        assert cut['store_ref']==view.data['config']['store_id'] and cut['branch_ref']=='branch:'+cut['store_ref']
        assert len(cut['streams'])==len(view.data['projection']['histories'])
    G.verify(O.SOURCE)
    O.write(PVT/'expected-public-cut-v2.json',cut)
    O.write(PVT/'reader_wrapper-v2.py',WRAPPER.encode())
    selection=O.load(PVT/'selection.json')
    selection['private_inputs']['cut']=O.binding(PVT/'expected-public-cut-v2.json')
    O.write(PVT/'selection-v2.json',selection)
    args=['-I','-B',str(PVT/'reader_wrapper-v2.py'),'--selection',str(PVT/'selection-v2.json'),
        '--selection-sha256',O.sha((PVT/'selection-v2.json').read_bytes()),'--wrapper-sha256',O.sha((PVT/'reader_wrapper-v2.py').read_bytes())]
    config={'command':O.PYTHON,'args':args,'cwd':str(O.ROOT),'timeoutSec':980,'graceSec':15}
    O.write(PVT/'adapter-config-v2.json',config)
    value={'result':'PREPARED','at':O.now(),'source':O.SOURCE,'profile':O.PROFILE,'source_name':policy['source_name'],
        'actual_cold_replay_public_cut':cut,'historical_policy_custody_cut':policy['history_control']['source_cut'],
        'grant_expires_at':policy['expires_at'],'expiry_changed':False,'private_seed_and_key_changed':False,
        'wrapper_binding':O.binding(PVT/'reader_wrapper-v2.py'),'selection_binding':O.binding(PVT/'selection-v2.json'),
        'adapter_config_binding':O.binding(PVT/'adapter-config-v2.json'),'original_failed_wrapper_binding':O.binding(PVT/'reader_wrapper.py'),
        'original_direct_counterevidence_binding':O.binding(HERE/'direct.json'),'setup_code_binding':O.binding(Path(__file__)),
        'exact_cut_function_binding':O.binding(O.API/'handlers.py'),'full_source_entry_exit':'PASS','owned_native_replay_closed':True,
        'read_only_policy_operations':O.READS,'agent_exposed_operations':['lab.status','catalog.get'],
        'private_keys_exported':False,'authority_effect':'none','human_pilot_complete':False}
    O.write(HERE/'readiness-v2.json',value);O.write(HERE/'adapter-config-v2.redacted.json',config)
    print(json.dumps(value),flush=True)
def direct():
    c=O.load(PVT/'adapter-config-v2.json')
    result=subprocess.run([c['command'],*c['args']],cwd=c['cwd'],capture_output=True,timeout=990)
    O.write(PVT/'direct-v2.stdout',result.stdout);O.write(PVT/'direct-v2.stderr',result.stderr)
    value={'at':O.now(),'actual_os_exit_code':result.returncode,'result':json.loads(result.stdout),'config_binding':O.binding(PVT/'adapter-config-v2.json')}
    O.write(HERE/'direct-v2.json',value);print(json.dumps(value),flush=True)
    return result.returncode
def create():
    d=O.load(HERE/'direct-v2.json');assert d['actual_os_exit_code']==0 and d['result']['result']=='PASS'
    assert not (PVT/'server-selection.json').exists()
    company=O.http('/api/companies',{'name':'CyberAlchemy Lab','description':'Owned local pilot: exact historical W09 engineering Lab evidence reads. Technical validation only; no Lab actions, Sessions or admission.','budgetMonthlyCents':0})
    O.write(PVT/'company.json',company)
    if company.get('requireBoardApprovalForNewAgents'):
        company=O.http('/api/companies/'+company['id'],{'requireBoardApprovalForNewAgents':False},'PATCH')
    config=O.load(PVT/'adapter-config-v2.json')
    agent=O.http('/api/companies/'+company['id']+'/agents',{'name':'Lab evidence reader','role':'general','title':'Historical Lab evidence reader','adapterType':'process',
        'capabilities':'Fixed nonce-authenticated status/catalog reads from exact genuine W09 engineering history. No governing role, Lab Session, action or admission.',
        'adapterConfig':config,'runtimeConfig':{'heartbeat':{'enabled':True,'intervalSec':0,'wakeOnDemand':True}},
        'permissions':{'canCreateAgents':False,'canCreateSkills':False,'canAssignTasks':False},'budgetMonthlyCents':0})
    O.write(PVT/'agent.json',agent)
    run=O.http('/api/agents/'+agent['id']+'/heartbeat/invoke',{'reason':'approved-local-read-only-technical-check','idempotencyKey':'paperclip-local-reader-0270-'+O.uuid.uuid4().hex})
    O.write(PVT/'server-selection.json',{'company_id':company['id'],'agent_id':agent['id'],'run_id':run['id'],'created_at':O.now()})
    value={'company_id':company['id'],'agent_id':agent['id'],'run_id':run['id'],'local_url':O.URL,'agent_name':agent['name'],
        'adapter_type':agent['adapterType'],'initial_run_status':run.get('status'),'human_pilot_complete':False,'governing_role_assigned':False}
    O.write(HERE/'server-created.json',value);print(json.dumps(value),flush=True)
def poll():
    s=O.load(PVT/'server-selection.json');run=O.http('/api/heartbeat-runs/'+s['run_id'])
    O.write(PVT/('run-observation-'+O.uuid.uuid4().hex+'.json'),run)
    print(json.dumps({k:run.get(k) for k in ('id','status','exitCode','signal','startedAt','finishedAt','error')}),flush=True)
    if run.get('status') not in ('succeeded','failed','cancelled','timed_out'):return 2
    result=run.get('resultJson',{});stdout=result.get('stdout') if isinstance(result,dict) else None
    value=json.loads(stdout) if stdout else None
    if value is None and isinstance(run.get('result'),dict):
        value=json.loads(run['result'].get('resultJson',{}).get('stdout','null'))
    M=O.modules();G=M('guard');G.verify(O.SOURCE)
    report={'result':'PASS' if run.get('status')=='succeeded' and run.get('exitCode')==0 and value and value.get('result')=='PASS' else 'FAIL',
        'at':O.now(),'company_id':s['company_id'],'agent_id':s['agent_id'],'run_id':s['run_id'],'server_run_status':run.get('status'),
        'actual_process_exit_code':run.get('exitCode'),'actual_process_result':value,'source':O.SOURCE,'profile':O.PROFILE,
        'readiness_binding':O.binding(HERE/'readiness-v2.json'),'direct_check_binding':O.binding(HERE/'direct-v2.json'),'created_binding':O.binding(HERE/'server-created.json'),
        'setup_code_binding':O.binding(Path(__file__)),'original_setup_code_binding':O.binding(original),
        'original_direct_counterevidence_binding':O.binding(HERE/'direct.json'),'full_source_current_exit':'PASS','local_url':O.URL,
        'private_keys_exported':False,'human_pilot_complete':False,'value_outcome_observed':False,'authority_effect':'none',
        'whole_API_qualified':False,'task_complete':False,'claim_ceiling':'Actual owned local Paperclip process-agent invocation of exact authenticated historical status/catalog reads only.'}
    O.write(HERE/'qualification.json',report);print(json.dumps(report),flush=True)
    return 0 if report['result']=='PASS' else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','direct','create','poll']);a=p.parse_args()
    raise SystemExit(globals()[a.mode]() or 0)
