#!/usr/bin/env python3
"""Verify C08 consumer while keeping governed-view production explicitly open."""
import hashlib,io,json,platform,subprocess,sys,time,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
PACKAGE=Path(__file__).resolve().parent;ROOT=PACKAGE.parents[3]
if len(sys.argv)>1 and sys.argv[1]=='--worker':
 sys.path.insert(0,str(PACKAGE/'tests'));import test_session
 stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromTestCase(test_session.SessionTests)
 result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 Path(sys.argv[2]).write_text(json.dumps({'tests':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'packs':test_session.SessionTests.observed_packs},indent=2)+'\n')
 print(stream.getvalue(),flush=True);sys.exit(0 if result.wasSuccessful() else 1)
started=time.perf_counter()
with TemporaryDirectory(prefix='lab-context-evidence-') as temp:
 result_file=Path(temp)/'result.json'
 try:process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(result_file)],capture_output=True,text=True,timeout=180)
 except subprocess.TimeoutExpired:
  directory=PACKAGE/'receipts/C08';directory.mkdir(exist_ok=True);index=1
  while (directory/f'{index:04d}.failure.json').exists():index+=1
  (directory/f'{index:04d}.failure.json').write_text(json.dumps({'task':'C08','result':'FLAG','authority_effect':'none','task_complete':False,'error':'180 second verification budget exceeded'},indent=2)+'\n');raise
 data=json.loads(result_file.read_text()) if result_file.exists() else {'tests':0,'successful':False,'failures':0,'errors':1,'packs':[]}
 directory=PACKAGE/'receipts/C08';directory.mkdir(exist_ok=True);index=1
 while (directory/f'{index:04d}.json').exists():index+=1
 log=directory/f'{index:04d}.log';log.write_text(process.stdout+process.stderr)
 outputs=[]
 if data['successful']:
  folder=PACKAGE/f'examples/context/{index:04d}';folder.mkdir(parents=True)
  example=folder/'observed-fixture-context.json';example.write_text(json.dumps({'authority_effect':'none','fixture_only':True,'scope':'Actually observed isolated test context; no real Agent work episode, owner outcome or human pilot.','pack':data['packs'][0]},indent=2,sort_keys=True)+'\n');outputs.append(example)
 files=[Path(__file__).resolve(),PACKAGE/'lab_runtime/session.py',PACKAGE/'tests/test_session.py',PACKAGE/'design/context-reference-contract.md',PACKAGE/'design/legacy-runtime-bindings.json']+outputs+list((PACKAGE/'profiles').rglob('*.json'))
 r={'schema_version':'lab-context-consumer-check/v1-candidate','task':'C08','result':'PASS' if process.returncode==0 and data['successful'] and data['tests']==13 else 'FLAG','task_complete':False,'completion_scope':'Verified reference-aware ephemeral protocol context consumer; original governed-view production criterion remains open.','authority_effect':'none','tests':{k:data[k] for k in ['tests','failures','errors']},'duration_seconds':time.perf_counter()-started,'environment':{'python':sys.version,'platform':platform.platform()},'remaining_obligations':['Actual governed Context/Ontology View production and canonical ontology event/cut binding','Exact new generator-to-Implementation realization binding in the reviewed candidate package','Stronger API artifact references must not be satisfied with protocol-only views'],'log_binding':{'path':log.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()},'files':[{'path':f.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(files)],'real_operational_stores_provisioned':0,'repository_admissions_applied':0,'human_pilot_observations':0}
 path=directory/f'{index:04d}.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':r['result'],'task_complete':False,'tests':r['tests'],'duration_seconds':r['duration_seconds'],'receipt':path.relative_to(ROOT).as_posix()}),flush=True)
 sys.exit(0 if r['result']=='PASS' else 1)
