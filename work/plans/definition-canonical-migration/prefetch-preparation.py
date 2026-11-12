from pathlib import Path
import json,time,subprocess,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
ctx=json.loads((P/'NATIVE-CONTEXT.json').read_bytes());head=R/ctx['store']/'HEAD.json'
# Start only after unit eight commits; unit eight was already preparing when this helper was introduced.
for previous in range(8,23):
 while json.loads(head.read_bytes())['sequence']<previous+1:time.sleep(2)
 index=previous+1;b=P/'batches'/('unit-%02d'%index)
 if (b/'COMPLETED.json').exists():continue
 result=subprocess.run(['python3','-B',str(P/'prepare-batch.py'),str(index)],capture_output=True,text=True,timeout=900)
 print(json.dumps({'prepared':index,'returncode':result.returncode,'result':result.stdout,'diagnostic':result.stderr[-1000:]}),flush=True)
 if result.returncode:sys.exit(result.returncode)
