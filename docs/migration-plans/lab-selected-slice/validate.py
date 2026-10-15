"""Freeze exact O04 candidate design and verify source/disposition closure."""
import os
import time
import traceback

from check_inventory import *

RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
RECEIPTS=ROOT/'implementation/lab-ontology/candidates/v1/receipts/O04'


def emit(path,value):
    with path.open('x') as stream:stream.write(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n')


def main():
    started=time.perf_counter();selection=parse(TARGET.read_bytes())
    context=parse((RUN/'context-O04.json').read_bytes());frozen={}
    for b in context['source_bindings']:
        require(sha((ROOT/b['path']).read_bytes())==b['sha256'],'O04 input changed')
        frozen[b['path']]={k:b[k] for k in ('path','sha256')}
    for task,path in [('O01','implementation/lab-ontology/candidates/v1/receipts/O01-0006.json'),
                      ('C07','implementation/lab-runtime/candidates/repeatable-operation/receipts/C07/0007.json')]:
        receipt=parse((ROOT/path).read_bytes())
        require(receipt['result']=='PASS' and receipt.get('task_complete') is not False,'exact upstream scope incomplete: '+task)
        for b in receipt.get('files',receipt.get('source_files',[]))+receipt.get('source_bindings',[]):
            require(sha((ROOT/b['path']).read_bytes())==b['sha256'],'upstream source/evidence drift: '+b['path'])
            frozen[b['path']]={k:b[k] for k in ('path','sha256')}
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and 'receipts' not in p.parts:
            b=bind(p);frozen[b['path']]=b
    for p in (TARGET,RUN/'context-O04.json'):
        b=bind(p);frozen[b['path']]=b
    for b in selection['external_source_bindings']:frozen[b['path']]=b
    files=list(frozen.values());RECEIPTS.mkdir(exist_ok=True)
    number=max([int(p.stem) for p in RECEIPTS.iterdir() if p.stem.isdigit()]+[0])+1
    output=RECEIPTS/f'{number:04d}';output.mkdir()
    emit(output/'manifest.json',{'authority_effect':'none','actual_owner_outcome':None,'files':files,
        'scope':'O04 exact selected source/dependency inventory and disposition design'})
    errors=[];checks=[];cold=None;actual=None
    try:
        actual=validate_selection(selection,True)
        with (output/'guards.stdout').open('wb') as stdout,(output/'guards.stderr').open('wb') as stderr:
            child=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_inventory.py','-v'],
                cwd=ROOT,stdout=stdout,stderr=stderr,timeout=60)
        require(child.returncode==0,'O04 inventory guards failed; original logs retained')
        raw=(output/'guards.stderr').read_text()
        require('Ran 42 tests' in raw and raw.rstrip().endswith('OK'),'42 complete authoring guards required')
        checks=[{'test':line.split(' ... ')[0],'result':'PASS','suite':'inventory-authoring-guards'}
            for line in raw.splitlines() if line.endswith(' ... ok')]
        require(len(checks)==42,'inventory guard result inventory differs')
        with (output/'cold.stdout').open('wb') as stdout,(output/'cold.stderr').open('wb') as stderr:
            child=subprocess.run([sys.executable,str(HERE/'reconstruct.py'),str(TARGET),sha(TARGET.read_bytes())],
                cwd=ROOT,stdout=stdout,stderr=stderr,timeout=120)
        require(child.returncode==0,'fresh source inventory reconstruction failed; original logs retained')
        cold=parse((output/'cold.stdout').read_bytes());require(cold['result']=='PASS','cold exact source parity incomplete')
        verify_observations(selection)
    except Exception as error:errors.append({'error':str(error),'traceback':traceback.format_exc()})
    drift=[b['path'] for b in files if not (ROOT/b['path']).is_file() or sha((ROOT/b['path']).read_bytes())!=b['sha256']]
    passed=bool(not errors and not drift and len(checks)==42 and cold)
    outputs=[bind(p) for p in output.iterdir() if p.is_file()]
    receipt={'schema_version':'lab-O04-exact-source-inventory-proof/v1-candidate','task':'O04','result':'PASS' if passed else 'FLAG',
        'task_complete':passed,'completion_mode':'candidate-design','authority_effect':'none','actual_owner_outcome':None,
        'tests':len(checks),'checks':checks,'duration_seconds':time.perf_counter()-started,
        'files':files+outputs,'source_bindings':context['source_bindings'],'source_drift':drift,'errors':errors,
        'selection_binding':bind(TARGET),'inventory_verification':actual,'cold_reconstruction':cold,
        'counts':selection['counts'],'disposition_counts':selection['disposition_counts'],
        'verified_obligation_ids':['M1','M2','M3','M4','M5','M6'] if passed else [],
        'blocked_dependency_revisions':[{'id':i['legacy_identity'],'expected_sha256':i['expected_sha256'],'reason':i['reason']}
            for i in selection['items'] if i['disposition']=='block'],
        'source_records_imported':0,'raw_source_bodies_exported':0,'source_effects_applied':0,'domain_instances_conformed':0,
        'remaining_obligations':[] if passed else ['Finish exact O04 inventory/disposition design verification.'],
        'downstream_obligations':['O05: build exact source-qualified Source/Node/local Edge adaptations and validate every produced Lab carrier; blocked dependencies remain explicit until exact source epoch replacement.',
            'O05/R03: signed Project/Product endpoint transaction coupling and W07 completion proof remain independent integration work.',
            'S02/R08: exact private use/publication, local interpretation profile, type/mapping and implementation ownership remain actual review obligations.'],
        'claim_ceiling':'Complete original O04 candidate design criteria only: explicit useful domain, exact repository/ref/file/selector/digest bindings, private/public classification, per-item disposition/dependency/carrier fit and existing adapter review. Five original source schemas checked and all 140 items accounted for; nine stale dependencies blocked. No Lab domain conformance, source execution/import, body export, transitive closure, live state, admission or actual owner outcome.'}
    path=output.with_suffix('.json');emit(path,receipt)
    print(json.dumps({'result':receipt['result'],'task_complete':passed,'tests':len(checks),
        'receipt':path.relative_to(ROOT).as_posix(),'source_drift':drift,'errors':[e['error'] for e in errors],
        'counts':selection['counts'],'dispositions':selection['disposition_counts']}))
    return 0 if passed else 1


if __name__=='__main__':sys.exit(main())
