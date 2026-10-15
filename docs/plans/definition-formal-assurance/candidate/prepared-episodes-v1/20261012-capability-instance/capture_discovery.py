from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent;argv=[sys.executable,'-B',str(p/'discover_consumers.py')]
r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True)
for key,data in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (p/('consumer-discovery-'+key+'.txt')).open('xb') as f:f.write(data)
with (p/'consumer-discovery-command-result.json').open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'consumer-discovery-stdout.txt','stderr':'consumer-discovery-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)

