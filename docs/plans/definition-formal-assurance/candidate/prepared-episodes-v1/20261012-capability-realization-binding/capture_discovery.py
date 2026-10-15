from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent;argv=[sys.executable,'-B',str(p/'discover_consumers.py')];r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True)
for suffix,data in [('stdout.txt',r.stdout),('stderr.txt',r.stderr),('command-result.json',(json.dumps({'argv':argv,'exit_code':r.returncode,'stdout':'consumer-discovery-stdout.txt','stderr':'consumer-discovery-stderr.txt'},indent=2)+'\n').encode())]:
 with (p/('consumer-discovery-'+suffix)).open('xb') as f:f.write(data)
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);raise SystemExit(r.returncode)
