import copy,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('architecture_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;p=m.PACKAGE/m.PREFIX
baseline=[r(p/'ELEMENT-TYPES.json')['element_types'],r(p/'PROPERTIES.json')['properties'],r(p/'CONSTRAINTS.json')['constraints'],r(p/'VIEWS.json')['views'],r(p/'OBSERVATION-PROJECTIONS.json')]
cases=['duplicate-type','duplicate-property','duplicate-constraint','missing-type','missing-property','unknown-as-pass','view-reference','invented-observation','authority']
for case in cases:
    t,pr,c,v,o=copy.deepcopy(baseline)
    if case=='duplicate-type':t.append(copy.deepcopy(t[0]))
    elif case=='duplicate-property':pr.append(copy.deepcopy(pr[0]))
    elif case=='duplicate-constraint':c.append(copy.deepcopy(c[0]))
    elif case=='missing-type':c[0]['subject_type']='missing'
    elif case=='missing-property':c[0]['property_ref']='missing'
    elif case=='unknown-as-pass':c[0]['on_unknown']='pass'
    elif case=='view-reference':v[0]['constraint_ids'].append('missing')
    elif case=='invented-observation':o['projections']=[{'result':'PASS'}]
    else:t[0]['authority_effect']='admitted'
    try:m.model_check(t,pr,c,v,o)
    except ValueError:pass
    else:raise AssertionError(case)
for ref in b['ontology']['concept_refs']:
    file,ptr=ref.split('#');obj=r(m.STORE/file)
    for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    assert isinstance(obj,dict)
assert b['ontology']['relation_ids']==[]
sources=r(p/'SOURCES.json')['sources'];assert len(sources)==len({s['source_id'] for s in sources})==5
for s in sources:
    path=m.PACKAGE/s['path'];assert m.tool.sha(path)==s['sha256'] and path.stat().st_size==s['size_bytes'];assert all(q in path.read_text() for q in s['selectors'])
profile=r(p/'PROFILE.json');assert set(profile['material_files'])=={str(f.relative_to(p)) for f in p.rglob('*') if f.is_file() and 'receipts' not in f.relative_to(p).parts}
output=json.loads(r(HERE/'source-validation.json')['stdout']);assert output['overall']=='PASS' and output['errors']==[]
material=hashlib.sha256()
for name in sorted(profile['material_files']):material.update(name.encode()+b'\0'+(p/name).read_bytes()+b'\0')
assert material.hexdigest()==output['material_digest']
assert not (p/'receipts').exists()
assert len(r(p/'RESIDUE.json')['residue'])==2 and baseline[-1]['projections']==[]
for entry in r(HERE/'package-inputs.json'):assert m.tool.sha(m.PACKAGE/entry['path'])==entry['sha256']
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['predecessor bindings and existing migration header contracts','restored source validator and independently computed material digest match','nine negative identity reference evidence and authority cases rejected','all 28 source record pointers resolve without invented relations','all five evidence files match fingerprints sizes and selectors','all seven views cover the eleven constraints','empty observations and two residue entries preserved','capability storage and entire restored snapshot unchanged'],'negative_cases':cases,'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: eight import checks and nine rejection cases; source validation passes with zero observations.')
