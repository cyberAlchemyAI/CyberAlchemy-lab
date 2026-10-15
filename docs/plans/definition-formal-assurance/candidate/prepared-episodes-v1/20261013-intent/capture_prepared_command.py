"""Capture a preparation/closeout command after its actual process termination."""
from pathlib import Path
import json,subprocess,sys
p=Path(__file__).resolve().parent;stem,script=sys.argv[1:3]
assert '/' not in stem and '/' not in script and script.endswith('.py')
argv=[sys.executable,'-B',str(p/script)]+sys.argv[3:]
r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True)
row={'check':stem,'argv':argv,'exit_code':r.returncode,'stdout':stem+'-stdout.txt','stderr':stem+'-stderr.txt'}
for key,value in [('stdout',r.stdout),('stderr',r.stderr)]:
    with(p/row[key]).open('xb') as f:f.write(value)
with(p/(stem+'-command-result.json')).open('x') as f:json.dump(row,f,indent=2);f.write('\n')
print(r.stdout.decode(),end='',flush=True);print(r.stderr.decode(),end='',file=sys.stderr,flush=True)
raise SystemExit(r.returncode or bool(r.stderr))
