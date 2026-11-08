"""Six independent read-only checks with retained actual terminal results."""
from pathlib import Path
import json,sys,subprocess,os
import build_candidate as b
jobs=[('contract',b.IMPL/'contracts.py',['validate','--kind','interpretation','--input',str(b.UNIT/'t.json')]),('model',b.UNIT/'verify_candidate.py',[]),('source',b.UNIT/'verify_source_checks.py',[]),('profile',b.UNIT/'verify_authority_profile.py',[]),('dependency',b.UNIT/'verify_dependencies.py',[]),('inventory',b.UNIT/'verify_current_inventory.py',[])];rows=[]
for name,script,extra in jobs:
 argv=[sys.executable,'-B',str(script)]+extra;r=subprocess.run(argv,cwd=b.ROOT,capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));row={'check':name,'argv':argv,'exit_code':r.returncode,'stdout':'fresh-'+name+'-stdout.txt','stderr':'fresh-'+name+'-stderr.txt'}
 for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
  with (b.UNIT/row[k]).open('xb') as f:f.write(raw)
 with (b.UNIT/('fresh-'+name+'-command-result.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 rows.append(row);print(json.dumps({'check':name,'exit_code':r.returncode}),flush=True)
 if r.returncode or r.stderr:raise SystemExit(r.returncode or 1)
 if name!='contract':assert r.stdout==(b.UNIT/(name+'-stdout.txt')).read_bytes(),'Fresh '+name+' observation differs'
b.put('fresh-command-results.json',rows);print('PASS-six-independent-delivery-checks')
