from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent;u=Path.cwd()/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D59'
argv=[sys.executable,'-B',str(u/'inspect_carrier_consumers.py'),'--write'];r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True)
for kind,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (p/('consumer-'+kind+'.txt')).open('xb') as f:f.write(raw)
with (p/'consumer-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'consumer-stdout.txt','stderr':'consumer-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
