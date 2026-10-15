#!/usr/bin/env python3
"""Bounded C08 evidence, retaining failed attempts and exact source bindings."""
import argparse,hashlib,io,json,os,platform,signal,subprocess,sys,time,unittest
from pathlib import Path
from tempfile import TemporaryDirectory

PACKAGE=Path(__file__).resolve().parent;ROOT=PACKAGE.parents[3]

if len(sys.argv)>1 and sys.argv[1]=='--worker':
    sys.path.insert(0,str(PACKAGE/'tests'));import test_context
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(test_context.ContextTests),unittest.defaultTestLoader.loadTestsFromTestCase(test_context.SessionTests)])
    stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    Path(sys.argv[2]).write_text(json.dumps({'tests':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'packs':test_context.ContextTests.observed},indent=2)+'\n')
    print(stream.getvalue(),flush=True);sys.exit(0 if result.wasSuccessful() else 1)

parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('native_executable');parser.add_argument('manifest');args=parser.parse_args()
env=os.environ.copy();env['LAB_C08_NATIVE_EXECUTABLE']=str(Path(args.native_executable).resolve());env['LAB_C08_GENERATOR_MANIFEST']=str(Path(args.manifest).resolve().relative_to(ROOT))
directory=PACKAGE/'receipts/C08';directory.mkdir(parents=True,exist_ok=True);index=1
while (directory/f'{index:04d}.json').exists() or (directory/f'{index:04d}.failure.json').exists():index+=1
started=time.perf_counter();timeout=False
with TemporaryDirectory(prefix='lab-c08-controller-') as temp:
    result_file=Path(temp)/'result.json'
    process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(result_file)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env,start_new_session=True)
    try:stdout,stderr=process.communicate(timeout=480)
    except subprocess.TimeoutExpired:
        timeout=True;os.killpg(process.pid,signal.SIGKILL);stdout,stderr=process.communicate()
    data=json.loads(result_file.read_text()) if result_file.exists() else {'tests':0,'successful':False,'failures':0,'errors':1,'packs':[]}
    passed=not timeout and process.returncode==0 and data['successful'] and data['tests']==36
    log=directory/f'{index:04d}.log';log.write_text(stdout+stderr)
    outputs=[]
    if passed:
        folder=PACKAGE/f'examples/{index:04d}';folder.mkdir(parents=True)
        output=folder/'observed-context.json';output.write_text(json.dumps({'authority_effect':'none','fixture_only':True,'human_outcome':None,'scope':'Observed candidate carrier production from an isolated signed Project store and real native event replay; fixed fixture clock, no real Agent work episode or domain ontology mapping.','pack':data['packs'][0]},indent=2,sort_keys=True)+'\n');outputs.append(output)
        for kind,record in data['packs'][0]['candidate_artifacts'].items():
            output=folder/(kind+'.json');output.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');outputs.append(output)
    manifest=Path(args.manifest).resolve();m=json.loads(manifest.read_text())
    files=[Path(__file__).resolve(),PACKAGE/'build_package.py',PACKAGE/'cold_probe.py',PACKAGE/'tests/native_fixture.py',PACKAGE/'tests/test_context.py',PACKAGE/'README.md',manifest,manifest.parent/'selection.json',*[ROOT/m[k]['path'] for k in ['implementation_record','realization_record']],ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-C08-v2.json',ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/CONTEXT-C08-v2.md']+outputs+[ROOT/r['path'] for r in m['files']]+list((ROOT/'implementation/lab-runtime/candidates/repeatable-operation/profiles').rglob('*.json'))
    receipt={'schema_version':'lab-exact-context-check/v1-candidate','task':'C08','result':'PASS' if passed else 'FLAG','task_complete':passed,'authority_effect':'none','duration_seconds':time.perf_counter()-started,'tests':{k:data[k] for k in ['tests','failures','errors']},'timeout_seconds':480,'timed_out':timeout,'completion_scope':'Candidate reference-aware Context/Ontology carrier production, actual supported native-event read, exact generator realization and ephemeral closure. C09 API integration and O02/O03 domain mappings/admission remain separate.','log_binding':{'path':log.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()},'source_bindings':m['files'],'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))],'native_executable_sha256':m['native_executable_sha256'],'environment':{'python':sys.version,'platform':platform.platform()},'real_operational_stores_provisioned':0,'repository_admissions_applied':0,'human_pilot_observations':0,'remaining_obligations':[] if passed else ['All C08 acceptance checks must pass; failed evidence supplies no completion.'],'claim_ceiling':'Candidate conformance only; no owner admission, activation, arbitrary ontology profile support or operational readiness.'}
    path=directory/(f'{index:04d}.json' if passed else f'{index:04d}.failure.json');path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':receipt['result'],'task_complete':passed,'tests':receipt['tests'],'duration_seconds':receipt['duration_seconds'],'receipt':path.relative_to(ROOT).as_posix()}),flush=True)
    if not passed:print((stdout+stderr)[-10000:],flush=True)
    sys.exit(0 if passed else 1)
