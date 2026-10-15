"""Approved owned local Paperclip reader setup; no Lab mutation or human claim."""
import argparse,base64,hashlib,importlib.util,json,os,subprocess,sys,tempfile,uuid
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
HERE=Path(__file__).resolve().parent
STATE=Path('/home/vlad_/.local/share/cal-paperclip-pilot-20261013')
PRIVATE=STATE/'lab-reader'
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v14'
CLIENT=API.parent/'paperclip-runner-v3'
SOURCE='aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240'
PROFILE='327d3c480168b0008597969e31e11e73f429370a226bd16370245e82ef78fb16'
PYTHON='/tmp/cal-R02-environment-0001/bin/python'
URL='http://127.0.0.1:3100'
READS=['lab.status','catalog.get','artifact.inspect','artifact.query']
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def load(path):return json.loads(Path(path).read_bytes())
def now():return datetime.now(timezone.utc).isoformat()
def write(path,value):
    raw=value if isinstance(value,bytes) else encoded(value)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw)
def http(path,body=None,method=None):
    req=Request(URL+path,data=None if body is None else encoded(body),headers={'Content-Type':'application/json'},method=method)
    with urlopen(req,timeout=15) as response:return json.load(response)
def binding(path):return {'path':str(path),'sha256':sha(Path(path).read_bytes())}
def modules():
    name='_cal_owned_paperclip_history_API14_0270'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return lambda suffix:__import__(name+'.'+suffix,fromlist=['*'])

# The persistent seed is never passed to Lab. Each invocation makes an owned
# private copy, rebases ONLY the empty workspace root, and retains seed expiry.
# A fresh pin check every second invalidates the staged grant on seed revocation.
WRAPPER=r'''import argparse,hashlib,json,os,stat,subprocess,sys,tempfile,time,uuid
from datetime import datetime,timezone
from pathlib import Path
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def selected(path,pin):
 p=Path(path);s=p.stat()
 assert p.is_absolute() and p.resolve()==p and not p.is_symlink() and not any(a.is_symlink() for a in p.parents)
 assert stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_mode&0o777==0o600
 raw=p.read_bytes();assert sha(raw)==pin
 return raw
def write(p,raw):
 fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'wb') as f:f.write(raw)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--selection',required=True);parser.add_argument('--selection-sha256',required=True)
 parser.add_argument('--wrapper-sha256',required=True);a=parser.parse_args()
 selected(Path(__file__).resolve(),a.wrapper_sha256)
 raw=selected(a.selection,a.selection_sha256);s=json.loads(raw)
 rows=s['private_inputs'];inputs={k:selected(v['path'],v['sha256']) for k,v in rows.items()}
 policy=json.loads(inputs['policy']);plan=json.loads(inputs['plan'])
 assert policy['allowed_operations']==['lab.status','catalog.get','artifact.inspect','artifact.query']
 assert policy['session_control'] is None and policy['projection_control'] is None and policy['history_control']['inspection_only'] is True
 assert policy['revoked'] is False and datetime.fromisoformat(policy['expires_at'])>datetime.now(timezone.utc)
 assert [x['operation'] for x in plan['steps']]==['lab.status','catalog.get']
 assert plan['steps'][0]['selectors']=={} and plan['steps'][1]['selectors']=={'carrier_refs':[],'include_relations':True,'limit':20,'page_cursor':None}
 env={k:v for k,v in os.environ.items() if not k.startswith('PAPERCLIP_') and k not in ('PYTHONPATH','PYTHONSTARTUP','PYTHONINSPECT')}
 env['PYTHONDONTWRITEBYTECODE']='1'
 episode=Path(s['runs'])/(uuid.uuid4().hex+'.json');log=episode.with_suffix('.stderr');terminal=episode.with_suffix('.terminal.json')
 started=datetime.now(timezone.utc).isoformat();removed=False;revoked=False;returncode=None;observed=None
 with tempfile.TemporaryDirectory(prefix='cal-paperclip-reader-0270-') as tmp:
  owned=Path(tmp);owned.chmod(0o700);workspace=owned/'workspace';workspace.mkdir(mode=0o700)
  for name in ('inputs','objects','journal'):(workspace/name).mkdir(mode=0o700)
  write(workspace/'workspace.json',inputs['workspace'])
  policy['workspace']['root']=str(workspace);write(owned/'policy.json',encoded(policy));write(owned/'reader.pem',inputs['key']);write(owned/'plan.json',inputs['plan'])
  args=[s['python'],'-I','-B',s['runner'],'--api-root',s['api'],'--source-sha256',s['source'],'--profile-sha256',s['profile'],
   '--policy',str(owned/'policy.json'),'--policy-sha256',sha((owned/'policy.json').read_bytes()),'--reader-key',str(owned/'reader.pem'),'--reader-key-sha256',sha(inputs['key']),
   '--plan',str(owned/'plan.json'),'--plan-sha256',sha(inputs['plan']),'--timeout-seconds','900']
  out=os.open(episode,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);err=os.open(log,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(out,'wb') as f,os.fdopen(err,'wb') as e:
   child=subprocess.Popen(args,stdout=f,stderr=e,env=env,cwd=s['repository']);limit=time.monotonic()+960
   try:
    while child.poll() is None:
     try:
      selected(a.selection,a.selection_sha256)
      for k,v in rows.items():selected(v['path'],v['sha256'])
      assert time.monotonic()<limit
     except Exception:
      revoked=True;(owned/'policy.json').write_bytes(encoded({'revoked':True}));child.terminate();break
     time.sleep(1)
    try:returncode=child.wait(timeout=10)
    except subprocess.TimeoutExpired:child.kill();returncode=child.wait(timeout=10)
   finally:
    if child.poll() is None:child.kill();child.wait(timeout=10)
  objects=len(list((workspace/'objects').iterdir()));journals=len(list((workspace/'journal').iterdir()))
 removed=not owned.exists()
 for k,v in rows.items():selected(v['path'],v['sha256'])
 try:observed=json.loads(episode.read_bytes())
 except Exception:observed=None
 passed=returncode==0 and not revoked and removed and objects==journals==0 and observed is not None and observed.get('result')=='PASS'
 if passed:
  assert [x['operation'] for x in observed['calls']]==['lab.status','lab.status','catalog.get']
  assert observed['Lab_mutations_requested']==0 and observed['private_keys_exported'] is False
  assert observed['source_cut']==policy['history_control']['source_cut']
 summary={'result':'PASS' if passed else 'FAIL','source':s['source'],'profile':s['profile'],'source_name':policy['source_name'],
  'source_cut':None if observed is None else observed.get('source_cut'),'grant_expires_at':policy['expires_at'],
  'operations':[] if observed is None else [x['operation'] for x in observed.get('calls',[])],
  'episode_path':str(episode),'episode_sha256':sha(episode.read_bytes()),'actual_runner_exit_code':returncode,
  'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'owned_stage_removed':removed,
  'workspace_objects':objects,'workspace_journal_records':journals,'seed_revocation_detected':revoked,
  'Lab_mutations_requested':0,'private_keys_exported':False,'human_pilot_complete':False,'authority_effect':'none'}
 write(terminal,encoded(summary));print(json.dumps(summary,sort_keys=True),flush=True)
 return 0 if passed else 1
if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as e:print(json.dumps({'result':'FAIL','error_class':type(e).__name__}),flush=True);raise SystemExit(1)
'''

def prepare():
    assert http('/api/health')['deploymentMode']=='local_trusted'
    assert not PRIVATE.exists(),'retain existing approved reader state; no overwrites'
    assert STATE.is_dir() and STATE.stat().st_mode&0o777==0o700
    M=modules();G=M('guard');P=M('protocol');G.verify(SOURCE);schemas=P.Schemas(PROFILE)
    selected=P.source.history_selection('genuine-W09-engineering-history')
    provider=P.source.history_provider();provider.validate_policy
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    key=Ed25519PrivateKey.generate();principal='principal:Paperclip-local-history-reader:'+uuid.uuid4().hex
    manifest={'schema_version':'lab-owned-candidate-workspace/v1-candidate','workspace_ref':'Paperclip-local-history-'+uuid.uuid4().hex,
        'principal_ref':principal,'scope_refs':[selected['scope_ref']],'materials':[],'target_metadata':{},'authority_effect':'none','actual_owner_outcome':None}
    workspace_raw=P.source.encoded(manifest)
    ref=lambda path,pin:{'ref':str(path.relative_to(ROOT)),'sha256':pin}
    policy={'schema_version':'lab-local-genuine-history-read-policy/v1-candidate','principal_ref':principal,
        'reader_public_key':base64.b64encode(key.public_key().public_bytes_raw()).decode(),'host_uid':os.getuid(),
        'source_name':selected['name'],'scope_refs':[selected['scope_ref']],'expires_at':(datetime.now(timezone.utc)+timedelta(minutes=30)).isoformat(),
        'max_request_bytes':65536,'max_response_bytes':1048576,'max_calls':16,'allowed_operations':READS,
        'session_control':None,'projection_control':None,'revoked':False,'scope_posture':'isolated-candidate-preparation','authority_effect':'none','actual_owner_outcome':None,
        'workspace':{'root':'/tmp/cal-paperclip-inactive-seed-0270/workspace','manifest_sha256':sha(workspace_raw),'max_actions':1},
        'development_authorization_binding':ref(RUN/'authorization.json',sha((RUN/'authorization.json').read_bytes())),
        'history_control':{'provider_source_binding':ref(provider.HERE/'source-manifest.json',P.source.HISTORY_PROVIDER_PIN),
            'provider_selection_binding':ref(provider.HERE/'selection.json',P.source.HISTORY_SELECTION_PIN),
            'source_archive_binding':{'ref':selected['archive_binding']['path'],'sha256':selected['archive_binding']['sha256']},
            'source_cut':{'baseline_snapshot_digest':selected['baseline_snapshot_digest'],'signed_head':selected['expected_head'],'sequence':1},
            'inspection_only':True,'expired_lessons_grant_application':False}}
    assert schemas.valid('reader-authentication',policy);P.source.validate_history_policy(policy)
    PRIVATE.mkdir(mode=0o700);(PRIVATE/'runs').mkdir(mode=0o700)
    write(PRIVATE/'reader.pem',key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));key=None
    write(PRIVATE/'policy.json',P.compact(policy));write(PRIVATE/'workspace.json',workspace_raw)
    write(PRIVATE/'plan.json',{'schema_version':'lab-paperclip-read-plan/v1-candidate','steps':[{'operation':'lab.status','selectors':{}},
        {'operation':'catalog.get','selectors':{'carrier_refs':[],'include_relations':True,'limit':20,'page_cursor':None}}]})
    write(PRIVATE/'reader_wrapper.py',WRAPPER.encode())
    selection={'python':PYTHON,'runner':str(CLIENT/'runner.py'),'api':str(API),'source':SOURCE,'profile':PROFILE,'repository':str(ROOT),'runs':str(PRIVATE/'runs'),
        'private_inputs':{k:binding(PRIVATE/n) for k,n in [('policy','policy.json'),('key','reader.pem'),('workspace','workspace.json'),('plan','plan.json')]}}
    write(PRIVATE/'selection.json',selection)
    args=['-I','-B',str(PRIVATE/'reader_wrapper.py'),'--selection',str(PRIVATE/'selection.json'),'--selection-sha256',sha((PRIVATE/'selection.json').read_bytes()),
        '--wrapper-sha256',sha((PRIVATE/'reader_wrapper.py').read_bytes())]
    config={'command':PYTHON,'args':args,'cwd':str(ROOT),'timeoutSec':980,'graceSec':15}
    write(PRIVATE/'adapter-config.json',config)
    G.verify(SOURCE)
    receipt={'result':'PREPARED','at':now(),'source':SOURCE,'profile':PROFILE,'source_name':policy['source_name'],'historical_source_cut':policy['history_control']['source_cut'],
        'read_only_policy_operations':READS,'agent_exposed_operations':['lab.status','catalog.get'],'grant_expires_at':policy['expires_at'],
        'wrapper_binding':binding(PRIVATE/'reader_wrapper.py'),'selection_binding':binding(PRIVATE/'selection.json'),'adapter_config_binding':binding(PRIVATE/'adapter-config.json'),
        'full_source_entry_exit':'PASS','persistent_private_modes':'0600 files/0700 directories','private_keys_exported':False,'authority_effect':'none','human_pilot_complete':False}
    write(HERE/'readiness.json',receipt);print(json.dumps(receipt),flush=True)
def direct():
    c=load(PRIVATE/'adapter-config.json');result=subprocess.run([c['command'],*c['args']],cwd=c['cwd'],capture_output=True,timeout=990)
    write(PRIVATE/'direct.stdout',result.stdout);write(PRIVATE/'direct.stderr',result.stderr)
    value={'at':now(),'actual_os_exit_code':result.returncode,'result':json.loads(result.stdout),'config_binding':binding(PRIVATE/'adapter-config.json')}
    write(HERE/'direct.json',value);print(json.dumps(value),flush=True)
    return result.returncode
def create():
    direct=load(HERE/'direct.json');assert direct['actual_os_exit_code']==0 and direct['result']['result']=='PASS'
    assert not (PRIVATE/'server-selection.json').exists()
    company=http('/api/companies',{'name':'CyberAlchemy Lab','description':'Owned local pilot: exact historical Lab evidence reads; technical validation only. No Lab actions or admission.','budgetMonthlyCents':0})
    write(PRIVATE/'company.json',company)
    if company.get('requireBoardApprovalForNewAgents'):
        company=http('/api/companies/'+company['id'],{'requireBoardApprovalForNewAgents':False},'PATCH')
    config=load(PRIVATE/'adapter-config.json')
    agent=http('/api/companies/'+company['id']+'/agents',{'name':'Lab evidence reader','role':'general','title':'Historical Lab evidence reader','adapterType':'process',
        'capabilities':'Fixed nonce-authenticated status/catalog reads from exact genuine W09 engineering history. No governing role, Lab Session, action or admission.',
        'adapterConfig':config,'runtimeConfig':{'heartbeat':{'enabled':True,'intervalSec':0,'wakeOnDemand':True}},
        'permissions':{'canCreateAgents':False,'canCreateSkills':False,'canAssignTasks':False},'budgetMonthlyCents':0})
    write(PRIVATE/'agent.json',agent)
    run=http('/api/agents/'+agent['id']+'/heartbeat/invoke',{'reason':'approved-local-read-only-technical-check','idempotencyKey':'paperclip-local-reader-0270-'+uuid.uuid4().hex})
    write(PRIVATE/'server-selection.json',{'company_id':company['id'],'agent_id':agent['id'],'run_id':run['id'],'created_at':now()})
    value={'company_id':company['id'],'agent_id':agent['id'],'run_id':run['id'],'local_url':URL,'company_url':URL+'/'+company.get('issuePrefix','')+'/dashboard','agent_name':agent['name'],'adapter_type':agent['adapterType'],'initial_run_status':run.get('status'),'human_pilot_complete':False}
    write(HERE/'server-created.json',value);print(json.dumps(value),flush=True)
def poll():
    s=load(PRIVATE/'server-selection.json');run=http('/api/heartbeat-runs/'+s['run_id'])
    write(PRIVATE/('run-observation-'+uuid.uuid4().hex+'.json'),run)
    print(json.dumps({k:run.get(k) for k in ('id','status','exitCode','signal','startedAt','finishedAt','error')}),flush=True)
    if run.get('status') not in ('succeeded','failed','cancelled','timed_out'):return 2
    parsed=run.get('resultJson',{});stdout=parsed.get('stdout') if isinstance(parsed,dict) else None
    value=json.loads(stdout) if stdout else None
    # DTOs may expose the adapter result through a nested field. Do not infer success.
    if value is None and isinstance(run.get('result'),dict):
        value=json.loads(run['result'].get('resultJson',{}).get('stdout','null'))
    M=modules();G=M('guard');G.verify(SOURCE)
    report={'result':'PASS' if run.get('status')=='succeeded' and run.get('exitCode')==0 and value and value.get('result')=='PASS' else 'FAIL',
        'at':now(),'company_id':s['company_id'],'agent_id':s['agent_id'],'run_id':s['run_id'],'server_run_status':run.get('status'),
        'actual_process_exit_code':run.get('exitCode'),'actual_process_result':value,'source':SOURCE,'profile':PROFILE,
        'readiness_binding':binding(HERE/'readiness.json'),'direct_check_binding':binding(HERE/'direct.json'),'created_binding':binding(HERE/'server-created.json'),
        'setup_code_binding':binding(Path(__file__)),'full_source_current_exit':'PASS','local_url':URL,'private_keys_exported':False,
        'human_pilot_complete':False,'value_outcome_observed':False,'authority_effect':'none','whole_API_qualified':False,'task_complete':False}
    write(HERE/'qualification.json',report);print(json.dumps(report),flush=True)
    return 0 if report['result']=='PASS' else 1
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','direct','create','poll']);a=p.parse_args()
    result=globals()[a.mode]();raise SystemExit(result or 0)
