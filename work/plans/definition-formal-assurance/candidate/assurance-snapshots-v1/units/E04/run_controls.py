"""Run the SWU-mandated command and retain exact attempt output and denominator."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6]
COMMAND=['python3','-m','unittest','discover','-s','craft/formalization/candidates/definition-assurance-v1/tests','-p','test_E04.py']
def ref(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def put(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
def main():
 attempt=1
 while (UNIT/f'run-{attempt:03d}').exists():attempt+=1
 folder=UNIT/f'run-{attempt:03d}';folder.mkdir();put(folder/'invocation.json',{'command':COMMAND,'working_directory':str(ROOT),'authority_effect':'none','unit':'E04.1'})
 completed=subprocess.run(COMMAND,cwd=ROOT,capture_output=True)
 for name,raw in [('stdout.txt',completed.stdout),('stderr.txt',completed.stderr)]:
  with (folder/name).open('xb') as f:f.write(raw)
 records=[line.split('=',1)[1] for line in completed.stdout.decode().splitlines() if line.startswith('E04_CONTROL_RESULTS=')]
 report=json.loads(records[0]) if len(records)==1 else None
 valid=completed.returncode==0 and report is not None and report['declared_case_count']==76 and report['executed_case_count']==76 and len(report['cases'])==76 and all(row['outcome']=='PASS' and row['tests_run']==1 and not any(row[k] for k in ['skipped','errors','failures','unexpected_successes','expected_failures']) for row in report['cases'])
 value={'result':'PASS' if valid else 'FAIL','return_code':completed.returncode,'command':COMMAND,'control_results':report,'stdout_ref':ref(folder/'stdout.txt'),'stderr_ref':ref(folder/'stderr.txt'),'authority_effect':'none','semantic_ready':False,'goal_status':'active'};put(folder/'result.json',value)
 print(json.dumps({'result':value['result'],'attempt':attempt,'executed_cases':report['executed_case_count'] if report else None,'result_path':str(folder/'result.json'),'elapsed_seconds':report['elapsed_seconds'] if report else None}));print(completed.stderr.decode()[-3000:]);sys.exit(0 if valid else 1)
if __name__=='__main__':main()
