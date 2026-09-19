import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('context_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;bundle=r(HERE/'bundle.json');assert m.build()==bundle
profile=r(HERE/'source/profile.json');nodes=r(HERE/'source/nodes.json');relations=r(HERE/'source/relations.json');cap=next(i for i in r(m.PREV/'imports.json') if i['id']==profile['product_capability_ref'])
for mode in ['endpoint','role','duplicate','authority']:
    ns=copy.deepcopy(nodes);rs=copy.deepcopy(relations)
    if mode=='endpoint':rs['relations'][0]['target']='missing'
    elif mode=='role':rs['relations'][0]['type']='contains'
    elif mode=='duplicate':ns['nodes'].append(copy.deepcopy(ns['nodes'][0]))
    else:rs['relations'][0]['authority_effect']='admitted'
    try:m.validate_source(profile,ns,rs,cap)
    except ValueError:pass
    else:raise AssertionError('Bad graph accepted: '+mode)
assert r(m.STORE/'bundle.json')==bundle
for b in bundle['snapshots']:
    p=m.ROOT/b['path'];assert p.read_bytes()==(m.STORE/p.relative_to(HERE)).read_bytes()
# Resolve the stored ontology's source-qualified pointers from the restored snapshot.
stored=r(m.STORE/'bundle.json')
for ref in stored['ontology']['concept_refs']:
    file,ptr=ref.split('#');obj=r(m.STORE/file)
    for part in ptr.strip('/').split('/'):obj=obj[int(part)] if isinstance(obj,list) else obj[part]
    assert obj['id']
assert stored['source_validation']['status']=='PASS'
assert stored['source_validation']['construction']['implementation_binding']=='not_evaluable'
assert len(r(HERE/'source/residue.json')['residue'])==6
spec=importlib.util.spec_from_file_location('restored_validator',m.STORE/'source/scripts/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.PACKAGE_ROOT=m.STORE/'source';v.REPOSITORY_ROOT=m.STORE/'evidence-root';v.SHARED_CAPABILITY_SCHEMA=v.REPOSITORY_ROOT/'cyberAlchemy-v2/capability/schemas/capability.schema.json'
assert v.validate()==stored['source_validation']
bad=copy.deepcopy(r(HERE/'source/sources.json')['sources'][0]);bad['sha256']='0'*64
errors=[];v.source_selection(bad,errors);assert any('digest drift' in e for e in errors)
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.PREV/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','checks':['deterministic source-bound context/schema replay','dangling endpoint rejected','invalid relation role rejected','duplicate concept rejected','authority escalation rejected','store and companion snapshots read back exactly; concept pointers resolve','six unresolved source items and unselected implementation preserved','full package validator passes from restored store','wrong evidence fingerprint rejected','capability store unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none','runtime_tests_rerun':False})
print('PASS: ten context-import checks; 22 concepts, 24 relations; recovered evidence validates.')
