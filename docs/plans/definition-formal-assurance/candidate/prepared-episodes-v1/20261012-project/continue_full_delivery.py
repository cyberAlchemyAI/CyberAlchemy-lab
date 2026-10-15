"""Continue the current Project delivery sequentially after its actual replay.

No producer is restarted. A failed or missing terminal observation stops this
controller. New unit writes stop at sealing; the following audit is read-only.
ARE continuation and state closure remain separate subsequent actions.
"""
from pathlib import Path
import json,subprocess,sys,time
root=Path.cwd();p=Path(__file__).resolve().parent
u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D60'
CAPTURE_PID=452232
def put(name,data):
 with (p/name).open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
def expected_capture_live():
 path=Path('/proc')/str(CAPTURE_PID)/'cmdline'
 try:raw=path.read_bytes()
 except FileNotFoundError:return False
 return b'20261012-project/capture_fresh_delivery.py' in raw
def run_stage(label,argv):
 result=subprocess.run(argv,cwd=root,capture_output=True)
 stem='sequential-'+label
 for suffix,data in [('stdout.txt',result.stdout),('stderr.txt',result.stderr)]:
  with (p/(stem+'-'+suffix)).open('xb') as f:f.write(data)
 row={'stage':label,'argv':argv,'exit_code':result.returncode,
      'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'}
 put(stem+'-command-result.json',row)
 print(json.dumps({'stage':label,'exit_code':result.returncode}),flush=True)
 if result.returncode or result.stderr:
  raise RuntimeError('Actual stage failed; evidence retained: '+stem)
 return row
def main():
 print('Waiting on existing exact capture PID452232/session59946; no restart.',flush=True)
 while expected_capture_live():time.sleep(2)
 capture=p/'fresh-delivery-command-result.json'
 if not capture.is_file():
  raise RuntimeError('Existing replay capture is terminal or absent, with no actual command result.')
 cmd=json.loads(capture.read_bytes())
 assert cmd['exit_code']==0 and not(p/cmd['stderr']).read_bytes(),cmd
 fresh=json.loads((u/'fresh-command-results.json').read_bytes())
 assert [x['check'] for x in fresh]==['contract','model','source','profile','dependency','inventory']
 assert all(x['exit_code']==0 and not(u/x['stderr']).read_bytes() for x in fresh)
 for x in fresh[1:]:
  assert (u/x['stdout']).read_bytes()==(u/(x['check']+'-stdout.txt')).read_bytes()
 assert not(u/'DELIVERY-REVIEW.md').exists() and not(u/'delivery-manifest.json').exists()
 stages=[]
 stages.append(run_stage('full-review',[sys.executable,'-B',str(p/'write_full_review.py')]))
 stages.append(run_stage('full-seal',[sys.executable,'-B',str(p/'capture_full_delivery.py'),'seal']))
 assert (u/'delivery-manifest.json').is_file()
 # No UNIT mutation is permitted between this seal and its separate audit.
 stages.append(run_stage('full-audit',[sys.executable,'-B',str(p/'capture_full_delivery.py'),'audit']))
 seal=json.loads((p/'full-delivery-seal-command-result.json').read_bytes())
 audit=json.loads((p/'full-delivery-audit-command-result.json').read_bytes())
 assert seal['exit_code']==audit['exit_code']==0
 report={'schema_version':'Project-sequential-full-delivery/v1-candidate',
         'result':'PASS-for-actual-full-seal-and-separate-audit',
         'existing_fresh_capture_pid':CAPTURE_PID,'existing_fresh_session_id':59946,
         'stages':stages,'candidate_files':len(json.loads((u/'delivery-manifest.json').read_bytes())['files']),
         'full_review_words':len((u/'DELIVERY-REVIEW.md').read_text().split()),
         'next_required_actions':['AREfullcontinuation','close_full_state.py','Capability Instance native types/logic'],
         'next_native_created':False,'source_fidelity':'pending','semantic_ready':False,
         'whole_definition_proofs':0,'authority_effect':'none','goal_status':'active'}
 put('sequential-delivery-result.json',report)
 print(json.dumps({'result':report['result'],'candidate_files':report['candidate_files'],'goal_status':'active'}),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as error:
  put('sequential-delivery-failure.json',{'result':'failed-without-restart','error_type':type(error).__name__,'error':str(error),'authority_effect':'none','goal_status':'active'})
  raise

