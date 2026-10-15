"""Retain the actual gated CI prepared semantic precheck terminal result."""
from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent
argv=[sys.executable,'-B',str(p/'check_after_Project_audit.py')]
r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True)
for key,data in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (p/('prepared-check-'+key+'.txt')).open('xb') as f:f.write(data)
with (p/'prepared-check-command-result.json').open('x') as f:
 json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'prepared-check-stdout.txt','stderr':'prepared-check-stderr.txt','actual_native_creation':False},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr)
raise SystemExit(r.returncode)

