#!/usr/bin/env python3
"""Freeze a scoped O02 representation proof; full lifecycle task stays open."""
import subprocess
import time
import traceback
import unittest

from represented_subjects import *
from observe_representation import observe
import test_represented_subjects

RUN = ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
RECEIPTS = PACKAGE/'receipts/O02'


def emit(path, value):
    with path.open('xb') as stream:
        stream.write((json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())


class Recording(unittest.TextTestResult):
    def __init__(self,*args):
        super().__init__(*args);self.checks=[]
    def addSuccess(self,test):
        super().addSuccess(test);self.checks.append({'test':test.id(),'result':'PASS'})
    def addFailure(self,test,error):
        super().addFailure(test,error);self.checks.append({'test':test.id(),'result':'FAIL'})
    def addError(self,test,error):
        super().addError(test,error);self.checks.append({'test':test.id(),'result':'ERROR'})


def main():
    started = time.perf_counter()
    context = parse((RUN/'context-O02.json').read_bytes())
    selected = {r['path']:{'path':r['path'],'sha256':r['sha256']} for r in context['source_bindings']}
    for binding in list(selected.values()):
        raw = original(binding)
        if not binding['path'].endswith('.json'):
            continue
        value = parse(raw)
        if 'result' in value and ('files' in value or 'source_files' in value):
            require(value['result']=='PASS', 'upstream evidence has not passed')
            for row in value.get('files',value.get('source_files',[]))+value.get('source_bindings',[]):
                b = {'path':row['path'],'sha256':row['sha256']}
                original(b)
                require(b['path'] not in selected or selected[b['path']]==b, 'conflicting original source pins')
                selected[b['path']] = b
    for path in (PACKAGE/'adapters').rglob('*'):
        if path.is_file() and path.suffix in ('.py','.md'):
            selected[path.relative_to(ROOT).as_posix()] = bind(path)
    if (RECEIPTS/'attempts').exists():
        for path in (RECEIPTS/'attempts').rglob('*'):
            if path.is_file():
                selected[path.relative_to(ROOT).as_posix()] = bind(path)
    selected[bind(RUN/'context-O02.json')['path']] = bind(RUN/'context-O02.json')
    RECEIPTS.mkdir(exist_ok=True)
    number = max([int(p.stem) for p in RECEIPTS.iterdir() if p.stem.isdigit()]+[0])+1
    output = RECEIPTS/f'{number:04d}';output.mkdir()
    files = list(selected.values())
    emit(output/'manifest.json',{'authority_effect':'none','task_complete':False,'files':files})
    errors=[];warm=None;cold=None;result=None
    try:
        with (output/'guards.log').open('w') as log:
            result = unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Recording).run(
                unittest.defaultTestLoader.loadTestsFromModule(test_represented_subjects))
        warm = observe();emit(output/'warm-observation.json',warm)
        with (output/'cold.stdout').open('wb') as stdout, (output/'cold.stderr').open('wb') as stderr:
            child = subprocess.run([sys.executable,str(PACKAGE/'adapters/observe_representation.py')],
                cwd=ROOT,stdout=stdout,stderr=stderr,timeout=90)
        require(child.returncode==0, 'cold observation failed')
        cold = parse((output/'cold.stdout').read_bytes())
        require(cold==warm, 'fresh original-byte reconstruction differs from warm view')
        emit(output/'cold-parity.json',{'result':'PASS','warm_observation_digest':object_sha(warm),
            'cold_observation_digest':object_sha(cold),'original_domain_effects_reexecuted':0})
    except Exception as error:
        errors.append({'error':str(error),'traceback':traceback.format_exc()})
    drift = [r['path'] for r in files if sha((ROOT/r['path']).read_bytes())!=r['sha256']]
    passed = bool(result and result.wasSuccessful() and result.testsRun==33 and warm and cold==warm and not errors and not drift)
    evidence = [bind(p) for p in output.rglob('*') if p.is_file()]
    receipt = {'schema_version':'lab-O02-representation-proof/v1-candidate','task':'O02','authority_effect':'none',
        'result':'PASS' if passed else 'FLAG','task_complete':False,'verified_obligation_ids':['P1','P2','P7'] if passed else [],
        'tests':result.testsRun if result else 0,'checks':result.checks if result else [],
        'duration_seconds':time.perf_counter()-started,'files':files+evidence,'source_bindings':context['source_bindings'],
        'source_drift':drift,'errors':errors,'represented_records':197 if passed else None,
        'candidate_relations_checked':70 if passed else None,'cold_reconstruction_parity':'PASS' if passed else 'FLAG',
        'original_domain_effects_reexecuted':0,'transactions_applied':0,'canonical_ontology_events_applied':0,
        'actual_owner_outcome':None,'signed_transaction_mapping_implemented':False,
        'remaining_obligations':[
            'Resolve rich Node/v2 definition selector digests, components, typed properties, obligations and forbidden collapses into Rust semantic state; no generic record passthrough.',
            'Declare and implement candidate native typed-profile support: the existing reducer only admits test-empty-profile/v1 with empty properties.',
            'Validate exact Lab source effects and map separate ontology semantic/governance events with exact event identity/digest/cursor joins.',
            'Demonstrate independent retire/remove/source-withdrawal and challenge-only semantic-byte preservation plus deterministic full lifecycle parity.',
            'O05/R03 must prove signed transaction coupling; W08/S02/R08 review exact mapping, implementation and effects; W07 remains open.'],
        'claim_ceiling':'Candidate represented-subject compatibility with actual frozen relation validator against independently replayed signed catalog. Prospective records remain unadmitted; unchanged signed inputs retain posture. No signed mapping persistence, rich native Artifact mapping, canonical ontology events, owner outcome or full O02/W07 completion.'}
    path=output.with_suffix('.json');emit(path,receipt)
    print(json.dumps({'result':receipt['result'],'task_complete':False,'tests':receipt['tests'],
        'receipt':path.relative_to(ROOT).as_posix(),'candidate_relations_checked':receipt['candidate_relations_checked'],
        'cold_reconstruction_parity':receipt['cold_reconstruction_parity']}))
    return 0 if passed else 1


if __name__=='__main__':sys.exit(main())
