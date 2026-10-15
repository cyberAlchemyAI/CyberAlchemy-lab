"""Capture the actual resume process; original interrupted capture is retained."""
from pathlib import Path
import sys,json,subprocess
p=Path(__file__).resolve().parent
argv=[sys.executable,'-B',str(p/'resume_fresh_inventory.py')]
r=subprocess.run(argv,cwd=Path.cwd(),capture_output=True)
for key,data in [('stdout',r.stdout),('stderr',r.stderr)]:
 with (p/('fresh-delivery-'+key+'.txt')).open('xb') as f:f.write(data)
with (p/'fresh-delivery-command-result.json').open('x') as f:
 json.dump({'argv':argv,'exit_code':r.returncode,'stdout':'fresh-delivery-stdout.txt','stderr':'fresh-delivery-stderr.txt','recovery_of_actual_interrupted_outer_capture':True,'only_unfinished_inventory_reexecuted':True,'retained_original_capture':'retained-interrupted-full-replay-1/interruption-observation.json'},f,indent=2);f.write('\n')
print(r.stdout.decode(),end='');print(r.stderr.decode(),end='',file=sys.stderr)
raise SystemExit(r.returncode)

