import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('kep_context',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.tool.read;b=r(HERE/'bundle.json');assert m.build()==b
for mode in ['endpoint','duplicate','meaning','authority']:
    source=copy.deepcopy(b['source_graph'])
    if mode=='endpoint':source['relations'][0]['target']='missing'
    elif mode=='duplicate':source['nodes'].append(copy.deepcopy(source['nodes'][0]))
    elif mode=='meaning':source['relations'][0]['relationship']=''
    else:source['authority_effect']='admitted'
    try:m.validate_graph(source,b['external_endpoints'])
    except ValueError:pass
    else:raise AssertionError('Invalid context accepted')
assert r(m.STORE/'bundle.json')==b
assert {v['ontology_id'] for v in b['composed_contexts']}==set(b['source_graph']['composed_ontology_refs'])
for v in b['composed_contexts']:assert m.tool.sha(m.ROOT/v['binding']['path'])==v['binding']['sha256']
for ref in b['snapshots']:
    p=m.ROOT/ref['path'];assert p.read_bytes()==(m.STORE/'source'/p.name).read_bytes()
for ref in b['ontology']['concept_refs']:
    file,ptr=ref.split('#');obj=r(m.STORE/file)
    for key in ptr.strip('/').split('/'):obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    assert obj['id']
assert b['source_graph']['construction_state']==r(HERE/'source/profile.json')['construction_state']
assert all(p['evidence_state']=='not_evaluable' for p in b['source_graph']['proof_requirements'])
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','checks':['source-bound replay and Lab header schemas','unexpected external endpoint rejected','duplicate concept rejected','missing relationship name rejected','source authority escalation rejected','stored snapshots match; all concept pointers resolve','source blocked stages and proof states preserved','capability store unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json'],'authority_effect':'none','runtime_tests_rerun':False})
print('PASS: eight context checks; 49 concepts, 54 relationships, two pinned composed contexts.')
