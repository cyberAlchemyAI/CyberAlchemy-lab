from pathlib import Path
import subprocess,json,sys
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
N='/home/vlad_/projects/cyberAlchemy-v2/.runtime/craft-release-2026-10-29/node-v26.12.1-linux-x64/bin/node'
for index in range(17,24):
 print(json.dumps({'unit':index,'process':'fresh-bounded-heap','state':'starting'}),flush=True)
 with Path('/tmp/canonical-migration-verified.log').open('a') as log:
  result=subprocess.run([N,'--max-old-space-size=4096',str(P/'migrate.mjs'),str(index)],cwd=R,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
 print(json.dumps({'unit':index,'exit_code':result.returncode}),flush=True)
 if result.returncode:sys.exit(result.returncode)
