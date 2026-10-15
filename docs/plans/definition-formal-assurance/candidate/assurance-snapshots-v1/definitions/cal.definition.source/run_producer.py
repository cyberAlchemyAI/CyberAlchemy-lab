"""Capture a producer's actual terminal result and exact stdout/stderr without replacing prior attempts."""
from pathlib import Path
import subprocess,sys,json
u=Path(__file__).resolve().parent;scripts={'profile':'verify_authority_profile.py','dependency':'verify_dependencies.py','inventory':'verify_current_inventory.py'};stem=sys.argv[1];argv=[sys.executable,str(u/scripts[stem]),'--write'];r=subprocess.run(argv,capture_output=True)
for suffix,data in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (u/(stem+'-'+suffix+'.txt')).open('xb') as f:f.write(data)
with (u/(stem+'-command-result.json')).open('x') as f:json.dump({'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr);print(json.dumps({'producer':stem,'exit_code':r.returncode}));raise SystemExit(r.returncode)
