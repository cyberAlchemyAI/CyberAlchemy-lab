from pathlib import Path
import subprocess,sys,json
p=Path(__file__).resolve().parent;u=Path.cwd()/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.projection-specification/next-unit-preparation';argv=[sys.executable,'-B',str(u/'inspect_source.py')];r=subprocess.run(argv,capture_output=True)
for suffix,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (u/('source-inspection-'+suffix+'.txt')).open('xb') as f:f.write(raw)
with (u/'source-inspection-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'source-inspection-stdout.txt','stderr':'source-inspection-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
