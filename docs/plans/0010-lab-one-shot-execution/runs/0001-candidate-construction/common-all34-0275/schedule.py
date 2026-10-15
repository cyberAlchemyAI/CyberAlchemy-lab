"""Run every new frozen16 common-dispatcher unit and observe real terminals."""
import concurrent.futures, hashlib, json, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
PLAN=HERE/'plan.json'
PIN='33c89d729656aa791e62028b6f8359b0d54473da95e5894b3ccc6e7905c789d9'
def run(unit):
 assert hashlib.sha256(PLAN.read_bytes()).hexdigest()==PIN
 plan=json.loads(PLAN.read_bytes());argv=[sys.executable,'-B',str(HERE/'run_unit.py')]
 for key,value in [('api-directory',plan['api_directory']),('source',plan['source_sha256']),('profile',plan['profile_sha256']),('caller-sha256',plan['caller_binding']['sha256']),('plan-sha256',PIN),('plan',str(PLAN)),('unit',unit)]:argv += ['--'+key,str(value)]
 result=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 output=HERE/(unit.replace(':','--').replace('.','-')+'.scheduler-terminal.json')
 observation={'unit':unit,'actual_runner_exit_code':result.returncode,'runner_output':result.stdout.decode(errors='replace'),'authority_effect':'none'}
 with output.open('x') as f:json.dump(observation,f,indent=2);f.write('\n')
 print(json.dumps({'unit':unit,'actual_runner_exit_code':result.returncode}),flush=True)
 return observation
if __name__=='__main__':
 plan=json.loads(PLAN.read_bytes())
 # The single real Source8 lifetime starts promptly while all other units run serially.
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
  source8=executor.submit(run,'member:Source8-lifecycle')
  for unit in plan['units']:
   if unit!='member:Source8-lifecycle':run(unit)
  source8.result()
 print(json.dumps({'scheduler_terminal':True,'aggregate_required':True,'authority_effect':'none'}),flush=True)
