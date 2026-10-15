from pathlib import Path
import sys,subprocess,json
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.principal-reference';argv=[sys.executable,'-B',str(u/'inspect_carrier_consumers.py')]+(['--write'] if '--write' in sys.argv else []);r=subprocess.run(argv,cwd=root,capture_output=True);stem='carrier-inspection' if '--write' in sys.argv else 'fresh-carrier-inspection'
for key,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (u/(stem+'-'+key+'.txt')).open('xb') as f:f.write(raw)
with (u/(stem+'-command-result.json')).open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
