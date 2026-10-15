#!/usr/bin/env python3
"""Bounded S01 bootstrap evidence, with immutable failed-attempt receipts."""
import hashlib,io,json,os,platform,signal,subprocess,sys,time,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
PACKAGE=Path(__file__).resolve().parent;ROOT=PACKAGE.parents[3]
if len(sys.argv)>1 and sys.argv[1]=='--worker':
    sys.path.insert(0,str(PACKAGE/'tests'));import test_bootstrap
    stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromTestCase(test_bootstrap.BootstrapTests)
    class ProgressResult(unittest.TextTestResult):
        def stopTest(self,test):
            super().stopTest(test)
            Path(sys.argv[2]+'.progress').write_text(json.dumps({'tests':self.testsRun,'successful':False,'failures':len(self.failures),'errors':len(self.errors),'observed':test_bootstrap.BootstrapTests.observed,'last_test':test.id()})+'\n')
    result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=ProgressResult).run(suite)
    Path(sys.argv[2]).write_text(json.dumps({'tests':result.testsRun,'successful':result.wasSuccessful(),
        'failures':len(result.failures),'errors':len(result.errors),'observed':test_bootstrap.BootstrapTests.observed},indent=2)+'\n')
    print(stream.getvalue(),flush=True);sys.exit(0 if result.wasSuccessful() else 1)
started=time.perf_counter();folder=PACKAGE/'receipts/S01';folder.mkdir(parents=True,exist_ok=True);index=1
while (folder/f'{index:04d}.json').exists():index+=1
with TemporaryDirectory(prefix='lab-bootstrap-check-output-') as temp:
    output=Path(temp)/'result.json';error=None
    fixtures=Path(temp)/'fixtures';fixtures.mkdir()
    worker=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(output)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
        start_new_session=True,env={**os.environ,'S01_FIXTURE_ROOT':str(fixtures)})
    try:
        stdout,stderr=worker.communicate(timeout=360);code=worker.returncode
    except subprocess.TimeoutExpired as exc:
        os.killpg(worker.pid,signal.SIGKILL);stdout,stderr=worker.communicate()
        code=124;error='360 second verification budget exceeded'
    progress=Path(str(output)+'.progress')
    data=json.loads(output.read_text()) if output.exists() else json.loads(progress.read_text()) if progress.exists() else {'tests':0,'successful':False,'failures':0,'errors':1,'observed':None}
    log=folder/f'{index:04d}.log';log.write_text(stdout+stderr)
    packages=sorted((PACKAGE/'packages').glob('[0-9][0-9][0-9][0-9]'));stage=packages[-1] if packages else None
    package_error=None
    try:
        from bootstrap import compose,load,select,package_materials,file_bytes,byte_digest
        assert stage is not None,'no exact staged package'
        manifest=load(stage/'PACKAGE-MANIFEST.json')
        assert {r['path'] for r in manifest['file_bindings']}=={p.relative_to(ROOT).as_posix() for p in stage.rglob('*') if p.is_file() and p.name!='PACKAGE-MANIFEST.json'},'staged file closure changed'
        for r in manifest['file_bindings']:assert byte_digest(file_bytes(ROOT/r['path']))==r['sha256'],r['path']
        selection=select(ROOT,**load(stage/'selection.json'));_,catalog=package_materials(ROOT,selection)
        assert catalog['digest']==manifest['catalog_digest'],'staged catalog mismatch'
    except Exception as exc:package_error=str(exc)
    observation=None
    if data['successful'] and data['observed']:
        path=PACKAGE/f'examples/{index:04d}';path.mkdir(parents=True)
        observation=path/'observed-isolated-bootstrap.json';observation.write_text(json.dumps(data['observed'],indent=2,sort_keys=True)+'\n')
    files=[Path(__file__).resolve(),PACKAGE/'bootstrap.py',PACKAGE/'generator.py',PACKAGE/'build_package.py',PACKAGE/'README.md',
        PACKAGE/'tests/test_bootstrap.py',log,ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-S01.json']
    if stage:files += [p for p in stage.rglob('*') if p.is_file()]
    if observation:files.append(observation)
    runtime=ROOT/'implementation/lab-runtime/candidates/repeatable-operation'
    files += [p for p in (runtime/'lab_runtime').rglob('*.py') if '__pycache__' not in p.parts] + [runtime/'lab.py']
    files += list((runtime/'profiles').rglob('*.json'))
    passed=code==0 and data['successful'] and data['tests']==20 and package_error is None and data['observed'] and data['observed'].get('profile_transition',{}).get('observed') is True
    context=json.loads((ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-S01.json').read_text())
    receipt={'schema_version':'lab-candidate-bootstrap-check/v1','task':'S01','result':'PASS' if passed else 'FLAG','task_complete':bool(passed),
        'authority_effect':'none','tests':{k:data[k] for k in ['tests','failures','errors']},'duration_seconds':time.perf_counter()-started,
        'returncode':code,'error':error,'staged_package_error':package_error,'environment':{'python':sys.version,'platform':platform.platform()},
        'staged_package':stage.relative_to(ROOT).as_posix() if stage else None,
        'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files))],
        'source_bindings':context['source_bindings'],'scope':'Exact D75-derived catalog, complete candidate Method type and generator realization, explicit Project/Product mappings, independent native profiles, isolated signed bootstrap/cold replay and fresh-key profile transition. No actual semantic or implementation admission.',
        'actual_owner_outcome':None,'canonical_registry_mutations':0,'canonical_project_state_mutations':0,'runtime_activations':0,'external_effects':0}
    path=folder/f'{index:04d}.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:receipt[k] for k in ['result','task_complete','tests','duration_seconds','error','staged_package_error']}));print(path.relative_to(ROOT).as_posix())
    sys.exit(0 if passed else 1)
