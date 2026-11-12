from pathlib import Path
import time,subprocess,json,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
N='/home/vlad_/projects/cyberAlchemy-v2/.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node'
while not (P/'batches/unit-23/COMPLETED.json').exists():time.sleep(2)
steps=[
 ('canonical-layout',[N,str(P/'finalize-layout.mjs')]),
 ('full-catalog',['python3','-B',str(P/'verify-final-catalog.py')]),
 ('default-discovery',[N,str(P/'verify-discovery.mjs')]),
 ('final-data-recovery',[N,str(P/'finalize-operational.mjs')]),
 ('hardening-and-restoration',[N,str(R/'implementation/lab-runtime/alchlang/shared-records/verify-hardening.mjs')]),
 ('final-readiness',[N,str(P/'verify-completion.mjs')])
]
for name,command in steps:
 log=Path('/tmp/canonical-final-'+name+'.log')
 print(json.dumps({'step':name,'state':'running','log':str(log)}),flush=True)
 with log.open('w') as out:result=subprocess.run(command,cwd=R,stdout=out,stderr=subprocess.STDOUT,timeout=5400)
 print(json.dumps({'step':name,'exit_code':result.returncode}),flush=True)
 if result.returncode:
  print(log.read_text()[-2500:],flush=True);sys.exit(result.returncode)
print(json.dumps({'status':'PASS','verification':str(P/'VERIFICATION.json')}),flush=True)
