from pathlib import Path
import subprocess,sys,json
root=Path.cwd();unit=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-type-resolution';argv=[sys.executable,'-B',str(unit/'inspect_carrier_consumers.py'),'--write'];r=subprocess.run(argv,cwd=root,capture_output=True)
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (unit/('carrier-inspection-'+k+'.txt')).open('xb') as f:f.write(raw)
with (unit/'carrier-inspection-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'carrier-inspection-stdout.txt','stderr':'carrier-inspection-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
