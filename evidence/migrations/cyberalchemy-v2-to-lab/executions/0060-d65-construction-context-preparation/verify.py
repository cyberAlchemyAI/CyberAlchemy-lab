import hashlib,json,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];PREV=HERE.parent/'0059-dependency-relevance-context-import'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,data):
    path=HERE/name;content=json.dumps(data,indent=2,sort_keys=True)+'\n'
    if path.exists() and path.read_text()!=content:raise ValueError('Frozen evidence drift')
    path.write_text(content)
for b in read(PREV/'verification.json')['bindings']:assert sha(ROOT/b['path'])==b['sha256']
manifest={b['path']:b['sha256'] for b in read(HERE/'package-inputs.json')}
with tarfile.open(HERE/'package-snapshot.tar.gz') as archive:
    names=[]
    for entry in archive:
        assert entry.isfile();names.append(entry.name)
        assert hashlib.sha256(archive.extractfile(entry).read()).hexdigest()==manifest[entry.name]
    assert len(names)==len(set(names))==len(manifest)
legacy=read(HERE/'legacy-evaluation.json');assert legacy['status']=='BLOCK' and len(legacy['errors'])==11
assert 'D65_REVISION_2_EVALUATOR_NOT_IMPLEMENTED' in legacy['blockers']
trans=read(HERE/'validation-transcripts.json');assert len(trans)==3 and all(t['exit_code']==0 for t in trans)
results=[json.loads(t['stdout']) for t in trans]
assert all(d['status']=='PASS' and d['authority_effect']=='none' for d in results)
assert len(results[0]['cases'])==len(results[1]['cases'])==8
r2=results[2];assert r2['definition_revision']==2 and r2['counts']=={'constructions':1,'ontology_scaffolds':1}
state=r2['eligibility']['GOV-D65-R2-PROTOTYPE-CONSTRUCTION-001']
assert state['product_approval_request']=='eligible' and state['authority_request']=='not_eligible'
build=read(HERE/'build-check.json');assert build['exit_code']==0 and build['changed_generated_artifacts']==[]
assert not (HERE/'bundle.json').exists()
assert (ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(HERE.parent/'0035-definition-card-import/imports.json').read_bytes()
dump('preparation.json',{'result':'BLOCK','reason':'Existing capability realization remains legacy revision 1; the passing revision-2 prototype needs explicit successor contracts and bindings.','authority_effect':'none','legacy_errors':11,'legacy_blockers':legacy['blockers'],'legacy_tests_passed':8,'revision_2_tests_passed':8,'revision_2_evaluation':'PASS','product_approval_request':'eligible','authority_request':'not_eligible','generated_artifacts_reproduce':True,'context_imported':False,'legacy_validation_scope':'stage diagnostics without dependency-validator subprocesses; independent source build checked'})
dump('verification.json',{'result':'PASS','import_status':'BLOCK','authority_effect':'none','checks':['predecessor bindings intact','archive exactly matches input manifest','legacy unsupported revision and eleven errors preserved','eight legacy hostile checks pass','eight revision-2 prototype checks pass','revision-2 evaluation passes for exact prototype and scaffold','eligibility remains distinct from approval and authority','generated artifacts reproduce and capability store unchanged; no import emitted'],'bindings':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: eight preparation checks; 8 legacy and 8 revision-2 tests. Successor binding required before import.')
