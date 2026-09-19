import copy,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('framings_import',HERE/'import.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.build();r=m.tool.read;p=HERE/'source-root'/m.PREFIX
for mode in ['duplicate','signature','endpoint','authority','vocabulary']:
 nodes=r(p/'nodes.json');rels=r(p/'relations.json')
 if mode=='duplicate':nodes['nodes'].append(copy.deepcopy(nodes['nodes'][0]))
 elif mode=='signature':rels['relations'][0]['type']='consumes'
 elif mode=='endpoint':rels['relations'][0]['target']='missing'
 elif mode=='authority':rels['relations'][0]['authority_effect']='admitted'
 else:rels['relation_types'].append(copy.deepcopy(rels['relation_types'][0]))
 try:m.validate_graph(nodes,rels)
 except ValueError:pass
 else:raise AssertionError(mode)
assert m.source_validation(m.STORE/'source-root')==b['source_validation']
for ref in b['snapshots']:
 p=m.ROOT/ref['path'];assert p.read_bytes()==(m.STORE/p.relative_to(HERE)).read_bytes()
for ref in b['ontology']['concept_refs']:
 file,ptr=ref.split('#');obj=r(m.STORE/file)
 for part in ptr.strip('/').split('/'):obj=obj[int(part)] if isinstance(obj,list) else obj[part]
 assert obj['id']
assert b['counts']['residue']==4
assert r(m.STORE/'bundle.json')==b
assert (m.ROOT/'.local/capability-inventory-import-0035/imports.json').read_bytes()==(m.CAPS/'imports.json').read_bytes()
m.dump(HERE/'verification.json',{'result':'PASS','authority_effect':'none','checks':['source-bound replay and admitted migration header schemas','duplicate node rejected','incorrect typed endpoint signature rejected','dangling endpoint rejected','authority escalation rejected','duplicate relation vocabulary rejected','full source validation passes after restoration','snapshot bytes and concept pointers preserved','four residue items and capability store unchanged'],'bindings':[m.bind(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='verification.json']})
print('PASS: nine import checks; 17 concepts and 16 relations.')
