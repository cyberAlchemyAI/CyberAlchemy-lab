#!/usr/bin/env python3
"""Observe completed W07 cases after parent framing failure; no effect redispatch."""
from pathlib import Path
import sys
import time
import traceback

sys.path.insert(0,str(Path(__file__).resolve().parent))
from integration_support import *
from validate_integration import worker_output,worker
from kind_probe import probe


def main(source,native):
    started=time.perf_counter();source=Path(source).resolve();native=Path(native).resolve()
    require(source.parent==PACKAGE/'receipts/integration/W07' and source.name=='0001','only selected completed source attempt supported')
    original=parse((source/'manifest.json').read_bytes());archived=parse((source/'source-snapshot/manifest.json').read_bytes())
    replacements={r['original_path']:r for r in archived['files']}
    bindings=[]
    for r in original['files']:
        if r['path'] in replacements:
            saved=replacements[r['path']];require(saved['sha256']==r['sha256'],'archived execution source differs')
            binding_row={'path':saved['archive_path'],'sha256':saved['sha256']}
        else:binding_row={'path':r['path'],'sha256':r['sha256']}
        bound(binding_row);bindings.append(binding_row)
    # All retained original output/source bytes are pinned before analysis.
    bindings += [binding(p) for p in source.rglob('*') if p.is_file()]
    # Retain failed observational predecessors without selecting their stale code.
    for attempt in source.parent.iterdir():
        if attempt.is_dir() and attempt.name.isdigit() and attempt.name!='0001':
            bindings += [binding(p) for p in attempt.rglob('*') if p.is_file()]
    own=list((PACKAGE/'tests').glob('*.py'))+[PACKAGE/'REVIEW.md']
    bindings += [binding(p) for p in own]
    unique={r['path']:r for r in bindings};bindings=list(unique.values())
    number=max([int(p.stem) for p in source.parent.iterdir() if p.stem.isdigit()]+[1])+1
    output=source.parent/f'{number:04d}';require(not output.exists() and not output.with_suffix('.json').exists(),'new observation receipt required')
    output.mkdir();logs=output/'process-logs';logs.mkdir()
    emit(output/'manifest.json',{'authority_effect':'none','files':bindings,'effect_reexecution_allowed':False})
    unit_results={}
    expected={'engineering':33,'research':41,'failure':52,'learning':53,'replay':14}
    for domain,count in expected.items():
        value=worker_output((source/'process-logs'/('unit-'+domain+'.stdout')).read_bytes(),'--unit',domain)
        retained=parse((source/('units-'+domain)/'result.json').read_bytes())
        require(value['result']=='PASS' and value['tests']==count and value['checks']==retained['checks'],'original unit result incomplete')
        unit_results[domain]=value
    regression=parse((source/'scenarios/engineering-default-regression.json').read_bytes())
    require(regression['result']=='PASS' and regression['tests']==42,'original default regression incomplete')
    cases=[];domain_results={}
    for domain in sorted(DOMAINS):
        raw=(source/'process-logs'/('episode-'+domain+'.stdout')).read_bytes()
        value=worker_output(raw,'--episode',domain,regression if domain=='engineering' else None)
        require(value['result']=='PASS','original completed domain case absent')
        cases.append(parse(bound(value['case'])));domain_results[domain]=value
    join=audit_join(cases);emit(output/'joined-audit.json',join)
    emit(output/'endpoint-inventory.json',endpoint_inventory_audit())
    actual=probe(cases);emit(output/'actual-kind-rejections.json',actual)
    index={'schema_version':'lab-W07-frozen-case-join/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
        'cases':[domain_results[d]['case'] for d in sorted(DOMAINS)],'model_kind_closure':join['result'],
        'effect_authority':'none','original_cases_reexecuted':0}
    path=output/'join-index.json';emit(path,index)
    cold=worker('--cold',byte_sha(path.read_bytes()),path,native,logs)
    # Fresh isolated joining guards verify the repaired parser and exact analysis.
    import unittest
    import test_integration
    from integration_worker import recording_type
    with (output/'integration-guards.log').open('w') as stream:
        guards=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=recording_type()).run(unittest.defaultTestLoader.loadTestsFromModule(test_integration))
    drift=[r['path'] for r in bindings if byte_sha((ROOT/r['path']).read_bytes())!=r['sha256']]
    native_manifest=ROOT/'implementation/lab-continuity/candidates/v1/packages/0001/generator-manifest.json'
    native_sha=parse(native_manifest.read_bytes())['native_executable_sha256']
    passed=guards.wasSuccessful() and guards.testsRun==28 and cold['result']=='PASS' and actual['result']=='PASS'
    passed=passed and join['evidence_coverage']=='PASS' and not drift and byte_sha(native.read_bytes())==native_sha
    checks=guards.checks+[c for v in unit_results.values() for c in v['checks']]+regression['checks']
    task_complete=bool(passed and join['result']=='PASS')
    context=parse((ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-W07.json').read_bytes())
    receipt={'schema_version':'lab-W07-integrated-workflow-evidence/v1-candidate','task':'W07','authority_effect':'none',
        'result':'PASS' if passed else 'FLAG','task_complete':task_complete,'model_integration_result':join['result'],
        'tests':len(checks),'checks':checks,'duration_seconds':time.perf_counter()-started,
        'files':bindings+[binding(p) for p in output.rglob('*') if p.is_file()],'source_bindings':context['source_bindings'],
        'source_drift':drift,'cold_verification':cold,'kind_rejection_probe':actual,'unit_results':unit_results,'domain_results':domain_results,
        'original_failed_parent':binding(source/'parent-process.log'),'original_domain_cases_reexecuted':0,
        'recovery_posture':'Observation of completed original cases plus fresh joining guards and cold context; no resumed effects or fabricated new success.',
        'actual_owner_outcome':None,'canonical_effects_applied':0,'global_merge_performed':False,
        'native_executable_binding':{'path':str(native),'sha256':native_sha},
        'remaining_obligations':[] if task_complete else [
            'Implement and verify the explicitly proposed Project/Product represented-subject mappings and exact signed-runtime coupling; workflow compatibility normalization is insufficient.',
            'Preserve raw carrier kinds and represented subject kinds as separate declared axes; bind mapping/source eligibility and contracts without implicit aliases.',
            'O02/O05/R03 supply the adapter/coupling implementation; W08/S02/R08 bind exact proposed mapping/code/effects; then rerun W07 completion proof.'],
        'claim_ceiling':'Original full candidate scenario evidence and repaired observational analysis only. Passing evidence receipt retains actual model FLAG and incomplete W07. No admission, alias authority, live operator recognition, Native Artifact mapping, general lesson effectiveness, Product benefit or whole-plan completion.'}
    receipt_path=output.with_suffix('.json');emit(receipt_path,receipt)
    print(encoded({'result':receipt['result'],'task_complete':task_complete,'model_integration_result':join['result'],
        'tests':len(checks),'receipt':receipt_path.relative_to(ROOT).as_posix(),'original_cases_reexecuted':0}).decode())
    return 0 if passed else 1


if __name__=='__main__':sys.exit(main(Path(sys.argv[1]),Path(sys.argv[2])))
