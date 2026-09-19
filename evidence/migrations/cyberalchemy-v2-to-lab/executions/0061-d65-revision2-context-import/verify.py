import copy,importlib.util,json,shutil,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('d65_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;binding=r(HERE/'successor-binding.json');model=r(HERE/'model.json');gov=m.PACKAGE/'cyberAlchemy-v2/ontology/governance'
spec=importlib.util.spec_from_file_location('adapter',m.STORE/'adapter.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
subject=binding['subject_ref'];baseline=a.evaluate(m.PACKAGE,subject)
assert baseline==r(HERE/'candidate-evaluation.json')
assert all(baseline[k] is False for k in ['product_approved','authority_granted','effect_authorized'])
assert baseline['source_evaluation']['eligibility'][subject]['authority_request']=='not_eligible'
cases=[]
for name in ['unknown','']:
    result=a.evaluate(m.PACKAGE,name);assert result['status']=='NOT_EVALUABLE' and result['errors']==['SUBJECT_NOT_BOUND'];cases.append('unbound subject '+repr(name))
with tempfile.TemporaryDirectory(prefix='d65-r2-adapter-') as tmp:
    root=Path(tmp)
    for item in binding['artifacts']:
        target=root/item['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(m.PACKAGE/item['path'],target)
    target=root/binding['artifacts'][0]['path'];original=target.read_bytes();target.write_bytes(original+b' ')
    assert a.evaluate(root,subject)['errors'][0].startswith('BOUND_INPUT_DRIFT:');cases.append('changed construction bytes rejected')
    target.unlink();assert a.evaluate(root,subject)['errors'][0].startswith('BOUND_INPUT_DRIFT:');cases.append('missing construction rejected')
original_read=a.read
for mode in ['duplicate','empty']:
    def mutated(path):
        d=original_read(path)
        if path.name=='prototype-constructions.json':
            d['constructions']=d['constructions']*2 if mode=='duplicate' else []
        return d
    a.read=mutated
    try:assert a.evaluate(m.PACKAGE,subject)['errors']==['EXACT_SINGLE_SUBJECT_REQUIRED']
    finally:a.read=original_read
    cases.append(mode+' subject registry rejected')
m.dump(HERE/'adapter-tests.json',{'result':'PASS','cases':cases,'authority_effect':'none'})
scaffold=r(gov/'ontology-scaffolds.json')['scaffolds'][0]
assert [n['name'] for n in model['business_concepts']]==scaffold['concept_refs']
assert [{k:v for k,v in n.items() if k!='evidence_ref'} for n in model['relation_hints']]==scaffold['relation_hints']
names=set(scaffold['concept_refs']);external=sorted({e[k] for e in scaffold['relation_hints'] for k in ['source_ref','target_ref']}-names)
assert model['external_hint_endpoints']==external and len(external)==3
assert all(e['posture']=='prototype-hint' for e in model['relation_hints'])
schema=r(gov/'schemas/prototype-construction.schema.json')
assert [n['name'] for n in model['system_contract_concepts']]==[k for k,v in schema['$defs'].items() if v.get('type')=='object']
for ref in b['ontology']['concept_refs']+b['ontology']['relation_ids']:
    file,ptr=ref.split('#');obj=r(m.STORE/file)
    for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    assert isinstance(obj,(dict,str))
trans=r(m.PREV/'validation-transcripts.json');tests=json.loads(trans[1]['stdout']);assert trans[1]['exit_code']==0 and tests['status']=='PASS' and len(tests['cases'])==8
assert baseline['source_evaluation']==json.loads(trans[2]['stdout'])
for entry in r(m.PREV/'package-inputs.json'):assert m.tool.sha(m.PACKAGE/entry['path'])==entry['sha256']
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
assert r(m.STORE/'bundle.json')==b
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['existing migration headers and predecessor bindings','exact subject baseline evaluation reproduces','six adapter rejection cases pass','PASS grants no product approval or authority','scaffold concepts and hints preserved exactly','three external hint endpoints explicitly retained','schema object concepts selected without legacy model substitution','all source-qualified pointers resolve','eight prior revision-2 tests bound to unchanged source bytes','entire original snapshot remains byte-identical','legacy capability inventory unchanged','restored bundle and candidate contracts resolve'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: twelve import checks, six adapter rejection cases; eight prior revision-2 tests retain exact inputs.')
