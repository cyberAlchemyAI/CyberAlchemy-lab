#!/usr/bin/env python3
"""Bounded actual C07 evidence; failed attempts stay immutable."""
import hashlib, io, json, platform, subprocess, sys, time, unittest
from pathlib import Path
from tempfile import TemporaryDirectory
PACKAGE=Path(__file__).resolve().parent;ROOT=PACKAGE.parents[3]
if len(sys.argv)>1 and sys.argv[1]=='--worker':
    sys.path.insert(0,str(PACKAGE/'tests'));import test_promotion
    stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromTestCase(test_promotion.PromotionTests)
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    Path(sys.argv[2]).write_text(json.dumps({'tests':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'observed':test_promotion.PromotionTests.observed},indent=2)+'\n')
    print(stream.getvalue(),flush=True);sys.exit(0 if result.wasSuccessful() else 1)
started=time.perf_counter();directory=PACKAGE/'receipts/C07';directory.mkdir(parents=True,exist_ok=True);index=1
while (directory/f'{index:04d}.json').exists():index+=1
with TemporaryDirectory(prefix='lab-publisher-check-output-') as temp:
    output=Path(temp)/'result.json';error=None
    try:
        process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(output)],capture_output=True,text=True,timeout=480)
        stdout,stderr,returncode=process.stdout,process.stderr,process.returncode
    except subprocess.TimeoutExpired as exc:
        stdout=(exc.stdout or b'').decode() if isinstance(exc.stdout,bytes) else exc.stdout or ''
        stderr=(exc.stderr or b'').decode() if isinstance(exc.stderr,bytes) else exc.stderr or ''
        returncode=124;error='480 second verification budget exceeded'
    data=json.loads(output.read_text()) if output.exists() else {'tests':0,'successful':False,'failures':0,'errors':1,'observed':None}
    log=directory/f'{index:04d}.log';log.write_text(stdout+stderr);observation=None
    if data['successful'] and data['observed']:
        folder=PACKAGE/f'examples/promotion/{index:04d}';folder.mkdir(parents=True)
        observation=folder/'observed-isolated-publication.json';observation.write_text(json.dumps(data['observed'],indent=2,sort_keys=True)+'\n')
    files=[Path(__file__).resolve(),PACKAGE/'tests/test_promotion.py',PACKAGE/'tests/test_transition.py',PACKAGE/'schemas/promotion.schema.json',PACKAGE/'design/promotion-contract.md',PACKAGE/'design/contract-impact.json',PACKAGE/'design/legacy-runtime-bindings.json',ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-C07-v2.json',log]
    files+=list((PACKAGE/'lab_runtime').rglob('*.py'))+list((PACKAGE/'profiles').rglob('*.json'))
    files+=list((ROOT/'implementation/lab-runtime/v1/lab_runtime').glob('*.py'))+[ROOT/'implementation/lab-runtime/v1/profile.json']
    if observation:files.append(observation)
    passed=returncode==0 and data['successful'] and data['tests']==20 and data['observed'] is not None
    receipt={'schema_version':'lab-repository-publisher-check/v1-candidate','task':'C07','result':'PASS' if passed else 'FLAG','task_complete':passed,'authority_effect':'none','tests':{k:data[k] for k in ['tests','failures','errors']},'duration_seconds':time.perf_counter()-started,'error':error,'returncode':returncode,'environment':{'python':sys.version,'platform':platform.platform()},'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(files)) if '__pycache__' not in p.parts],'scope':'Selected signed local Work/Definition and coeval ArtifactType/schema/instance exports; separate repository owner key; actual carrier consequences, atomic immutable commit, fresh-process verification and managed mirror recovery in isolated repository copies. No actual R08 human outcome or canonical repository admission.','actual_owner_outcome':None,'real_repository_admissions_applied':0,'runtime_activations':0,'external_effects':0}
    path=directory/f'{index:04d}.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:receipt[k] for k in ['result','task_complete','tests','duration_seconds','error']}));print(path.relative_to(ROOT).as_posix())
    sys.exit(0 if passed else 1)
