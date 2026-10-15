from pathlib import Path
import json,sys,subprocess
p=Path(__file__).resolve().parent;argv=[sys.executable,'-B',str(p/'check_assembled_prepared.py')]
r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True)
for key,data in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (p/('assembled-check-'+key+'.txt')).open('xb') as f:f.write(data)
with (p/'assembled-check-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'assembled-check-stdout.txt','stderr':'assembled-check-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)

