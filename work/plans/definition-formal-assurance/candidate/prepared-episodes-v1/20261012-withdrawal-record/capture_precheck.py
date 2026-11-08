"""Retain the actual prepared producer and terminal captures before native creation."""
from pathlib import Path
import subprocess,sys,json
p=Path(__file__).resolve().parent;argv=[sys.executable,'-B',str(p/'check_prepared.py')];r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True)
for k,raw in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (p/('prepared-check-'+k+'.txt')).open('xb') as f:f.write(raw)
with (p/'prepared-check-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'prepared-check-stdout.txt','stderr':'prepared-check-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
