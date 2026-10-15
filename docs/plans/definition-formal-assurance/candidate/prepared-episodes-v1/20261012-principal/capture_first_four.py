from pathlib import Path
import json,sys,subprocess
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.principal';argv=[sys.executable,'-B',str(u/'replay_first_four.py')];r=subprocess.run(argv,cwd=root,capture_output=True)
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (p/('fresh-first-four-'+k+'.txt')).open('xb') as f:f.write(raw)
with (p/'fresh-first-four-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'fresh-first-four-stdout.txt','stderr':'fresh-first-four-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
