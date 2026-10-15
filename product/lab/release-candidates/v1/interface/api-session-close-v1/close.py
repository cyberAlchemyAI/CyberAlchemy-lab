"""Retain complete parent closure and record proven Context/Session partial progress."""
import argparse,hashlib,json,os
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_bytes())
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();assert sha(HERE/'source-manifest.json')==a.source_sha256
 for row in load(HERE/'source-manifest.json')['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 parent=HERE.parent/'context-delivery-v3/receipts/R03-0014.json';previous=load(parent);assert sha(parent)=='4755b2961df56acbecc6c1e944cb6877fc9fd2c660a5dcd93a84fcb70ee8540b'
 audit=load(HERE.parent/'api-session-audit-v3/result.json');tests=load(HERE.parent/'api-session-tests-v4/receipts/0001/tests.json');process=load(HERE.parent/'api-session-process-v2/receipts/0001/result.json')
 assert audit['result']==tests['result']==process['result']=='PASS' and tests['tests_run']==34 and tests['errors']==tests['failures']==0
 paths={row['path'] for row in previous['files']};paths.add(str(parent.relative_to(ROOT)))
 for row in previous['files']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
 directories=['api-v13','api-v14','api-session-process-v1','api-session-process-v2','api-session-tests-v1','api-session-tests-v2','api-session-tests-v3','api-session-tests-v4','api-session-snapshot-v1','api-session-audit-v1','api-session-audit-v2','api-session-audit-v3','session-environment-recovery-v1','api-session-close-v1']
 for directory in directories:
  for path in (HERE.parent/directory).rglob('*'):
   if path.is_file() and '__pycache__' not in path.parts and path.suffix!='.pyc':paths.add(str(path.relative_to(ROOT)))
 run=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
 for path in run.glob('context-R03-*session*json'):paths.add(str(path.relative_to(ROOT)))
 for filename in ['context-R03-session-suite-0004.json','context-R03-session-environment-recovery-0001.json','session-environment-interruption-0001.json']:paths.add(str((run/filename).relative_to(ROOT)))
 rows=[{'path':name,'sha256':sha(ROOT/name)} for name in sorted(paths)]
 remaining=previous['remaining_obligations']
 if not isinstance(remaining,list):raise ValueError('original remaining obligation list unavailable')
 remaining=[s.replace('27 remaining','23 remaining').replace('7/34','11/34') if isinstance(s,str) else s for s in remaining]
 remaining += ['Complete all other 23 original public API handlers and full original R03 criteria; no task, public API or owner obligation is narrowed.', 'Actual human R04 pilot and final full S02/R08 review remain required; no canonical admission, activation or publication occurred.', 'Only scoped source-reader resources were realized. Tool/model dispatch and complete Product capability realization remain unproven.', 'Original arbitrary-byte custody followup remains open; retained old source/definition/index gaps remain independent.', 'Historical Context deliveries, destroyed process scopes and interrupted test runs grant no current permission or memory rehydration. The original absolute Assignment period must never be silently reset.']
 result={'schema_version':'lab-R03-context-session-partial-proof/v1-candidate','task':'R03','result':'PASS','task_complete':False,'authority_effect':'none','actual_owner_outcome':None,'goal_complete':False,'parent_receipt_binding':{'path':str(parent.relative_to(ROOT)),'sha256':sha(parent)},'files':rows,'retained_parent_file_count':len(previous['files']),'actual_session_suite_tests':34,'actual_preparation_regression_tests':47,'actual_immutable_reader_regression_tests':157,'actual_supplemental_snapshot_tests':1,'independent_audit_checks':len(audit['checks']),'actual_process_checks':len(process['checks']),'actual_processes':len(process['children']),'actual_wire_frames':audit['wire_frames'],'actual_public_api_operations':11,'original_public_api_obligations':34,'remaining_public_api_operations':23,'original_task_obligations':46,'closed_task_criteria':35,'remaining_obligations':remaining,'canonical_effects_applied':0,'private_keys_exported':False,'short_memory_exported':False,'historical_protected_source_custody':'Original protected archives remain in their original privacy boundary; new replies and eligible process exports contain no Session memory or private key.','claim_ceiling':'Selected Context and Ontology delivery, classified ephemeral source-reader resources, original API controls, actual disposal/expiry and process loss/cold metadata proof. Full R03, all 34 APIs, human pilot, owner outcome, canonical admission and complete plan remain unproven.'}
 output=HERE/'receipts/R03-0015.json';output.parent.mkdir(exist_ok=True,mode=0o700)
 fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write((json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
 print(json.dumps({'result':'PASS','files':len(rows),'parent_files_retained':len(previous['files']),'public_operations':11,'remaining_APIs':23,'task_complete':False,'receipt_sha256':sha(output)}))
if __name__=='__main__':main()
