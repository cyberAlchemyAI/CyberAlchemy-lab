"""Six independent read-only replays with exact terminal capture and stdout comparison."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,subprocess,sys
root=Path.cwd();unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.coordination-context';impl=root/'craft/formalization/candidates/definition-assurance-v1';order=['contract','model','source','profile','dependency','inventory']
commands={'contract':[sys.executable,'-B',str(impl/'contracts.py'),'validate','--kind','interpretation','--input',str(unit/'t.json')]}
for name,script in [('model','verify_candidate.py'),('source','verify_source_checks.py'),('profile','verify_authority_profile.py'),('dependency','verify_dependencies.py'),('inventory','verify_current_inventory.py')]:commands[name]=[sys.executable,'-B',str(unit/script)]
def run(name):
 result=subprocess.run(commands[name],cwd=root,capture_output=True);stem='fresh-'+name;row={'check':name,'argv':commands[name],'exit_code':result.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'}
 for key,data in [('stdout',result.stdout),('stderr',result.stderr)]:
  with (unit/row[key]).open('xb') as f:f.write(data)
 with (unit/(stem+'-command-result.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 expected=unit/('fresh-types-contract-stdout.txt' if name=='contract' else name+'-stdout.txt');print(name,result.returncode,'stdout_equal',result.stdout==expected.read_bytes(),flush=True)
 if result.returncode or result.stderr or result.stdout!=expected.read_bytes():raise ValueError('Fresh replay failed '+name)
 return row
rows={};errors=[]
with ThreadPoolExecutor(max_workers=3) as pool:
 futures={pool.submit(run,name):name for name in order}
 for future in as_completed(futures):
  try:rows[futures[future]]=future.result()
  except Exception as error:errors.append(str(error))
if errors:print(json.dumps({'errors':errors}),flush=True);raise SystemExit(1)
with (unit/'fresh-command-results.json').open('x') as f:json.dump([rows[name] for name in order],f,indent=2);f.write('\n')
print('PASS-six-fresh-full-delivery-checks',flush=True)
