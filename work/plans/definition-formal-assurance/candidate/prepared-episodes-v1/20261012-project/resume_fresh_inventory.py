"""Rerun only the actually interrupted unfinished sixth delivery check."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path.cwd();p=Path(__file__).resolve().parent
u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D60'
h=p/'retained-interrupted-full-replay-1'
interruption=json.loads((h/'interruption-observation.json').read_bytes())
assert interruption['actual_tool_capture_exit_code']==143 and interruption['actual_tool_controller_exit_code']==1
for pid in [452232,452233,455091,456751]:assert not(Path('/proc')/str(pid)/'cmdline').exists()
rows=[]
for name in ['contract','model','source','profile','dependency']:
 path=u/('fresh-'+name+'-command-result.json');row=json.loads(path.read_bytes())
 assert row['exit_code']==0 and not(u/row['stderr']).read_bytes()
 for file in [path,u/row['stdout'],u/row['stderr']]:assert file.read_bytes()==(h/file.name).read_bytes()
 if name!='contract':assert (u/row['stdout']).read_bytes()==(u/(name+'-stdout.txt')).read_bytes()
 rows.append(row)
typed=json.loads((u/'types-logic-receipt.json').read_bytes())
for ref in typed['inputs']+typed['checker_bindings']:
 assert hashlib.sha256((root/ref['path']).read_bytes()).hexdigest()==ref['sha256']
assert not(u/'fresh-inventory-command-result.json').exists() and not(u/'fresh-command-results.json').exists()
argv=[sys.executable,'-B',str(u/'verify_current_inventory.py')]
r=subprocess.run(argv,cwd=root,capture_output=True)
row={'check':'inventory','argv':argv,'exit_code':r.returncode,'stdout':'fresh-inventory-stdout.txt','stderr':'fresh-inventory-stderr.txt'}
for key,data in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (u/row[key]).open('xb') as f:f.write(data)
with (u/'fresh-inventory-command-result.json').open('x') as f:json.dump(row,f,indent=2);f.write('\n')
if r.returncode or r.stderr:raise SystemExit(r.returncode or 1)
assert r.stdout==(u/'inventory-stdout.txt').read_bytes(),'Resumed actual inventory output differs'
rows.append(row)
with (u/'fresh-command-results.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
print(json.dumps({'result':'PASS-six-independent-delivery-checks-with-retained-interruption','checks':[{'check':x['check'],'exit_code':x['exit_code']} for x in rows],'only_inventory_rerun':True}),flush=True)

