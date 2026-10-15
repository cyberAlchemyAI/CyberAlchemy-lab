#!/usr/bin/env python3
"""Run isolated full-verifier parity checks and preserve their actual evidence."""
import hashlib,io,json,platform,subprocess,sys,time,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
PACKAGE=Path(__file__).resolve().parent;ROOT=PACKAGE.parents[3]
if len(sys.argv)>1 and sys.argv[1]=='--worker':
 sys.path.insert(0,str(PACKAGE/'tests'))
 import test_replay
 output=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromTestCase(test_replay.ReplayTests)
 result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
 value={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'successful':result.wasSuccessful(),'timings':test_replay.ReplayTests.performance,'log':output.getvalue()}
 Path(sys.argv[2]).write_text(json.dumps(value,indent=2)+'\n');print(output.getvalue(),flush=True)
 sys.exit(0 if result.wasSuccessful() else 1)
started=time.perf_counter()
with TemporaryDirectory(prefix='lab-replay-check-output-') as temp:
 out=Path(temp)/'result.json'
 try:process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(out)],capture_output=True,text=True,timeout=180)
 except subprocess.TimeoutExpired as exc:
  directory=PACKAGE/'receipts/C06';directory.mkdir(exist_ok=True)
  index=1
  while (directory/f'{index:04d}.failure.json').exists():index+=1
  failure={'task':'C06','result':'FLAG','authority_effect':'none','error':'180 second verification budget exceeded','duration_seconds':time.perf_counter()-started,'task_complete':False}
  (directory/f'{index:04d}.failure.json').write_text(json.dumps(failure,indent=2)+'\n');raise
 data=json.loads(out.read_text()) if out.exists() else {'successful':False,'tests':0,'failures':0,'errors':1,'timings':[]}
 directory=PACKAGE/'receipts/C06';directory.mkdir(exist_ok=True)
 index=1
 while (directory/f'{index:04d}.json').exists():index+=1
 log=directory/f'{index:04d}.log';log.write_text(process.stdout+process.stderr)
 files=[Path(__file__).resolve(),PACKAGE/'tests/test_replay.py',PACKAGE/'design/legacy-runtime-bindings.json',PACKAGE/'design/replay-reuse-decision.md',PACKAGE/'receipts/C03-acceptance-0001.json']+list((PACKAGE/'lab_runtime').glob('*.py'))+list((ROOT/'implementation/lab-runtime/v2/lab_runtime').glob('*.py'))
 receipt={'schema_version':'lab-replay-parity-check/v1-candidate','task':'C06','result':'PASS' if process.returncode==0 and data['successful'] and data['tests']==14 else 'FLAG','authority_effect':'none','selected_acceleration':'measured-no-op','cache_enabled':False,'persistent_checkpoint_trust':False,'duration_seconds':time.perf_counter()-started,'tests':{k:data[k] for k in ['tests','failures','errors']},'timings':data['timings'],'environment':{'python':sys.version,'platform':platform.platform()},'log_binding':{'path':log.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()},'files':[{'path':f.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(set(files))],'scope':'Exact legacy v2 full-replay read bridge with independent pins; one actual isolated signed fixture transaction, mutation checks and fresh-process parity. No accelerated path or new general store writer is claimed.','real_operational_stores_provisioned':0,'repository_admissions_applied':0,'actual_owner_outcome':None}
 path=directory/f'{index:04d}.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 if receipt['result']=='PASS' and not (PACKAGE/'receipts/replay-parity.json').exists():(PACKAGE/'receipts/replay-parity.json').write_bytes(path.read_bytes())
 print(json.dumps({'result':receipt['result'],'tests':receipt['tests'],'duration_seconds':receipt['duration_seconds'],'timings':receipt['timings'],'receipt':path.relative_to(ROOT).as_posix()}),flush=True)
 sys.exit(0 if receipt['result']=='PASS' else 1)
