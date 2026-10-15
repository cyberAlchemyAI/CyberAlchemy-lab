"""Three separate read-only processes; retain exact terminal output and exit code."""
from pathlib import Path
import json,subprocess,sys,os
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D20';impl=root/'craft/formalization/candidates/definition-assurance-v1'
jobs=[('contract',[sys.executable,'-B',str(impl/'contracts.py'),'validate','--kind','interpretation','--input',str(u/'t.json')]),('model',[sys.executable,'-B',str(u/'verify_candidate.py')]),('source',[sys.executable,'-B',str(u/'verify_source_checks.py')])];rows=[]
for name,argv in jobs:
 r=subprocess.run(argv,cwd=root,capture_output=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));row={'check':name,'argv':argv,'exit_code':r.returncode,'stdout':'fresh-types-'+name+'-stdout.txt','stderr':'fresh-types-'+name+'-stderr.txt'}
 for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
  with (u/row[k]).open('xb') as f:f.write(raw)
 with (p/('fresh-types-'+name+'-command-result.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
 rows.append(row);print(json.dumps({'check':name,'exit_code':r.returncode}),flush=True)
 if r.returncode or r.stderr:raise SystemExit(r.returncode or 1)
 if name!='contract':assert r.stdout==(u/(name+'-stdout.txt')).read_bytes(),name
with (u/'fresh-types-logic-results.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
print('PASS-three-independent-fresh-types-logic-checks')
