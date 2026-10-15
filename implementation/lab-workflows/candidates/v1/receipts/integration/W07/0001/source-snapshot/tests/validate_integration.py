#!/usr/bin/env python3
"""Freeze combined family, run fresh scenarios, retain actual integration failures."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import os
import subprocess
import sys
import time
import traceback
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from integration_support import *
from integration_worker import recording_type
from kind_probe import probe

HERE=Path(__file__).resolve().parent
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def worker(mode,domain,destination,native,logs):
    start=time.perf_counter()
    argv=[sys.executable,str(HERE/'integration_worker.py'),mode,domain,str(destination),str(native)]
    if mode=='--cold':argv=[sys.executable,str(HERE/'integration_worker.py'),mode,str(destination),domain,str(native)]
    try:
        p=subprocess.run(argv,capture_output=True,timeout=900)
        stdout,stderr=p.stdout,p.stderr;code=p.returncode;error=None
    except subprocess.TimeoutExpired as exc:
        stdout,stderr=exc.stdout or b'',exc.stderr or b'';code=None;error='bounded worker timeout; no automatic restart'
    stem=mode.removeprefix('--')+'-'+(domain if mode!='--cold' else 'join')
    (logs/(stem+'.stdout')).write_bytes(stdout);(logs/(stem+'.stderr')).write_bytes(stderr)
    value=parse(stdout) if code==0 else None
    print(encoded({'stage':mode,'domain':domain if mode!='--cold' else 'all','returncode':code,
        'result':value.get('result') if value else 'FLAG','duration_seconds':time.perf_counter()-start}).decode().strip(),flush=True)
    return {'result':'PASS' if code==0 and value and value['result']=='PASS' else 'FLAG','returncode':code,
        'value':value,'error':error,'stdout':binding(logs/(stem+'.stdout')),'stderr':binding(logs/(stem+'.stderr'))}


def main():
    start=time.perf_counter();native=Path(sys.argv[1]).resolve()
    native_manifest=ROOT/'implementation/lab-continuity/candidates/v1/packages/0001/generator-manifest.json'
    native_sha=parse(native_manifest.read_bytes())['native_executable_sha256']
    require(byte_sha(native.read_bytes())==native_sha,'independent native executable pin differs')
    os.environ['W02_NATIVE_EXECUTABLE']=str(native)
    context=parse((RUN/'context-W07.json').read_bytes());sources=verify_upstream()+context['source_bindings']
    own=list(HERE.glob('*.py'))+[PACKAGE/'REVIEW.md',RUN/'context-W07.json',RUN/'CONTEXT-W07.md',native_manifest]
    sources += [binding(p) for p in own]
    unique={}
    for r in sources:
        key=r['path'];require(key not in unique or unique[key]['sha256']==r['sha256'],'combined source binding conflict')
        unique[key]={'path':key,'sha256':r['sha256']};bound(unique[key])
    files=list(unique.values())
    receipts=PACKAGE/'receipts/integration/W07';receipts.mkdir(parents=True,exist_ok=True);number=1
    while (receipts/f'{number:04d}').exists() or (receipts/f'{number:04d}.json').exists():number+=1
    output=receipts/f'{number:04d}';output.mkdir();logs=output/'process-logs';logs.mkdir()
    (output/'manifest.json').write_bytes(encoded({'authority_effect':'none','files':files}))
    print(encoded({'stage':'sources-frozen','files':len(files),'output':output.relative_to(ROOT).as_posix()}).decode().strip(),flush=True)
    import test_integration
    with (output/'integration-guards.log').open('w') as stream:
        guards=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=recording_type()).run(unittest.defaultTestLoader.loadTestsFromModule(test_integration))
    unit_results={}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures={executor.submit(worker,'--unit',d,output/('units-'+d),native,logs):d for d in ['engineering','research','failure','learning','replay']}
        for f in as_completed(futures):unit_results[futures[f]]=f.result()
    scenarios=output/'scenarios';scenarios.mkdir()
    domain_results={}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures={executor.submit(worker,'--episode',d,scenarios/d,native,logs):d for d in sorted(DOMAINS)}
        for f in as_completed(futures):domain_results[futures[f]]=f.result()
    cases=[];join=None;kind_result=None;cold=None;error=None
    try:
        require(all(r['result']=='PASS' for r in domain_results.values()),'fresh representative scenario incomplete; retain errors without restart')
        cases=[parse(bound(domain_results[d]['value']['case'])) for d in sorted(DOMAINS)]
        join=audit_join(cases);emit(output/'joined-audit.json',join)
        inventory=endpoint_inventory_audit();emit(output/'endpoint-inventory.json',inventory)
        kind_result=probe(cases);emit(output/'actual-kind-rejections.json',kind_result)
        index={'schema_version':'lab-W07-frozen-case-join/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
            'cases':[domain_results[d]['value']['case'] for d in sorted(DOMAINS)],'model_kind_closure':join['result'],'effect_authority':'none'}
        path=output/'join-index.json';emit(path,index)
        cold=worker('--cold',byte_sha(path.read_bytes()),path,native,logs)
    except Exception:
        error=traceback.format_exc();(output/'integration-error.log').write_text(error)
    drift=[r['path'] for r in files if byte_sha((ROOT/r['path']).read_bytes())!=r['sha256']]
    expected={'engineering':33,'research':41,'failure':52,'learning':53,'replay':14}
    units_ok=all(unit_results[d]['result']=='PASS' and unit_results[d]['value']['tests']==count for d,count in expected.items())
    regression=parse((scenarios/'engineering-default-regression.json').read_bytes()) if (scenarios/'engineering-default-regression.json').exists() else None
    evidence_pass=guards.wasSuccessful() and guards.testsRun==28 and units_ok and regression is not None and regression['result']=='PASS' and regression['tests']==42
    evidence_pass=evidence_pass and join is not None and join['evidence_coverage']=='PASS' and kind_result is not None and kind_result['result']=='PASS'
    evidence_pass=evidence_pass and cold is not None and cold['result']=='PASS' and not drift and byte_sha(native.read_bytes())==native_sha
    task_complete=bool(evidence_pass and join['result']=='PASS')
    checks=guards.checks+[c for result in unit_results.values() if result['value'] for c in result['value']['checks']]
    if regression:checks+=regression['checks']
    remaining=[] if task_complete else [
        'Implement and verify the already declared Project/Product represented-subject mappings and exact signed-runtime coupling; helper normalization cannot supply it.',
        'Bind current raw carrier kinds, represented endpoint kinds and actual source eligibility under exact proposed mappings without collapsing them.',
        'Stage necessary mapping/code/contract effects for O02/O05/R03 and W08/S02/R08; rerun complete W07 coupling proof before task closure.']
    receipt={'schema_version':'lab-W07-integrated-workflow-evidence/v1-candidate','task':'W07','authority_effect':'none',
        'result':'PASS' if evidence_pass else 'FLAG','task_complete':task_complete,'model_integration_result':join['result'] if join else 'not-observed',
        'tests':len(checks),'checks':checks,'duration_seconds':time.perf_counter()-start,'source_drift':drift,
        'files':files+[binding(p) for p in output.rglob('*') if p.is_file()],'source_bindings':context['source_bindings'],
        'unit_results':unit_results,'domain_results':domain_results,'cold_verification':cold,
        'kind_rejection_probe':kind_result,'integration_error':error,'remaining_obligations':remaining,
        'actual_owner_outcome':None,'canonical_effects_applied':0,'global_merge_performed':False,
        'native_executable_binding':{'path':str(native),'sha256':native_sha},
        'claim_ceiling':'Complete candidate evidence production only if PASS. Actual exact signed-runtime kind integration remains unproven/failed where flagged; W07 is not complete until repaired. Actual representative procedures and read-only rejection probes do not admit mappings, instances, workflows, Method, aliases or Product benefits.'}
    path=receipts/f'{number:04d}.json';emit(path,receipt)
    print(encoded({'result':receipt['result'],'task_complete':task_complete,'model_integration_result':receipt['model_integration_result'],
        'tests':len(checks),'receipt':path.relative_to(ROOT).as_posix()}).decode().strip(),flush=True)
    return 0 if evidence_pass else 1


if __name__=='__main__':sys.exit(main())
